import pytest

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
