# P11G Deterministic Tree-Decoder Successor Protocol V1

**Paper:** ORION-P11 — State as Computation  
**Issue:** #471  
**Protocol:** `ORION.P11G.DeterministicTreeDecoder.v1`  
**Frozen:** 2026-08-21 before P11G protected execution.

## Why P11G exists

P11F produced a positive finite tree-decoder result, but hostile PR review found a protocol-conformance defect: the runner set `n_jobs=-1` although the frozen protocol said the ExtraTrees arm used the specified tree count/feature rule and otherwise sklearn defaults. The two observed P11F payloads happened to match, but the implementation did not exactly instantiate the written protocol.

P11F is therefore retained as **non-authoritative protocol-mismatch evidence**. P11G is a new successor; it does not edit or relabel P11F.

## Frozen construction

- fresh data seed: `2026082120`;
- cells: `(17,4,5)` and `(19,3,7)`;
- three protected queries per cell;
- train sizes: `64,128,256,512,1024`;
- test size: `4096`;
- same parity-majority no-answer-laundering construction;
- vectorized parity bank;
- no protected hyperparameter tuning.

## Decoder arms

### Universal nonlinear decoder

`UNIVERSAL_EXTRA_TREES`

- `ExtraTreesClassifier`;
- `n_estimators=96`;
- `max_features="sqrt"`;
- explicit deterministic `random_state` per cell/query/train-size;
- **`n_jobs=1`**;
- every other estimator argument left at sklearn default.

### Compiled decoder

`COMPILED_L2`

- active query components only;
- L2 logistic regression, `C=1`, `liblinear`;
- explicit deterministic `random_state`.

Neither arm receives the final label as an input feature.

## Replay authority

The authoritative P11G executable must itself launch **two fresh Python subprocess executions** of the complete one-run scientific pipeline. A positive terminal is impossible unless:

1. both subprocesses exit successfully;
2. their canonical scientific JSON bytes are identical;
3. their SHA-256 digests are identical;
4. all scientific gates below pass.

Replay verification is therefore in the terminal decision path, not merely prose or a manually asserted receipt field.

## Scientific gates

`P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED` requires all of:

1. zero answer-laundering failures;
2. compiled 0.95 threshold `<=64` in both cells;
3. tree-universal 0.95 threshold `>=256` or `NOT_REACHED` in both cells;
4. compiled-minus-tree mean accuracy at `n=64 >= 0.20` in both cells;
5. two fresh subprocess scientific payloads byte-identical.

Any failed gate produces `P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET` and remains first-class evidence.

## Claim authority

A positive P11G result supports only:

> In two fresh high-dimensional no-answer-laundering cells, query-conditioned component state retains a registered low-sample advantage over a deterministic single-thread 96-tree ExtraTrees decoder operating on the complete universal parity bank.

It does not establish a universal nonlinear lower bound, real-agent superiority, or that compilation dominates all possible downstream search mechanisms.
