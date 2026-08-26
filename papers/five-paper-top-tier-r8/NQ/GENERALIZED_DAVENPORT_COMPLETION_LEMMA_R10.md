# Completion Lemma from Generalized Davenport Obstructions to Short-Free Zero-Sum Sequences — R10

Date: 2026-08-26

Status: elementary analytic reduction with direct relevance to the D4(C5^3) search space. It should be compared explicitly with existing inverse-D_k characterizations, especially Qinghai Zhong's 2025 rank-two Proposition 3.1. No claim is made that the underlying complement trick is unprecedented.

## 1. Statement

Let `G` be a finite abelian group and suppose

`D_k(G)=N`.

Let `t>=1`, and let `M` be a sequence over `G` of length

`|M|=N+t`

that contains no `k+1` pairwise disjoint nonempty zero-sum subsequences.

Write

`g=-sigma(M)`

and form the one-term completion

`S=M g`.

### Theorem NQ-R10.9 — generalized completion lemma

Under the assumptions above:

1. `M` has no nonempty zero-sum subsequence of length at most `t`;
2. `S` is a total-zero sequence of length `N+t+1`; and
3. `S` also has no nonempty zero-sum subsequence of length at most `t`.

Thus every length-`D_k(G)+t` obstruction to `k+1` disjoint zero sums admits a one-term completion into a total-zero `t`-short-free sequence.

## 2. Proof

### Part 1 — the obstruction is already t-short-free

Suppose `Z | M` is a nonempty zero-sum subsequence with `|Z|<=t`. Then

`|M Z^{-1}| >= N = D_k(G)`.

By the definition of `D_k(G)`, the complement contains `k` pairwise disjoint nonempty zero-sum subsequences. Together with `Z`, these give `k+1` disjoint zero sums in `M`, contradiction.

Hence `M` is `t`-short-free.

### Part 2 — completion is total zero

By definition of `g`,

`sigma(S)=sigma(M)+g=0`.

### Part 3 — completion remains t-short-free

Suppose `Z | S` is a nonempty zero-sum subsequence with `|Z|<=t`.

By Part 1, `Z` cannot lie entirely in `M`; therefore it uses the new occurrence `g`. Write

`Z=g R`

with `R | M` and `|R|<=t-1`.

Since `sigma(Z)=0`,

`sigma(R)=-g=sigma(M)`.

Therefore

`T=M R^{-1}`

is a zero-sum sequence. Its length satisfies

`|T| >= N+t-(t-1)=N+1`.

Choose any `N` terms of `T`. By `D_k(G)=N`, those `N` terms contain `k` pairwise disjoint nonempty zero-sum subsequences

`A_1,...,A_k`.

Their union uses at most `N` terms, whereas `|T|>=N+1`. Hence the complementary subsequence

`L=T (A_1 ... A_k)^{-1}`

is nonempty. Because `T` and every `A_i` are zero-sum,

`sigma(L)=0`.

Thus `A_1,...,A_k,L` are `k+1` pairwise disjoint nonempty zero-sum subsequences of `T`, hence of `M`, contradiction.

So `S` is `t`-short-free. ∎

## 3. Exact specialization to C5^3 and D4

Once the independently replayed authority for

`D_3(C_5^3)=25`

is granted, set

`k=3`, `N=25`, `t=5`.

### Corollary NQ-R10.10 — exact D4 obstruction lift

If a length-30 sequence `M` over `C_5^3` contains no four pairwise disjoint nonempty zero-sum subsequences, then:

1. `M` is 5-short-free; and
2. adjoining `g=-sigma(M)` produces a total-zero length-31 sequence `S=M g` that is also 5-short-free.

Therefore excluding **all** total-zero length-31 5-short-free sequences is a valid sufficient route to proving

`D_4(C_5^3)=30`.

This precisely justifies the search object used by the current saturation/multiplicity programme.

## 4. One-way authority

The completion lemma is one-way.

A total-zero length-31 5-short-free sequence `S` need not automatically yield a length-30 `D_4` obstruction after deleting an arbitrary term. Such an `S` can be a relaxation-level survivor without being a source obstruction.

Therefore:

- **UNSAT / complete exclusion** of the length-31 total-zero 5-short-free class is sufficient for `D_4=30`, provided completeness is independently certified;
- **SAT / a surviving completed sequence** is only a candidate and must still be checked for a deletion whose 30-term source lacks four disjoint zero sums.

This asymmetry should be encoded in solver receipts and manuscript language.

## 5. Relation to the saturation analysis

The R9 manuscript begins its D4 structural programme by assuming a total-zero length-31 sequence with no zero sum of length at most five. The completion lemma supplies the missing bridge from the generalized Davenport obstruction to that object.

Once the bridge is explicit, the subsequent structural steps have a transparent dependency chain:

`D_3=25`

`=> hypothetical length-30 D4 obstruction`

`=> total-zero length-31 5-short-free completion`

`=> multiplicity <=4 and Property-C saturation where applicable`

`=> saturation-defect certificates`

`=> multiplicity grammar`

`=> repeated-stratum rank forcing`

`=> source-level lift-aware search`.

A failure at any arrow narrows the claim rather than being hidden in the solver.

## 6. Search reduction value

The lemma transforms the D4 upper problem from arbitrary length-30 sequences into a more constrained total-zero class after adding one known completion term. The total-zero condition is algorithmically useful:

- one coordinate/term can be reconstructed from the others;
- symmetry canonicalization may normalize relative to the completion term;
- complement arguments become exact;
- saturation and Property-C machinery can be applied to the completed sequence;
- candidate certificates can carry both source and completion identities.

The amount of actual computational reduction must be measured; no asymptotic speedup is inferred from the lemma alone.

## 7. Prior-art boundary

The 2025 rank-two inverse-D_k literature proves a stronger extremal equivalence in rank at most two: for a zero-sum sequence at the exact rank-two `D_k` length, failure to partition into `k+1` zero sums is characterized by the absence of a zero sum shorter than the exponent.

The R10 lemma is more elementary and more general in a different direction: it applies to every finite abelian group once `D_k(G)=N` is known, at length `N+t`, and produces a total-zero `t`-short-free completion. It does not classify the completed sequence.

The submission must search for this exact completion observation before claiming it as a new lemma. Even if donor-subsumed, writing it explicitly remains necessary because it validates the D4 computational search space.
