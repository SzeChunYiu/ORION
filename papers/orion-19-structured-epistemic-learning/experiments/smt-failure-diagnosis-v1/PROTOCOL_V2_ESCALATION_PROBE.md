# ORION-19 successor V2 — an architecture-independent diagnosis feature

**Committed before the V2 runner exists and before any V2 outcome is computed.**
V1's record is not edited. Its terminal, its arms and its numbers stand.

## What V1 found that makes this necessary

V1's `resource_vector` uses **conflict count**, and V1 established its failure
mechanism rather than merely noting a miss: conflict count measures
*conflict-driven* search, so it is blind wherever the solver does not use it.
z3 solves nonlinear integer arithmetic by a route that is not conflict-driven,
so the entire factoring family's accessibility-deficient instances burn a full
budget while accruing 5, 6 and 11 conflicts — indistinguishable from compute
starvation. Family accuracy there is 0.727 against 1.000 elsewhere.

No threshold repairs that. The feature inherits the solver's architecture.

## The V2 feature, frozen here

**A budget-escalation probe.** Re-run the failing instance at **2× the budget it
failed under** and read the verdict:

- verdict `sat` at the original budget → `INFORMATION` (unchanged from V1);
- otherwise, if the 2× run **resolves** (`sat` or `unsat`) → `COMPUTE`: more time
  demonstrably helped;
- otherwise → `ACCESSIBILITY`: more time demonstrably did not.

This asks the question the diagnosis is actually about — *does compute help?* —
instead of a proxy for it. It reads no solver statistic and so cannot inherit a
solver's architecture.

## The cost, which is the point and not a footnote

The probe **spends compute to decide whether to spend compute**, which is
self-undermining if unpriced. V1's arms each spent one probe at the original
budget; this arm spends one at twice it.

Total solver seconds per arm are therefore a **reported endpoint, not diagnostic
colour**, and the comparison is explicitly two-dimensional: an arm that buys
accuracy with compute must be shown to buy it cheaply enough to be worth it
against `always_compute`, which spends nothing to decide and is wrong on every
non-compute failure.

## Arms

`always_compute`, `verdict_only`, `resource_vector` (V1's, unchanged, as the
comparator this successor must beat), `escalation_probe`, `oracle`.

## Instances

The V1 instance set exactly — same families, same parameters, same construction,
same exclusion rule. Changing the instances and the feature together would leave
the comparison uninterpretable.

## Scoring

**All instances, not a split.** V1's held-out half scored 0.0000 false escalation
only because all three blind-spot cases landed in development, and this successor
exists because of that. A split that can hide the effect under test is the wrong
instrument here. `escalation_probe` has no fitted threshold, so there is nothing a
development half would protect against; `resource_vector` reuses V1's
dev-fitted threshold unchanged, so it is not refitted on the data it is scored on.

## Terminals

- `ESCALATION_PROBE_SUPPORTED` — strictly lower false compute escalation than
  `resource_vector` on all instances, **and** no worse on the factoring family,
  **and** its extra solver seconds reported.
- `ESCALATION_PROBE_NOT_SUPPORTED` — otherwise, recorded with the confusion matrix.
- `CANNOT_CHECK_NO_SEPARATION` — if doubling the budget resolves nothing anywhere,
  the probe carries no signal and the design has no power.

A pass says a direct escalation test diagnoses better than a solver statistic on
these constructed instances, at a stated compute price. It does not make either
feature correct on naturally-occurring instances.
