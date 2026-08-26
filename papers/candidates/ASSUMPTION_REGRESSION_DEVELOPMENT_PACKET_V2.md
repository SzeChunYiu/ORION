# Development packet — ORION-16–ORION-18 V2 assumption-regression tranche

**Date:** 2026-08-17  
**Branch:** `shadow/p6-p8-mathematical-completion-2026-08-17`  
**Stack base:** draft programme branch `shadow/p6-p8-paper-programme-2026-08-17`

## Problem

The candidate-paper branch already contained strong V1 formal cores and finite checkers. Two risks remained:

1. a theorem could be stronger than the semantic assumptions encoded by its finite checker;
2. benchmark JSON could be structurally valid without its expected scientific terminal being executed.

## Scoped change

Add only new V2 files. Do not replace the current V1 formal cores/checkers, modify ORION-11–ORION-15, change the five-paper registry, or claim promotion.

## Invariants

- ORION-11–ORION-15 ownership remains unchanged.
- V1 exhaustive counts remain untouched.
- ORION-16 corrections narrow claims; they do not increase authority.
- ORION-17/ORION-18 reference oracles are manifest-integrity checks, not candidate-agent baselines.
- every hostile family has a negative/clean control sufficient to defeat trivial detectors or total refusal.
- no network/model dependency is introduced.

## Failure cases frozen before commit

- ORION-16 spurious dependency edge disproving minimality from graph soundness alone;
- undeclared write and separation aliasing;
- forged authority root, recursive cycle and self-authorization;
- ORION-17 unknown/censored coverage, deceptive route diversity, beneficial/harmful topology change and non-retrieval transfer;
- ORION-18 five paired domain cases, five laundering attacks, unresolved hard obligation and valid explicit cross-domain coercion.

## Verification

```bash
python -m compileall -q papers/candidates
python papers/candidates/run_assumption_regressions_v2.py \
  --json-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.json \
  --markdown-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.md
```

Frozen terminal: 28 tests, 29 structural checks and 37 cases pass; aggregate hash `bbf26697db10993486c3620c8571b6231de7eef997d966cdda8f87761e569a04`.

## Rollback

All changes are additive. Reverting the single V2 commit removes the tranche without altering the V1 programme or official paper tree.
