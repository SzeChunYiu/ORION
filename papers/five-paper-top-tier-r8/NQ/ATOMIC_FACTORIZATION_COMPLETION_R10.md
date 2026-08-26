# Atomic Factorization Skeleton of a Generalized-Davenport Completion — R10

Date: 2026-08-26

Status: analytic structural reduction. Block-monoid/factorization language is established donor theory. Numerical C5^3 use remains conditional on independent replay of `D_3(C_5^3)=25` until issue #1383 closes.

## 1. Packing and factorization in a total-zero sequence

For a zero-sum sequence `S`, let `nu(S)` be the maximum number of pairwise disjoint nonempty zero-sum subsequences.

Let `L_max(S)` be the maximum number of factors in a factorization

`S=A_1 ... A_r`

where every `A_i` is a nonempty zero-sum sequence. Refining every nonminimal factor into zero-sum atoms shows that the maximum may equivalently be taken over factorizations into atoms of the block monoid.

### Proposition NQ-R10.12

For every nonempty total-zero sequence `S`,

`nu(S)=L_max(S)`.

Moreover, every maximum packing of `nu(S)` disjoint zero-sum subsequences covers every term of `S`.

### Proof

A factorization into `r` zero-sum factors is an `r`-packing, so `nu(S)>=L_max(S)`.

Conversely let `A_1,...,A_r` be any disjoint zero-sum packing. If their union does not equal `S`, the nonempty complement

`R=S(A_1...A_r)^{-1}`

is also zero-sum because `S` and all `A_i` have sum zero. Hence the packing extends to a factorization of all of `S` into `r+1` zero-sum factors. If the packing already covers `S`, it is itself a factorization. Therefore a maximum packing must cover `S`, and its size is at most `L_max(S)`. Equality follows. ∎

## 2. Maximum packings are atomic

### Corollary NQ-R10.13

Every factor in a maximum-length factorization of `S` is a minimal zero-sum sequence (an atom).

### Proof

If one factor contained a nonempty proper zero-sum subsequence, its zero-sum complement would split that factor into two nonempty zero-sum factors, contradicting maximality. ∎

Thus a packing-number statement about a total-zero sequence is exactly a maximum factorization-length statement in the block monoid.

## 3. Apply the matching-critical completion theorem

Under the assumptions of `MATCHING_CRITICAL_COMPLETION_R10.md`, a generalized-Davenport obstruction `M` with

`D_k(G)=N`, `|M|=N+t`, `nu(M)=k`

completes to `S=M(-sigma(M))` with

`nu(S)=k+1`.

### Corollary NQ-R10.14

The completed sequence `S` has a factorization into exactly `k+1` zero-sum atoms, and no factorization into `k+2` zero-sum factors exists.

Every maximum packing is an atomic factorization of the entire completion.

This provides a factorization-theoretic certificate independent of the original disjoint-subsequence implementation.

## 4. C5^3 D4 specialization

Conditional on the replayed `D_3(C_5^3)=25`, any hypothetical length-30 source obstruction to four disjoint zero sums completes to a sequence `S` satisfying:

- `|S|=31`;
- `sigma(S)=0`;
- no zero sum has length at most five;
- `nu(S)=4`;
- every four-packing is a factorization of all 31 terms into four atoms;
- every maximum factorization contains the distinguished completion occurrence in exactly one atom;
- deleting that occurrence leaves a source sequence with packing number exactly three.

The ordinary Davenport constant is

`D(C_5^3)=13`.

Therefore every zero-sum atom has length at most 13. Short-freeness gives atom length at least 6.

### Theorem NQ-R10.15 — eleven atom-length skeletons

The sorted atom-length multiset of any genuine completed D4 obstruction must be one of exactly eleven possibilities:

1. `(6,6,6,13)`;
2. `(6,6,7,12)`;
3. `(6,6,8,11)`;
4. `(6,6,9,10)`;
5. `(6,7,7,11)`;
6. `(6,7,8,10)`;
7. `(6,7,9,9)`;
8. `(6,8,8,9)`;
9. `(7,7,7,10)`;
10. `(7,7,8,9)`;
11. `(7,8,8,8)`.

### Proof

Four integer atom lengths lie in `[6,13]` and sum to 31. Direct integer partition enumeration gives the displayed list. ∎

The list is complete and independent of the multiplicity/orbit normalization used elsewhere in the search.

## 5. Distinguished completion atom

Let `A_g` be the atom containing the distinguished completion occurrence `g` in a maximum factorization

`S=A_g A_2 A_3 A_4`.

Then in the source

`M=Sg^{-1}`,

the three atoms `A_2,A_3,A_4` give three disjoint zero sums, while the residue

`A_g g^{-1}`

is nonzero-sum; otherwise `M` would have a fourth zero sum.

Because `A_g` is an atom, this residue contains no zero-sum subsequence whose complement in `A_g` is also nonempty zero-sum. Source-level replay can therefore carry:

- the atom partition;
- the index of `A_g`;
- the distinguished occurrence `g`;
- exact atom minimality certificates; and
- a four-packing failure certificate after deleting `g`.

This is substantially stronger than a bare total-zero/short-free completion receipt.

## 6. LUNARC branching strategy

The eleven atom-length patterns provide an independent partition of the source search.

A source-level solver can branch first by sorted length pattern, then by which atom contains `g`, and only then by multiplicity/orbit structure. For each branch require:

1. four disjoint selectors partition all 31 occurrences;
2. selector lengths equal the frozen pattern;
3. each selector sums to zero;
4. each selected zero-sum factor is atom-minimal (or is independently refined to atoms and rejected if it splits);
5. every source-level length-1..5 zero sum remains forbidden;
6. deleting `g` yields exact packing number three.

The atom branch can coexist with the existing saturation/multiplicity branch. Agreement of the two independent partition schemes is a valuable completeness check.

A useful fail-fast rule is immediate: any candidate for which a proposed four-factor partition contains a splittable factor has at least five disjoint zero sums and cannot correspond to a D4 source obstruction.

## 7. Factorization-theory application

Generalized Davenport constants were introduced in connection with factorization invariants. The completed obstruction makes that link explicit rather than rhetorical: it is a block-monoid element of total sequence length 31 whose maximum factorization length is exactly four, with all atoms of lengths 6 through 13 and one distinguished occurrence whose deletion lowers the zero-sum packing number.

The manuscript should ask factorization specialists whether this matching-critical/maximum-length profile has an established invariant-theoretic name or known inverse classification. Generic block-monoid factorization theory is donor-owned.

## 8. Authority boundary

The proposition `nu(S)=L_max(S)` for a total-zero sequence is elementary and may be standard; no novelty claim should rest on it alone.

The scientific value is the exact structural chain for the unresolved rank-three D4 bit:

`D_3=25`

`=> one-term short-free completion`

`=> completion term is matching-critical`

`=> exact four-atom factorization of all 31 terms`

`=> eleven possible atom-length skeletons`

`=> independent source-level search partition and certificate language`.

This chain should reduce computation and improve proof transparency even if some individual steps are donor-subsumed.
