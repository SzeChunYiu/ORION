# P11D Negative-Result Root-Cause Audit

**Terminal:** `P11D_SPARSE_DECODER_GAP_NOT_MET`  
**Scientific result:** retained negative  
**Protected cells:** `(17,4,5)` and `(19,3,7)`

## Registered gate that failed

P11D required the universal L1 sparse decoder to need at least four times the compiled sample threshold in **both** cells. Compiled state reached 0.95 mean accuracy at `n=64` in both cells. Sparse universal decoding reached it at `n=128` and `n=256`. The first cell therefore produced only a 2× threshold gap, so the protected terminal is negative.

This terminal is not retuned, relabelled or deleted.

## Scientific root cause

The universal representation contains the five or seven active coordinates among hundreds or thousands of nuisance parity features. The original dense decoder has no explicit support-selection bias and pays a large finite-sample discovery cost. L1 regularization supplies precisely such a bias: it performs downstream structural selection and therefore substitutes for part of the compiler's work.

This identifies the causal boundary of the original result. The state compiler is not creating information; it is supplying a structural prior. A decoder with an appropriate structural prior can buy back part of the accessibility gap.

The residual is still material in the protected cells:

- `(17,4,5)`: compiled `64`, sparse universal `128` at 0.95; `+0.2903076171875` compiled accuracy advantage at `n=64`.
- `(19,3,7)`: compiled `64`, sparse universal `256`; `+0.384033203125` at `n=64`.
- answer-laundering failures: `0`.

The paper therefore promotes the **resource-substitution mechanism**, not the failed ≥4×-everywhere sparse-decoder claim.

## Replay root cause

A second execution reproduced the scientific thresholds and `n=64` deltas exactly, but the canonical full JSON hash changed. The L1 `liblinear` estimator was not given an explicit `random_state`; tiny non-headline curve differences can therefore enter the full payload.

First full-result SHA-256:
`292494434dbb4bc9bb7a5598d19f82e1b0e015357c6b8c3ed6b138412a5b618e`

Second full-result SHA-256:
`c6debddd1699e4c49af46fd733bd2e93495f0ac4b5da35598b01a737a48c563f`

No future run may repair this historical receipt by simply adding a seed and calling the old terminal deterministic. A future replication must receive a new protocol identity with an explicit solver seed frozen before execution.

## Stronger unresolved attack

P11C preregistered L2, L1 and ExtraTrees universal-state arms. Its protected run did not emit a terminal inside the available execution window even after a no-outcome vectorization amendment. P11C remains `CANNOT_CHECK`. It is listed as an open attack rather than inferred from P11D.
