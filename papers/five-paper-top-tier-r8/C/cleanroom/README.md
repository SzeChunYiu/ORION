# FiberGuard R8 Clean-Room Replay

Date: 2026-08-26

Terminal: `C_FIBERGUARD_INDEPENDENT_REPLAY_PASS`

A new implementation reproduces the registered FiberGuard benchmark without importing or invoking the reference program.

## Independent constructions

- **Graph colouring:** 156 six-node graph-atlas representatives are exhaustively relabeled, producing exactly 32,768 unique labeled masks. Chromatic number is solved by minimum independent-set cover; endpoint values are rechecked by complete color assignments.
- **Set cover:** the 155,106 covering five-set families are regenerated from the U5 subset universe. Minimum cover is solved by coverage-state BFS; endpoints are rechecked by cardinality-ordered subset enumeration.
- **2-CNF:** the 24 clauses are regenerated as a variable-pair/sign product. All 42,504 five-clause formulas are counted by recursive formula simplification; endpoints are rechecked by truth tables.

## Exact agreement

The clean-room lane matches every registered instance count, fibre count, maximum diameter, endpoint value, endpoint witness, fibre multiplicity, candidate-refinement statistic, selected collision-guided feature, and matched baseline across all three domains.

Total instances replayed: **230,378**.

Reference blob: `3519d2ae6dfb61b94ebefb23c0645e5a69cbe11f`  
Clean-room script SHA-256: `1d4f6337000afff0f2e2174b94fc294d27cd96aace3f954048f1feee05d746b8`  
Clean-room result-file SHA-256: `4055a69b2bf63bb64e0113a79181eb19112169fb9b4fbbbf79c2720c827f0518`

## Boundary

This is an independent **internal** replay. It does not establish external replication, novelty, scaling beyond the frozen panels, real-distribution collision prevalence, feature-acquisition cost, or journal readiness.
