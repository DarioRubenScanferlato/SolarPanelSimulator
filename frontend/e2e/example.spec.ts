import { test, expect } from '@playwright/test';

test.describe('Solar Panel Simulator - Basic Smoke Tests', () => {
  test('page loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Solar/i);
  });

  test('Solar Simulation tab is visible', async ({ page }) => {
    await page.goto('/');
    const solarTab = page.locator('[data-tab="solar"]');
    await expect(solarTab).toBeVisible();
  });

  test('form inputs are present', async ({ page }) => {
    await page.goto('/');
    const latitudeInput = page.locator('input[aria-label*="Latitude"], input[placeholder*="latitude"], input[name*="latitude"]').first();
    const longitudeInput = page.locator('input[aria-label*="Longitude"], input[placeholder*="longitude"], input[name*="longitude"]').first();
    const simulateButton = page.locator('button:has-text("Simulate")').first();

    await expect(latitudeInput).toBeVisible();
    await expect(longitudeInput).toBeVisible();
    await expect(simulateButton).toBeVisible();
  });

  test('defaults are loaded on page load', async ({ page }) => {
    await page.goto('/');
    const latitudeInput = page.locator('input[aria-label*="Latitude"], input[placeholder*="latitude"], input[name*="latitude"]').first();
    const value = await latitudeInput.inputValue();
    expect(value).toBeTruthy();
  });

  test('Battery and Cost Analysis tabs are visible', async ({ page }) => {
    await page.goto('/');
    const batteryTab = page.locator('[data-tab="battery"]');
    const costTab = page.locator('[data-tab="cost"]');

    await expect(batteryTab).toBeVisible();
    await expect(costTab).toBeVisible();
  });
});
