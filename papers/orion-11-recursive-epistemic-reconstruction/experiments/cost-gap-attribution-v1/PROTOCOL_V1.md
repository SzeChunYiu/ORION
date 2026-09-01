# ORION-11 cost-gap attribution V1 — diagnostic, no new claim

**Protocol id:** `ORION11.COST_GAP_ATTRIBUTION.v1`
**Status:** `DESIGN_FROZEN` — committed before any attribution output was computed.
**Parent:** `NECESSITY_CLAIM_FALSIFIED__COST_OBSERVATION_RETAINED__PACKAGE_OPEN`.

## What is open, precisely

ORION-11's headline necessity claim is **falsified**: the faithful comparator
matches or beats ORION. The freeze retains a **cost observation** and states
explicitly that it is *not attributed* — Theorem C indicates the surviving gap is
donor-owned mathematics rather than an ORION mechanism.

"Unattributed" is the open item. This protocol attributes it. It does **not**
attempt to revive the falsified necessity claim, and cannot: no output of this
study can convert `NECESSITY_CLAIM_FALSIFIED` into a pending success.

## Data — frozen, already collected

`experiments/costed-ordering-v1/` — `raw_traces.jsonl.gz`, `RESULT_V1.json`,
2,882 worlds, `budget_ceiling` 4.0, eight arms with `per_stratum` breakdowns.
No new data is generated. Nothing is re-run.

## Pre-declared decomposition

For each arm, decompose `mean_total_cost` into:

1. **stratum composition** — cost attributable to the mix of world strata an arm
   ends up on, holding per-stratum cost fixed;
2. **within-stratum ordering** — cost attributable to the arm's ordering decisions
   inside a stratum, holding composition fixed;
3. **budget truncation** — contribution of `budget_truncated_rows`, which differ
   sharply across arms (0 for `exact_dp_oracle` and `faithful_active_voi`, 346 for
   `cost_greedy_repair`, 161 for `gain_per_cost_greedy`).

A standard two-way decomposition, computed both orderings and reported as a range
rather than a single attribution, so the answer does not depend on decomposition
order.

## Pre-declared reporting rule

Every arm is reported. No arm is selected after seeing the decomposition. The
three components are reported per arm with the residual shown explicitly; a
decomposition whose residual exceeds 10% of `mean_total_cost` for any arm is
reported as `ATTRIBUTION_INCOMPLETE` for that arm rather than rounded away.

## Terminals

- `COST_GAP_ATTRIBUTED_TO_DONOR_MATH` — the gap is explained predominantly by
  stratum composition and truncation, i.e. by what the donor construction hands
  each arm, consistent with Theorem C.
- `COST_GAP_ATTRIBUTED_TO_ORDERING` — the gap is explained predominantly by
  within-stratum ordering, i.e. by an ORION-side mechanism. **This would be a
  finding against the current freeze text** and must be reported as such, not
  softened.
- `COST_GAP_MIXED__NO_DOMINANT_SOURCE` — neither component dominates.
- `ATTRIBUTION_INCOMPLETE` — residual too large on one or more arms.

## Authority

`scientific_authority_delta: NONE`. Diagnostic attribution of an already-recorded
observation on already-collected frozen data. Grants no claim, does not alter
ORION-11's falsified terminal, and does not touch its `journal_package/`.
