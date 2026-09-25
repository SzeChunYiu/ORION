# Davenport unsaturated faces: preserved routes and exact failed inferences

Status: **research-route record, not an additional closure theorem**. This note preserves the unsuccessful shortcuts encountered while proving the first two unsaturated type-two faces and the first unsaturated type-one inverse theorem.

## 1. The selected corridor factorization is existential

The original six-pattern corridor argument selects a shortest atom and then a shortest atom in its complement. It does not restrict every alternative factorization. The exact correction and its justification are in `CORRIDOR_FACTORIZATION_QUANTIFIER_AUDIT_V1.md`; the two affected older statements were corrected in local commit `78d2478ff`.

Therefore an alternate zero-sum factorization whose lengths are outside that list cannot be rejected just by quoting the selected list. The correction preserves the covering strategy: eliminating every possible selected pattern would still prove the intended contradiction.

## 2. The first-face near-maximal exchange really has length m+1

In the main `b=2` rank-three family, write

`rx=2y-cs-g`, `y=(A,-A,1)`, `r=H+1-c`.

The occurrence sequence

\[
Z=x^r s^{c-1}e_1^{[u-2A]_p}e_2^{[u+2A]_p}
\]

is zero-sum, because `rx+(c-1)s=2y-s-g` has third coordinate zero. Its two axis counts sum to either `1` or `p+1`; its other counts sum to `H`. Thus it has length `H+1` or **`m+1`**. The first case is short and impossible. The second case is not a strict-short certificate.

In a hypothetical short-free product, `Z` and its complementary zero-sum would be atoms of lengths `m+1` and `D-1`, because each is shorter than `2m`. The second factor has length `D-1`, so a maximal-atom classification does not apply to it. Section 1 also prevents using the selected corridor list to forbid this alternative factorization. The later complement-interval theorem and mixed selector close the actual `b=2` face without either inference.

The older multiplier-three continuation from one light share to two likewise has length `m+1`, not a contradiction. It remains preserved in the rectangular-rigidity checkpoint.

## 3. A large auxiliary rectangle does not itself solve all higher deficits

For a main-family rank-three row with general `b>=4`, put

\[
A_0=2c-b+1>0,\qquad R_0=2r,\qquad
A_0+R_0=p+b-2.
\]

In an auxiliary cyclic group, the occurrence sequence

\[
T=(A_0h)^{R_0}(-R_0h)^{A_0}
\]

is zero-sum and has length greater than `p`. Its zero-sum count relation is `A0 i=R0 w`. Such a vector would give the generalized type-two group `x^i s^{w+1}`, but only after proving all of

\[
1\le i\le r=R_0/2,\quad 0\le w\le c+1,\quad i+w\le H,
\]

the required third-coordinate range, and the nonexceptional equation from `A2_GENERALIZED_WEIGHT_TWO_MIXED_PACKET_SELECTOR_V1.md`.

An arbitrary atomization of `T` does not automatically place an atom or a union of atoms inside this smaller actual-capacity region. Nor does length alone establish the third-coordinate or exceptional-equation conditions. This is an unproved existence gate. No full `b>=4` theorem is inferred from the auxiliary zero-sum.

At `b=3`, the successful auxiliary sequence instead has length exactly `H+1`. Its proper parts, repeated-factor exception, and one additional light occurrence were all handled explicitly in `A2_RANK3_SECOND_UNSATURATED_MAIN_FAMILY_ELIMINATION_V1.md`. That proof must not be transported to the larger rectangle without new bounds.

## 4. Endpoint hypotheses cannot be discarded

- The first and second unsaturated donor inverses require respectively three and four available type-two light terms. The four-light certificate at `p=11,y=(8,6,2)` is material to the second theorem.
- The second inverse theorem at `p=7,K=4` was proved with a saturated `g` donor. Its one-missing-`g` analogue was not asserted. The top-capacity conclusion at seven uses a separate donor-only certificate and is unaffected.
- The new type-one inverse uses `K>=2`; the two nonzero centered slopes are excluded with two actual sum-direction occurrences. It does not claim the same form for one occurrence after truncation.
- The planar half-power theorem removes every minimal-overlap endpoint only after its main-family hypothesis is known. Its unconditional threshold is stated separately.
- The general type-one circle certificate uses `y^(k-d)`, so `k>=d` is essential. The stepped circle enforces it. A close pair with a smaller index difference is not automatically a legal certificate.

## 5. Global gates remain separate

The support-six maximal-atom exchange at top rank-two overlap remains a valid prior construction, not a contradiction. The support-four classification cannot be applied to that exchanged atom. The remaining canonical faces, larger-support and global first-corridor gates, `D_3(C_7^3)`, and generalized Davenport numerical formula remain unproved. No failure above is asserted to produce a realizable companion or a counterexample.
