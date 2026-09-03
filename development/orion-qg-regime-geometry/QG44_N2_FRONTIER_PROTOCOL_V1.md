# QG44 — n=2 witness frontier: genuine geometry vs the t_c = 1 boundary (V1)

> **Provenance (registration note).** This study was first registered as
> "QG23" in (closed) PR #2162, stacked on the "QG22" registration of #2153.
> Both were renumbered (QG-22 slot collision with the hidden-home-state
> study; see the QG-43 provenance note) to **QG-43** / **QG-44**. Machinery,
> grid, panels, gates, terminals, and the frozen seed (20260903) are
> byte-identical modulo the identifier rename (`QG23`->`QG44`,
> `Q23G`->`Q44G`, and the predecessor binding `QG22`->`QG43`); the registered
> outcome is regenerated deterministically against the fresh QG-43 receipt
> (G7). Original registration commit f841abd43b stays visible on the closed
> PR.

## Aim

QG43 established (exhaustive in instances at n=1, 41-objective margin grid) that
the exact support-2 region at n=1 strictly contains the QG8 cone: ZERO n=1
witnesses anywhere, while the same outside objectives carry up to 34 witnesses
from the n=2/3 panels. Witness mass concentrated at margins `dc = -3` under
`t_r = 2` — i.e. exactly where `t_c = 2*t_r + dc = 1`, the absolute
central-cost boundary — with only isolated 2-gap points elsewhere. Two readings
survive: (a) the n=2 region boundary is genuine cone geometry (a frontier in
margin space), or (b) support-3 gaps are an artifact of the degenerate central
cost `t_c = 1`. This study separates them at n=2 and is the direct successor to
QG43's registered open question.

## Frozen machinery (identical to QG43, imported not copied)

`qg2.dp_cost_pairs_ob` (exact unrestricted optimum), `qg2.dxx_cost_ob` (exact
support-`<=2` optimum), `qg2.dp_witness_ob`, `qg2.brute_config_n1_ob`,
`qg2.clear_caches`, `qg2.Objective`. `gap(I,O) = C_DP - C_Dxx`; a **witness**
is `gap < 0` (serialized DP witness then has `max_frame_support > 2`).
Margins `dc = t_c - 2*t_r`, `dnc = t_nc - 2*t_r`; every objective keeps
`t_c >= 1`, `t_nc >= 1`, `t_c <= t_nc`. All costs exact integers; rho = 0,
t_tag = 2 throughout.

## Registered outcome run (single pass, exit 0 = complete)

1. **Objective grid** (13 objectives: 6 `H_main` + 6 `H_scale` + 1 anchor):
   - `H_main` (t_r = 2): `(dc,dnc) in {-3,-2,-1} x {0,1}` -> 6 objectives
     (`t_c = 4+dc`, `t_nc = 4+dnc`). `dc = -3` points have `t_c = 1`
     (witness-mass comparators); `dc = -2` points have `t_c = 2` (the
     witness-free column QG43 could only sample); `dc = -1` shallow controls.
   - `H_scale` (fixed margins, raised t_c): `(dc,dnc,t_r) in
     {(-3,0),(-3,1),(-2,0)} x {3,4}` -> 6 objectives, `t_c in {3,4,5,6}` —
     the same margins as the H_main witness comparators with the absolute
     central cost lifted off 1. ((-3,1) included so the t_c=1 comparator with
     dnc=1 has its raised-t_c pair.)
   - `O1ANCHOR` = frozen QG2 O1 `(7,1,4,3,0)`, margins `(-5,+1)`, `t_c = 1`
     -> 1 objective (gate G6 replay only).
2. **Instance panels**:
   - `P1` EXHAUSTIVE letter-alphabet n=2: all 729 instances with each of the 6
     targets one of `{(1,0),(1,1),(0,1)}` (QG43's n=1 letters, embedded at
     width 2) x the 6 `H_main` objectives. Exact claim scoped to this subclass.
   - `P2` hostile: frozen `r6m._HOSTILE_N1_PANELS` (3) and
     `_HOSTILE_N2_PANELS` (2) x all 11 objectives.
   - `P3` witness continuation: every serialized QG43 witness row (cap 20)
     re-evaluated on all 11 objectives.
   - `P4` discovery (seed 20260903, `numpy.default_rng`, QG43's generator
     verbatim): 600 random n=2 instances x the 12 non-anchor objectives.
3. **Registered questions** (authored before the run):
   - **Q1 (primary):** does any n=2 witness exist at an objective with
     `t_c >= 2` (any panel)? This is the geometry-vs-artifact separator.
     Prediction: YES (QG43's isolated 2-gap points at `dc = -2` had `t_c = 2`)
     — the informative output is the RATE and margin structure, not bare
     existence.
   - **Q2 (frontier density):** per `(dc,dnc,t_c)` cell over P4 (600 seeded
     instances), the exact witness count and the minimum gap; contrast
     `t_c = 1` cells vs raised-`t_c` cells at identical margins (H_main vs
     H_scale).
   - **Q3 (exhaustive subclass):** P1 verdict — zero or nonzero witnesses in
     the letter-subclass at width 2 (exact, scoped).
   - **Q4 (continuation stability):** each QG43 serialized witness, evaluated
     at its own margins with `t_r` raised (t_c 1 -> 3 -> 5 for `dc = -3`;
     2 -> 4 -> 6 for `dc = -2`): does witness status survive the lift?
4. **Gates (hard):**
   - `G1`: `C_DP <= C_Dxx` on every evaluation (assert, abort on violation).
   - `G3`: every serialized witness row has `max_frame_support > 2`.
   - `G4`: independent n=1 brute cross-check (as QG43) at the two most
     witness-bearing n=2-discovered points, on 12 fixed letter instances.
   - `G5`: anti-instrument import gate (as QG43).
   - `G6`: O1-anchor replay — frozen QG2 O1 witnesses reproduce exactly
     `C_DP = 11`, `C_Dxx = 13`.
   - `G7` (NEW, QG43 receipt binding): `QG43_CONE_EXACTNESS_RESULTS.json`
     sha256 recorded; its terminal must be
     `QG43_REGION_STRICTLY_CONTAINS_CONE_AT_N1`; every serialized QG43
     witness row must round-trip — reconstruct the row's exact objective from
     its serialized name (`t_nc = 2*t_r+dnc`, `t_c = 2*t_r+dc`, `t_tag`,
     `t_r`; grid member or fresh equally-weighted objective) and require the
     same `C_DP`/`C_Dxx`.
5. **Artifacts:** `QG44_N2_FRONTIER_RESULTS.json` (schema
   `ORION.QG.QG44.N2Frontier.v1`: grid, per-objective aggregates
   `{n_eval, n_gaps, min_gap, n_eval_p4}`, P4 cell table
   `{(dc,dnc,t_r): {n_eval, n_gaps, min_gap}}`, `q1_witness_at_tc_ge2`,
   `q1_cells_with_witnesses`, `q3_p1_verdict`, `q4_continuation_rows`,
   `g4_brute_report`, `qg43_receipt_sha256`, gate verdicts, witness rows
   capped at 20), `RUN_QG44.log`.

## Terminals

- `QG44_FRONTIER_IS_GEOMETRY` — Q1 YES with witnesses at `t_c >= 2` in at
  least two distinct margin cells OR any P1/P3 witness at `t_c >= 2`: the
  n=2 frontier is margin geometry, not a `t_c = 1` artifact.
- `QG44_TC1_ARTIFACT_DOMINANT` — Q1 NO: zero witnesses at `t_c >= 2` across
  all panels (P1 exhaustive subclass, P2 hostile, P3 continuation, P4 x600):
  support-3 gaps at n=2 concentrate on the absolute central-cost boundary.
- `QG44_CONSISTENCY_FAILURE` — any gate violated (exit 3, no claims).

## Discipline & authority

No fitted parameters; every number is an exact integer from the frozen
`qg2_objective_robustness` machinery (imported, not copied). Unique
`Objective.name` per grid point; `clear_caches()` between objectives only.
P4 rates are exact fractions of a seeded finite panel — no distributional
claim. Authority: EXACT IN INSTANCES for P1 (scoped to the letter subclass at
n=2), PANEL-BOUNDED elsewhere; NO all-n claim; NOT R6. All-n statements
remain QG8's. Successor (QG24, conditional): if FRONTIER_IS_GEOMETRY, an
all-n sharpness attempt on the `dc = -2` column; if TC1_ARTIFACT_DOMINANT, a
theorem-shaped attack on "witnesses require `t_c = 1`" via the QG8 exchange
resource vectors.
