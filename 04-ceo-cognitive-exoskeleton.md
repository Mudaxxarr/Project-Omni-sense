# Phase 4 — CEO Cognitive Exoskeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the private CEO experience that restores mental context, protects attention, challenges thinking, strengthens decisions, preserves ideas and closes the owner’s day cleanly.

**Architecture:** Add a `cognitive` bounded module accessible only to owner-authorized identities and a separate interruptible Deep Analyst worker. Use event-sourced records for thoughts, decisions, assumptions and reviews; use retrieval over owner-approved memory, never unrestricted surveillance. All reasoning remains local and the Core Business Lane continues when the model is unloaded.

**Tech Stack:** Existing stack plus PostgreSQL full-text retrieval, optional benchmarked `pgvector`, a local `llama.cpp`-class GGUF runtime, quantized multilingual 3B–4B Deep Analyst candidates, local embeddings, JSON-schema-constrained generation and native background workers. Cloud-model providers are excluded.

**Governing Runtime Design:** `docs/superpowers/specs/2026-07-29-local-cpu-runtime-design.md` applies to every task and acceptance gate.

## Global Constraints

- Owner Cognitive records are `RESTRICTED_OWNER`.
- Staff/developers cannot read private cognitive content by default.
- AI must distinguish facts, assumptions, interpretations and simulations.
- No cognitive feature sends messages or performs external actions.
- No mood inference from camera.
- Thought capture is push-to-record or explicit owner text in this phase.
- No owner memory, prompt or generated reasoning is sent to a cloud model.
- Deep Analyst runs only with a Resource Governor Green lease and exactly one heavy job.
- Rules/full-text retrieval remain usable when the model is queued or unavailable.
- A 7B candidate is overnight-only and may ship only after exact-PC benchmark approval.
- Every generated recommendation links to source memory and model/prompt version.
- Multi-agent agreement is not independent proof.
- Overnight work is analysis/drafting only.

---

## 1. Phase outcome

The intended daily experience:

```text
ASSALAM-O-ALAIKUM, MUDASSAR

You left yesterday with one unfinished strategic thought:
“Discount ke bajaye certainty sell karni chahiye.”

Since then:
• One related lost-sale pattern strengthened.
• Junaid’s promised response is overdue.
• Today’s first meeting is in 42 minutes.

[RESTORE WORKSPACE] [90-SECOND BRIEFING] [CHOOSE MODE]
```

At departure:

```text
EVERYTHING IMPORTANT IS RECORDED

Decided        3
Unresolved     2
Promises       4
Tomorrow start “Finalize premium bundle experiment”

[SEAL DAY]
```

---

## 2. Visual architecture

### 2.1 Four spaces

```text
NOW       Current reality, priorities, re-entry and approvals
THINK     Decisions, contradictions, simulations and creative work
PEOPLE    Meetings, promises, relationships and delegation
MEMORY    Thoughts, decisions, patterns and approved knowledge
```

### 2.2 Think space

```text
┌────────────────────────── DECISION CHAMBER ─────────────────────────────────┐
│ DECISION: Launch “Waiting-Time Value Experience” next month?                │
├──────────────────┬──────────────────┬────────────────────────────────────────┤
│ VERIFIED FACTS   │ ASSUMPTIONS      │ UNKNOWNS                               │
│ 18 wait cases    │ Customers value  │ Staff capacity                         │
│ 31% abandon      │ free setup       │ Competitor response                    │
├──────────────────┴──────────────────┴────────────────────────────────────────┤
│ OPTION B IS STRONGEST IF ASSUMPTION A IS VERIFIED BY THURSDAY               │
│ Maximum credible downside: staff congestion + 35k campaign/setup cost        │
│ [RUN PRE-MORTEM] [SAVE DECISION] [REQUEST EVIDENCE]                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Writing tone

- Direct, calm and evidence-aware.
- No theatrical “absolute domination” language in operational UI.
- Use Roman Urdu naturally where it increases speed.
- Never shame the owner for contradiction; ask whether context changed.

---

## 3. Cognitive contracts

### 3.1 Thought

```python
class ThoughtV1(BaseModel):
    thought_id: UUID
    owner_id: UUID
    captured_at: datetime
    raw_text: str
    observation: str | None
    hypothesis: str | None
    question: str | None
    experiment_candidate: str | None
    evidence_needed: list[str]
    related_record_ids: list[UUID]
    publication_status: Literal["private", "approved_memory", "discarded"]
```

### 3.2 Decision

```python
class DecisionV1(BaseModel):
    decision_id: UUID
    objective: str
    facts: list[ClaimRef]
    assumptions: list[Assumption]
    unknowns: list[str]
    options: list[DecisionOption]
    selected_option_id: UUID | None
    expected_outcome: str | None
    confidence: float | None
    maximum_credible_downside: str
    reversibility: int
    review_conditions: list[str]
    review_at: datetime
```

### 3.3 Memory retrieval result

```python
class MemoryHitV1(BaseModel):
    record_id: UUID
    record_type: str
    excerpt: str
    occurred_at: datetime
    similarity: float
    source_event_ids: list[UUID]
    access_reason: str
```

---

## 4. Tasks

### Task 1: Implement owner memory vault and retrieval policy

**Files:**
- Create: `services/core/app/modules/cognitive/memory/models.py`
- Create: `services/core/app/modules/cognitive/memory/service.py`
- Create: `services/core/app/modules/cognitive/memory/retrieval.py`
- Test: `services/core/tests/cognitive/test_memory_access.py`

**Interfaces:**
- Produces: `store_private_memory`, `publish_memory`, `search_owner_memory`.

- [ ] Test owner-only access, discarded thought exclusion and source-link requirement.
- [ ] Store embeddings only for owner-approved memory.
- [ ] Implement PostgreSQL full-text retrieval as the frozen baseline.
- [ ] Filter by classification before full-text or optional vector similarity.
- [ ] Keep `pgvector` disabled unless it improves top-5 recall by `>= 10%` without adding more than 200 ms p95 latency.
- [ ] Log retrieval reason without exposing content to unauthorized audit viewers.
- [ ] Commit.

### Task 2: Build local Deep Analyst runtime and structured-output boundary

**Files:**
- Create: `services/core/app/modules/ai/runtime/base.py`
- Create: `services/core/app/modules/ai/runtime/local_gguf.py`
- Create: `services/core/app/modules/ai/runtime/model_manifest.py`
- Create: `services/deep-analyst/app/worker.py`
- Create: `services/deep-analyst/app/resource_lease.py`
- Create: `services/core/app/modules/ai/redaction.py`
- Test: `services/core/tests/ai/test_structured_output.py`
- Test: `services/deep-analyst/tests/test_resource_lease.py`

**Interfaces:**
- Produces: `queue_local_generation(schema, messages, policy) -> AIJobId` and `LocalGenerationResult`.

- [ ] Test invalid JSON, missing citations, prompt injection text, model-load failure, cancellation and worker timeout.
- [ ] Test that Deep Analyst cannot acquire a lease below 16 GB available physical RAM or while another heavy lease exists.
- [ ] Treat retrieved content as quoted untrusted data.
- [ ] Keep redaction for least-privilege prompt construction even though inference is local.
- [ ] Persist local runtime, model hash, quantization, prompt and schema versions.
- [ ] Terminate the worker above its 8 GB hard ceiling, requeue once and then require manual review.
- [ ] Fail closed to a manual/rules/full-text workflow without creating a cloud fallback.
- [ ] Show why a job is queued, current compute state, cancel and run-later controls.
- [ ] Commit.

### Task 3: Implement Cognitive Mode Selector

**Files:**
- Create: `services/core/app/modules/cognitive/modes/service.py`
- Create: `apps/desktop/src/features/cognitive/ModeSelector.tsx`
- Create: `apps/desktop/src/features/cognitive/modeStore.ts`
- Test: `apps/desktop/tests/mode-selector.test.tsx`

**Interfaces:**
- Produces: commander, creator, deep_work, people and recovery modes.

- [ ] Test mode-specific notification density and navigation emphasis.
- [ ] Persist mode per session, not as a psychological profile.
- [ ] Add quick keyboard switching and reduced-motion behavior.
- [ ] Commit.

### Task 4: Expand Re-Entry and Interruption Recovery

**Files:**
- Modify: `services/core/app/modules/cognitive/reentry/service.py`
- Create: `services/core/app/modules/cognitive/reentry/workspace_adapter.py`
- Create: `apps/desktop/src/features/reentry/InterruptionCapsule.tsx`
- Test: `services/core/tests/cognitive/test_interruption_capsule.py`

**Interfaces:**
- Produces: explicit save/restore for OMNISCIENCE routes, documents and owner notes.

- [ ] Test restricted-app exclusion and expired workspace state.
- [ ] Capture active OMNISCIENCE context and whitelisted document URI only.
- [ ] Never record password/OTP fields or global keystrokes.
- [ ] Restore one click with a preview of what will reopen.
- [ ] Commit.

### Task 5: Implement Thought Capture and Thought Extension

**Files:**
- Create: `services/core/app/modules/cognitive/thoughts/service.py`
- Create: `services/core/app/modules/cognitive/thoughts/parser.py`
- Create: `apps/desktop/src/features/thoughts/ThoughtCapture.tsx`
- Create: `apps/desktop/src/features/thoughts/ThoughtWorkbench.tsx`
- Test: `services/core/tests/cognitive/test_thought_parser.py`

**Interfaces:**
- Produces: `ThoughtV1` and challenge prompts.

- [ ] Test fragmented Roman Urdu, observation versus hypothesis and evidence-needed extraction.
- [ ] Keep raw owner text and generated structure visibly separate.
- [ ] Add “wrong interpretation” correction.
- [ ] Offer strongest version, hidden assumption, opposite and moat questions.
- [ ] Commit.

### Task 6: Implement Reality-versus-Story and Contradiction Engine

**Files:**
- Create: `services/core/app/modules/cognitive/claims/models.py`
- Create: `services/core/app/modules/cognitive/claims/service.py`
- Create: `services/core/app/modules/cognitive/contradictions/service.py`
- Create: `apps/desktop/src/features/cognitive/ContradictionCard.tsx`
- Test: `services/core/tests/cognitive/test_contradictions.py`

**Interfaces:**
- Produces: fact, assumption, interpretation, fear, prediction and anecdote classifications plus source pairs.

- [ ] Test changed context versus true conflict.
- [ ] Require both conflicting source excerpts.
- [ ] Phrase output as a question, not an accusation.
- [ ] Allow owner to mark “circumstances changed” with reason.
- [ ] Commit.

### Task 7: Implement Decision Chamber

**Files:**
- Create: `services/core/app/modules/cognitive/decisions/models.py`
- Create: `services/core/app/modules/cognitive/decisions/service.py`
- Create: `services/core/app/modules/cognitive/decisions/perspectives.py`
- Create: `apps/desktop/src/features/decisions/DecisionChamber.tsx`
- Test: `services/core/tests/cognitive/test_decision_chamber.py`

**Interfaces:**
- Produces: `DecisionV1`, option comparison and conditional recommendation.

- [ ] Test incomplete facts, irreversible option, maximum downside and review-condition requirement.
- [ ] Generate financial, customer, operational, brand and future-scale perspectives independently before synthesis.
- [ ] Label all perspective output as analysis.
- [ ] Block save until review date and downside exist.
- [ ] Commit.

### Task 8: Implement Pre-Mortem and Future-Self simulations

**Files:**
- Create: `services/core/app/modules/cognitive/simulations/service.py`
- Create: `apps/desktop/src/features/decisions/PreMortemPanel.tsx`
- Create: `apps/desktop/src/features/decisions/FutureSelfCouncil.tsx`
- Test: `services/core/tests/cognitive/test_simulation_labels.py`

**Interfaces:**
- Produces: failure causes, early indicators, controls and perspective narratives.

- [ ] Test every output carries `SIMULATION — NOT PREDICTION`.
- [ ] Require explicit assumptions.
- [ ] Convert failure causes into optional tasks only after owner selection.
- [ ] Commit.

### Task 9: Implement Decision Journal and calibration review

**Files:**
- Create: `services/core/app/modules/cognitive/decisions/review.py`
- Create: `apps/desktop/src/features/decisions/DecisionJournal.tsx`
- Create: `apps/desktop/src/features/decisions/CalibrationView.tsx`
- Test: `services/core/tests/cognitive/test_decision_review.py`

**Interfaces:**
- Produces: append-only outcome review and calibration aggregates.

- [ ] Test original confidence cannot be edited at review.
- [ ] Record actual, variance, failed assumption and lesson.
- [ ] Separate owner confidence calibration from business outcome value.
- [ ] Require minimum sample count before showing a trend.
- [ ] Commit.

### Task 10: Build Meeting Pre-Brief and People workspace

**Files:**
- Create: `services/core/app/modules/cognitive/meetings/prebrief.py`
- Create: `apps/desktop/src/features/people/PeopleWorkspace.tsx`
- Create: `apps/desktop/src/features/meetings/MeetingPrebrief.tsx`
- Test: `services/core/tests/cognitive/test_meeting_prebrief.py`

**Interfaces:**
- Consumes: approved customer/party relationships and Promise Graph.
- Produces: meeting purpose, history, questions, sensitivities and desired outcome.

- [ ] Test permission filtering and unresolved promise inclusion.
- [ ] Provide source links for sensitive facts.
- [ ] Avoid exposing unrelated private customer data.
- [ ] Commit.

### Task 11: Implement Creativity Collider, Opportunity Archaeologist and Pattern Memory

**Files:**
- Create: `services/core/app/modules/cognitive/creativity/service.py`
- Create: `services/core/app/modules/cognitive/patterns/service.py`
- Create: `apps/desktop/src/features/cognitive/CreativityCollider.tsx`
- Create: `apps/desktop/src/features/cognitive/PatternMemory.tsx`
- Test: `services/core/tests/cognitive/test_pattern_retrieval.py`

**Interfaces:**
- Produces: grounded idea combinations and prior-case comparisons.

- [ ] Require each creative input to reference a real record.
- [ ] Test an old rejected idea reappears only when blocking condition changes.
- [ ] Show what is similar and different in pattern retrieval.
- [ ] Allow dismissal without training a global negative bias.
- [ ] Commit.

### Task 12: Implement Private Rehearsal and Relationship Compass

**Files:**
- Create: `services/core/app/modules/cognitive/rehearsal/service.py`
- Create: `services/core/app/modules/cognitive/relationships/service.py`
- Create: `apps/desktop/src/features/people/RehearsalStudio.tsx`
- Create: `apps/desktop/src/features/people/RelationshipCompass.tsx`
- Test: `services/core/tests/cognitive/test_relationship_signals.py`

**Interfaces:**
- Produces: private rehearsal transcript/feedback and relationship-attention signals.

- [ ] Keep rehearsal completely internal with no send path.
- [ ] Test relationship reminder based on contact pattern and unresolved promise.
- [ ] Do not infer emotion/loyalty from silence alone.
- [ ] Commit.

### Task 13: Implement Nocturnal Sentinel and End-of-Day Memory Seal

**Files:**
- Create: `services/core/app/modules/cognitive/overnight/service.py`
- Create: `services/core/app/modules/cognitive/day_seal/service.py`
- Create: `apps/desktop/src/features/cognitive/EndOfDaySeal.tsx`
- Create: `apps/desktop/src/features/cognitive/NightReplay.tsx`
- Test: `services/core/tests/cognitive/test_zero_external_action.py`

**Interfaces:**
- Produces: analysis-only overnight jobs and next-day briefing inputs.

- [ ] Test that overnight job registry contains no external-action capability.
- [ ] Compile unresolved thoughts, meetings, contradictions and questions.
- [ ] Require Resource Governor Green before model work; otherwise preserve the durable job for the next eligible window.
- [ ] Benchmark a 7B quantized candidate separately and keep it disabled unless a 500-token report completes in `<= 120 seconds` within the 8 GB worker ceiling.
- [ ] Create sealed restart point.
- [ ] Show transparent replay of work performed.
- [ ] Commit.

### Task 14: Phase 4 privacy, visual and acceptance gate

**Files:**
- Create: `tests/acceptance/test_phase_4_cognitive.py`
- Create: `apps/desktop/tests/cognitive-day.spec.ts`
- Create: `docs/runbooks/owner-memory-export-delete.md`

- [ ] Test staff/developer denial of owner records.
- [ ] Test that network isolation does not change local reasoning behavior and no cloud-model credential exists.
- [ ] Test Green/Yellow/Orange/Red admission, single-heavy-job enforcement and rules fallback.
- [ ] Run full arrival → decision → interruption → rehearsal → day-seal journey.
- [ ] Verify simulation labels and source links.
- [ ] Verify overnight zero-action rule.
- [ ] Run visual snapshots for all five cognitive modes.
- [ ] Commit and tag `v0.4.0-cognitive-exoskeleton`.

---

## 5. Phase 4 acceptance gate

- Owner private content is inaccessible to ordinary staff/admin roles.
- Re-Entry restores useful context without unrestricted screen/key capture.
- Contradiction cards expose both sources and non-accusatory wording.
- Decision Chamber cannot save a high-stakes decision without downside and review conditions.
- Simulations cannot be mistaken for predictions.
- Overnight worker has no external action tool.
- A 500-token Deep Analyst report p95 is `<= 120 seconds` in Green state on the target PC.
- Cognitive rules, memory search and manual workflows remain usable in Red state.
- Peak Deep Analyst working set is `<= 8 GB`; a second heavy job cannot start.
- No cloud-model hostname, provider credential or inference code path exists.
- End-of-Day Seal creates a reliable next-day restart point.
- Owner confirms the visual experience feels like a private cognitive operating room, not a chatbot dashboard.
