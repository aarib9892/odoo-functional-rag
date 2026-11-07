// Explicit, metered local browser → API → real provider check. Not part of npm test.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { chromium } from 'playwright';

const config = await readFile(new URL('../../backend/.env.pilot', import.meta.url), 'utf8');
function value(name) {
  const line = config.split('\n').find(line => line.startsWith(`${name}=`));
  return line?.slice(name.length + 1).trim().replace(/^(['"])(.*)\1$/, '$2');
}
const origin = value('PILOT_PUBLIC_ORIGIN') || 'http://localhost:8000';
assert.equal(new URL(origin).hostname, 'localhost', 'This smoke script is restricted to localhost.');
const key = Object.values(JSON.parse(value('PILOT_ACCESS_KEYS') || '{}'))[0];
assert.equal(typeof key, 'string', 'Configure local pilot credentials first.');
const directory = new URL('../../data/pilot/browser/', import.meta.url);
await mkdir(directory, { recursive: true });
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(origin);
  await page.getByLabel('Pilot access key').fill(key);
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await page.getByLabel('Your Odoo task', { exact: true }).waitFor({ state: 'visible' });
  assert.equal(await page.getByRole('combobox').count(), 0);
  await page.getByLabel('Your Odoo task', { exact: true }).fill(
    'I changed Sales settings to Invoice what is delivered. Do existing products change automatically, and where do I update them?');
  const pending = page.waitForResponse(response => response.url().endsWith('/api/answers'), { timeout: 70000 });
  await page.getByRole('button', { name: 'Ask Fieldguide' }).click();
  const response = await pending;
  const answer = await response.json();
  assert.equal(response.status(), 200);
  assert.equal(answer.status, 'answered');
  assert.ok(answer.claims.length > 0 && answer.citations.length > 0);
  assert.equal(answer.trace.validation, 'citations_and_model_support_review_passed');
  assert.ok(answer.trace.embedding.cache_hit, 'This development question should reuse its saved embedding.');
  await page.locator('.evidence summary').first().click();
  await page.screenshot({ path: new URL('live-desktop.png', directory).pathname, fullPage: true });
  await writeFile(new URL('live-result.json', directory), JSON.stringify({
    kind: 'engineering_browser_smoke_not_operations_task_result', ...answer,
  }, null, 2), { mode: 0o600 });
  assert.deepEqual(errors, []);
  await page.getByRole('button', { name: 'Sign out' }).click();
  console.log(JSON.stringify({ status: answer.status, citations: answer.citations.length,
    latency_ms: answer.trace.latency_ms, query_cache_hit: answer.trace.embedding.cache_hit,
    report: 'data/pilot/browser/live-result.json' }));
} finally { await browser.close(); }
