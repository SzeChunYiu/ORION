# QG-20 Recovery V4 — Signed Complete Weight Enumerator Protocol V1

**Status:** `FROZEN_AFTER_V3_NEGATIVE__BEFORE_V4_OUTCOME`  
**Owner:** QG-20 #863  
**Recovery coordinator:** #964

## Immutable recovery chain

On the complete `n=4` StabPrep domain (36,720 states; 1,640 GE-donor-exact positives):

| state map | floor | mixed cells |
|---|---:|---:|
| original QG-15b `phi0` | 586 | 54 |
| `phi0 + negative_weight_sum` | 128 | 20 |
| V2 best prefrozen companions (`+ n_negative + y_position_union`) | 85 | 12 |
| V3 simple signed weight enumerator `(S_1..S_4)` | 33 | 7 |

All reported maps were independently reconstructed. V3 used no feature selection and returned:

`QG20_RECOVERY_V3_SIMPLE_SIGNED_WEIGHT_NONIDENTIFYING__COMPLETE_ENUMERATOR_OR_QUOTIENT_REQUIRED`.

## Why V4 is licensed

The pre-V2 donor note and the frozen V3 protocol explicitly predeclared the next escalation if simple signed weight remained non-identifying: use the **signed complete Pauli weight enumerator**, which retains X/Y/Z composition as well as sign.

This is donor mathematics. V4 claims no invention of complete/signed quantum weight enumerators.

## Frozen representation

For each signed stabilizer element `lambda(P) P`, let:

- `a = # X-only tensor positions`,
- `b = # Y tensor positions`,
- `c = # Z-only tensor positions`,
- `lambda(P) in {+1,-1}`.

For every triple `(a,b,c)` with `a,b,c >= 0`, `1 <= a+b+c <= 4`, define

`C_{a,b,c} = sum_{P with composition (a,b,c)} lambda(P)`.

The V4 vector contains **all** such coefficients in fixed lexicographic order `(a,b,c)`. There is no subset selection, coefficient pruning, learned projection, or post-outcome compression.

The tested map is:

`phi4 = (original QG-15b 13-vector, C_{a,b,c} for all nonzero triples with total<=4)`.

For context only, report the already-frozen `phi0`, `phi1`, `phi2`, and `phi3` statistics. They do not select V4.

## Exact domain and gold

- `n=4` complete exact stabilizer-state graph from `qg15_third_family.referee(4)`;
- expected states: `36,720`;
- frozen GE donor;
- exact donor-exact label `C_D == C_opt`.

V4 is a same-domain representation recovery. The representation family was predeclared before the V3 result, but all n=4 labels have been used in prior diagnosis; therefore even a positive V4 must be followed by a held-out-size confirmation.

## Independent verifier

A separate implementation must:

1. decode each encoded stabilizer element directly;
2. count X-only, Y, and Z-only positions independently;
3. accumulate sign `+1/-1` into the exact composition coefficient;
4. independently rebuild original `phi0` and exact donor label;
5. reproduce all map cell/mixed/floor statistics;
6. verify the V4 vector includes the complete fixed coefficient set and no selection occurred.

## Positive terminal

All required:
- domain count `36,720`;
- V4 floor `0`;
- V4 mixed cells `0`;
- analyzer deterministic replay;
- independent verifier `ACCEPT` with exact statistic agreement;
- complete coefficient vector fixed before outcome; no selection.

Terminal:

`QG20_RECOVERY_V4_SIGNED_COMPLETE_WEIGHT_ENUMERATOR_DETERMINES_DONOR_EXACTNESS_COMPLETE_N4`

Honest alternatives:
- `QG20_RECOVERY_V4_COMPLETE_ENUMERATOR_NONIDENTIFYING__EXACT_QUOTIENT_REQUIRED`
- `QG20_RECOVERY_V4_DUAL_DISAGREEMENT`
- `CANNOT_CHECK`.

## Next step after V4

- **If positive:** freeze a new `n=5` panel with the V4 representation unchanged and obtain exact target costs through an independently verified targeted Dijkstra/referee. Do not search V4 coordinates on n=5.
- **If negative:** stop hand-designed weight-enumerator escalation. Execute the full QG-20 continuation-equivalence quotient / minimal distinguishing suffix programme and derive a human coordinate only after that exact state object is sealed.

## Claim boundary

A V4 positive is only a complete-n=4 determination result for the frozen StabPrep GE-donor exactness label. It is not all-n state sufficiency, global minimality, a new compiler, novelty for weight enumerators, or physical quantum advantage.