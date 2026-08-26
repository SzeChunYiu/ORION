# P13 real responsibility-shift protocol V1

**Programme:** #977  
**State:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** test responsibility-carrying state on a non-synthetic real dataset with a genuine change in required responsibility.

## Dataset

Use scikit-learn `load_digits` handwritten digits. Five-fold stratified CV, shuffled with seed `20261301`.

Fit `StandardScaler` on training fold only.

## State construction

From the 64-dimensional standardized image state `x`, train a logistic parity classifier on training labels transformed to

`PARITY = digit mod 2`.

The compact state stored for later reuse is exactly the two parity class probabilities plus provenance/compiler metadata. The compact numerical payload therefore has dimension `2`; raw image state has dimension `64`.

The compact compiler sees training labels only. Test labels remain protected.

## Responsibilities

Every protected test item is evaluated under two later responsibilities, producing paired responsibility episodes:

1. `R_PARITY` — return even/odd;
2. `R_DIGIT` — return the exact digit identity 0–9.

The responsibility contract for the compact state registers **only `R_PARITY`**. `R_DIGIT` is prospectively unsupported and requires raw-state reopen.

This is a real responsibility change on the same source state; it is not inferred after observing failures.

## Downstream models

- parity from compact state: `argmax` parity probability;
- digit from raw state: logistic regression over all standardized 64 coordinates, `C=1`, `lbfgs`, `max_iter=5000`;
- digit-from-compact hostile decoder: logistic regression trained on the two compact parity probabilities to predict digit identity.

The hostile decoder is given first right of refusal; if two-dimensional compact state happens to support exact digit identity well, that weakens the debt.

## Reuse policies

### UNQUALIFIED

Reuse compact state for every responsibility. For `R_DIGIT`, use the trained hostile digit-from-compact decoder.

### CONFIDENCE_ONLY

If maximum parity probability >= `0.90`, reuse compact state regardless of responsibility. Otherwise reopen raw state. This is a strong control for high-confidence but responsibility-blind reuse.

### PROVENANCE_ONLY

The compact state is current and correctly provenanced in all episodes, so provenance-only policy reuses it for both responsibilities.

### ALWAYS_RAW

Always reopen/use the 64-dimensional raw state. It is the safety ceiling and cost-heavy baseline.

### RCS

Read the registered responsibility contract. Reuse compact state for `R_PARITY`; reopen raw state for `R_DIGIT`.

## Resource accounting

Per responsibility episode count:

- compact numerical state read: `2` floats;
- raw state read/reopen: `64` floats;
- model coefficient count used for the decision;
- reopen event count.

The initial parity compiler/model training cost is reported separately and never treated as free. Since all reuse policies share the same already-constructed compact state, the headline reuse comparison concerns post-construction responsibility-service cost.

No wall-time scalar is used.

## Primary outcomes

- `unsupported_reuse_rate`: fraction of `R_DIGIT` episodes served from compact state despite the frozen contract;
- parity accuracy;
- digit accuracy;
- combined episode accuracy;
- mean floats read per responsibility episode;
- reopen rate;
- compact hostile digit-decoder accuracy.

## Frozen positive terminal

`P13_REAL_RESPONSIBILITY_SHIFT_V1_SUPPORTED` requires:

1. RCS unsupported-reuse rate `0`;
2. RCS digit accuracy equals ALWAYS_RAW digit accuracy fold-by-fold because both use the same frozen raw digit model;
3. RCS parity accuracy equals UNQUALIFIED compact parity accuracy fold-by-fold;
4. RCS mean state floats read per episode is at least `40%` lower than ALWAYS_RAW;
5. CONFIDENCE_ONLY or PROVENANCE_ONLY performs at least one unsupported compact reuse on `R_DIGIT`;
6. hostile digit-from-compact mean accuracy is at least `0.15` below raw digit mean accuracy, demonstrating material responsibility debt on this state.

If item 6 fails, retain the result as evidence that this compact state happened to support more responsibility than expected; do not retune state dimension or confidence threshold.

## Approximate support calibration

In addition to task accuracy, report the fold-level parity error rate and the Hoeffding upper bound from T13.3 using frozen `alpha=0.05`. This does not certify universal parity support; it reports calibrated risk under the protected fold distribution.

## Hostile checks

- compact state contains only parity probabilities, not digit logits/labels;
- scaler/parity compiler/digit models fit only on training fold;
- confidence threshold frozen at `0.90`;
- provenance is identical across policies;
- RCS cannot use raw state on parity episodes merely to improve accuracy;
- ALWAYS_RAW cannot avoid its raw-read cost;
- unsupported reuse is measured from the prospective responsibility contract, not defined after errors;
- all five folds and all digits remain reported.

## Authority boundary

A positive establishes a non-synthetic real responsibility-shift/safety-cost result on handwritten digits. The broad top-tier P13 claim still requires a verifier-backed or agent/research workflow, real semantic/version transport of certificates, independent external validation and submission-day donor refresh.
