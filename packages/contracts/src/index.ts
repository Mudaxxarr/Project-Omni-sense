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
