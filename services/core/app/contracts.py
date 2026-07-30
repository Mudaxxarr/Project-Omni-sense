"""Stable Phase 0 API contracts."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

RequirementStatus = Literal["ready", "planned", "not_configured", "unavailable"]


class RequirementView(BaseModel):
    """A truthful readiness result for one local prerequisite."""

    model_config = ConfigDict(frozen=True)

    status: RequirementStatus
    detail: str


class PrerequisitesView(BaseModel):
    """Readiness state for the foundations required by later phases."""

    model_config = ConfigDict(frozen=True)

    core_api: RequirementView
    postgresql: RequirementView
    evidence_vault: RequirementView
    audit_chain: RequirementView
    retention_worker: RequirementView
    backup_restore: RequirementView


class DataConnectionView(BaseModel):
    """Operational source connection state."""

    model_config = ConfigDict(frozen=True)

    status: Literal["not_connected", "connected", "stale"]
    detail: str


class HealthView(BaseModel):
    """Versioned health contract shared with the desktop shell."""

    model_config = ConfigDict(frozen=True)

    contract_version: Literal["health.v1"] = "health.v1"
    service: Literal["omniscience-core"] = "omniscience-core"
    version: str
    mode: Literal["local"] = "local"
    status: Literal["healthy", "degraded"]
    local_only: Literal[True] = True
    cloud_inference_enabled: Literal[False] = False
    timezone: Literal["Asia/Karachi"] = "Asia/Karachi"
    checked_at: datetime
    prerequisites: PrerequisitesView
    data_connection: DataConnectionView
