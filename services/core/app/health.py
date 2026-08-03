"""Local runtime health and prerequisite detection."""

from __future__ import annotations

import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from services.core.app.contracts import (
    DataConnectionView,
    HealthView,
    PrerequisitesView,
    RequirementView,
)
from services.core.app.settings import RuntimeSettings, load_runtime_settings


def _postgresql_status(database_url: str | None = None) -> RequirementView:
    pg_isready = shutil.which("pg_isready")
    conventional_probe = Path(
        "C:/Program Files/PostgreSQL/16/bin/pg_isready.exe"
    )
    if pg_isready is None and conventional_probe.exists():
        pg_isready = str(conventional_probe)

    if pg_isready is None:
        return RequirementView(
            status="not_configured",
            detail="Native PostgreSQL 16 has not been configured.",
        )

    try:
        arguments = [pg_isready, "--timeout", "2"]
        if database_url:
            parsed = urlsplit(database_url)
            if not parsed.hostname:
                return RequirementView(
                    status="unavailable",
                    detail="Protected PostgreSQL configuration has no database host.",
                )
            arguments.extend(["--host", parsed.hostname])
            if parsed.port is not None:
                arguments.extend(["--port", str(parsed.port)])
        else:
            arguments.extend(["--host", "127.0.0.1", "--port", "5432"])
        result = subprocess.run(
            arguments,
            capture_output=True,
            check=False,
            text=True,
            timeout=4,
        )
    except (OSError, subprocess.TimeoutExpired):
        return RequirementView(
            status="unavailable",
            detail="PostgreSQL did not answer the bounded readiness check.",
        )

    if result.returncode == 0:
        return RequirementView(
            status="ready",
            detail="Native PostgreSQL 16 is accepting local connections.",
        )

    return RequirementView(
        status="unavailable",
        detail="PostgreSQL is configured but is not accepting connections.",
    )


def build_health_view(settings: RuntimeSettings | None = None) -> HealthView:
    """Return a fresh, deterministic view of the local runtime."""

    runtime_settings = settings or load_runtime_settings()
    postgresql = _postgresql_status(runtime_settings.database_url)
    storage_environment = RequirementView(
        status="not_configured"
        if runtime_settings.is_fixture_mode
        else "ready",
        detail=runtime_settings.storage_configuration_detail,
    )
    prerequisites = PrerequisitesView(
        core_api=RequirementView(
            status="ready",
            detail="Local core API is responding.",
        ),
        postgresql=postgresql,
        storage_environment=storage_environment,
        evidence_vault=RequirementView(
            status="planned",
            detail="Evidence storage is scheduled for Phase 1.",
        ),
        audit_chain=RequirementView(
            status="planned",
            detail="Tamper-evident audit chaining is scheduled for Phase 1.",
        ),
        retention_worker=RequirementView(
            status="planned",
            detail="Retention enforcement is scheduled for Phase 1.",
        ),
        backup_restore=RequirementView(
            status="planned",
            detail="Backup and restore proof is scheduled for Phase 1.",
        ),
    )

    return HealthView(
        version="0.0.1",
        status=(
            "healthy"
            if postgresql.status == "ready" and storage_environment.status == "ready"
            else "degraded"
        ),
        checked_at=datetime.now(UTC),
        prerequisites=prerequisites,
        data_connection=DataConnectionView(
            status="not_connected",
            detail="No operational source is connected.",
        ),
    )
