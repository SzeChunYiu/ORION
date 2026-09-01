# Mathematical Extensions R4 — The Property-C Boundary and an Expanded Rank-Forcing Frontier

Date: 2026-08-25

Canonical predecessor: `MANUSCRIPT_V3_PIPELINE.md`

Status: rigorous theorem addendum. It strengthens the unconditional structural reduction but does not claim the exact value of `D_4(C_5^3)` or a proof of `C_0(31)`.

## 1. Purpose

The V3 manuscript proves that a saturated, 5-short-free, total-zero sequence `S` of length 31 has multiplicities in `{1,2,4}` and that the high-multiplicity subsequence

`H = product_{v:m(v)>=2} v^{m(v)}`

has full rank whenever

`s+c_4 <= 24`.

Here `s=|supp(S)|` and `c_i` is the number of support points of multiplicity `i`. This addendum extends the analytic frontier to

`s+c_4 <= 25`

for every residual branch with `s>=23`. The new boundary step uses the rank-two Property-C classification at length 12 rather than another bounded-support computation.

## 2. Recalled multiplicity equations

From V3,

`c_1+c_2+c_4=s`,

`c_1+2c_2+4c_4=31`,

and therefore

`c_2=31-s-3c_4`,

`c_1=2s-31+2c_4`.

The high-multiplicity length is

`|H|=2c_2+4c_4=62-2s-2c_4=62-2(s+c_4)`.

Thus the new boundary `s+c_4=25` is exactly the case `|H|=12`.

## 3. Donor theorem used at the boundary

The rank-two constant is

`eta(C_5^2)=13`.

The Property-C inverse theorem for `C_5^2` says that a sequence of length 12 with no nonempty zero-sum subsequence of length at most 5 has the form

`T^4`

for a length-three sequence `T`. Equivalently, after a rank-two change of basis it has the standard three-block form with four copies of each of three support points.

This is an external rank-two donor theorem, not a new result of this paper. The addendum uses only its length-12 consequence. A final bibliography pass should cite the original Property-C source together with a modern rank-two statement; Grynkiewicz and Liu, *The m-wise Davenport constant for finite abelian groups* (2021), summarize the relevant Property-C implication for moduli divisible only by primes at most seven.

## 4. Boundary classification

**Theorem NQ1 (rank-two boundary classification).** Let `S` be saturated, 5-short-free, total-zero, and of length 31 in `C_5^3`. Suppose

`s+c_4=25`

and `rank(span H)<=2`. Then

`(s,c_1,c_2,c_4)=(22,19,0,3)`,

and `H=T^4` for three distinct support points spanning a rank-two subgroup.

**Proof.** The equality `s+c_4=25` gives `|H|=12`. The subsequence `H` is 5-short-free because it is a subsequence of `S`.

It cannot lie in a rank-one subgroup: every length-five sequence in `C_5` has a nonempty zero-sum subsequence of length at most five, whereas `H` has length 12. Hence `rank(span H)=2`.

Apply Property C in `C_5^2`. We obtain `H=T^4` with `|T|=3`. The three terms of `T` are distinct; otherwise one group element would occur at least eight times in `H`, and five equal copies would form a forbidden zero sum.

By definition of `H`, every support point occurs in it with multiplicity either two or four. The representation `T^4` therefore forces exactly three multiplicity-four points and no multiplicity-two points:

`c_4=3`, `c_2=0`.

Using `c_2=31-s-3c_4` gives

`0=31-s-9`,

so `s=22`. Then `c_1=s-c_4=19`. ∎

The theorem identifies the only possible low-rank configuration on the new diagonal. It is a support-22 exception, not a residual support-23-or-larger branch.

## 5. Expanded rank-forcing theorem

**Theorem NQ2 (rank forcing through the 25-diagonal).** Let `S` satisfy the hypotheses above and suppose `s>=23`. If

`s+c_4<=25`,

then

`rank(span H)=3`.

**Proof.** When `s+c_4<=24`, the V3 theorem gives full rank from `|H|>=14` and `eta(C_5^2)=13`.

It remains to consider equality `s+c_4=25`. If `rank(span H)<=2`, Theorem NQ1 forces `s=22`, contradicting `s>=23`. Therefore `H` has rank three. ∎

This is an unconditional analytic improvement. It does not use the internal search frontier through support 22.

## 6. Newly closed residual branches

The new theorem closes the entire diagonal

`(s,c_4)=(23,2),(24,1),(25,0)`.

Indeed each pair satisfies `s+c_4=25`, so the repeated stratum spans `C_5^3`.

For clarity, the first residual rows now have the following analytic status.

| support `s` | `c_4` | `c_2` | `|H|` | rank conclusion |
|---:|---:|---:|---:|---|
| 23 | 0 | 8 | 16 | rank 3 by V3 |
| 23 | 1 | 5 | 14 | rank 3 by V3 |
| 23 | 2 | 2 | 12 | rank 3 by Theorem NQ2 |
| 24 | 0 | 7 | 14 | rank 3 by V3 |
| 24 | 1 | 4 | 12 | rank 3 by Theorem NQ2 |
| 24 | 2 | 1 | 10 | unresolved by this theorem |
| 25 | 0 | 6 | 12 | rank 3 by Theorem NQ2 |
| 25 | 1 | 3 | 10 | unresolved by this theorem |
| 25 | 2 | 0 | 8 | unresolved by this theorem |

Thus every support-23 branch is now analytically in the mixed-basis regime. The first silent diagonal moves from `s+c_4=25` to `s+c_4=26`.

## 7. Canonical-basis consequence

**Corollary NQ3 (repeated-stratum basis).** Under Theorem NQ2, there exist three support points of multiplicity at least two that form a basis of `C_5^3`.

**Proof.** The high-multiplicity support spans rank three, so it contains a three-element basis. ∎

After applying an element of `GL(3,5)`, those repeated points may be normalized to the standard basis. This is useful for exact residual enumeration: the basis is chosen from the repeated stratum rather than from arbitrary support points, and all three basis points retain multiplicity information.

This is an algorithmic normalization, not a proof that the remaining residual branches are empty.

## 8. Interaction with the atom-factorization reduction

The V3 manuscript shows that any counterexample to `C_0(31)` has a factorization into at most four atoms. In the four-atom corridor, the sorted atom-length pattern is conditionally restricted to

`(6,6,6,13)` or `(6,6,7,12)`

under the stated high-density compression lemma.

Theorem NQ2 supplies a stronger basis for analyzing the support-23 part of either pattern: every candidate has three repeated basis points. Consequently, each atom can be encoded relative to a basis that is simultaneously visible in the global multiplicity profile. This may reduce the orbit types that must be considered in an overlap theorem.

No atom-overlap classification is proved here. In particular, the theorem does not establish projective squarefreeness of length-12 or length-13 atoms.

## 9. Application implications

### 9.1 Exact additive search

The expanded frontier removes three rank-ambiguous branches before search. A residual verifier may normalize a basis from the repeated stratum on all support-23 candidates and on the specified support-24 and support-25 diagonals.

### 9.2 Nonunique factorization theory

The conditional four-atom corridor corresponds to extremal factorization length in a block monoid over `C_5^3`. A proof that every total-zero length-31 sequence has five atoms would determine the relevant generalized Davenport threshold. The multiplicity and rank reductions isolate the only candidate factorization geometries that can obstruct this conclusion.

### 9.3 Coding-theoretic interpretation

A sequence of vectors in `F_5^3` can be viewed as a multiset of columns. A short zero-sum subsequence is a low-weight dependence with all selected coefficients equal to one. Saturation says that adding one more copy of any existing column creates such a dependence. Theorem NQ2 then says that, on the first residual diagonals, the repeated columns already span the ambient parity-check space. This is a structural analogy, not a new coding bound.

### 9.4 Search-to-proof conversion

The unique low-rank boundary pattern from Theorem NQ1 gives a precise target for theorem extraction. Any future proof replacing the support-22 computation need only exclude the configuration

`1^19 4^3`

with a rank-two Property-C repeated stratum, rather than all support-22 multiplicity profiles.

## 10. Remaining exact barriers

The analytic frontier is stronger, but the central problem remains open in this packet. A top-tier exact theorem would require at least one of the following.

1. Extend rank forcing to the `|H|=10` diagonal `s+c_4=26`.
2. Prove a rank-three atom-overlap theorem excluding both conditional four-atom patterns.
3. Replace the internal bounded-support frontier by an independently replayable complete classification.
4. Establish `C_0(31)` directly by a new congruence, polynomial, or inverse-additive argument.

The current theorem does not imply any of these statements.

## 11. Integration into the manuscript

1. Replace the V3 rank-forcing theorem by Theorem NQ2, retaining the old `|H|>=14` proof as the first case.
2. Add Theorem NQ1 as the boundary inverse lemma.
3. Update the residual table so that `(23,2)`, `(24,1)`, and `(25,0)` are no longer marked rank-silent.
4. Add Corollary NQ3 to the residual enumeration protocol.
5. Keep the title and abstract conditional unless the full `C_0(31)` gate is proved.

## 12. Atomic claim status

- Multiplicity equations and `|H|` formula: `VERIFIED` in V3.
- Rank-one exclusion at length 12: `VERIFIED` from `D(C_5)=5`.
- Property-C boundary input: `EXTERNAL_DONOR`, applicable at `n=5`.
- Boundary classification Theorem NQ1: `VERIFIED` from the donor theorem and multiplicity equations.
- Expanded rank forcing Theorem NQ2: `VERIFIED`.
- Newly closed diagonal and repeated-stratum basis: `VERIFIED`.
- Exact value of `D_4(C_5^3)`: `UNRESOLVED`.
- `C_0(31)`: `UNRESOLVED`.
- External replay of the support-through-22 computation: `UNRESOLVED`.

## 13. Editorial effect

This addendum supplies a genuine unconditional advance over V3: the first rank-silent diagonal is resolved analytically, and all support-23 candidates enter the full-rank mixed-basis regime. That is publishable structural progress for a specialist additive-combinatorics note. It is not yet a top-tier resolution of the generalized Davenport problem because the four-atom obstruction remains.