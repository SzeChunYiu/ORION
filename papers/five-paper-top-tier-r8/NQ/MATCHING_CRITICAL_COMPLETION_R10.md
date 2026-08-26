# Matching-Critical Completion of Generalized Davenport Obstructions — R10

Date: 2026-08-26

Status: analytic strengthening of the completion lemma. Numerical C5^3 consequences remain conditional on the independently replayed `D_3=25` authority until issue #1383 closes.

## 1. Packing number

For a sequence `T` over a finite abelian group, let

`nu(T)`

be the maximum number of pairwise disjoint nonempty zero-sum subsequences of `T`.

Thus `D_k(G)=N` means every sequence of length at least `N` has `nu>=k`.

## 2. Critical-completion theorem

Assume `D_k(G)=N`, let `t>=1`, and let `M` be a sequence of length `N+t` satisfying

`nu(M)<=k`.

Because `|M|>=N`, in fact `nu(M)=k`.

Let

`g=-sigma(M)`

and `S=M g`.

The companion completion lemma proves that `S` is total zero and `t`-short-free.

### Theorem NQ-R10.11 — exact one-step packing increase

Under these assumptions:

1. `nu(M)=k`;
2. `nu(S)=k+1`;
3. every packing of `k+1` disjoint zero-sum subsequences in `S` uses the distinguished occurrence `g`; and
4. therefore deletion of `g` lowers the packing number by exactly one:

   `nu(S)-nu(S g^{-1})=1`.

### Proof

The first claim was noted above: `D_k(G)=N` and `|M|>=N` give `nu(M)>=k`, while the obstruction assumption gives `nu(M)<=k`.

To prove `nu(S)>=k+1`, choose any `N` terms of `M`. They contain `k` pairwise disjoint nonempty zero-sum subsequences `A_1,...,A_k`. Their union uses at most `N` terms. Since

`|S|=N+t+1>N`,

the complement

`L=S(A_1...A_k)^{-1}`

is nonempty. The total of `S` and every `A_i` is zero, so `sigma(L)=0`. Hence `A_1,...,A_k,L` form a packing of size `k+1` in `S`.

If `S` had a packing of size at least `k+2`, at most one packed zero-sum subsequence could contain the single occurrence `g`. Removing that packed factor if necessary would leave at least `k+1` disjoint zero sums entirely inside `M`, contradiction. Thus `nu(S)=k+1`.

Finally, any size-`k+1` packing in `S` must use `g`; otherwise all its factors lie in `M`, again contradicting `nu(M)=k`. ∎

## 3. C5^3 specialization

Conditional on `D_3(C_5^3)=25`, let `M` be any hypothetical length-30 sequence with no four disjoint zero sums. Then

`nu(M)=3`.

For its completion `S=M(-sigma(M))`,

`nu(S)=4`,

and every four-packing in `S` contains the distinguished completion term.

Combined with the completion lemma:

- `|S|=31`;
- `sigma(S)=0`;
- `S` has no zero sum of length at most five;
- `nu(S)=4`;
- the completion term lies in every maximum four-packing; and
- deleting it leaves packing number exactly three.

These conditions are strictly stronger than “total-zero and 5-short-free.”

## 4. Hypergraph interpretation

Let the zero-sum hypergraph of `S` have one vertex for each occurrence of the sequence and a hyperedge for each nonempty zero-sum subsequence.

Then the completion term `g` is a **matching-critical vertex**:

`nu(H)=k+1`,

`nu(H-g)=k`.

Equivalently, every maximum `(k+1)`-matching covers `g`.

This provides a third independent certificate language for the source-lift search. It is stronger than merely finding one four-packing that contains `g`.

## 5. Solver consequences for D4

A source-level candidate completion should satisfy all of the following before it is treated as a genuine D4 obstruction lift:

1. total zero;
2. 5-short-freeness;
3. exact packing number four;
4. completion-term criticality: deleting `g` yields exact packing number three;
5. every four-packing uses `g` (equivalent to 4 when exact packing values are trusted);
6. the 30-term source is the declared deletion `M=Sg^{-1}` and fails four-bin packing.

### Fail-fast use

If a completed candidate admits **five** disjoint zero sums, reject it immediately: at least four avoid the single completion term, so the source is not a D4 obstruction.

If a completed candidate has a four-packing avoiding `g`, reject it immediately for the same reason.

These cuts can be added lazily to a source-level SAT/CP-SAT or hypergraph-matching formulation.

## 6. Authority asymmetry

The theorem improves both positive and negative interpretation:

- a complete proof that no sequence satisfies the stronger completed-source conditions proves there is no length-30 D4 obstruction;
- a sequence satisfying only total-zero/short-free conditions remains a relaxation survivor;
- a sequence satisfying exact matching-critical completion plus source four-packing failure is a genuine obstruction witness.

The solver manifest should explicitly record which level has been checked.

## 7. Relation to inverse-D_k literature

Inverse generalized-Davenport theory studies extremal zero-sum sequences whose factorization/packing number is bounded. The matching-critical completion statement is a simple consequence of the one-term completion construction plus the definition of `D_k`; its exact novelty must be checked against that literature.

Even if the observation is donor-subsumed, its explicit use materially strengthens the computational proof contract because it separates completed relaxation survivors from true source obstructions and supplies an independently checkable matching certificate.
