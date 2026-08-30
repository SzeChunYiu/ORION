# ORION-22 regret-floor transfer to Defects4J — protocol V1

**Committed before the runner exists and before any outcome is computed.**

## What is being transferred

The Wave-2 result is an *exact* law, not an average: 36 alias classes, 23 with
positive forced regret, a maximum class floor of 700 and a total forced regret of
5,092, with refinement closing the floor. #1701 asks whether that law transfers to
a structurally different decision family.

It is the exactness that has to survive. A mean regret that goes down is not the
claim; the claim is that when an observation aliases several true states, the
single action the observer is forced to take leaves a *countable* number of
decisions wrong, and that number is predictable and is reduced by refinement.

## Family choice, fixed here

**E3 Defects4J.** #1701 says choose one before protocol freeze; this is the
choice, and E2 OpenML is not used in this study.

Defects4J metadata is already fetched and digest-recorded for the ORION-08 leg
(`papers/orion-08-typed-state/experiments/real-transfer-defects4j-v1`). The same
bytes are reused; the decision built on them is not.

## Why this is not the ORION-08 decision again

ORION-08's Defects4J leg asks, for each `(change, test)` pair, whether to run that
test — a binary action per pair, scored by a utility matrix, with regret averaged
over rows. This study asks a different question on the same corpus: given a
change, **choose exactly one test package to schedule**. The action set is the set
of test packages, the utility is integer, and the regret is a count of decisions
forced wrong by aliasing rather than an average. Neither the action space, the
utility, nor the estimand is shared.

## The decision

- **True state**: one bug. Its native oracle action is any test package containing
  one of its trigger tests. Bugs with no trigger test inside the project's test
  universe are excluded before outcomes and their count is reported.
- **Observation (alias class)**: the package of the bug's first modified class.
  This is what a scheduler sees when a change lands and before any test has run.
- **Action**: one test package, drawn from the project's test packages.
- **Utility**: 1 if the scheduled package contains a trigger test for that bug,
  else 0. Integer, and frozen here.

**Forced regret of an alias class** = `|class| − max over packages of the number
of bugs in the class that package catches`. This is exact and requires no
estimation: it is the number of bugs in the class that any single action must get
wrong.

## Refinement

One refinement, fixed here: alias class `package(modified class)` refines to
`(package(modified class), simple name of the modified class)`. The theorem's
expectation is that the total floor is non-increasing and strictly decreases on
exactly those classes whose members disagree about the best action.

## Prediction before protected evaluation

Bugs are split into a **prediction half** and a **protected half** by a fixed
seed (`20260830`). On the prediction half alone, and written to the receipt before
the protected half is touched:

1. the total forced regret, the number of positive-regret classes and the maximum
   class floor;
2. the predicted **floor rate** per class, `floor / |class|`, carried to the
   protected half's class sizes to give a predicted protected total;
3. the predicted reduction from the single refinement.

Then the protected half is scored once. Predictions are not revised.

## Arms

`coarse` (one action per alias class), `refined`, `strongest heuristic` — schedule
the test package whose name best matches the modified class's package, a rule that
uses no outcome statistics — and `oracle` (per-bug best action, regret 0).

## Required contrast

Both a **zero-regret** and a **positive-regret** alias class must exist, or the
terminal is `CANNOT_CHECK_NO_CONTRAST`. A family in which every class is forced
wrong somewhere, or none is, does not test a law about which classes carry a
floor.

## Terminals

- `REGRET_FLOOR_LAW_TRANSFERS` — the protected total lies within the predicted
  interval, refinement is non-increasing everywhere and strictly decreases exactly
  on the disagreeing classes.
- `REGRET_FLOOR_LAW_FAILS_ON_D4J` — any of those fails, recorded with the class
  and the margin, and not rescued by re-aliasing.
- `CANNOT_CHECK_NO_CONTRAST` — as above.

A pass transfers an exact aliasing law to one further decision family. It does not
establish the law for arbitrary observation channels, and it says nothing about
whether scheduling one test package is a good way to revalidate software.
