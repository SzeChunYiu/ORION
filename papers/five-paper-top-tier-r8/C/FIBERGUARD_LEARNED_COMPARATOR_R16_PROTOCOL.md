# FiberGuard R16 — untouched learned-selector comparator protocol

Date frozen: 2026-08-26

Exact source parent: `4aac9b030c7e143b739caf42262718924b9a9005`

Status at this commit: **scenario registry, feature/cost accounting, model classes, hyperparameters, folds, arms and interpretation gates are frozen before any R16 algorithm-run, feature-value, feature-cost or feature-runstatus outcome table is read**.

R16 is a comparator study, not a replacement for the exact R11–R15 evidence. It asks whether the action map learned by two standard random-forest formulations improves on FiberGuard's exact support-gated robust cell action when both receive the same representation and pay the same measured feature cost.

## 1. Frozen untouched scenario registry

Repository: `coseal/aslib_data`

Commit: `551b22beef8df17de59286b4822ef720e0aa4d6f`

The registry was selected from domain metadata and complete availability of solver runs, source CV, feature values, feature runstatus and feature costs. No registered scenario may be removed after outcome access.

### BNSL-2016

Domain: Bayesian-network structure learning.

- `description.txt`: `e193c8a46d2b3b9fadfe1cb27bef16db8540bc29`;
- `algorithm_runs.arff`: `33adc274ba3bd7d62875a5ee017d9b4b147e6ee8`;
- `cv.arff`: `b53e47f5d081cfa8901ff652daf40b9c5ecd0a87`;
- `feature_costs.arff`: `09afa0572cc46269bfe03cfc2f008d5b95d2bf40`;
- `feature_runstatus.arff`: `90e494a307c44f3978ca33c5a02e66d2fe4726f3`;
- `feature_values.arff`: `5d981d99a76395ad9828d0ff51f60ecb5fb7965f`.

The description declares runtime/PAR10, a 28,800-second solver cutoff, a 10-second feature cutoff, one feature step and 19 algorithms.

### MIP-2016

Domain: mixed-integer programming solver selection.

- `description.txt`: `0148a3489bdb7afdf2b7fdc46c52e0cdd8cd741c`;
- `algorithm_runs.arff`: `7b079046b38162f8f726c2e3d462684665532a92`;
- `cv.arff`: `a596ee50c3105c6fb45ad2347dc4ab956a9bcd45`;
- `feature_costs.arff`: `c49eb3c464afe8b8dfce5f04cd0450508354a865`;
- `feature_runstatus.arff`: `efc70f485ed47a4cd9fef8751f139b46f5482708`;
- `feature_values.arff`: `139e81684591d6d2a27eba6a805810fd02c8e6de`.

The description declares PAR10, a 7,200-second solver/feature cutoff and one feature step.

### TSP-LION2015

Domain: travelling-salesperson solver selection.

- `description.txt`: `923b7e0cb7cf354af398875f536717e21a8c7388`;
- `algorithm_runs.arff`: `7ec9db6394c52a2b62d1c44fcd84df47b10ba7b9`;
- `cv.arff`: `9d9bee231caaa9cfa017cb176999a36f04d163e5`;
- `feature_costs.arff`: `d6649105f201e9155f5646ff5191e46a824a0ee3`;
- `feature_runstatus.arff`: `259e00133d47da914d9cc9f7435f9c97a4346bb9`;
- `feature_values.arff`: `8c62bc84e319d721691d7b1ef1326f1d08437641`.

The description declares runtime, a 3,600-second solver cutoff, four feature steps and four algorithms.

CPMP-2015 was considered from metadata but excluded before outcomes because its public directory does not contain the feature-cost table required by the common total-excess contract.

## 2. Common folds and accounting

Every scenario is evaluated under:

1. source-supplied CV repetition 1;
2. balanced outcome-blind hash folds obtained by sorting immutable instance identifiers by `(SHA-256(identifier), identifier)` and assigning round-robin to ten folds.

Every arm uses only outer-training outcomes for representation selection, imputation and model fitting.

For one state `x`, action `a` and selected feature-step set `J`, total excess is

`F_J(x) + PAR10(a,x) - min_b PAR10(b,x)`.

The statewise virtual-best oracle has zero feature cost. Non-`ok` solver runs use ten times the scenario cutoff. Feature acquisition uses recorded step cost, with the scenario feature cutoff as the fail-closed missing-cost fallback. Metrics are compared within a scenario, never pooled in raw seconds across domains.

## 3. FiberGuard representation and action

For every outer fold:

1. compute training quartiles for every numeric feature;
2. retain missingness and feature-step runstatus explicitly;
3. enumerate every dependency-closed feature-step set;
4. require at least two training instances before using a cell-specific action;
5. otherwise use the outer-training no-feature robust fallback;
6. select the step set by the R15 lexicographic objective:
   - selected-solver timeout count;
   - mean total excess over the worst `ceil(0.05*n_train)` rows;
   - mean total excess;
   - robust total excess;
   - step count;
   - lexical step tuple.

The selected step set is then frozen for all same-representation learned comparators on that fold. The FiberGuard action remains the exact minimizer of maximum training action regret in each supported quartile cell.

## 4. Frozen learned baselines

Implementation: scikit-learn `1.5.2`, Python `3.12`.

All random states are derived from the immutable string

`SHA-256("R16|scenario|split|fold|arm|algorithm") mod 2^32`.

All forests use:

- `n_estimators=96`;
- `max_depth=18`;
- `min_samples_leaf=2`;
- `max_features="sqrt"`;
- `bootstrap=True`;
- `n_jobs=1`;
- no hyperparameter search.

The fixed depth/leaf controls avoid unconstrained tree growth. Fixed random states make fitting deterministic.

### RF runtime regression

Fit one `RandomForestRegressor` per solver to

`log1p(PAR10 runtime)`.

At test time choose the solver with minimum predicted log-runtime; ties use solver name. This baseline treats PAR10 as a finite target and is not censor-aware survival analysis.

### RF oracle classification

Label each training instance by the lexically first statewise virtual-best solver. Fit one `RandomForestClassifier` with `class_weight="balanced_subsample"`. At test time use the predicted class.

This optimizes oracle-action classification rather than runtime or total excess and is retained as a distinct common formulation.

## 5. Train-only feature matrix

For a selected step set:

- take the sorted union of features provided by those steps;
- for a feature whose nonmissing training values are numeric, replace missing/nonfinite values by the outer-training median and add a missing-indicator column;
- if a numeric feature is missing for the entire outer-training set, use zero;
- for a nonnumeric feature, one-hot encode only outer-training categories and add explicit unknown and missing columns;
- add one-hot step-runstatus columns for the fixed categories `ok`, `presolved`, `timeout`, `memout`, `crash`, `other` and `missing`.

No held-out value influences medians, categories, representation selection or model fitting. Constant columns are retained; no outcome-driven feature pruning is performed.

If FiberGuard selects no feature steps, same-representation RF arms are exactly the no-feature fallback and do not fabricate an identifier feature.

## 6. Registered arms

For every scenario, split and fold:

1. `no_features`;
2. `fiberguard_selected`;
3. `rf_regression_same_steps`;
4. `rf_classification_same_steps`;
5. `rf_regression_all_steps`;
6. `rf_classification_all_steps`.

The same-step arms pay exactly the FiberGuard-selected step cost. All-step arms pay every feature-step cost. Offline model fitting and prediction wall time are not mixed into the historical ASlib runtime unit. GitHub workflow/job accounting remains the engineering resource receipt and is intentionally outside the byte-identical scientific JSON.

## 7. Frozen outputs

Per scenario/split/arm emit:

- selected-solver timeout count/rate;
- worst-five-percent empirical mean total excess;
- mean, median, p95 and robust total excess;
- mean/maximum feature cost;
- one out-of-fold row per instance;
- selected steps by fold;
- train-only matrix dimension and imputation/encoding digest;
- model-class/hyperparameter/random-state digest.

## 8. Precommitted comparator terminals

For two arms `A` and `B` on one split, say `A` failure-aware dominates `B` when:

1. `A` timeout rate is no worse than `B`;
2. `A` worst-five-percent empirical mean is strictly lower than `B`;
3. `A` mean total excess is strictly lower than `B`.

A scenario terminal uses both splits:

- `C_FIBERGUARD_DOMINATES_BOTH_SAME_REPRESENTATION_RF` when FiberGuard dominates both same-step RF arms on both splits;
- `C_BOTH_RF_FORMULATIONS_DOMINATE_FIBERGUARD` when both same-step learned formulations dominate FiberGuard on both splits;
- `C_RF_REGRESSION_DOMINATES_FIBERGUARD` when same-step regression alone dominates FiberGuard on both splits;
- `C_RF_CLASSIFICATION_DOMINATES_FIBERGUARD` when same-step classification alone dominates FiberGuard on both splits;
- `C_LEARNED_AND_FIBERGUARD_MIXED_NO_DOMINANCE` otherwise.

The portfolio reports the exact histogram of these terminals. No scenario is removed after outcomes.

All-feature RF arms are cost-aware controls, not candidates for the same-representation terminal.

## 9. Interpretation and prior-art boundary

Random forests, per-solver runtime regression, oracle-action classification, ASlib, AutoFolio, SUNNY-style selectors, survival-analysis selectors, censor-aware online selection and risk-averse algorithm selection are established donor work. R16 does not claim that a fixed untuned RF is the strongest possible selector.

A FiberGuard win would establish value over two transparent common learned formulations under matched representation/cost, not superiority to AutoFolio, SUNNY-AS2, Run2Survive, HARRIS or every learned selector. A learned win would narrow the FiberGuard application claim without affecting the exact fibre/action-regret theorems.

The next journal gate after R16 remains a current, independently implemented, censor-aware or configured algorithm-selection comparator and external replay. A same-owner scikit-learn baseline cannot confer external authority.

## 10. Authority ceiling

A positive R16 result would be prospectively frozen finite out-of-fold comparator evidence in three historical public scenarios. It would not establish domain-expert family independence, distribution-free tail safety, current production value, external replication, novelty or journal authority.
