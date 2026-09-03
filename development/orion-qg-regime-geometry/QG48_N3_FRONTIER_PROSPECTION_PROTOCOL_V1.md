# QG48 — n=3 frontier prospection: exact depth-3 kernel slice + stratified seeded sampling (V1)

## Aim (registered question)

After the certified EMPTY exhaustive n=2 frontier (QG47: 68,343,750
evaluations, terminal `QG47_N2_FRONTIER_EMPTY`, PR #2178) and its one-stage
attribution (witness-predicate stage, uniform emptiness; PR #2180, section 6
of `QG47_EMPTY_FRONTIER_ATTRIBUTION_V1.md` freezes this design), does the
dimension lever `n -> 3` open a witness frontier of non-negligible mass
OUTSIDE the known witness8 kernel closures?

**Lever hypothesis `H_n`**: dimension opens a frontier of non-negligible
mass at n=3. **Prediction**: R2 finds >= 1 witness at kernel distance >= 4
(exact popcount in the 36-bit target-flip space) from the witness8 base.

**Falsifiers**:
- (a) R2 completes at full size (per-cell N = 225 x 15,000 = 3,375,000;
  95% one-sided detection floor `ln(20)/N = 8.88e-7` per cell) with 0
  witnesses outside the closures -> `H_n` falsified in favor of "isolated
  measure-zero kernel at n=3" (terminal `QG48_N3_FRONTIER_ISOLATED`).
- (b) R1's exact depth-3 closure contains 0 witnesses while R2 is sparse ->
  the kernel decays faster than the dimension-geometry reading predicts.

## Frozen machinery (identical to QG43–QG47, imported not copied)

`qg2.dp_cost_pairs_ob`, `qg2.dxx_cost_ob`, `qg2.clear_caches`,
`qg2.Objective`; grid + G4/G6 machinery imported from
`qg47_n2_full_sweep.py` (certified). Grid = the frozen 6 cells LOADED from
the QG46 receipt's serialized weights; n=3 alphabet = the canonical sorted
63-mask order `(x,z) in {0..7}^2 \ {(0,0)}` fixed in the driver (sha256
recorded in every part receipt, checked uniform by the merge). Kernel base
= the QG45 `witness8.targets` rows (6 rows x 2 targets in `{0..7}`).

## Registered execution plan (batch campaign; single certified merge)

1. **R1 (exact slice, cheap)**: ordered `C(36,3) = 7,140` three-bit-flip
   closure of the witness8 kernel base x 6 objectives = 6 tasks (one per
   objective), 42,840 rows max (rows whose flip lands a target on `(0,0)`
   are skipped and counted). Extends QG45 depth-1 / QG46 depth-2 anatomy
   to exact depth 3 (`kernel_depth_completed = 3`).
2. **R2 (stratified seeded uniform sampling)**: uniform over the full
   63-letter n=3 alphabet, 6 letters per instance, 3-pair shape, at each
   of the 6 frozen cells; `R2_SEED = 20260903`, per-task PRNG
   `Random(R2_SEED * 1000003 + task_id)` (fully deterministic given the
   task id). **1,350 tasks** (225 streams x 6 objectives) x **15,000
   instances = 20,250,000 evaluations**. Per-task instance count sized by
   the pre-registration rate probe (below), rescaled from the attribution
   doc's assumed 25,000 to hold the ~630 core-hour budget.
3. **Part receipts**: `ORION.QG.QG48.R1Part.v1` / `ORION.QG.QG48.R2Part.v1`
   — exact gap histogram, min gap, exact witness count (sample capped at
   200, count always exact), witness kernel-distance histogram (R2), probe
   evaluations, objective weights, letters sha256, seed, wall; content
   digest (canonical JSON sha256).
4. **Certified merge** (`--merge`, single process): completeness (exactly
   task ids 0–5 R1 and 0–1349 R2, no duplicates), per-part digest
   re-verification, letters-sha uniformity, per-part instance counts and
   seed, weight match vs the frozen grid, independent probe re-evaluation,
   R2 witness classification by exact kernel distance
   (`inside_closure` = distance <= 3 vs `witnesses_outside_closure`).
5. **Gates (hard)**: `G1` (`C_DP <= C_Dxx` asserted on every evaluation),
   `G4` (independent n=1 brute cross-check via `qg47.g4_brute`), `G5`
   (anti-instrument AST import gate), `G6` (receipt-chain binding: QG45
   sha256 + `QG45_LIFT_IS_ISOLATED` + QG46 sha256 + `QG46_KERNEL_PARTIAL`
   + full round-trips via `qg47.g6_binding`, AND QG47 sha256 + terminal
   `QG47_N2_FRONTIER_EMPTY` + 0 witnesses + empty problems).
6. **Terminals**: `QG48_N3_FRONTIER_WITNESSED` (>= 1 R2 witness outside
   the depth-3 closure) / `QG48_N3_FRONTIER_ISOLATED` (0 outside) /
   `QG48_CONSISTENCY_FAILURE` (any merge problem or gate failure; exit 3,
   no claims).

## Pre-registration rate probe (sizing input, NOT a result)

`--rate-probe`: measured n=3 realized rate 8.62 evals/s/core (2026-09-03,
recorded in the driver constant), re-verified at registration: 8.17
evals/s/core (150 instances, wall 18.36 s, single core, Mac). Per R2 task
~= 15,000 / 8.2 ~= 31 min single-core; campaign ~= 650 core-hours.

## Execution environment (compute-host discipline)

Pure-math no-network batch on a sanctioned heavy-compute host only —
LUNARC batch via the QG47 tarball pattern (driver + import closure +
receipt inputs; NO repository clone, NO outbound network on nodes; R2 in
waves of <= 250 array indices, R1 one 6-task array) or laptop billy
(bounded rolling queue) — never a local worker pool on the Mac mini.
Driver: `development/orion-qg-regime-geometry/qg48_campaign.sh`. Parts are
collected to the Mac worktree and the certified merge runs as a single
deterministic process; the outcome lands as a second commit at the
registration SHA per the QG43–QG47 chain discipline.

## Pre-registration smoke evidence (committed with the registration)

`--selftest` (reduced 2+2-part configuration through the FULL merge path
including G4 and both G6 bindings): rc=0, `problems=[]`,
`probe_failures=0`, all 9 merge gates green; terminal on the mini slice
`QG48_N3_FRONTIER_WITNESSED` (plumbing evidence ONLY — selftest is NOT a
result and its witness counts carry no authority); merge digest
`ddec4c03f641f4c8321b841a6e95cd255c135e3506afffe0ab99a18d116f2aec`.
Registration also fixed a merge-path defect found by the selftest
(`fold()` missing `nonlocal probe_checks, probe_failures` ->
`UnboundLocalError`); the fix is part of this registration, before any
production part was produced.

## Discipline & authority

No fitted parameters; every number is an exact integer from the frozen
machinery; R2 is seed-bounded sampling, NOT exhaustive. Authority:
`R1_EXACT_DEPTH3_KERNEL_SLICE_PLUS_SAMPLED_UNIFORM_N3_FULL_ALPHABET_STRATIFIED_PER_CELL_AT_FROZEN_6_CELL_GRID__SEED_BOUNDED__NO_ALL_N_CLAIM__NOT_R6`;
`novelty_authority=false`, `physical_quantum_advantage_claim=false`.
No all-n claim; exhaustive n=3 (`63^6 ~= 6.25e10` per objective) is out of
reach and NOT claimed.
