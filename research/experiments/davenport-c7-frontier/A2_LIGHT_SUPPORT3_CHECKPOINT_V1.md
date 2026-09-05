# `a=2` light-share support-three checkpoint — V1

Status: **live theorem-development checkpoint after the one-, two-, and three-share eliminations; no generalized Davenport closure claim**.

## Current lower bound on the shared multiplicity

In the first maximal corridor, an exact-support-six support-three companion for the support-four maximal-atom type `a=2` has the light-share form

`V=e3^c x^r y^t`

or the heavy-share form using `g4`.

The heavy-share form is empty prime-uniformly by `A2_HEAVY_SUPPORT3_DOUBLE_TRIPLE_V1.md`.

The light-share files

- `A2_LIGHT_SUPPORT3_ONE_TWO_SHARE_ELIMINATION_V1.md`, and
- `A2_LIGHT_SUPPORT3_THREE_SHARE_ELIMINATION_V1.md`

prove for every prime `p>=7` that `c=1,2,3` are impossible. Therefore

`boxed{c>=4.}`

## Exact upper bound from the multi-copy criterion

Put

`H=(p-1)/2`, `L=ceil(H/2)`, `u=2^(-1)=(p+1)/2`.

The first-corridor light multi-copy criterion requires

`[u k]_p<=p-L`

for every integer `k` from `2` through `2+c`.

For even `k=2j`,

`[u k]_p=j`,

which never reaches the forbidden top block in the relevant range.

For odd `k=2j+1`,

`[u k]_p=H+1+j`.

The first forbidden odd residue occurs at

`j=H-L+1`.

Thus the exact light-overlap ceiling is

`boxed{c_light=2(H-L)=2 floor(H/2)=2 floor((p-1)/4).}`

Combining both bounds, every hypothetical `a=2` light-share support-three equality companion satisfies

`boxed{4<=c<=2 floor((p-1)/4).}`

## Immediate C7 corollary

At `p=7`, the upper bound is

`c_light=2`.

The lower bound is `c>=4`, so the light-share branch is empty. The heavy-share branch was already empty. Therefore:

> **C7 corollary.** For the support-four maximal-atom type `a=2`, no exact-support-six first-corridor support-three companion exists.

For this maximal type, the only remaining support-six equality mechanism at `p=7` is the rank-three support-four companion sharing both unsaturated maximal-atom values.

This corollary is analytic and does not rely on the finite C7 equality-face sweep.

## Small next-prime windows

The exact interval is now very narrow at the next primes:

| `p` | `c_light` | remaining possible `c` |
|---:|---:|---:|
| 7 | 2 | none |
| 11 | 4 | 4 only |
| 13 | 6 | 4, 5, 6 |
| 17 | 8 | 4 through 8 |
| 19 | 8 | 4 through 8 |

Thus the first unresolved stress test is a single multiplicity layer at `p=11`.

## Mechanism learned from `c=3`

The decisive identity remains

`2e3=2g4+e1+e2`.

For `c=3`, doubling kills every interior multiplicity row. The three boundary rows are closed by explicit multipliers split only by `p mod 6`, while `p=7` is removed by the multi-copy ceiling. A complete all-multiplier replay over 9826 atom-compatible rows through prime 1009 leaves no residual.

A hostile mutation that disables the two-for-four synthesis leaves 1309 residual rows. Therefore any general `c` argument must preserve the radial resource cost rather than counting only actual copies of `e3`.

## Next discriminator

The next theorem target is the `c=4` layer. Two complementary routes are registered:

1. derive a symbolic boundary catalogue after doubling eliminates the interior, now split by `p mod 8` or a smaller invariant if possible;
2. exploit that `p=11` has only this one remaining light-share multiplicity and attempt a complete exact-depth closure there as the smallest mutation base.

In parallel, the remaining C7 `a=2` rank-three support-four face should be attacked through simultaneous quotient atomicity rather than through the rank-two relation method.

## Claim ceiling

- The light-share family with `c>=4` is not globally closed here.
- The rank-three support-four equality face remains open.
- The C7 corollary closes only the support-three branch for maximal type `a=2`.
- No `D_3(C_7^3)` value, all-prime `D_k(C_p^3)` formula, or novelty/priority claim is made.
