# QG47 — exhaustive full-alphabet n=2 ordered sweep (V1)

## Aim

Settle the n=2 witness frontier EXACTLY at the frozen 6-cell objective grid:
does ANY n=2 instance over the FULL letter alphabet — all 15 masks
`(x,z) in {0..3}^2 \ {(0,0)}`, `15^6 = 11,393,390` ordered instances —
witness (`gap = C_DP - C_Dxx < 0`) at ANY grid objective? Prior evidence,
all zero: QG43 (exhaustive n=1), QG45 (two exhaustive letter subclasses
1,458 instances + #8's width-2 projection + seeded random + hostile panels),
QG44/QG46 (the unique `t_c >= 2` lift is a single n=3 instance). This sweep
removes the sampling: every n=2 instance is evaluated.

## Frozen machinery (identical to QG43–QG46, imported not copied)

`qg2.dp_cost_pairs_ob`, `qg2.dxx_cost_ob`, `qg2.dp_witness_ob`,
`qg2.brute_config_n1_ob`, `qg2.clear_caches`, `qg2.Objective`. Grid = the
frozen 6 cells, LOADED from the QG46 receipt's serialized weights
(`QG46_KERNEL_ANATOMY_RESULTS.json`, terminal `QG46_KERNEL_PARTIAL`);
letters = the canonical sorted 15-mask order fixed in the driver (sha256
recorded in every part receipt and checked uniform by the merge).

## Registered execution plan (batch campaign; single certified merge)

1. **Task decomposition**: task `T in [0,1350)` = (objective, prefix pair)
   — `ob_idx = T // 225`, prefix letters `(i,j) = divmod(T % 225, 15)` —
   enumerating all `15^4 = 50,625` ordered completions `(l2..l5)`.
   225 prefixes x 6 objectives = **1,350 tasks, 11,393,390 instances per
   objective, 68,360,340 evaluations total**. Ordered enumeration
   (`itertools.product` over the fixed letter order); the committed
   frame-permutation invariance probe (`qg47_sweep_invariance_probe.py`)
   is design evidence ONLY and is NOT relied upon anywhere.
2. **Part receipts**: each task writes `ORION.QG.QG47.SweepPart.v1` —
   exact gap histogram, min gap, exact witness count, witness sample capped
   at 200 instances (count always exact), 5 probe evaluations (first 4 +
   last completion), objective weights, letters sha256, wall; content
   digest (canonical JSON sha256).
3. **Certified merge** (`--merge`, single process): completeness (exactly
   the 1,350 unique task ids), per-part digest re-verification, letters
   sha uniformity, per-objective instance totals `= 15^6`, per-objective
   weight match vs the QG46 receipt, independent re-evaluation of all
   5 probes x 1,350 parts (6,750 evaluations).
4. **Gates (hard)**:
   - `G1`: `C_DP <= C_Dxx` asserted on EVERY evaluation (task aborts on
     violation; merge fails).
   - `G4`: independent n=1 brute cross-check — 12 fixed letter sextuples,
     brute minimum over 4 branch perms x CENTRALS8 must equal the DP value.
   - `G5`: anti-instrument import gate (AST scan, as QG43–QG46).
   - `G6`: chain binding — QG45 receipt sha256 + terminal
     `QG45_LIFT_IS_ISOLATED` + full single-flip round-trip (36 rows x 6
     objectives from `q2_flip_table` + `witness8.qg45_base_row`, 216
     evaluations, gap equality; lift-cell absent => 0 by G1) AND QG46
     receipt sha256 + terminal `QG46_KERNEL_PARTIAL` + full two-bit panel
     round-trip (598 rows x 6 objectives, 3,588 evaluations); QG43/QG44
     sha256s recorded for chain continuity.
5. **Registered questions**:
   - **Q1 (primary)**: total witness evaluations over the whole space at
     the 6-cell grid — is the n=2 frontier empty?
   - **Q2**: per-objective and per-cell-class (`lift`/`home`) witness
     counts; per-objective gap histograms and min gaps (near-miss depth).
   - **Q3 (conditional)**: if nonempty, witness letters are serialized
     (capped lists, exact counts) for layer-local / same-bit structure
     analysis in the successor.
6. **Terminals**: `QG47_N2_FRONTIER_EMPTY` (0 witnesses anywhere) /
   `QG47_N2_FRONTIER_NONEMPTY` (>= 1) / `QG47_CONSISTENCY_FAILURE`
   (any merge problem or gate failure; exit 3, no claims).

## Execution environment (compute-host discipline)

The campaign is a ~`5.2 x 10^2` core-hour pure-math batch (measured 36.2
evaluations/s/core at n=2 on one core; full chunk `15^4` = 50,625
evaluations ~= 23 min). It
runs ONLY on a sanctioned heavy-compute host — LUNARC batch (pure-math
no-network tarball: driver + `qg2` module + the QG45/QG46 receipts; NO
repository clone, NO outbound network on nodes) or laptop billy — never
as a local worker pool on the Mac mini. Parts are collected and the
certified merge runs as a single deterministic process; the outcome lands
as a second commit at the registration SHA, per the QG43–QG46 chain
discipline.

## Pre-registration smoke evidence (committed with the registration)

`--selftest` (reduced 2-part configuration through the FULL merge path
including G4 + G6): terminal `QG47_N2_FRONTIER_EMPTY` on the mini slice,
0 problems, 0 probe failures, all 7 merge gates green, wall 235 s; G6
round-trip covers 36 single rows + 598 pair rows x 6 objectives =
3,804 evaluations, all gap-equal to the QG45/QG46 receipts
(`roundtrip_ok: true`, result digest
`8e4c5fffaa7111168b8d49ec343f95598551286a1b7fa02d6893ade3c12eaf0a`).
One full-size chunk (`--chunk 7`) timed on a single core to validate the
production chunk path: see `RUN_QG47_REGISTRATION.log`.

## Discipline & authority

No fitted parameters; every number is an exact integer from the frozen
machinery. Authority: EXHAUSTIVE ORDERED n=2 FULL-ALPHABET at the frozen
6-cell grid — exact, complete in instances; NO all-n claim (n >= 3
untouched); NOT R6.
