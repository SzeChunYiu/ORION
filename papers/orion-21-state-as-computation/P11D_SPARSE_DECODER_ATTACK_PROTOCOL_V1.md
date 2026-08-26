# P11D Sparse-Decoder Hostile Attack Protocol V1

**Paper:** ORION-ORION-21 — State as Computation  
**Issue:** #471  
**Protocol:** `ORION.P11D.SparseDecoderAttack.v1`  
**Frozen:** 2026-08-21 before protected execution.

P11D asks whether P11B's finite-sample gap is merely an artifact of a dense universal-state decoder that fails to exploit the true sparse support.

- Fresh seed `2026082116`.
- Cells `(17,4,5)` and `(19,3,7)`.
- Five protected queries per cell.
- Same parity-majority/no-answer-laundering construction as P11B.
- Train sizes `64,128,256,512,1024,2048`; test `8192`.
- `UNIVERSAL_L1`: universal parity bank, L1 logistic regression, `C=0.1`, `liblinear`.
- `COMPILED_L2`: only the registered active components, L2 logistic regression, `C=1`, `liblinear`.
- Vectorized parity evaluation is an implementation detail and does not alter sample identity.

Primary threshold is first `n` with mean accuracy >=0.95.

`P11D_SPARSE_DECODER_GAP_SUPPORTED` requires:
1. zero active component equal to or negating the final signed label;
2. compiled threshold <=64 in both cells;
3. universal-L1 threshold / compiled threshold >=4 in both cells;
4. compiled minus universal-L1 accuracy at n=64 >=0.20 in both cells;
5. two byte-identical executions.

A positive result authorizes only the claim that the registered high-dimensional controlled gap survives a fixed sparse-linear feature-selection attack. It does not settle the frozen ExtraTrees attack or establish a universal nonlinear lower bound.
