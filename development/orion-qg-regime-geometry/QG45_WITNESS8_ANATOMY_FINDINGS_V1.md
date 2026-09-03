# QG45 findings — witness #8 anatomy (V1)

Run: registration SHA `9b59638c1` (PR #2165), wall 403.5 s, exit 0.
Result digest `35517ae79a582168a84adf346c1709fe9f68e12d786f03f16f3612980be1096e`.
Receipt: `research/extensions/orion-qg/QG45_WITNESS8_ANATOMY_RESULTS.json`
(schema `ORION.QG.QG45.Witness8Anatomy.v1`). Gate G6 binds the QG44 receipt
sha256 `b1e76edefc31198f308297052318a658c3484de08aa9ceb860c986b17533c35f`
(terminal `QG44_FRONTIER_IS_GEOMETRY`, #8 round-trip at all 6 of its witnessed
objectives) and the QG43 receipt sha256 `974fe8b8ed8af1ec7ee7808d658ad782100a48c48c840f99a7e1c0fade15ba8e`
(same serialized targets/n that built the panels — loaded, not hand-copied).

## Terminal

**`QG45_LIFT_IS_ISOLATED`** — Q1: **7 of 35** valid bit-flip neighbors of
witness #8 lift at any `t_c >= 2` objective; registered threshold was
`ceil(35/2) = 18`. The unique `t_c >= 2` lift is confined to a thin set of
exact masks (isolated up to single-bit moves), NOT structurally stable.

## What the run establishes

1. **The lift is a thin set; the phenomenon is not.** Every one of the 36 PA
   instances (base + all 35 valid flips) witnesses at BOTH `t_c = 1` home
   cells — the t_c=1 phenomenon is fully single-bit stable — but only 8 of 36
   (base + 7 flips) reach any `t_c >= 2` cell. Crossing the t_c=1 → t_c=2
   boundary is the fragile part; being a witness at all is not.
2. **The lift is cell-uniform per instance.** Each of the 7 lifting flips
   lifts at ALL FOUR `t_c >= 2` cells simultaneously (never a subset): the
   four cells (dc,dnc) = (-2,0),(-2,1),(-3,0),(-3,1) behave as one frontier.
3. **The killing is not positional.** The 7 lifting flips span 5 of 6 targets,
   both coordinates, and all three bit positions; no target/coordinate/bit
   owns the lift. 28/35 single-bit moves simply fall back to t_c=1.
4. **No n=2 witness in #8's projection (Q3).** The low-2-bit projection of
   the unique lifting instance has gap 0 at all 6 objectives.
5. **No n=2 witness in either exhaustive letter subclass (Q4).** 0 of 729
   saturated-mask instances (`A_max`) and 0 of 729 mid-mask instances
   (`A_mid`) witness at ANY of the 6 objectives — 1,458 exhaustive instances.
   Combined with QG44's minimal-letter 729 and uniform-random panels, the
   "n >= 3 necessary" reading now covers minimal, mid, and full-mask letters
   plus #8's own canonical projection at width 2.

## Gates (all green)

G1 (`C_DP <= C_Dxx` on all 8,970 panel evaluations, 6x1,495, hard assert) ·
G3 (all 40 serialized witness rows have `max_frame_support > 2`; cap 40
reached, all rows PA) · G4 (independent n=1 brute cross-check, 12 fixed
letter instances at the most witness-bearing objective, exact) · G5
(anti-instrument import gate) · G6 (QG44+QG43 receipt binding, round-trip
6/6). Exit 0. `novelty_authority: false`;
`physical_quantum_advantage_claim: false`.

## Discipline

Exact integer machinery imported from frozen `qg2_objective_robustness`
(never copied); no fitted parameters; the registered threshold `ceil(F/2)`
was computed at runtime (F = 35 valid flips; 1 zeroing flip skipped and
counted); PA/PB finite defined sets, PC exhaustive over the two registered
width-2 letter subclasses. Authority: EXACT IN INSTANCES for the evaluated
panels; no all-n claim; not R6.

## Successor (QG46, conditional on this terminal)

Per the registered successor plan, ISOLATED selects the **n-threshold
attack** as the width analogue of QG8's cone theorem: exhaustive signed /
full-alphabet n=2 sweep beyond letter subclasses (all `(x,z)` masks in
`{0..3}^2 \ {(0,0)}`: 15 letters, 15^6 = 11,393,390 ordered instances,
chunked), which would settle the n=2 frontier exactly rather than by
subclass evidence. Secondary thread: two-bit-flip neighborhood of #8 (does
the 7-flip lift set have second-order structure?) before any
positive-measure claim about the lift set is attempted.
