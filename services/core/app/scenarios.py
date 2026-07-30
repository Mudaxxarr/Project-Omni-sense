"""Deterministic, anonymized Phase 0 scenario fixtures."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from services.core.app.contracts import (
    FixtureRecord,
    ScenarioClock,
    ScenarioDefinition,
    ScenarioFixtureSummary,
    ScenarioSummary,
    ScenarioView,
)

CATALOG_PATH = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "scenario-catalog.v1.json"
)
EXPECTED_ENTITY_FAMILIES = {
    "users",
    "roles",
    "financial_imports",
    "customers",
    "visits",
    "products",
    "promises",
    "tasks",
    "evidence",
    "meetings",
    "provider_responses",
    "model_outcomes",
}

KARACHI_TIMEZONE = timezone(timedelta(hours=5), name="Asia/Karachi")


class FixtureScenarioDefinition(ScenarioDefinition):
    """Catalog-only scenario fields that remain deterministic."""

    model_config = ConfigDict(frozen=True)

    signals: list[str]


class FixtureCatalog(BaseModel):
    """Validated durable source for the Phase 0 fixture API."""

    model_config = ConfigDict(frozen=True)

    catalog_schema: Literal["omniscience.fixture-catalog.v1"] = Field(alias="schema")
    fixture_version: str
    anchor_utc: datetime
    entities: dict[str, list[FixtureRecord]]
    scenarios: list[FixtureScenarioDefinition]


def _load_catalog() -> FixtureCatalog:
    catalog = FixtureCatalog.model_validate_json(
        CATALOG_PATH.read_text(encoding="utf-8")
    )
    if set(catalog.entities) != EXPECTED_ENTITY_FAMILIES:
        raise ValueError("Fixture catalog entity families are incomplete.")
    return catalog


def build_scenario_view(scenario_id: str) -> ScenarioView:
    """Build a repeatable API view for one named fixture condition."""

    catalog = _load_catalog()
    entities = catalog.entities
    scenarios = catalog.scenarios
    selected = next(
        (scenario for scenario in scenarios if scenario.id == scenario_id),
        None,
    )
    if selected is None:
        raise KeyError(scenario_id)

    anchor = catalog.anchor_utc
    local_anchor = anchor.astimezone(KARACHI_TIMEZONE)
    record_count = sum(len(records) for records in entities.values())

    return ScenarioView(
        fixture_version=catalog.fixture_version,
        action_lock_reason="Fixture-only data cannot authorize real actions.",
        scenario=selected,
        available_scenarios=[
            ScenarioSummary(id=scenario.id, label=scenario.label, status=scenario.status)
            for scenario in scenarios
        ],
        clock=ScenarioClock(
            stored_at_utc=anchor,
            displayed_at_local=local_anchor,
        ),
        summary=ScenarioFixtureSummary(
            entity_family_count=len(entities),
            record_count=record_count,
        ),
        entities=entities,
        signals=selected.signals,
    )
