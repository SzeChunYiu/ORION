# First-corridor Davenport generalization checkpoint — 2026-09-04 V3

Status: **live theorem-development checkpoint after the `a=1` one- and two-share eliminations; no `D_3` closure claim**.

## New theorem since V2

In the first maximal corridor, let the support-four maximal atom have type `a=1`. An exact-support-six support-three companion has form

`V=s^c x^r y^t`,

where `s` is the light unsaturated maximal-atom value.

`A1_LIGHT_SUPPORT3_ONE_SHARE_ELIMINATION_V1.md` already proves `c!=1` for every prime `p>=7`.

`A1_LIGHT_SUPPORT3_TWO_SHARE_ELIMINATION_V1.md` now proves

`boxed{c!=2}`

for every prime `p>=7`.

Therefore every hypothetical companion in this branch satisfies

`boxed{c>=3.}`

## Mechanism

For `c=2`, every atom-compatible multiplicity row is eliminated by a scalar multiple of the companion relation lifted through the saturated maximal atom, except one arithmetic resonance:

`(p,c,r,t)=(13,2,6,11)`.

That isolated row is discharged exactly. In saturated coordinates its plane is parameterized by a vector `x` with pairwise distinct coordinates and `y=s+3x`. Of 1716 structural values, 312 pass singleton depth, and all 312 fail a pure-power depth inequality. A separate occurrence-DP verifier reproduces zero exact pair survivors.

## Current frontier

The `a=1` support-three equality branch is now reduced to shared multiplicity `c>=3`. The exact multi-copy criterion still imposes an arithmetic upper bound on `c`, so the next target is no longer an unbounded overlap problem.

The preferred next discriminator is to determine whether the scalar-depth lifting lemma extends to all `c` below a positive fraction of `p`, leaving only a central resonance band for mixed rectangle analysis.

In parallel, the `a=2` light-share and rank-three four-support branches remain separate theorem lanes.

## Claim ceiling

No `D_3(C_7^3)` value, all-prime `D_k(C_p^3)` formula, or novelty/priority claim is made here.
