# OMNISCIENCE Founder Mode

This repository is executed through verified vertical slices.

## Source hierarchy

1. `PROJECT_OMNISCIENCE_MASTER_SPEC.md`
2. `2026-07-29-local-cpu-runtime-design.md`
3. `01-*.md` through `08-*.md`
4. `PROJECT_OMNISCIENCE_FOUNDER_MODE_EXECUTION_PLAN.md`
5. Feature contracts under `docs/engineering/features/`
6. Code and tests

Code never resolves a source conflict silently. Record intentional changes in `docs/founder/DECISION_LOG.md`.

## Autonomous scope

Routine workspace edits, local Git branches, tests, local services, fixture data, browser automation, screenshots, and repair loops are authorized.

Ask before:

- using a real secret or production credential;
- connecting a real accounting/POS source;
- activating a real monitoring zone;
- sending or publishing through a real provider;
- changing production OS, network, or security settings;
- deleting or overwriting production data;
- changing a locked product or safety boundary.

## Mandatory feature loop

1. Create or select a feature contract.
2. Write the smallest failing mechanical and visible proof.
3. Implement the smallest backend-to-UI slice.
4. Run targeted tests, then affected regression tests.
5. Start the real local stack.
6. Verify the actual user journey in a browser.
7. Compare visible values with API and durable facts.
8. Repair until the slice passes.
9. Write a verification manifest and visual review.
10. Integrate only after every applicable gate is green.

## Non-negotiable rules

- `main` must stay runnable.
- Core business behavior cannot require an AI model.
- No cloud-model inference.
- No source-accounting write.
- No external action without deterministic policy and human-bound approval.
- No hidden monitoring, global keylogging, lie verdict, payment, trading, or self-deployment path.
- Stale or incomplete data must be visible and must disable consequential actions.
- Tests and fixtures use anonymized data.
- A port listener is not runtime proof; verify HTTP plus expected content.
- Visual proof includes console/network health and screenshots at 1280x720, 1440x900, and 1920x1080.

