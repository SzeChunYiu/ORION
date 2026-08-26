# P11C Stronger-Decoder Hostile Attack Protocol V1

**Paper:** ORION-P11 — State as Computation  
**Issue:** #471 (with #664 and #667)  
**Protocol identity:** `ORION.P11C.StrongerDecoderAttack.v1`  
**Frozen:** 2026-08-21 before protected-seed execution.

## Question

Does the no-answer-laundering state-compilation advantage survive a materially stronger universal-state decoder that is allowed to exploit sparsity or nonlinear tree ensembles?

This is a hostile attack on the P11B finite-sample result, not a new task family.

## Fixed construction

- Fresh master seed: `2026082111`.
- Protected cells: `(d,s,r)=(17,4,5)` and `(19,3,7)`.
- Query bank: all size-`s` parity characters over `d` Boolean coordinates.
- Five protected queries per cell, each selecting `r` active parity components without replacement.
- Label: majority sign of the `r` selected components.
- Training sizes: `64, 128, 256, 512, 1024, 2048`.
- Test size: `8192`.
- The compiler exposes the `r` selected components only. It is forbidden to output the final label.
- Every selected component is checked against the signed label and its negation on the protected test set.

## Decoder arms

All universal-state arms receive the complete parity bank.

1. `UNIVERSAL_L2`: logistic regression, `C=1`, `liblinear`.
2. `UNIVERSAL_L1`: sparse logistic regression, L1 penalty, `C=0.1`, `liblinear`.
3. `UNIVERSAL_EXTRA_TREES`: 256 ExtraTrees, `max_features=sqrt`, otherwise sklearn defaults, deterministic per-query seed.
4. `COMPILED_L2`: the same L2 logistic learner as arm 1, but only on the `r` compiled components.

No protected-result hyperparameter tuning is permitted. The L1 and ExtraTrees settings were selected as fixed hostile families before the protected seed is run.

## Primary estimand

For each cell and arm, the **first registered training size reaching mean test accuracy >= 0.95** across the five protected queries. `NOT_REACHED` is retained literally.

Define the best hostile universal threshold as the earliest threshold reached by any of the three universal-state arms.

## Positive gate

The protected terminal is `P11C_STRONGER_DECODER_GAP_SUPPORTED` only if all are true:

1. zero answer-laundering failures;
2. `COMPILED_L2` reaches 0.95 by `n=64` in both cells;
3. the best hostile universal threshold is at least 4x the compiled threshold in both cells, treating `NOT_REACHED` as beyond the largest grid point only for the directional gate and never as an extrapolated numeric threshold;
4. at `n=64`, compiled mean accuracy exceeds the best universal mean accuracy by at least `0.20` in both cells;
5. two fresh-process executions produce byte-identical canonical JSON.

Failure of any gate is retained as a negative hostile result. No model is removed after outcomes.

## Claim authority

A positive result authorizes only:

> In two preregistered high-dimensional no-answer-laundering parity-majority cells, the sample-accessibility advantage of query-conditioned component compilation survives fixed sparse-linear and nonlinear tree-ensemble attacks.

It does not authorize a universal nonlinear lower bound, a transformer result, or a real-system superiority claim.
