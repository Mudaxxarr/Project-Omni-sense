# Phase 6 — Market Intelligence, Growth and Approved External Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn lawful market/customer signals into controlled opportunities, approved campaigns, individualized recovery messages and bounded marketplace actions through an isolated execution gateway.

**Architecture:** The fully local Intelligence Plane creates drafts only. A deterministic Policy Decision Point evaluates the exact payload; owner WebAuthn/FIDO2 approval binds that payload; a separate native Windows Gateway process performs idempotent provider calls and stores readback. Internet is used for authorized business providers, never for AI inference.

**Tech Stack:** Existing native-Windows stack plus separate FastAPI Gateway service, PostgreSQL durable action ledger, WebAuthn/FIDO2, provider SDK adapters, Playwright for permitted public-page tests and statistical experiment tooling. RabbitMQ, Celery, Docker Desktop and cloud-model SDKs are excluded.

**Governing Runtime Design:** `docs/superpowers/specs/2026-07-29-local-cpu-runtime-design.md` applies to every task and acceptance gate.

## Global Constraints

- Only official APIs, owner-authorized exports and legally accessible public information.
- No private-chat interception, credential sharing, captcha bypass or hidden competitor-system access.
- Daraz remains approximately 10% of product attention.
- No external action without exact-payload approval.
- AI confidence alone cannot pass policy.
- Recovery sends are individualized; no unsupervised bulk blast.
- Campaigns use pre-approved templates and official product assets.
- Price, budget, recipient, velocity and stock guardrails are deterministic.
- Provider timeout requires readback before retry.
- No payments, bank transfers, trades or credit commitments.
- Market interpretation, drafting and campaign reasoning remain local; external APIs receive only approved provider payloads.
- Gateway and provider jobs use PostgreSQL durable state and cannot acquire an AI heavy lease.

---

## 1. Phase outcome

The owner sees:

```text
MARKET OPPORTUNITY • REVIEW

OPPO A78 REGIONAL SHORTAGE                    SCORE 84/100

Evidence
A  Internal lost-sale spike: 11 requests / 48h
B  Two authorized supplier notices: delayed restock
C  Public listings: 7/10 unavailable

Alhamd
Stock: 9 units • Campaign floor: 3 • Margin band: Healthy

Prepared action
Meta campaign • Khanewal +10 km • 1,200 PKR/day • 48 hours
Template: “Ready stock + Original Charger Guarantee”

[VIEW MATH] [EDIT] [APPROVE WITH YUBIKEY] [REJECT]
```

After approval:

```text
EXECUTION VERIFIED
Provider campaign ID: 92841
Budget readback: 1,200 PKR/day
Auto-pause: stock ≤3 or 48h
Idempotency: satisfied
```

---

## 2. Visual design

### 2.1 Growth Studio

Three columns:

1. **Signal:** evidence and uncertainty.
2. **Draft:** audience, content, offer and assets.
3. **Guardrails:** stock floor, budget, expiry and approval.

Never hide campaign downside or attribution uncertainty.

### 2.2 Approval card

Use a fixed layout for all external actions:

```text
ACTION       SEND WHATSAPP TEMPLATE
RECIPIENT    Safwan • +92•••••041
CONTENT      Exact final message
SOURCE       Invoice 4054 • due +3 days
RISK         Relationship sensitivity: VIP
EXPIRES      10 minutes
UNDO         Not supported after provider acceptance

[TOUCH SECURITY KEY TO APPROVE]
```

---

## 3. Contracts

### 3.1 Market signal

```python
class MarketSignalV1(BaseModel):
    signal_id: UUID
    signal_type: str
    source_id: UUID
    observed_at: datetime
    product_id: UUID | None
    region: str | None
    claim: str
    evidence_grade: Literal["A", "B", "C", "D"]
    freshness_expires_at: datetime
    permission_basis: str
```

### 3.2 External action

```python
class ExternalActionV1(BaseModel):
    action_id: UUID
    action_type: Literal[
        "whatsapp_send",
        "meta_campaign_create",
        "meta_campaign_pause",
        "marketplace_price_update",
    ]
    exact_payload: dict
    policy_version: str
    evidence_ids: list[UUID]
    requested_by: UUID
    idempotency_key: str
    nonce: str
    expires_at: datetime
```

### 3.3 Approval assertion

```python
class ApprovalAssertionV1(BaseModel):
    action_id: UUID
    payload_sha256: str
    credential_id: str
    webauthn_assertion: dict
    approved_by: UUID
    approved_at: datetime
```

---

## 4. Tasks

### Task 1: Implement lawful source registry and acquisition policy

**Files:**
- Create: `services/core/app/modules/market_sources/models.py`
- Create: `services/core/app/modules/market_sources/service.py`
- Create: `apps/desktop/src/features/market/SourceAdmin.tsx`
- Test: `services/core/tests/market_sources/test_permission_expiry.py`

**Interfaces:**
- Produces: active source with method, permission basis, rate and freshness limits.

- [ ] Test expired permission, private source, unsupported method and stale signal.
- [ ] Require owner approval before activating a scraper/API source.
- [ ] Store terms/permission reference and collection limits.
- [ ] Disable source automatically when permission expires.
- [ ] Commit.

### Task 2: Build market-signal ingestion

**Files:**
- Create: `services/core/app/modules/market_signals/service.py`
- Create: `services/core/app/modules/market_signals/dedup.py`
- Create: `services/core/app/modules/market_signals/connectors/manual.py`
- Create: `services/core/app/modules/market_signals/connectors/public_page.py`
- Test: `services/core/tests/market_signals/test_ingestion.py`

**Interfaces:**
- Produces: validated `MarketSignalV1`.

- [ ] Test duplicates, echo sources, changed page schema, rate limit and human report.
- [ ] Keep raw public evidence snapshot within permitted retention.
- [ ] Treat identical reposts as correlated, not independent corroboration.
- [ ] Quarantine parser/schema changes.
- [ ] Commit.

### Task 3: Implement Market Intelligence Radar

**Files:**
- Create: `services/core/app/modules/market_intelligence/service.py`
- Create: `apps/desktop/src/features/market/MarketRadar.tsx`
- Test: `services/core/tests/market_intelligence/test_evidence_grades.py`

**Interfaces:**
- Produces: what changed, why it matters, affected products/customers, recommended verification and urgency.

- [ ] Test single weak signal, multiple correlated signals and authoritative source.
- [ ] Never state hidden competitor stock/intention as fact.
- [ ] Show source independence and freshness.
- [ ] Commit.

### Task 4: Implement Market Gap Strike scoring

**Files:**
- Create: `services/core/app/modules/opportunities/market_gap.py`
- Create: `services/core/app/modules/opportunities/policies.py`
- Create: `apps/desktop/src/features/market/OpportunityCard.tsx`
- Test: `services/core/tests/opportunities/test_market_gap.py`

**Interfaces:**
- Produces: normalized score, components, hard-block reasons and action draft eligibility.

- [ ] Encode 25% evidence, 20% demand gap, 20% stock coverage, 15% contribution, 10% expiry, 10% reversibility.
- [ ] Test stale stock, below-floor margin, weak single source and insufficient campaign stock.
- [ ] Expose full component math.
- [ ] Commit.

### Task 5: Build Growth and Community campaign planner

**Files:**
- Create: `services/core/app/modules/campaigns/models.py`
- Create: `services/core/app/modules/campaigns/service.py`
- Create: `apps/desktop/src/features/growth/CampaignStudio.tsx`
- Test: `services/core/tests/campaigns/test_audience_consent.py`

**Interfaces:**
- Produces: campaign draft with segment, content, asset, budget, expiry and attribution plan.

- [ ] Test consented/non-consented audience, expired offer and unavailable product.
- [ ] Use approved Mad-Libs templates; no free-form price promise.
- [ ] Link every campaign to business objective and primary metric.
- [ ] Commit.

### Task 6: Implement Business Experimentation Lab

**Files:**
- Create: `services/core/app/modules/experiments/models.py`
- Create: `services/core/app/modules/experiments/service.py`
- Create: `services/core/app/modules/experiments/assignment.py`
- Create: `apps/desktop/src/features/experiments/ExperimentDesigner.tsx`
- Test: `services/core/tests/experiments/test_assignment.py`

**Interfaces:**
- Produces: preregistered randomized/switchback assignment and result shell.

- [ ] Require hypothesis, population, primary metric, harm metric, duration and stop rule.
- [ ] Test deterministic assignment and no post-hoc primary metric changes.
- [ ] Keep experiment result separate from organic totals.
- [ ] Commit.

### Task 7: Create isolated Execution Gateway skeleton

**Files:**
- Create: `services/gateway/app/main.py`
- Create: `services/gateway/app/policy.py`
- Create: `services/gateway/app/idempotency.py`
- Create: `services/gateway/app/providers/base.py`
- Create: `services/gateway/tests/test_no_ai_imports.py`
- Create: `infra/windows/install-gateway-service.ps1`
- Create: `infra/windows/gateway-service.xml`

**Interfaces:**
- Consumes: approved `ExternalActionV1` plus `ApprovalAssertionV1`.
- Produces: provider readback.

- [ ] Add architectural test that Gateway dependencies contain no LLM/model packages.
- [ ] Add architectural test that Gateway dependencies contain no RabbitMQ, Celery or cloud-model SDK.
- [ ] Give Gateway a separate database role and narrow network egress.
- [ ] Package Gateway as a native Windows service with recovery restart and no Docker/WSL dependency.
- [ ] Validate schema, policy, nonce, expiry, payload hash and assertion.
- [ ] Default deny unknown action/provider.
- [ ] Commit.

### Task 8: Complete FIDO2/WebAuthn payload-bound approval

**Files:**
- Create: `services/core/app/modules/approvals/webauthn.py`
- Create: `apps/desktop/src/features/approvals/ApprovalCard.tsx`
- Create: `services/gateway/app/approval_verifier.py`
- Test: `tests/security/test_payload_bound_approval.py`

**Interfaces:**
- Produces: challenge derived from canonical action payload hash.

- [ ] Test changed recipient, budget, content, expired challenge, replayed nonce and wrong credential.
- [ ] Render exact payload before requesting key touch.
- [ ] Require a new assertion after any edit.
- [ ] Store assertion and policy decision as evidence.
- [ ] Commit.

### Task 9: Implement Gateway idempotency and uncertain-timeout reconciliation

**Files:**
- Create: `services/gateway/app/execution.py`
- Create: `services/gateway/app/reconciliation.py`
- Test: `services/gateway/tests/test_idempotency.py`
- Test: `services/gateway/tests/test_timeout_readback.py`

**Interfaces:**
- Produces: `accepted`, `rejected`, `unknown_pending_reconciliation`, `confirmed`.

- [ ] Test concurrent duplicate requests and provider success with lost response.
- [ ] Persist request before provider call.
- [ ] Query provider/readback before retry.
- [ ] Never blindly duplicate an unknown action.
- [ ] Commit.

### Task 10: Implement WhatsApp approved-send adapter

**Files:**
- Create: `services/gateway/app/providers/whatsapp.py`
- Create: `services/core/app/modules/messages/drafts.py`
- Modify: `apps/desktop/src/features/recovery/RecoveryMatrix.tsx`
- Test: `services/gateway/tests/providers/test_whatsapp.py`

**Interfaces:**
- Produces: approved template send and provider message ID.

- [ ] Test template mismatch, recipient mismatch, opt-out, rate cap and provider rejection.
- [ ] Require individualized draft selection.
- [ ] Store exact sent content/readback.
- [ ] No “send all” recovery control.
- [ ] Commit.

### Task 11: Implement Meta campaign adapter and automatic bounded pause

**Files:**
- Create: `services/gateway/app/providers/meta_ads.py`
- Create: `services/gateway/app/monitors/campaign_limits.py`
- Create: `apps/desktop/src/features/growth/ActiveCampaign.tsx`
- Test: `services/gateway/tests/providers/test_meta_ads.py`

**Interfaces:**
- Produces: create/pause only within approved account, budget and duration.

- [ ] Test over-budget, stock floor, expiry, click anomaly and provider mismatch.
- [ ] Auto-pause is allowed because it reduces exposure; budget increase is not.
- [ ] Reconcile spend and state.
- [ ] Commit.

### Task 12: Implement bounded marketplace/Daraz adapter

**Files:**
- Create: `services/gateway/app/providers/marketplace.py`
- Create: `services/core/app/modules/daraz/summary.py`
- Create: `apps/desktop/src/features/daraz/DarazLight.tsx`
- Test: `services/gateway/tests/providers/test_marketplace_price.py`

**Interfaces:**
- Produces: lightweight status and owner-approved price update if official support exists.

- [ ] Test price floor/ceiling, stale cost, wrong listing and unsupported provider.
- [ ] Keep module hidden/disabled when official permission is absent.
- [ ] Keep Daraz navigation visually subordinate.
- [ ] Commit.

### Task 13: Implement Dynamic Authority Governor

**Files:**
- Create: `services/core/app/modules/authority/models.py`
- Create: `services/core/app/modules/authority/service.py`
- Create: `apps/desktop/src/features/authority/AuthorityMatrix.tsx`
- Test: `services/core/tests/authority/test_caps.py`

**Interfaces:**
- Produces: category level, hard maximum, promotion proposal and automatic demotion.

- [ ] Encode the master authority matrix.
- [ ] Test payment/trading and employee discipline cannot exceed their caps.
- [ ] Require owner FIDO2 for promotion.
- [ ] Auto-demote on policy violation, repeated undo or stale data.
- [ ] Commit.

### Task 14: Implement campaign impact with honest attribution

**Files:**
- Create: `services/core/app/modules/attribution/service.py`
- Create: `services/core/app/modules/attribution/grades.py`
- Create: `apps/desktop/src/features/growth/CampaignImpact.tsx`
- Test: `services/core/tests/attribution/test_grades.py`

**Interfaces:**
- Produces: Grade A/B/C/D impact with interval and caveats.

- [ ] Test promo-code sale, holdout lift, baseline correlation and unverifiable anecdote.
- [ ] Never count Grade C/D as exact causal value.
- [ ] Separate Meta-reported attribution from internal estimate.
- [ ] Commit.

### Task 15: Run red-team and external-action acceptance

**Files:**
- Create: `tests/security/test_phase_6_gateway.py`
- Create: `tests/acceptance/test_phase_6_actions.py`
- Create: `docs/runbooks/provider-unknown-state.md`
- Create: `docs/runbooks/global-safe-state.md`

- [ ] Attempt prompt injection to bypass Gateway.
- [ ] Attempt modified payload after approval.
- [ ] Simulate duplicate click and provider timeout.
- [ ] Push excessive ad budget and below-floor price.
- [ ] Activate safe state and verify new outbound calls stop while local POS/core remains available.
- [ ] Disable internet and verify all market reasoning/drafts remain local while provider actions enter an honest external-offline state.
- [ ] Verify the Resource Governor can pause AI without interrupting Gateway reconciliation.
- [ ] Verify no payment/trading credential exists.
- [ ] Commit and tag `v0.6.0-approved-execution`.

---

## 5. Phase 6 acceptance gate

- Every active source has documented permission and expiry.
- Opportunity cards expose source independence, freshness and component score.
- No hidden competitor-stock/intention claim exists.
- Edited payload invalidates approval.
- Replayed/duplicate actions are rejected or return prior readback.
- Recovery sends remain individualized.
- Campaign auto-pause works at stock, budget and expiry limits.
- Price write cannot cross configured floor/ceiling.
- Daraz remains lightweight and permission-gated.
- Safe state stops side effects without deleting data.
- Authorized business APIs are the only network use; no transcript/prompt/model-inference request leaves the PC.
- Gateway runs as a native Windows service without Docker, RabbitMQ or Celery.
- No bank/broker/payment execution capability exists.
