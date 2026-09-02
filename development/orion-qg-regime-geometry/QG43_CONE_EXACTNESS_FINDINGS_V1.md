# QG43 findings — cone exactness at n=1 (V1, 2026-09-03)

Run: registration SHA `230fd327b2828564b8cf` (PR #2163), wall 893.0 s over 41 objectives, exit 0.
Result digest `be2413b2645f5c2ad3ee8037ec81c2ca3af6f6ffd8aef4d3212cfe92f9f861ef`.
Renumbered re-registration of the study first registered as QG-22 in (closed)
PR #2153 (same run content; see the protocol's provenance note).
Terminal: **`QG43_REGION_STRICTLY_CONTAINS_CONE_AT_N1`**.

## Headline

On the registered margin grid (41 objectives — see the count note below), **no
objective — not even the deepest valid outside points (dc = −5) — has a single
support-3 witness among ALL 729 exhaustive n=1 instances** (`n_gaps_p1 = 0`
everywhere). The exact support-2 region at n=1 therefore strictly contains the
QG8 cone on this grid, and support-3 gaps are **a width-n ≥ 2 phenomenon**: the
same outside objectives that are n=1-clean carry up to 34 witnesses from the
n=2/3 panels.

**Grid count note.** The protocol's registered grid is its set notation (Slice A
`(dc,dnc) ∈ {-3..2}², dc <= dnc` → 21; Slice B `dc ∈ {-5..0} × dnc ∈ {0,1}` →
12; O1 anchor 1; tag extras 6; scale probe 1 = **41 objectives**). The
protocol's parenthetical prose counts (36 / 15 / 13) were an arithmetic slip in
commentary, not in the registered set; the driver implements the set notation
exactly, and the protocol file is deliberately left untouched so its sha256
binding in the receipt stays verifiable. P4 accordingly ran on the 21 G_main
objectives.

## Registered answers

- **Q1 (region vs cone): YES.** 33 of the 41 grid objectives are outside the
  cone;
  every one of them has `gap = 0` on all of P1 (exhaustive). QG19's ambiguity
  is resolved: its zero-witness panel at `(−1,0)` was **not** panel poverty —
  exhaustive enumeration confirms zero n=1 witnesses there.
- **Q2 (frontier): 18/33 outside objectives bear witnesses somewhere in
  P2∪P3∪P4** (never in P1). `min |dc|` among witness-bearing points = **2**.
  Witness mass concentrates at the valid-objective boundary `dc = −3`
  (`t_c = 1`): 24–34 gaps, `min_gap = −3`, vs isolated 2-gap points elsewhere.
- **Q3a (rays): exact.** `gap(λ·O_base) = λ·gap(O_base)` for λ ∈ {2,3} on all
  12 serialized witnesses of the deterministic base `O_base = (dc,dnc) = (−3,−2)`
  (first in `(−n_gaps, dc, dnc)` order) — arithmetic certification only.
- **Q3b (scale probe):** `(dc,dnc) = (−1,0)` has zero witnesses at
  `t_r ∈ {1,2,3}` — witness absence at shallow margins is scale-stable in t_r.
- **Q4 (tag):** at `(dc,dnc) = (−3,0)` witnesses exist for `t_tag ∈ {0,2,4}`
  (2 / 34 / 2 gaps) — tag changes magnitude, not existence, consistent with
  QG8's tag-unconstrained exchange halfspaces.

## Gates

All green: G1 (`C_DP ≤ C_Dxx` on all 32,276 evaluations), G2 (strictly-inside
objectives zero-gap on P1), G3 (all serialized witnesses `max_frame_support > 2`),
G4 (24 independent n=1 brute enumerations exact at the two selected objectives),
G5 (anti-instrument import), G6 (O1-anchor replay: both frozen QG2 O1 witnesses
reproduce exactly `C_DP = 11`, `C_Dxx = 13`).

## Authority and next rung

EXACT, EXHAUSTIVE IN INSTANCES at n=1, GRID-ONLY in objective space; no all-n
sharpness claim; NOT R6. Open successor: the witness frontier at n=2 is where
the geometry lives — an n=2 exhaustive or structured enumeration around
`dc = −3` (and the `(−2,*)` column, currently witness-free at min |dc| = 2) is
the natural QG23: either find the n=2 region boundary or show the frontier is
a boundary artifact (`t_c = 1`) rather than cone geometry.
