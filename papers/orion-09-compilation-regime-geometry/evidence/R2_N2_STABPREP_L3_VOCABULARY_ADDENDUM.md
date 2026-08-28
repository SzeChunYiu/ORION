# R2 revival addendum — N2 (StabPrep vocabulary floor) and N4 residual (3/120 lattice errors)

Operator mandate 2026-08-28: every recorded negative gets a genuine revival attempt before any
freeze is final. This addendum amends the frozen claim rows **without touching any frozen file**
(the V1/V2 science-freeze pins stay intact); the amendment vehicle is this file plus the results
receipt beside it.

| Claim row | Old verdict | Failure attribution (ONE stage) | Lever applied | New verdict | Evidence |
|---|---|---|---|---|---|
| QG1V2-C7 (N2) | 43/1146 irreducible floor in V1 (QG-15b); 1 surviving mixed cell in V2 (QG-15c); 5-floor/3-mixed-cells in the 66-feature L2 donor-path vocabulary | Feature stage: every committed vocabulary statistic is a **multiset/sign-blind function of the stabilizer generators** — blind exactly where two states share donor step-cost profile, weight enumerator and tensor factor sizes but differ in negative-sign census | Mechanic improvement (not outcome tuning): L3 = V2 (33) + L2 donor-path (53) + NEW 41-feature sign-aware permutation-covariant STATE block (negative-sign census; sign-split weight counts; sign-split Y-counts; sign-split (x mod 2, z mod 2) classes; per-qubit column X/Y/Z marginal stats), frozen in R2_N2_STABPREP_L3_VOCABULARY_PROTOCOL_V1.md (sha256 c78b0e0b35663cdbe4c66dfe89aeb6e0154941e43380b0e0b203ad5fd3944135) BEFORE the run | **POSITIVE CONVERSION (pre-frozen criterion H-A: floor(L3)==0 on the complete 1146 n<=3 domain)** — mixed_cell_count 0, irreducible_error_floor 0, all gates green. See the memorization disclosure below; the conversion is at the vocabulary-existence level, not a compact-law claim | R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json (result_digest 0042e934fff27274b809d4ef200e97a7210b1530b0317d54449e25e35e574f41; stage1_digest printed before any n=4 referee output) |
| QG1V2-C6 (N4 residual 3/120) | QG-23 H1 refuted: V2 normalization does not transfer; lattice predicate 3/120 errors on the frozen 120-state n=4 panel | Generalization stage: the same state-structural block that determines n<=3 does not transfer out-of-sample — panel coverage under parity-split CV is 2/120 | Re-test of the frozen L3 under the pre-frozen H-B criterion (in-panel floor==0 AND CV errors==0; IMPROVED-CONDITIONAL iff errors<=3 and <32 and shuffle p<0.05) | **NOT IMPROVED (honest stand)** — in-panel floor 0 but CV errors 32/120 (= parent cell-lookup baseline, not <32), errors_among_covered 0, shuffle-null mean 32.41, empirical p 0.51. The N4 residual negative stands; the lever that converts N2 does not generalize to unseen n=4 states | same receipt, stage2 block |

## Pair-level witness (re-test vs strongest parent)

The single V2 surviving mixed cell's minimal_distinguishing_pair (QG-15c receipt, n=3,
donor_step_cost_profile [7,4,0] identical on both members, same weight enumerator, same tensor
factor sizes) was re-fed through the L3 map with committed primitives:

- donor-exact member canonical_key [0,7,26,29,47,104,114,117]: C_D=11=C_opt (label True),
  negative_sign_census 3;
- trade member canonical_key [0,7,25,30,41,46,48,119]: C_D=11 vs C_opt=9 (label False),
  negative_sign_census 1;
- V2 33-block: **identical** (the parent's blindness, reproduced);
- L3 STATE block: **separated at 12/41 coordinates**, first differing coordinate = index 0 =
  negative_sign_census (3 vs 1) — exactly the mechanism QG-25 identified.

## Memorization disclosure (gate, pre-frozen)

Stage 1 determination is near-injective on the domain: 1109 unique cells / 1146 instances
(compression ratio 0.9677), 1072 singleton cells. The floor-0 conversion therefore proves
**existence of a sign-aware feature class that determines donor-exactness on n<=3**; it does NOT
establish a compact or low-dimensional law, and (per stage 2) it does not yield an out-of-sample
predictor. Both limits are recorded in the receipt; no promotion of N2 beyond
vocabulary-existence is claimed. Authority ceiling NOT_R6 unchanged.

## Provenance

Modules imported unmodified (sha256 in receipt): research/extensions/orion-qg/qg15_third_family.py,
qg15c_vocabulary.py, qg15c_enlarged_vocab.py. Script: scripts/r2_revive_stabprep_l3_vocabulary.py
(rc=0). No network, no chemistry data, no protected subject, no criterion change after outcomes
were seen (protocol frozen and hashed before the run; stage-1 digest printed before any n=4
referee computation).
