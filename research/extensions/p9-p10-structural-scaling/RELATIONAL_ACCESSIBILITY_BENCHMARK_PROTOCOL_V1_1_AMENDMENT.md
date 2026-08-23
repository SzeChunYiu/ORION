# Relational Accessibility Benchmark Protocol V1.1 Amendment

Status: **FROZEN BEFORE BENCHMARK OUTCOME**

Frozen: 2026-08-20

Supersedes for execution: `RELATIONAL_ACCESSIBILITY_BENCHMARK_PROTOCOL_V1.md` only by clarifying the previously qualitative hostile-control phrase “do not reproduce the relational result”.

No dimension, sample size, seed, model, representation, primary effect threshold or endpoint changes.

## Exact hostile-control gates

At `n_train=4096`, for every frozen dimension:

1. **Broken relation:** logistic test accuracy on the cyclically misaligned relational coordinates must be `< 0.65`.
2. **Label shuffle:** both FLAT and RELATIONAL logistic test accuracy with shuffled training labels must be `< 0.65`.
3. **Shared surface permutation:** for each representation separately, absolute accuracy change relative to the canonical unpermuted run must be `< 0.03`.
4. **Bijection:** reconstruction failure count must be exactly `0` across all canonical generated train and protected-test rows.

If any hostile-control gate fails, the controlled positive terminal is blocked even if the primary accuracy deltas pass.

Execution protocol identity: `P9P10.RelationalAccessibilityProtocol.v1.1`.
