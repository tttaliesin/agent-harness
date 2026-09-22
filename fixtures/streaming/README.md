# Streaming fixture

Run real CPU synthetic RTSP publication, interruption, recovery, and optional WebRTC reception on isolated loopback resources.
The fixture calls the [streaming-testing probe](../../skills/streaming-testing/scripts/stream_probe.py) directly with Python's standard library; no consumer runtime is required.
Use it from the same repository revision as the shared skills.

## Prepare pinned tools

The tested native platform is Windows x64 with Python 3.12.14, MediaMTX 1.15.6, FFmpeg 8.0, Node 24.19.0, pnpm 11.19.0, and Playwright 1.58.2's Chromium 145.0.7632.6.
The [tool manifest](tools.json) records release URLs and GitHub release-asset SHA-256 digests.
FFmpeg's [download page](https://ffmpeg.org/download.html) links Gyan's Windows builds; these are distributor binaries, not binaries produced by the FFmpeg project.
No binary is committed or installed globally.

From `fixtures/streaming` in PowerShell, download, check, and extract the two native archives:

```powershell
$pins = Get-Content -Raw tools.json | ConvertFrom-Json
New-Item -ItemType Directory -Force .reports/tools | Out-Null
foreach ($name in @('mediamtx', 'ffmpeg')) {
    $tool = $pins.$name
    $archive = Join-Path .reports/tools ($name + '.zip')
    if (-not (Test-Path -LiteralPath $archive)) {
        Invoke-WebRequest -Uri $tool.url -OutFile $archive -TimeoutSec 120
    }
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLower() -ne $tool.sha256) {
        throw "Archive checksum mismatch: $name"
    }
    $destination = Join-Path .reports/tools $name
    if (-not (Test-Path -LiteralPath $destination)) {
        Expand-Archive -LiteralPath $archive -DestinationPath $destination
    }
}
```

Keep the archive licenses with the extracted tools.
The runner checks executable versions before starting resources.
Linux/macOS runs require separately verified native builds of the same versions; their execution is not covered by the Windows evidence.

For browser reception, use a locally available pnpm 11.19.0 executable, or invoke that version with `npx --yes pnpm@11.19.0`.
From this fixture directory, keep install caches and browsers local:

```powershell
$env:npm_config_cache = Join-Path (Get-Location) '.reports/npm-cache'
npx --yes pnpm@11.19.0 install --frozen-lockfile --ignore-scripts --store-dir .reports/pnpm-store --cache-dir .reports/pnpm-cache --config.state-dir=.reports/pnpm-state
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path (Get-Location) '.reports/browsers'
$env:PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT = '45000'
node node_modules/playwright/cli.js install chromium
```

Installation is an explicit preparation step; checks never download tools or alter locks.
If `--webrtc` is selected, unavailable tools or browser execution cannot yield a passing run.

## Run the scenario

From the repository root with `python` pointing at Python 3.12 or newer:

```powershell
python -B fixtures/streaming/run.py --ffmpeg fixtures/streaming/.reports/tools/ffmpeg/ffmpeg-8.0-essentials_build/bin/ffmpeg.exe --mediamtx fixtures/streaming/.reports/tools/mediamtx/mediamtx.exe --webrtc
```

Use `--node <NODE_EXECUTABLE>` when Node is not on PATH.
Use `--browser-cache <EXISTING_CACHE>` to reuse an already installed task-local browser cache when running from another worktree.
Omit `--webrtc` only for a transport-only run; the result records browser reception as `NOT_RUN`.
The executable arguments resolve from the caller's directory; all generated resources resolve from this fixture's source directory.
Exit `0` means the selected checks passed, `1` indicates failure or timeout, and `2` indicates a missing tool or browser.

Each run creates a fresh `.reports/run-<id>/` directory containing its exact commands, generated MediaMTX configuration, logs, raw frame checksums, browser samples when selected, and `result.json`.
The server binds RTSP, API, HTTP, and ICE UDP only on `127.0.0.1`; other protocols are disabled, with no STUN/TURN or broad interface discovery.
Each run selects ephemeral ports and a random stream path, and clears inherited `MTX_` settings that could override the fixture configuration.
Native bind races cause failure; the fixture never stops another process to claim a port.

The scenario requires 12 decoded frames before interruption, a live-server 404 and zero frames during at least two seconds without publication, and 12 decoded frames after restart with at least four new hashes.
Red and blue source-epoch corner markers distinguish pre-outage frames from recovery frames.
Readiness waits are bounded at ten seconds, decoder reads at twelve seconds, outage reads at three seconds, and browser execution at 45 seconds.
The publisher also has a 90-second media limit.
Cleanup records only this run's process handles and stops their owned trees; it never uses process-name or port-wide termination.

The browser checks increasing WebRTC inbound bytes and decoded frames together with advancing media time and changing rendered pixels.
It starts a new receiver after publication recovers; this does not prove that an existing browser session reconnects automatically.

## Interpret the evidence

This fixture demonstrates CPU media transport and a synthetic source restart.
It does not execute GPU inference, test tracker identity continuity, exercise a production media server, or establish trusted CI provenance.
Both GPU and tracker results remain `NOT_RUN`.
The product adapter must separately invoke its real RTSP → inference → WebRTC route and approved device, timing, and tracking checks, as described in [product pipeline evidence](../../skills/streaming-testing/references/product-pipeline.md).

Run the targeted regression tests from the repository root with the prepared maintenance environment:

```sh
python -B -m pytest -q -p no:cacheprovider tests/test_streaming_probe.py
```

The tests exercise malformed/empty output, frozen pixels, stale recovery frames, nonadvancing timestamps, real subprocess timeout cleanup, a missing executable, report collision, and cleanup preserving an unrelated process.
Preserve failed run directories and their logs when diagnosing a failure; subsequent invocations use new directories.
