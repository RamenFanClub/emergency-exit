/**
 * F58 — Wishes CRUD + Will & Docs Tests
 */
const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault } = require('./helpers');

test.describe('Wishes CRUD', () => {

  test.beforeEach(async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.click('#n-wishes');
  });

  test('empty state shows on Wishes screen', async ({ page }) => {
    const text = await page.locator('#s-wishes').textContent();
    expect(text).toMatch(/wish|wish/i);
    // Empty state CTA should be present
    expect(text).toContain('Add a Wish');
  });

  test('can open Add Wish modal', async ({ page }) => {
    await page.locator('#s-wishes .gbtn').click();
    await expect(page.locator('#wm')).toHaveClass(/on/);
  });

  test('saving wish without title shows validation', async ({ page }) => {
    await page.locator('#s-wishes .gbtn').click();
    await page.locator('#wm').getByText('Save Wish').click();
    await expect(page.locator('.toast')).toContainText('wish');
  });

  test('can add a wish and it appears in the list', async ({ page }) => {
    await page.locator('#s-wishes .gbtn').click();
    await page.fill('#wt', 'Cremation preferred');
    await page.selectOption('#wp', 'high');
    await page.locator('#wm').getByText('Save Wish').click();
    await expect(page.locator('#s-wishes')).toContainText('Cremation preferred');
  });

  test('can delete a wish', async ({ page }) => {
    await setupPage(page, {
      vault: buildVault({
        wishes: [{ id: 1, category: 'Funeral & Service', title: 'Wish to delete', details: '', priority: 'medium' }]
      })
    });
    await loginViaUI(page);
    await page.click('#n-wishes');
    await expect(page.locator('#s-wishes')).toContainText('Wish to delete');
    await page.locator('#s-wishes .del-btn').first().click();
    await expect(page.locator('#s-wishes')).not.toContainText('Wish to delete');
  });

  test('Statement of Wishes nudge shows when SOW not recorded (F32)', async ({ page }) => {
    // No suppDocs with SOW type → nudge should be visible
    const text = await page.locator('#s-wishes').textContent();
    expect(text).toContain('Statement of Wishes');
  });

});

test.describe('Will & Legal Documents', () => {

  test('Will shows "Not recorded" by default', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.click('#n-wishes');
    await expect(page.locator('#will-badge')).toContainText('Not recorded');
  });

  test('Will badge shows "Signed & witnessed" after recording signed Will', async ({ page }) => {
    await setupPage(page, {
      vault: buildVault({
        will: { status: 'signed', date: '2024-01-01', solicitor: 'Smith & Co', loc1: 'Office', loc2: '', notes: '' }
      })
    });
    await loginViaUI(page);
    await page.click('#n-wishes');
    await expect(page.locator('#will-badge')).toContainText('Signed');
  });

});
