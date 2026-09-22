const { defineConfig } = require('@playwright/test');

const port = Number(process.env.FIXTURE_PORT || 8765);
if (!Number.isInteger(port) || port < 1024 || port > 65535)
  throw new Error('FIXTURE_PORT must be an integer between 1024 and 65535');
const python = process.platform === 'win32' ? '.venv\\Scripts\\python.exe' : '.venv/bin/python';
const channel = process.env.FIXTURE_BROWSER_CHANNEL || (process.platform === 'win32' ? 'msedge' : 'chrome');
const baseURL = `http://127.0.0.1:${port}`;

module.exports = defineConfig({
  testDir: './e2e',
  outputDir: '.reports/playwright',
  reporter: [['line'], ['junit', { outputFile: '.reports/browser.xml' }]],
  timeout: 15_000,
  globalTimeout: 60_000,
  expect: { timeout: 5_000 },
  retries: 0,
  workers: 1,
  use: { baseURL, channel, headless: true, trace: 'retain-on-failure' },
  webServer: {
    command: `"${python}" -B app.py --port ${port}`,
    cwd: __dirname,
    url: `${baseURL}/health`,
    reuseExistingServer: false,
    timeout: 10_000,
  },
});
