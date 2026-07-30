from fastapi.testclient import TestClient

from services.core.app.main import app

client = TestClient(app)


def test_health_exposes_local_runtime_and_honest_prerequisites() -> None:
    response = client.get("/v1/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["service"] == "omniscience-core"
    assert payload["mode"] == "local"
    assert payload["status"] in {"healthy", "degraded"}
    assert payload["local_only"] is True
    assert payload["cloud_inference_enabled"] is False
    assert payload["timezone"] == "Asia/Karachi"
    assert payload["prerequisites"]["core_api"]["status"] == "ready"
    assert payload["prerequisites"]["postgresql"]["status"] in {
        "ready",
        "not_configured",
        "unavailable",
    }
    assert payload["data_connection"]["status"] == "not_connected"


def test_health_has_a_stable_contract_version() -> None:
    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json()["contract_version"] == "health.v1"

