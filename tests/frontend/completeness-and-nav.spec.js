const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault, buildFullVault } = require('./helpers');

test.describe('Completeness Score', () => {

  test('empty vault shows 0%', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await expect(page.locator('#cp-lbl')).toHaveText('0%');
  });

  test('full vault shows 100%', async ({ page }) => {
    await setupPage(page, { vault: buildFullVault() });
    await loginViaUI(page);
    await expect(page.locator('#cp-lbl')).toHaveText('100%');
  });

  test('partial vault shows correct percentage', async ({ page }) => {
    // 3 checks pass: asset exists, asset has beneficiary, contact exists → 43%
    const vault = buildVault({
      assets: [{ id: 1, name: 'House', category: 'Property', value: 500000, details: '', beneficiary: 'Jane', notes: '' }],
      kin: [{ id: 2, first: 'Jane', last: 'Doe', rel: 'Partner', email: 'j@t.com', phone: '', notifyVia: 'email', order: 1, letter: '' }],
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#cp-lbl')).toHaveText('43%');
  });

  test('progress bar width matches percentage', async ({ page }) => {
    await setupPage(page, { vault: buildFullVault() });
    await loginViaUI(page);
    const width = await page.locator('#cp-bar').evaluate((el) => el.style.width);
    expect(width).toBe('100%');
  });

  test('completeness tips show for incomplete vault', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    const tips = page.locator('#cp-tips');
    const text = await tips.textContent();
    expect(text.length).toBeGreaterThan(0);
  });

});

test.describe('Navigation', () => {

  // Shared login — all nav tests use same vault state
  test.beforeEach(async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
  });

  test('Home screen is visible by default after login', async ({ page }) => {
    await expect(page.locator('#s-home')).toBeVisible();
  });

  test('can navigate to Assets screen', async ({ page }) => {
    await page.click('#n-ledger');
    await expect(page.locator('#s-ledger')).toBeVisible();
    await expect(page.locator('#s-home')).toBeHidden();
  });

  test('can navigate to Wishes screen', async ({ page }) => {
    await page.click('#n-wishes');
    await expect(page.locator('#s-wishes')).toBeVisible();
    await expect(page.locator('#s-home')).toBeHidden();
  });

  test('can navigate to Contacts screen', async ({ page }) => {
    // Contacts nav ID is n-kin, screen ID is s-kin
    await page.click('#n-kin');
    await expect(page.locator('#s-kin')).toBeVisible();
    await expect(page.locator('#s-home')).toBeHidden();
  });

  test('can navigate to Settings screen', async ({ page }) => {
    // Settings nav ID is n-config, screen ID is s-config
    await page.click('#n-config');
    await expect(page.locator('#s-config')).toBeVisible();
    await expect(page.locator('#s-home')).toBeHidden();
  });

  test('can navigate back to Home from another screen', async ({ page }) => {
    await page.click('#n-config');
    await expect(page.locator('#s-config')).toBeVisible();
    await page.click('#n-home');
    await expect(page.locator('#s-home')).toBeVisible();
    await expect(page.locator('#s-config')).toBeHidden();
  });

});
