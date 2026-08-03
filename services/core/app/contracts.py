"""Stable Phase 0 API contracts."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

RequirementStatus = Literal["ready", "planned", "not_configured", "unavailable"]
ScenarioId = Literal[
    "valid",
    "stale",
    "duplicate",
    "contradictory",
    "denied",
    "degraded",
    "timeout",
    "recovery",
]
ScenarioStatus = Literal[
    "ready",
    "stale",
    "review",
    "blocked",
    "denied",
    "degraded",
    "timeout",
    "recovered",
]
FixtureAttribute = str | int | float | bool | None


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
    storage_environment: RequirementView
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


class FixtureRecord(BaseModel):
    """One anonymized record in the deterministic Phase 0 catalog."""

    model_config = ConfigDict(frozen=True)

    id: str
    label: str
    recorded_at_utc: datetime
    attributes: dict[str, FixtureAttribute]


class ScenarioSummary(BaseModel):
    """Stable navigation metadata for one fixture condition."""

    model_config = ConfigDict(frozen=True)

    id: ScenarioId
    label: str
    status: ScenarioStatus


class ScenarioDefinition(ScenarioSummary):
    """Visible interpretation of one deterministic fixture condition."""

    model_config = ConfigDict(frozen=True)

    headline: str
    detail: str


class ScenarioClock(BaseModel):
    """The fixed instant represented in UTC and owner-local time."""

    model_config = ConfigDict(frozen=True)

    deterministic: Literal[True] = True
    stored_at_utc: datetime
    displayed_at_local: datetime
    timezone: Literal["Asia/Karachi"] = "Asia/Karachi"


class ScenarioFixtureSummary(BaseModel):
    """Counts used to reconcile API and visible fixture facts."""

    model_config = ConfigDict(frozen=True)

    entity_family_count: int
    record_count: int


class ScenarioView(BaseModel):
    """Read-only, local-only Phase 0 scenario contract."""

    model_config = ConfigDict(frozen=True)

    contract_version: Literal["scenario.v1"] = "scenario.v1"
    fixture_version: str
    fixture_mode: Literal[True] = True
    anonymized: Literal[True] = True
    local_only: Literal[True] = True
    consequential_actions_enabled: Literal[False] = False
    action_lock_reason: str
    scenario: ScenarioDefinition
    available_scenarios: list[ScenarioSummary]
    clock: ScenarioClock
    summary: ScenarioFixtureSummary
    entities: dict[str, list[FixtureRecord]]
    signals: list[str]
