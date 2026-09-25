# Type two: complete elimination of the H-minus-four overlap layer — V1

Status: **proved for every prime with positive `c=H-4`**, including all unsaturated multiplicities. The proof uses exact atom spectra and actual long-atom exchanges.

## 2. Type-two setup at d=4

Use the canonical rank-two light-share hypotheses of `A2_RANK2_EXACT_QUOTIENT_DEFECT_BUDGET_V1.md`. Let `p=2H+1`, `c=H-4>=1`, and `R=x^r y^t`, so `|R|=p+4` and both multiplicities are below `p`. Necessarily `p>=11`.

Every quotient atom has a defect `D` in `{1,2,3,4}`, with length

\[
\ell_D=[4D\cdot5^{-1}]_p,
\]

and `ell_D+D` is even. Every atomic factorization of the quotient has exact defect sum five. Count vectors are unique for each defect. Each projected atom is mixed.

The argument below uses direct least-residue arithmetic, and therefore does not need the optional hypothesis `d^2<p`.

## 3. The class p=10L+1

Put `z=2L+1`; then `p=5z-4`. Since `p>=11`, `L>=1`, and `z` is odd and at least three.

For `L>=2`, all four atom lengths have the form

\[
\ell_D=Dz\quad(1\le D\le4),
\]

because `4z<p`. At `L=1` (`p=11`), the lengths for `D=1,2,3` are still `Dz`, while `ell_4=1`; defect four is excluded because `ell_4+4` is odd.

If a defect-one atom `P` exists, any other allowable defect `D` has count vector equal to `D` times the vector of `P`: its counts do not wrap, because their sum is `D|P|=Dz<p`. Thus all candidates of defect at least two are powers of `P`, and are not atoms. Consequently the quotient has `P` as its only atomic divisor and equals `P^5`. The established rigid-power plus saturated-boundary theorem excludes this.

If no defect-one atom exists, no defect-four atom can exist: its complementary quotient-zero subsequence would factor with total defect one. The exact budget therefore forces one defect-two atom and one defect-three atom. All atom lengths are multiples of `z>1`, and the defect-three atom has length

\[
N=3z>p/2+1=(5z-2)/2.
\]

This contradicts the elementary gcd dichotomy in `TWO_VALUE_LATTICE_ATOMS_AND_LENGTH_GCD_DICHOTOMY_V1.md`.

## 4. The class p=10L+3

Here `L>=1`. The four least-residue lengths are

\[
(\ell_1,\ell_2,\ell_3,\ell_4)
=(4L+2,\ 8L+4,\ 2L+3,\ 6L+5).
\]

Parity excludes defects one and four. The budget five forces a factorization with exactly one defect-two atom and one defect-three atom. Thus all atom lengths belong to

\[
\{M,N\}=\{2L+3,\ 8L+4\}.
\]

The long atom satisfies `N>p/2+1`. The two-length consequence of `CYCLIC_TWO_VALUE_LONG_ATOM_EXCHANGE_V1.md` would require

\[
N-M=6L+1\mid p-N=2L-1,
\]

which is impossible since `0<2L-1<6L+1`.

This includes `p=13`; no square-root assumption was used.

## 5. The class p=10L+7

Here `L>=1`, because `p=7` does not have positive `H-4`. The four lengths are

\[
(\ell_1,\ell_2,\ell_3,\ell_4)
=(6L+5,\ 2L+3,\ 8L+8,\ 4L+6).
\]

Parity excludes defects two and three. The defect budget allows `1+4` or five copies of defect one, but the latter has total length `3p+4`, not `p+4`. Hence every factorization has exactly the two lengths

\[
N=6L+5,\qquad M=4L+6.
\]

Again `N>p/2+1`. The two-length lemma in `CYCLIC_TWO_VALUE_LONG_ATOM_EXCHANGE_V1.md` gives

\[
w=N-M=2L-1,\qquad wB=p-N=4L+2,
\]

so `B=2+4/w`.

There are two complete ways to finish:

**Parity finish.** The defect-one atom has canonical light coefficient `q=(N+1)/2=3L+3`. The lower proper-part inequality `2-epsilon(q)<=1` requires `q` odd and therefore `L` even. Thus `w=2L-1` is odd and at least three. But `w|4`, a contradiction.

**Second-exchange finish, independently of that last parity test.** If the first exchange avoids contradiction, it has the short atom's length. Two zero-sum subsequences of a two-value sequence with equal length below `p` have equal count vectors, so the short factor is exactly `P'=h^(A-j)(jh)^(B+1)`. Here `j=w+1=2L`, `A=N-B`, and

\[
A-2j=2L+5-B\ge2L-1\ge1,
\]

because `B=2+4/w<=6`. The quotient contains `P P'`, so a second exchanged atom

\[
P''=h^{A-2j}(jh)^{B+2}
\]

fits: its nonunit count is at most `2B+1` and its unit count is positive. It has positive representative sum `p` and length `N-2w<M`, contradicting the two-point spectrum.

## 6. The class p=10L+9

The existing negative-class theorem applies with `a=5`, since `p==-1 (mod 10)`. Every candidate atom violates parity. This class is empty.

## 7. Conclusion, audit, and exact scope

Every prime admitting positive `c=H-4` lies in one of the four classes above. Therefore the entire rank-two type-two `c=H-4` layer is empty.

This extends the consecutive empty layers to `H-1,H-2,H-3,H-4`. The positive class in Section 3 also follows directly from `A2_RANK2_POSITIVE_CONGRUENCE_CLASS_ELIMINATION_V1.md`; its earlier factorization proof is preserved here. It does not settle `c=H`, all lower layers, rank-three unsaturated type-two cases, global support gates, the full first corridor, or a generalized Davenport numerical formula.

The proof-audit teammate independently checked the long-atom lemma, all four residue classes, the `p=11` wrap, the `p=13` case, and the second class-seven exchange; no blocker was found. The coordinating researcher also reviewed the proof against that fixed commit before integration.

## 8. Preserved limitations of the route

- A long-atom gcd obstruction needs an actual long atomic divisor. A formal modular signature does not provide one.
- A displayed power factorization alone does not establish rigidity; the defect-one argument separately excludes every other atom by exact occurrence counts.
- The exchange spectrum is the set of all atomic-divisor lengths, not just the lengths in one preferred factorization.
- The strict index threshold is retained. Atoms exactly on or below it require other arguments.
- At general defect, multiple short atom types can partition the budget without producing a long atom. This proof does not exclude that possibility.
