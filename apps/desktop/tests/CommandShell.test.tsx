import { render, screen } from "@testing-library/react";

import { CommandShell } from "../src/app/CommandShell";
import type { HealthView } from "../src/app/contracts";


const healthyView: HealthView = {
  contract_version: "health.v1",
  service: "omniscience-core",
  version: "0.0.1",
  mode: "local",
  status: "degraded",
  local_only: true,
  cloud_inference_enabled: false,
  timezone: "Asia/Karachi",
  checked_at: "2026-07-29T15:00:00Z",
  prerequisites: {
    core_api: {
      status: "ready",
      detail: "Local core API is responding.",
    },
    postgresql: {
      status: "not_configured",
      detail: "Native PostgreSQL 16 has not been configured.",
    },
    storage_environment: {
      status: "not_configured",
      detail: "Fixture mode is active; protected PostgreSQL storage is not configured.",
    },
    evidence_vault: {
      status: "planned",
      detail: "Phase 1 capability.",
    },
    audit_chain: {
      status: "planned",
      detail: "Phase 1 capability.",
    },
    retention_worker: {
      status: "planned",
      detail: "Phase 1 capability.",
    },
    backup_restore: {
      status: "planned",
      detail: "Phase 1 capability.",
    },
  },
  data_connection: {
    status: "not_connected",
    detail: "No operational source is connected.",
  },
};


describe("CommandShell", () => {
  it("renders the owner spaces and honest local state", () => {
    render(<CommandShell health={healthyView} scenario="live" />);

    expect(screen.getByRole("link", { name: "Now" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Think" })).toBeVisible();
    expect(screen.getByRole("link", { name: "People" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Memory" })).toBeVisible();
    expect(
      screen.getByText("Local only. No data leaves this PC."),
    ).toBeVisible();
    expect(screen.getByText("PostgreSQL setup required")).toBeVisible();
    expect(screen.getByText("Secure storage configuration required")).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Start source setup" }),
    ).toBeDisabled();
  });

  it("locks consequential setup when the backend is stale", () => {
    render(<CommandShell health={null} scenario="stale" />);

    expect(
      screen.getByText("Data stale. Consequential controls are locked."),
    ).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Start source setup" }),
    ).toBeDisabled();
  });

  it("shows a distinct safe error state when health evidence is invalid", () => {
    render(<CommandShell health={null} scenario="error" />);

    expect(screen.getByText("Health check failed")).toBeVisible();
    expect(
      screen.getByText(
        "Local readiness could not be verified. Consequential controls are locked.",
      ),
    ).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Start source setup" }),
    ).toBeDisabled();
  });
});
