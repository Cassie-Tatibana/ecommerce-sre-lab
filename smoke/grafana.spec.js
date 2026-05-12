const { test, expect } = require("@playwright/test");

const grafanaUsername = process.env.GRAFANA_USERNAME || "admin";
const grafanaPassword = process.env.GRAFANA_PASSWORD || "ecommerce-admin";

async function loginToGrafana(page) {
  await page.goto("/login");
  await page.getByLabel("Email or username").fill(grafanaUsername);
  await page.getByLabel("Password").fill(grafanaPassword);
  await page.getByRole("button", { name: "Log in" }).click();

  const skipPasswordChangeButton = page.getByRole("button", { name: /skip/i });
  if (await skipPasswordChangeButton.isVisible().catch(() => false)) {
    await skipPasswordChangeButton.click();
  }
}

test("Grafana login page is reachable", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByLabel("Email or username")).toBeVisible();
  await expect(page.getByLabel("Password")).toBeVisible();
});

test("Provisioned dashboard is visible after login", async ({ page }) => {
  await loginToGrafana(page);
  await page.goto("/d/ecommerce-overview");
  await expect(page.getByText("E-commerce Supply Chain Overview")).toBeVisible();
});
