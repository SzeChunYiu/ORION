# Support-8 projective deficit reduction — V1

Status: **analytic structural reduction**. Novelty/priority: **CANNOT_CHECK**.

Let `G=C_7^3`, and let `B` be a zero-sum sequence with `|B|=37` and zero-sum packing number `z(B)<=3`.

The existing `D_2(G)=29` reduction implies that `B` is 7-short-zero-free: a zero-sum subsequence of length at most seven would leave a zero-sum complement of length at least 30, which already has three disjoint zero sums, giving four in `B`.

Hence:

- every one-dimensional subgroup contains at most 6 terms of `B` (7 terms in `C_7` contain a nonempty zero sum of length at most 7);
- every two-dimensional subgroup contains at most 18 terms of `B` (use `eta(C_7^2)=19`).

## Projective deficit lemma

Suppose the support of `B` occupies exactly `r` projective directions. Let `n_i` be the total occupancy of direction `i`. Then

`1 <= n_i <= 6`, `sum_i n_i=37`.

Put `d_i=6-n_i`. Then

`d_i>=0`, `sum_i d_i=6r-37`.

If `h` of the projective directions are collinear, the corresponding vectors lie in a two-dimensional subgroup, so

`6h - sum_{i in line} d_i <= 18`.

Since `sum_{i in line} d_i <= 6r-37`, any collinear set of size `h=r-3` would have occupancy at least

`6(r-3)-(6r-37)=19`,

contradicting the plane cap 18.

Therefore:

> **No `r-3` occupied projective directions can be collinear.**

This is a capacity/deficit form of the finite-geometry obstruction.

## Consequence for support size eight

Assume `|supp(B)|=8`. Since each projective direction contains at most 6 terms and `|B|=37`, the number `r` of projective directions is at least 7. Thus only two branches exist.

### Branch A: `r=7`

Exactly one projective direction contains two distinct support elements and the other six directions contain one support element each. The projective deficit lemma forbids four collinear directions. Hence the seven directions form a seven-point `(7,3)`-arc in `PG(2,7)`.

The existing projective generator has already classified these into exactly 54 projective equivalence classes. Therefore the entire one-projective-collision support-8 branch reduces to:

1. one of the 54 frozen seven-direction classes;
2. a choice of the doubled direction;
3. two distinct nonzero scalar representatives on that direction;
4. an occupancy split on the doubled direction and occupancies on the other six directions;
5. the total-zero congruence and exact four-pack test.

This is a finite extension of the completed support-7 computation, not a new unconstrained search.

### Branch B: `r=8`

All eight support elements lie on distinct projective directions. The deficit lemma forbids five collinear directions, so the projectivized support is an eight-point set in `PG(2,7)` with at most four points on any line, i.e. an `(8,4)`-arc in the usual finite-geometry language.

This gives a separate finite-geometry classification/enumeration target.

## Research consequence

The next support layer should be attacked projectively rather than as arbitrary vectors in `F_7^3`:

- close Branch A by reusing the 54 `(7,3)`-arc representatives and adding exactly one scalar collision;
- independently generate/canonicalize the `(8,4)`-arc classes for Branch B;
- for each class, solve total-zero scalar/occupancy fibers and run the existing exact packing referee.

A complete closure of both branches would upgrade the current theorem from `|supp(B)|>=8` to `|supp(B)|>=9` for any hypothetical length-37 obstruction.
