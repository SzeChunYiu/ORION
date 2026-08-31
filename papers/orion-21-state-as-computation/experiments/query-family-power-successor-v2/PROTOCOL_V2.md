# ORION-21 query-family capability successor protocol V2

**Parent:** `P11_QUERY_FAMILY_PHASE_PROTOCOL_V1.md`, terminal
`P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET` (LINEAR 3/10, RBF 5/10, KNN 5/10
against a frozen `>=8/10` gate).

## Chronology

This protocol and its runner are committed before any V2 outcome exists. It does
**not** retune, replace or rescue the V1 gate. The V1 negative remains
authoritative and its terminal is unchanged by anything here.

## Why a successor is warranted, and what it may not do

`GATE_DESIGN_POWER_V1` established two things at once. The V1 miss is *not* an
n=10 artefact: every arm's exact interval lies below the capability the `>=8/10`
gate is powered to detect, so the preregistered capability level is genuinely
excluded. But capability anywhere in the **0.6-0.8 band is not excluded**, and
across that band the gate's power is only 17-68%. The V1 design can therefore say
"below the registered bar" and cannot say where below.

That residual is an estimation problem, not a gate problem. So V2 asks a
different question from V1:

> **V1 asked:** does family-scale capability clear `>=8/10`?  Answered: no.
> **V2 asks:** what *is* family-scale capability, estimated with enough
> responsibilities to resolve the 0.6-0.8 band?

V2 is an estimation study and declares **no pass/fail gate of its own**. It
cannot convert the V1 negative into a positive, and no outcome here authorises a
placement claim that V1 refused.

## What is held fixed

Everything mechanical is inherited verbatim from V1 and may not be altered:

- scikit-learn handwritten digits, raw universal state `d=64`;
- `StratifiedKFold(n_splits=5, shuffle=True, random_state=20261121)` over the
  original ten-class labels, all fitting on training folds only;
- compiler: `StandardScaler` then `SelectKBest(f_classif, k=16)` fit on the
  binary training responsibility; compiled state is those 16 standardized
  coordinates; no test label or future-query outcome visible to selection;
- decoders, identical hyperparameters on universal and compiled state:
  `LogisticRegression(C=1, solver=lbfgs, max_iter=5000)`,
  `SVC(C=1, kernel=rbf, gamma=scale)`,
  `KNeighborsClassifier(n_neighbors=7, weights=distance)`;
- quality rule: a responsibility is quality-supported for an access class when
  `compiled_mean >= universal_mean - 0.02` in balanced accuracy.

`k`, the decoder hyperparameters and the `-0.02` rule are frozen. Retuning any of
them after seeing V2 outcomes is forbidden and would void this study.

## The one thing that changes: the query family

V1 froze ten responsibilities `q_j(x) = 1 iff digit(x) == j`. These are exactly
the size-one subsets of the digit alphabet. V2 keeps them and adds the size-two
subsets over the same source state and the same full dataset:

`q_S(x) = 1 iff digit(x) in S`, for every `S` with `|S| = 2`  ->  45 responsibilities.

This is the same kind of object as V1 (a binary responsibility over the same
64-pixel source state, evaluated on all 1,797 examples), so sample size and fold
structure are unchanged. It is a genuine enlargement of the future-query family,
not a different experiment: the V1 family is the `|S|=1` stratum of the V2 family.

Total: **55 responsibilities**, reported as two strata and pooled.

## Stage A -- reproduction, and the right to proceed

The recorded V1 environment is numpy 2.3.2 / scikit-learn 1.7.1; V2 runs on a
different machine and a different scikit-learn. So V2 first re-derives the
`|S|=1` stratum and compares it to the frozen record:

- required: LINEAR **3/10**, RBF **5/10**, KNN **5/10** quality-supported.

If any arm's count differs, the terminal is `REPRO_FAILED` (exit 4), the `|S|=2`
stratum is reported as descriptive only, and no capability estimate carries
authority. An extension of a result that does not reproduce would measure the
environment, not the mechanism.

## Stage B -- estimand and reporting

For each access class, the estimand is the family-scale capability

`theta = P(a responsibility drawn from the family is quality-supported)`,

estimated by the quality-supported fraction with a **Clopper-Pearson 95%
interval**, reported for the `|S|=1` stratum, the `|S|=2` stratum and pooled
(n=55). Responsibilities within a stratum share one dataset and one fold split,
so they are not independent; the interval is reported as a nominal binomial
interval and that dependence is stated rather than modelled away.

Predeclared readings, fixed before outcomes:

- if the pooled interval lies **entirely below 0.6**, capability is sharply
  bounded below the V1 bar and the V1 negative is strengthened, not merely
  repeated;
- if the interval lies **entirely within 0.6-0.8**, the band the V1 design could
  not resolve is resolved, and the result is a regime-conditional capability that
  still fails the V1 bar;
- if the interval **straddles 0.8**, V2 has not resolved the question either and
  the honest terminal is `CANNOT_CHECK_POWER_STILL_INSUFFICIENT`;
- a difference between the `|S|=1` and `|S|=2` strata is itself a finding about
  responsibility structure and is reported whichever way it points.

Every responsibility/fold/access-class cell is reported. No responsibility may be
dropped after outcomes.

## Terminals

- `QUERY_FAMILY_CAPABILITY_ESTIMATED` (exit 0) -- Stage A reproduced and a pooled
  interval is reported for all three access classes;
- `CANNOT_CHECK_POWER_STILL_INSUFFICIENT` (exit 3) -- reproduced, but no interval
  separates the readings above;
- `REPRO_FAILED` (exit 4) -- the `|S|=1` stratum did not reproduce the V1 record.

No terminal here promotes any ORION-21 claim. The paper's active authority
remains `P11_ACTIVE_CLAIM_AUTHORITY_V2.json`.
