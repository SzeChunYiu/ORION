# ORION-04 M4 theory: exact exclusion of supports 11, 12, and 13

## Scope

This packet advances only the bounded `C_5^3` obstruction theorem. It starts from the committed M3 result that a length-31, total-zero sequence with no nonempty zero-sum subsequence of length at most five must have support at least 11. It does not use the prospective support-through-22 ledger as theorem evidence.

Let `a`, `b`, and `c` be the numbers of support points having multiplicity 1, 2, and 4. The saturation-defect theorem excludes multiplicity 3 and the exponent bound excludes multiplicity at least 5. Therefore

```text
a + b + c = s,
a + 2b + 4c = 31.
```

For `s = 11, 12, 13`, solving these equations in nonnegative integers gives exactly:

```text
s=11: (a,b,c)=(1,5,5),(3,2,6)
s=12: (a,b,c)=(1,7,4),(3,4,5),(5,1,6)
s=13: (a,b,c)=(1,9,3),(3,6,4),(5,3,5),(7,0,6)
```

The independent checker recomputes this list rather than trusting the result file.

## Rank split and normalization

Four multiplicity-4 points contribute 16 terms. If those points lay in a rank-at-most-two subgroup, `eta(C_5^2)=13` would force a zero-sum subsequence of length at most five. Thus every row with `c>=4` has three multiplicity-4 points spanning rank three; `GL(3,5)` sends them to `e1,e2,e3`.

The sole row not covered by that forced-rank argument is `(1,9,3)`. Its three multiplicity-4 points have either rank three or rank two. The rank-three branch uses the same basis normalization. In the rank-two branch, two independent points are normalized to `e1,e2`; projective-line isolation makes the third `a e1+b e2` with `a,b` both nonzero. The checker enumerates all 16 coefficient pairs. Seven fail before depth-first enumeration because the normalized seed already violates short-freeness; the remaining nine exact searches are recorded individually.

## Exact state invariant

Both engines maintain reachability by exact subsequence weight through five. In the primary engine, each weight is a 125-bit mask stored in `unsigned __int128`. In the replay engine, the same state is an explicit byte array `reach[weight][sum]`. Adding a copy of a support point shifts the previous weight layer by that group element. A branch is rejected exactly when zero becomes reachable at weight 1, 2, 3, 4, or 5.

Support points within each multiplicity stratum are chosen in increasing encoded order, so every normalized support is visited once. A point sharing a projective line with a multiplicity-4 point is rejected by the symbolic short-zero-sum lemma. The final singleton is forced by the total-sum equation and is checked for distinctness, line conflict, canonical order, and the exact reachability invariant.

## Theorem step

The two state representations agree on every rank-three row and on every rank-two seed row. Every branch has zero solutions. Since M3 already excludes support at most 10 and the multiplicity equations list every support-11, support-12, and support-13 row, any remaining obstruction has support at least 14.

## Authority boundary

The accepted authority is exactly:

> A length-31 total-zero sequence over `C_5^3` with no nonempty zero-sum subsequence of length at most five, if one exists, has support at least 14.

This packet does not prove support at least 23, membership of 31 in `C_0(C_5^3)`, either exact value of `D_4(C_5^3)`, novelty, venue suitability, or external independent replay.
