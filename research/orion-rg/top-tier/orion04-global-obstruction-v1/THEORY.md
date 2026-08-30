# Global saturation obstruction over `C_5^3`

## Object

Let `S` be a length-31 sequence over `C_5^3` with total sum zero and no nonempty zero-sum subsequence of length at most five. The inherited saturation theorem gives positive multiplicities in `{1,2,4}`. Write `a1,b2,c4` for their support counts. Then

```text
a1+b2+c4 = support,
a1+2*b2+4*c4 = 31.
```

The committed M4 parent excludes supports at most 13. The finite grammar has 42 patterns on supports 14–22 and 18 patterns on supports 23–31.

## Local projective-line theorem

A projective line consists of `x,2x,3x,4x`. Independent enumeration of all states in `{0,1,2,4}^4` leaves exactly 21 that are 5-short-free. Consequently a multiplicity-4 point is isolated on its projective line, and two multiplicity-2 points cannot be collinear. Thus any two high-multiplicity support points are linearly independent.

## Supports 14–22

For `c4<=2`, the high-multiplicity subsequence has length `2*b2+4*c4>13=eta(C_5^2)`, hence spans rank three. A basis has profile `(2,2,2)`, `(4,2,2)`, or `(4,4,2)`.

For `c4>=4`, four multiplicity-4 points contribute 16 terms, so their support spans rank three and three are normalized to `e1,e2,e3`.

For `c4=3`, split by the rank of those three points. In rank three they form the basis. In rank two, normalize two to `e1,e2` and enumerate the third plane direction. When `b2>0`, `12+2*b2>13` forces a doubleton outside the plane; when `b2=0`, full rank forces a singleton outside. The plane stabilizer maps that outside point to `e3`.

These rules give 51 exhaustive branches.

## Supports 23–31: uniform rank/plane decomposition

The full sequence spans rank three, since a rank-at-most-two sequence of length 31 contradicts `eta(C_5^2)=13`.

Let `H` be the support of multiplicities two and four.

- If `rank(H)=3`, matroid basis extension gives exactly one of the basis profiles `(2,2,2)`, `(4,2,2)`, or `(4,4,2)`.
- If `rank(H)=2`, two independent high points normalize to `e1,e2`; all remaining high points are restricted to their plane, and an outside singleton normalizes to `e3`.
- If `|H|=1`, the unique high point extends with two singleton points to a basis.
- If `H` is empty, three singleton points form a basis.

The `eta(C_5^2)` inequality removes rank-two branches whenever the high subsequence already has length greater than 13. The resulting complete cover has 18 patterns and 27 branches.

## Exact search invariant

Both engines maintain all sums reachable at exact weights zero through five. The primary engine uses one 128-bit mask per weight and coordinate-mask translations. The independent engine uses five 25-bit coordinate planes packed into AVX2 lanes, with independently implemented cyclic coordinate shifts. Adding a point copies the previous state, translates each exact-weight layer, rejects immediately if zero becomes reachable, and unions the translated layer.

Remaining points of each multiplicity are enumerated in increasing encoded order. In plane branches, remaining doubletons are restricted to `span(e1,e2)`. After every nonseed singleton except one is selected, total sum uniquely forces the last singleton. Distinctness, line isolation, canonical order, and exact short-zero exclusion are checked before acceptance.

The two engines must agree exactly on nodes, leaves, solutions, and every normalized rank-two seed row. Any survivor is preserved as an explicit native sequence.

## Theorem target and authority boundary

If all 78 support-14-through-31 branches have zero solutions, then no length-31 total-zero 5-short-free sequence over `C_5^3` exists, i.e. `31 in C_0(C_5^3)`. Under the committed extremal implication and bound `30<=D_4(C_5^3)<=31`, this gives `D_4(C_5^3)=30`.

The finite theorem does not by itself establish novelty, external independent reproduction, peer review, or venue readiness. Those remain separate gates.
