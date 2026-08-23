# QG-20 Recovery — Complete n=4 Confirmation Protocol V1

**Status:** `FROZEN_AFTER_SEEDED_PANEL_POSITIVE__BEFORE_COMPLETE_N4_CLASSIFICATION`  
**Parent:** QG-20 #863 / #964 recovery programme  
**Discovery freeze:** `QG20_RECOVERY_FEATURE_SEARCH_PROTOCOL_V1.md`

## Immutable discovery carried forward

The prospectively frozen V1 feature search selected exactly one added coordinate:

`negative_weight_sum`

where the coordinate is the sum of Pauli support weights over negative stabilizer-group elements.

The discovery run is immutable:

- base QG-15b 13-coordinate map: `E_floor=43`, `12` mixed cells on all 1,146 n<=3 states;
- augmented map `(phi0, negative_weight_sum)`: `E_floor=0`, `0` mixed cells on all 1,146 n<=3 states;
- sealed seeded n=4 panel, 120 states: base floor `2` in `2` mixed cells; augmented floor `0`, `0` mixed cells;
- independent verifier: `ACCEPT` on all registered checks;
- analyzer replay: byte-identical;
- dual digest: `804aacd8794daae3ba46ac33251725175c3a588f09791e3b70fb1bbaa71e22d2`.

No feature, threshold, subset, seed, or endpoint may change in this confirmation.

## Question

Does the already-selected 14-coordinate map

`phi1 = (phi0, negative_weight_sum)`

remain label-determining on the **complete n=4 StabPrep stabilizer-state space**, rather than only the prospectively seeded 120-state panel?

This is a confirmation of the recovered coordinate, not a new feature search.

## Exact domain

Use the existing exact `qg15_third_family.referee(4)` state graph.

Expected complete n=4 state count is fixed by the existing StabPrep formula:

`2^4 * prod_{k=1..4}(2^k + 1) = 36,720`.

For every exact n=4 state:

1. run the frozen GE donor;
2. rebuild the original 13-vector `phi0`;
3. compute `negative_weight_sum` from the target stabilizer group only;
4. label donor exactness as `C_D == C_opt` using the exact referee;
5. group states by `phi0` and by `phi1` separately;
6. compute cell count, mixed-cell count, and deterministic error floor.

## No-search rule

There is **no feature selection** in this confirmation.

The only admitted added coordinate is the already frozen `negative_weight_sum`. If it fails, the result is retained and the next successor must move to the full QG-20 quotient / a new prospectively frozen coordinate grammar. The n=4 failures may not be used to redefine V1 and rerun under the same protocol.

## Independent verifier

A separate implementation must:

- rebuild `negative_weight_sum` by direct bit decoding of encoded stabilizer elements;
- independently rebuild `phi0` from donor outputs and primitive structural functions;
- independently recompute all 36,720 donor-exact labels;
- independently recompute base and augmented cell statistics;
- agree exactly on all counts and floors.

## Positive terminal

All are required:

- exact n=4 domain count = `36,720`;
- base map statistics are reported without claim preference;
- augmented `phi1` mixed-cell count = `0`;
- augmented `phi1` deterministic error floor = `0`;
- independent verifier `ACCEPT` with exact count/stat agreement;
- deterministic analyzer replay.

Terminal:

`QG20_RECOVERY_NEGATIVE_WEIGHT_SUM_DETERMINES_DONOR_EXACTNESS_COMPLETE_N4`

Honest alternatives:

- `QG20_RECOVERY_NEGATIVE_WEIGHT_SUM_REFUTED_COMPLETE_N4`
- `QG20_RECOVERY_COMPLETE_N4_DUAL_DISAGREEMENT`
- `CANNOT_CHECK`.

## Claim boundary

A positive confirms the recovered coordinate on the complete n<=4 StabPrep domains (with n<=3 discovery and n=4 confirmation). It is still **not** an all-n theorem, not proof that this is the globally minimal sufficient state coordinate, not a new compiler, and not a physical quantum-advantage claim.