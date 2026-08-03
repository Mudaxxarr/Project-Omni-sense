# Data classification policy

**Status:** Active  
**Date:** 2026-08-03

## Classes

| Class | Use | Minimum handling rule |
|---|---|---|
| `PUBLIC` | Material approved for public release | Do not treat as evidence until its source and capture time are recorded. |
| `INTERNAL` | Routine non-sensitive operational material | Local access is limited to the business role that needs it. |
| `CONFIDENTIAL_CUSTOMER` | Customer identity, contact, interaction and service data | Limit access to the assigned operational scope; never send to cloud inference. |
| `CONFIDENTIAL_EMPLOYEE` | Employee task, coaching and operational evidence | No hidden monitoring, emotion/lie verdicts or automated employment consequences. |
| `RESTRICTED_FINANCIAL` | Read-only accounting exports, balances, recovery and payment-risk material | Accounting remains authoritative; no source-accounting write or payment authority. |
| `RESTRICTED_OWNER` | Owner memory, decisions and private approved context | Access requires the owner scope and is never exposed to staff by default. |
| `RESTRICTED_SECURITY` | Authentication, audit-integrity, incident and security-control material | Restrict to authorized administrators; preserve audit evidence and do not expose secrets in UI or logs. |

## Required metadata

Every durable evidence item and material event stores exactly one class,
source-system lineage, recorded timestamp, retention-policy reference and
access scope. A missing or unrecognized class fails closed.

## Retention and export

Retention is governed by a policy reference; correction and deletion actions
remain auditable. Raw sensitive media follows its stricter feature policy and
never becomes training or cloud-inference input. Export is denied unless a
feature's deterministic policy and the actor's scope both allow it.

## Sources

- `01-foundation-trust-kernel.md` Task 1
- `PROJECT_OMNISCIENCE_MASTER_SPEC.md` sections 3-4
