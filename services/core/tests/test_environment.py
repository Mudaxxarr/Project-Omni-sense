import pytest

from services.core.app.health import _postgresql_status
from services.core.app.main import create_app
from services.core.app.settings import ConfigurationError, load_runtime_settings


def test_postgres_runtime_requires_a_database_url() -> None:
    with pytest.raises(ConfigurationError, match="DATABASE_URL"):
        load_runtime_settings(
            {
                "OMNI_RUNTIME_MODE": "postgres",
                "APP_ENCRYPTION_KEY_ID": "local-key-v1",
            }
        )


def test_postgres_runtime_requires_an_encryption_key_identity() -> None:
    with pytest.raises(ConfigurationError, match="APP_ENCRYPTION_KEY_ID"):
        load_runtime_settings(
            {
                "OMNI_RUNTIME_MODE": "postgres",
                "DATABASE_URL": "postgresql+psycopg://localhost/omniscience_dev",
            }
        )


def test_fixture_runtime_stays_explicitly_unconfigured() -> None:
    settings = load_runtime_settings({"OMNI_RUNTIME_MODE": "fixture"})

    assert settings.is_fixture_mode is True
    assert settings.storage_configuration_detail == (
        "Fixture mode is active; protected PostgreSQL storage is not configured."
    )


def test_postgres_runtime_fails_during_application_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OMNI_RUNTIME_MODE", "postgres")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_ENCRYPTION_KEY_ID", raising=False)

    with pytest.raises(ConfigurationError, match="DATABASE_URL"):
        create_app()


def test_postgresql_probe_uses_the_configured_local_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[str] = []

    class Result:
        returncode = 0

    def fake_run(arguments: list[str], **_: object) -> Result:
        observed.extend(arguments)
        return Result()

    monkeypatch.setattr("services.core.app.health.subprocess.run", fake_run)

    status = _postgresql_status(
        "postgresql+psycopg://omniscience_dev:unused@127.0.0.1:5544/omniscience_dev"
    )

    assert status.status == "ready"
    assert "--host" in observed
    assert observed[observed.index("--host") + 1] == "127.0.0.1"
    assert observed[observed.index("--port") + 1] == "5544"
