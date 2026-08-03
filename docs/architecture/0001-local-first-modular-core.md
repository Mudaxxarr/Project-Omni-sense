# ADR 0001: Local-first modular core

**Status:** Accepted  
**Date:** 2026-08-03

## Context

OMNISCIENCE protects business continuity and sensitive local data on a Windows
PC with constrained available memory. Core business workflows must remain
useful when every AI worker is paused or unavailable.

## Decision

- The product is one Electron/React desktop application backed by a modular
  FastAPI core service.
- Native PostgreSQL is the durable source of truth for business state, durable
  jobs, advisory locks and the transactional outbox.
- The Core Business Lane runs independently of language, speech and vision
  models. An AI worker never receives database-superuser credentials.
- All model inference is local to the owner's PC. No cloud LLM, speech or
  vision inference, key or fallback path is permitted.
- The Resource Governor is deterministic, has precedence over AI workers, and
  allows at most one heavy job. It pauses AI work before it can degrade the UI,
  core API, PostgreSQL, POS-facing work or financial awareness.
- PostgreSQL stores timestamps in UTC. The owner interface presents business
  time in Asia/Karachi and always labels the timezone where it matters.
- Production does not depend on Redis, Docker Desktop, WSL2, RabbitMQ, Celery,
  Kubernetes, a standalone vector database or multiple local model servers.

## Consequences

Features must expose honest local, stale, queued and degraded states. They may
use deterministic rules when model work is unavailable, but they cannot hide a
missing model result or move a consequential action outside its approval path.

## Sources

- `PROJECT_OMNISCIENCE_MASTER_SPEC.md` sections 2-4
- `2026-07-29-local-cpu-runtime-design.md` sections 1-5 and 8
