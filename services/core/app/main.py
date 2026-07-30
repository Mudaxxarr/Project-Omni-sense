"""OMNISCIENCE local core API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.core.app.contracts import HealthView
from services.core.app.health import build_health_view

app = FastAPI(
    title="OMNISCIENCE Core",
    description="Local-only owner intelligence runtime.",
    version="0.0.1",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4173", "http://localhost:4173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/", tags=["runtime"])
def runtime_identity() -> dict[str, str | bool]:
    """Expose a minimal human-readable identity probe."""

    return {
        "service": "omniscience-core",
        "mode": "local",
        "local_only": True,
        "health": "/v1/health",
    }


@app.get("/v1/health", response_model=HealthView, tags=["runtime"])
def health() -> HealthView:
    """Report local runtime health without concealing missing prerequisites."""

    return build_health_view()
