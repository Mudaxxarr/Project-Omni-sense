import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

const playwrightRoot = path.resolve(
  process.cwd(),
  process.env.OMNISCIENCE_PLAYWRIGHT_ROOT ?? "../../output/playwright",
);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: true,
  retries: 0,
  reporter: [
    ["list"],
    [
      "junit",
      {
        outputFile: path.join(playwrightRoot, "phase0", "test-results.xml"),
      },
    ],
  ],
  timeout: 30_000,
  expect: {
    timeout: 5_000,
  },
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "on",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    ...devices["Desktop Chrome"],
    viewport: {
      width: 1440,
      height: 900,
    },
  },
  outputDir: path.join(playwrightRoot, "phase0", "test-results"),
});
