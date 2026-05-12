const { test, expect } = require("@playwright/test");

test("Grafana login page is reachable", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByLabel("Email or username")).toBeVisible();
  await expect(page.getByLabel("Password")).toBeVisible();
});

test("Provisioned dashboard is visible after login", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email or username").fill("admin");
  await page.getByLabel("Password").fill("admin");
  await page.getByRole("button", { name: "Log in" }).click();

  await page.waitForURL(/grafana|\/$/);
  await page.goto("/d/ecommerce-overview/e-commerce-supply-chain-overview");
  await expect(page.getByText("E-commerce Supply Chain Overview")).toBeVisible();
});
