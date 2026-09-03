# QG44 findings — n=2 witness frontier (V1, 2026-09-03)

Run: registration SHA `1b4789e225922657c8d` (PR #2164), wall 749.8 s, exit 0.
Result digest `806e24d25a6cddc68f116298fd21e9dde448e3033de7e157b23be9d9785475be`.
Renumbered re-registration of the study first registered as QG-23 in (closed)
PR #2162 (same run content; see the protocol's provenance note); G7 binds to
the fresh QG-43 receipt (#2163), sha256 `974fe8b8…15ba8e`.
Terminal: **`QG44_FRONTIER_IS_GEOMETRY`** (registered criterion: witnesses at
`t_c >= 2` in >= 2 distinct margin cells, or any P1/P3 witness at `t_c >= 2`).

## Headline

The registered criterion fires — four distinct margin cells carry witnesses
with the absolute central cost lifted off 1 — but the attribution is sharper
than the terminal: **every witness in the entire run is an n=3 instance, and
all but one of them require `t_c = 1`.**

- **Zero n=2 witnesses anywhere in this study.** The 729-instance exhaustive
  letter subclass at width 2: zero witnesses at every `H_main` objective
  (exact, scoped — the direct width-2 analogue of QG43's exhaustive n=1
  zero). The 600-instance seeded random n=2 panel: zero witnesses at every
  grid objective (`n_gaps_p4 = 0` in all 12 non-anchor cells). Hostile n=2
  panels: zero.
- **The 21-gap `t_c = 1` cells (`dc=-3`, `t_r=2`) are entirely continuation
  mass**: 19 of QG43's 20 serialized witnesses + both frozen QG2 O1
  witnesses, all n=3, re-witness at gap -2. Attribution is in-receipt this
  run: every one of the 20 capped witness rows carries `panel = "P3"` and
  `n = 3`, and 19 + 2 = 21 exactly accounts for the cell's gap count, so
  P1/P2/P4 contribute zero at those cells.
- **Exactly one instance lifts to `t_c >= 2`**: QG43 witness #8
  (`P4:RANDOM_n3:11`, n=3), which witnesses with gap -2 at
  `(dc,dnc) = (-2,0)`, `(-2,1)` (`t_c = 2`) and at `(-3,0)`, `(-3,1)` with
  `t_r = 3` (`t_c = 3`). No other instance, panel, or cell produces a
  `t_c >= 2` witness (4/4 such cells trace to this single instance).

## Registered answers

- **Q1 (primary): YES** — witnesses at `t_c >= 2` exist, in 4 distinct
  margin cells; terminal `QG44_FRONTIER_IS_GEOMETRY`. Carried by one n=3
  instance (above).
- **Q2 (frontier density):** `t_c = 1` cells at `(dc,dnc) = (-3,0)/(-3,1)`:
  21 witness evaluations each (2.9% of cell evaluations, all n=3
  continuation); `t_c >= 2` cells: exactly 1 witness evaluation each; the
  600-instance discovery panel contributes zero at every cell. The frontier
  density collapses by >= 20x when `t_c` lifts 1 -> 2 and by another ~factor
  to zero for random n=2 mass.
- **Q3 (exhaustive subclass): ZERO** — no letter-subclass instance at width
  2 is a witness on any `H_main` objective (729 instances x 6 objectives).
  Note: the JSON field `q3_p1_verdict.cells_with_witnesses` records
  all-panel counts per cell (21 at the `t_c=1` cells), not P1-only counts;
  the P1-only zero is established by the in-receipt panel attribution (all
  capped witness rows are P3 continuation rows; 19 + 2 = 21 closes the
  account). The field name is a labeling defect in the driver; the
  registered verdict (zero) is unaffected.
- **Q4 (continuation stability):** 19/20 QG43 witnesses re-witness at the
  `t_c = 1` cells; 1/20 (witness #8) survives any `t_c >= 2` lift; the `t_r`
  ladder at fixed margins (`t_c` 1 -> 3 -> 5) kills every witness except #8
  already at the first rung.

## Gates

All green: G1 (C_DP <= C_Dxx on all 11,925 gap evaluations — 6x1356 H_main +
6x627 H_scale + 27 anchor), G3 (witnesses support > 2), G4 (24 n=1 brute
cross-checks exact), G5 (anti-instrument import), G6 (O1-anchor replay 11/13
x2), G7 (QG43 receipt bound: terminal + sha256 + 20/20 serialized-witness
cost round-trip via reconstructed objectives).

## Authority and successor

EXACT for the letter subclass at width 2 (scoped); panel-bounded elsewhere;
NO all-n claim; NOT R6. The structural picture across QG43+QG44: support-3
witnesses are absent at n=1 (exhaustive) and at n=2 (exhaustive letter
subclass + 600 random + hostile), first appear at n=3, concentrate at
`t_c = 1`, and exactly one known instance survives `t_c >= 2`. Natural
successor (QG45):
(a) neighborhood perturbation of witness #8 at n=3 — is its lift structurally
stable or measure-zero; (b) targeted n=2 search seeded by #8's target values
(close the last n=2 gap); (c) an n-threshold attack: is `n >= 3` necessary
for ANY support-3 witness in this family — the width analogue of QG8's cone
theorem.
