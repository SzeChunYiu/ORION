# Mathematical Extensions R6 — Quotient Compression of the Five Residual 26-Diagonal Forms

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, and `MATHEMATICAL_EXTENSIONS_R5.md`

Status: rigorous structural and finite-exact reduction. It does not eliminate the five residual forms, determine `D_4(C_5^3)`, or prove `C_0(31)`.

## 1. Corrected frontier

The authoritative R5 result does not force rank three through the full 26-diagonal. The rows with profiles `2^5` and `4,2,2,2` are eliminated in rank two, but the row

`(s,c_1,c_2,c_4)=(24,21,1,2)`

still permits

`H=a^4 b^4 c^2`

inside a plane `P=span(a,b)`. After normalization `a=e_1`, `b=e_2`, the five swap classes for `c` are

`(1,1), (1,2), (1,3), (1,4), (2,3)`.

This addendum moves from repeated-stratum classification to the 21 singleton points. It proves that almost all singletons lie outside `P`, caps every nonzero quotient coset, and reduces the quotient data to 139 or 223 exact occupancy vectors depending on the normal form.

The numerical rank-forcing frontier is not falsely promoted to 27.

## 2. Singleton points inside the repeated plane

Fix one of the five normalized forms and let `x` be a singleton support point in `P`, distinct from `a,b,c`. The multiset

`a^4 b^4 c^2 x`

must remain free of nonempty zero sums of length at most five.

**Theorem NQ7 (exact plane-singleton classification).** The only possible plane singletons are:

| normalized `c` | allowed singleton points in `P` |
|---|---|
| `(1,1)` | `(1,2)`, `(2,1)` |
| `(1,2)` | `(1,4)` |
| `(1,3)` | `(1,1)` |
| `(1,4)` | `(1,3)`, `(2,3)` |
| `(2,3)` | `(4,1)` |

Coordinates are with respect to the ordered basis `(a,b)`.

**Proof.** There are only 21 nonzero plane points other than `a,b,c`. For each candidate, enumerate every bounded submultiplicity vector

`0<=i,j<=4`, `0<=k<=2`, `0<=ell<=1`

with total length between one and five and test

`ia+jb+kc+ell x=0`.

A separate length-indexed dynamic program computes exactly the same reachable sums. The two engines agree on every candidate and return the displayed table. This is a complete finite theorem over `C_5^2`, not a sampled search. ∎

**Corollary NQ8.** At most two of the 21 singleton support points lie in `P`. More precisely, the forms `(1,1)` and `(1,4)` allow at most two, while `(1,2)`, `(1,3)`, and `(2,3)` allow at most one. Hence at least 19 singletons lie outside `P`, and at least 20 do so in three of the five forms.

## 3. A cap in each nonzero quotient coset

Let

`pi:C_5^3 -> C_5^3/P ~= C_5`

be the quotient map. For a fixed nonzero quotient class `r`, its affine coset has the form `t+P`. Distinct singleton support points in that coset correspond to a subset of the 25-element plane `P`.

The set-valued Kemnitz constant for `C_5^2` is

`g(C_5^2)=9`:

every nine-element subset contains five distinct elements with sum zero, while an eight-element counterexample exists. The `p=5` value is the classical small-prime case recorded in W. Gao and R. Thangadurai, *A variant of Kemnitz Conjecture*, Journal of Combinatorial Theory, Series A 107 (2004), 69–86, DOI `10.1016/j.jcta.2004.03.009`.

**Theorem NQ9 (affine-coset cap).** No nonzero quotient coset contains nine singleton support points. Therefore every nonzero quotient occupancy is at most eight.

**Proof.** Suppose `x_i=t+p_i`, `i=1,...,9`, are distinct points in one coset. Choose five plane components with `p_{i_1}+...+p_{i_5}=0`, which exist by `g(C_5^2)=9`. Since the group has exponent five,

`x_{i_1}+...+x_{i_5}=5t+(p_{i_1}+...+p_{i_5})=0`.

This is a forbidden zero sum of length five. ∎

The portfolio verifier independently exhausts the `p=5` finite statement. By affine invariance, a hypothetical nine-set may be normalized to contain `(0,0),(1,0),(0,1)`. It checks all `binom(22,6)=74,613` normalized completions. Direct five-subset enumeration and an independent complement-four engine agree and find no survivor. It also verifies an explicit zero-sum-free eight-set, so the cap is exact.

## 4. Quotient occupancy vectors

Let

`n_r = number of singleton points x with pi(x)=r`, `r in C_5`.

The high-multiplicity stratum lies in `P`. Because the full sequence has total sum zero,

`n_1+2n_2+3n_3+4n_4 = 0 mod 5`.

The previous theorems give

`n_0<=2`, `n_r<=8` for `r=1,2,3,4`, and `sum_r n_r=21`.

For the three one-plane-singleton forms, strengthen the first inequality to `n_0<=1`.

**Theorem NQ10 (exact quotient-profile compression).** The integer system above has:

- 223 solutions when `n_0<=2`; and
- 139 solutions when `n_0<=1`.

Every solution uses at least three of the four nonzero quotient classes.

**Proof.** The profile counts follow by direct enumeration of the five bounded integers and the displayed congruence. At least 19 points lie outside `P`; two nonzero cosets can hold at most 16 by Theorem NQ9, so at least three nonzero classes are occupied. ∎

Thus the former search over 21 arbitrary distinct singleton points is replaced, at quotient level, by a finite list of 139 or 223 occupancy vectors plus affine-plane data inside occupied cosets.

## 5. Factorization interface

The hypothetical extremal sequence admits a factorization into four occurrence-disjoint atoms. For an atom `U_j`, define

`m_{jr}=number of singleton occurrences of quotient class r in U_j`.

Every row satisfies

`sum_{r=1}^4 r m_{jr}=0 mod 5`,

and the column sums are the quotient profile:

`sum_j m_{jr}=n_r`.

The high terms `a^4b^4c^2` contribute only to the zero quotient column but constrain each atom's remaining plane sum. Atom lengths and the previously derived repetition–overlap identity add independent row bounds.

This gives the correct next proof object: a `4 x 5` quotient-occupancy matrix coupled to five small affine-plane problems. Exact search should now be used adversarially to test these symbolic constraints, rather than restarting an undirected 21-point enumeration.

## 6. What has and has not advanced

The new theorems remove most plane placements and impose a sharp prior-art cap on every affine quotient coset. They materially compress the five residual forms but do not contradict all 139/223 quotient profiles. Coarse quotient row sums alone are insufficient; plane sums, saturation defects, total sum, and atom allocation must be combined next.

Accordingly:

- `s+c_4=26` remains the live diagonal;
- the five `4,4,2` normal forms remain possible at the current authority level;
- `D_4(C_5^3)` remains in `{30,31}` under H1 and H2; and
- no statement at diagonal 27 is authorized.

## 7. Verification

`papers/verify_five_math_extensions_r6.py` checks:

1. the complete plane-singleton table with two exact zero-sum engines;
2. the affine-coset threshold by 74,613 normalized nine-set checks under two independent criteria;
3. an explicit eight-point zero-sum-free witness;
4. the 139 and 223 quotient-profile counts; and
5. the lower bound of three occupied nonzero quotient classes.

The Gao–Thangadurai/Kemnitz theorem supplies the symbolic coset cap; the exhaustive replay is hostile finite corroboration.

## 8. Prior-art calibration

The value `g(C_5^2)=9`, affine normalization, and quotient zero-sum reasoning are donor mathematics. No novelty is claimed for the Kemnitz constant. The paper-specific residual is the way that theorem intersects the previously classified `4,4,2` repeated plane, the exact plane-singleton table, and the four-atom obstruction grammar for the length-31 Davenport problem.

## 9. Atomic status

- Five R5 normal forms: `RETAINED`.
- Plane-singleton classification: `FINITE_EXACT`, two engines.
- At least 19 outside-plane singletons: `VERIFIED`.
- Nonzero affine-coset cap eight: `VERIFIED` from the published `g(C_5^2)=9` theorem and independently replayed at `p=5`.
- Quotient profile counts 139/223: `FINITE_EXACT`.
- Elimination of every quotient profile: `UNRESOLVED`.
- Full 26-diagonal rank forcing: `UNRESOLVED`.
- Exact `D_4(C_5^3)` and `C_0(31)`: `UNRESOLVED`.

## 10. Remaining scientific frontier

The next recursive cycle should enumerate symbolic quotient-atom matrices first, then add plane sums and saturation-defect obligations form by form. A contradiction must be expressed as a reusable quotient/factorization lemma; exact computation should certify the finite residue and search for hostile counterexamples. Repeating the already closed rank-two high-stratum classification would add no new authority.
