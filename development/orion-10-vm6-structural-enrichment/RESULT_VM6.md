# VM6 — RESULT (V1)

**Terminal:** `NO_REGISTERED_STRUCTURAL_ENRICHMENT__BPRIME_MIXING_SURVIVES_ALL`
(negative — pre-recorded primary prediction confirmed)

- Study: `VM6_STRUCTURAL_ENRICHMENT`, schema `ORION10.VM6_STRUCTURAL_ENRICHMENT.v1`
- Protocol: `VM6_STRUCTURAL_ENRICHMENT_PROTOCOL_V1.md`
  (sha256 `925d60e31ca5426d98b35fa0cf9542c3ff57774d0a74ea2c85270d0c25d5839c`, frozen before the run)
- Registration SHA: `8393f8008e137feed494a5b90bb020eb61d035e9`
  (base revision `4f2a223ae383cb7a999c86538befc8bd28d1357d`)
- Result digest: `9b49d9941ca6cd5a1263efd72c5a9b60f024ede598a032dda2e27af750df1025`
- Receipt: `RUN_3561900_RAW.json.gz`, decompressed sha256
  `28a760c7b4abb552cb9c4cd66c705bd070c21c4332b5330d7b53191e8ee7857f`
- Machinery: `run_per_panel_v4.py` imported unmodified (sha256 `1525895d...ffd9`)
- Run: `RUN_VM6.log`, 40.771 s, exit code 1 (negative terminal), all gates green.

## Question (registered)

For which registered vocabularies Psi is `C_Dxx` constant on every Psi-fibre of
the 13,458-row frozen V4 census? (certificate-explanation-gap-v1 Thm 1/2: an
exact Psi-only cost explanation exists iff yes.)

## Answer

None of the registered candidates S1..S6, nor the full registered conjunction
C, separates the cost-mixed `f_Bprime` fibres. B0 reproduces V5's refutation
exactly. The full canonical key (CONTROL) is cost-constant by construction
(G5: 12,632 distinct keys, every cross-panel collision cost-consistent) — the
discrete vocabulary remains exact on this population; every strictly
structural coarsening of it that was registered fails.

| Psi | fibres | cost-mixed | rows in mixed fibres | worst spread |
|-----|--------|-----------|----------------------|--------------|
| B0 = {f_B'} | 9 | 7 | 13,420 | 5 |
| S1 = +n | 18 | 14 | 13,420 | 5 |
| S2 = +weights | 869 | 449 | 11,104 | 5 |
| S3 = +column_supports | 1,054 | 370 | 9,222 | 4 |
| S4 = +letter_multiset | 973 | 445 | 11,728 | 4 |
| S5 = +commutation_matrix | 7,488 | 603 | 3,057 | 5 |
| S6 = +pair_commute | 56 | 49 | 13,396 | 5 |
| C = conjunction (5 features) | 12,602 | **6** | **12** | 1 |
| CONTROL = {canonical_key} | 12,632 | 0 | 0 | 0 |

Secondary prediction (registered): CONFIRMED — the commutation matrix (S5) is
the single most separating registered feature (3,057 rows in mixed fibres vs
9,222+ for every other single feature).

## Worst surviving pair under C (serialized in RESULT_VM6.json)

H1_n3 local_index 798 (C_Dxx = 9, regime `split`) vs local_index 696
(C_Dxx = 10, regime `tie`), both f_B' = 10. Canonical keys:

- low: cols [(0,1,0,0,1,2), (1,1,1,0,0,2), (1,2,0,2,0,0)]
- high: cols [(0,1,1,0,0,2), (1,1,0,0,1,2), (1,2,0,2,0,0)]

Identical under every registered feature: weights (2,3,1,1,1,2),
column_supports (3,4,3), letter_multiset, commutation matrix, pair_commute
(0,1,0), n. The keys differ only by which target row carries the X/Z letters
in the first two columns — a letter-position rearrangement outside the
registered family. All six mixed C-fibres (12 rows total) sit at f_B' = 10
with cost profile exactly {9, 10} (re-derived and verified over the full
population, not just the serialized sample).

## One-stage failure attribution

The failing stage is the **coarseness of the registered feature family with
respect to letter position**. Every registered feature is invariant under
moving a non-identity letter from one target row to another whenever the row
weights, the global letter multiset, and the symplectic commutation pattern
are preserved; `C_Dxx` is not invariant under that move (9 vs 10 above). The
mixing is genuine structure-blindness of the family, not an artefact: the
replay binding is exact (G2 full-panel counters, G3 30 exact evaluate()
probes, G5 cross-panel key consistency).

## Named revival lever (one)

Register a **position-respecting, cost-independent** refinement one rung
finer than the family tested here: the multiset of per-row letter supports
(each target row's letter tuple, the whole key quotiented by qubit-column
permutation only — no letter permutation). It is admissible (computed from
letters alone, before outcomes), strictly finer than `letter_multiset` +
commutation (it remembers which row carries which letters) and strictly
coarser than the full canonical key (whose exactness on this population is
already known and carries no compression). Whether it separates the 6
surviving C-fibres is exactly checkable by replaying this study's frozen
feature table (sha256 `03838b3d0eddea5c1ba6f7df5b16056f8c8837125b4652daf145bb6d75ad8e00`)
— a V7 protocol can extend the registered family without re-running the DP.

If that rung also fails, the surviving mixing is direct finite-population
evidence toward the vocabulary-level lower bound of
certificate-explanation-gap-v1 Thm 3 / UVM2's named-vocabulary question: any
exact vocabulary must remember per-row letter position.

## Gates (executed, all green)

- G0 machinery sha256 == registration; G1 receipt sha256; G2 replay counters
  + row sequence on all 10 panels; G3 30/30 exact `evaluate()` probes
  reproduce receipt (C_DP, C_Dxx, C_Dplus, f_Bprime, gap4, regime);
  G4 51 canonical round-trip + commutation-invariance checks; G5 cross-panel
  key cost consistency (also the discrete-vocabulary control); G6
  anti-instrument AST gate + staged feature table hashed before constancy;
  G7 C_DP == C_Dxx on 13,458/13,458 rows.
- Constancy-checker self-test on synthetic mixed/constant populations passed
  before any real analysis.

## Authority limits

Finite-population statement over the frozen V4 census (13,458 instances, 10
registered panels, unit-cost R6M grammar at the frozen config). Not an all-n
statement; no promotion; `novelty_authority=false`;
`physical_quantum_advantage_claim=false`. A negative terminal is evidence
toward, not a proof of, the vocabulary-level lower bound.
