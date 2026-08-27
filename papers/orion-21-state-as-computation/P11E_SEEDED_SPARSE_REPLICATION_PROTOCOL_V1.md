# P11E Seeded Sparse-Decoder Replication Protocol V1

**Paper:** ORION-21 — State as Computation  
**Issue:** #471  
**Protocol:** `ORION.P11E.SeededSparseReplication.v1`  
**Frozen:** 2026-08-21 before protected execution.

## Motivation

P11D permanently failed its preregistered ≥4×-threshold-in-both-cells gate. It nevertheless produced a 2× and 4× threshold residual, but its full JSON was not byte-identical across runs because the `liblinear` sparse decoder had no explicit `random_state`.

P11E does **not** relabel P11D. It tests a new replication hypothesis on a fresh data seed with all stochastic estimator seeds explicit:

> Does query-conditioned component compilation retain at least a 2× 0.95-accuracy sample-threshold advantage over a frozen sparse L1 universal-state decoder in both registered hostile cell families?

The ≥2× replication target is prospectively frozen for this new experiment because P11D already ruled out the stronger ≥4×-in-both-cells claim.

## Frozen construction

- fresh data seed: `2026082117`;
- cells: `(17,4,5)` and `(19,3,7)`;
- five protected queries per cell;
- train sizes: `64,128,256,512,1024,2048`;
- test size: `8192`;
- same no-answer-laundering parity-majority construction as P11D;
- vectorized parity-bank evaluation only.

## Decoder arms

- `UNIVERSAL_L1`: L1 logistic regression, `C=0.1`, `liblinear`, `random_state` frozen per cell/query/training size;
- `COMPILED_L2`: L2 logistic regression, `C=1`, `liblinear`, explicit frozen `random_state`, active components only.

No hyperparameter is selected from protected outcomes.

## Positive terminal

`P11E_SEEDED_SPARSE_RESIDUAL_REPLICATED` requires:

1. zero answer-laundering failures;
2. compiled threshold <=64 in both cells;
3. sparse universal threshold >=128 or `NOT_REACHED` in both cells;
4. compiled minus sparse-universal mean accuracy at `n=64` >=0.20 in both cells;
5. two fresh evaluations produce byte-identical canonical JSON.

## Claim authority

A positive P11E result supports only:

> On a fresh protected seed with explicitly deterministic sparse decoding, the controlled query-conditioned compilation advantage replicates at a minimum 2× sample-threshold gap in both registered cell families.

It does not restore P11D's failed ≥4×-in-both-cells claim.
