# `a=2` light-share support-three checkpoint — V1

Status: **live theorem-development checkpoint; no generalized Davenport closure claim**.

## New lower bound on the shared multiplicity

In the first maximal corridor, an exact-support-six support-three companion for the support-four maximal-atom type `a=2` has the light-share form

`V=e3^c x^r y^t`

or the heavy-share form using `g4`.

The heavy-share form is already empty prime-uniformly by `A2_HEAVY_SUPPORT3_DOUBLE_TRIPLE_V1.md`.

`A2_LIGHT_SUPPORT3_ONE_TWO_SHARE_ELIMINATION_V1.md` proves for every prime `p>=7` that the light-share form cannot have `c=1` or `c=2`. Therefore

`boxed{c>=3.}`

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

`boxed{3<=c<=2 floor((p-1)/4).}`

## Immediate C7 corollary

At `p=7`, the upper bound is

`c_light=2`.

The new theorem gives `c>=3`, so the light-share branch is empty. The heavy-share branch was already empty. Therefore:

> **C7 corollary.** For the support-four maximal-atom type `a=2`, no exact-support-six first-corridor support-three companion exists.

For this maximal type, the only remaining support-six equality mechanism at `p=7` is the rank-three support-four companion sharing both unsaturated maximal-atom values.

This corollary is analytic: it combines the prime-uniform one/two-share elimination, the existing heavy-share theorem, and the exact multi-copy criterion. It does not rely on the finite C7 equality-face sweep.

## Small next-prime windows

The exact interval is already narrow at the next primes:

| `p` | `c_light` | remaining possible `c` |
|---:|---:|---:|
| 7 | 2 | none |
| 11 | 4 | 3, 4 |
| 13 | 6 | 3, 4, 5, 6 |
| 17 | 8 | 3 through 8 |

This makes the `a=2` light-share lane a finite-width arithmetic problem at each prime, while preserving a prime-uniform formulation.

## Next discriminator

The relation-multiple search indicates that the `c=3` layer has no arithmetic residual for any prime `p>=11`; the only raw residuals occur at `p=7`, which is already excluded by the multi-copy ceiling. This is discovery evidence, not yet theorem authority.

The next proof task is therefore to extract a clean symbolic `c=3` multiplier argument, preferably without a growing catalogue of congruence cases. In parallel, the remaining C7 `a=2` rank-three support-four face should be attacked through simultaneous quotient atomicity rather than through the rank-two relation method.

## Claim ceiling

- The light-share family with `c>=3` is not globally closed here.
- The rank-three support-four equality face remains open.
- The C7 corollary closes only the support-three branch for maximal type `a=2`.
- No `D_3(C_7^3)` value, all-prime `D_k(C_p^3)` formula, or novelty/priority claim is made.
