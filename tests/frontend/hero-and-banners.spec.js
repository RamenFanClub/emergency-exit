const { test, expect } = require('@playwright/test');
const { loginViaUI, setupPage, buildVault, buildFullVault } = require('./helpers');

test.describe('Hero Headline States (F45)', () => {

  test('empty vault shows "Let\'s get you set up."', async ({ page }) => {
    await setupPage(page, { vault: buildVault() });
    await loginViaUI(page);
    await expect(page.locator('#home-hero')).toContainText('set up');
  });

  test('partial vault (30-69%) with no contacts shows "You\'re making progress."', async ({ page }) => {
    // No contacts — F65 does not apply, so progress state fires normally
    const vault = buildVault({
      assets: [{ id: 1, name: 'House', category: 'Property', value: 500000, details: '', beneficiary: 'Jane', notes: '' }],
      wishes: [{ id: 2, category: 'Funeral & Service', title: 'Cremation', details: '', priority: 'high' }],
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#home-hero')).toContainText('progress');
  });

  test('partial vault (30-69%) with a contact but no check-in shows amber "Almost there" (F65)', async ({ page }) => {
    // F65: once a contact exists, badge/hero escalates to amber "check in" nudge regardless of completeness %
    const vault = buildVault({
      assets: [{ id: 1, name: 'House', category: 'Property', value: 500000, details: '', beneficiary: 'Jane', notes: '' }],
      wishes: [{ id: 2, category: 'Funeral & Service', title: 'Cremation', details: '', priority: 'high' }],
      kin: [{ id: 3, first: 'Jane', last: 'Doe', rel: 'Partner', email: 'j@t.com', phone: '', notifyVia: 'email', order: 1, letter: '' }],
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#home-hero')).toContainText('Almost there');
  });

  test('complete vault without check-in shows amber "Almost there"', async ({ page }) => {
    await setupPage(page, { vault: buildFullVault({ lastCheckin: null }) });
    await loginViaUI(page);
    await expect(page.locator('#home-hero')).toContainText('Almost there');
  });

  test('complete vault with check-in shows "Your light is on."', async ({ page }) => {
    await setupPage(page, { vault: buildFullVault() });
    await loginViaUI(page);
    await expect(page.locator('#home-hero')).toContainText('Your light is on');
  });

  test('overdue vault with contacts shows red "Action needed."', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (90 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#home-hero')).toContainText('Action needed');
  });

});

test.describe('Overdue Banner (F01)', () => {

  test('overdue banner is visible when grace period expired', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (90 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#overdue-banner')).toBeVisible();
  });

  test('overdue banner is hidden when not overdue', async ({ page }) => {
    await setupPage(page, { vault: buildFullVault() });
    await loginViaUI(page);
    await expect(page.locator('#overdue-banner')).toBeHidden();
  });

  test('overdue banner contains cancellation reassurance (F50)', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (90 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    const bannerText = await page.locator('#overdue-banner').textContent();
    expect(bannerText).toContain('cancel');
  });

});

test.describe('Reminder Banner (F05)', () => {

  test('reminder banner shows when check-in is due soon', async ({ page }) => {
    // 50 days ago on a 2-month (60-day) window = 10 days left, inside 25% (15-day) amber window
    const vault = buildFullVault({
      lastCheckin: Date.now() - (50 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#reminder-banner')).toBeVisible();
  });

  test('reminder banner is hidden when check-in is not due soon', async ({ page }) => {
    await setupPage(page, { vault: buildFullVault() });
    await loginViaUI(page);
    await expect(page.locator('#reminder-banner')).toBeHidden();
  });

});

test.describe('Grace Period Banner (F98)', () => {
  // Default vault: 2-month (60-day) interval + 7-day grace = 67-day overdue threshold.
  // The grace window is the gap between day 60 (due date) and day 67 (overdue threshold).

  test('grace banner shows once the due date has passed but grace has not expired', async ({ page }) => {
    // 63 days ago: 3 days past due date, 4 days before grace expires
    const vault = buildFullVault({
      lastCheckin: Date.now() - (63 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#grace-banner')).toBeVisible();
    await expect(page.locator('#overdue-banner')).toBeHidden();
    await expect(page.locator('#reminder-banner')).toBeHidden();
  });

  test('grace banner is hidden before the due date (reminder window instead)', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (50 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#grace-banner')).toBeHidden();
  });

  test('grace banner is hidden once truly overdue (overdue banner instead)', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (90 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#grace-banner')).toBeHidden();
    await expect(page.locator('#overdue-banner')).toBeVisible();
  });

  test('hero headline reads "flickering" during the grace period', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (63 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#home-hero')).toContainText('flickering');
  });

  test('status badge reads "Grace Period" during the grace period', async ({ page }) => {
    const vault = buildFullVault({
      lastCheckin: Date.now() - (63 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#status-badge')).toContainText('Grace Period');
  });

  test('pulse card title reads "Grace period active" and days label reflects days until notified', async ({ page }) => {
    // 63 days ago -> graceEnd at day 67 -> 4 days until contacts notified
    const vault = buildFullVault({
      lastCheckin: Date.now() - (63 * 24 * 60 * 60 * 1000),
    });
    await setupPage(page, { vault });
    await loginViaUI(page);
    await expect(page.locator('#pulse-title')).toHaveText('Grace period active');
    await expect(page.locator('#days-label')).toContainText('until notified');
  });

});
