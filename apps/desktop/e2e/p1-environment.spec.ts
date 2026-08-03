import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const playwrightRoot = process.env.OMNISCIENCE_PLAYWRIGHT_ROOT ?? "../../output/playwright";
const artifactDir = path.resolve(process.cwd(), playwrightRoot, "p1-environment");

const viewports = [
  { name: "1280x720", width: 1280, height: 720 },
  { name: "1440x900", width: 1440, height: 900 },
  { name: "1920x1080", width: 1920, height: 1080 },
] as const;

test.beforeAll(async () => {
  await mkdir(artifactDir, { recursive: true });
});

for (const viewport of viewports) {
  test(`fixture storage configuration stays locked at ${viewport.name}`, async ({
    page,
  }) => {
    const browserErrors: string[] = [];
    const networkErrors: string[] = [];
    page.on("console", (message) => {
      if (message.type() === "error") {
        browserErrors.push(message.text());
      }
    });
    page.on("pageerror", (error) => browserErrors.push(error.message));
    page.on("requestfailed", (request) => {
      networkErrors.push(`${request.method()} ${request.url()}`);
    });

    await page.setViewportSize(viewport);
    await page.goto("/", { waitUntil: "networkidle" });

    await expect(page.getByText("Data not connected")).toBeVisible();
    await expect(
      page.getByText("Secure storage configuration required"),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Start source setup" }),
    ).toBeDisabled();

    const healthResponse = await page.request.get(
      "http://127.0.0.1:8765/v1/health",
    );
    expect(healthResponse.status()).toBe(200);
    const health = await healthResponse.json();
    expect(health.prerequisites.postgresql.status).toBe("ready");
    expect(health.prerequisites.storage_environment.status).toBe(
      "not_configured",
    );

    const hasHorizontalOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    expect(hasHorizontalOverflow).toBe(false);
    expect(browserErrors).toEqual([]);
    expect(networkErrors).toEqual([]);

    await page.screenshot({
      path: path.join(artifactDir, `fixture-${viewport.name}.png`),
    });
  });
}
