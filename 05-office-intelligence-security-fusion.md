# Phase 5 — Office Intelligence, Meeting Integrity and Security Fusion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add authorized local meeting transcription, observable behavioral context, declared-zone business-relevance audio detection, selective 72-hour retention and correlation with objective security/business events.

**Architecture:** Office Intelligence runs as separate local Sentinel, ASR and optional vision workers with no external-action credentials. Ambient audio remains in an encrypted memory ring buffer; only policy-qualified clips are written to the evidence vault. Resource Governor serializes ASR, vision and Deep Analyst pressure so the Core Business Lane remains responsive. Behavioral observations never become lie or intent verdicts.

**Tech Stack:** Python, local authenticated IPC, CPU `faster-whisper` using a small multilingual model with `int8` compute, WebRTC VAD, RNNoise/WebRTC audio processing, FFmpeg/Opus, CPU spectral/BIC diarization baseline, optional benchmarked ONNX speaker embeddings, MediaPipe CPU landmarks at 1–2 FPS, PostgreSQL, encrypted local storage, optional OpenVINO/ONNX Intel acceleration, Pytest and curated local evaluation sets. CUDA is not assumed.

**Governing Runtime Design:** `docs/superpowers/specs/2026-07-29-local-cpu-runtime-design.md` applies to every task and acceptance gate.

## Global Constraints

- Activate only after written monitoring policy, declared zones and visible notice are approved.
- Excluded/private zones are technically disabled.
- Do not target voices outside owned premises.
- Irrelevant audio is never written to disk.
- Raw relevant clips expire after 72 hours unless owner preserves with reason and expiry.
- No permanent visitor voiceprint by default.
- No global employee ranking from conversations.
- No `liar`, `dishonest`, `criminal`, `emotion certainty` or hidden-intention output.
- Behavioral signals are within-session deviations and cannot independently raise a high-risk alert.
- Objective event correlation is preferred over language-only suspicion.
- No cloud model receives audio, video, transcript or derived behavioral context.
- ASR and vision require Resource Governor leases; they never run concurrently with Deep Analyst.
- Exactly one ASR job runs at a time and uses bounded rolling chunks.
- The audio storage quota is 10 GB; new capture stops at 15 GB free `C:` space.
- Intel UHD 770 acceleration is disabled until it beats CPU on the same accuracy/stability corpus.
- Automatic disciplinary/customer action is impossible.

---

## 1. Phase rollout

Phase 5 does not begin with always-on monitoring.

1. **Lab fixtures:** staged, consented recordings.
2. **Meeting pilot:** push-to-start meeting mode.
3. **One-zone shadow monitor:** relevance decisions logged without owner alerts.
4. **Owner-reviewed alert pilot:** one declared zone and limited hours.
5. **Controlled production:** only after precision, deletion and policy gates pass.

---

## 2. Visual experience

### 2.1 Live Meeting Copilot

```text
┌──────────────────────── LIVE MEETING • RECORDING ───────────────────────────┐
│ Purpose: Finalize supplier delivery terms       00:18:42      ● LOCAL      │
├─────────────────────────────────────────────────────────────────────────────┤
│ PRIVATE PROMPTS                                                             │
│ • Delivery deadline is still unclear.                                      │
│ • “Seven days” conflicts with the 24 July commitment of “three days.”       │
│ • Ask who owns damage-in-transit risk.                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ COMMITMENTS                                                                  │
│ Supplier: rate valid until 5 PM              OWNER: missing                 │
│ Mudassar: reply after stock check            DUE: today 3 PM               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Conversation Integrity card

```text
REVIEW PRIORITY 76/100

Statement
“Payment kal transfer kar di thi.”

Evidence Conflict        HIGH
• No transaction reference
• Date changed twice

Behavioral Deviation     MODERATE
• Response latency +3.1s from this meeting’s neutral baseline
• Speech tempo changed

Possible explanations
Uncertainty • pressure • incomplete information • possible concealment

DECEPTION NOT ESTABLISHED
[PLAY 42s SOURCE] [ASK VERIFICATION QUESTION]
```

### 2.3 Business relevance inbox

```text
IMPORTANT AUDIO • AUTO-DELETES WITHIN 72 HOURS

HIGH  Possible unrecorded stock movement       01:12     delete in 51h
MED   Coordinated software non-adoption         00:48     delete in 66h
LOW   UI/training complaint                     transcript only

[REVIEW] [DELETE NOW] [PRESERVE WITH REASON]
```

### 2.4 Required language

Use:

- “Review priority.”
- “Evidence conflict.”
- “Behavioral deviation.”
- “Possible operational risk.”
- “Verification required.”

Never use:

- “Lie probability.”
- “Snake detected.”
- “Guilty.”
- “Employee intends theft.”

---

## 3. Data contracts

### 3.1 Monitoring zone

```python
class MonitoringZoneV1(BaseModel):
    zone_id: UUID
    name: str
    purpose: Literal["meeting", "security", "business_relevance"]
    microphone_ids: list[str]
    camera_ids: list[str]
    authorized_hours: list[TimeWindow]
    raw_retention_hours: int = 72
    notice_version: str
    excluded: bool = False
```

### 3.2 Transcript segment

```python
class TranscriptSegmentV1(BaseModel):
    session_id: UUID
    segment_id: UUID
    start_ms: int
    end_ms: int
    speaker_tag: str
    text: str
    language_hint: str | None
    confidence: float
    stored_raw_clip_id: UUID | None
```

### 3.3 Conversation alert

```python
class ConversationAlertV1(BaseModel):
    alert_id: UUID
    session_id: UUID
    category: str
    business_relevance_score: int
    evidence_conflict_score: int | None
    behavioral_deviation_score: int | None
    statement_excerpt: str
    reasons: list[Reason]
    possible_explanations: list[str]
    verification_question: str
    correlated_event_ids: list[UUID]
    raw_clip_id: UUID | None
    expires_at: datetime
    conclusion: Literal["review_required", "not_relevant", "insufficient_data"]
```

---

## 4. Tasks

### Task 1: Implement monitoring-zone policy and hardware registry

**Files:**
- Create: `services/core/app/modules/office_policy/models.py`
- Create: `services/core/app/modules/office_policy/service.py`
- Create: `services/office-intelligence/app/devices.py`
- Create: `apps/desktop/src/features/office/ZoneAdmin.tsx`
- Test: `services/core/tests/office_policy/test_zones.py`

**Interfaces:**
- Produces: signed active zone policy consumed by Office Intelligence.

- [ ] Test excluded zone, expired notice, unauthorized time and unregistered device.
- [ ] Require owner reauthentication to activate a zone.
- [ ] Display live mic/camera state and physical location.
- [ ] Fail closed when policy cannot be loaded.
- [ ] Commit.

### Task 2: Build encrypted in-memory audio ring buffer

**Files:**
- Create: `services/office-intelligence/app/audio/ring_buffer.py`
- Create: `services/office-intelligence/app/audio/capture.py`
- Create: `services/office-intelligence/tests/audio/test_ring_buffer.py`
- Create: `tests/security/test_no_irrelevant_audio_on_disk.py`

**Interfaces:**
- Produces: `AudioRingBuffer.append(frame)` and `extract_window(start_ms, end_ms)`.

- [ ] Write wraparound, process-crash and 120-second-cap tests.
- [ ] Allocate memory only; prohibit temp-file spill.
- [ ] Cap ring-buffer allocation at 256 MB and reject any configuration that would exceed it.
- [ ] Zero released buffers where supported.
- [ ] Add test scanning configured storage directories for irrelevant fixture audio signatures.
- [ ] Commit.

### Task 3: Implement local voice activity, denoising and acoustic-zone filtering

**Files:**
- Create: `services/office-intelligence/app/audio/preprocess.py`
- Create: `services/office-intelligence/app/audio/vad.py`
- Create: `services/office-intelligence/app/audio/zone_filter.py`
- Test: `services/office-intelligence/tests/audio/test_preprocess.py`

**Interfaces:**
- Produces: timestamped speech frames and acoustic quality metrics.

- [ ] Test fan/traffic noise, overlapping speakers, closed-door distant speech and near-field speech.
- [ ] Use directional/channel energy to reject out-of-zone sound where hardware permits.
- [ ] Mark uncertain zone attribution; do not compensate by increasing mic gain.
- [ ] Record quality metrics, not irrelevant audio.
- [ ] Commit.

### Task 4: Implement ASR and code-switch evaluation harness

**Files:**
- Create: `services/office-intelligence/app/asr/base.py`
- Create: `services/office-intelligence/app/asr/faster_whisper.py`
- Create: `services/office-intelligence/app/asr/resource_lease.py`
- Create: `services/office-intelligence/app/asr/openvino_candidate.py`
- Create: `services/office-intelligence/evaluation/asr_manifest.jsonl`
- Create: `services/office-intelligence/evaluation/evaluate_asr.py`
- Test: `services/office-intelligence/tests/asr/test_timestamps.py`

**Interfaces:**
- Produces: word/segment timestamps, text and confidence.

- [ ] Collect consented staged Urdu/Punjabi/Roman Urdu/English fixtures with ground-truth transcripts.
- [ ] Configure the initial CPU candidate as multilingual `small`, `int8`, one worker, bounded rolling chunks and a 4.5 GB process hard ceiling.
- [ ] Test domain words: IMEI, model names, local party names, amounts and dates.
- [ ] Compute WER plus critical-entity accuracy.
- [ ] Add custom phrase hints without forcing false matches.
- [ ] Require critical-entity accuracy `>= 0.90` and ten-minute audio completion in `<= 15 minutes` in Green state.
- [ ] Deny long ASR work in Orange/Red; preserve the durable backlog and show its age.
- [ ] Benchmark OpenVINO on Intel UHD 770/CPU and leave it disabled unless latency improves by `>= 20%` with no accuracy or crash regression.
- [ ] Commit.

### Task 5: Implement speaker diarization with anonymous tags

**Files:**
- Create: `services/office-intelligence/app/diarization/base.py`
- Create: `services/office-intelligence/app/diarization/adapter.py`
- Create: `services/office-intelligence/evaluation/evaluate_diarization.py`
- Test: `services/office-intelligence/tests/diarization/test_overlap.py`

**Interfaces:**
- Produces: `SPEAKER_1`, `SPEAKER_2` session-local tags.

- [ ] Test two, three, overlapping and out-of-zone speakers.
- [ ] Implement spectral/BIC anonymous clustering as the CPU baseline; do not require a neural diarization server.
- [ ] Evaluate an ONNX speaker-embedding candidate only as a session-local enhancement.
- [ ] Do not persist reusable voice embeddings by default.
- [ ] Display “speaker uncertain” when confidence fails.
- [ ] Measure diarization error rate on local fixtures.
- [ ] Commit.

### Task 6: Implement selective Opus clip storage and 72-hour deletion

**Files:**
- Create: `services/office-intelligence/app/audio/clip_service.py`
- Create: `services/core/app/modules/office_intelligence/retention.py`
- Create: `tests/acceptance/test_audio_72h_deletion.py`
- Create: `tests/security/test_audio_encryption.py`

**Interfaces:**
- Produces: encrypted 30-second pre-context plus up-to-60-second post-context clip.

- [ ] Write failing clock-controlled 72-hour deletion test.
- [ ] Encode 16 kHz mono Opus at configured low bitrate.
- [ ] Enforce a 10 GB audio quota, 72-hour expiry and 15 GB free-space capture stop.
- [ ] Store key ID, hash, reason and exact expiry.
- [ ] Implement owner delete-now and preserve-with-reason flows.
- [ ] Verify preserved evidence receives a new explicit expiry.
- [ ] Commit.

### Task 7: Build meeting-mode consent and recording controls

**Files:**
- Create: `services/core/app/modules/office_intelligence/meeting_session.py`
- Create: `apps/desktop/src/features/meetings/MeetingStartDialog.tsx`
- Create: `apps/desktop/src/features/meetings/RecordingIndicator.tsx`
- Test: `apps/desktop/tests/meeting-consent.spec.ts`

**Interfaces:**
- Produces: authorized meeting session with purpose, participants, notice and sensors.

- [ ] Test start blocked without purpose/policy/indicator.
- [ ] Implement clear start/stop and physical mute reflection.
- [ ] Keep recording indicator persistent above all app routes.
- [ ] On stop, show transcript review and retention timer.
- [ ] Commit.

### Task 8: Implement meeting topic, question and commitment analysis

**Files:**
- Create: `services/office-intelligence/app/meeting/analyzer.py`
- Create: `services/office-intelligence/app/meeting/commitments.py`
- Create: `apps/desktop/src/features/meetings/LiveCopilot.tsx`
- Test: `services/office-intelligence/tests/meeting/test_commitments.py`

**Interfaces:**
- Produces: topic drift, unanswered question, contradiction candidate and commitment draft.

- [ ] Test vague “kal kar denge”, missing owner, conditional promise and repeated discussion.
- [ ] Require human confirmation before publishing Promise Graph entries.
- [ ] Keep private prompts subtle and non-disruptive.
- [ ] Commit.

### Task 9: Implement observable visual-feature extraction

**Files:**
- Create: `services/office-intelligence/app/vision/landmarks.py`
- Create: `services/office-intelligence/app/vision/pose.py`
- Create: `services/office-intelligence/app/vision/baseline.py`
- Test: `services/office-intelligence/tests/vision/test_observations.py`

**Interfaces:**
- Produces: timestamps for head/pose/gesture/gaze-direction changes with quality score.

- [ ] Test occlusion, low light, multiple faces and camera loss.
- [ ] Sample authorized meeting video at 1 FPS initially and allow at most 2 FPS after the mixed-load benchmark.
- [ ] Request a vision lease; drop stale frames instead of building an unbounded queue.
- [ ] Pause vision whenever ASR or Deep Analyst owns the heavy lease.
- [ ] Calculate within-session neutral baseline only after sufficient quality.
- [ ] Never map landmarks directly to emotion or deception labels.
- [ ] Discard raw frames unless meeting policy explicitly preserves the meeting video.
- [ ] Commit.

### Task 10: Implement Evidence Conflict and Behavioral Deviation scores

**Files:**
- Create: `services/office-intelligence/app/integrity/evidence_conflict.py`
- Create: `services/office-intelligence/app/integrity/behavioral_deviation.py`
- Create: `services/office-intelligence/app/integrity/fusion.py`
- Test: `services/office-intelligence/tests/integrity/test_score_caps.py`

**Interfaces:**
- Produces: separate scores and explanations; never `P(lie)`.

- [ ] Test nervous truthful fixture, calm contradictory fixture and insufficient baseline.
- [ ] Evidence score uses records/statements; behavioral score uses observable deviation.
- [ ] Cap overall review priority when no evidence/content conflict exists.
- [ ] Always include alternative explanations and “deception not established.”
- [ ] Commit.

### Task 11: Implement business relevance and adoption-risk classifier

**Files:**
- Create: `services/office-intelligence/app/relevance/taxonomy.py`
- Create: `services/office-intelligence/app/relevance/rules.py`
- Create: `services/office-intelligence/app/relevance/classifier.py`
- Create: `services/office-intelligence/evaluation/relevance_manifest.jsonl`
- Test: `services/office-intelligence/tests/relevance/test_examples.py`

**Interfaces:**
- Produces: direct business relevance, adoption resistance, possible manipulation, stock/cash/security risk or irrelevant.

- [ ] Encode direct/indirect owner, business, stock, cash, invoice, credential and customer-data entities.
- [ ] Add staged examples including “software kisi ne use nahi karna.”
- [ ] Freeze deterministic rules as the baseline; a 1.5B–3B quantized Sentinel candidate may ship only if it improves the preregistered relevance metrics within a 2.5 GB process ceiling.
- [ ] Classify criticism as feedback unless an operational bypass/refusal exists.
- [ ] Require strong confidence or event correlation for high alert.
- [ ] Measure per-category precision/recall; prioritize precision for accusatory-risk categories.
- [ ] Commit.

### Task 12: Implement objective event correlation

**Files:**
- Create: `services/core/app/modules/security_fusion/service.py`
- Create: `services/core/app/modules/security_fusion/rules.py`
- Test: `services/core/tests/security_fusion/test_correlation.py`

**Interfaces:**
- Consumes: conversation candidate, access event, inventory snapshot, POS reference and CCTV timestamp.
- Produces: correlated review alert.

- [ ] Test phrase-only, phrase+door, phrase+door+IMEI mismatch and unrelated coincidence.
- [ ] Increase priority only with time-bounded objective correlation.
- [ ] Never mark theft proven.
- [ ] Keep evidence links and uncertainty.
- [ ] Commit.

### Task 13: Build owner review inbox and correction loop

**Files:**
- Create: `apps/desktop/src/features/office/ConversationInbox.tsx`
- Create: `apps/desktop/src/features/office/IntegrityCard.tsx`
- Create: `services/core/app/modules/office_intelligence/review.py`
- Test: `apps/desktop/tests/conversation-inbox.spec.ts`

**Interfaces:**
- Produces: relevant, not relevant, category correction, delete and preserve decisions.

- [ ] Show countdown to raw deletion.
- [ ] Require source playback access audit.
- [ ] Display content/evidence and behavior separately.
- [ ] Do not expose alert to manager/staff by default.
- [ ] Use owner corrections for evaluation datasets only after review, not live self-training.
- [ ] Commit.

### Task 14: Implement one-zone shadow pilot

**Files:**
- Create: `services/office-intelligence/app/pilot/shadow.py`
- Create: `services/office-intelligence/evaluation/pilot_report.py`
- Create: `docs/runbooks/office-intelligence-pilot.md`
- Test: `tests/acceptance/test_phase_5_shadow.py`

- [ ] Run limited-hour shadow mode with no visible alerts.
- [ ] Have owner independently label sampled segments under policy.
- [ ] Compare precision/recall, missed risk, false business relevance and source quality.
- [ ] Verify irrelevant audio absence and 72-hour deletion.
- [ ] Verify ten-minute audio completes in `<= 15 minutes`, routine Sentinel result p95 is `<= 5 seconds` after transcript availability and Core API p95 remains `<= 500 ms`.
- [ ] Verify ASR peak working set `<= 4.5 GB`, Sentinel `<= 2.5 GB`, ring buffer `<= 256 MB` and no concurrent heavy lease.
- [ ] Freeze these production thresholds before opening pilot results: critical business-risk precision `>= 0.90`, staged explicit-risk recall `>= 0.75`, adoption-resistance precision `>= 0.80`, critical-entity ASR accuracy `>= 0.90`, and non-overlap diarization error rate `<= 0.20`.
- [ ] Treat any raw-retention violation, invisible meeting capture, prohibited deception verdict, or unauthorized playback as an automatic pilot failure regardless of aggregate accuracy.
- [ ] Commit.

### Task 15: Phase 5 adversarial and failure-day acceptance

**Files:**
- Create: `tests/acceptance/test_phase_5_office_intelligence.py`
- Create: `tests/security/test_phase_5_privacy.py`
- Create: `docs/runbooks/audio-deletion-failure.md`
- Create: `docs/runbooks/monitoring-complaint.md`

- [ ] Inject outside voice, overlapping speech, joke, sarcasm, software criticism and explicit bypass discussion.
- [ ] Disconnect camera/mic mid-meeting and verify graceful degradation.
- [ ] Force Green, Yellow, Orange and Red states and verify the exact admission/degradation matrix.
- [ ] Fill `C:` fixture volume to the 15 GB free-space boundary and verify capture stops while deletion and Core continue.
- [ ] Stop deletion worker and verify Rank 0 privacy alert.
- [ ] Attempt unauthorized playback and verify denial/audit.
- [ ] Search UI/API schemas for prohibited verdict labels.
- [ ] Run complete regression suite.
- [ ] Commit and tag `v0.5.0-office-intelligence-pilot`.

---

## 5. Phase 5 acceptance gate

- Monitoring policy and physical zone are approved.
- Meeting recording cannot start invisibly.
- Irrelevant raw audio is absent from disk.
- Relevant clips delete automatically within 72 hours.
- Critical business-risk precision is `>= 0.90`; staged explicit-risk recall is `>= 0.75`.
- Adoption-resistance precision is `>= 0.80`; critical-entity ASR accuracy is `>= 0.90`.
- Non-overlap diarization error rate is `<= 0.20`.
- Ten-minute audio completes in `<= 15 minutes` in Green state.
- Routine Sentinel output p95 is `<= 5 seconds` after transcript availability.
- Core API p95 remains `<= 500 ms` during mixed audio/vision load.
- ASR, Sentinel and ring-buffer memory ceilings pass; heavy concurrency never exceeds one.
- Camera sampling is 1–2 FPS, raw video is not retained and stale frames do not queue.
- Raw-retention, invisible-capture, prohibited-verdict and unauthorized-playback violations are all zero.
- Adoption criticism is not mislabeled as theft/sabotage.
- Behavioral deviation cannot independently produce a high-risk conclusion.
- Every alert says verification is required and deception is not established.
- Owner can delete or preserve with reason.
- No staff punishment, message or external action path exists.
- One-zone shadow pilot is accepted before controlled production.
