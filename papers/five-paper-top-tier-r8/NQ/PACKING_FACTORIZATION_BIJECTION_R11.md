# Packing–factorization bijection for generalized-Davenport completions — R11

Date: 2026-08-26

Status: analytic theorem. Generic factorization language is donor-owned. Numerical `C_5^3` consequences remain conditional on independent replay authority for `D_3(C_5^3)=25` until issue #1383 closes.

## 1. Setup

Let `G` be a finite abelian group. Write `nu(T)` for the largest number of pairwise disjoint nonempty zero-sum subsequences of a sequence `T`.

Fix `k>=1` and suppose

`D_k(G)=N`.

Let `t>=1`, and let `M` be a sequence with

`|M|=N+t`

and no `k+1` pairwise disjoint nonempty zero sums. Define the one-term completion

`g=-sigma(M)`,

`S=M g`.

Thus `sigma(S)=0` and `|S|=N+t+1`.

The R10 completion lemma already gives the short-free completion. The statements below sharpen the relation between source packings and completed block-monoid factorizations.

## 2. Exact source and completion packing numbers

### Theorem NQ-R11.1

Under the setup above:

1. `nu(M)=k`;
2. `M` has no nonempty zero-sum subsequence of length at most `t`;
3. `S` has no nonempty zero-sum subsequence of length at most `t`;
4. `nu(S)=k+1`;
5. every maximum `(k+1)`-packing of `S` contains the distinguished occurrence `g`.

### Proof

Because `|M|>=D_k(G)`, the definition of `D_k` gives `nu(M)>=k`; the obstruction hypothesis gives `nu(M)<=k`, proving equality.

If `M` contained a zero sum `Z` with `|Z|<=t`, then `|M Z^{-1}|>=N`, so the complement would contain `k` disjoint zero sums. Together with `Z` this gives `k+1`, contradiction. Hence `M` is `t`-short-free.

Now suppose `S` contains a zero sum `Z` with `|Z|<=t`. If `g` is not in `Z`, this contradicts short-freeness of `M`. If `g` is in `Z`, then the complement `C=S Z^{-1}` is a zero-sum subsequence of `M` with

`|C|>=N+1`.

Choose any `N` occurrences of `C`. By `D_k(G)=N`, those `N` occurrences contain `k` disjoint nonempty zero sums. They use at most `N` occurrences, so the complement of those `k` zero sums inside `C` is nonempty; since `C` and the `k` selected factors all sum to zero, that complement is itself a nonempty zero sum. Thus `M` would contain `k+1` disjoint zero sums, contradiction. Hence `S` is also `t`-short-free.

Take any maximum `k`-packing `Z_1,...,Z_k` in `M`. The complement in `S` is nonempty because it contains `g`, and it is zero-sum because `S` and every `Z_i` have sum zero. Hence `nu(S)>=k+1`.

If `S` admitted `k+2` disjoint zero sums, at most one could contain the single occurrence `g`; deleting that factor would leave at least `k+1` disjoint zero sums inside `M`, contradiction. Therefore `nu(S)=k+1`, and every maximum packing must contain `g`. ∎

## 3. Zero-sum-free residual theorem

### Theorem NQ-R11.2

Let `Z_1,...,Z_k` be **any** maximum packing of `M`, and define the residual

`R=M (Z_1...Z_k)^{-1}`.

Then:

1. every `Z_i` is a zero-sum atom;
2. `R` is zero-sum-free;
3. `R g` is a zero-sum atom;
4. `t <= |R| <= D(G)-1`;
5. `t+1 <= |R g| <= D(G)`.

### Proof

If some `Z_i` were not minimal zero-sum, it would split into two nonempty zero-sum factors, producing a `(k+1)`-packing in `M`. Thus every `Z_i` is an atom.

If `R` contained a nonempty zero-sum subsequence, it would join `Z_1,...,Z_k` to form a `(k+1)`-packing in `M`. Thus `R` is zero-sum-free, giving `|R|<=D(G)-1`.

Because `sigma(Z_i)=0` for every `i`,

`sigma(R)=sigma(M)=-g`,

so `R g` is zero-sum. It is minimal: a proper zero-sum subsequence avoiding `g` would be a zero sum in `R`; a proper zero-sum subsequence containing `g` would have a nonempty complementary zero-sum subsequence inside `R`. Both are impossible. Hence `R g` is an atom.

The completion `S` is `t`-short-free by Theorem NQ-R11.1, so every atom in it has length at least `t+1`. In particular `|R g|>=t+1`, i.e. `|R|>=t`. The upper bound `|R g|<=D(G)` is the definition of the ordinary Davenport constant as maximum atom length. ∎

The zero-sum-free conclusion is stronger than the earlier R10 note's statement that the distinguished residual is merely non-zero-sum.

## 4. Exact packing–factorization bijection

Let `P_k(M)` denote maximum `k`-packings of `M`, modulo permutation of the `k` factors. Let `F_{k+1}^g(S)` denote maximum-length atomic factorizations of `S` into `k+1` atoms, with the unique factor containing the distinguished occurrence `g` marked.

### Theorem NQ-R11.3 — bijection

There is a canonical bijection

`P_k(M) <-> F_{k+1}^g(S)`.

It sends a maximum source packing

`{Z_1,...,Z_k}`

to

`{Z_1,...,Z_k,Rg}`,

where `R` is its zero-sum-free residual.

The inverse removes the unique atom containing `g`; deleting `g` from that atom gives the source residual.

### Proof

Theorem NQ-R11.2 shows the forward map is an atomic factorization of all of `S` into `k+1` factors.

Conversely, let

`S=A_g A_1...A_k`

be a maximum atomic factorization with `g` in `A_g`. The `A_1,...,A_k` lie in `M` and are disjoint zero sums, so they form a `k`-packing. Since `nu(M)=k`, it is maximum. The residual is exactly `A_g g^{-1}`. Atom minimality of `A_g` implies this residual is zero-sum-free: any zero sum in the residual would have a zero-sum complement in `A_g`. The two constructions are inverse. ∎

### Consequence

A clean-room engine need not treat “packing” and “factorization” as merely analogous certificates. On the completed obstruction they are exactly equivalent finite objects, with the completion atom encoding the source zero-sum-free residue.

This gives a structurally distinct replay interface:

- Engine A may enumerate source packings;
- Engine B may enumerate completed atomic factorizations;
- a neutral comparator checks the bijection by deleting/adding the distinguished completion occurrence.

Agreement is stronger than running two solvers over the same packing encoding.

## 5. `C_5^3`, `D_4` specialization

Conditional on replay authority for

`D_3(C_5^3)=25`, 

set `k=3`, `N=25`, `t=5`. Any hypothetical length-30 obstruction `M` to four disjoint zero sums has:

- `nu(M)=3`;
- no zero sum of length at most five;
- every maximum three-packing consists of three atoms;
- every maximum three-packing leaves a zero-sum-free residual `R` with
  `5 <= |R| <= 12`;
- `R g` is an atom with length `6..13`;
- the total-zero completion `S=Mg` has `nu(S)=4`;
- every maximum four-factorization of `S` is atomic, covers all 31 terms, and contains `g` in exactly one atom.

This upgrades the R10 eleven undistinguished atom-length skeletons to a **distinguished residual skeleton**.

Let the three source atom lengths, sorted, be

`6 <= a <= b <= c <= 13`.

Then

`|R|+a+b+c=30`,

with `5<=|R|<=12`. Exactly 31 quadruples `( |R| ; a,b,c )` satisfy these bounds:

- `|R|=5`: `(6,6,13)`, `(6,7,12)`, `(6,8,11)`, `(6,9,10)`, `(7,7,11)`, `(7,8,10)`, `(7,9,9)`, `(8,8,9)`;
- `|R|=6`: `(6,6,12)`, `(6,7,11)`, `(6,8,10)`, `(6,9,9)`, `(7,7,10)`, `(7,8,9)`, `(8,8,8)`;
- `|R|=7`: `(6,6,11)`, `(6,7,10)`, `(6,8,9)`, `(7,7,9)`, `(7,8,8)`;
- `|R|=8`: `(6,6,10)`, `(6,7,9)`, `(6,8,8)`, `(7,7,8)`;
- `|R|=9`: `(6,6,9)`, `(6,7,8)`, `(7,7,7)`;
- `|R|=10`: `(6,6,8)`, `(6,7,7)`;
- `|R|=11`: `(6,6,7)`;
- `|R|=12`: `(6,6,6)`.

These 31 branches are the eleven R10 atom-length partitions with the completion atom distinguished and then shortened by one occurrence.

## 6. Search consequences

A source-level `D_4` candidate can now be required to carry one of two mutually checkable certificates:

### Source-packing certificate

1. three disjoint atom selectors in `M`;
2. a residual selector covering every remaining occurrence;
3. residual zero-sum-freeness;
4. residual length one of `5..12` and one of the 31 exact length skeletons;
5. `sigma(R)=sigma(M)`.

### Completion-factorization certificate

1. append the distinguished `g=-sigma(M)`;
2. four atom selectors partition all 31 occurrences;
3. exactly one contains `g`;
4. deleting `g` from that factor gives a zero-sum-free sequence;
5. deleting the entire distinguished factor leaves the other three source atoms.

The neutral conversion is exact and reversible. A disagreement therefore exposes an implementation error or a source/completion identity mismatch rather than a mathematical ambiguity.

The existing saturation/multiplicity stratification and the new factorization stratification are orthogonal: one classifies point multiplicities and rank; the other classifies maximum zero-sum decompositions. Their intersection can be used for branch pruning and, more importantly, for a second completeness accounting of the full census.

## 7. Further inverse-theory boundary

The extreme residual branch `|R|=12` is a maximum zero-sum-free sequence and `R g` is a maximal-length atom of length `D(C_5^3)=13`. Classical work gives structural information on maximal atoms in elementary p-groups, but the current literature search does not justify replacing that branch by a single normal form. Any additional inverse classification used for pruning must be cited and independently checked before becoming load-bearing.

## 8. Authority boundary

The bijection is analytic and does not depend on the current search implementation. Generic block-monoid terminology and known inverse zero-sum theory are donor-owned.

The `C_5^3` numerical specialization depends on the independently replayed input `D_3(C_5^3)=25`; until #1383 closes, it is a conditional search reduction, not external theorem authority. It does not determine whether `D_4(C_5^3)` is 30 or 31 by itself.
