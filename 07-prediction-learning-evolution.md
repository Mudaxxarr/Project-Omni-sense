# Phase 7 — Prediction, Decision Calibration and Governed Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add scientifically defensible probabilistic forecasting, immutable prediction accountability, advanced evidence grading, causal impact reporting, priority learning and a governed Champion/Challenger evolution pipeline.

**Architecture:** Models remain inside the fully local Intelligence Plane and initially operate in shadow mode. Predictions are sealed before outcomes exist, scored later against observable ground truth and never directly connected to the Execution Gateway. Training, tuning and inference are serialized through Resource Governor leases so the Core Business Lane is never starved.

**Tech Stack:** Existing stack plus CPU scikit-learn, one of XGBoost or LightGBM after benchmark, MAPIE/conformal tooling, PostgreSQL model metadata, signed filesystem artifacts, Polars, lightweight custom drift metrics, time-boxed Optuna in sandbox, Jupyter for offline analysis only and native Windows workers. No always-on MLflow server or cloud training service.

**Governing Runtime Design:** `docs/superpowers/specs/2026-07-29-local-cpu-runtime-design.md` applies to every task and acceptance gate.

## Global Constraints

- Never claim 100% accuracy, guaranteed profit or zero downside.
- Chronological splits only; random time-series leakage is prohibited.
- Always compare against a frozen simple baseline.
- Numerical ranges report empirical coverage; event probabilities report calibration.
- Counterfactual outcomes are labelled unobservable.
- No model may use future data relative to prediction time.
- No model can directly call the Execution Gateway.
- Model/prompt/weight/config production deployment always requires human-reviewed signed release.
- Safety rules, financial limits and authority caps are not tunable by AI.
- Treasury remains view-only and separately reviewed.
- Training/inference uses local data and local CPU only.
- One model-training/tuning/inference heavy lease exists at a time.
- Tuning is limited to 20 trials or 60 minutes, whichever occurs first.
- Phase 7 must remain removable without affecting Phase 1–3 business operations.

---

## 1. Phase outcome

```text
PREDICTION REGISTER

Demand: Oppo A78 • Next 14 days
Expected range        12–20 units
Empirical coverage    87% on 214 unseen forecasts
Baseline range        8–24 units
Data freshness        19 minutes
Out-of-distribution   No

Expected contribution scenario    18k–31k PKR
Maximum credible downside          42k PKR

Status: SHADOW — CANNOT EXECUTE
[VIEW EVIDENCE SNAPSHOT] [VIEW MODEL CARD]
```

Evolution report:

```text
CHAMPION v1.4          CHALLENGER v1.5
Coverage 88%           90%
Interval width 11.2    9.6
Shock loss 41k         38k

Blind holdout: PASS
Shadow: 30/60 days

[CONTINUE SHADOW] [REJECT] [REQUEST RELEASE REVIEW]
```

---

## 2. Model governance contracts

### 2.1 Model card

```python
class ModelCardV1(BaseModel):
    model_id: UUID
    name: str
    version: str
    target: str
    training_cutoff: datetime
    features: list[str]
    excluded_features: list[str]
    baseline: str
    metrics: dict[str, float]
    known_failures: list[str]
    approved_use: list[str]
    prohibited_use: list[str]
    artifact_sha256: str
    status: Literal["candidate", "shadow", "champion", "retired"]
```

### 2.2 Sealed prediction

```python
class SealedPredictionV1(BaseModel):
    prediction_id: UUID
    created_at: datetime
    horizon_end: datetime
    target: str
    model_id: UUID
    evidence_snapshot_hash: str
    feature_cutoff: datetime
    probability: float | None
    interval_low: float | None
    interval_high: float | None
    assumptions: list[str]
    invalidating_conditions: list[str]
    review_at: datetime
    previous_hash: str
    current_hash: str
```

---

## 3. Tasks

### Task 1: Enhance Truth and Evidence Kernel

**Files:**
- Create: `services/core/app/modules/truth_kernel/scoring.py`
- Create: `services/core/app/modules/truth_kernel/conflicts.py`
- Create: `services/core/app/modules/truth_kernel/correlation.py`
- Create: `apps/desktop/src/features/truth/TruthDrawer.tsx`
- Test: `services/core/tests/truth_kernel/test_grades.py`

**Interfaces:**
- Produces: A/B/C/D grade, freshness, independence and conflict set.

- [ ] Test authoritative record, authenticated human evidence, weak single claim, echo repost and stale contradiction.
- [ ] Keep evidence grade explainable; no “snake” label.
- [ ] Require conflict display instead of silent weighted average.
- [ ] Commit.

### Task 2: Implement immutable Prediction Register

**Files:**
- Create: `services/core/app/modules/predictions/models.py`
- Create: `services/core/app/modules/predictions/service.py`
- Create: `services/core/app/modules/predictions/hash_chain.py`
- Create: `apps/desktop/src/features/predictions/PredictionRegister.tsx`
- Test: `services/core/tests/predictions/test_sealing.py`

**Interfaces:**
- Produces: seal, list, review-due and append-outcome commands.

- [ ] Test editing prediction fields after seal is impossible.
- [ ] Include previous/current hash and evidence snapshot.
- [ ] Use server monotonic/UTC checks; mark unsynchronized time.
- [ ] A chain break raises an audit incident but does not stop unrelated POS/business work.
- [ ] Commit.

### Task 3: Create leakage-safe feature pipeline

**Files:**
- Create: `models/demand/features.py`
- Create: `models/demand/dataset.py`
- Create: `models/demand/splits.py`
- Test: `models/tests/test_no_lookahead.py`

**Interfaces:**
- Produces: chronological training, calibration and untouched test sets.

- [ ] Build fixture with a deliberately leaked future column.
- [ ] Assert feature pipeline rejects timestamps after prediction cutoff.
- [ ] Include source freshness and missingness indicators.
- [ ] Store dataset manifest/hash.
- [ ] Commit.

### Task 4: Build simple frozen baselines

**Files:**
- Create: `models/baselines/moving_average.py`
- Create: `models/baselines/seasonal_naive.py`
- Create: `models/evaluation/metrics.py`
- Test: `models/tests/test_baselines.py`

**Interfaces:**
- Produces: 30-day moving average and seasonal-naive ranges.

- [ ] Test numerical forecast metrics: MAE, pinball loss, interval coverage and width.
- [ ] Test event metrics: Brier Score and ECE.
- [ ] Freeze baseline definition before candidate model evaluation.
- [ ] Commit.

### Task 5: Implement probabilistic demand candidate

**Files:**
- Create: `models/demand/train.py`
- Create: `models/demand/predict.py`
- Create: `models/demand/model_card.py`
- Test: `models/tests/test_demand_intervals.py`

**Interfaces:**
- Produces: quantile/conformal interval and model card.

- [ ] Start with gradient-boosted quantile regression; do not begin with deep learning.
- [ ] Calibrate interval on chronological calibration set.
- [ ] Test empirical coverage and outlier behavior.
- [ ] For numerical demand forecasts, require pinball loss at least `10%` lower than the stronger frozen baseline and empirical `90%` interval coverage between `85%` and `95%`.
- [ ] For event forecasts, require Brier Score at least `10%` lower than the stronger frozen baseline and `ECE < 0.10`.
- [ ] Reject any candidate that worsens the preregistered critical-harm metric or rare-event stress result even when its average metric improves.
- [ ] Commit.

### Task 6: Implement outcome scorer and calibration dashboard

**Files:**
- Create: `services/core/app/modules/predictions/outcomes.py`
- Create: `services/core/app/modules/predictions/calibration.py`
- Create: `apps/desktop/src/features/predictions/CalibrationDashboard.tsx`
- Test: `services/core/tests/predictions/test_outcomes.py`

**Interfaces:**
- Produces: prediction score after horizon and minimum sample-aware aggregate.

- [ ] Test realized, invalidated and counterfactual-unobservable cases.
- [ ] Do not score unpurchased inventory as realized profit/loss.
- [ ] Display calibration only after minimum count.
- [ ] Show interval width as well as coverage.
- [ ] Commit.

### Task 7: Implement out-of-distribution and drift controls

**Files:**
- Create: `models/monitoring/drift.py`
- Create: `models/monitoring/ood.py`
- Create: `services/core/app/modules/model_health/service.py`
- Test: `models/tests/test_drift_actions.py`

**Interfaces:**
- Produces: healthy, warning, shadow-only or disabled recommendation.

- [ ] Test price shock, missing source, new product and changed customer mix.
- [ ] Define drift thresholds before observing production outcomes.
- [ ] Demote affected model to shadow/recommendation-disabled state.
- [ ] Never retrain and deploy automatically.
- [ ] Commit.

### Task 8: Build Apex Triad v2 with learned ranking under hard overrides

**Files:**
- Modify: `services/core/app/modules/briefing/ranking.py`
- Create: `services/core/app/modules/briefing/feedback.py`
- Modify: `apps/desktop/src/features/briefing/ApexTriad.tsx`
- Test: `services/core/tests/briefing/test_rank_zero.py`

**Interfaces:**
- Produces: learned ranking adjustment bounded by deterministic Rank 0 and authority rules.

- [ ] Test low-value urgency trap and high-downside long-horizon item.
- [ ] Use owner actions as preference feedback, not objective truth.
- [ ] Cap learned weights.
- [ ] Keep all-signals archive.
- [ ] Commit.

### Task 9: Implement Benefit Ledger with causal grades

**Files:**
- Create: `services/core/app/modules/benefit_ledger/models.py`
- Create: `services/core/app/modules/benefit_ledger/service.py`
- Create: `services/core/app/modules/benefit_ledger/dedup.py`
- Create: `apps/desktop/src/features/benefit/BenefitLedger.tsx`
- Test: `services/core/tests/benefit_ledger/test_no_double_count.py`

**Interfaces:**
- Produces: Grade A measured, B estimated, C directional and D hypothesis value.

- [ ] Test one campaign credited through multiple modules and prevent double count.
- [ ] Include negative failure/time costs.
- [ ] Keep avoided-loss counterfactual outside realized total unless robustly estimated.
- [ ] Display intervals and method.
- [ ] Commit.

### Task 10: Implement Champion/Challenger sandbox

**Files:**
- Create: `models/forge/candidate.py`
- Create: `models/forge/blind_judge.py`
- Create: `models/forge/shadow.py`
- Create: `apps/desktop/src/features/evolution/ChallengerReview.tsx`
- Test: `models/tests/test_blind_holdout.py`

**Interfaces:**
- Produces: candidate report and shadow prediction stream.

- [ ] Lock holdout access away from optimizer.
- [ ] Test overfit candidate passes train but fails blind holdout.
- [ ] Compare critical harm metrics, not accuracy alone.
- [ ] Acquire a Green heavy lease before training/tuning; checkpoint and yield if the Core requests priority.
- [ ] Limit optimization to 20 trials or 60 minutes and store CPU time, peak RAM and model size in the candidate report.
- [ ] Enforce an 8 GB worker hard ceiling and Below Normal process priority.
- [ ] Require shadow duration and sample count.
- [ ] Commit.

### Task 11: Enforce signed human deployment and rollback

**Files:**
- Create: `models/registry/signing.py`
- Create: `models/registry/filesystem_store.py`
- Create: `services/core/app/modules/model_registry/service.py`
- Create: `infra/scripts/promote-model.ps1`
- Create: `infra/scripts/rollback-model.ps1`
- Test: `tests/security/test_model_artifact_signing.py`

**Interfaces:**
- Produces: signed champion artifact and immutable promotion record.

- [ ] Test altered artifact, unsigned candidate and safety-policy change.
- [ ] Store model binaries on `C:` within the shared 15 GB model quota; metadata and hashes remain in PostgreSQL.
- [ ] Reject promotion when total model quota would exceed 15 GB or `C:` free space is below 30 GB.
- [ ] Require developer review plus owner approval for business behavior promotion.
- [ ] Rollback only to signed known-good artifact on technical health failure.
- [ ] Prevent model pipeline from editing `.py`, `.sql` or policy files.
- [ ] Commit.

### Task 12: Implement Treasury Advisory Laboratory

**Files:**
- Create: `services/core/app/modules/treasury_advisory/models.py`
- Create: `services/core/app/modules/treasury_advisory/scenarios.py`
- Create: `apps/desktop/src/features/treasury/TreasuryAdvisory.tsx`
- Test: `services/core/tests/treasury_advisory/test_boundaries.py`

**Interfaces:**
- Produces: owner-specified scenario comparison; no broker/bank action.

- [ ] Test operating cash cannot be silently classified as surplus.
- [ ] Require owner-confirmed liabilities/horizon.
- [ ] Show fees, tax, liquidity and downside inputs.
- [ ] Architectural test verifies no execution credentials/provider methods.
- [ ] Display current-regulation review date.
- [ ] Commit.

### Task 13: Run crisis, poisoning and calibration acceptance

**Files:**
- Create: `tests/acceptance/test_phase_7_models.py`
- Create: `models/evaluation/crisis_scenarios.py`
- Create: `docs/runbooks/model-drift.md`
- Create: `docs/runbooks/prediction-register-chain-break.md`

- [ ] Inject missing records, poisoned sales spike, price shock and unseen product.
- [ ] Verify forecasts disable or widen uncertainty rather than fake confidence.
- [ ] Run the suite in Green, Yellow, Orange and Red states; only frozen lightweight inference may run outside Green and all core workflows must remain responsive.
- [ ] Verify combined AI CPU remains at or below 60% and Core API p95 stays `<= 500 ms`.
- [ ] Verify training worker peak RAM `<= 8 GB`, optimizer stops at 20 trials/60 minutes and model artifacts stay within 15 GB.
- [ ] Verify model cannot execute externally.
- [ ] Verify original sealed prediction remains unchanged.
- [ ] Verify overfit challenger is rejected.
- [ ] Commit and tag `v0.7.0-governed-intelligence`.

---

## 4. Phase 7 acceptance gate

- Prediction Register is append-only and evidence-sealed.
- No look-ahead leakage in automated tests.
- Candidate beats frozen baseline on preregistered unseen test.
- Coverage and interval width both meet gates.
- OOD/drift disables unsafe use.
- Benefit Ledger separates measured, estimated and directional claims.
- AI cannot deploy prompt/model/weight/policy.
- Signed rollback works without data destruction.
- Model registry uses PostgreSQL plus signed local files; no always-on MLflow/cloud service is required.
- Training/tuning respects single-heavy-lease, CPU, time, RAM and disk quotas.
- Core API p95 remains `<= 500 ms` during the mixed-load model test.
- Treasury is advisory-only and has no execution credential.
- No forecast or AI score directly calls the Gateway.
