from datetime import datetime

from fastapi.testclient import TestClient

from services.core.app.main import app

client = TestClient(app)

SCENARIOS = {
    "valid",
    "stale",
    "duplicate",
    "contradictory",
    "denied",
    "degraded",
    "timeout",
    "recovery",
}
ENTITY_FAMILIES = {
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


def test_valid_scenario_exposes_anonymized_deterministic_fixture_catalog() -> None:
    response = client.get("/v1/scenarios/valid")

    assert response.status_code == 200
    payload = response.json()

    assert payload["contract_version"] == "scenario.v1"
    assert payload["scenario"]["id"] == "valid"
    assert payload["fixture_mode"] is True
    assert payload["anonymized"] is True
    assert payload["local_only"] is True
    assert payload["consequential_actions_enabled"] is False
    assert payload["clock"]["deterministic"] is True
    assert payload["clock"]["timezone"] == "Asia/Karachi"
    assert set(payload["entities"]) == ENTITY_FAMILIES
    assert payload["summary"]["entity_family_count"] == len(ENTITY_FAMILIES)
    assert payload["summary"]["record_count"] == sum(
        len(records) for records in payload["entities"].values()
    )

    available = {scenario["id"] for scenario in payload["available_scenarios"]}
    assert available == SCENARIOS


def test_scenario_clock_pairs_utc_storage_with_asia_karachi_display() -> None:
    payload = client.get("/v1/scenarios/valid").json()

    stored_at = datetime.fromisoformat(
        payload["clock"]["stored_at_utc"].replace("Z", "+00:00")
    )
    displayed_at = datetime.fromisoformat(payload["clock"]["displayed_at_local"])

    assert stored_at.utcoffset().total_seconds() == 0
    assert displayed_at.utcoffset().total_seconds() == 5 * 60 * 60
    assert stored_at.timestamp() == displayed_at.timestamp()


def test_every_scenario_is_repeatable_and_action_locked() -> None:
    valid_payload = client.get("/v1/scenarios/valid").json()
    anchor = valid_payload["clock"]
    fixture_version = valid_payload["fixture_version"]

    for scenario in SCENARIOS:
        first = client.get(f"/v1/scenarios/{scenario}")
        second = client.get(f"/v1/scenarios/{scenario}")

        assert first.status_code == 200
        assert first.json() == second.json()
        assert first.json()["clock"] == anchor
        assert first.json()["fixture_version"] == fixture_version
        assert first.json()["consequential_actions_enabled"] is False


def test_fixture_records_are_structured_and_contain_no_real_owner_identity() -> None:
    payload = client.get("/v1/scenarios/valid").json()

    for family, records in payload["entities"].items():
        assert records, family
        for record in records:
            assert record["id"].startswith("fx-")
            assert record["label"]
            assert record["recorded_at_utc"].endswith("Z")

    serialized = str(payload).lower()
    assert "mudassar" not in serialized
    assert "alhamd" not in serialized


def test_unknown_scenario_fails_closed() -> None:
    response = client.get("/v1/scenarios/not-a-scenario")

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown fixture scenario."
