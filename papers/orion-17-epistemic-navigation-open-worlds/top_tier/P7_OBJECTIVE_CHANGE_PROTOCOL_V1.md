# ORION-17 real objective-change transport protocol V1

**Programme:** #977  
**Purpose:** complete the third non-synthetic regime-change class with a real observed-data objective/obligation change after predictions have already been produced.

## Development-to-protected chronology

The dataset is the Wisconsin Diagnostic Breast Cancer data bundled by scikit-learn. Development folds with `StratifiedKFold(n_splits=5, shuffle=True, random_state=20261207)` are used only to choose a scientifically interpretable changed obligation. No protected result from the seed below is inspected before this protocol is committed.

Protected folds are frozen at:

`StratifiedKFold(n_splits=5, shuffle=True, random_state=20261217)`.

The model is fixed for every fold:

- training-fold `StandardScaler`;
- `LogisticRegression(C=1, solver=lbfgs, max_iter=5000)`;
- no threshold tuning or refit after the objective change.

## Regime transition

### Old scientific responsibility

The original evidence summary asks only whether test accuracy is at least `0.95`.

### Changed scientific responsibility

After predictions are frozen, the obligation changes to:

> malignant-class recall must be at least `0.95`.

In the scikit-learn dataset malignant is target class `0`.

The change is deliberately scientific/operational rather than representational: the same predictions are being assessed under a different obligation.

## Evidence witnesses

For each protected fold create two evidence states from the identical predictions.

### FULL_CLASS_WITNESS

Retain the complete 2x2 confusion counts, overall accuracy and class-conditioned recall. The new obligation is decidable without recollecting data.

Disposition:

- `PRESERVE` if malignant recall >= 0.95;
- `REOPEN` otherwise.

### ACCURACY_ONLY

Retain only sample count, correct count and overall accuracy. No class-conditioned counts or labels remain.

Disposition: `CANNOT_CHECK` under the changed obligation, even when the old accuracy obligation was satisfied.

No candidate may infer malignant recall from aggregate accuracy.

## Comparators

1. `VALUE_ONLY`: if the old accuracy obligation was satisfied, declare `PRESERVE` after the objective change.
2. `ALWAYS_REOPEN`: declare `REOPEN` for every fold/evidence state.
3. `WITNESS_AWARE`: apply the evidence-state semantics above.

All comparators receive the same retained evidence object for that cell.

## Endpoints

- exact changed-obligation disposition accuracy;
- false closure under objective change;
- unnecessary reopen of a fully witnessed valid transition;
- correct `CANNOT_CHECK` on accuracy-only summaries;
- count of full-witness `PRESERVE` and `REOPEN` folds;
- deterministic replay;
- second implementation agreement.

## Positive terminal

`P7_OBJECTIVE_CHANGE_TRANSPORT_V1_SUPPORTED` requires:

- all five protected folds reported in both evidence-state conditions (`10` cells);
- at least one full-witness `PRESERVE` and at least one full-witness `REOPEN` fold;
- WITNESS_AWARE exact accuracy `1.0`;
- WITNESS_AWARE correct `CANNOT_CHECK` on all five accuracy-only cells;
- VALUE_ONLY makes at least one false-closure decision;
- ALWAYS_REOPEN makes at least one unnecessary-reopen decision;
- the predictions/evidence facts are deterministic and both implementations agree.

This result tests objective/obligation transport only. It does not claim a new classifier or medical decision rule, and no clinical use is implied.
