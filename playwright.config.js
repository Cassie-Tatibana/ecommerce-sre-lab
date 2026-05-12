const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./smoke",
  timeout: 60_000,
  use: {
    baseURL: "http://127.0.0.1:3000",
    headless: true,
    trace: "retain-on-failure",
  },
});
