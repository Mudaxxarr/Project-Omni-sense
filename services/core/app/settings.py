"""Safe runtime configuration for the local core."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

RuntimeMode = Literal["fixture", "postgres"]


class ConfigurationError(ValueError):
    """Raised before startup when protected storage configuration is incomplete."""


@dataclass(frozen=True)
class RuntimeSettings:
    """Non-secret runtime configuration state safe to expose through health."""

    mode: RuntimeMode
    database_url: str | None
    encryption_key_id: str | None

    @property
    def is_fixture_mode(self) -> bool:
        return self.mode == "fixture"

    @property
    def storage_configuration_detail(self) -> str:
        if self.is_fixture_mode:
            return "Fixture mode is active; protected PostgreSQL storage is not configured."
        return "DATABASE_URL and encryption-key identity are configured for protected storage."


def load_runtime_settings(
    environment: Mapping[str, str] | None = None,
) -> RuntimeSettings:
    """Load safe configuration and fail closed for the PostgreSQL runtime."""

    values = os.environ if environment is None else environment
    mode_value = values.get("OMNI_RUNTIME_MODE", "fixture").strip().lower()
    if mode_value not in {"fixture", "postgres"}:
        raise ConfigurationError(
            "OMNI_RUNTIME_MODE must be either 'fixture' or 'postgres'."
        )

    mode: RuntimeMode = mode_value  # type: ignore[assignment]
    database_url = values.get("DATABASE_URL", "").strip() or None
    encryption_key_id = values.get("APP_ENCRYPTION_KEY_ID", "").strip() or None

    if mode == "postgres":
        missing = [
            name
            for name, value in (
                ("DATABASE_URL", database_url),
                ("APP_ENCRYPTION_KEY_ID", encryption_key_id),
            )
            if value is None
        ]
        if missing:
            raise ConfigurationError(
                "PostgreSQL runtime requires " + " and ".join(missing) + "."
            )

    return RuntimeSettings(
        mode=mode,
        database_url=database_url,
        encryption_key_id=encryption_key_id,
    )
