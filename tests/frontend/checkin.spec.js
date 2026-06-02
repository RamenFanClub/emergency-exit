/**
 * F58 — Check-in Tests (F01, F51)
 * Tapping the pulse card, milestone modal, and state changes.
 */
const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault, buildFullVault } = require('./helpers');

test.describe('Check-in (Pulse Card)', () => {

  test('tapping pulse card on first ever check-in shows milestone modal (F51)', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    // No ee_first_checkin_done flag = first check-in
    await page.locator('.vr').click();
    await expect(page.locator('#milestone-modal')).toBeVisible();
    await expect(page.locator('#milestone-modal')).toContainText("You're all set");
  });

  test('milestone modal can be dismissed', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.locator('.vr').click();
    await expect(page.locator('#milestone-modal')).toBeVisible();
    await page.locator('.milestone-btn').click();
    await expect(page.locator('#milestone-modal')).toBeHidden();
  });

  test('check-in sets lastCheckin in localStorage', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    const before = await page.evaluate(() => {
      const s = JSON.parse(localStorage.getItem('ee_v3') || '{}');
      return s.lastCheckin;
    });
    expect(before).toBeNull();
    await page.locator('.vr').click();
    const after = await page.evaluate(() => {
      const s = JSON.parse(localStorage.getItem('ee_v3') || '{}');
      return s.lastCheckin;
    });
    expect(after).not.toBeNull();
    expect(after).toBeGreaterThan(0);
  });

  test('check-in sets ee_first_checkin_done flag', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.locator('.vr').click();
    const flag = await page.evaluate(() => localStorage.getItem('ee_first_checkin_done'));
    expect(flag).toBe('true');
  });

  test('second check-in shows toast not milestone modal', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    // Already checked in before
    await page.evaluate(() => localStorage.setItem('ee_first_checkin_done', 'true'));
    await loginViaUI(page);
    await page.locator('.vr').click();
    // Milestone modal should NOT appear
    await expect(page.locator('#milestone-modal')).toBeHidden();
    // Toast should appear instead
    await expect(page.locator('.toast')).toContainText('alive');
  });

  test('check-in from overdue state resets to green', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (90 * 24 * 60 * 60 * 1000), // 90 days ago = overdue
    });
    await setupPage(page, { vault });
    await page.evaluate(() => localStorage.setItem('ee_first_checkin_done', 'true'));
    await loginViaUI(page);
    // Should start overdue
    await expect(page.locator('#overdue-banner')).toBeVisible();
    // Check in
    await page.locator('.vr').click();
    // Overdue banner should disappear
    await expect(page.locator('#overdue-banner')).toBeHidden();
    // Hero should update
    await expect(page.locator('#home-hero')).toContainText('in order');
  });

  test('pulse card dims when completeness < 40% (F30)', async ({ page }) => {
    await setupPage(page, { vault: buildVault() }); // 0% completeness
    await loginViaUI(page);
    await expect(page.locator('#pulse-card')).toHaveClass(/pulse-dimmed/);
    await expect(page.locator('#pulse-hint')).toBeVisible();
  });

  test('pulse card not dimmed when completeness >= 40%', async ({ page }) => {
    await setupPage(page, { vault: buildFullVault() }); // 100% completeness
    await loginViaUI(page);
    await expect(page.locator('#pulse-card')).not.toHaveClass(/pulse-dimmed/);
  });

});
