// Real WebRTC decode and changing rendered pixels; MediaMTX supplies the player.
import { writeFile } from 'node:fs/promises';
import { chromium } from 'playwright';

const [url, output] = process.argv.slice(2);
if (!url || !output || new URL(url).hostname !== '127.0.0.1') {
  throw new Error('usage: node browser-receive.mjs http://127.0.0.1:PORT/PATH REPORT');
}
let browser;
let report = { status: 'FAIL', reason: 'receive did not complete' };
try {
  browser = await chromium.launch({ headless: true, timeout: 10000 });
  const page = await browser.newPage();
  page.setDefaultTimeout(15000);
  await page.addInitScript(() => {
    window.fixturePeers = [];
    const Peer = window.RTCPeerConnection;
    window.RTCPeerConnection = class extends Peer {
      constructor(...args) { super(...args); window.fixturePeers.push(this); }
    };
  });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
  await page.waitForFunction(() => document.querySelector('video')?.videoWidth > 0);
  const received = await page.evaluate(async () => {
    const video = document.querySelector('video');
    const canvas = document.createElement('canvas');
    canvas.width = 80; canvas.height = 45;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const samples = [];
    const deadline = performance.now() + 6000;
    while (performance.now() < deadline && samples.length < 12) {
      await new Promise(resolve => setTimeout(resolve, 150));
      ctx.drawImage(video, 0, 0, 80, 45);
      const pixels = ctx.getImageData(0, 0, 80, 45).data;
      let hash = 2166136261;
      for (const byte of pixels) hash = Math.imul(hash ^ byte, 16777619) >>> 0;
      let decoded = 0, bytes = 0;
      for (const peer of window.fixturePeers) {
        for (const stat of (await peer.getStats()).values()) {
          if (stat.type === 'inbound-rtp' && stat.kind === 'video') {
            decoded += stat.framesDecoded ?? 0;
            bytes += stat.bytesReceived ?? 0;
          }
        }
      }
      samples.push({ decoded, bytes, hash, mediaTime: video.currentTime });
    }
    return { samples, width: video.videoWidth, height: video.videoHeight };
  });
  const first = received.samples[0], last = received.samples.at(-1);
  const unique = new Set(received.samples.map(sample => sample.hash)).size;
  if (!first || last.decoded - first.decoded < 4 || last.bytes <= first.bytes ||
      last.mediaTime <= first.mediaTime || unique < 4) {
    throw new Error(`WebRTC did not deliver new decoded/rendered frames: ${JSON.stringify(received)}`);
  }
  report = { status: 'PASS', browser: browser.version(), ...received, unique_frames: unique,
    decoded_delta: last.decoded - first.decoded, bytes_delta: last.bytes - first.bytes };
} catch (error) {
  report = { status: /Executable doesn't exist/.test(error.message) ? 'BLOCKED' : 'FAIL',
    reason: error.message };
} finally {
  if (browser) await browser.close();
  await writeFile(output, JSON.stringify(report, null, 2), { flag: 'wx' });
}
console.log(JSON.stringify({ status: report.status, output }));
process.exitCode = report.status === 'PASS' ? 0 : report.status === 'BLOCKED' ? 2 : 1;
