# P9 real accessibility scaling protocol V1

**Programme:** #977  
**State:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** add a non-synthetic real-data intervention to the bounded P9 package while preserving all historical negative/sufficiency results.

## Scientific discriminator

Can two interfaces carry the same semantic information yet impose materially different downstream resource/capacity requirements, and can a representation repair close that deficit more cheaply than model/access-mechanism escalation?

This is a real supervised-learning accessibility study, not yet the open-weight LLM + verifier-backed two-domain terminal required for the broadest P9 claim.

## Frozen datasets

Use only scikit-learn bundled datasets, so no network data drift is possible:

1. `load_breast_cancer` — clinical/tabular binary classification;
2. `load_wine` — chemical/tabular multiclass classification;
3. `load_digits` — handwritten-image multiclass classification.

For each dataset use `StratifiedKFold(n_splits=5, shuffle=True, random_state=20260823 + dataset_index)`.

`StandardScaler` is fit on the training fold only and applied to both train/test.

## Representation interventions

Given standardized feature vector `z`:

- `NATIVE`: `z`;
- `CUBIC`: elementwise `z^3`;
- `REPAIRED`: `cuberoot(CUBIC)`, which should reconstruct `z` numerically;
- `LOSSY`: `CUBIC` with every second feature coordinate zeroed after the transform.

`CUBIC` is a bijection over real-valued vectors, so `NATIVE`, `CUBIC`, and `REPAIRED` contain the same mathematical information. `LOSSY` is an explicit missing-information control.

A protected run fails if maximum absolute `REPAIRED-NATIVE` reconstruction error exceeds `1e-10`.

## Access/model classes

Freeze three deterministic access mechanisms:

1. `LINEAR`: multinomial/binary logistic regression, `C=1`, `max_iter=5000`, `lbfgs`;
2. `FOREST_20`: random forest, 20 trees, `max_depth=6`, `min_samples_leaf=2`, single-threaded;
3. `FOREST_200`: same configuration with 200 trees.

Random forest seeds are fixed by `(2026082300 + dataset_index*100 + fold_index)` and shared across representations inside the fold.

Trees are included because monotone feature transformations preserve per-feature ordering, making them a strong access-mechanism attack on a linear accessibility effect. P9 does not assume they will lose.

## Resource accounting

Do **not** use wall-clock time as a headline resource because hosted-runner timing is noisy.

Report:

- representation transform operations per example (native=0; cubic and repair separately counted; lossy mask counted);
- feature count;
- logistic fitted coefficient count and iteration count;
- forest tree count, total fitted node count and mean fitted maximum depth;
- test accuracy for every fold/arm.

These remain separate coordinates; no post-hoc scalar weighting.

## Primary quantities

Per dataset:

- `linear_access_gap = accuracy(NATIVE,LINEAR) - accuracy(CUBIC,LINEAR)`;
- `repair_residual = accuracy(NATIVE,LINEAR) - accuracy(REPAIRED,LINEAR)`;
- `forest_representation_gap_20/200 = accuracy(NATIVE,FOREST) - accuracy(CUBIC,FOREST)`;
- `capacity_gain_on_cubic = accuracy(CUBIC,FOREST_200) - accuracy(CUBIC,LINEAR)`;
- lossy-control accuracy for all mechanisms.

Use fold as the paired experimental unit and report all five fold values; no item-level pseudo-replication.

## Frozen terminals

### Same-information validity

`P9_REAL_SAME_INFORMATION_VALID` iff every fold/dataset reconstructs `NATIVE` from `CUBIC` through `REPAIRED` with max absolute error <= `1e-10`.

### Accessibility positive

`P9_REAL_ACCESSIBILITY_EFFECT_OBSERVED` iff at least one dataset has mean `linear_access_gap >= 0.02` and its paired fold mean gap is positive.

### Repair positive

For every dataset with mean linear gap >= `0.01`, `REPAIRED` must recover at least 90% of the gap and finish within absolute mean accuracy `0.01` of `NATIVE` linear accuracy.

### Access-mechanism attack

Report whether `FOREST_200` reduces the absolute native-vs-cubic representation gap relative to `LINEAR`. This is diagnostic, not required to be positive.

### Combined terminal

`P9_REAL_ACCESSIBILITY_SCALING_V1_SUPPORTED` requires same-information validity + accessibility positive + repair positive. It does **not** require forests to lose; a forest tie/closure is evidence that accessibility is access-class relative.

If no dataset meets the preregistered `0.02` gap, retain `P9_REAL_ACCESSIBILITY_SCALING_V1_GATE_NOT_MET`; do not change transform powers, seeds, models or threshold.

## Hostile checks

- no train/test scaler leakage;
- cubic transform must remain bijective and reconstruction checked;
- model hyperparameters identical across representations;
- forest seeds identical across representations;
- no result-dependent dataset removal;
- no wall-clock scalar used to claim efficiency;
- `LOSSY` never described as same-information;
- P9 bounded historical results remain unchanged.

## Authority boundary

A positive here establishes a non-synthetic classical-learning accessibility/capacity crossover only. The broad P9 top-tier terminal still requires a second qualitatively different real domain, preferably open-weight procedural/agent and verifier-backed formal/search tasks, plus immediate submission-day literature refresh.
