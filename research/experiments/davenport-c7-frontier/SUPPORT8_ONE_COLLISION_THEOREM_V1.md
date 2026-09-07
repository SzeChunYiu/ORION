# Complete support-8 one-projective-collision elimination — V1

Status: **bounded exact structural theorem; primary exhaustive search complete, independent replay wired separately**. Global `D_3(C_7^3)` and novelty/priority remain `CANNOT_CHECK` until the remaining support-8 Type-A branch and higher support are closed.

Let `B` be a zero-sum sequence over `C_7^3` with

- `|B|=37`,
- `z(B)<=3`,
- `|supp(B)|=8`, and
- exactly seven projective support directions (so one direction contains two distinct actual support values).

Then no such `B` exists.

Equivalently, any hypothetical length-37 obstruction of support eight must have **eight distinct projective directions**.

## Analytic cover

`SUPPORT8_ONE_PROJECTIVE_COLLISION_REDUCTION_V1.md` proves that the seven projected directions form a seven-point `(7,3)`-arc in `PG(2,7)`. Therefore the complete 54-class projective cover from the support-7 campaign applies unchanged.

Write the total occupancies of the seven directions as `t_i<=6`. Their direction deficits `d_i=6-t_i` satisfy

`d_i>=0`, `sum d_i=5`.

There are exactly 462 ordered direction-deficit profiles.

On the doubled direction normalize the two actual values as `x` and `a*x`, with multiplicities `r,s`. Exact one-dimensional 7-short-zero-freeness leaves 18 oriented states. Quotienting only by swapping the two actual support values leaves exactly **9 swap-canonical local states**. For every surviving state,

`h=r+a*s != 0 (mod 7)`.

For each deficit profile and choice of doubled direction, retain only local states with `r+s=t_j`. Across all seven choices of doubled direction this gives exactly **2583 profile/local/doubled-direction states**.

## Scalar/kernel parameterization

Let `q_1,...,q_7` be fixed projective representatives of one of the 54 arc classes. For an unsplit direction, write the actual vector as `lambda_i q_i`; on the doubled direction write the values as `lambda_j q_j` and `a lambda_j q_j`.

The total-zero equation is

`sum_{i != j} t_i lambda_i q_i + (r+a s) lambda_j q_j = 0`.

Define the effective coefficient vector

`c_i=t_i lambda_i` for `i!=j`, and `c_j=(r+a s)lambda_j`.

Every coefficient is nonzero, so `c` is a full-support projective kernel vector of the `3 x 7` projective support matrix. Conversely, for any full-support projective kernel vector `c`, the scalar lift is uniquely recovered (up to one global nonzero scalar) by

`lambda_i=c_i/t_i`, `lambda_j=c_j/(r+a s)`.

Thus the cover is duplicate-controlled by:

1. one of 54 projective support classes;
2. one of its full-support projective kernel vectors, normalized by `c_0=1`;
3. one of 2583 deficit/doubled-direction/local states.

The 54 classes contain **7400** full-support projective kernel vectors in aggregate, hence the total canonical lift count is

`7400 * 2583 = 19,114,200`.

## Primary exact result

`search_support8_one_collision_v1.cpp` checks every one of the 19,114,200 canonical total-zero lifts.

For each lift it first performs an exact 7-short-zero-free test. Exactly

**15,844**

lifts survive this necessary condition.

For every survivor it then performs an exact four-pack test. Since all zero-sum blocks have length at least eight, any four-partition of 37 terms has two successive smallest blocks of length 8 or 9 and every block has length at most 13. The primary engine enumerates the required zero-sum count vectors and tests the resulting complements exactly.

Result:

- canonical total-zero lifts: **19,114,200**;
- 7-short-zero-free lifts: **15,844**;
- short-free lifts with a four-pack: **15,844**;
- survivors with packing number at most three: **0**.

Per-class totals and short-free counts are frozen in `SUPPORT8_ONE_COLLISION_RESULT_V1.json`.

## Independent verifier

`verify_support8_one_collision_independent_v1.cpp` deliberately changes the two load-bearing scientific tests:

- short-zero-freeness is checked by a flat independently generated list of all eight-coordinate count vectors of total weight 1 through 7, rather than the primary recursive early-rejection search;
- four-pack existence is checked by enumerating all zero-sum count vectors of lengths 8 through 13, forming all admissible **pairs** of disjoint zero-sum blocks, and testing whether the complement is another such pair. This is an exact four-block partition test and is structurally different from the primary successive-smallest-block search.

It also freezes the 54 per-class candidate totals and short-free counts, so a changed negative classification cannot silently pass merely because every surviving candidate still four-packs.

## Consequence

Combining this theorem with the complete support-7 theorem gives:

> If a zero-sum sequence `B` of length 37 over `C_7^3` has `z(B)<=3` and support size at most eight, then `|supp(B)|=8` and its eight support elements lie on **eight distinct projective directions**.

The remaining support-8 residual is exactly Type A in `SUPPORT8_DEFICIT_GEOMETRY_V1.md`: one of the 350 eight-point projective classes with no five collinear, after the Property-C deficit filters.

## Boundary

This is a finite, declared branch closure. It does not by itself prove `D_3(C_7^3)=36`, and computation grants no novelty authority.
