import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(directory, '.build/site');
const prefix = '/github-copilot-app-java-workshop';
const origin = process.env.WORKSHOP_SITE_URL;
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };
const server = origin ? null : createServer(async (request, response) => {
  const url = new URL(request.url, 'http://localhost');
  if (!url.pathname.startsWith(prefix + '/')) {
    response.writeHead(404).end();
    return;
  }
  const filename = path.resolve(root, '.' + decodeURIComponent(url.pathname.slice(prefix.length)),
    url.pathname.endsWith('/') ? 'index.html' : '');
  if (!filename.startsWith(root + path.sep)) {
    response.writeHead(403).end();
    return;
  }
  try {
    const body = await readFile(filename);
    response.writeHead(200, { 'Content-Type': types[path.extname(filename)] || 'application/octet-stream' });
    response.end(body);
  } catch (error) {
    if (error.code !== 'ENOENT') console.error(error);
    response.writeHead(error.code === 'ENOENT' ? 404 : 500).end();
  }
});

let browser;
try {
  if (server) await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = origin || `http://127.0.0.1:${server.address().port}${prefix}/`;
  browser = await chromium.launch(process.env.CAPTURE_CHANNEL ? { channel: process.env.CAPTURE_CHANNEL } : {});
  const context = await browser.newContext({ permissions: ['clipboard-read', 'clipboard-write'] });
  const analytics = [];
  await context.route(/https:\/\/(?:[^/]+\.)?(?:googletagmanager|google-analytics)\.com\//, route => {
    analytics.push(route.request().url());
    return route.abort();
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport);
    await page.goto(base);
    await page.locator('#consent-banner').waitFor({ state: 'visible' });
    assert.equal(analytics.length, 0, 'Analytics request before consent');
    assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'),
      'https://www.julien-dubois.com' + prefix + '/');
    assert.equal(await page.locator('.workshop-content h1').count(), 1);
    assert.equal(await page.locator('.workshop-next a').getAttribute('href'), prefix + '/setup/');
    assert.equal(await page.locator('.workshop-nav').first().locator('a[aria-current=page]').count(), 1);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
      'Horizontal page overflow');
    assert.ok(await page.locator('.navbar').evaluate(element =>
      getComputedStyle(element).position === 'fixed'), 'Theme CSS did not load');
    if (viewport.width < 600) {
      await page.locator('.navbar-toggler').click();
      await page.locator('#navbarNav.show').waitFor();
      await page.locator('.navbar-toggler').click();
      await page.locator('#navbarNav').waitFor({ state: 'hidden' });
      await page.locator('.workshop-mobile-nav summary').click();
      await page.locator('.workshop-mobile-nav a', { hasText: 'Prompt cards' }).click();
      assert.ok(page.url().endsWith('/prompts/'));
    }
    await page.locator('#consent-decline').click();
    await page.goto(new URL('setup/', base).href);
    const button = page.locator('.code-copy-button').first();
    await button.click();
    await page.waitForFunction(() => document.querySelector('.code-copy-button')?.dataset.state === 'copied');
    assert.ok((await page.evaluate(() => navigator.clipboard.readText())).trim().length > 20);
    await mkdir(path.join(directory, '.build'), { recursive: true });
    await page.screenshot({ path: path.join(directory, `.build/site-${viewport.width}.png`) });
    await page.evaluate(() => localStorage.removeItem('jdubois-analytics-consent'));
  }
  await page.goto(base);
  await page.locator('#consent-accept').click();
  await page.waitForFunction(() => document.querySelector('script[src*="googletagmanager.com/gtag/js"]'));
  assert.equal(await page.evaluate(() => localStorage.getItem('jdubois-analytics-consent')), 'granted');
  assert.equal(await page.evaluate(() => window['ga-disable-G-92TRR0HJMQ']), false);
  const second = await context.newPage();
  await second.goto(new URL('ticket/', base).href);
  assert.equal(await second.locator('#consent-banner').isVisible(), false, 'Shared decision was not reused');
  await page.locator('[data-consent-manage]').click();
  await page.locator('#consent-decline').click();
  await second.waitForFunction(() => window['ga-disable-G-92TRR0HJMQ'] === true);
  assert.equal(await page.evaluate(() => window['ga-disable-G-92TRR0HJMQ']), true);
  assert.equal(await page.evaluate(() => localStorage.getItem('jdubois-analytics-consent')), 'denied');
  assert.ok(analytics.length > 0, 'Acceptance did not attempt the consent-gated GA load');
  assert.deepEqual(errors, [], 'Browser script errors');
  console.log('Desktop/mobile theme, navigation, clipboard, shared consent and live revocation OK; GA requests blocked.');
} finally {
  if (browser) await browser.close();
  if (server) await new Promise(resolve => server.close(resolve));
}
