# Mathematical Extensions R5 — Exact Classification on the 26-Diagonal

Date: 2026-08-25

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md` and `MATHEMATICAL_EXTENSIONS_R4.md`

Status: rigorous finite-classification addendum. It advances the structural frontier but does not determine `D_4(C_5^3)` or prove `C_0(31)`.

## 1. Purpose

R4 moved the first rank-silent diagonal to

`s+c_4=26`,

where the high-multiplicity subsequence has length ten. This pass classifies every possible rank-two high-multiplicity sequence on that diagonal. Two of the three multiplicity branches are impossible. The remaining branch reduces to five explicit normal forms.

## 2. Multiplicity profiles on the diagonal

The V3 equations give

`c_2=31-s-3c_4`,

`c_1=2s-31+2c_4`,

and

`|H|=62-2(s+c_4)`.

When `s+c_4=26`, `|H|=10` and the admissible rows are

| `s` | `c_1` | `c_2` | `c_4` | multiplicity profile of `H` |
|---:|---:|---:|---:|---|
| 26 | 21 | 5 | 0 | `2^5` |
| 25 | 21 | 3 | 1 | `4,2,2,2` |
| 24 | 21 | 1 | 2 | `4,4,2` |

Rank one is impossible because a length-ten sequence in a cyclic group of order five contains a nonempty zero sum of length at most five. The only low-rank case is therefore rank two.

## 3. Exact rank-two classification

**Theorem NQ4 (length-ten repeated-stratum classification).** Let `H` be a rank-two sequence over `C_5^2`, of length ten, with every multiplicity in `{2,4}`, and with no nonempty zero-sum subsequence of length at most five. Then its multiplicity profile is `4,4,2`.

Write the two multiplicity-four points as `a,b` and the multiplicity-two point as `c`. The points `a,b` are independent. After taking the ordered basis `a=e_1`, `b=e_2` and writing

`c=u e_1+v e_2`,

the allowed coordinate pairs are exactly

`(1,1),(1,2),(1,3),(1,4),(2,1),(2,3),(3,1),(3,2),(4,1)`.

Up to swapping the two fourfold basis points, there are exactly five normal forms, represented by

`(1,1),(1,2),(1,3),(1,4),(2,3)`.

**Proof.** The three possible multiplicity profiles are `4,4,2`, `4,2,2,2`, and `2^5`. The last two are excluded by the exact finite classification in Section 4.

For profile `4,4,2`, the fourfold points cannot lie on the same one-dimensional subspace. If `b=t a` with `t=2,3,4`, respectively, then

`3a+b`, `2a+b`, or `a+b`

is a zero sum of length at most four; equality of the points would supply five equal copies. Hence `a,b` are independent.

Normalize them to the standard basis and write `c=(u,v)`. Both coordinates are nonzero, otherwise `c` lies on a basis line and gives a short zero sum with the corresponding fourfold point. A zero sum using one copy of `c` must use the unique coefficients

`x=-u mod 5`, `y=-v mod 5`,

chosen in `{1,2,3,4}`. It is forbidden exactly when `x+y+1<=5`. A zero sum using two copies of `c` similarly uses

`x'=-2u mod 5`, `y'=-2v mod 5`

and is forbidden exactly when `x'+y'+2<=5`. There is no zero sum using zero copies of `c` because `a,b` are independent and fewer than five copies of either are available.

Thus short-freeness is equivalent to

`x+y>=5` and `x'+y'>=4`.

Direct evaluation of the sixteen nonzero coordinate pairs gives the displayed nine pairs. Swapping `a,b` exchanges `u,v`, leaving the five stated orbits. ∎

## 4. Finite proof certificate for the excluded profiles

The exclusion of `4,2,2,2` and `2^5` is a finite theorem over `C_5^2`, not an asymptotic computation. The public verifier supplies two independently implemented zero-sum engines on the complete state space:

1. direct enumeration of every bounded submultiplicity vector of total length at most five; and
2. a bounded-knapsack dynamic program indexed by subsequence length and group sum.

They agree on every state. The raw classifier checks

- 42,480 rank-two support/multiplicity assignments of profile `4,2,2,2`; and
- 42,504 assignments of profile `2^5`,

with zero survivors in both cases. As a separately normalized completeness check, fix an independent pair to `e_1,e_2`. The normalized search checks all 231 remaining support pairs for `4,2,2,2` and all 1,540 remaining support triples for `2^5`; again there are zero survivors.

For `4,4,2`, the raw search checks 6,000 rank-two assignments and finds 2,160 labeled survivors, while the normalized classifier returns exactly the nine coordinate pairs and five swap classes in Theorem NQ4.

The finite proof is independently replayable and small enough to audit line by line. It is reported as `FINITE_EXACT`, not promoted to a symbolic all-prime theorem.

## 5. Consequence for the length-31 obstruction

**Theorem NQ5 (26-diagonal reduction).** Let `S` be a saturated, 5-short-free, total-zero sequence of length 31 over `C_5^3`. Suppose `s+c_4=26`.

1. If `(s,c_4)=(26,0)` or `(25,1)`, then `rank(span H)=3`.
2. If `(s,c_4)=(24,2)`, then either `rank(span H)=3`, or `H` has profile `4,4,2` and, after a `GL(3,5)` change of basis, its rank-two part is one of the five normal forms in Theorem NQ4.

**Proof.** The three rows have exactly the profiles listed in Section 2. Rank one is impossible. Theorem NQ4 excludes rank two for `2^5` and `4,2,2,2`, proving the first item. In the last row, Theorem NQ4 gives the complete rank-two alternative. ∎

**Corollary NQ6.** Every branch through `s+c_4=26` has a repeated-stratum basis except the single row `(s,c_1,c_2,c_4)=(24,21,1,2)`. Even there, low rank is reduced to five explicit configurations rather than an unrestricted rank-two search.

## 6. Why this matters for the next proof attack

The residual low-rank obstruction now has a rigid form:

`S = a^4 b^4 c^2 product_{i=1}^{21} x_i`,

where `a,b` span a plane, `c` belongs to one of five normalized positions in that plane, and the remaining terms are singletons. Total sum fixes the plane component of `sum_i x_i`. Saturation supplies a defect certificate of length at most three for every singleton. Any symbolic elimination of the five forms would extend full-rank forcing through the entire 26-diagonal.

This is now the highest-value local target. Searching arbitrary rank-two length-ten strata would repeat work already closed by Theorem NQ4.

## 7. Atomic status

- Diagonal multiplicity rows: `VERIFIED` algebraically.
- Rank-one exclusion: `VERIFIED`.
- Symbolic classification of `4,4,2`: `VERIFIED`.
- Exclusion of `4,2,2,2` and `2^5`: `FINITE_EXACT`, independently checked by two zero-sum engines and a normalized enumeration.
- 26-diagonal reduction: `VERIFIED`.
- Elimination of the five residual forms: `UNRESOLVED`.
- Exact `D_4(C_5^3)` and `C_0(31)`: `UNRESOLVED`.

## 8. Remaining scientific frontier

There are now two nonredundant routes:

1. eliminate the five `(24,2)` rank-two normal forms using total sum, saturation defects, and the 21 singleton points; or
2. bypass multiplicity rank forcing with an atom-overlap theorem for the conditional four-atom patterns `(6,6,6,13)` and `(6,6,7,12)`.

A complete replay of the older support-through-22 search remains valuable for reproducibility but no longer advances the 26-diagonal mathematics. The next recursive cycle should attack the five explicit forms, not widen an undirected enumeration.
