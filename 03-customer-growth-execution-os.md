# Phase 3 — Customer Growth and Execution OS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn customer visits, sales, lost sales, products, trust benefits, installments, staff knowledge and SOP execution into a closed learning loop.

**Architecture:** Extend the Business Core with customer and operational aggregates built from durable events. Keep sale/accounting references read-only; OMNISCIENCE owns customer workflow, recommendations, tasks and evidence—not invoices or ledgers.

**Tech Stack:** Existing native-Windows stack plus PostgreSQL full-text search, optional `pgvector` only after a measured retrieval benchmark, XState for complex UI flows and Playwright device/store-journey tests. No customer workflow requires a loaded local language model.

**Governing Runtime Design:** `docs/superpowers/specs/2026-07-29-local-cpu-runtime-design.md` applies to every task and acceptance gate.

## Global Constraints

- Customer data access follows role, branch and purpose.
- No recommendation may invent stock, price, eligibility or guarantee.
- Product price/cost originates from approved read-only sources or authenticated owner input.
- AI supports staff; it never impersonates a salesperson or sends a customer message.
- Lost sales are first-class records and cannot be rewritten into successful outcomes.
- Staff evaluation uses opportunity and verified actions, not raw sales count alone.
- Household/referral relationships require a legitimate business purpose and owner-approved policy.
- No continuous audio/video is introduced in this phase.
- Deterministic rules and verified catalog data produce the default sales recommendations.
- Every customer/store workflow remains available in Resource Governor Red state.
- Semantic retrieval is optional; PostgreSQL full-text search is the frozen baseline.

---

## 1. Phase outcome

When a customer arrives, staff receive one guided workspace:

```text
SAFWAN • RETURNING VIP • BUDGET 75–90K

PURPOSE
Upgrade from Reno 8 • camera + battery priority

COMPARE
1. Oppo Reno 12      Ready stock     Margin band: Healthy
2. Vivo V40          Ready stock     Margin band: Healthy
3. Samsung A55       Low stock       Owner quote approval below floor

VALUE TO EXPLAIN
No-Regret Swap • Charger Guarantee • Priority setup

NEXT BEST QUESTION
“Is camera more important in daylight or low light?”

[START COMPARISON] [SAVE SHORTLIST] [RECORD OUTCOME]
```

The owner sees conversion, lost demand, staff capability and customer lifetime signals rather than a sales leaderboard alone.

---

## 2. Visual system

### 2.1 Staff workspace principles

- One customer at a time.
- Large customer purpose at top.
- Three comparison choices maximum by default.
- Stock/margin states use words plus color.
- No confidential exact margin visible to unauthorized staff.
- A persistent “Record outcome” control prevents silent walk-outs.

### 2.2 Customer profile

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ SAFWAN                         VIP • TRUST TIER 2        LAST: 19 JUN 2026  │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ RELATIONSHIP                  │ NEXT BEST ACTION                            │
│ Current: Reno 8               │ Upgrade review due in 12 days              │
│ 3 purchases • 2 referrals     │ Evidence: 22-month ownership + inquiry     │
│ 1 resolved complaint          │ [PREPARE CALL DRAFT]                        │
├───────────────────────────────┼─────────────────────────────────────────────┤
│ ENTITLEMENTS                  │ HISTORY                                     │
│ No-Regret Swap: Eligible      │ Visit • Sale • Complaint • Resolution      │
│ Priority Setup: Active        │                                             │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

### 2.3 Owner Growth view

Use funnels only where stages have reliable denominators. Show:

- Visits.
- Properly attended.
- Demo completed.
- Offer presented.
- Sale.
- Follow-up lead.
- Silent exit.

---

## 3. Core contracts

### 3.1 Visit

```python
class VisitV1(BaseModel):
    visit_id: UUID
    customer_id: UUID | None
    arrived_at: datetime
    purpose: str
    assigned_staff_id: UUID
    requirements: list[str]
    budget_min_paisa: int | None
    budget_max_paisa: int | None
    outcome: Literal["sale", "lead", "lost", "service", "unknown"]
    evidence_ids: list[UUID]
```

### 3.2 Lost sale

```python
class LostSaleV1(BaseModel):
    visit_id: UUID
    interested_product_ids: list[UUID]
    quoted_price_paisa: int | None
    stock_available: bool | None
    reason_code: str
    objection: str | None
    competitor_alternative: str | None
    follow_up_possible: bool
    estimated_contribution_range_paisa: tuple[int, int] | None
```

### 3.3 Recommendation

```python
class SalesRecommendationV1(BaseModel):
    customer_or_visit_id: UUID
    generated_at: datetime
    product_options: list[UUID]
    questions_to_ask: list[str]
    approved_claims: list[str]
    bundle_options: list[UUID]
    uncertainty_notes: list[str]
    source_event_ids: list[UUID]
    model_or_rule_version: str
```

---

## 4. Tasks

### Task 1: Build customer master and consent-aware relationship model

**Files:**
- Create: `services/core/app/modules/customers/models.py`
- Create: `services/core/app/modules/customers/schemas.py`
- Create: `services/core/app/modules/customers/service.py`
- Create: `apps/desktop/src/features/customers/CustomerProfile.tsx`
- Test: `services/core/tests/customers/test_profile_access.py`

**Interfaces:**
- Produces: customer create/update-by-event, relationship timeline and purpose-scoped profile.

- [ ] Test branch access, restricted notes, duplicate phone handling and consent withdrawal.
- [ ] Store normalized contact separately from display values.
- [ ] Implement timeline from sale references, visits, complaints, promises and entitlements.
- [ ] Build profile with role-dependent redaction.
- [ ] Commit.

### Task 2: Implement visit orchestration and queue

**Files:**
- Create: `services/core/app/modules/visits/models.py`
- Create: `services/core/app/modules/visits/service.py`
- Create: `apps/desktop/src/features/visits/VisitCheckIn.tsx`
- Create: `apps/desktop/src/features/visits/VisitQueue.tsx`
- Test: `services/core/tests/visits/test_visit_lifecycle.py`

**Interfaces:**
- Produces: check-in, assign, start-demo, record-outcome and close commands.

- [ ] Test anonymous visit, returning customer, reassignment, silent-exit timeout and service-only visit.
- [ ] Require an outcome or explicit unknown/silent-exit reason.
- [ ] Build fast keyboard/touch check-in under 20 seconds.
- [ ] Commit.

### Task 3: Implement product catalog and read-only inventory snapshots

**Files:**
- Create: `services/core/app/modules/products/models.py`
- Create: `services/core/app/modules/products/service.py`
- Create: `services/core/app/modules/products/inventory_adapter.py`
- Create: `apps/desktop/src/features/products/ProductComparison.tsx`
- Test: `services/core/tests/products/test_snapshot_freshness.py`

**Interfaces:**
- Produces: product facts, approved benefits, inventory snapshot and freshness.

- [ ] Test stale inventory, missing cost, duplicate SKU and discontinued product.
- [ ] Separate immutable source snapshot from user-facing aggregate.
- [ ] Hide exact cost/margin from unauthorized roles.
- [ ] Build accessible comparison table with maximum three default columns.
- [ ] Commit.

### Task 4: Build Lost-Sale Intelligence

**Files:**
- Create: `services/core/app/modules/lost_sales/models.py`
- Create: `services/core/app/modules/lost_sales/service.py`
- Create: `apps/desktop/src/features/lost-sales/LostSaleCapture.tsx`
- Create: `apps/desktop/src/features/lost-sales/LostSaleInsights.tsx`
- Test: `services/core/tests/lost_sales/test_capture.py`

**Interfaces:**
- Produces: immutable lost-sale event and weekly reason aggregates.

- [ ] Test mandatory reason, stock-related loss, price objection, staff-pitch issue and recoverable follow-up.
- [ ] Make capture possible in under 30 seconds.
- [ ] Display denominators and unknowns.
- [ ] Prevent manager from changing reason without correction event.
- [ ] Commit.

### Task 5: Implement rules-first Intelligent Sales Workspace

**Files:**
- Create: `services/core/app/modules/sales_workspace/rules.py`
- Create: `services/core/app/modules/sales_workspace/service.py`
- Create: `apps/desktop/src/features/sales/SalesWorkspace.tsx`
- Test: `services/core/tests/sales_workspace/test_recommendations.py`

**Interfaces:**
- Produces: `SalesRecommendationV1`.

- [ ] Test budget, stated need, stock, trust entitlement, installment and alternative product rules.
- [ ] Exclude stale/missing-stock products.
- [ ] Limit default comparison to three options and show why each fits.
- [ ] Display uncertainty and ask staff to confirm key needs.
- [ ] Log whether recommendation was used and outcome.
- [ ] Commit.

### Task 6: Implement bundles and accessory intelligence

**Files:**
- Create: `services/core/app/modules/bundles/models.py`
- Create: `services/core/app/modules/bundles/service.py`
- Create: `apps/desktop/src/features/bundles/BundlePresenter.tsx`
- Test: `services/core/tests/bundles/test_eligibility.py`

**Interfaces:**
- Produces: eligible protection, productivity, gaming, travel, premium, family and essentials bundles.

- [ ] Test product compatibility, customer relevance, stock and minimum contribution boundary.
- [ ] Record presented/accepted/rejected plus reason.
- [ ] Never pressure staff to present an incompatible or unavailable item.
- [ ] Commit.

### Task 7: Implement Trust Premium and Loyalty OS

**Files:**
- Create: `services/core/app/modules/loyalty/models.py`
- Create: `services/core/app/modules/loyalty/service.py`
- Create: `apps/desktop/src/features/loyalty/BenefitWallet.tsx`
- Create: `apps/desktop/src/features/loyalty/EntitlementAdmin.tsx`
- Test: `services/core/tests/loyalty/test_entitlements.py`

**Interfaces:**
- Produces: eligibility, issuance, redemption, expiry and cost events.

- [ ] Encode Perpetual Cover, No-Regret Swap and Royal Founders only after owner configuration.
- [ ] Test issuance, double redemption, expiry and owner-required exception.
- [ ] Show customer-friendly value without exposing internal reserve/cost.
- [ ] Commit.

### Task 8: Implement installment opportunity workflow

**Files:**
- Create: `services/core/app/modules/installments/models.py`
- Create: `services/core/app/modules/installments/service.py`
- Create: `apps/desktop/src/features/installments/InstallmentGuide.tsx`
- Test: `services/core/tests/installments/test_workflow.py`

**Interfaces:**
- Produces: candidate, document checklist, application status and drop-off reason.

- [ ] Test eligibility “unknown”, document missing, application abandoned and approved outcome.
- [ ] Never make a lending/credit decision.
- [ ] Show source/provider for every eligibility rule.
- [ ] Link successful customer to future relationship workflow.
- [ ] Commit.

### Task 9: Implement Product Launch War Room

**Files:**
- Create: `services/core/app/modules/launches/models.py`
- Create: `services/core/app/modules/launches/service.py`
- Create: `apps/desktop/src/features/launches/LaunchWarRoom.tsx`
- Test: `services/core/tests/launches/test_launch_stages.py`

**Interfaces:**
- Produces: pre-launch, live and post-launch stage aggregates.

- [ ] Test waitlist, staff certification, demo readiness, stock allocation and post-launch review.
- [ ] Build timeline UI with stage gates.
- [ ] Show unresolved preparation as risks before launch.
- [ ] Commit.

### Task 10: Implement Evidence-Based SOP Engine

**Files:**
- Create: `services/core/app/modules/sops/models.py`
- Create: `services/core/app/modules/sops/service.py`
- Create: `services/core/app/modules/sops/evidence_rules.py`
- Create: `apps/desktop/src/features/sops/SopRunner.tsx`
- Create: `apps/desktop/src/features/sops/SopReview.tsx`
- Test: `services/core/tests/sops/test_evidence.py`

**Interfaces:**
- Produces: scheduled SOP run, step evidence, pass/fail, reopen and coaching event.

- [ ] Test photo/document requirement, invalid proof, random manager sample and repeat failure.
- [ ] Prevent checklist-only completion where evidence is required.
- [ ] Build mobile/touch-friendly step runner.
- [ ] Commit.

### Task 11: Implement Employee Capability and micro-coaching

**Files:**
- Create: `services/core/app/modules/capability/models.py`
- Create: `services/core/app/modules/capability/service.py`
- Create: `apps/desktop/src/features/capability/TodayLesson.tsx`
- Create: `apps/desktop/src/features/capability/ManagerCoachingView.tsx`
- Test: `services/core/tests/capability/test_fair_measurement.py`

**Interfaces:**
- Produces: competency, certification, coaching action and progress event.

- [ ] Test that opportunity-normalized metrics do not punish low footfall.
- [ ] Generate one product lesson, one objection scenario and one practical action.
- [ ] Restrict private coaching details to employee, manager and owner.
- [ ] No automatic salary/discipline action.
- [ ] Commit.

### Task 12: Implement Institutional Knowledge Library

**Files:**
- Create: `services/core/app/modules/knowledge/models.py`
- Create: `services/core/app/modules/knowledge/service.py`
- Create: `services/core/app/modules/knowledge/search.py`
- Create: `apps/desktop/src/features/knowledge/KnowledgeLibrary.tsx`
- Test: `services/core/tests/knowledge/test_publication.py`

**Interfaces:**
- Produces: draft, review, publish, supersede and search.

- [ ] Test draft conversation note cannot appear as approved knowledge.
- [ ] Add source evidence and responsible approver.
- [ ] Use PostgreSQL full-text first; add embeddings only for approved content.
- [ ] Show current/superseded status.
- [ ] Commit.

### Task 13: Build Business Core owner analytics

**Files:**
- Create: `services/core/app/modules/growth_metrics/service.py`
- Create: `apps/desktop/src/features/growth/GrowthOverview.tsx`
- Create: `apps/desktop/src/features/growth/TopDealerScore.tsx`
- Test: `services/core/tests/growth_metrics/test_denominators.py`

**Interfaces:**
- Produces: visit funnel, lost-sale reasons, accessory contribution, retention and internal Top Dealer Score components.

- [ ] Test explicit denominators, normalized units and missing data.
- [ ] Keep Top Dealer Score directional and decomposable.
- [ ] Do not label it an official brand/dealer ranking.
- [ ] Add methodology drawer.
- [ ] Commit.

### Task 14: Run complete store-journey acceptance

**Files:**
- Create: `tests/acceptance/test_phase_3_customer_journey.py`
- Create: `apps/desktop/tests/customer-journey.spec.ts`
- Create: `docs/runbooks/customer-data-correction.md`

**Interfaces:**
- Produces: release gate evidence.

- [ ] Simulate new anonymous visit, returning VIP, sale, lost sale, installment lead and complaint.
- [ ] Verify role redaction and correction events.
- [ ] Complete SOP with invalid then valid evidence.
- [ ] Verify recommendation source/freshness.
- [ ] Disable all AI workers and repeat customer, product, lost-sale, bundle, loyalty, installment, SOP and knowledge-library journeys.
- [ ] Run the optional semantic candidate against the frozen retrieval set; keep it disabled unless it improves top-5 recall by `>= 10%` without adding more than 200 ms p95 query latency.
- [ ] Run all regression tests.
- [ ] Commit and tag `v0.3.0-customer-execution`.

---

## 5. Phase 3 acceptance gate

- Every meaningful visit ends with an auditable outcome or explicit unknown.
- Lost sales remain visible and drive weekly insights.
- No unavailable/stale product is confidently recommended.
- Staff can run the common visit workflow without owner intervention.
- Entitlements cannot be double redeemed.
- SOPs requiring evidence cannot close via checkbox alone.
- Employee analytics expose opportunity context.
- Knowledge requires responsible approval.
- Full-text retrieval and all store journeys work with no model loaded.
- Optional vector retrieval stays off unless it passes the exact-PC quality and latency gate.
- No external message or financial write exists.
- Owner accepts the visual customer and growth workspaces.
