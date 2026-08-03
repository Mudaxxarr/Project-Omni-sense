import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const playwrightRoot = process.env.OMNISCIENCE_PLAYWRIGHT_ROOT ?? "../../output/playwright";
const artifactDir = path.resolve(process.cwd(), playwrightRoot, "phase0");

test.beforeAll(async () => {
  await mkdir(artifactDir, { recursive: true });
});

const viewports = [
  { name: "1280x720", width: 1280, height: 720 },
  { name: "1440x900", width: 1440, height: 900 },
  { name: "1920x1080", width: 1920, height: 1080 },
] as const;

const scenarios = ["live", "degraded", "stale", "loading", "error"] as const;

for (const scenario of scenarios) {
  for (const viewport of viewports) {
    test(`${scenario} state is safe at ${viewport.name}`, async ({ page }) => {
      const browserErrors: string[] = [];
      const networkErrors: string[] = [];
      page.on("console", (message) => {
        if (message.type() === "error") {
          browserErrors.push(message.text());
        }
      });
      page.on("pageerror", (error) => browserErrors.push(error.message));
      page.on("requestfailed", (request) => {
        networkErrors.push(
          `${request.method()} ${request.url()} ${request.failure()?.errorText ?? "failed"}`,
        );
      });
      page.on("response", (response) => {
        if (response.status() >= 400) {
          networkErrors.push(`${response.status()} ${response.url()}`);
        }
      });

      await page.setViewportSize(viewport);
      const query = scenario === "live" ? "" : `?state=${scenario}`;
      await page.goto(`/${query}`, { waitUntil: "networkidle" });

      await expect(page).toHaveTitle("OMNISCIENCE Command Centre");
      await expect(
        page.getByRole("heading", { name: "Good evening, Mudassar." }),
      ).toBeVisible();
      await expect(
        page.getByText("Local only. No data leaves this PC."),
      ).toBeVisible();

      const sourceSetup = page.getByRole("button", {
        name: "Start source setup",
      });
      if (scenario === "stale") {
        await expect(
          page.getByText("Data stale. Consequential controls are locked."),
        ).toBeVisible();
        await expect(sourceSetup).toBeDisabled();
      } else if (scenario === "error") {
        await expect(page.getByText("Health check failed")).toBeVisible();
        await expect(
          page.getByText(
            "Local readiness could not be verified. Consequential controls are locked.",
          ),
        ).toBeVisible();
        await expect(sourceSetup).toBeDisabled();
      } else if (scenario === "loading") {
        await expect(
          page.getByText("Checking the local trust boundary"),
        ).toBeVisible();
      } else {
        await expect(page.getByText("Data not connected")).toBeVisible();
        await expect(sourceSetup).toBeEnabled();
        if (scenario === "live") {
          await expect(
            page.getByText(
              "Native PostgreSQL 16 is accepting local connections.",
            ),
          ).toBeVisible();
          await expect(
            page.getByText(
              "The local database is ready. Connect a read-only source in the next build gate.",
            ),
          ).toBeVisible();
        } else {
          await expect(
            page.getByText(
              "Verification scenario: PostgreSQL readiness is intentionally unavailable.",
            ),
          ).toBeVisible();
          await expect(page.getByText("PostgreSQL setup required")).toBeVisible();
        }
      }

      const hasHorizontalOverflow = await page.evaluate(
        () =>
          document.documentElement.scrollWidth >
          document.documentElement.clientWidth,
      );
      expect(hasHorizontalOverflow).toBe(false);

      if (viewport.name === "1440x900") {
        const accessibility = await new AxeBuilder({ page }).analyze();
        const seriousViolations = accessibility.violations.filter(
          (violation) =>
            violation.impact === "serious" ||
            violation.impact === "critical",
        );
        expect(
          seriousViolations.map((violation) => ({
            id: violation.id,
            impact: violation.impact,
            help: violation.help,
          })),
        ).toEqual([]);
      }

      await page.screenshot({
        path: path.join(artifactDir, `${scenario}-${viewport.name}.png`),
      });

      if (scenario === "degraded" && viewport.name === "1440x900") {
        await sourceSetup.focus();
        await expect(sourceSetup).toBeFocused();
        await page.keyboard.press("Enter");
        const dialog = page.getByRole("dialog", { name: "Foundation first" });
        await expect(dialog).toBeVisible();
        await expect(
          dialog.getByText("PostgreSQL setup required"),
        ).toBeVisible();
        await page.screenshot({
          path: path.join(artifactDir, "source-setup-1440x900.png"),
        });
        await page.keyboard.press("Escape");
        await expect(dialog).toBeHidden();
      }

      expect(browserErrors).toEqual([]);
      expect(networkErrors).toEqual([]);
    });
  }
}
