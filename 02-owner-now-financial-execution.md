# Phase 2 — Owner Now, Financial Awareness and Execution Discipline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the first daily-use release: the read-only **Financial X-Ray**, counterparty integrity and recovery discipline, promises, delegation contracts, structured escalations, owner Delta Briefing and Re-Entry Capsule.

**Architecture:** Add deterministic business modules to the Phase 1 Core Business Lane without weakening the Trust Kernel. Financial data enters through a read-only adapter and becomes operational events; it is never posted back to the accounting source. Phase 2 remains fully usable in Resource Governor Red state and loads no language model.

**Tech Stack:** Phase 1 stack plus Pandera for tabular validation, Polars for imports, APScheduler for local scheduled jobs and Recharts for restrained timeline visuals.

**Governing Runtime Design:** `docs/superpowers/specs/2026-07-29-local-cpu-runtime-design.md` applies to every task and acceptance gate.

## Global Constraints

- Existing accounting/POS software is the only financial source of truth.
- Integration credentials are `SELECT`-only or file-import-only.
- Store money as integer paisa; never binary floating point.
- Every imported row retains source file/query, batch, timestamp and hash.
- Recovery messages remain drafts; Phase 2 has no external send capability.
- Staff escalation cannot become owner interruption without completeness checks.
- No prediction, trading, continuous audio, advertisement or marketplace write.
- Phase 2 loads no LLM, ASR, vision model or standalone vector service.
- Import/reconciliation jobs preempt future Deep Analyst work and must remain responsive under AI load.
- Every completion requires an explicit definition of done and evidence rule.

---

## 1. Phase outcome

Each morning Mudassar receives a short, evidence-linked briefing:

```text
WHAT CHANGED SINCE 8:42 PM

1  CASH RISK
   Oppo payment: 2,000,000 PKR due in 4 days
   Verified available: 1,690,000 PKR
   Defensive gap: 310,000 PKR

2  RECOVERABLE TODAY
   7 parties • 615,000 PKR • 3 promises due before 2 PM

3  EXECUTION RISK
   2 commitments lack evidence; 1 staff escalation is incomplete

[OPEN TODAY] [RESTORE LAST WORKSPACE]
```

Staff receive clear action queues rather than a generic dashboard.

---

## 2. Visual structure

### 2.1 Owner Now screen

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ NOW            COMMANDER MODE        DATA AGE 04m         LOCAL • HEALTHY    │
├──────────────────────────────────────────┬───────────────────────────────────┤
│ APEX TRIAD                               │ 7-DAY CASH AWARENESS              │
│ 1. Recover 310k by Thursday              │ Today       +615k / -220k         │
│ 2. Resolve Junaid payment dispute        │ Day 4       -310k GAP             │
│ 3. Assign 2 ownerless promises           │ Day 7       +140k buffer          │
│                                          │ [VIEW SOURCES]                    │
├──────────────────────────────────────────┼───────────────────────────────────┤
│ WHAT IS ALREADY HANDLED                  │ NEEDS YOUR DECISION               │
│ 6 follow-ups assigned                    │ Tier review: Atta                 │
│ 4 tasks awaiting evidence                │ Expense anomaly: 48k              │
└──────────────────────────────────────────┴───────────────────────────────────┘
```

### 2.2 Staff Today screen

```text
TODAY

08:30  Recover invoice 4054 from Junaid
       Outcome: receive commitment or dispute reason
       Evidence: call note / receipt / written promise
       [START]

11:00  Follow up 3 installment candidates
       Script and customer context available
       [OPEN QUEUE]
```

### 2.3 Interaction rules

- Monetary cards show source and freshness inline.
- Forecast-looking values are labelled scenario/awareness, not certainty.
- Red appears only for a verified deadline or policy breach.
- The owner sees exceptions; staff see next actions.
- “Complete” remains disabled until evidence/definition-of-done rules pass.

---

## 3. Data contracts

### 3.1 Daily financial row

```python
class DailyFinancialRowV1(BaseModel):
    date: date
    party_external_id: str | None
    party_name: str
    direction: Literal["receivable", "payable"]
    amount_paisa: int
    due_date: date
    reference: str
    settled_today_paisa: int = 0
    remaining_paisa: int
    account_source: str | None
    expense_category: str | None
    responsible_person_external_id: str | None
    dispute_flag: bool = False
    notes: str | None
```

### 3.2 Promise

```python
class PromiseV1(BaseModel):
    promise_id: UUID
    direction: Literal["made_by_us", "made_to_us"]
    counterparty_id: UUID
    description: str
    owner_id: UUID
    due_at: datetime
    condition: str | None
    evidence_ids: list[UUID]
    status: Literal["open", "fulfilled", "broken", "disputed", "cancelled"]
```

### 3.3 Delegation contract

```python
class TaskContractV1(BaseModel):
    outcome: str
    why_it_matters: str
    assignee_id: UUID
    due_at: datetime
    first_action: str
    authority_limit: str
    definition_of_done: list[str]
    required_evidence_types: list[str]
    dependencies: list[UUID]
    escalation_condition: str
    impact: Literal["low", "medium", "high", "critical"]
```

---

## 4. Tasks

### Task 1: Build source connector and import-batch framework

**Files:**
- Create: `services/core/app/modules/financial_awareness/connectors/base.py`
- Create: `services/core/app/modules/financial_awareness/connectors/csv_connector.py`
- Create: `services/core/app/modules/financial_awareness/models.py`
- Create: `services/core/app/modules/financial_awareness/schemas.py`
- Test: `services/core/tests/financial_awareness/test_import_batch.py`

**Interfaces:**
- Produces: `FinancialSourceConnector.read_batch() -> FinancialImportBatch`.

- [ ] Write failing tests for valid import, duplicate batch, corrupt file, missing columns and negative remaining amount.
- [ ] Implement SHA-256 file/batch identity and exact source metadata.
- [ ] Validate with Pandera before any row becomes a business event.
- [ ] Quarantine invalid rows without partially publishing the batch.
- [ ] Run `uv run pytest services/core/tests/financial_awareness/test_import_batch.py -v`.
- [ ] Commit with `git commit -m "feat: add read-only financial import framework"`.

### Task 2: Add optional read-only database connector and mutation test

**Files:**
- Create: `services/core/app/modules/financial_awareness/connectors/sql_connector.py`
- Create: `tests/security/test_financial_source_read_only.py`
- Create: `docs/runbooks/financial-source-credentials.md`

**Interfaces:**
- Produces: parameterized `SELECT` queries returning the Phase 2 contract.

- [ ] Create a test database user with only `CONNECT`, `USAGE` and `SELECT`.
- [ ] Write tests that `INSERT`, `UPDATE`, `DELETE`, `DROP` and stored procedure execution fail.
- [ ] Implement query timeout, maximum row count and source watermark.
- [ ] Log query hash, not raw credentials.
- [ ] Run security test and commit.

### Task 3: Normalize parties without unsafe automatic merges

**Files:**
- Create: `services/core/app/modules/parties/models.py`
- Create: `services/core/app/modules/parties/matcher.py`
- Create: `apps/desktop/src/features/financial/PartyResolutionQueue.tsx`
- Test: `services/core/tests/parties/test_matcher.py`

**Interfaces:**
- Produces: `match_party(name, external_id) -> ExactMatch | CandidateMatches | Unresolved`.

- [ ] Write tests for exact external ID, exact normalized name, 90%+ candidate and ambiguous names.
- [ ] Implement Unicode normalization and alias table.
- [ ] Never auto-merge on fuzzy name alone.
- [ ] Build one-click resolution queue with visible source rows.
- [ ] Persist human resolution as an auditable mapping.
- [ ] Commit.

### Task 4: Implement reconciliation and seven-day awareness

**Files:**
- Create: `services/core/app/modules/financial_awareness/service.py`
- Create: `services/core/app/modules/financial_awareness/scenarios.py`
- Test: `services/core/tests/financial_awareness/test_cash_awareness.py`

**Interfaces:**
- Produces: `build_cash_awareness(as_of) -> CashAwarenessView`.

- [ ] Test opening/closing mismatch, missing sequence, stale batch, disputed inflow and defensive mode.
- [ ] Calculate daily expected inflow/outflow without claiming bank balance certainty.
- [ ] In defensive mode, count disputed/unverified inflows as zero.
- [ ] Expose `verified`, `expected`, `disputed` and `unknown` separately.
- [ ] Commit.

### Task 5: Build financial awareness timeline UI

**Files:**
- Create: `apps/desktop/src/features/financial/CashAwarenessCard.tsx`
- Create: `apps/desktop/src/features/financial/SevenDayTimeline.tsx`
- Create: `apps/desktop/src/features/financial/ImportHealthPanel.tsx`
- Test: `apps/desktop/tests/financial-awareness.test.tsx`
- Test: `apps/desktop/tests/financial-awareness.spec.ts`

**Interfaces:**
- Consumes: `CashAwarenessView`.

- [ ] Test currency formatting, source links, stale state and defensive scenario labels.
- [ ] Render a restrained horizontal seven-day timeline; no decorative pie chart.
- [ ] Add keyboard-accessible evidence drill-down.
- [ ] Add customer-facing privacy masking.
- [ ] Run Vitest and Playwright; commit.

### Task 6: Implement Promise Graph

**Files:**
- Create: `services/core/app/modules/promises/models.py`
- Create: `services/core/app/modules/promises/service.py`
- Create: `services/core/app/modules/promises/api.py`
- Create: `apps/desktop/src/features/promises/PromiseGraph.tsx`
- Test: `services/core/tests/promises/test_lifecycle.py`

**Interfaces:**
- Produces: create, fulfil, dispute, cancel and mark-broken commands; no direct status updates.

- [ ] Write lifecycle tests including conditional and repeatedly delayed promises.
- [ ] Implement append-only status transitions.
- [ ] Link promises to parties, invoices, tasks and evidence.
- [ ] Visualize relationship and chronology; keep table alternative.
- [ ] Commit.

### Task 7: Implement delegation contracts and evidence-based completion

**Files:**
- Create: `services/core/app/modules/tasks/models.py`
- Create: `services/core/app/modules/tasks/service.py`
- Create: `services/core/app/modules/tasks/rules.py`
- Create: `apps/desktop/src/features/tasks/TaskCard.tsx`
- Create: `apps/desktop/src/features/tasks/EvidenceSubmitter.tsx`
- Test: `services/core/tests/tasks/test_completion.py`

**Interfaces:**
- Produces: `create_task_contract`, `submit_task_evidence`, `verify_task`, `reopen_task`.

- [ ] Test that incomplete delegation is rejected.
- [ ] Test that completion without required evidence fails.
- [ ] Implement assignee authority/dependency validation.
- [ ] Implement verifier separation for high-impact tasks.
- [ ] Build staff card showing outcome, why, first step, deadline and proof.
- [ ] Commit.

### Task 8: Implement structured staff escalation and Attention Firewall v1

**Files:**
- Create: `services/core/app/modules/escalations/models.py`
- Create: `services/core/app/modules/escalations/service.py`
- Create: `apps/desktop/src/features/escalations/EscalationForm.tsx`
- Create: `apps/desktop/src/features/escalations/DecisionBatch.tsx`
- Test: `services/core/tests/escalations/test_routing.py`

**Interfaces:**
- Produces: `route_escalation() -> immediate | batch | delegate | needs_information`.

- [ ] Test missing proposed option, safety emergency, reversible low-impact issue and owner-only deadline.
- [ ] Implement deterministic routing first; no LLM dependency.
- [ ] Require `situation`, `impact`, `attempted`, `options`, `recommendation`, `deadline`.
- [ ] Add emergency path with explicit misuse audit.
- [ ] Build owner decision batch.
- [ ] Commit.

### Task 9: Implement Counterparty Integrity Ledger and recovery workflow in draft-only mode

**Files:**
- Create: `services/core/app/modules/counterparties/integrity.py`
- Create: `services/core/app/modules/counterparties/risk_tiers.py`
- Create: `services/core/app/modules/recovery/models.py`
- Create: `services/core/app/modules/recovery/service.py`
- Create: `services/core/app/modules/recovery/templates.py`
- Create: `apps/desktop/src/features/counterparties/IntegrityLedger.tsx`
- Create: `apps/desktop/src/features/recovery/RecoveryMatrix.tsx`
- Test: `services/core/tests/counterparties/test_integrity_ledger.py`
- Test: `services/core/tests/recovery/test_stages.py`

**Interfaces:**
- Produces: evidence-linked `IntegrityAssessment`, owner-approved risk-tier recommendation, internal employee action and customer message draft; no send method.

- [ ] Calculate integrity only from observable business facts: on-time payment rate, Promise-to-Pay adherence, documented delivery variance, verified disputes and prior owner-approved exceptions.
- [ ] Every deduction must link to invoice, promise, payment or delivery evidence; unverified chat sentiment cannot reduce the score.
- [ ] Implement Tier 1 Normal, Tier 2 Caution and Tier 3 Cash-Only as recommendations; entering or leaving Tier 3 requires owner approval and a recorded reason.
- [ ] Never emit “liar”, “fraudster”, “snake” or criminal-intent labels. UI language is “payment risk”, “evidence conflict” or “verification required”.
- [ ] Add recovery/healing logic after cleared dues and three compliant cash transactions, but require owner confirmation before restoring credit.
- [ ] Test 24-hour sync buffer, dispute freeze, “paid/de diye/check” response and responsible employee routing.
- [ ] Implement VIP/dealer tone templates as versioned content.
- [ ] Prevent draft generation when financial source is stale.
- [ ] Show why each draft exists and who approved the credit originally.
- [ ] Commit.

### Task 10: Implement owner Re-Entry Capsule v1

**Files:**
- Create: `services/core/app/modules/cognitive/reentry/models.py`
- Create: `services/core/app/modules/cognitive/reentry/service.py`
- Create: `apps/desktop/src/features/reentry/ReentryCapsule.tsx`
- Test: `services/core/tests/cognitive/test_reentry.py`

**Interfaces:**
- Produces: `build_reentry_capsule(owner_id, since)`.

- [ ] Test unresolved thought/task/promise inclusion and privacy-domain exclusion.
- [ ] Use only OMNISCIENCE state and explicit owner notes in Phase 2.
- [ ] Provide “restore”, “dismiss” and “not relevant” feedback.
- [ ] Do not capture global screen/keystrokes.
- [ ] Commit.

### Task 11: Implement Delta Briefing and Apex Triad v1

**Files:**
- Create: `services/core/app/modules/briefing/service.py`
- Create: `services/core/app/modules/briefing/ranking.py`
- Create: `apps/desktop/src/features/briefing/DeltaBriefing.tsx`
- Create: `apps/desktop/src/features/briefing/ApexTriad.tsx`
- Test: `services/core/tests/briefing/test_ranking.py`

**Interfaces:**
- Produces: `DeltaBriefingView` with `rank_zero`, three priorities and all-signals link.

- [ ] Write ranking tests for deadline, financial gap, owner-only decision, reversible task and stale data.
- [ ] Implement deterministic initial priority score with documented normalized inputs.
- [ ] Never allow a high-downside item to disappear below top three.
- [ ] Build expandable evidence/assumption view.
- [ ] Commit.

### Task 12: Add import scheduler, overnight read-only run and Phase 2 acceptance

**Files:**
- Create: `services/core/app/workers/financial_import.py`
- Create: `services/core/app/workers/morning_briefing.py`
- Create: `tests/acceptance/test_phase_2.py`
- Create: `docs/runbooks/financial-import-failure.md`

**Interfaces:**
- Produces: idempotent scheduled import and briefing compilation jobs.

- [ ] Test duplicate schedule execution, power interruption and stale-source fallback.
- [ ] Implement durable job record before work starts.
- [ ] Run a 30-day fixture simulation covering missing/duplicate/disputed rows.
- [ ] Force Resource Governor Red state and verify imports, reconciliation, Promise Graph, tasks, recoveries and briefing remain available.
- [ ] Simulate 60% background CPU load and verify core API p95 stays `<= 500 ms`.
- [ ] Verify no source write and no external communication.
- [ ] Run full Phase 1 and Phase 2 test suites.
- [ ] Commit and tag `v0.2.0-owner-now`.

---

## 5. Phase 2 acceptance gate

- Thirty representative daily batches import without silent data loss.
- Invalid batches are quarantined and explained.
- Source mutation tests fail with permission denied.
- Defensive cash awareness never counts disputed inflows as available.
- Promise history cannot be rewritten.
- Tasks cannot close without required evidence.
- Staff incomplete escalations do not interrupt the owner.
- Every counterparty integrity deduction opens its underlying business evidence.
- Tier 3 Cash-Only cannot be applied or removed without owner approval and reason.
- No intent, deception or criminal label exists in the counterparty schema or UI.
- Recovery remains draft-only.
- All Phase 2 workflows pass with every AI worker stopped.
- Mixed-load core API p95 is `<= 500 ms` on the target PC.
- Owner can understand the top three issues and sources within five seconds.
- No Phase 1 permission, retention or restore regression.

## 6. Demo narrative

1. Import today’s receivable/payable file.
2. Resolve one ambiguous party.
3. Show seven-day gap and source lineage.
4. Convert three due recoveries into staff actions.
5. Submit incomplete task evidence and demonstrate rejection.
6. Submit a complete escalation and show decision batching.
7. Open Promise Graph.
8. Leave an unresolved owner note, end session and reopen.
9. Show Re-Entry Capsule and Delta Briefing.
