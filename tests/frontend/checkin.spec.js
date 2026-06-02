/**
 * F58 — Check-in Tests (F01, F51)
 */
const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault, buildFullVault } = require('./helpers');

test.describe('Check-in (Pulse Card)', () => {

  test('tapping pulse card on first ever check-in shows milestone modal (F51)', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    // Click the inner pulse button (the .vc circle), not the outer ring
    await page.locator('.vc').click();
    // Milestone modal uses style.display='flex' — check via style attribute
    await page.waitForFunction(() => {
      const el = document.getElementById('milestone-modal');
      return el && el.style.display === 'flex';
    }, { timeout: 5000 });
    await expect(page.locator('#milestone-modal')).toContainText("You're all set");
  });

  test('milestone modal can be dismissed', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await page.locator('.vc').click();
    await page.waitForFunction(() => {
      const el = document.getElementById('milestone-modal');
      return el && el.style.display === 'flex';
    }, { timeout: 5000 });
    await page.locator('.milestone-btn').click();
    // After dismiss, display goes back to 'none'
    await page.waitForFunction(() => {
      const el = document.getElementById('milestone-modal');
      return el && el.style.display === 'none';
    }, { timeout: 5000 });
  });

  test('check-in sets lastCheckin in localStorage', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    const before = await page.evaluate(() => {
      const s = JSON.parse(localStorage.getItem('ee_v3') || '{}');
      return s.lastCheckin;
    });
    expect(before).toBeNull();
    await page.locator('.vc').click();
    // Wait for save() to run
    await page.waitForTimeout(500);
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
    await page.locator('.vc').click();
    await page.waitForFunction(() => {
      const el = document.getElementById('milestone-modal');
      return el && el.style.display === 'flex';
    }, { timeout: 5000 });
    const flag = await page.evaluate(() => localStorage.getItem('ee_first_checkin_done'));
    expect(flag).toBe('true');
  });

  test('second check-in shows toast not milestone modal', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await page.evaluate(() => localStorage.setItem('ee_first_checkin_done', 'true'));
    await loginViaUI(page);
    await page.locator('.vc').click();
    // Milestone modal should NOT appear (display stays 'none')
    await page.waitForTimeout(300);
    const display = await page.evaluate(() => document.getElementById('milestone-modal').style.display);
    expect(display).not.toBe('flex');
    // Toast should appear
    await expect(page.locator('.toast')).toContainText('alive');
  });

  test('check-in from overdue state resets to green', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (90 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await page.evaluate(() => localStorage.setItem('ee_first_checkin_done', 'true'));
    await loginViaUI(page);
    await expect(page.locator('#overdue-banner')).toBeVisible();
    await page.locator('.vc').click();
    await expect(page.locator('#overdue-banner')).toBeHidden();
    await expect(page.locator('#home-hero')).toContainText('in order');
  });

  test('pulse card dims when completeness < 40% (F30)', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await expect(page.locator('#pulse-card')).toHaveClass(/pulse-dimmed/);
    await expect(page.locator('#pulse-hint')).toBeVisible();
  });

  test('pulse card not dimmed when completeness >= 40%', async ({ page }) => {
    await setupPage(page, { vault: buildFullVault() });
    await loginViaUI(page);
    await expect(page.locator('#pulse-card')).not.toHaveClass(/pulse-dimmed/);
  });

});
