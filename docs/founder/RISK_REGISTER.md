# Phase 0 Risk Register

| Risk | State | Automatic response |
|---|---|---|
| Native PostgreSQL 16 is unavailable | Closed locally | Doctor and runtime health verify the native service before each feature proof |
| Python 3.12 is unavailable system-wide | Open | Let `uv` provision a project-local 3.12 runtime |
| Real POS/accounting format is unavailable | Expected | Use versioned anonymized fixtures |
| Real provider credentials are unavailable | Expected | No provider code path in Phase 0 |
| UI/API state diverges | Controlled | Contract test plus browser/API cross-check before integration |
| Browser or Electron runtime fails | Open | Capture exact failure and repair before shell integration |
