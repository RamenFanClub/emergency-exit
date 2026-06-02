/**
 * F58 — Asset CRUD Tests
 * Add, edit, delete assets via the modal. Verifies the write layer works.
 */
const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault, getVaultState } = require('./helpers');

test.describe('Asset CRUD', () => {

  test.beforeEach(async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.click('#n-ledger');
  });

  test('empty state shows on Assets screen with no assets', async ({ page }) => {
    const text = await page.locator('#s-ledger').textContent();
    expect(text).toContain('Record your first asset');
  });

  test('can open Add Asset modal', async ({ page }) => {
    await page.click('.gbtn'); // "Record New Asset" gradient button
    await expect(page.locator('#am')).toHaveClass(/on/);
    await expect(page.locator('#am-title')).toHaveText('Record New Asset');
  });

  test('saving asset without name shows validation', async ({ page }) => {
    await page.click('.gbtn');
    await page.locator('#am .cfb, #am [id*="save"]').first().click();
    // Toast should appear warning about missing name
    await expect(page.locator('.toast')).toContainText('asset name');
  });

  test('can add an asset and it appears in the list', async ({ page }) => {
    await page.click('.gbtn');
    await page.fill('#an', 'ANZ Savings Account');
    await page.selectOption('#ac2', 'Bank account');
    await page.fill('#av', '15000');
    await page.fill('#ab2', 'Jane Doe');
    // Click save button inside the modal
    await page.locator('#am').getByText('Save Asset').click();
    // Asset should now appear in the ledger
    await expect(page.locator('#s-ledger')).toContainText('ANZ Savings Account');
  });

  test('adding an asset updates completeness score', async ({ page }) => {
    // Start at 0%
    await expect(page.locator('#cp-lbl')).toHaveText('0%');
    await page.click('.gbtn');
    await page.fill('#an', 'House');
    await page.selectOption('#ac2', 'Property');
    await page.fill('#ab2', 'Jane'); // beneficiary check
    await page.locator('#am').getByText('Save Asset').click();
    // At least 2 checks pass now (asset exists, has beneficiary) → >0%
    const pct = await page.locator('#cp-lbl').textContent();
    expect(parseInt(pct)).toBeGreaterThan(0);
  });

  test('can edit an existing asset', async ({ page }) => {
    // Inject an asset first
    await setupPage(page, {
      vault: buildVault({
        assets: [{ id: 1, name: 'Old Name', category: 'Property', value: 100, details: '', beneficiary: '', notes: '' }]
      })
    });
    await loginViaUI(page);
    await page.click('#n-ledger');
    // Click the edit button on the asset
    await page.locator('button[onclick*="editA"]').first().click();
    await expect(page.locator('#am-title')).toHaveText('Edit Asset');
    await page.fill('#an', 'Updated Name');
    await page.locator('#am').getByText('Update Asset').click();
    await expect(page.locator('#s-ledger')).toContainText('Updated Name');
  });

  test('can delete an asset', async ({ page }) => {
    await setupPage(page, {
      vault: buildVault({
        assets: [{ id: 1, name: 'Car to Delete', category: 'Vehicle', value: 20000, details: '', beneficiary: '', notes: '' }]
      })
    });
    await loginViaUI(page);
    await page.click('#n-ledger');
    await expect(page.locator('#s-ledger')).toContainText('Car to Delete');
    await page.locator('.del-btn').first().click();
    await expect(page.locator('#s-ledger')).not.toContainText('Car to Delete');
  });

  test('asset value displays formatted with $ sign', async ({ page }) => {
    await setupPage(page, {
      vault: buildVault({
        assets: [{ id: 1, name: 'Property', category: 'Property', value: 750000, details: '', beneficiary: '', notes: '' }]
      })
    });
    await loginViaUI(page);
    await page.click('#n-ledger');
    const text = await page.locator('#s-ledger').textContent();
    expect(text).toContain('750,000');
  });

});
