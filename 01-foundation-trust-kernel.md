# Phase 1 — Foundation, Trust Kernel and Visual Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the secure local-first repository, data foundation, identity system, event/evidence spine, retention engine and premium desktop shell on which every later OMNISCIENCE phase depends.

**Architecture:** Build a monorepo with one Electron/React desktop application, one modular FastAPI core service and PostgreSQL as the durable source of truth. The core service contains isolated modules behind contracts; the future external Execution Gateway remains a separate service and is not built in this phase.

**Tech Stack:** Electron, React, TypeScript, Vite, Tailwind CSS, Zustand, TanStack Query, Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic, native PostgreSQL 16, APScheduler, psutil, Windows services, Pytest, Vitest and Playwright. Docker Desktop, WSL2, Redis and a standalone vector database are excluded from the daily production runtime.

**Governing Runtime Design:** `docs/superpowers/specs/2026-07-29-local-cpu-runtime-design.md` applies to every task and acceptance gate.

## Global Constraints

- Existing POS/accounting software remains untouched and authoritative.
- No external messages, advertisements, price writes, payments or trading.
- PostgreSQL is the database, job ledger, outbox and lock authority; Redis is not part of the target-PC baseline.
- Every material record carries source, timestamp, actor, classification and audit lineage.
- Sensitive actions require fresh owner authentication.
- All user-facing dates use Asia/Karachi while storage uses UTC.
- UI supports Urdu/Roman Urdu/English content without breaking layout.
- No global screen recording, keystroke recording, ambient audio or camera processing.
- Target hardware is i9-12900K, 32 GB RAM and Intel UHD 770 without CUDA.
- All future model inference is local and subordinate to the non-AI Resource Governor.
- Native Windows operation must not require Docker Desktop or WSL2.
- The phase is complete only after permission, deletion and restore tests pass.

---

## 1. Phase outcome

At the end of Phase 1, Mudassar opens a signed PC application and sees a calm, premium Command Terminal. He can authenticate, see system health, switch between the four future spaces, inspect evidence/audit records and manage users and declared data policies. No business automation exists yet, but the foundation is strong enough that later phases cannot bypass identity, evidence, retention or audit.

## 2. Visual character

The interface should feel like a private executive operating room, not a generic admin template.

### 2.1 Design direction

- Background: near-black graphite, not pure black.
- Primary surface: layered charcoal panels with subtle borders.
- Primary action: restrained emerald.
- Warning: amber.
- Critical: red used only for verified urgency.
- Information: desaturated blue.
- Typography: Geist/Inter for UI, JetBrains Mono for identifiers and system telemetry.
- Radius: 10–14px; no excessive pill-shaped components.
- Motion: 150–220ms, purposeful and interruptible.
- Density: owner screens spacious; staff/data screens compact.
- Every important card includes `Why?`, `Source`, `Freshness` and `Authority`.

### 2.2 Initial shell

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ OMNISCIENCE       LOCAL • HEALTHY       DATA: NOT CONNECTED       09:41 PKT │
├───────────┬──────────────────────────────────────────────────────────────────┤
│  NOW      │  GOOD MORNING, MUDASSAR                                         │
│  THINK    │                                                                  │
│  PEOPLE   │  FOUNDATION STATUS                                               │
│  MEMORY   │  ✓ Local database     ✓ Evidence vault     ✓ Audit chain         │
│           │  ✓ Backup verified    ✓ Retention worker   ✓ Owner identity      │
│           │                                                                  │
│           │  No operational data is connected yet.                           │
│           │  [ START SOURCE SETUP ]                                           │
├───────────┴──────────────────────────────────────────────────────────────────┤
│ SAFE STATE: READ-ONLY                  F1 Help       Ctrl+K Command Palette   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Design tokens

Create semantic tokens rather than hard-coded color values:

```ts
export const semanticTokens = {
  bgCanvas: "var(--color-graphite-950)",
  bgSurface: "var(--color-graphite-900)",
  borderSubtle: "var(--color-graphite-750)",
  textPrimary: "var(--color-stone-100)",
  textMuted: "var(--color-stone-400)",
  actionPrimary: "var(--color-emerald-500)",
  stateWarning: "var(--color-amber-500)",
  stateCritical: "var(--color-red-500)",
  stateInfo: "var(--color-sky-500)",
} as const;
```

---

## 3. Repository map

```text
omniscience/
  apps/
    desktop/
      electron/
      src/
        app/
        components/
        features/
        routes/
        styles/
      tests/
  services/
    core/
      app/
        api/
        config/
        db/
        modules/
          identity/
          authorization/
          events/
          evidence/
          audit/
          retention/
          health/
      migrations/
      tests/
  packages/
    contracts/
      schemas/
      src/
    ui-kit/
      src/
    observability/
  infra/
    compose/
    scripts/
  docs/
    architecture/
    security/
    runbooks/
  tests/
    acceptance/
    security/
```

Responsibility rules:

- `packages/contracts` owns wire formats and generated TypeScript/Python types.
- `services/core/app/modules/*` may communicate through service interfaces, not direct table imports.
- UI-kit contains visual primitives, not business rules.
- Audit and retention modules cannot be disabled by feature modules.
- No future AI module receives database superuser credentials.

---

## 4. Core contracts

### 4.1 Business event

```python
from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class BusinessEventV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: UUID
    event_type: str
    occurred_at: datetime
    recorded_at: datetime
    actor_id: UUID | None
    source_system: str
    source_record_id: str | None
    branch_id: UUID
    data_classification: str
    payload_schema_version: str
    payload: dict[str, Any]
    payload_hash: str
    correlation_id: UUID
    causation_id: UUID | None
    evidence_ids: list[UUID]
    retention_policy_id: UUID
```

### 4.2 Evidence reference

```python
class EvidenceRefV1(BaseModel):
    evidence_id: UUID
    kind: str
    source_system: str
    captured_at: datetime
    freshness_at: datetime | None
    classification: str
    sha256: str
    storage_uri: str | None
    metadata: dict[str, Any]
```

### 4.3 API error

```json
{
  "error": {
    "code": "AUTHORIZATION_DENIED",
    "message": "This action requires owner reauthentication.",
    "correlation_id": "uuid",
    "details": {}
  }
}
```

---

## 5. Tasks

### Task 1: Freeze architecture decisions and project conventions

**Files:**
- Create: `docs/architecture/0001-local-first-modular-core.md`
- Create: `docs/architecture/0002-event-and-evidence-contract.md`
- Create: `docs/architecture/0003-ui-design-system.md`
- Create: `docs/security/data-classification.md`

**Interfaces:**
- Consumes: Master specification.
- Produces: Architecture decision records referenced by every later task.

- [ ] **Step 1: Write ADR 0001**

Record Electron/React desktop, FastAPI modular core, native PostgreSQL durability/jobs/locks, local-only model inference, Resource Governor precedence, UTC storage and Asia/Karachi presentation. Explicitly exclude production Redis, Docker Desktop and WSL2.

- [ ] **Step 2: Write ADR 0002**

Define event immutability, source lineage, evidence hashes, correction events and outbox delivery.

- [ ] **Step 3: Write ADR 0003**

Define semantic colors, typography, spacing, motion, owner/staff density and non-negotiable evidence affordances.

- [ ] **Step 4: Write data-classification policy**

Use exactly:

```text
PUBLIC
INTERNAL
CONFIDENTIAL_CUSTOMER
CONFIDENTIAL_EMPLOYEE
RESTRICTED_FINANCIAL
RESTRICTED_OWNER
RESTRICTED_SECURITY
```

- [ ] **Step 5: Commit**

```bash
git add docs
git commit -m "docs: freeze omniscience foundation decisions"
```

### Task 2: Bootstrap the monorepo and deterministic development environment

**Files:**
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `infra/scripts/check-local-dependencies.ps1`
- Create: `docs/runbooks/windows-development-setup.md`
- Create: `Makefile`
- Create: `README.md`

**Interfaces:**
- Consumes: ADR 0001.
- Produces: `pnpm dev`, `uv run pytest` and a verified native PostgreSQL 16 development service.

- [ ] **Step 1: Add root package scripts**

```json
{
  "private": true,
  "scripts": {
    "dev": "concurrently \"pnpm --filter desktop dev\" \"uv run uvicorn app.main:app --reload --app-dir services/core\"",
    "test": "pnpm -r test && uv run pytest",
    "lint": "pnpm -r lint && uv run ruff check .",
    "typecheck": "pnpm -r typecheck && uv run mypy services"
  }
}
```

- [ ] **Step 2: Configure Python dependencies**

Include FastAPI, Pydantic, SQLAlchemy, Alembic, psycopg, structlog, pytest, pytest-asyncio, mypy and ruff.

- [ ] **Step 3: Add native Windows dependency preflight**

`check-local-dependencies.ps1` must verify `node`, `pnpm`, `uv`, `python`, `psql`, `pg_isready`, PostgreSQL major version 16, free `C:` space and available physical RAM. It exits non-zero and prints an exact remediation for each missing dependency.

- [ ] **Step 4: Verify native PostgreSQL**

Run:

```powershell
.\infra\scripts\check-local-dependencies.ps1
pg_isready -h 127.0.0.1 -p 5432
```

Expected: dependency preflight passes and PostgreSQL reports `accepting connections`.

- [ ] **Step 5: Add environment validation test**

Test that application startup fails with a clear error if `DATABASE_URL` or `APP_ENCRYPTION_KEY_ID` is absent.

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "build: bootstrap omniscience monorepo"
```

### Task 3: Build the visual token system and desktop shell

**Files:**
- Create: `packages/ui-kit/src/tokens.css`
- Create: `packages/ui-kit/src/components/StatusBadge.tsx`
- Create: `packages/ui-kit/src/components/EvidenceLink.tsx`
- Create: `apps/desktop/src/app/AppShell.tsx`
- Create: `apps/desktop/src/routes/routes.tsx`
- Test: `apps/desktop/tests/app-shell.test.tsx`
- Test: `apps/desktop/tests/app-shell.spec.ts`

**Interfaces:**
- Consumes: ADR 0003.
- Produces: `AppShell`, `StatusBadge`, `EvidenceLink`, primary routes `/now`, `/think`, `/people`, `/memory`.

- [ ] **Step 1: Write failing shell test**

```tsx
it("renders the four owner spaces and local health state", () => {
  render(<AppShell health={{ mode: "local", status: "healthy" }} />);
  expect(screen.getByText("NOW")).toBeVisible();
  expect(screen.getByText("THINK")).toBeVisible();
  expect(screen.getByText("PEOPLE")).toBeVisible();
  expect(screen.getByText("MEMORY")).toBeVisible();
  expect(screen.getByText(/LOCAL/)).toBeVisible();
});
```

- [ ] **Step 2: Run and confirm failure**

```bash
pnpm --filter desktop test app-shell.test.tsx
```

Expected: FAIL because `AppShell` does not exist.

- [ ] **Step 3: Implement semantic tokens and shell**

Implement fixed owner navigation, top telemetry, content outlet, command palette and footer safe-state indicator.

- [ ] **Step 4: Add keyboard and accessibility behavior**

Ensure focus order, skip link, reduced-motion support and screen-reader labels.

- [ ] **Step 5: Add Playwright visual test**

Capture 1440×900 screenshot and assert no horizontal overflow at 1280×720.

- [ ] **Step 6: Run tests**

```bash
pnpm --filter desktop test
pnpm --filter desktop exec playwright test
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/desktop packages/ui-kit
git commit -m "feat: add premium command terminal shell"
```

### Task 4: Create database base models and migrations

**Files:**
- Create: `services/core/app/db/base.py`
- Create: `services/core/app/db/session.py`
- Create: `services/core/app/modules/identity/models.py`
- Create: `services/core/app/modules/events/models.py`
- Create: `services/core/app/modules/evidence/models.py`
- Create: `services/core/app/modules/audit/models.py`
- Create: `services/core/app/modules/retention/models.py`
- Create: `services/core/migrations/versions/0001_foundation.py`
- Test: `services/core/tests/db/test_foundation_migration.py`

**Interfaces:**
- Produces: SQLAlchemy models for tenant, branch, user, role, permission, source system, event, outbox, evidence, audit and retention policy.

- [ ] **Step 1: Write migration smoke test**

Test upgrade to head, expected tables, required indexes and successful downgrade in an isolated test database.

- [ ] **Step 2: Implement UUID/UTC mixins**

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 3: Implement tables and constraints**

Add unique event IDs, unique outbox idempotency key, non-null classification and retention references.

- [ ] **Step 4: Apply migration**

```bash
uv run alembic -c services/core/alembic.ini upgrade head
```

Expected: all foundation tables created.

- [ ] **Step 5: Run tests and commit**

```bash
uv run pytest services/core/tests/db/test_foundation_migration.py -v
git add services/core
git commit -m "feat: add foundation data model"
```

### Task 5: Implement owner/staff authentication and sessions

**Files:**
- Create: `services/core/app/modules/identity/service.py`
- Create: `services/core/app/modules/identity/api.py`
- Create: `services/core/app/modules/identity/schemas.py`
- Create: `apps/desktop/src/features/auth/LoginScreen.tsx`
- Create: `apps/desktop/src/features/auth/sessionStore.ts`
- Test: `services/core/tests/identity/test_sessions.py`
- Test: `apps/desktop/tests/login.test.tsx`

**Interfaces:**
- Produces: `POST /v1/session`, `DELETE /v1/session`, `GET /v1/session/me`.
- Session result: `SessionView { user_id, roles, expires_at, reauth_at }`.

- [ ] **Step 1: Write session expiration tests**

Cover valid login, wrong credential, disabled user, inactivity expiration and fresh-reauth requirement.

- [ ] **Step 2: Implement password hashing and local session tokens**

Use Argon2id. Store only token hashes server-side. Set 15-minute staff inactivity and configurable 5-minute owner-sensitive timeout.

- [ ] **Step 3: Implement login UI**

Do not reveal whether a username exists. Display local/offline state.

- [ ] **Step 4: Add FIDO2/WebAuthn interface stub**

Define `ReauthChallenge` now; complete hardware integration before external execution phases.

- [ ] **Step 5: Run tests and commit**

```bash
uv run pytest services/core/tests/identity -v
pnpm --filter desktop test login.test.tsx
git add services/core apps/desktop
git commit -m "feat: add secure local sessions"
```

### Task 6: Implement RBAC, ABAC and row-level scope

**Files:**
- Create: `services/core/app/modules/authorization/policy.py`
- Create: `services/core/app/modules/authorization/dependencies.py`
- Create: `services/core/app/modules/authorization/rls.sql`
- Test: `services/core/tests/authorization/test_policy_matrix.py`
- Test: `tests/security/test_cross_domain_access.py`

**Interfaces:**
- Produces: `authorize(subject, action, resource, context) -> AuthorizationDecision`.

- [ ] **Step 1: Encode the initial permission matrix**

Include owner, manager, sales, finance, marketing and developer boundaries from the master specification.

- [ ] **Step 2: Write cross-domain failing tests**

Verify sales cannot read owner memory, marketing cannot read financial exposure and a Daraz-scoped user cannot read retail private rows.

- [ ] **Step 3: Implement policy evaluator**

```python
@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    reason_code: str
    policy_version: str
```

- [ ] **Step 4: Apply PostgreSQL RLS**

Use transaction-local subject and branch settings; deny when context is absent.

- [ ] **Step 5: Run security tests and commit**

```bash
uv run pytest services/core/tests/authorization tests/security/test_cross_domain_access.py -v
git add services/core tests/security
git commit -m "feat: enforce domain and row authorization"
```

### Task 7: Implement durable event spine and transactional outbox

**Files:**
- Create: `services/core/app/modules/events/schemas.py`
- Create: `services/core/app/modules/events/service.py`
- Create: `services/core/app/modules/events/outbox_worker.py`
- Test: `services/core/tests/events/test_event_append.py`
- Test: `services/core/tests/events/test_outbox_recovery.py`

**Interfaces:**
- Produces: `append_event(session, command) -> BusinessEventV1`.
- Produces: `claim_outbox_batch(worker_id, limit)`.

- [ ] **Step 1: Write atomicity test**

Prove domain change and event/outbox row commit together or neither commits.

- [ ] **Step 2: Implement canonical payload hashing**

Use sorted JSON, UTF-8 and SHA-256. Reject floats for money; require integer paisa.

- [ ] **Step 3: Implement append-only protection**

Application role receives insert/select only for sealed event rows.

- [ ] **Step 4: Implement lease-based outbox worker**

Recover abandoned leases and preserve attempt history.

- [ ] **Step 5: Test crash recovery**

Kill worker after claim, advance lease time, verify another worker processes once.

- [ ] **Step 6: Commit**

```bash
git add services/core/app/modules/events services/core/tests/events
git commit -m "feat: add durable event and outbox spine"
```

### Task 8: Implement source and evidence registry

**Files:**
- Create: `services/core/app/modules/evidence/service.py`
- Create: `services/core/app/modules/evidence/storage.py`
- Create: `services/core/app/modules/evidence/api.py`
- Create: `apps/desktop/src/features/evidence/EvidenceDrawer.tsx`
- Test: `services/core/tests/evidence/test_lineage.py`
- Test: `apps/desktop/tests/evidence-drawer.test.tsx`

**Interfaces:**
- Produces: `register_evidence()`, `link_evidence()`, `GET /v1/evidence/{id}`.

- [ ] **Step 1: Write lineage test**

Create a source, evidence object and event; assert UI response includes source, freshness, hash and classification.

- [ ] **Step 2: Implement encrypted object storage adapter**

Store content outside database; store URI, hash, encryption key ID and metadata in PostgreSQL.

- [ ] **Step 3: Implement evidence drawer**

Display source, captured time, freshness, transformations, hash and related events.

- [ ] **Step 4: Test unauthorized access**

Ensure a user without classification access receives 404-style denial without metadata leakage.

- [ ] **Step 5: Commit**

```bash
git add services/core/app/modules/evidence apps/desktop/src/features/evidence
git commit -m "feat: add evidence lineage and viewer"
```

### Task 9: Implement audit trail and tamper-evident manifests

**Files:**
- Create: `services/core/app/modules/audit/service.py`
- Create: `services/core/app/modules/audit/manifest.py`
- Create: `apps/desktop/src/features/audit/AuditTimeline.tsx`
- Test: `services/core/tests/audit/test_manifest.py`

**Interfaces:**
- Produces: `record_audit()`, `seal_daily_manifest()`, `verify_manifest()`.

- [ ] **Step 1: Write tamper test**

Alter a copied historical row in a test fixture and assert manifest verification identifies the exact date/batch.

- [ ] **Step 2: Implement audit event schema**

Record actor, action, resource, before/after hashes, reason, request correlation and policy decision.

- [ ] **Step 3: Implement daily manifest**

Hash ordered critical records and sign with the local audit key.

- [ ] **Step 4: Build audit timeline**

Allow filtering but not modification.

- [ ] **Step 5: Commit**

```bash
git add services/core/app/modules/audit apps/desktop/src/features/audit
git commit -m "feat: add tamper-evident audit history"
```

### Task 10: Implement retention and verifiable deletion

**Files:**
- Create: `services/core/app/modules/retention/service.py`
- Create: `services/core/app/modules/retention/worker.py`
- Create: `services/core/app/modules/retention/api.py`
- Test: `services/core/tests/retention/test_expiry.py`
- Test: `services/core/tests/retention/test_failure_alert.py`

**Interfaces:**
- Produces: `apply_retention_policy()`, `expire_due_objects()`, `preserve_with_reason()`.

- [ ] **Step 1: Write expiry tests**

Cover database-only record, encrypted object, legal/evidence preservation and deletion worker failure.

- [ ] **Step 2: Implement expiry query with `SKIP LOCKED`**

Multiple workers must not delete the same object twice.

- [ ] **Step 3: Implement deletion receipt**

Receipt stores object ID, policy, deleted time and previous hash; it must not retain deleted content.

- [ ] **Step 4: Add owner alert on failure**

Retention failure appears as a Rank 0 privacy/safety issue.

- [ ] **Step 5: Commit**

```bash
git add services/core/app/modules/retention services/core/tests/retention
git commit -m "feat: enforce data retention and deletion"
```

### Task 11: Implement Resource Governor, health, freshness and safe-state UI

**Files:**
- Create: `services/core/app/modules/resources/models.py`
- Create: `services/core/app/modules/resources/governor.py`
- Create: `services/core/app/modules/resources/windows_metrics.py`
- Create: `services/core/app/modules/health/service.py`
- Create: `services/core/app/modules/health/api.py`
- Create: `apps/desktop/src/features/health/LocalComputeStatus.tsx`
- Create: `apps/desktop/src/features/health/HealthBar.tsx`
- Create: `apps/desktop/src/features/health/StaleDataOverlay.tsx`
- Test: `services/core/tests/resources/test_governor.py`
- Test: `apps/desktop/tests/stale-data.spec.ts`

**Interfaces:**
- Produces: `ResourceSnapshot`, `ResourceDecision`, `GET /v1/health`, `SystemHealthView`.

- [ ] **Step 1: Define health states**

```ts
type SystemMode = "healthy" | "degraded" | "external_offline" | "safe_state" | "recovery";
type ComputeState = "green" | "yellow" | "orange" | "red";
```

- [ ] **Step 2: Write Resource Governor threshold tests**

Assert Green at `>= 16 GB`, Yellow at `12–15.9 GB`, Orange at `8–11.9 GB` and Red below `8 GB`. Assert pagefile is ignored, heavy concurrency is one, AI CPU ceiling is 60%, and Deep Analyst is denied outside Green.

- [ ] **Step 3: Implement native Windows metrics and decisions**

Read available physical RAM, CPU, disk free space, process working sets and core API latency. The governor is deterministic and imports no model runtime.

- [ ] **Step 4: Write stale overlay test**

If core heartbeat exceeds five seconds, financial/action areas blur and display “DATA STALE — DO NOT MAKE CONSEQUENTIAL DECISIONS.”

- [ ] **Step 5: Implement health aggregation**

Include database, retention worker, backup age, event backlog, local service version, compute state, available RAM, AI lease owner and the reason a job is queued.

- [ ] **Step 6: Implement non-destructive safe-state command**

In Phase 1 it only records requested state; later the Gateway subscribes to it.

- [ ] **Step 7: Run backend and Playwright tests and commit**

```bash
uv run pytest services/core/tests/resources/test_governor.py -v
pnpm --filter desktop exec playwright test stale-data.spec.ts
git add services/core apps/desktop
git commit -m "feat: add local resource governor and safe-state experience"
```

### Task 12: Implement backup, isolated restore and Phase 1 acceptance suite

**Files:**
- Create: `infra/scripts/backup.ps1`
- Create: `infra/scripts/restore-isolated.ps1`
- Create: `docs/runbooks/backup-restore.md`
- Create: `tests/acceptance/test_phase_1.py`
- Create: `tests/security/test_phase_1_permissions.py`

**Interfaces:**
- Produces: encrypted backup artifact, signed manifest and isolated restore database.

- [ ] **Step 1: Write backup script**

Use `pg_dump` custom format, hash the artifact, encrypt it and write a manifest. Active application data stays on `C:`; encrypted rotating backups target `J:` with a 40 GB allocation.

- [ ] **Step 2: Write isolated restore script**

Refuse a target matching the production database name or host. Restore only to an explicitly supplied isolated target.

- [ ] **Step 3: Execute restore drill**

```powershell
.\infra\scripts\backup.ps1 -Environment local
.\infra\scripts\restore-isolated.ps1 -BackupPath .\backups\local\omniscience-local-2026-07-29.dump.enc -TargetDatabase omniscience_restore_test
```

Expected: manifest valid, row counts match, live database untouched.

- [ ] **Step 4: Enforce target-PC storage thresholds**

Warn at 30 GB free on `C:`, enter storage defensive mode at 20 GB and block model downloads/recording at 15 GB. Refuse backup rotation that would delete the latest verified restore point. Never spill automatically to `E:`, `H:` or `I:`.

- [ ] **Step 5: Run complete acceptance suite**

```bash
pnpm test
uv run pytest tests/acceptance/test_phase_1.py tests/security/test_phase_1_permissions.py -v
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add infra docs/runbooks tests
git commit -m "test: complete phase one foundation gate"
```

---

## 6. Phase 1 acceptance gate

All conditions are mandatory:

- Desktop app opens on the target Windows PC.
- Core API and database work without internet.
- Native runtime starts without Docker Desktop, WSL2 or Redis.
- Resource Governor produces the exact four RAM states and permits only one heavy lease.
- `LOCAL ONLY: NO DATA LEAVES THIS PC` is visible in system health.
- Owner and staff permissions are demonstrably isolated.
- Audit records cannot be modified through the application role.
- Every evidence item exposes lineage and classification.
- Retention worker deletes expired test objects and records receipts.
- Backup restores into an isolated database with verified hashes.
- `C:` defensive thresholds and the `J:` 40 GB backup quota behave exactly as specified.
- Stale-data overlay appears within five seconds of backend loss.
- No external provider credential exists.
- No accounting/POS write integration exists.
- Visual QA passes at 1280×720, 1440×900 and 1920×1080.

## 7. Phase 1 demo script

1. Launch application offline.
2. Authenticate as owner.
3. Show four-space shell and health bar.
4. Create sales user and demonstrate owner-memory denial.
5. Register a sample source and evidence record.
6. Open evidence drawer and audit timeline.
7. Expire the sample evidence and show deletion receipt.
8. Stop backend and show stale-data overlay.
9. Restore backend.
10. Run encrypted backup and isolated restore.

## 8. Exit artifact

Phase 1 ends with a signed local release tagged:

```text
v0.1.0-foundation
```

Phase 2 may begin only after Mudassar accepts the visual shell and all acceptance gates pass.
