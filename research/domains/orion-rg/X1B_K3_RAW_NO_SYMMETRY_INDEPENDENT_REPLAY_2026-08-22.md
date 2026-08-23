# X1-B k=3 — raw no-symmetry independent replay eliminates every candidate

Parent: #900.
Independent verifier: `x1b_k3_raw_no_symmetry_replay.cpp`.
Committed before k=3 closure or C15 proof assembly.

## Independence

This verifier deliberately avoids the main symmetry machinery of both earlier k=3 implementations:

- no `GL(3,3)` quotient;
- no canonical orbit representative computation;
- no support-stabilizer quotient;
- no reuse of the exploratory or confirmatory Python code.

It directly enumerates every raw 10-position multiset satisfying the frozen short-zero-sum generator conditions:

- nonzero `F_3^3` support elements;
- multiplicity at most 2, since three equal nonzero elements sum to zero;
- no opposite support pair;
- no three distinct support elements summing to zero;
- support sizes 5 through 8.

Every completed 10-position multiset is then replayed from primitive position subsets.

## Exact result

Fresh run:

```text
raw_candidates 1190124 no_disjoint 400608 inconsistent 400608 consistent 0 max_masks 43
```

Thus:

- raw generated 10-position candidates: **1,190,124**;
- candidates with no two disjoint nonempty quotient zero sums: **400,608**;
- among those, common-RHS `F_5` scalar systems inconsistent: **400,608**;
- scalar-consistent candidates: **0**.

The largest zero-sum-subset count among admitted no-disjoint candidates was 43.

## Consequence

There is no raw 10-position quotient residual satisfying simultaneously:

1. the k=3 no-short-zero-sum residual condition;
2. no two disjoint quotient zero sums; and
3. existence of scalar values on the ten residual positions for which **every** nonempty quotient-zero-sum subset has one common nonzero scalar sum (normalized to 1).

This conclusion does not depend on a symmetry quotient. It independently confirms and strengthens the earlier result that the 43 canonical residual orbits all have inconsistent common-RHS systems.

## Interface to local scalarization

In the k=3 branch there are already eleven fixed quotient-zero-sum triple blocks plus one residual quotient-zero-sum block. Fixing those eleven other blocks, the committed p-group local-scalarization lemma supplies one nonzero linear functional on `C_5^3` under which every legal residual replacement block has the same nonzero scalar value. Every quotient-zero-sum subset of the 10-position residual is such a legal twelfth block relative to the fixed eleven triples.

Therefore a genuine C15 k=3 counterexample would induce exactly a common-RHS scalar assignment of the type ruled out above.

## Authority boundary

This is a raw independent finite replay and supplies strong mathematical evidence for k=3 closure. The canonical research-harness campaign remains non-authorizing by design and should still be executed/admitted for provenance. Full `D(C_15^3)=43` promotion additionally requires the whole proof chain to survive hostile donor/interface audit.