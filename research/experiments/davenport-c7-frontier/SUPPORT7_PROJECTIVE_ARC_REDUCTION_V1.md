# Any support-7 length-37 obstruction is a `(7,3)`-arc in `PG(2,7)` — V1

Status: **analytic reduction**, conditional only on donor inputs `D_2(C_7^3)=29` and `eta(C_7^2)=19`. Novelty/priority: **CANNOT_CHECK**.

Let `B` be a zero-sum sequence over `C_7^3` with `|B|=37` and zero-sum packing number `z(B)<=3`.

## Multiplicity cap and minimum support

No element can occur seven times. If `g^7|B`, then `g^7` is zero-sum and the total-zero complement has length 30. Since adjoining `g^7` to any three disjoint zero-sums in the complement would give four in `B`, that complement has packing number at most two, contradicting `D_2(C_7^3)=29`.

Hence every multiplicity is at most six and `|supp(B)| >= ceil(37/6)=7`.

Assume now `|supp(B)|=7`.

## Distinct projective directions

The total occupancy of any one-dimensional subgroup is at most six. Seven terms in a copy of `C_7` contain a nonempty zero-sum; removing it leaves a total-zero complement of length at least 30 with packing number at most two, contradicting `D_2=29`.

If two of the seven support elements represented the same projective point, their common one-dimensional subgroup would contribute at most six terms, while the other five support elements contribute at most `5*6=30`, giving `|B|<=36`. Contradiction.

Thus the seven support elements determine seven distinct points of `PG(2,7)`.

## No four projective support points are collinear

The total occupancy of any two-dimensional subgroup is at most 18. This follows from `eta(C_7^2)=19`: 19 terms in such a subgroup contain a zero-sum subsequence of length at most seven. Removing it would again leave a total-zero complement of length at least 30 with packing number at most two, impossible by `D_2=29`.

If four projective support points were collinear, the corresponding four vector directions would lie in one two-dimensional subgroup and contribute at most 18 terms. The remaining three support elements contribute at most `3*6=18`. Hence `|B|<=36`, contradiction.

Therefore the projectivized support is a seven-point set in `PG(2,7)` with no four collinear.

## Computational consequence

The companion generator `generate_support7_projective_arcs_v1.py` independently fixes a projective frame, enumerates all frame-containing candidates, and quotients by internal frame changes. It obtains 57 projective points, 18,451 normalized candidates, 54 projective equivalence classes, 53 classes with a collinear triple, and one ordinary seven-arc class with no three collinear. The split `53+1` independently matches the published `[7,3,4]_7` NMDS classification plus the ordinary MDS-type seven-arc class; the literature count is used as an external control, not as executable cover authority.
