# Tier-A baselines are discriminating — a registered shortcut probe, run

**Date:** 2026-09-02 · **Scientific authority delta:** `NONE`. No theorem, bound or terminal
changes. This executes one of ORION-paper#49's registered computations and reports what it found.

## Why this probe exists

A baseline set is a shortcut if two nominally different baselines are extensionally identical,
or if one is constant where it is not meant to be. Either makes a comparison weaker than the
study claims **while every gate still passes**. That is not hypothetical here: A6's ideal-donor
tie gate could not fail, because the candidate and the "information-equivalent ideal donor"
both delegated to one function.

It is decidable with no protected outcome, because each lane's pre-gold input alphabet is finite.

## Result

| lane | records enumerated | collapsed pairs | degenerate |
|---|---|---|---|
| A3 change-transport | 243 | **none** | **none** |
| A4 hidden-cause routers | 480 | **none** | **none** |
| A6 authority (in the sibling repair) | 81 | tie holds vs an independent derivation | 9/81 discriminating |

`ALWAYS_REUSE` and `ALWAYS_REOPEN` are constant **by design** and declared as such; every other
baseline is genuinely multi-valued. The A4 intervention oracle is implemented and correctly
**absent** from the outcome-blind set — it is analysis-only, as registered.

**This is a passing control, and it is reported as one.** A probe only ever run against
defects is a probe nobody has calibrated.

## The probe produced two false positives before it was correct

Both were defects in the probe, caught by reading the source rather than reporting:

1. **Five A4 routers appeared constant** at `METHOD/CANNOT_CHECK`. The synthetic records used
   invented field names. The routers read `task_id`,
   `development_majority_intervention`, `declared_intervention_cost_vectors`,
   `uncertainty_score`, `learned_router_prediction` — not the names guessed for them.
2. **`MAJORITY_DEVELOPMENT` and `LEARNED_ROUTER_DEVELOPMENT_ONLY` appeared collapsed.** The grid
   set the learned prediction equal to the development majority, so they agreed by construction.
   Varying them independently separates them cleanly.

Both are recorded because the second one is the same mistake the A6 gate itself made: two
things look identical when the harness makes them identical. The grid builder now carries that
warning at the point where it would recur.

## Validated against its own failure modes

| mutation | result |
|---|---|
| add a router that clones `compute_first` | **exit 2**, names the collapsed pair |
| expose the intervention oracle in the outcome-blind set | **exit 2** |
| unmutated | exit 0 |
