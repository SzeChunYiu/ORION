# Non-quantum math M3 — exact support-10 exclusion replay

Date: 2026-08-24

Base: `f04e5b27da6d88ac8c62638671c331f6e6b6b8bf`

Owner: `NON_QUANTUM_MATH`

Status: **FROZEN AFTER A LOCAL TIMING SCOUT REPRODUCED THE ARCHIVED SUPPORT-10 OUTCOME, BEFORE THE SIGNED SOURCE/GENERIC/NATIVE CAMPAIGN**

This is confirmatory, post-outcome work. It has no prospective-validation authority.

Authority ceiling: bounded exact exclusion of support ten for a length-31 total-zero 5-short-free sequence over `C_5^3`.

## Parent theorem

M2 established, with a human symbolic proof and isolated dual replay, that any length-31 total-zero 5-short-free sequence over `C_5^3` has support at least ten. It also proved that every support-greater-than-eight candidate is saturated and hence has no multiplicity-three point.

M3 binds the signed M2 result and advances exactly one stratum.

## Complete support-10 pattern reduction

Every multiplicity is at most four. At support ten, let `c_j` be the number of support points of multiplicity `j`. Since multiplicity three is impossible,

`c_1+c_2+c_4=10`,

`c_1+2c_2+4c_4=31`.

The nonnegative integer solutions are exactly

- `(c_1,c_2,c_4)=(3,0,7)`, or `1^3 4^7`;
- `(c_1,c_2,c_4)=(1,3,6)`, or `1 2^3 4^6`.

Thus no other support-10 multiplicity pattern may be searched or silently added after outcome.

## Rank-three normalization

Both patterns contain at least six multiplicity-four support points. Four such points cannot all lie in a rank-two subgroup: their 16 terms would exceed the donor threshold `eta(C_5^2)=13` and create a zero-sum subsequence of length at most five. Therefore the multiplicity-four stratum spans rank three.

Choose an independent triple of multiplicity-four points and map it by `GL(3,5)` to the standard basis. This normalization is complete. A distinct support point on the same projective line as a multiplicity-four point is impossible because the four copies plus the suitable scalar mate contain a zero-sum of length at most five.

## Exact finite discriminator

The frozen u128 and byte programs implement the same complete normalized grammar with different exact-weight subset-sum states:

- GNU u128 translation masks for weights zero through five;
- explicit byte reachability indexed by weight and group sum.

Each program enumerates the remaining multiplicity-four, multiplicity-two, and non-final singleton points canonically. The final singleton is forced by the total-sum equation. A branch is rejected exactly when adding a term creates a nonempty zero-sum subsequence of length at most five.

Registered rows:

| pattern | nodes per engine | leaves per engine | solutions per engine |
|---|---:|---:|---:|
| `1^3 4^7` | 210,700 | 3,558 | 0 |
| `1 2^3 4^6` | 272,119 | 0 | 0 |

The formal build is `gcc -std=gnu11 -O3 -Wall -Wextra -Werror`. GNU mode deliberately admits the frozen u128 extension; every actual warning fails the build.

## Replay contract

The signed source lane must:

1. bind the M2 result digest and file hash;
2. bind both frozen support-10 C-source hashes;
3. build both sources warning-clean in a fresh temporary directory;
4. run both registered patterns through both executables;
5. require exact agreement on parameters, nodes, leaves, and zero solutions;
6. delete temporary executables after the run;
7. preserve all post-outcome and authority boundaries.

The generic lane independently solves the multiplicity equations, checks the rank-three premise and signed identities, and rejects any changed count or boundary. The native campaign fails closed unless all source and generic fields agree.

## Strong terminal

`NONQUANTUM_M3_C5CUBED_SUPPORT10_BOTH_DEFICIT_PATTERNS_EXCLUDED__OBSTRUCTION_SUPPORT_AT_LEAST11`

## Authority boundary

M3 does not exclude support eleven or greater, upgrade the archived support-23 packet, prove `31 in C_0(C_5^3)`, or decide exact `D_4(C_5^3)`. It is local post-outcome replay, not external independent replication or prospective validation. No novelty, venue, quantum, physical-resource, or CI authority is granted.
