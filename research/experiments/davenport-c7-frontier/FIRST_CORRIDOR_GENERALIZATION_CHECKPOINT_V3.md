# First-corridor Davenport generalization checkpoint — 2026-09-04 V3

Status: **live theorem-development checkpoint after the `a=1` one- and two-share eliminations; no `D_3` closure claim**.

## New theorem since V2

The `a=1` exact-support-six support-three branch has

`V=e3^c x^r y^t`.

V2 proved `c!=1` for every prime `p>=7`. The new file

`A1_LIGHT_SUPPORT3_TWO_SHARE_ELIMINATION_V1.md`

now proves

`boxed{c!=2}`

for every prime `p>=7` as well.

Therefore every hypothetical `a=1` support-three equality companion satisfies

`boxed{c>=3.}`

The `c=2` proof is nearly uniform. A relation-multiple certificate kills the interior and both multiplicity boundaries by explicit multipliers depending only on `p mod 4`; the single exceptional arithmetic base `p=13` is empty by a tiny exact depth table.

## Reusable new mechanism

For a support-three relation

`c s+r x+t y=0`,

multiplication by `n` gives residues

`d=[nc]_p`, `A=[nr]_p`, `B=[nt]_p`.

The pair contains `c+1` actual copies of `s`; any additional required copy can be synthesized as `f1+f2+f3`. Thus the exact term cost for the `d s` part is

`lambda_c(d)=d` for `d<=c+1`,

`lambda_c(d)=3d-2c-2` for `d>c+1`.

Whenever

`A<=r`, `B<=t`, `lambda_c(d)+A+B<=m-1`,

the branch is impossible.

A first uniform corollary already cuts the remaining family:

> if `2<=c<=(p+3)/4` and both new multiplicities exceed `p/2`, doubling produces a forbidden zero-sum.

So low-`c` survivors are forced onto the boundary `r<=q=(p-1)/2`.

## Current distance to the first-corridor support-seven theorem

The target remains

> for prime `p>=7`, a first-corridor maximal pair with support-four maximal atom should satisfy `|supp(UV)|>=7`.

The equality face is now substantially thinner. The main unresolved mechanisms are:

- `a=1` light-share support-three with `c>=3`; the new relation certificate and exact depth collapse both apply;
- `a=2` light-share support-three; the heavy-share side is already eliminated uniformly;
- rank-three four-support companions, especially the `a=2` model;
- any support-four type not removed by the modular-inverse sharing selector must still be discharged analytically rather than by finite controls.

Exact searches at `p=7,11,13,17` remain discovery controls only.

## Best next attack

For `a=1`, combine the new relation-multiple certificate with the observed mixed-subsum phenomenon: after radial pruning, the finite controls are typically killed by a tiny subsequence `x y^j` on the anti-depth side. The desired next lemma is a prime-uniform statement forcing one such mixed power whenever `c>=3` survives every relation multiple.

Keep the rank-three four-support lane separate: simultaneous quotient atomicity is the more natural invariant there.

## Distance to the global generalized Davenport theorem

Closing the first-corridor support-seven statement would be a real prime-uniform theorem and an important bridge, but it would not by itself prove the candidate `D_k(C_p^3)` formula. The global program would still need the other first-failure corridors, maximal atoms with larger support, and the rank-three positive-gain conformal refactor/augmentation step.

The local frontier is now a handful of structured mechanisms; the global theorem remains several structural steps beyond it.

## Claim ceiling

No `D_3(C_7^3)` value, all-prime `D_k(C_p^3)` formula, or novelty/priority claim is made here.
