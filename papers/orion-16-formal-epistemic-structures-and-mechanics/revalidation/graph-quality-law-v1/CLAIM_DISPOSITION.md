# Claim disposition — ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION.v1

Protocol and theory frozen at `fa1886a72` before verification ran.
Terminal: **T1_GRAPH_QUALITY_LAW_HOLDS**.
Promotion status: **GENERAL_THEOREM_ESTABLISHED__PROMOTION_NOT_EARNED__BOUNDED_PAPER_RETAINED**.

## Result

| claim | violations |
|---|---|
| N1 monotonicity | **0** |
| N2 over-approximation sound, extra work localised to added-edge heads | **0** |
| N3 wrongly-retained set equals the missing-path set | **0** |
| N4 no nonnegative weighting beats the affected closure | **0** |

Exhaustive over DAGs on 3–5 nodes, every change set, and over- and under-approximations in
both directions.

## Coverage was not degenerate

An exhaustive sweep proves nothing if every case is trivial, so the protocol required
non-degenerate instances and counted them:

- **119,038** strict over-approximations with *positive* extra work
- **310,002** strict under-approximations with a *nonempty* wrongly-retained set
- **559,233** N3 comparisons, each a **set equality** against an independently computed
  wrongly-retained set rather than containment in one direction
- **310,002 / 310,002** planted unsound cases caught by the same soundness predicate the
  real search uses — so "no unsound over-approximation found" is distinguishable from a
  predicate that cannot fire
- **32,760 / 32,760** zero-weighting cases correctly *not* alarmed

## What the law says

Graph **quality**, not weighting, determines both cost and safety.

- Over-approximation is always sound, and conservative edges cost only reachability from
  their heads — not a global penalty (N2).
- Under-approximation fails **exactly** on nodes whose every true path from the change set
  runs through a missing edge. A missing edge bypassed by another path costs nothing (N3).
- **N4 inverts the brief.** "Cost-optimal revalidation under weighted obligations" suggests
  a weighting to tune. There is none: every proper subset of the affected closure is
  unsound, so any sound set contains it and no nonnegative weighting can do better. Cost
  optimisation has no freedom left, and all achievable savings come from graph quality.

## The real-system evidence — retrospective, licensing nothing

`revalidation/P6_REVALIDATION_COMPARISON_V1.json` records `outcome_accessed: true`. Its
numbers were read before this theory was authored, so **no frozen test was run against them
and none is reported as evidence.**

As a labelled consistency observation only: `selective` retains 74.87% / 84.90% / 89.33%
on numpy / scipy / flask with **zero** invalid retentions, while `native-dep` wrongly
retains 28,709 and 51,353. That is the shape N2 and N3 describe — Python import graphs are
a *superset* of true semantic dependencies, so a closure taken over them is the
over-approximation case and is sound by N2, while a narrower neighbour-based policy is the
under-approximation case and fails by N3. This observation **evidences nothing**; it is
recorded because omitting it would be less honest than labelling it.

## Why promotion is not earned

#1649's stop rule: *if real dependency extraction cannot be made authoritative, keep the
general theorem [as a] bounded paper; do not manufacture deployed-system claims.*

Import graphs are over-approximate by construction, so extraction **cannot certify `G*`**
— it certifies a `G' ⊇ G*`. The premise the stop rule guards against is exactly the one
that fails here, and it was recorded in `PROTOCOL.json` before verification ran rather than
after. ORION-16 stays in the bounded lane and **no deployed-system claim is made on any
outcome**.

## Authority

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission authority.
Nothing frozen is retracted; `DEPENDENCY_CLOSED_REVALIDATION.v1` and the P6 comparison
stand exactly as they are. Outcomes were read once.
