import { expect, test } from '@playwright/test';

test('Odoo 19 questions, citations, feedback and session isolation without a version selector', async ({ page }) => {
  const browserErrors: string[] = [];
  page.on('pageerror', error => browserErrors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Welcome to Fieldguide' })).toBeVisible();
  await page.getByLabel('Pilot access key').fill('test-internal-access-key-123456789');
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await expect(page.getByLabel('Your Odoo task', { exact: true })).toBeVisible();
  await expect(page.getByRole('combobox')).toHaveCount(0);
  await expect(page.locator('.supported-version')).toHaveText('Odoo 19');
  await page.getByLabel('Your Odoo task', { exact: true }).fill('How do I invoice delivered quantities?');
  const pending = page.waitForResponse(response => response.url().endsWith('/api/answers'));
  await page.getByRole('button', { name: 'Ask Fieldguide' }).click();
  expect((await pending).request().postDataJSON().odoo_version).toBe('19.0');
  await expect(page.getByText('Validate the delivery before creating the invoice.', { exact: true })).toBeVisible();
  await page.locator('.evidence summary').click();
  await expect(page.getByRole('link', { name: 'Read Odoo documentation' })).toHaveAttribute('href', /documentation\/19\.0\/en\//);
  await expect(page.getByRole('link', { name: 'Pinned source' })).toHaveAttribute('href', /c9202e68/);
  await page.locator('.feedback summary').last().click();
  await page.getByLabel('Partially solved', { exact: true }).last().check();
  await page.getByLabel('Correction or comment').last().fill('Need the next backorder step.');
  await page.getByRole('button', { name: 'Save feedback' }).last().click();
  await expect(page.getByText('Feedback saved. Thank you.')).toBeVisible();
  await page.reload();
  await expect(page.getByText('Feedback recorded', { exact: false })).toBeVisible();
  await expect(page.getByRole('combobox')).toHaveCount(0);
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome to Fieldguide' })).toBeVisible();
  await page.getByLabel('Pilot access key').fill('test-other-access-key-123456789');
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await expect(page.getByRole('heading', { name: 'What are you working on?' })).toBeVisible();
  await expect(page.locator('.supported-version')).toHaveText('Odoo 19');
  await expect(page.getByRole('combobox')).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'How do I invoice delivered quantities?' })).toHaveCount(0);
  expect(browserErrors).toEqual([]);
});

test('mobile layout and recoverable provider errors', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await page.getByLabel('Pilot access key').fill('test-internal-access-key-123456789');
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await expect(page.getByLabel('Your Odoo task', { exact: true })).toBeVisible();
  await expect(page.getByRole('combobox')).toHaveCount(0);
  await page.route('**/api/answers', route => route.fulfill({ status: 503,
    contentType: 'application/json', body: JSON.stringify({ detail: { message: 'Please retry.', request_id: 'test-failure' } }) }));
  await page.getByLabel('Your Odoo task', { exact: true }).fill('How do I process a return?');
  await page.getByRole('button', { name: 'Ask Fieldguide' }).click();
  await expect(page.getByRole('alert')).toContainText('test-failure');
  await expect(page.getByRole('button', { name: 'Ask Fieldguide' })).toBeEnabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: 'test-results/mobile-pilot.png', fullPage: true });
});
