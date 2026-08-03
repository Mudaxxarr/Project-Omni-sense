# ADR 0003: Trust-visible Command Centre design system

**Status:** Accepted  
**Date:** 2026-08-03

## Context

The Command Centre must remain premium and calm while making uncertainty,
authority, evidence and system health impossible to miss. A visually polished
screen must never imply that unavailable or stale information is safe to act
on.

## Decision

- UI uses semantic tokens rather than feature-owned raw colours. Tokens cover
  canvas, surface, border, primary and muted text, primary action, warning,
  critical and informational states.
- The standard desktop density serves an owner who needs context and a staff
  member who needs a focused task. Critical information receives hierarchy and
  plain-language labels before decorative detail.
- Every material value or recommendation provides visible source, captured or
  freshness time, classification/authority where relevant, and an evidence
  route when evidence exists.
- Stale, incomplete, denied, queued, degraded and error states are distinct.
  Consequential controls remain disabled until required evidence and authority
  are valid.
- Keyboard navigation, a skip link, focus visibility, screen-reader labels and
  reduced-motion behavior are required for shared shell components.
- Visual verification covers 1280x720, 1440x900 and 1920x1080, with no
  horizontal overflow and no console or failed-network errors.

## Consequences

The UI kit owns reusable visual primitives; it contains no business decisions.
Feature UI cannot replace evidence with AI prose, omit a stale state, or imply
cloud processing where none exists.

## Sources

- `PROJECT_OMNISCIENCE_MASTER_SPEC.md` sections 3-4
- `01-foundation-trust-kernel.md` Task 3
- `2026-07-29-local-cpu-runtime-design.md` sections 10-11
