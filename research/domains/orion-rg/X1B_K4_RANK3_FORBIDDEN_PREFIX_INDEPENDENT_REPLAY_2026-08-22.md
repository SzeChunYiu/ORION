# X1-B k=4 — independent no-memo replay closes all three rank-3 forbidden classes

Parent: #900.
Primary protocol: `X1B_K4_RANK3_FORBIDDEN_PREFIX_PROTOCOL.md`.
Independent verifier: `x1b_k4_rank3_forbidden_prefix_nomemo_replay.cpp`.

## Independence

This replay deliberately does **not** use:

- layerwise dynamic programming;
- memoization;
- illegal-state deduplication across different prefixes;
- minimum-last dominance.

It walks the full canonical nondecreasing multiset tree directly. The only shared mathematics is the primitive exact legality update for the frozen forbidden-subset-sum problem.

## Results

### R3-10

- canonical DFS nodes: `120,661,048`
- deepest legal prefix: length `9`
- length-10 witness: **none**

### R3-11

- canonical DFS nodes: `79,704,122`
- deepest legal prefix: length `9`
- length-10 witness: **none**

### R3-12

- canonical DFS nodes: `55,788,917`
- deepest legal prefix: length `9`
- length-10 witness: **none**

## Agreement

The independent verifier agrees exactly with the prospectively frozen primary layerwise enumerations:

> **Every one of the three rank-3 forbidden-set classes has exact maximum admissible prefix length 9.**

Since those three `GL(3,5)` classes cover all 116 rank-3 bilinear completions of the two surviving k=4 quotient orbits, **no rank-3 completion can satisfy the required ten-prefix condition**.

Thus the rank-3 realization branch of the k=4 residual is eliminated by two algorithmically distinct exact enumerations.

## Remaining k=4 frontier

The only bilinear realization type not covered by this conclusion is the separately identified **rank-2 completion with an additional radical coordinate**. The radical coordinate is invisible to the rank-2 Gram matrix and can alter residual subset sums, so it must be treated independently.

## Authority boundary

This packet closes the rank-3 completion branch of the finite k=4 interface. It does not yet close the rank-2 radical family, the full k=4 residual, or prove `D(C_15^3)=43`. Novelty authority remains open.