# Resource-accounting contract and statistical analysis

The scalar controlled budget is intentionally clean. Real systems require vector receipts including:

- compiler/retrieval/preprocessing model and operations;
- state tokens/bytes and memory traffic;
- downstream generated tokens/recurrent steps;
- search nodes and verifier calls;
- tool calls and external latency;
- cache/recovery cost;
- model identity/capacity;
- end-to-end latency and reproducible energy where available.

A joint policy cannot “win” by shortening the downstream trace while hiding expensive retrieval or compilation upstream. Likewise a reasoning-only baseline cannot receive a larger model or search cap. If resource vectors are incomparable, the result should be a quality–resource Pareto frontier rather than a post-hoc weighted score.

## Statistical analysis

The protected unit of generalization is the held-out family. Policies see paired items inside each family, while headline uncertainty is computed by a deterministic **20,000-resample family-block bootstrap** over the 16 family-level joint gains. The registered lower bound is positive.

The analysis does not pool items as if 8,192 individual trials were independent domains. Hyperparameters are frozen before protected evaluation. The worst-family gain is reported to prevent a favorable mean from hiding a family-level failure.