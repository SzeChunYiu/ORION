# X1-B k=4 — rank-2 bilinear witness lifts the 13-point residual itself zero-sum-freely

Parent: #900.
Predecessor: `X1B_K4_FINAL_MINRANK_RESULT_2026-08-22.md`.
Committed before searching for the ten fixed triple-block sums.

## Explicit residual kernel coordinates

Use the common rank-2 witness matrix B from the two surviving quotient orbits. With principal set `S=(0,1)`, put

`Y = B[:,S]` and `M=diag(3,4)` over `F_5`.

The 13 row vectors are

```text
(2,0),
(0,4),(0,4),(0,4),(0,4),
(4,4),(4,4),(4,4),(4,4),
(1,0),(1,0),(1,0),(1,0).
```

Embed them as `(a,b,0)` in `F_5^3`.

## Primitive residual zero-sum replay

For orbit `942777`, primitive enumeration gives 305 nonempty quotient-zero-sum position subsets in `C_3^3`. For every one of these masks Z,

`sum_{j in Z} y_j != 0 in F_5^3`.

For orbit `1470123`, the same check holds for all 293 quotient-zero-sum masks.

Therefore, pairing the committed quotient positions with these kernel coordinates gives a **zero-sum-free 13-term residual sequence in `C_3^3 direct-sum C_5^3 ≅ C_15^3`** for each surviving quotient orbit.

This is stronger than an abstract bilinear witness: the final two quotient residuals are compatible with an actual zero-sum-free lift at the residual level.

## Compression of residual block-sum types

Under this common lift, all disjoint quotient-zero-sum pairs use only three unordered kernel block-sum pair types:

```text
((0,2),(3,2)),
((0,2),(0,2)),
((1,0),(2,4)),
```

(with zero third coordinate). Their edge multiplicities differ by orbit, but no other pair value is needed.

## Next exact interface

A hypothetical full C15 counterexample would additionally require ten fixed kernel block sums `t_1,...,t_10 in C_5^3` from the ten quotient-zero-sum triples removed before the 13-point residual, such that for **each** of the three pair types above the 12-term sequence

`t_1...t_10 x y`

is maximal zero-sum-free in `C_5^3`.

Finding such T would show that all currently restored block-sum/group-algebra constraints still admit the quotient obstruction and would force an original-index/global-lift search. Proving no such T exists would eliminate both final quotient orbits simultaneously.

No C15 counterexample or theorem follows from the residual lift alone.