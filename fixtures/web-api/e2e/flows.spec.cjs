const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page, request }) => {
  const health = await request.get('/health');
  expect(await health.json()).toEqual({ service: 'agent-harness-web-api', ready: true });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.fixtureErrors = errors;
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Web/API fixture' })).toBeVisible();
});

test.afterEach(async ({ page }) => {
  expect(page.fixtureErrors).toEqual([]);
});

test('normal input renders the real HTTP greeting', async ({ page }) => {
  await page.getByLabel('Name', { exact: true }).fill('Ada');
  const response = page.waitForResponse(r => new URL(r.url()).pathname === '/api/greet');
  await page.getByRole('button', { name: 'Greet', exact: true }).click();
  expect((await response).status()).toBe(200);
  await expect(page.getByRole('status')).toHaveText('Hello, Ada!');
});

test('empty input displays the server validation failure', async ({ page }) => {
  const response = page.waitForResponse(r => new URL(r.url()).pathname === '/api/greet');
  await page.getByRole('button', { name: 'Greet', exact: true }).click();
  expect((await response).status()).toBe(422);
  await expect(page.getByRole('alert')).toHaveText('Name must contain 1 to 40 characters');
});

for (const [identity, status, message] of [
  ['guest', 401, 'Authentication required'],
  ['viewer', 403, 'Admin role required'],
  ['admin', 200, 'Admin access granted'],
]) {
  test(`${identity} receives the expected authorization result`, async ({ page }) => {
    await page.getByLabel('Fixture identity').selectOption(identity);
    const response = page.waitForResponse(r => new URL(r.url()).pathname === '/api/admin');
    await page.getByRole('button', { name: 'Check admin access' }).click();
    expect((await response).status()).toBe(status);
    await expect(page.getByRole(status === 200 ? 'status' : 'alert')).toHaveText(message);
  });
}

test('service error is visible and the next request recovers', async ({ page }) => {
  const response = page.waitForResponse(r => new URL(r.url()).pathname === '/api/error');
  await page.getByRole('button', { name: 'Simulate service error' }).click();
  expect((await response).status()).toBe(503);
  await expect(page.getByRole('alert')).toHaveText('Fixture service unavailable');
  await page.getByLabel('Name', { exact: true }).fill('Recovered');
  await page.getByRole('button', { name: 'Greet', exact: true }).click();
  await expect(page.getByRole('status')).toHaveText('Hello, Recovered!');
  await expect(page.getByRole('alert')).toBeEmpty();
});

test('user input is rendered as text', async ({ page }) => {
  await page.getByLabel('Name', { exact: true }).fill('<img src=x onerror=alert(1)>');
  await page.getByRole('button', { name: 'Greet', exact: true }).click();
  await expect(page.getByRole('status')).toHaveText('Hello, <img src=x onerror=alert(1)>!');
  await expect(page.locator('img')).toHaveCount(0);
});
