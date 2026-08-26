# ORION-15 checkbox audit versus `origin/main` (2026-08-17, issue #102)

Subject inspected: `origin/main` at `03b2dae910ac3cc4a1bc21cb422caea6e37cfb22` plus additive journal files in `cursor/paper-102`.

## Method

Boxes are ticked only when a repository artifact on this subject supports them. Protocol/design ticks do not promote H1. The glm-5.2 JSONL was recounted from raw rows: 21 correct, 3 incorrect (`ORION-15-HC-002`, `ORION-15-HC-012`, `ORION-15-HC-018`). A previously advertised perfect-score report is not used (`research/failures/2026-08-p5-live-artifact-branch-identity-mismatch/`).

## Live campaign

`CANNOT_CHECK`. `OPENAI_API_KEY`, protected-verifier URL/token/hash, and `ORION_PHASE2_EVALUATION_EPOCH_ID` were unset. `#8` `LIVE_TRIAL_PACKET_V1.json` still has `corpus_revision: UNBOUND`. No new live run was started.

## Tables

| Artifact | Status |
| --- | --- |
| Table ORION-15-1 nearest work | Present on main |
| ORION-15-3 confusion matrix | Generated here from 21/24 JSONL |
| Residual-error ledger | Generated here; three errors preserved |
| ORION-15-2, ORION-15-4, ORION-15-5, ORION-15-6, ORION-15-7 | `CANNOT_CHECK` stubs (no campaign rows) |
| Table ORION-15-T2 baselines/ablations | `CANNOT_CHECK` stub |
| Table ORION-15-T3 campaign harmful/null | `CANNOT_CHECK` stub |

Sibling `p5-tables` worktree was read-only and not written.
