# X1-B k=4 — exact ten-prefix forbidden-subset-sum result

Parent: #900.
Frozen protocol: `X1B_K4_TEN_PREFIX_FORBIDDEN_SUM_PROTOCOL.md`.
Authoritative search source: `x1b_k4_ten_prefix_forbidden_sum_exact.cpp`.
Committed before theorem promotion or C15 proof assembly.

## Result

The exact symmetry-normalized exhaustive search completed with:

- length-10 admissible prefix: **NONE FOUND — exhaustive NO**;
- maximum admissible length: **9**;
- DFS nodes: **19,083,343**;
- memoized dead states: **17,063,102**.

One explicit length-9 witness is

```text
(0,0,1)^4,
(1,0,1)^3,
(0,2,1)^2.
```

Primitive subset-sum replay confirms that every nonempty subset sum of this length-9 sequence avoids

```text
{(0,0,0),(0,1,0),(2,1,0),(0,3,0),(3,1,0),(4,0,0),(2,3,0)}.
```

The search proves that no tenth term can be added in any symmetry-equivalent configuration.

## Completeness basis

1. A valid length-10 prefix cannot lie entirely in the plane `z=0`, because that would be a length-10 zero-sum-free sequence in `C_5^2`, contradicting `D(C_5^2)=9`.
2. Therefore at least one term is off-plane.
3. The subgroup of `GL(3,5)` consisting of maps

   `(x,y,z) -> (x+az, y+bz, cz)`, with `c!=0`,

   fixes the forbidden plane pointwise and acts transitively on off-plane vectors. Hence one selected off-plane term may be normalized to `e3=(0,0,1)` without changing the forbidden set.
4. The remaining nine terms are enumerated as a multiset in a fixed nondecreasing canonical order; repetitions are allowed.
5. The exact represented-subset-sum state is carried as a 125-bit set. An extension by x is accepted iff its translated current sumset avoids the seven forbidden values. This condition is exactly equivalent to preserving the required avoidance invariant.
6. Memoization by `(sumset, depth, last canonical index)` is sound because all future legal extensions depend only on those coordinates.

## Scientific consequence if independently confirmed

The common rank-2 residual obstruction requires a ten-term prefix T whose nonempty subset sums avoid exactly this seven-point set. Exhaustive nonexistence therefore eliminates **both** final k=4 quotient orbits simultaneously.

This would close the entire k=4 / 13-point residual, leaving the separately governed k=3 confirmation as the only finite residual before full C15 proof assembly.

## Authority boundary

This is one exact implementation of a prospectively frozen finite theorem. Before promoting k=4 closure, require:

- an independently implemented confirmation or equivalent formal certificate;
- harness replay of the frozen search contract;
- primitive verification of the symmetry normalization and length-9 witness;
- no inference from resource exhaustion (the reported run completed exhaustively).