"""Local runtime health and prerequisite detection."""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from services.core.app.contracts import (
    DataConnectionView,
    HealthView,
    PrerequisitesView,
    RequirementView,
)


def _postgresql_status() -> RequirementView:
    database_url = os.getenv("OMNISCIENCE_DATABASE_URL", "").strip()
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
            arguments.extend(["--dbname", database_url])
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


def build_health_view() -> HealthView:
    """Return a fresh, deterministic view of the local runtime."""

    postgresql = _postgresql_status()
    prerequisites = PrerequisitesView(
        core_api=RequirementView(
            status="ready",
            detail="Local core API is responding.",
        ),
        postgresql=postgresql,
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
        status="healthy" if postgresql.status == "ready" else "degraded",
        checked_at=datetime.now(UTC),
        prerequisites=prerequisites,
        data_connection=DataConnectionView(
            status="not_connected",
            detail="No operational source is connected.",
        ),
    )
