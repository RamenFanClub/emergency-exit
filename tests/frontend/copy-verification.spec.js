const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault } = require('./helpers');

test.describe('Copy & Label Verification', () => {

  test.beforeEach(async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
  });

  test('Assets screen title says "My Assets" (F53)', async ({ page }) => {
    await page.click('#n-ledger');
    // .st is the screen title class in the app
    await expect(page.locator('#s-ledger .st').first()).toContainText('My Assets');
  });

  test('Nav label for assets says "Assets" not "Ledger" (F53)', async ({ page }) => {
    // Nav labels use class .l inside .ni
    await expect(page.locator('#n-ledger .l')).toHaveText('Assets');
  });

  test('Wishes screen CTA says "Add a Wish" (F54)', async ({ page }) => {
    await page.click('#n-wishes');
    // Find any button/element in the wishes screen containing "Add a Wish"
    const cta = page.locator('#s-wishes').getByText('Add a Wish').first();
    await expect(cta).toBeVisible();
  });

  test('Settings shows grace period default of 7 days (F56)', async ({ page }) => {
    await page.click('#n-config');
    await expect(page.locator('#gp-val')).toHaveText('7');
  });

  test('Privacy note mentions cloud storage (F31)', async ({ page }) => {
    const text = await page.locator('#s-home').textContent();
    expect(text).toContain('cloud');
  });

  test('Contacts screen shows what contacts will receive (F46)', async ({ page }) => {
    await page.click('#n-kin');
    // The ib2 info box on the contacts screen describes the full package
    const infoBox = page.locator('#s-kin .ib2');
    const text = await infoBox.textContent();
    expect(text.toLowerCase()).toContain('full package');
  });

});
