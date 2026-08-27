# P11F Tractable Nonlinear Tree-Decoder Attack Protocol V1

**Paper:** ORION-21 — State as Computation  
**Issue:** #471  
**Protocol:** `ORION.P11F.TractableTreeDecoderAttack.v1`  
**Frozen:** 2026-08-21 before protected execution.

## Motivation

P11C preregistered a larger ExtraTrees attack but repeatedly exceeded the available execution window before emitting any protected terminal, even after a no-outcome parity-bank vectorization amendment. P11C remains `CANNOT_CHECK`.

P11F is a new, computationally bounded successor. It does not claim that P11C passed. Its purpose is to test whether the controlled state-compilation advantage survives one **nonlinear tree-ensemble universal-state decoder** whose entire resource envelope is frozen to complete reproducibly on the available harness.

## Frozen construction

- fresh data seed `2026082118`;
- cells `(17,4,5)` and `(19,3,7)`;
- three protected queries per cell;
- train sizes `64,128,256,512,1024`;
- test size `4096`;
- same no-answer-laundering parity-majority construction;
- vectorized parity bank;
- no protected hyperparameter tuning.

## Decoder arms

- `UNIVERSAL_EXTRA_TREES`: 96 trees, `max_features="sqrt"`, deterministic per-cell/query/training-size seed, otherwise sklearn defaults;
- `COMPILED_L2`: L2 logistic regression, `C=1`, `liblinear`, explicit deterministic seed, only the registered active components.

The tree arm receives the complete universal parity bank. The compiled arm never receives the final label as a feature.

## Positive terminal

`P11F_TREE_DECODER_GAP_SUPPORTED` requires:

1. zero answer-laundering failures;
2. compiled threshold <=64 in both cells;
3. tree-universal 0.95 threshold >=256 or `NOT_REACHED` in both cells;
4. compiled minus tree-universal mean accuracy at `n=64` >=0.20 in both cells;
5. two fresh executions produce byte-identical canonical JSON.

## Claim authority

A positive result supports only:

> In two fresh high-dimensional no-answer-laundering cells, the low-sample accessibility advantage of query-conditioned component compilation survives a frozen nonlinear ExtraTrees universal-state decoder under the registered tree resource envelope.

It does not establish a universal nonlinear lower bound and does not retroactively resolve P11C.
