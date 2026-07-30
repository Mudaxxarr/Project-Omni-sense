export type RequirementStatus =
  | "ready"
  | "planned"
  | "not_configured"
  | "unavailable";

export interface RequirementView {
  status: RequirementStatus;
  detail: string;
}

export interface HealthView {
  contract_version: "health.v1";
  service: "omniscience-core";
  version: string;
  mode: "local";
  status: "healthy" | "degraded";
  local_only: true;
  cloud_inference_enabled: false;
  timezone: "Asia/Karachi";
  checked_at: string;
  prerequisites: {
    core_api: RequirementView;
    postgresql: RequirementView;
    evidence_vault: RequirementView;
    audit_chain: RequirementView;
    retention_worker: RequirementView;
    backup_restore: RequirementView;
  };
  data_connection: {
    status: "not_connected" | "connected" | "stale";
    detail: string;
  };
}

export type HealthScenario =
  | "loading"
  | "live"
  | "degraded"
  | "stale"
  | "error";

export type ScenarioId =
  | "valid"
  | "stale"
  | "duplicate"
  | "contradictory"
  | "denied"
  | "degraded"
  | "timeout"
  | "recovery";

export type ScenarioStatus =
  | "ready"
  | "stale"
  | "review"
  | "blocked"
  | "denied"
  | "degraded"
  | "timeout"
  | "recovered";

export type FixtureFamily =
  | "users"
  | "roles"
  | "financial_imports"
  | "customers"
  | "visits"
  | "products"
  | "promises"
  | "tasks"
  | "evidence"
  | "meetings"
  | "provider_responses"
  | "model_outcomes";

export interface FixtureRecord {
  id: string;
  label: string;
  recorded_at_utc: string;
  attributes: Record<string, string | number | boolean | null>;
}

export interface ScenarioSummary {
  id: ScenarioId;
  label: string;
  status: ScenarioStatus;
}

export interface ScenarioView {
  contract_version: "scenario.v1";
  fixture_version: string;
  fixture_mode: true;
  anonymized: true;
  local_only: true;
  consequential_actions_enabled: false;
  action_lock_reason: string;
  scenario: ScenarioSummary & {
    headline: string;
    detail: string;
  };
  available_scenarios: ScenarioSummary[];
  clock: {
    deterministic: true;
    stored_at_utc: string;
    displayed_at_local: string;
    timezone: "Asia/Karachi";
  };
  summary: {
    entity_family_count: number;
    record_count: number;
  };
  entities: Record<FixtureFamily, FixtureRecord[]>;
  signals: string[];
}
