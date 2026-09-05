# Type two: complete elimination of the H-minus-five overlap layer — V1

Status: **proved for every prime with positive `c=H-5`**. Dependencies are the exact quotient budget, `TWO_VALUE_LATTICE_ATOMS_AND_LENGTH_GCD_DICHOTOMY_V1.md`, `A2_RANK2_POSITIVE_CONGRUENCE_CLASS_ELIMINATION_V1.md`, and the previously established negative class and rigid-power reduction.

## Hypotheses

Use the canonical rank-two light-share type-two setup. Put `p=2H+1`, `c=H-5>=1`, `d=5`, and `a=6`. Then `p>=13`, `|R|=p+5`, both projected values are nonzero and distinct, and both total multiplicities are below `p`.

Every atomic divisor of the cyclic quotient has a defect `D` in `{1,2,3,4,5}`, length

\[
\ell_D=[5D\cdot6^{-1}]_p,
\]

and `ell_D+D` even. Every atomization has total defect six. The exact count formula makes each defect's count vector unique.

All prime classes are modulo twelve. The direct arithmetic below includes small primes, and does not assume `d^2<p`.

## The classes plus and minus one

The new positive-class theorem and the previously proved negative-class theorem exclude `p==1` and `p==-1 (mod 12)`, respectively. Both apply for arbitrary overlap defect.

## The class p=12L+5

Here `L>=1`. The candidate lengths are

\[
\ell_D=p-2LD\qquad(1\le D\le5).
\]

They are all odd, so parity permits only defects one, three, and five. For any factorization with `k` atoms,

\[
p+5=\sum\ell_{D_i}=kp-2L\sum D_i=kp-12L.
\]

Thus `k=2`, and its defect pattern is either `1+5` or `3+3`.

If no defect-one atom exists, no defect-five atom can occur, because its complementary zero-sum part must factor with total defect one. Therefore the quotient has exactly one atomic-divisor type, of defect three, and is a rigid square. Its length `p+5` exceeds the rigid-square bound `p+1`, a contradiction.

Otherwise an actual defect-one atom `P` has length

\[
N=10L+5>p/2+1.
\]

Apply the long-atom exchange lemma from `CYCLIC_TWO_VALUE_LONG_ATOM_EXCHANGE_V1.md`. With an index-one normalization `P=h^A(jh)^B`, write `w=j-1`; then `wB=p-N=2L`. The complementary quotient factor is mixed, so the actual exchanged atom exists and has length `N-w`. As `1<=w<=2L`,

\[
8L+5\le N-w\le10L+4.
\]

This is strictly between `N` and the next allowed atom length `6L+5`; hence it is not in the permitted spectrum. Contradiction.

## The class p=12L+7

Again `L>=1`; `p=7` does not have positive `H-5`.

For `L>=2`, every candidate has unwrapped length

\[
\ell_D=(2L+2)D\qquad(1\le D\le5),
\]

because `5(2L+2)<p`. Parity requires `D` even, leaving only defects two and four.

At `L=1` (`p=19`), the first four candidate lengths obey the same formula. Defect five instead wraps to length one. It cannot be an atom because the quotient values are nonzero. Defects one and three still fail parity. Thus only defects two and four occur in this case as well.

All actual atomic-divisor lengths have common divisor `2L+2>1`. The elementary spectrum-gcd dichotomy therefore forces a unique atomic-divisor type. The quotient is a rigid power, which the existing rigid-power plus saturated-boundary theorem excludes. (Alternatively, defect two must occur by the budget; defect four is its square by the no-wrap count formula, so the only actual atom has defect two, and the rigid cube has length `p+5>p+2`.)

## Conclusion and audit

Every prime admitting positive `c=H-5` is excluded. Together with the prior layers and the H-minus-four proof, the five consecutive positive layers `H-1,...,H-5` are empty.

The proof-audit teammate independently checked both nontrivial residue classes, factor counts, the no-defect-one implication, the long exchange interval and occurrence capacity, and the sole small wrap `p=19,D=5`. The coordinating researcher also checked these steps before integration; no blocker was found.

This is a local whole-layer advance. It does not prove the full first corridor, the remaining unsaturated type-two or type-one faces, or the generalized Davenport numerical formula.
