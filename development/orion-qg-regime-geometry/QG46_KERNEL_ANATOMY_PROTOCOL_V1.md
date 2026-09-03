# QG46 — kernel anatomy: two-bit-flip closure of the 7-flip lift kernel (V1)

## Aim

QG45 (receipt `QG45_WITNESS8_ANATOMY_RESULTS.json`, terminal
`QG45_LIFT_IS_ISOLATED`) showed that exactly **7 of 35** valid single-bit
flips of witness #8 (`P4:RANDOM_n3:11`, n=3, targets
`[(3,7),(5,0),(2,4),(0,2),(5,4),(7,1)]`) preserve the `t_c >= 2` lift, and
that these 7 flips span 5 of 6 targets, both coordinates, and all 3 bit
positions. This study asks whether that 7-flip **kernel** is a coherent
second-order structure — specifically whether it *closes under pairwise
composition* (do two kernel flips applied together still lift?) — and
measures second-order lift rates by class. It is the registered secondary
thread of QG45's successor plan, executed before (and informing the design
of) the n-threshold attack; that primary thread (exhaustive full-alphabet
n=2 sweep) is renumbered **QG47** and requires a batch campaign (see
"Successor" below).

## Frozen machinery (identical to QG43/QG44/QG45, imported not copied)

`qg2.dp_cost_pairs_ob`, `qg2.dxx_cost_ob`, `qg2.dp_witness_ob`,
`qg2.brute_config_n1_ob`, `qg2.clear_caches`, `qg2.Objective`;
`gap(I,O) = C_DP - C_Dxx`; a **witness** is `gap < 0` (serialized DP witness
then has `max_frame_support > 2`). rho = 0, t_tag = 2 throughout. Witness
#8's targets/n and the 7 kernel flips are LOADED FROM THE QG45 RECEIPT
(`witness8` field and the rows of `q2_flip_table` with non-empty
`lift_cells`; the derived kernel count must equal `q1_neighbor_witness_count`
= 7). Nothing is hand-copied; G6 re-verifies by round-trip.

## Registered outcome run (single pass, exit 0 = complete)

1. **Objective grid**: the same frozen 6 cells as QG45 (4 `t_c >= 2` lift
   cells `Q45G_tr2_dc-2_dnc0_tag2`, `Q45G_tr2_dc-2_dnc1_tag2`,
   `Q45G_tr3_dc-3_dnc0_tag2`, `Q45G_tr3_dc-3_dnc1_tag2`; 2 `t_c = 1` homes
   `Q45G_tr2_dc-3_dnc0_tag2`, `Q45G_tr2_dc-3_dnc1_tag2`).
2. **Instance panel `PK2`**: #8 itself plus all **two-bit-flip neighbors** —
   unordered pairs of distinct flip positions from the 36 positions
   (6 targets x 2 coordinates x 3 bit positions, `XOR 1<<q` each). A pair is
   skipped and counted iff applying both flips zeroes any target (note this
   is weaker than requiring both flips individually valid: a pair containing
   the one individually-zeroing flip is retained when the second flip lands
   so that no target zeroes). Validated construction counts (by the panel
   builder against the receipt-loaded targets): **598 valid pairs + base =
   599 instances** (32 skipped), classified against the derived kernel as
   **KK = 21** (both flips kernel), **KX = 195** (exactly one), **XX = 382**
   (neither) — all 598 x all 6 objectives = 3,594 evaluations.
3. **Registered questions** (authored before the run):
   - **Q1 (primary, closure):** how many of the 21 valid KK pairs witness
     (`gap < 0`) at >= 1 of the 4 lift cells?
   - **Q2 (second-order rates):** lift rates by class (KK / KX / XX) at the
     lift cells; per-pair cell pattern (does QG45's cell-uniformity — all
     four lift cells together — persist at depth two?); minimum lift-cell
     gap by class.
   - **Q3 (depth):** minimum gap anywhere in the panel at lift cells and at
     homes, vs the base's -2 / -3.
   - **Q4 (home stability):** how many of the 598 pairs witness at BOTH
     homes (QG45: 36/36 singles did)?
4. **Gates (hard):**
   - `G1`: `C_DP <= C_Dxx` on every evaluation (assert, abort on violation).
   - `G3`: every serialized witness row has `max_frame_support > 2`.
   - `G4`: independent n=1 brute cross-check (`qg2.brute_config_n1_ob`) at
     the most witness-bearing objective, on 12 fixed minimal-letter
     instances (as QG43-QG45).
   - `G5`: anti-instrument import gate (as QG43-QG45).
   - `G6` (QG45 receipt binding): `QG45_WITNESS8_ANATOMY_RESULTS.json`
     sha256 recorded; its terminal must be `QG45_LIFT_IS_ISOLATED`; FULL
     single-flip round-trip — re-evaluate #8 and all 35 valid single flips
     at all 6 objectives (objectives reconstructed from the QG45 receipt's
     own serialized weights) and require the same gap everywhere (a lift
     cell absent from a receipt row's `lift_cells` means gap 0, since G1
     enforces gap <= 0); the QG44 and QG-43 receipt sha256s are recorded
     for chain continuity.
5. **Artifacts:** `QG46_KERNEL_ANATOMY_RESULTS.json` (schema
   `ORION.QG.QG46.KernelAnatomy.v1`: `kernel`, panels, `q1_kk_closed`,
   `q2_class_lift`, `q2_pair_table`, `q3_depth`, `q4_home_stability`,
   `g4_brute_report`, `g6_qg45_binding`, witness rows capped at 40),
   `RUN_QG46.log`.

## Terminals

- `QG46_KERNEL_CLOSED` — all 21 valid KK pairs lift: the kernel composes;
  the lift set contains the pairwise closure of the kernel (second-order
  interior).
- `QG46_KERNEL_PARTIAL` — some but not all KK pairs lift.
- `QG46_KERNEL_BROKEN` — no KK pair lifts: kernel membership is not
  compositional; the lift set is thinner than a pairwise-closed structure.
- `QG46_CONSISTENCY_FAILURE` — any gate violated (exit 3, no claims).

Independent of the terminal, KX/XX rates and the emergent-lift count
(`xx_lift > 0`: two non-kernel flips jointly lifting where neither does
alone) are recorded as fields.

## Discipline & authority

No fitted parameters; every number is an exact integer from the frozen
`qg2_objective_robustness` machinery (imported, not copied). Unique
`Objective.name` per grid point; `clear_caches()` between objectives only.
PK2 is a finite defined set (exact in instances). Authority: EXACT IN
INSTANCES for the evaluated panel; NO all-n claim, NO region claim; NOT R6.

## Successor (QG47, registered as the primary thread deferred from QG45)

The **n-threshold attack**: exhaustive full-alphabet n=2 ordered sweep —
all `(x,z)` in `{0..3}^2 \ {(0,0)}` (15 letters), 15^6 = 11,393,390 ordered
instances x the 6-cell grid (68.4M evaluations, ~10^3 core-hours) — a batch
campaign on LUNARC (pure-math, no-network), chunked deterministically with
per-chunk part receipts merged into one outcome. Design evidence committed
with this registration: `development/orion-qg-regime-geometry/
qg47_sweep_invariance_probe.py` — the machinery's `(C_DP, C_Dxx)` was
verified exactly invariant under frame permutation on all 40 gap<0 rows of
the QG45 receipt (all 3! permutations each), 300/300 random n=2 instances,
and 80/80 random n=2/n=3 shuffles; QG47 does NOT rely on this reduction for
its exactness claim (ordered enumeration is airtight) — the probe informs
only cross-check design.
