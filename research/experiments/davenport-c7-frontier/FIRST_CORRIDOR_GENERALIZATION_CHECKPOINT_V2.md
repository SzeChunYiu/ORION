# First-corridor Davenport generalization checkpoint — 2026-09-04 V2

Status: **live theorem-development checkpoint after the `a=1` one-share elimination; no `D_3` closure claim**.

## New theorem since V1

In the first maximal corridor

`C_1(p)=(p+1,(3p-1)/2,3p-2)`,

let the support-four maximal atom have type `a=1`. At exact pair support six, a support-three rank-two companion has the form

`V=e3^c x^r y^t`.

`A1_LIGHT_SUPPORT3_ONE_SHARE_ELIMINATION_V1.md` proves symbolically that for every prime `p>=7`,

`boxed{c!=1}`.

Hence every hypothetical `a=1` support-three equality companion now satisfies

`boxed{c>=2}`.

The proof has three new ingredients:

1. in the saturated basis, the `a=1` depth collapses to `rho(z)=S(z)-2` off the coordinate hyperplanes and `rho(z)=S(z)` on them;
2. the boundary multiplicity `(1,(p-1)/2,p-1)` forces the `p-1`-fold value to have radial residue pattern `(1,a,p-a)` by a second-moment jump-set argument;
3. the induced companion value `x=2(s-y)` then violates the pair depth inequality, including the unique central case via `j0=ceil((p+3)/6)`.

The interior multiplicity range dies earlier by doubling the atom relation, using the two available copies of the shared light value across `U` and `V`.

## Current first-corridor support-seven target

The evidence still supports

> for prime `p>=7`, a first-corridor maximal pair with support-four maximal atom should satisfy `|supp(UV)|>=7`.

The proof is not complete. The equality face is now narrower, but the following analytic work remains:

- `a=1` light-share support-three companions with shared multiplicity `c>=2`;
- `a=2` light-share support-three companions (the heavy-share branch is already eliminated uniformly);
- rank-three four-support companions, with the `a=2` face still the clearest difficult model;
- any additional support-four types allowed by the modular-inverse sharing selector must be discharged rather than inferred away from finite searches.

The finite equality-face searches at `p=7,11,13,17` remain discovery controls, not authority for these missing branches.

## Distance to the larger generalized Davenport theorem

Even a complete first-corridor support-seven theorem would be an important local theorem, not the final generalized Davenport formula. The larger program still needs to connect the maximal-pair geometry to the surviving rank-three first-failure configurations, other factorization corridors, and the positive-gain conformal refactor/augmentation step recorded elsewhere in the Davenport ledger.

So the frontier has changed from an uncontrolled search to a small list of structured equality mechanisms, but the global theorem is not yet one lemma away.

## Next atomic target

Attack the `a=1`, `c>=2` family using the new saturated-coordinate depth collapse. The preferred route is to combine the exact multi-copy bound on `c` with mixed `x/y` rectangle sums, rather than return to arbitrary rank-three enumeration.

A parallel lane should keep the `a=2` rank-three four-support face separate, where the simultaneous quotient-atom constraints are more natural than the rank-two rectangle argument.

## Claim ceiling

No `D_3(C_7^3)` value, all-prime `D_k(C_p^3)` formula, or novelty/priority claim is made here.
