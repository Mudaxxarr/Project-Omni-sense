# ADR 0002: Event, evidence and correction contract

**Status:** Accepted  
**Date:** 2026-08-03

## Context

Every material business claim needs a source, timestamp, freshness state and
responsible source system. The system must preserve contradictions and make
later correction auditable instead of overwriting history.

## Decision

- Business events are append-only records with a UUID, event type, occurrence
  time, record time, actor, source-system lineage, correlation and causation
  identifiers, payload schema version, payload hash, evidence references,
  classification and retention-policy reference.
- Evidence is content-addressed with SHA-256, source system, capture and
  freshness times, classification, storage location and metadata. AI text is
  not evidence on its own.
- A correction creates a new linked event. It never edits or removes the
  original event, claim, evidence reference or audit entry.
- A state change and its outbox record are committed in the same PostgreSQL
  transaction. Delivery consumers use an idempotency key and record outcome;
  an external delivery never becomes proof that the source state changed.
- Contradictory evidence remains visible and is represented as a conflict, not
  silently selected or discarded.

## Consequences

Every future feature contract must declare the events it produces or consumes,
the permitted evidence classifications, freshness behavior and how a user can
see source lineage. No feature may import another module's tables directly to
bypass this contract.

## Sources

- `PROJECT_OMNISCIENCE_MASTER_SPEC.md` sections 4.1 and 4.4
- `01-foundation-trust-kernel.md` sections 4.1-4.2 and Task 7-9
