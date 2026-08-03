import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const playwrightRoot = process.env.OMNISCIENCE_PLAYWRIGHT_ROOT ?? "../../output/playwright";
const artifactDir = path.resolve(process.cwd(), playwrightRoot, "phase0-scenarios");

test.beforeAll(async () => {
  await mkdir(artifactDir, { recursive: true });
});

const viewports = [
  { name: "1280x720", width: 1280, height: 720 },
  { name: "1440x900", width: 1440, height: 900 },
  { name: "1920x1080", width: 1920, height: 1080 },
] as const;

const scenarios = [
  "valid",
  "stale",
  "duplicate",
  "contradictory",
  "denied",
  "degraded",
  "timeout",
  "recovery",
] as const;

interface ScenarioApiProof {
  scenario: {
    id: string;
  };
  consequential_actions_enabled: boolean;
  clock: {
    stored_at_utc: string;
    displayed_at_local: string;
  };
  summary: {
    entity_family_count: number;
    record_count: number;
  };
  entities: Record<string, unknown[]>;
}

for (const scenario of scenarios) {
  for (const viewport of viewports) {
    test(`${scenario} fixture is safe at ${viewport.name}`, async ({ page }) => {
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
      await page.goto(`/?scenario=${scenario}`, { waitUntil: "networkidle" });

      await expect(page).toHaveTitle("OMNISCIENCE Command Centre");
      await expect(
        page.getByRole("heading", { name: "Deterministic Scenario Lab" }),
      ).toBeVisible();
      await expect(page.getByText("Anonymized fixture data")).toBeVisible();
      await expect(page.getByText("12 entity families")).toBeVisible();
      await expect(page.getByText("2026-07-29T12:00:00Z")).toBeVisible();
      await expect(page.getByText("29 Jul 2026, 17:00 PKT")).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Consequential actions locked" }),
      ).toBeDisabled();
      await expect(
        page.getByRole("button", {
          name: new RegExp(`^${scenario}$`, "i"),
        }),
      ).toHaveAttribute("aria-pressed", "true");

      const apiResponse = await page.request.get(
        `http://127.0.0.1:8765/v1/scenarios/${scenario}`,
      );
      expect(apiResponse.status()).toBe(200);
      const apiProof = (await apiResponse.json()) as ScenarioApiProof;
      expect(apiProof.scenario.id).toBe(scenario);
      expect(apiProof.consequential_actions_enabled).toBe(false);
      await expect(
        page.getByText(
          `${apiProof.summary.entity_family_count} entity families`,
        ),
      ).toBeVisible();
      await expect(
        page.getByText(`${apiProof.summary.record_count} deterministic`),
      ).toBeVisible();
      await expect(page.getByText(apiProof.clock.stored_at_utc)).toBeVisible();
      for (const [family, records] of Object.entries(apiProof.entities)) {
        await expect(
          page.locator(`[data-family="${family}"] strong`),
        ).toHaveText(String(records.length));
      }

      const hasHorizontalOverflow = await page.evaluate(
        () =>
          document.documentElement.scrollWidth >
          document.documentElement.clientWidth,
      );
      expect(hasHorizontalOverflow).toBe(false);
      const hasVerticalOverflow = await page.evaluate(
        () =>
          document.documentElement.scrollHeight >
          document.documentElement.clientHeight,
      );
      expect(hasVerticalOverflow).toBe(false);

      if (viewport.name === "1440x900") {
        const accessibility = await new AxeBuilder({ page }).analyze();
        expect(
          accessibility.violations
            .filter(
              (violation) =>
                violation.impact === "serious" ||
                violation.impact === "critical",
            )
            .map((violation) => violation.id),
        ).toEqual([]);
      }

      await page.screenshot({
        path: path.join(artifactDir, `${scenario}-${viewport.name}.png`),
      });

      expect(browserErrors).toEqual([]);
      expect(networkErrors).toEqual([]);
    });
  }
}

test("scenario switch changes the visible API-backed state", async ({ page }) => {
  await page.goto("/?scenario=valid", { waitUntil: "networkidle" });

  await expect(
    page.getByRole("button", { name: "Valid" }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Stale" }).click();

  await expect(page).toHaveURL(/\?scenario=stale$/);
  await expect(
    page.getByRole("heading", { name: "Fixture source is stale" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Stale" }),
  ).toHaveAttribute("aria-pressed", "true");
});
