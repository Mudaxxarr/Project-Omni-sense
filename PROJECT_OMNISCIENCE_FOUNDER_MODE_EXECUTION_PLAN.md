# Project OMNISCIENCE — Founder Mode Autonomous Execution Plan

**Version:** 1.0  
**Date:** 29 July 2026  
**Status:** Implementation operating plan  
**Scope:** Nine phases, numbered Phase 0 through Phase 8  
**Primary rule:** A feature may be developed on an isolated branch, but it may not be integrated into `main` until its backend behavior, data contract, permissions, failure states, and visible user outcome have all been verified.

---

## 1. Executive decision

Project OMNISCIENCE should be built in **nine phases**:

1. Phase 0 — Founder Control Plane and Proof Harness
2. Phase 1 — Foundation, Trust Kernel and Command Shell
3. Phase 2 — Owner Now, Financial Awareness and Execution Discipline
4. Phase 3 — Customer Growth and Store Execution OS
5. Phase 4 — CEO Cognitive Exoskeleton
6. Phase 5 — Office Intelligence and Security Fusion Pilot
7. Phase 6 — Market Growth and Approved External Execution
8. Phase 7 — Prediction, Calibration and Governed Evolution
9. Phase 8 — Resilience, Visual Polish, Scale and v1.0 Productization

This resolves the mismatch between the master specification, which uses Phase 0–7, and the eight detailed implementation files, which use Phase 1–8. The detailed phase files remain the task-level sources; this document controls their execution order, integration gates, and autonomous verification loop.

The build is not organized as “finish backend, then build frontend.” It is organized as **thin, end-to-end vertical slices**. Each slice must produce a real user-visible outcome backed by real local services, deterministic fixtures, and auditable evidence.

---

## 2. What was analyzed

The source corpus contains ten project-owned Markdown files:

- `PROJECT_OMNISCIENCE_MASTER_SPEC.md`
- `2026-07-29-local-cpu-runtime-design.md`
- `01-foundation-trust-kernel.md`
- `02-owner-now-financial-execution.md`
- `03-customer-growth-execution-os.md`
- `04-ceo-cognitive-exoskeleton.md`
- `05-office-intelligence-security-fusion.md`
- `06-market-growth-approved-execution.md`
- `07-prediction-learning-evolution.md`
- `08-resilience-polish-scale.md`

Together they define approximately 30,720 words, 109 explicit implementation tasks, and 621 checklist steps.

The workspace currently contains specifications only:

- no Git repository;
- no application source;
- no package manifests;
- no database migrations;
- no test harness;
- no CI;
- no visual baselines;
- no runnable localhost or Electron application.

Implementation has therefore not started. Phase 0 is mandatory.

---

## 3. Source-of-truth hierarchy

When two documents appear to disagree, use this order:

1. **Master specification** — product scope, safety, authority, privacy, prohibited behavior, and business outcomes.
2. **Local CPU runtime design** — hardware limits, local-only inference, Resource Governor, storage quotas, model admission, and degradation.
3. **Detailed phase files** — task breakdown, interfaces, test ideas, visual intent, and phase-specific acceptance.
4. **This Founder Mode plan** — build order, autonomous permissions, vertical slicing, proof requirements, branch policy, and integration rules.
5. **Feature contract** — the approved executable definition for one feature slice.
6. **Code and tests** — implementation evidence; code may not silently redefine a higher-level source.

Any intentional change to items 1–3 must be recorded in an architecture or product decision record. Code is never allowed to resolve a specification conflict silently.

---

## 4. Deep audit findings

### 4.1 Architecture is coherent

The documents consistently converge on:

- one unified Electron/React application;
- a modular FastAPI backend;
- native PostgreSQL as the durable source of truth, job ledger, outbox, and lock authority;
- a separate Execution Gateway with no AI dependencies;
- local-only LLM, ASR, embedding, and vision inference;
- exactly one heavy AI lease;
- deterministic rules and core workflows that continue without AI;
- evidence, freshness, authority, and uncertainty visible in the UI;
- non-destructive recovery;
- existing POS/accounting remaining independent and authoritative.

This architecture should remain locked unless exact-PC benchmarks disprove a component.

### 4.2 The current roadmap is component-oriented

Many current tasks create models, services, workers, or individual components and then immediately request a commit. That can produce technically complete pieces without proving that a user can achieve the required outcome.

Founder Mode changes the unit of delivery from a component to a **verified vertical slice**:

```text
user intent
→ permission decision
→ API contract
→ durable state/event
→ visible UI state
→ evidence/freshness
→ failure behavior
→ automated and visual proof
```

Backend-only and frontend-only work may be checkpointed on a feature branch, but neither is integrated alone.

### 4.3 Visual verification is not yet an integration gate

The phase files contain Playwright and screenshot tasks, but do not define one universal rule preventing an unverified feature from entering the integrated product.

This plan adds a single `verify:feature` gate and an evidence bundle for every slice.

### 4.4 Two repository references need normalization

- Every detailed phase points to `docs/superpowers/specs/2026-07-29-local-cpu-runtime-design.md`, but the file currently exists at repository root.
- Every detailed phase refers to external `superpowers:*` execution skills. Those may remain useful hints, but the project cannot depend on an agent environment having them.

Phase 0 must move or copy the runtime design to the canonical referenced location and provide a repository-owned execution loop.

### 4.5 Human authority is intentionally required in a few places

The system can minimize routine approvals, but it must not remove approval from:

- real external messages, advertisements, listing/price changes, or customer promises;
- production credentials and provider accounts;
- monitored-zone activation and final legal/privacy policy;
- payment, transfer, trading, or employee-disciplinary actions, which remain prohibited;
- production model promotion;
- destructive production data operations;
- final production release and disaster-recovery cutover.

Reducing repeated prompts means pre-authorizing safe engineering work, not bypassing the product’s safety constitution.

### 4.6 Hardware constraints materially affect sequencing

The verified PC has 32 GB RAM but only about 9.2–9.7 GB observed free memory. The approved Deep Analyst gate requires at least 16 GB free. Therefore:

- Phase 1–3 must be completely useful without AI.
- Phase 4 begins with rules and full-text retrieval.
- A local model is admitted only after an exact-PC benchmark.
- Phase 5 ASR, vision, and Deep Analyst work must remain serialized.
- Failure to pass a model benchmark disables that candidate; it does not block the core product.

### 4.7 Production is already blocked by known environmental gates

Development may proceed, but v1.0 production signoff cannot occur while:

- Windows is on the Insider Preview channel;
- Secure Boot is off;
- BitLocker recovery is unverified;
- controlled available RAM cannot reach 16 GB;
- clean-room restore and mixed-load tests have not passed.

These are Phase 8 gates, not reasons to delay Phase 0–3 development.

### 4.8 The cross-phase dependency graph has seven critical bridges

The plans are not eight independent modules. Their important connections are:

1. **Trust Kernel → Event Spine → every business core.** Identity, source, evidence, audit, and append-only events are the shared foundation; Phase 2–7 must not create parallel truth systems.
2. **Lost-Sale Intelligence → Market Gap Strike.** Phase 3 missed demand becomes Phase 6 opportunity evidence. The shared product/customer/source IDs must be designed in Phase 3.
3. **Promise Graph → Meeting Commitments → Objective Event Correlation.** Phase 2 promises feed Phase 4 meeting preparation and Phase 5 verification; commitment identity and correction semantics must remain stable.
4. **Decision Journal → Prediction Register.** Phase 4 owner-confidence calibration and Phase 7 model calibration are different metrics but need compatible append-only review patterns.
5. **Campaign Attribution → Benefit Ledger.** Phase 6 action outcomes become Phase 7 benefit claims; deduplication identifiers must be introduced before campaigns execute.
6. **Resource Governor → Deep Analyst/ASR/Sentinel/Training.** Resource control is a Phase 1 dependency, not a Phase 8 optimization.
7. **Signal → Policy Decision Point → payload-bound approval → Gateway → readback.** External execution is one chain; no intermediate module may bypass it.

Feature contracts must declare which bridge they consume or produce so a later phase never discovers that an earlier identifier, event, or evidence contract is unusable.

---

## 5. Founder Mode autonomy charter

### 5.1 Default autonomous scope

Once implementation starts, the coding agent may proceed without asking again for routine actions inside the repository:

- read and edit workspace files;
- initialize and use the local Git repository;
- create feature branches and local commits;
- run formatting, lint, typecheck, unit, integration, contract, security, and Playwright tests;
- start and stop processes launched by this repository;
- start the local UI and API;
- create and migrate disposable/local development databases;
- generate deterministic fixtures and anonymized seed data;
- use browser automation, screenshots, traces, and videos for verification;
- fix frontend, backend, schema, migration, fixture, and test failures;
- repeat the implementation/verification loop until the slice passes;
- integrate a slice into `main` after every required gate is green;
- continue to the next unblocked slice.

### 5.2 One-time tool permission envelope

At the start of Phase 0, approve categories rather than individual commands where the environment supports it:

- `git` repository operations excluding destructive reset;
- `pnpm` install/build/test/lint/typecheck/dev;
- `uv` sync/run and Python test/migration commands;
- Playwright browser installation and tests;
- local PostgreSQL development commands;
- repository-owned PowerShell scripts under `infra/scripts` and `scripts`;
- local app/API launch and verified shutdown.

Lockfiles, hashes, and repository scripts define the allowed dependency versions. New undeclared system software or a new external service still requires a deliberate decision.

### 5.3 Actions that always require the owner or another authorized human

- entering or rotating a real secret;
- connecting a real accounting/POS source;
- enabling a real microphone/camera monitoring zone;
- accepting legal/privacy/employee-monitoring policy;
- sending/publishing to a real external provider;
- changing a real price or campaign budget;
- changing Windows security settings or production firewall/network rules;
- deleting or overwriting production data;
- promoting a model or release into production;
- changing a locked product/safety boundary.

### 5.4 Non-blocking fixture rule

If a real input is not yet available, development continues using a clearly labeled fixture or provider simulator. The slice may reach **fixture-verified** status but not **production-ready** status.

Examples:

- no POS export → use versioned sample financial batches;
- no WhatsApp credentials → use a provider emulator and contract tests;
- no approved monitored zone → use consented staged audio only;
- no FIDO2 key → use a test authenticator, never weaken the production contract;
- local model fails benchmark → use rules/manual/full-text mode.

---

## 6. The autonomous Founder Build Loop

Every feature slice follows the same loop.

### Step 1 — Create the feature contract

Create `docs/engineering/features/<feature-id>.yml` containing:

```yaml
id: P2-FIN-01
title: Import daily financial batch
source_requirements:
  - BIZ-17
roles:
  - accountant
  - owner
input_sources:
  - daily_financial_csv_v1
authority:
  observe: accountant
  correct_mapping: owner
  external_action: none
api_contracts:
  - POST /v1/financial-imports
visible_outcomes:
  - accepted batch summary
  - quarantined batch explanation
required_states:
  - loading
  - empty
  - success
  - partial
  - stale
  - denied
  - error
forbidden_outcomes:
  - source write
  - silent row loss
proof_scenarios:
  - valid batch
  - duplicate batch
  - missing column
  - ambiguous party
rollback:
  - disable feature flag and preserve imported audit events
```

No implementation begins until the contract is complete enough to write a failing acceptance test.

### Step 2 — Create failing proof first

Before production code:

- write backend unit/contract/integration tests;
- write permission and negative tests;
- write the Playwright user journey;
- define screenshot names and viewports;
- define expected audit/event/database facts;
- confirm the test fails for the intended reason.

### Step 3 — Implement the smallest end-to-end slice

Implement only enough backend, database, API, frontend, and fixture behavior to satisfy one coherent user outcome.

Do not build a large invisible backend in advance of its visible consumer.

### Step 4 — Run mechanical gates

The slice must pass:

- formatting and lint;
- TypeScript and Python type checks;
- unit tests;
- API/schema contract tests;
- migration upgrade/downgrade test where relevant;
- authorization/RLS tests;
- event, audit, evidence, and retention tests where relevant;
- integration tests against local PostgreSQL;
- previous-phase regression tests.

### Step 5 — Launch the real local stack

Use repository-owned scripts:

```text
scripts/doctor.ps1
scripts/start-local.ps1
scripts/seed-scenario.ps1 <scenario>
scripts/verify-feature.ps1 <feature-id>
scripts/stop-local.ps1
```

The start script must prove:

- PostgreSQL is accepting connections;
- core API `/health` returns 200;
- frontend dev server is reachable;
- Electron opens or its web-renderable shell is reachable;
- expected title/version/health content is present.

A port listener alone is not proof.

### Step 6 — Verify the visible outcome

For each required role and state:

1. open the real application with Playwright;
2. perform the actual user journey;
3. assert visible content, control state, keyboard behavior, and focus;
4. confirm no console error or failed network request;
5. capture screenshots at 1280×720, 1440×900, and 1920×1080;
6. inspect the screenshots visually, not only by pixel threshold;
7. compare displayed data with the API response and database/event facts;
8. confirm source, freshness, evidence, uncertainty, and authority are visible;
9. verify stale, denied, empty, loading, degraded, and error states where applicable;
10. save a Playwright trace for a critical journey.

### Step 7 — Diagnose and repair

If the visible result is wrong:

- correct API but wrong UI → fix frontend state, formatting, hierarchy, or interaction;
- wrong API/data → fix backend/domain/data contract before touching presentation;
- correct rows but wrong totals → fix calculation and add a regression fixture;
- intermittent result → fix transaction, job, lease, race, or idempotency behavior;
- permission mismatch → fix policy/RLS; never hide the control as a substitute;
- stale source shown as current → fix freshness propagation and disable consequential actions;
- visual overflow or unreadable state → fix the shared UI pattern, then rerun affected screenshots.

Repeat Steps 4–7 until all required proof passes.

After three identical failed approaches, change the implementation strategy and record the failed assumption. Do not repeatedly ask the owner to approve another routine attempt.

### Step 8 — Seal evidence and integrate

Write:

```text
artifacts/verification/<feature-id>/
  manifest.json
  test-results.xml
  api-contract.json
  audit-events.json
  screenshots/
  trace.zip
  console.log
  visual-review.md
```

`manifest.json` records:

- source commit;
- feature contract hash;
- test commands and results;
- database migration version;
- fixture versions;
- screenshots and viewports;
- roles/states exercised;
- known limitations;
- verifier identity/tool version.

Only then may the feature branch be squash-merged into `main`.

---

## 7. Definition of Integrated

A feature is integrated only when all applicable checks are true:

- requirement IDs are traceable;
- API and UI use the same versioned contract;
- durable state, events, audit, and evidence are correct;
- authorization and row scope are tested;
- retention and deletion behavior are defined;
- healthy and failure paths are implemented;
- the application was launched successfully;
- the primary user journey was completed against the real local stack;
- screenshots were captured and visually inspected;
- visible values match backend/database facts;
- console/network errors are zero;
- target resolutions and keyboard access pass;
- relevant previous-phase regression tests pass;
- rollback/disable behavior is documented;
- proof artifacts exist;
- no prohibited capability was introduced.

“Code written,” “unit tests pass,” and “screenshot looks fine” are each insufficient alone.

---

## 8. Branch, commit, and release policy

### 8.1 Branches

- `main` is always runnable and contains only verified slices.
- Work occurs on `feat/<feature-id>-<slug>`.
- Experimental model work occurs on `exp/<feature-id>-<slug>` and cannot enter production paths directly.
- Urgent verified fixes use `fix/<incident-id>-<slug>`.

### 8.2 Commits

Intermediate local commits are allowed on a feature branch for recovery and review. Existing phase-file “commit” steps are treated as branch checkpoints.

Integration means:

1. feature verification manifest is green;
2. branch is rebased/updated against `main`;
3. affected regression suite is rerun;
4. feature is squash-merged;
5. `main` smoke test is rerun;
6. the phase ledger is updated.

### 8.3 Release tags

```text
v0.0.1-control-plane
v0.1.0-foundation
v0.2.0-owner-now
v0.3.0-customer-execution
v0.4.0-cognitive-exoskeleton
v0.5.0-office-intelligence-pilot
v0.6.0-approved-execution
v0.7.0-governed-intelligence
v1.0.0-omniscience
```

---

## 9. Phase 0 — Founder Control Plane and Proof Harness

### Objective

Convert the blueprint folder into a deterministic, agent-operable repository where every later slice can be built, launched, visually inspected, repaired, and integrated without repeatedly asking for routine permission.

### Vertical slices

#### P0.1 — Canonical specification and traceability

- initialize Git;
- create the canonical `docs/` structure;
- place the runtime design at its referenced path;
- preserve original source documents in `docs/product/source/`;
- create ADRs for local-first modular architecture, events/evidence, UI system, and Resource Governor;
- create `REQUIREMENTS_TRACEABILITY.md`;
- map every TK/CEO/BIZ/OI/model/gateway requirement to a phase and future feature ID;
- record the source hierarchy from this plan.

#### P0.2 — Autonomous engineering control plane

- add `AGENTS.md` with the Founder Build Loop;
- add autonomy, decision, risk, phase, and blocked-input ledgers;
- add feature-contract and verification-manifest templates;
- add `doctor`, `start-local`, `stop-local`, `seed-scenario`, and `verify-feature` scripts;
- establish a local-only secret strategy and `.env.example`;
- establish feature flags and fixture/production-ready status.

#### P0.3 — Monorepo and native Windows runtime

- bootstrap pnpm, TypeScript, Python/uv, FastAPI, Electron/React/Vite, and shared contracts;
- connect native PostgreSQL 16 development service;
- exclude daily-production Docker, WSL2, Redis, RabbitMQ, Celery, Grafana, and cloud-model SDKs;
- add lint, typecheck, unit, integration, security, acceptance, and Playwright commands;
- add deterministic lockfiles.

#### P0.4 — Visual proof laboratory

- implement a web-renderable Command Shell plus Electron wrapper;
- add semantic design tokens;
- add a route/state laboratory for loading, empty, healthy, stale, degraded, denied, and error states;
- add Playwright, screenshot comparison, `axe` accessibility checks, console/network failure capture, and trace retention;
- establish 1280×720, 1440×900, and 1920×1080 baselines.

#### P0.5 — Scenario and fixture factory

- create anonymized users, roles, financial imports, customers, visits, products, promises, tasks, evidence, meetings, provider responses, and model outcomes;
- make time deterministic;
- make Asia/Karachi rendering and UTC storage testable;
- support valid, stale, duplicate, contradictory, denied, degraded, timeout, and recovery scenarios.

### Visual proof

- open the shell offline;
- show `NOW`, `THINK`, `PEOPLE`, and `MEMORY`;
- show `LOCAL ONLY: NO DATA LEAVES THIS PC`;
- switch through every state in the visual laboratory;
- stop the API and prove the stale overlay;
- capture the three viewport baselines with zero overflow and zero console error.

### Exit gate

- repository is initialized and clean;
- one command checks dependencies;
- one command starts the local stack;
- API and UI are reachable and proven;
- one command verifies the shell slice and writes a proof bundle;
- CI runs the same deterministic commands;
- the owner approves the visual North Star once;
- tag `v0.0.1-control-plane`.

---

## 10. Phase 1 — Foundation, Trust Kernel and Command Shell

### Objective

Make every later feature inherit identity, authorization, durable events, evidence lineage, audit, retention, resource status, freshness, and safe recovery.

### Vertical slices

1. Owner/staff login, session expiry, fresh reauthentication, user administration.
2. RBAC + ABAC + PostgreSQL RLS with a visible denied-access state.
3. Durable event + transactional outbox with recovery visibility.
4. Source/evidence registry + Evidence Drawer.
5. Tamper-evident audit + read-only Audit Timeline.
6. Retention policies + delete/preserve flows + deletion receipts.
7. Resource Governor + health/freshness/safe-state UI.
8. Encrypted backup + isolated restore report.

### Visual proof journey

Authenticate as owner, create a sales user, prove owner-memory denial, register evidence, inspect lineage, view an audit event, expire evidence, see a deletion receipt, stop the backend, see consequential controls lock, restore the service, and view a successful isolated-restore report.

### Exit gate

Use every Phase 1 acceptance item in `01-foundation-trust-kernel.md`, plus:

- each trust function has a visible user/admin state;
- three viewport visual matrix passes;
- no later module can bypass audit/retention through direct table access;
- complete proof bundle exists;
- tag `v0.1.0-foundation`.

---

## 11. Phase 2 — Owner Now, Financial Awareness and Execution Discipline

### Objective

Deliver the first daily-use version without any AI dependency or external send path.

### Vertical slices

1. Financial file import, validation, quarantine, batch identity, and import-health UI.
2. Optional read-only SQL connector and source mutation-denial proof.
3. Party resolution queue without fuzzy auto-merge.
4. Seven-day cash awareness with verified/expected/disputed/unknown separation.
5. Promise Graph with append-only lifecycle.
6. Task contracts and evidence-based completion.
7. Structured escalation and deterministic Attention Firewall.
8. Counterparty Integrity Ledger and draft-only recovery.
9. Re-Entry Capsule.
10. Delta Briefing and Apex Triad v1.
11. Durable schedules and 30-day fixture simulation.

### Visual proof journey

Import a batch, quarantine a bad batch, resolve an ambiguous party, open the cash timeline, prove disputed inflow becomes zero in defensive mode, create a promise, reject invalid task evidence, route an incomplete escalation back for information, prepare but do not send a recovery draft, close the day, and reopen into Re-Entry plus the Delta Briefing.

### Exit gate

- all workflows operate with AI workers disabled;
- no source write and no external communication code path exists;
- visible amounts reconcile to the fixture/source rows;
- owner identifies the top three issues and sources within five seconds;
- Phase 1 regression remains green;
- tag `v0.2.0-owner-now`.

---

## 12. Phase 3 — Customer Growth and Store Execution OS

### Objective

Turn visits, outcomes, product facts, lost sales, benefits, SOPs, and staff learning into a closed operational loop.

### Vertical slices

1. Consent-aware customer profile and relationship timeline.
2. Visit check-in, assignment, demo, outcome, and silent-exit handling.
3. Product catalog and freshness-aware inventory snapshots.
4. Rules-first Sales Workspace and three-product comparison.
5. Lost-Sale capture and weekly intelligence.
6. Bundles and accessory eligibility.
7. Trust Premium/Loyalty entitlements and redemption.
8. Installment opportunity guide without lending decisions.
9. Product Launch War Room.
10. Evidence-Based SOP runner and reviewer.
11. Opportunity-normalized capability and micro-coaching.
12. Approved Institutional Knowledge Library.
13. Owner Growth analytics and decomposable Top Dealer Score.

### Visual proof journey

Run anonymous, returning VIP, sale, lost-sale, installment, complaint, benefit-redemption, invalid-SOP-evidence, and corrected-knowledge scenarios. Compare visible funnel denominators and product freshness to backend facts.

### Exit gate

- common customer journey works without owner intervention;
- all recommendations are rules-first and source/freshness aware;
- lost sales cannot be rewritten;
- role redaction and customer privacy mode pass;
- full-text search remains the baseline;
- optional vectors remain disabled unless the exact benchmark passes;
- tag `v0.3.0-customer-execution`.

---

## 13. Phase 4 — CEO Cognitive Exoskeleton

### Objective

Create a private owner workspace that restores context, challenges thinking, records decisions, and closes the day without becoming a generic chatbot or gaining execution authority.

### Vertical slices

1. Owner-only memory vault and full-text retrieval.
2. Local Deep Analyst job boundary, schema validation, redaction, and resource lease.
3. Commander/Creator/Deep Work/People/Recovery modes.
4. Re-Entry and whitelisted Interruption Capsule.
5. Thought Capture and Thought Extension.
6. Reality-versus-Story and Contradiction cards.
7. Decision Chamber with facts, assumptions, unknowns, downside, and review.
8. Pre-Mortem and Future-Self simulations.
9. Decision Journal and calibration.
10. Meeting Pre-Brief and People workspace.
11. Creativity, patterns, private rehearsal, and Relationship Compass.
12. Nocturnal Sentinel and End-of-Day Seal.

### Visual proof journey

Run arrival → thought → contradiction → decision → simulation → interruption → meeting pre-brief → rehearsal → day seal → next-day re-entry. Repeat in Red state and prove manual/rules/full-text workflows remain usable.

### Exit gate

- staff/developer access to owner content is denied;
- no cloud-model hostname, credential, or inference route exists;
- every generated output separates facts, assumptions, and simulation;
- Deep Analyst meets the 120-second/8-GB Green-state gate or remains disabled;
- a second heavy job cannot start;
- owner accepts the experience as a cognitive operating room;
- tag `v0.4.0-cognitive-exoskeleton`.

---

## 14. Phase 5 — Office Intelligence and Security Fusion Pilot

### Objective

Introduce authorized meeting and declared-zone intelligence through staged, measurable pilots, never through immediate always-on monitoring.

### Mandatory rollout order

1. consented lab fixtures;
2. push-to-start meeting pilot;
3. one-zone shadow mode;
4. owner-reviewed limited-hour alerts;
5. controlled production only after legal, privacy, deletion, and metric gates.

### Vertical slices

1. Monitoring-zone policy, device registry, visible sensor status, and fail-closed activation.
2. Encrypted in-memory ring buffer and proof that irrelevant audio never reaches disk.
3. VAD, denoising, and acoustic-zone filtering.
4. ASR benchmark and code-switch evaluation.
5. Anonymous session-local diarization.
6. Selective encrypted clips, 72-hour deletion, delete-now, and preserve-with-reason.
7. Meeting consent, persistent recording indicator, and transcript review.
8. Topic/question/commitment extraction with human confirmation.
9. Observable 1–2 FPS visual features without emotion/deception mapping.
10. Evidence Conflict and Behavioral Deviation as separate explainable scores.
11. Business relevance/adoption-risk rules and candidate benchmark.
12. Objective event correlation.
13. Owner Review Inbox and correction loop.
14. Shadow pilot and adversarial failure-day acceptance.

### Visual proof journey

Prove invisible capture is impossible; start and stop a consented meeting; inspect anonymous transcript segments; confirm a commitment before publishing it; review an alert that says “DECEPTION NOT ESTABLISHED”; delete a clip; preserve another with a new expiry; show countdown; classify software criticism as feedback; disconnect mic/camera; force low-RAM and low-disk states; show graceful degradation.

### Exit gate

- policy/legal/notice approval exists before real monitoring;
- irrelevant raw audio on disk is zero;
- retention, invisible-capture, prohibited-verdict, and unauthorized-playback violations are zero;
- stated ASR, relevance, diarization, latency, memory, and API gates pass;
- no employee/customer action path exists;
- one-zone shadow pilot is explicitly accepted;
- tag `v0.5.0-office-intelligence-pilot`.

---

## 15. Phase 6 — Market Growth and Approved External Execution

### Objective

Convert lawful signals into bounded opportunities and exact-payload-approved actions through an isolated Gateway.

### Vertical slices

1. Lawful source registry, permission expiry, and acquisition limits.
2. Market-signal ingestion, deduplication, and parser quarantine.
3. Market Radar with evidence independence and freshness.
4. Market Gap Strike scoring with exposed component math.
5. Campaign Studio and preregistered Experiment Lab.
6. Execution Gateway with no AI/cloud-model dependency.
7. Payload-bound WebAuthn/FIDO2 approval.
8. Idempotency and uncertain-timeout readback.
9. Individual WhatsApp approved-send adapter.
10. Bounded Meta create/pause adapter.
11. Lightweight permission-gated marketplace/Daraz adapter.
12. Dynamic Authority Governor.
13. Honest campaign attribution.
14. Red-team, safe-state, and external-offline acceptance.

### Visual proof journey

Create an opportunity from multiple sources, inspect score math, edit an action and prove approval invalidation, approve a simulator payload with a test authenticator, double-click and prove one execution, simulate provider success plus lost response and prove readback before retry, trigger stock-floor auto-pause, activate safe state, and show exactly what stopped.

Real provider verification occurs only in an owner-authorized production-like window. All earlier work uses contract simulators.

### Exit gate

- no action can bypass deterministic policy and payload-bound approval;
- duplicate and unknown-timeout behavior is proven;
- no payment/trading credential or method exists;
- all AI reasoning remains local;
- Daraz remains optional and visually subordinate;
- tag `v0.6.0-approved-execution`.

---

## 16. Phase 7 — Prediction, Calibration and Governed Evolution

### Objective

Add probabilistic intelligence that is accountable, sealed before outcomes, benchmarked against frozen baselines, removable, and unable to execute.

### Vertical slices

1. Enhanced Truth/Evidence Kernel.
2. Immutable Prediction Register and hash chain.
3. Leakage-safe chronological feature pipeline.
4. Frozen moving-average and seasonal-naive baselines.
5. Probabilistic demand candidate and conformal/quantile intervals.
6. Outcome scoring and calibration dashboard.
7. OOD/drift warning, shadow-only, and disable controls.
8. Apex Triad v2 under hard Rank 0 overrides.
9. Benefit Ledger with causal grades and no double count.
10. Champion/Challenger blind holdout and shadow sandbox.
11. Signed human promotion and known-good rollback.
12. Advisory-only Treasury Laboratory.
13. Crisis, poisoning, and mixed-load acceptance.

### Visual proof journey

Seal a forecast, attempt and fail to edit it, reveal evidence cutoff, score an outcome, show coverage and interval width, inject a price shock and watch the model demote, compare champion/challenger, reject an overfit candidate, alter an artifact and prove signature failure, and show that Treasury has no action control.

### Exit gate

- no look-ahead leakage;
- candidate beats the preregistered baseline and harm gates;
- prediction remains shadow until promotion criteria pass;
- drift disables unsafe use;
- training stays within time/RAM/disk/CPU quotas;
- no forecast or score can call the Gateway;
- tag `v0.7.0-governed-intelligence`.

---

## 17. Phase 8 — Resilience, Visual Polish, Scale and v1.0

### Objective

Prove the complete product under real hardware, failure, security, accessibility, and full-business-day conditions.

### Vertical slices

1. Production hardware, OS, storage, UPS, and sensor baseline.
2. Network segmentation and Gateway-only egress.
3. Endpoint hardening, secrets, signed reproducible releases, and SBOM.
4. Bounded observability with sensitive-data redaction.
5. Fortress safe-state orchestration.
6. 3-2-1 backup and clean-room restore/reconciliation.
7. Full red-team and insider-threat review.
8. Performance, offline tolerance, and three-hour mixed load.
9. Unified visual pattern audit and regression suite.
10. Accessibility, localization, and Roman Urdu resilience.
11. Multi-branch/tenant isolation.
12. Safe shared product-kernel boundary.
13. Role-based training and monthly governance.
14. Complete owner business-day acceptance.

### Visual proof journey

Run the complete day:

```text
morning re-entry
→ Delta Briefing
→ financial import/recovery
→ customer visit/recommendation/lost sale
→ SOP/evidence
→ authorized meeting
→ review selective alert
→ approved external simulator/real controlled action
→ sealed shadow prediction
→ Fortress failure
→ recovery
→ End-of-Day Seal
```

Capture the journey at all target resolutions and with owner, manager, staff, finance, and marketing roles.

### Exit gate

- every prior phase acceptance suite passes;
- stable Windows, Secure Boot, BitLocker recovery, and controlled RAM gates pass;
- clean-room restore succeeds without overwriting healthy data;
- three-hour mixed-load latency and memory ceilings pass;
- no prohibited capability or cloud-model path exists;
- owner and staff training is complete;
- owner signs visual and functional acceptance;
- tag `v1.0.0-omniscience`.

---

## 18. Universal visual verification matrix

Every feature contract selects applicable rows from this matrix.

### Viewports

- 1280×720 — minimum supported desktop
- 1440×900 — primary design baseline
- 1920×1080 — full desktop

### Roles

- owner
- manager
- sales staff
- finance operator
- marketing operator
- developer/system administrator
- unauthenticated/expired session

### Data/runtime states

- first-run/empty
- normal healthy
- loading
- partial
- stale
- contradictory
- permission denied
- validation error
- backend offline
- external provider offline
- Resource Governor Green/Yellow/Orange/Red
- safe state
- recovery

### Visual quality checks

- no overflow, clipping, overlap, or unreadable mixed-language content;
- semantic color plus text/icon, never color alone;
- stable action locations;
- evidence/freshness/authority visible;
- red reserved for verified urgency or policy breach;
- loading is honest; queued local AI never uses an unexplained spinner;
- destructive and irreversible actions are separated;
- sensitive information is masked in customer-facing mode;
- keyboard focus and screen-reader name are correct;
- empty/error/degraded states remain useful.

---

## 19. Regression strategy

Use a layered suite so fast feedback stays fast:

1. **On file change:** formatter, targeted unit test, targeted typecheck.
2. **Before feature proof:** affected unit, contract, integration, policy, and Playwright tests.
3. **Before merge:** feature proof plus affected prior-phase suite.
4. **Nightly/local scheduled:** all unit/integration/security/visual suites and fixture matrix.
5. **Before phase tag:** every completed phase acceptance suite, clean install, backup/restore where applicable.
6. **Before v1.0:** full business day, three-hour mixed load, red team, clean-room restore, accessibility, localization, and signed-release verification.

Flaky tests are defects. They are fixed or the slice remains unintegrated; they are not silently retried until green.

---

## 20. Owner touchpoints: few, batched, consequential

Routine engineering does not need repeated owner permission. Owner input is batched into these checkpoints.

### Kickoff pack — once in Phase 0

- roles, branch/department boundaries, and authority limits;
- Six Pillars definitions;
- visual North Star;
- anonymized sample POS/accounting layout;
- KPI dictionary and baseline;
- price/margin floors, recovery stages, and tone policy;
- consent and customer-communication practice.

### Phase 4 pack

- owner-memory retention/export/delete choices;
- approved memory sources;
- exact-PC model benchmark acceptance.

### Phase 5 pack

- declared monitoring zones and excluded areas;
- written employee/customer/visitor policy;
- notice wording;
- approved sensors/hours/retention/review roles;
- local legal review;
- acceptance of the one-zone shadow pilot.

### Phase 6 pack

- real provider accounts and least-privilege credentials;
- budget, price, stock, recipient, and velocity limits;
- FIDO2/WebAuthn production credential;
- one controlled real-action window.

### Phase 8 pack

- OS/security maintenance window;
- production network/backup topology;
- staff training;
- residual-risk acceptance;
- final owner signoff.

If an input is missing, the project continues in fixture/shadow mode and records the production-readiness block.

---

## 21. Risk register and automatic response

| Risk | Automatic response |
|---|---|
| POS format unavailable | Continue with versioned fixture; block only real-source acceptance. |
| Accounting mutation risk | File import first; SQL connector remains off until mutation tests prove denial. |
| Low free RAM | Queue/unload AI; Core Business Lane continues. |
| Model fails accuracy/latency/RAM | Reject candidate; retain rules/manual/full-text workflow. |
| ASR accuracy weak for local speech | Stay in lab/shadow mode; expand consented frozen corpus. |
| Monitoring policy incomplete | No real capture; staged fixtures only. |
| Provider permission absent | Hide adapter; use emulator. |
| Provider timeout | Persist unknown state and read back before retry. |
| Stale data | Mark visibly and disable consequential actions. |
| Retention worker failure | Rank 0 privacy incident; stop new capture. |
| Visual regression | Block integration and repair shared pattern or slice. |
| Flaky test | Treat as failure; identify nondeterminism. |
| Specification conflict | Stop that slice, record decision, continue unrelated slices. |
| Production security gate fails | Continue development; prohibit production tag/cutover. |

---

## 22. Immediate implementation order

When the owner says “start,” execute in this order:

1. initialize Git and create `main`;
2. preserve/canonicalize all source specifications;
3. create ADRs, autonomy charter, traceability, risk, decision, and phase ledgers;
4. create feature-contract and verification templates;
5. bootstrap pnpm/uv/FastAPI/Electron/PostgreSQL;
6. create deterministic `doctor/start/seed/verify/stop` scripts;
7. build the semantic token system and Command Shell;
8. add Playwright, accessibility, screenshot, console, network, and trace proof;
9. run and visually inspect P0 shell scenarios;
10. integrate P0 only after the proof bundle is green;
11. proceed slice-by-slice through Phase 1 without asking for routine permission.

---

## 23. Final success condition

Founder Mode is working when the repository can repeatedly perform this loop without owner supervision:

```text
select next unblocked feature contract
→ create isolated branch
→ write failing mechanical and visual proof
→ implement end-to-end slice
→ start real local stack
→ exercise the user journey
→ inspect visible result and backend facts
→ repair until correct
→ seal proof bundle
→ integrate into main
→ rerun smoke/regression
→ update ledger
→ continue
```

The owner is interrupted only for a genuine business, legal, security, credential, production, or product-boundary decision.

That is the correct form of autonomy for OMNISCIENCE: aggressive automation inside a clear evidence and authority boundary.
