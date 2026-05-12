const { test, expect } = require("@playwright/test");

test("Grafana login page is reachable", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByLabel("Email or username")).toBeVisible();
  await expect(page.getByLabel("Password")).toBeVisible();
});

test("Provisioned dashboard is visible", async ({ page }) => {
  await page.goto("/d/ecommerce-overview");
  await expect(page).toHaveURL(/\/d\/ecommerce-overview/);
  await expect(page.getByText("Order Status Distribution")).toBeVisible();
  await expect(page.getByText("Inventory Levels by SKU")).toBeVisible();
});
