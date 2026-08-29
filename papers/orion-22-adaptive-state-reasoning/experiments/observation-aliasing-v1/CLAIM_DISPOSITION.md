# Claim disposition — ORION22.OBSERVATION_ALIASING_ROBUSTNESS.v1

Protocol frozen at `cba3ad9c6` before any outcome was read. Result at `RESULT_V1.json`.
Terminal reached: **T2_SOME_PRICE_BLIND_CLASSES_EMPTY__PRICE_REFINEMENT_RESOLVES_ALL**.

## What was asked

`robustness_boundary_leaf` records `price_axis: BROKEN` and `distribution_shift_axis: BROKEN`
with `retuned: false`. Two readings of that negative were live, and they carry very
different consequences:

- **policy failure** — the frozen allocator was a poor rule on an adequate surface, so a
  better rule on the same surface would fix it;
- **information failure** — the surface itself does not determine the optimal action, so
  *no* rule on it can be zero-regret.

The successor theory in #1615 Priority 3 supplies a criterion that separates these: a
deterministic observation-based zero-regret policy `pi: Z -> A` exists **iff** for every
observation class `z`, the intersection over `{e : h(e) = z}` of `O(e)` is nonempty.

## What was measured

Under the price-blind surface, the five regimes of a case differ only in the price vector,
which is not readable; so each case is a single observation class containing five
environments.

| | |
|---|---|
| observation classes | 36 |
| classes with an **empty** common optimum | **23 (63.9%)** |
| classes with a nonempty common optimum | 13 |

For 23 of 36 cases there is **no allocation that is optimal in all five regimes**.

`SAT_T3_BUDGET_RACE` is representative: per-regime optima 332 / 378 / 470 / 618 / 1160
across FLAT / MEM2X / MEM4X / CMP2X / CMP4X, with no single budget-feasible allocation
attaining all five.

## Disposition

The ORION-22 robustness negative is an **information boundary**, not a policy defect. On
64% of the frozen family, `price_axis: BROKEN` could not have been repaired by choosing a
different price-blind rule, because the criterion's necessary condition fails. This does
not retract the negative; it explains it, and it converts an observed defect into a
statement about what the surface can support.

It also explains, rather than merely records, why `P12_PRICE_AWARE_SUCCESSOR_V1` reaches
0 positive-regret cells in every regime with **zero new free parameters**. Making
`(p_build, p_serve)` readable splits each aliased class into per-regime singletons, whose
intersections are nonempty by construction. The successor did not out-tune the frozen
allocator; it moved to a surface on which a zero-regret policy exists at all. Under the
criterion, its success was the predicted outcome.

## Controls

All four fired before the finding was read.

- **Pool integrity** — the five pinned hashes in `frozen_pool_unchanged` were resolved to
  files by content, not by guessed filename. An early apparent mismatch was my own wrong
  guess (`v1_cases_sha256` is `p12_transfer_cases_v1.json`); resolving by hash showed the
  pool intact.
- **`O(e)` non-emptiness** — an empty optimum set exits 3 as CANNOT_CHECK rather than
  being silently counted as an empty intersection.
- **Singleton class** — a class with one environment must have a nonempty intersection;
  one reported empty is an analyzer defect and exits 3. Vacuous here (0 singleton classes
  under this surface) and correctly non-firing.
- **Tie completeness** — `O(e)` collects **every** optimal allocation. Recording one
  tie-broken argmin would make every intersection a singleton and fabricate T1. This is
  the control that decides whether the result means anything.

## Limits

36 classes over the two committed pools; some case ids appear in both `v1` and `expanded`
and are counted separately, because they are separate environments. The criterion is
evaluated on this frozen family and is not a claim about arbitrary charging environments.
The price-aware arm is settled by construction rather than by enumeration, and
`RESULT_V1.json` says so in `price_aware_surface_note` rather than reporting it as a
measured contrast.

## Authority

`MEASUREMENT_ONLY`. `scientific_authority_delta: NONE`. No submission authority. The
`BINDING_NEGATIVE_BOUNDARY` leaf and the `P12_ROBUSTNESS_STRESS_V1_EXECUTED` terminal
stand unchanged.

Per the frozen stop rule, outcomes were read once. T2 was reached, so the lane closes here
and is not re-run under a different surface.
