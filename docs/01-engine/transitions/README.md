# Mechanic transition semantics

A mechanic is governed by a state-transition relation, not by unconstrained prose generation.

The universal lifecycle is fail-closed:

```text
CREATED -> READY -> RUNNING -> {SUCCEEDED, PARTIAL, FAILED, BLOCKED, CANNOT_CHECK}
```

Each rule declares a trigger, preconditions, postconditions, determinism/nondeterminism class, side-effect semantics and retry safety. `BLOCKED` and `CANNOT_CHECK` can occur before or during execution and must not be coerced into success.

A generic relation is

\[
F_i:(X_i,I_i,A_i)\rightarrow\mathcal P(X'_i,O_i,S_i),
\]

where the set-valued codomain permits nondeterministic/external outcomes. A calibrated stochastic kernel may replace the set-valued relation only where probabilities are justified.

## Retry and side effects

Validation-only transitions are expected to be idempotent. External/model/tool effects require a side-effect guard and receipts. Once a terminal receipt exists, recovery should normally replay the receipt rather than silently execute the same external effect again.

## Boundary

This lifecycle contract is universal orchestration, not the scientific dynamics of each child mechanic. SEARCH ranking, evidence absorption, GLUE, diagnosis, experiment selection, and other steps still require their own formal state/action/transition semantics and hostile tests.
