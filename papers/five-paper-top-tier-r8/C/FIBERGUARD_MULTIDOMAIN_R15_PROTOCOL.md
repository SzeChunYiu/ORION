# FiberGuard R15 — untouched multi-domain catastrophe/tail protocol

Date frozen: 2026-08-26

Exact source parent: `002117dbf8a90bc1ef26ba0148e856fbc41fdc6d`

Status at this commit: **scenario registry, objective, implementation contract and all interpretation gates frozen before any R15 algorithm-run, feature-value, feature-cost or feature-runstatus outcome table is read**.

R14 is inherited adverse evidence. It showed that a static training-selected SAT policy can improve mean total excess while failing strict robust transfer because one timeout plus positive feature cost exceeds the no-feature PAR10 ceiling. R15 does not change that protocol or reinterpret its result.

## 1. Scientific question

Does FiberGuard's decision-aware representation selection have reproducible cost/tail value outside SAT, when the domain registry is fixed before outcomes and catastrophic solver timeouts are separated lexicographically from average cost?

The experiment is deliberately not another SAT12-ALL reanalysis. It uses three previously unread non-SAT ASlib scenarios spanning distinct optimization/decision domains.

## 2. Frozen external registry

Repository: `coseal/aslib_data`

Commit: `551b22beef8df17de59286b4822ef720e0aa4d6f`

### ASP-POTASSCO

Domain: answer-set programming.

- `description.txt`: `10cf3733c628eaa0dab60a3cef13a88dd639d72e`;
- `algorithm_runs.arff`: `3aacc83ac6b870b9ac52e209d9989c8161c18c17`;
- `cv.arff`: `2c62b456a455c9aedcb15beee0be045866463228`;
- `feature_costs.arff`: `f9e4a8ed429627361066d539cd50451b0ddc16af`;
- `feature_runstatus.arff`: `219bb090549bf2dbda82b385d3ff986b23b9d51f`;
- `feature_values.arff`: `77d7b3e06b7f5c1e718dbfa471f97abe7c98bb10`.

The description declares a 600-second solver and feature cutoff and five dependency-ordered feature steps: one static step and four dynamic steps.

### CSP-Minizinc-Time-2016

Domain: MiniZinc/constraint solver selection.

- `description.txt`: `c4131c095682fe776d21fd05f001e96de66ffd1c`;
- `algorithm_runs.arff`: `96957f2e5010aad21dbb475dffd0a2d23f532d04`;
- `cv.arff`: `4372a490cc67eaa18641bfaf63539f0f1a529ce9`;
- `feature_costs.arff`: `8bcd8c6e2638648ce8dec369fedd980d0e418bad`;
- `feature_runstatus.arff`: `536f31d5c9120e92382d8dabffb8075c5f57f552`;
- `feature_values.arff`: `d48ea61ec21533dddd2a4f88fdd6da9e66eb1733`.

The description declares runtime/PAR10 evaluation, a 1200-second cutoff and one feature step.

### GRAPHS-2015

Domain: graph/subgraph-isomorphism solver selection.

- `description.txt`: `ee98eec74659ed5fe6e354e48b34f4ba9e26c52a`;
- `algorithm_runs.arff`: `69a3670c150366da4f04d280de9a936e9a0d017b`;
- `cv.arff`: `82aa8f02c47dce6b2e5908c72170533c27c855db`;
- `feature_costs.arff`: `5785e525f31f1094ddd707c435273e39e8336ee9`;
- `feature_runstatus.arff`: `d14b49e4d9ae01e4cce0f0084252af72cbc16b19`;
- `feature_values.arff`: `cda576a683a700ce25af0868fa9facb2d97f51a0`.

The description declares seven deterministic solvers, five feature steps and a runtime objective.

The three scenario names were fixed from domain/metadata and complete-file availability, not from algorithm or feature outcomes. All three must be retained regardless of result.

## 3. Common accounting

For each scenario independently:

- aggregate repeated runtime observations by the same median/most-common-status convention used in R11;
- map every non-`ok` solver run to ten times the scenario cutoff;
- retain feature runstatus and missingness in the representation;
- charge measured feature-step acquisition time, with the scenario feature cutoff as the fail-closed missing-cost fallback;
- define `C*(x)` as the statewise virtual-best PAR10 solver runtime with zero feature cost;
- define total excess as

`feature acquisition cost + selected-solver PAR10 runtime - C*(x)`.

Every domain uses its own runtime unit/cutoff. Metrics are compared within a scenario; raw seconds-equivalent values are not pooled across scenarios.

## 4. Two outcome-blind split schemes

### Source CV

Use exactly repetition 1 from each scenario's bound `cv.arff`. All representation thresholds, actions and selection decisions for an outer fold use only the other folds.

### Balanced hash folds

Sort immutable instance identifiers by `(SHA-256(identifier), identifier)` and assign them round-robin to ten folds. This is independent of all outcomes and guarantees fold sizes differ by at most one.

The hash split is a structural control, not a family or distribution-shift oracle. Neither split grants domain-expert family independence.

## 5. Representation and support rule

For each outer fold:

1. compute nearest-rank 25/50/75 percentiles from outer-training numeric feature values only;
2. encode each numeric feature by its training-quartile bin;
3. keep missing values and feature-step runstatus as explicit symbols;
4. enumerate every dependency-closed feature-step set;
5. permit a cell-specific action only when the training cell has at least two members;
6. otherwise use the outer-training no-feature robust action.

The support threshold is fixed at two. No outcome-dependent smoothing or nearest-cell borrowing is allowed.

## 6. Registered arms

For every scenario, split and fold:

1. `no_features`;
2. `all_features` with training quartiles/support two;
3. `robust_selected`: exact minimization of outer-training robust total excess over the complete dependency-closed menu;
4. `catastrophe_tail_selected`: exact lexicographic minimization of
   - selected-solver timeout count;
   - mean total excess over the worst `ceil(0.05*n_train)` rows;
   - mean total excess;
   - robust total excess;
   - number of selected feature steps;
   - lexical step tuple.

This ordering is not a weighted scalarization. One fewer timeout dominates every possible improvement in lower-priority quantities.

## 7. Exact finite theorems

### Theorem R15.1 — ceiling barrier

Let a baseline policy have robust total excess `B`. If another policy has some state `x` with terminal action regret at least `B` and positive feature cost on `x`, its robust total excess is strictly greater than `B`.

**Proof.** Its total excess on `x` is `c(x)+R(x)>B`; the robust maximum is at least that value. ∎

In a PAR10 panel where the no-feature baseline reaches the penalty ceiling, any selected-solver timeout with sufficiently small oracle runtime and positive acquisition cost can therefore defeat strict robust improvement. This is an accounting fact, not evidence that feature acquisition lacks average value.

### Definition R15.2 — exact empirical worst-five-percent mean

For a finite list of `n` total-excess values, let `k=ceil(0.05 n)`. Sort losses nonincreasingly and average the first `k`. The statistic is exact and is witnessed by those `k` rows.

It is a finite descriptive tail functional. It is not a population CVaR bound or a distribution-free guarantee.

### Theorem R15.3 — exact lexicographic selection

On a finite dependency-closed feature menu and finite training corpus, exhaustive evaluation returns the exact minimum of the R15 catastrophe/tail tuple.

**Proof.** Every candidate tuple is computed exactly and the menu is finite; lexicographic order is total after the declared tie breakers. ∎

### Theorem R15.4 — no average-to-safety promotion

A lower mean or empirical tail statistic does not imply a lower robust maximum. Conversely, a lower robust maximum does not imply a lower mean.

**Proof.** Two-coordinate counterexamples are `(0,10)` versus `(6,6)` for the first direction and `(5,5)` versus `(0,6)` for the second. ∎

Therefore every outcome must report timeout, tail, mean and robust values separately.

## 8. Primary gate

For one scenario/split, the catastrophe-tail arm passes only if:

1. its selected-solver timeout rate is no worse than both no features and all features;
2. its worst-five-percent mean total excess is strictly below both extremes;
3. its mean total excess is strictly below both extremes.

A scenario passes only if all three conditions hold on both source CV and balanced-hash folds.

The portfolio terminal is determined solely by the number of passing scenarios:

- `C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_ALL_THREE`;
- `C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_TWO_OF_THREE`;
- `C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_ONE_OF_THREE`;
- `C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_NONE`.

No scenario may be removed after outcome access.

## 9. Frozen outputs

Emit, per scenario/split/arm:

- instance, solver, feature and candidate-set counts;
- exact selected steps by fold;
- policy and quartile-threshold digests;
- selected-solver timeout count/rate;
- robust, worst-five-percent mean, mean, median and p95 total excess;
- mean/maximum feature cost;
- signature-seen, supported-cell-use and fallback rates;
- one out-of-fold prediction row per instance;
- exact primary-gate booleans.

The workflow must run the complete audit twice and require byte-identical JSON and terminal output.

## 10. Interpretation boundary

A positive result would establish that one exact catastrophe/tail selection procedure retains finite out-of-fold value in the named historical scenarios. It would not establish:

- a learned-selector advantage;
- a probabilistic tail guarantee;
- domain-expert family independence;
- cross-repository replication;
- current production value;
- generic novelty; or
- journal authority.

Generic PAR10, cross-validation, quantile binning, lexicographic optimization, tail-risk summaries, active feature acquisition and algorithm-selection methods are donor-owned. The residual FiberGuard claim remains the exact complete-fibre/action-regret accounting, the failure-aware representation policy, and the evidence discipline connecting complete-corpus, held-out and cross-domain terminals without promoting one into another.
