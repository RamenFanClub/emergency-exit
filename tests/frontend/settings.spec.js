/**
 * F58 — Settings Tests
 * Check-in frequency stepper, grace period, notification protocol.
 */
const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault } = require('./helpers');

test.describe('Settings', () => {

  test.beforeEach(async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.click('#n-config');
  });

  test('check-in frequency defaults to 2 months', async ({ page }) => {
    await expect(page.locator('#fc')).toHaveText('2');
    await expect(page.locator('#fu')).toHaveText('Months');
  });

  test('can increase check-in frequency', async ({ page }) => {
    await page.locator('.cb').last().click(); // + button
    await expect(page.locator('#fc')).toHaveText('3');
  });

  test('can decrease check-in frequency', async ({ page }) => {
    await page.locator('.cb').first().click(); // − button
    await expect(page.locator('#fc')).toHaveText('1');
  });

  test('can switch frequency unit to Weeks', async ({ page }) => {
    await page.click('#tw');
    await expect(page.locator('#tw')).toHaveClass(/on/);
    await expect(page.locator('#fu')).toHaveText('Weeks');
  });

  test('grace period defaults to 7 days (F56)', async ({ page }) => {
    await expect(page.locator('#gp-val')).toHaveText('7');
  });

  test('can increase grace period', async ({ page }) => {
    // Grace period + button is the one inside the grace period card
    await page.locator('#gp-plus').click();
    await expect(page.locator('#gp-val')).toHaveText('8');
  });

  test('can decrease grace period', async ({ page }) => {
    await page.locator('#gp-minus').click();
    await expect(page.locator('#gp-val')).toHaveText('6');
  });

  test('notification protocol options are in plain English (F49)', async ({ page }) => {
    const text = await page.locator('#s-config').textContent();
    expect(text).toContain('Warn me first');
    expect(text).toContain('Notify contacts immediately');
    expect(text).toContain('one at a time');
  });

  test('settings changes persist to localStorage', async ({ page }) => {
    await page.locator('.cb').last().click(); // increase frequency to 3
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('ee_v3') || '{}'));
    expect(state.fc).toBe(3);
  });

});
