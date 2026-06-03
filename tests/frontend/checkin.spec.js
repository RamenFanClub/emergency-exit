/**
 * F58 — Check-in Tests (F01, F51)
 *
 * KEY INSIGHT: The onclick="checkin()" is on the .vr div (outer ring),
 * not .vc (inner circle). We call checkin() directly via page.evaluate()
 * to avoid any click interception issues with the animated overlay.
 *
 * The milestone modal visibility is controlled via style.display (not CSS class),
 * so we check the style attribute directly rather than using toBeVisible().
 */
const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault, buildFullVault } = require('./helpers');

// Helper: call checkin() directly in the browser and wait for side effects
async function doCheckin(page) {
  await page.evaluate(() => window.checkin());
  await page.waitForTimeout(200); // allow synchronous DOM updates to render
}

// Helper: get milestone modal display style
async function milestoneDisplay(page) {
  return page.evaluate(() => document.getElementById('milestone-modal').style.display);
}

test.describe('Check-in (Pulse Card)', () => {

  test('tapping pulse card on first ever check-in shows milestone modal (F51)', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await doCheckin(page);
    const display = await milestoneDisplay(page);
    expect(display).toBe('flex');
    await expect(page.locator('#milestone-modal')).toContainText("You're all set");
  });

  test('milestone modal can be dismissed', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await doCheckin(page);
    expect(await milestoneDisplay(page)).toBe('flex');
    await page.locator('.milestone-btn').click();
    await page.waitForTimeout(400); // dismissMilestone() has a 250ms fade
    expect(await milestoneDisplay(page)).toBe('none');
  });

  test('check-in sets lastCheckin in localStorage', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    const before = await page.evaluate(() => JSON.parse(localStorage.getItem('ee_v3') || '{}').lastCheckin);
    expect(before).toBeNull();
    await doCheckin(page);
    await page.waitForTimeout(300);
    const after = await page.evaluate(() => JSON.parse(localStorage.getItem('ee_v3') || '{}').lastCheckin);
    expect(after).not.toBeNull();
    expect(after).toBeGreaterThan(0);
  });

  test('check-in sets ee_first_checkin_done flag', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await doCheckin(page);
    expect(await milestoneDisplay(page)).toBe('flex'); // confirms checkin() fired
    const flag = await page.evaluate(() => localStorage.getItem('ee_first_checkin_done'));
    expect(flag).toBe('true');
  });

  test('second check-in shows toast not milestone modal', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await page.evaluate(() => localStorage.setItem('ee_first_checkin_done', 'true'));
    await loginViaUI(page);
    await doCheckin(page);
    // Milestone modal should NOT appear
    expect(await milestoneDisplay(page)).not.toBe('flex');
    // Toast text is set synchronously — check immediately
    const toastText = await page.evaluate(() => document.getElementById('toast').textContent);
    expect(toastText).toContain('alive');
  });

  test('check-in from overdue state resets to green', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (90 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await page.evaluate(() => localStorage.setItem('ee_first_checkin_done', 'true'));
    await loginViaUI(page);
    await expect(page.locator('#overdue-banner')).toBeVisible();
    await doCheckin(page);
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
