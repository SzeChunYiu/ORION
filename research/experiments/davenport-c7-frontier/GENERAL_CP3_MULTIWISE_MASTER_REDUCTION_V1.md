# Prime-uniform `C_p^3` multiwise Davenport master reduction — V1

Status: **research reduction / program architecture**. The donor inputs are named below. The short-threshold hypothesis is **not** claimed proved for general `p`.

## Scope and donor baseline

Let `p>=5` be prime and `G=C_p^3`.

The donor-derived `D2_PRIME_POWER_COROLLARY_V1.md` gives

\[
D_2(G)=\frac{9p-5}{2}.
\]

The Freeze--Schmid lower bound specializes, for every `k>=2`, to

\[
D_k(G)\ge L_k:=\frac{9p-5}{2}+(k-2)p.
\]

Thus the prime-uniform target is immediate stabilization at the lower-bound slope `p`:

\[
D_k(C_p^3)=L_k \qquad(k\ge2).
\]

This file records one sufficient theorem that would prove the entire tail at once.

## A zero-sum-conditioned short threshold

For this research packet only, define

\[
\zeta_p:=\min\{N:\text{ every zero-sum sequence }B\text{ over }C_p^3\text{ with }|B|\ge N
\text{ has a nonempty zero-sum subsequence of length }\le p\}.
\]

This notation is internal; no claim is made that `zeta_p` is standard terminology.

### Master lemma

If

\[
\zeta_p\le D_2(G)+p+1=\frac{11p-3}{2},
\]

then

\[
D_k(C_p^3)=\frac{9p-5}{2}+(k-2)p
\]

for every `k>=2`.

### Proof

Use the standard zero-sum block characterization

\[
D_k(G)=\max\{|B|:B\text{ is zero-sum and }z(B)\le k\},
\]

where `z(B)` is the largest number of pairwise disjoint nonempty zero-sum subsequences.

The case `k=2` is the donor-derived exact value above. Assume inductively that `D_k(G)=L_k` for some `k>=2` and let `B` be any zero-sum sequence with

\[
|B|=D_k(G)+p+1.
\]

The assumed threshold gives a nonempty zero-sum `U|B` with `|U|<=p`. Its complement `C=BU^{-1}` is zero-sum and satisfies

\[
|C|\ge D_k(G)+1.
\]

By the block characterization, `z(C)>=k+1`. Adjoining `U` gives `z(B)>=k+2`. Hence no zero-sum sequence of length `D_k+p+1` has packing number at most `k+1`, so

\[
D_{k+1}(G)\le D_k(G)+p=L_{k+1}.
\]

Freeze--Schmid supplies the reverse inequality. Induction completes the proof.

## Why this is the right cross-scene object

The same hypothesis has several equivalent/useful interpretations.

1. **Block monoid / factorization.** A zero-sum sequence is an element of the block monoid. The bound says every sufficiently long block has a nontrivial divisor of degree at most `p`. Combined with the exact `D_2`, repeatedly removing such a divisor forces the lower-bound factorization slope.
2. **Invariant theory.** For abelian groups the generalized Noether number satisfies `beta_k(G)=D_k(G)`. A short zero-sum divisor is a low-degree invariant monomial divisor. The desired threshold is therefore a bounded-degree divisibility/conductor statement for the monomial part of the invariant ring.
3. **Affine semigroup / toric language.** For a fixed support matrix `Q`, zero-sum multiplicity vectors are the nonnegative integer solutions of congruences `Qx=0 mod p`; atoms are the irreducible/Hilbert-basis elements. A `(k+1)`-pack is a conformal decomposition of one semigroup element into `k+1` nonzero semigroup elements.
4. **Coding / projective geometry.** After projectivizing the support, zero-sums are bounded positive kernel vectors of a diagonally scaled projective code. Short-zero-freeness becomes a forbidden low-weight positive-kernel condition.
5. **Hypergraph matching.** Term occurrences are vertices and nonempty zero-sum subsequences are hyperedges. `D_k` is a matching threshold. The master lemma says that, beyond one zero-sum-conditioned size threshold, a short edge always exists and can be peeled without losing the inductive matching surplus.

These translations are not novelty claims; they are route-selection tools.

## Specialization to `p=7`

The master threshold becomes

\[
\zeta_7\le37.
\]

So proving that every total-zero length-37 sequence over `C_7^3` contains a zero-sum subsequence of length at most seven would not merely prove `D_3(C_7^3)=36`; together with the exact `D_2=29` and the Freeze--Schmid lower bound, it would prove

\[
D_k(C_7^3)=7k+15 \qquad(k\ge2).
\]

The existing support-7 computation proves that any counterexample to this short-threshold statement must have support at least eight.

## Boundary

- The inequality `zeta_p <= (11p-3)/2` is a **sufficient master hypothesis**, not a theorem in this packet.
- It must be tested prime-by-prime before being promoted to a conjecture; in particular the known `p=5` multiwise formula does not by itself imply this stronger short-threshold statement.
- This program concerns the prime-uniform multiwise constants of `C_p^3`. Determining the classical Davenport constant for arbitrary finite abelian groups is a much broader problem and is not claimed here.
