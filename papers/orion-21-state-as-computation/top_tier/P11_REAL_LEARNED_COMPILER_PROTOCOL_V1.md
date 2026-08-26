# ORION-21 real learned-compiler protocol V1

**Programme:** #977  
**State:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** test a learned, non-oracle task-state compiler on non-synthetic public data with explicit compiler/state/downstream accounting.

## Datasets and protected evaluation

Use only scikit-learn bundled real datasets:

- breast cancer Wisconsin;
- wine chemistry;
- handwritten digits.

Five-fold `StratifiedKFold(shuffle=True)` with seeds `20261101 + dataset_index`. Every compiler/model is fit on the training fold only; test labels are unavailable until final scoring.

`StandardScaler` is fit on the training fold only.

## Learned compiler

Use training-fold `SelectKBest(f_classif)` as a deliberately simple donor-owned learned compiler. It learns **which source coordinates to retain**, not the test answer.

Freeze retained dimensions:

- breast cancer: `k=15` of 30;
- wine: `k=7` of 13;
- digits: `k=32` of 64.

The compiled state is the selected standardized coordinates. The compiler may use training labels but never protected test labels/outcomes. Selected feature identities must be recorded per fold.

This selector is not claimed as novel; it is an instrument for the state-as-computation hypothesis.

## Downstream systems

All models use fixed hyperparameters across folds/datasets/arms.

1. `UNIVERSAL_LINEAR` — logistic regression over all standardized coordinates;
2. `COMPILED_LINEAR` — identical logistic regression over compiled coordinates;
3. `UNIVERSAL_FOREST` — 200-tree random forest over all standardized coordinates;
4. `COMPILED_FOREST` — same forest over compiled coordinates.

Logistic: `C=1`, `lbfgs`, `max_iter=5000`.

Forest: `n_estimators=200`, `max_depth=10`, `min_samples_leaf=2`, `n_jobs=1`; fold seed fixed and shared across universal/compiled arms.

## Resource vector

Follow `papers/candidates/RESOURCE_LOCATION_SEMANTICS_V1.md`.

Record separately:

- **compiler fit proxy:** `n_train * d` univariate feature-value inspections plus stable top-k selection;
- **compiler inference proxy:** `n_example * d` source-coordinate inspections to form compiled state;
- state dimension and float count;
- downstream logistic coefficient count + iterations;
- downstream forest tree count + total node count + mean depth;
- accuracy.

Do not use hosted-runner wall time as scientific authority.

## Primary real-system tests

### E11.1 learned non-oracle compiler

The compiler is valid only if it was fit from the training fold, its selected feature indices are archived, and no test label enters scaling/selection/training.

### E11.2 smaller-state/smaller-reasoner non-inferiority

Per dataset compare `COMPILED_LINEAR` to `UNIVERSAL_LINEAR` at fold level.

Positive dataset criterion:

- mean compiled accuracy >= mean universal accuracy - `0.02`;
- compiled state dimension <= 0.6 * universal dimension;
- compiled logistic coefficient count <= 0.65 * universal coefficient count.

Programme positive requires at least **2 of 3 datasets** meet the criterion. All three remain reported.

### E11.3 stronger nonlinear access attack

Compare the universal-vs-compiled gap under forest access. If the forest eliminates a linear accessibility effect, report that as access-class dependence; do not delete the result.

### E11.4 compiler amortization

For each fold, report the one-time compiler-fit proxy and the per-example compiled-state formation proxy. Do not claim total-cost superiority unless the prospectively declared use horizon amortizes compiler cost; instead report exact break-even horizon for downstream stored-state floats/parameter savings where meaningful.

## Hostile checks

- train/test leakage through scaler/selector;
- test labels influence selected coordinates;
- compiler directly emits predicted class rather than state coordinates;
- universal and compiled arms use different downstream hyperparameters;
- compile cost is treated as free;
- only positive datasets are reported;
- accuracy non-inferiority hides large class-specific failure: report per-class accuracy/recall tables;
- feature selection is rebranded as ORION-21 novelty.

## Frozen terminal

`P11_REAL_LEARNED_COMPILER_V1_SUPPORTED` requires valid leakage checks and at least 2/3 positive datasets under E11.2. Forest results are diagnostic and cannot be used to retune k/hyperparameters.

If the gate fails, retain `P11_REAL_LEARNED_COMPILER_V1_GATE_NOT_MET` and use the result to localize where the compiler/state tradeoff fails.

## Authority boundary

A positive closes one real learned-compiler/explicit-accounting requirement. It does not satisfy the preferred open-weight/procedural + formal/search cross-domain replication or universal state-as-computation superiority.
