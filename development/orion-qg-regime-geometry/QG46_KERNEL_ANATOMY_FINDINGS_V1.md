# QG46 findings — kernel anatomy: two-bit-flip closure of the 7-flip lift kernel (V1)

Run: registration SHA `5b7dd1268` (PR #2166), wall 300.9 s, exit 0.
Result digest `8c1e34af7efc49d6e5972176c1383af9a94f532dcd17f281b198877368558ea3`.
Receipt: `research/extensions/orion-qg/QG46_KERNEL_ANATOMY_RESULTS.json`
(schema `ORION.QG.QG46.KernelAnatomy.v1`). Gate G6 binds the QG45 receipt
sha256 `f2f52d7cfaf96e0b3ce5853d0356eeafaf4e8ab7cec69d3654a2fa0f5fe139ce`
(terminal `QG45_LIFT_IS_ISOLATED`; FULL single-flip round-trip — #8 + all 35
valid single flips at all 6 objectives, 216/216 gaps identical) and records
the QG44 (`b1e76ede…`) and QG-43 (`974fe8b8…`) receipt sha256s for chain
continuity. The kernel was DERIVED from the QG45 receipt's own `q2_flip_table`
(7 flips: `t0_c0_b0, t1_c0_b2, t1_c1_b1, t2_c1_b1, t4_c0_b1, t5_c0_b0,
t5_c1_b1`).

## Terminal

**`QG46_KERNEL_PARTIAL`** — 18 of 21 valid KK (kernel x kernel) pairs lift
at a `t_c >= 2` cell: the kernel is *mostly* closed under pairwise
composition but is NOT a pairwise-closed structure.

## What the run establishes

1. **The kernel composes 18/21 — and every broken pair shares one member.**
   The 3 non-lifting KK pairs all contain `FLIP_t2_c1_b1` (target 2, z-bit
   1): `(t1_c1_b1, t4_c0_b1)`, `(t2_c1_b1, t4_c0_b1)`,
   `(t2_c1_b1, t5_c1_b1)`. `t2_c1_b1` composes with only 3 of its 6 kernel
   partners and participates in just 1 of the 26 lifting KX pairs — it is
   the kernel's weakest (non-compositional) member; `t4_c0_b1` is the
   strongest (8 of 26 lifting KX pairs).
2. **Emergent lifts exist: the lift set is not the kernel's closure.**
   14 of 382 XX pairs (neither flip a kernel member) lift — two
   individually-non-lifting flips jointly lift. At least 10 of the 14 are
   **same-bit-position pairs** (both flips at the same `q` — e.g.
   `t0_c0_b1 + t3_c0_b1`, `t4_c1_b0 + t5_c1_b0`), including 3 pairs
   flipping both coordinates of a single target at the same bit (`t3`,
   `t4` at b0/b2). Mechanistic reading: the DP is layerwise in `q`, so
   same-`q` double flips act within one DP layer — layer-local moves can
   restore a feasibility single-layer moves cannot.
3. **Lift rates stratify sharply by class**: KK 85.7% (18/21), KX 13.3%
   (26/195), XX 3.7% (14/382). Kernel membership is ~3.6x the base
   two-bit rate — strongly predictive, far from sufficient; the lift set
   has graded second-order structure, not threshold structure.
4. **Cell-uniformity persists at depth 2.** 57 of the 58 lifting pairs
   witness at ALL FOUR `t_c >= 2` cells simultaneously (one at a strict
   subset); the four lift cells continue to behave as a single frontier.
5. **Depth grows at homes, not at the frontier.** Minimum gap over the
   whole panel is -2 at lift cells (no two-bit neighbor reaches -3 there —
   the `t_c >= 2` lift stays shallow) but **-4 at home cells** (two below
   the base's -2): deep witnesses are a `t_c = 1` phenomenon.
6. **Home stability stops being universal at depth 2.** 570 of 598 pairs
   witness at both homes (28 fail) — versus 36/36 for single flips: the
   `t_c = 1` witness phenomenon is robust but no longer two-bit invariant.

## Gates (all green)

G1 (`C_DP <= C_Dxx` on all 3,594 panel evaluations, hard assert) · G3 (all
serialized witness rows have `max_frame_support > 2`; cap 40) · G4
(independent n=1 brute cross-check, 12 fixed letter instances, exact) · G5
(anti-instrument import gate) · G6 (QG45 receipt binding + 216/216
single-flip round-trip). Exit 0. `novelty_authority: false`;
`physical_quantum_advantage_claim: false`.

## Discipline

Exact integer machinery imported from frozen `qg2_objective_robustness`
(never copied); no fitted parameters; kernel and targets loaded from the
QG45 receipt (nothing hand-copied); PK2 is a finite defined set (exact in
instances). Authority: EXACT IN INSTANCES for the evaluated panel; no
all-n claim; not R6.

## Successor

The graded, layer-structured second-order geometry (mostly-closed kernel +
same-bit emergent lifts + deep home-cell witnesses) sharpens the case for
**QG47**, the registered primary thread: the exhaustive full-alphabet n=2
ordered sweep (15^6 = 11,393,390 instances x the 6-cell grid, LUNARC batch
campaign, chunked with per-chunk part receipts) that settles the n=2
frontier exactly — now with a concrete mechanistic hypothesis to test
there: whether n=2 witnesses (if any) also concentrate on layer-local
(same-`q`) structure, and whether the QG45/QG46 letter-subclass zeros
extend to the full alphabet.
