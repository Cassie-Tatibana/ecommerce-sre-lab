const { test, expect } = require("@playwright/test");

test("Grafana login page is reachable", async ({ page }) => {
  const response = await page.goto("/login");
  expect(response).not.toBeNull();
  expect(response.ok()).toBeTruthy();
  await expect(page).toHaveURL(/\/login/);
});

test("Provisioned dashboard is visible", async ({ page }) => {
  const response = await page.goto("/d/ecommerce-overview");
  expect(response).not.toBeNull();
  expect(response.ok()).toBeTruthy();
  await expect(page).toHaveURL(/\/d\/ecommerce-overview/);
});
