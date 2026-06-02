const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault } = require('./helpers');

test.describe('First-Run Explainer Card (F44)', () => {

  test('explainer card shows on first visit (no ee_onboarded flag)', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await expect(page.locator('#explainer-card')).toBeVisible();
  });

  test('explainer card is hidden when ee_onboarded is set', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await page.evaluate(() => localStorage.setItem('ee_onboarded', 'true'));
    await loginViaUI(page);
    await expect(page.locator('#explainer-card')).toBeHidden();
  });

  test('dismissing explainer sets ee_onboarded flag', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.locator('.ex-dismiss').click();
    const flag = await page.evaluate(() => localStorage.getItem('ee_onboarded'));
    expect(flag).toBe('true');
  });

  test('explainer stays hidden after page reload', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.locator('.ex-dismiss').click();
    // Re-mock before reload (routes reset on navigation)
    const { mockAPI, buildVault: bv } = require('./helpers');
    await mockAPI(page, { vault: bv() });
    await page.reload();
    await page.waitForSelector('#home-hero', { timeout: 8000 });
    await expect(page.locator('#explainer-card')).toBeHidden();
  });

});

test.describe('Pulse Card Explainer (F48)', () => {

  test('pulse explainer text shows before first check-in', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    const pulseExplainer = page.locator('#pulse-explainer');
    await expect(pulseExplainer).toBeVisible();
    const text = await pulseExplainer.textContent();
    expect(text).toContain('Check in');
  });

  test('pulse explainer is hidden after first check-in', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await page.evaluate(() => localStorage.setItem('ee_first_checkin_done', 'true'));
    await loginViaUI(page);
    await expect(page.locator('#pulse-explainer')).toHaveClass(/hidden/);
  });

});
