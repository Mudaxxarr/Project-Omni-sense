import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { ScenarioLab } from "../src/app/ScenarioLab";
import type { ScenarioView } from "../src/app/contracts";

const view: ScenarioView = {
  contract_version: "scenario.v1",
  fixture_version: "phase0-fixtures.v1",
  fixture_mode: true,
  anonymized: true,
  local_only: true,
  consequential_actions_enabled: false,
  action_lock_reason: "Fixture-only data cannot authorize real actions.",
  scenario: {
    id: "valid",
    label: "Valid",
    status: "ready",
    headline: "Fixture inputs agree",
    detail: "All deterministic fixture records pass their contract checks.",
  },
  available_scenarios: [
    {
      id: "valid",
      label: "Valid",
      status: "ready",
    },
    {
      id: "stale",
      label: "Stale",
      status: "stale",
    },
  ],
  clock: {
    deterministic: true,
    stored_at_utc: "2026-07-29T12:00:00Z",
    displayed_at_local: "2026-07-29T17:00:00+05:00",
    timezone: "Asia/Karachi",
  },
  summary: {
    entity_family_count: 12,
    record_count: 12,
  },
  entities: {
    users: [],
    roles: [],
    financial_imports: [],
    customers: [],
    visits: [],
    products: [],
    promises: [],
    tasks: [],
    evidence: [],
    meetings: [],
    provider_responses: [],
    model_outcomes: [],
  },
  signals: ["Deterministic input accepted."],
};

describe("ScenarioLab", () => {
  it("shows fixture boundaries, deterministic time, and every entity family", () => {
    render(
      <ScenarioLab
        error={null}
        loading={false}
        onSelect={vi.fn()}
        view={view}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Deterministic Scenario Lab" }),
    ).toBeVisible();
    expect(screen.getByText("Anonymized fixture data")).toBeVisible();
    expect(screen.getByText("2026-07-29T12:00:00Z")).toBeVisible();
    expect(screen.getByText("29 Jul 2026, 17:00 PKT")).toBeVisible();
    expect(screen.getByText("12 entity families")).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Consequential actions locked" }),
    ).toBeDisabled();
    expect(screen.getByText("Financial imports")).toBeVisible();
    expect(screen.getByText("Provider responses")).toBeVisible();
    expect(screen.getByText("Model outcomes")).toBeVisible();
  });

  it("lets the owner select another deterministic scenario", () => {
    const onSelect = vi.fn();
    render(
      <ScenarioLab
        error={null}
        loading={false}
        onSelect={onSelect}
        view={view}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Stale" }));

    expect(onSelect).toHaveBeenCalledWith("stale");
  });

  it("fails closed when scenario evidence is unavailable", () => {
    render(
      <ScenarioLab
        error="Scenario contract unavailable."
        loading={false}
        onSelect={vi.fn()}
        view={null}
      />,
    );

    expect(screen.getByText("Scenario evidence unavailable")).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Consequential actions locked" }),
    ).toBeDisabled();
  });
});
