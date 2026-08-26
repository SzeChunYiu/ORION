# P3 remaining `CANNOT_CHECK` — V1 journal-readiness closeout

**Date:** 2026-08-17  
**Issue:** #100  
**Rule:** an LLM cannot become gold. Missing expert labels are recorded, not filled.

## Expert gold (original `P3.cross-domain-atlas.v1`)

| Requirement | Status | Evidence |
|---|---|---|
| Two independent annotators on a shared subset | `CANNOT_CHECK` | `gold/annotations/annotator-a/` and `annotator-b/` do not exist; `GOLD_METHODOLOGY_V1.md` §3.1 |
| Per-coordinate inter-annotator agreement | `CANNOT_CHECK` | agreement not computable without independent labels |
| Adjudication of real disagreements | `CANNOT_CHECK` | `seed-to-gold-v1` templates skipped independent labeling |
| Domain-expert review of specialist cases | `CANNOT_CHECK` | no specialist-review artifacts on `origin/main` |
| Verified open-access source spans for the 32 eight-family samples | `CANNOT_CHECK` | SEED placeholder document IDs and `seed:sha256:…` hashes |
| Promote `gold/adjudicated/P3.*.gold.json` to expert gold | **forbidden** | annotator_id is `seed-to-gold-v1` |

These boxes stay open. They are not closable by generating labels.

## Atlas CI flakiness (operational, not a mapping-result defect)

Recent red Xes on `p3-public-reference.yml` and `p3-public-reference-confirmatory-eval.yml` failed at **auto-push of archived evidence back to the PR branch** (`! [rejected] HEAD -> <branch> (fetch first)`), after the gold/evaluation artifacts had already been written and uploaded.

| Run | Workflow | Failure class |
|---|---|---|
| [32048771229](https://github.com/SzeChunYiu/ORION/actions/runs/32048771229) | P3 public-reference atlas | non-fast-forward push to PR branch |
| [32048685335](https://github.com/SzeChunYiu/ORION/actions/runs/32048685335) | P3 public-reference atlas | same class |
| [32047808154](https://github.com/SzeChunYiu/ORION/actions/runs/32047808154) | confirmatory eval | same class |

Later runs of the same workflows, and `p3-public-reference-atlas.yml` / publication workflow, are green. Treat historical red Xes as **CI push-race flakiness**, not as a failed confirmatory mapping evaluation. Do not re-freeze gold because of them. A workflow that cannot push to a moving PR branch is still `CANNOT_CHECK` as a fully hands-off archive path.

## Claims that remain `CANNOT_CHECK`

From `CLAIM_LEDGER_V1.md`:

- **P3.C7** raw-text end-to-end integration vs model/RAG/schema baselines
- **P3.C8** downstream scientific answer quality
- **P3.C6** necessity of every coordinate (partial: obstruction/modality supported; referent/construct/measurement/temporal unidentified on current coverage)

Issue #280 owns the adversarial V2 atlas that would test those coordinates. This file does not start that atlas.
