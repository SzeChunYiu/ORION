# ORION-08 real-domain transfer on Defects4J — protocol V1

**Committed before the runner produced any outcome.**

## Why a second leg, and why this one

#1701 asks for **two** structurally different decision families, not one dataset
family twice:

> Use E3 Defects4J for selective testing/revalidation decisions.
> Use E2 OpenML-CC18 for a second structurally different decision family where
> actions/utilities can be frozen objectively.

The CC18 leg is tabular classification: the action is a label and the utility is a
cost matrix over that label. This leg is a **selection** decision: given a change,
choose which test class to revalidate. Nothing about the mechanism is shared with
CC18 except the theorem being tested, which is the point of asking for two.

## Data

Defects4J metadata, fetched from `rjust/defects4j` at a pinned commit recorded in
the receipt. No Java toolchain and no test execution: only the project metadata,
which is sufficient because the ground truth needed here is *which test classes
catch which bug*, and that is what `trigger_tests` records.

Per bug: `modified_classes/<id>.src` (what changed), `trigger_tests/<id>` (which
tests fail on the buggy revision), `relevant_tests/<id>` (which tests touch the
modified code).

## The decision, frozen before outcomes

For each `(bug, candidate test class)` pair the action is `{run, skip}`. The
utility is frozen here and not tuned:

```
utility(run,  catches)     = +1        a caught regression
utility(run,  catches not) = -0.05     the cost of running a test class
utility(skip, catches)     = -1        a regression shipped
utility(skip, catches not) =  0
```

`catches` means the test class contains a trigger test for that bug. The cost of a
run is deliberately far below the cost of a miss, because that is the real economics
of revalidation, and it is fixed before any fibre is scored. Under this matrix the
optimal action for a fibre is `run` iff `P(catches | fibre) > 0.05/2.05 ≈ 0.0244`.

## Bindings, frozen before outcomes

- **coarse** — the Java package of the first modified class, truncated to three
  segments (e.g. `org.apache.commons`), paired with the candidate test class's
  own three-segment package.
- **refined / typed** — the same, with the full modified class name and full test
  class name. A strict refinement by construction.

Both are computed from metadata only. No feature is selected after an outcome.

## Prediction and strata

Exactly as the CC18 leg, and for the same reason: the prediction is computed from
a training half alone — whether any positive-mass coarse fibre is action-impure —
and datasets are reported in a **value** and a **no-value** stratum. Projects are
the unit. At least one project must land in each stratum or the terminal is
`CANNOT_CHECK_NO_CONTRAST`.

"Positive mass" means at least one row, matching the measurement, because a
threshold applied to the prediction but not the regret measurement manufactures
contradictions out of fibres the predictor never examined. That error was made and
corrected on the CC18 leg and is not repeated here.

The theorem is scored **in-sample**, on the empirical distribution its fibres are
defined on. Out-of-sample transfer is reported separately and is a different
claim; conflating them was the other error corrected on the CC18 leg.

## Arms

`coarse`, `refined_typed`, `run_all` (revalidate everything — the safe, expensive
baseline), `relevant_only` (Defects4J's own `relevant_tests`, the domain's
standard heuristic and the strongest non-theoretical competitor), and `oracle`.

`relevant_only` matters: if it matches the typed binding, the theorem's criterion
is not doing work the domain's existing practice does not already do.

## Terminals

- `THEOREM_PREDICTS_REAL_TRANSFER_D4J` — prediction matches observed direction in
  both strata.
- `THEOREM_FAILS_ON_REAL_DATA_D4J` — any project contradicts it, recorded with the
  fibre and not rescued by re-binning.
- `CANNOT_CHECK_NO_CONTRAST` — a stratum is empty.

A pass makes real-domain transfer supported on **both** legs. It does not make the
typed binding a good selective-testing method; the CC18 leg already found it is
beaten out-of-sample by a generic heuristic, and `relevant_only` is here to test
whether the same holds in this domain.
