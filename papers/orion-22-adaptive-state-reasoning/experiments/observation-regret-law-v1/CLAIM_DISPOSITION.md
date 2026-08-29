# Claim disposition — ORION22.OBSERVATION_REGRET_LAW.v1

Protocol and theory frozen at `52b4176c9` before any outcome was read.
Terminal: **T1_REGRET_LAW_HOLDS**.
Promotion status: **SCOPED_QUANTITATIVE_LAW__PROMOTION_NOT_EARNED**.

## Result

| | |
|---|---|
| observation classes | 36 |
| classes with **positive** regret floor | **23** |
| classes with zero floor | 13 |
| maximum forced regret `R*(z)` | **700** |
| total forced regret across the family | **5092** |
| classes where price refinement closes the floor completely | **36 of 36** |

All four predictions hold: the floor is respected, it is attained, its zero set agrees
with the committed record, and refinement closes it exactly.

## What was promoted

`ORION22.OBSERVATION_ALIASING_ROBUSTNESS.v1` found that 23 of 36 price-blind classes have
an empty common-optimum intersection — a **qualitative** boundary saying zero regret is
impossible there.

That boundary is now the **zero level set of a quantity**. `R*(z)`, the minimax regret over
the class, is computed exactly per class: it is `> 0` on precisely the 23 empty classes and
`0` on precisely the 13 nonempty ones. The qualitative result is recovered, not assumed.

And the quantity says how much is at stake, which the qualitative statement could not:
**5092 units of regret are forced** across the family, up to **700** in a single class,
and price refinement closes **all** of it — every class's refined floor is exactly zero.

That also explains `P12_PRICE_AWARE_SUCCESSOR_V1` more sharply than before. Its zero
positive regret at zero new free parameters is not merely consistent with the theory; under
Q3 and Q4 it is **forced**, because refining to per-regime singletons drives every floor to
zero by construction.

## Controls

- **Y2** is the one that matters: the zero set was cross-checked against the
  **already-committed** aliasing record, not against an intersection recomputed here.
  18 committed empty case identities against 18 measured positive-floor identities, exact
  match. Recomputing the intersection myself and finding agreement would have been
  circular — it would have tested this packet against itself.
- **Y1** — a planted sub-floor value is caught by the same comparison P1 uses: **36/36**.
- **Y3** — every singleton sub-class has floor exactly zero: **180/180**.
- **Y4** — pools resolved by content through the committed runner.

## Scope, fixed before any number was read

This is the frozen charging family (`p12_transfer_cases_v1` and the expanded pool). #1649's
stop rule is explicit: *if the law does not transfer beyond the frozen charging family,
retain it as a scoped information-boundary result and stop broadening.*

No multi-domain transfer was attempted and none is claimed. **Promotion is therefore not
earned even on the favourable terminal**, and the result carries that in its own status
field rather than in a footnote.

## Authority

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission authority.
The aliasing terminal and the `BINDING_NEGATIVE_BOUNDARY` leaf are unchanged — this
quantifies the boundary, it does not retract it. Outcomes were read once.
