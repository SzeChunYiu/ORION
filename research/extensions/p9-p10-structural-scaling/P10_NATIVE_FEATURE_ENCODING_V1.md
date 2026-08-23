# P10 Native Feature Encoding V1

Status: **FROZEN BEFORE NATIVE-STATE OUTCOMES**

Frozen: 2026-08-20

This file fixes implementation details left abstract by the parent native-state protocol.

- Tactic-label order is the existing 16-family order in `lean_source.TACTIC_FAMILIES`.
- Goal/context shape categories are exactly the eleven categories in `P10_NATIVE_TRACE_STATE_EXTRACTOR_AMENDMENT_V1.md`.
- State token buckets are `0-31`, `32-63`, `64-127`, `128-255`, `256-511`, `512+`.
- Visible depth buckets are `0-2`, `3-5`, `6-9`, `10+`.
- Normalized-state duplicate-group buckets are `1`, `2`, `3-4`, `5+`.
- Numeric count/fraction features are used at their raw deterministic values; no outcome-fitted scaling or feature selection is performed.
- Categorical features are fixed one-hot coordinates. Unseen categories therefore cannot create a new held-out feature column.
- B2/B3/B4 are L2-regularized multinomial logistic regressions with `lbfgs`, maximum 2000 iterations and no class weighting.
- C grid is exactly `{0.01,0.1,1.0,10.0}`. Nested leave-one-training-module-out total held-module negative log likelihood selects C; ties choose the smaller C.
- If a held-out true family is absent from an inner/outer fitted classifier's class set, its probability is `1e-15` for log-loss accounting. This does not fabricate a class prediction.
- No feature normalization, PCA, embedding, calibration, feature pruning or threshold tuning is permitted after outcomes.
