# P11 donor-complete compiler comparator protocol V1

**Programme:** #977  
**State:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** close the donor-complete baseline gate registered in
`P11_NEAREST_WORK_REFRESH_2026-08-23.md` (donor D5) by racing the registered
learned compiler against the named donor's selection principle at matched
charged compiler work, under the same protected evaluation as
`P11_REAL_LEARNED_COMPILER_PROTOCOL_V1`.

## Named donor

D5 — *Learning to Maximize Mutual Information for Dynamic Feature Selection*
(arXiv:2301.00557, ICML 2023). The donor's core instrument is mutual-information
feature scoring. This study adopts the donor's selection principle
(`mutual_info_classif` with a deterministic fold-seeded estimator) as a compiler
arm at the SAME frozen k as the registered compiler, on the same protected
folds, with the same downstream decoder. It does not reimplement the donor's
full interactive pipeline; the frozen comparison isolates the selection
principle at matched charged work, which is the quantity the placement claim
depends on.

## Protected evaluation (identical to the frozen parent study)

- breast cancer (k=15 of 30), wine (k=7 of 13), digits (k=32 of 64);
- `StratifiedKFold(n_splits=5, shuffle=True, random_state=20261101 + dataset_index)`;
- `StandardScaler` fit on the training fold only;
- logistic downstream `C=1.0, lbfgs, max_iter=5000`;
- model/compiler seed `2026110100 + dataset_index*100 + fold_index`;
- resource-vector semantics per `papers/candidates/RESOURCE_LOCATION_SEMANTICS_V1.md`.

## Arms

The four registered arms (`UNIVERSAL_LINEAR`, `COMPILED_LINEAR`,
`UNIVERSAL_FOREST`, `COMPILED_FOREST`, with f_classif selection) are reproduced
through the identical code path and seeds. Two comparator arms are added:

1. `DONOR_MI_COMPILED_LINEAR` — `SelectKBest(partial(mutual_info_classif,
   random_state=fold_seed), k=k)` fit on the scaled training fold; identical
   downstream logistic. This is the named-donor selection principle.
2. `RANDOM_K_COMPILED_LINEAR` — uniform random k-subset per fold
   (`np.random.default_rng(fold_seed)`); identical downstream logistic. Cheap
   control: a placement result that a random selector also passes would not
   evidence a learned-compiler effect.

## Charged compiler work

Both learned selectors are charged the identical parent formula
`n_train * d` per fold (`compiler_fit_proxy`). The donor arm additionally
records `mi_estimator_calls = d` and `mi_nn_distance_evals_proxy = d * n_train`
— MI estimation is charged, never free. The random control is charged the same
`n_train * d` formula (its scoring is trivial but it still inspects the matrix).

## Frozen placement predicate (per compiled arm)

Identical to the parent study: an arm is placement-positive on a dataset iff

- `mean(acc_compiled) >= mean(acc_UNIVERSAL_LINEAR) - 0.02`, and
- compiled state dimension `<= 0.6 *` universal dimension, and
- compiled coefficient count `<= 0.65 *` universal coefficient count.

## Endpoints

- **EP1 reproduction** — the four registered arms must reproduce the bound
  parent result exactly: `positive_datasets == ["wine", "digits"]`, terminal
  `P11_REAL_LEARNED_COMPILER_V1_SUPPORTED`. Any drift is a hard failure, not a
  re-tuning opportunity.
- **EP2 donor disposition** per dataset over
  {`CHALLENGER_BELOW`, `CHALLENGER_ABOVE`, `BOTH_PASS`, `BOTH_FAIL`}, comparing
  the donor arm's placement verdict to the registered compiler's, plus an
  accuracy-parity descriptor `|Δacc| <= 0.01`.
- **EP3 random-control disposition** — same vocabulary for the random arm.
- **EP4 resource parity** — per (dataset, fold): the three selectors' charged
  `compiler_fit_proxy` values are equal; MI charged fields present and
  non-negative.

## Pre-registered predictions (binding record, not gates)

- breast_cancer: donor `BOTH_FAIL` (medium confidence), random `BOTH_FAIL`.
- wine: donor `BOTH_PASS` (medium), random `CHALLENGER_BELOW` (medium-high).
- digits: both withheld (`CANNOT_CHECK_PREDICTION` — MI selection over 64
  pixel features is genuinely uncertain).

Predictions are recorded in the receipt as `CONFIRMED` / `CORRECTED` /
`WITHHELD`; `CORRECTED` is a first-class outcome and never triggers re-tuning.

## Terminals

- `P11_DONOR_COMPARATOR_V1_SUPPORTED` — EP1 reproduced, EP2/EP3 computed for
  every dataset, EP4 verified on every fold.
- `P11_DONOR_COMPARATOR_V1_GATE_NOT_MET` — otherwise.

No cell may be re-tuned after execution. Negative and challenger-below
outcomes are binding boundaries of the placement claim, reported as such.