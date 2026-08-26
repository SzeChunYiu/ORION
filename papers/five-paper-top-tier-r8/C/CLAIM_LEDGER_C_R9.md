# Paper C Claim Ledger R9

| ID | Claim | Evidence | Boundary |
|---|---|---|---|
| C9-1 | For a scalar target, the exact representation-only minimax absolute radius equals half the maximum target diameter of a fibre. | `VERIFIED`; endpoint proof | Exact target range and exact representation equality. Generic optimal-recovery machinery is donor-owned. |
| C9-2 | Integer, randomized absolute, squared-loss, exact-interval, Boolean-classification, and deterministic-coarsening corollaries hold. | `VERIFIED` | Stated loss and exact-coverage conventions only. |
| C9-3 | The complete six-vertex graph, five-element set-cover, and four-variable 2-CNF panels have the recorded maximum fibre diameters 1, 1, and 4. | `FINITE_EXACT`; two target solvers per instance | Frozen generators and feature maps only. |
| C9-4 | The registered collision-guided feature closes every fibre on each finite panel and strictly beats the frozen matched baseline. | `FINITE_EXACT` | Panel-specific sufficiency; no deployment inference. |
| C9-5 | For the graph representation `Phi(G)=(sorted degree sequence, triangle count)`, chromatic-number fibre diameter is unbounded. | `PROVEN-ALL-SIZE` in `FIBERGUARD_GRAPH_SCALING_THEOREM_R9.md` | Uses donor Häggkvist–Hell graph existence/unbounded-chromatic theorem; ORION contribution is the exact matched bipartite collision construction for the frozen feature map. |
| C9-6 | For every `k>=2`, one `Phi`-fibre contains a bipartite graph and a graph of chromatic number at least `k`. | `PROVEN-ALL-SIZE` | High graph is two copies of a donor regular triangle-free graph; low graph is an explicit regular bipartite circulant with the same vertex count and degree. |
| C9-7 | Every `Phi`-only chromatic-number estimator has unbounded worst-case absolute error, and exact intervals have unbounded worst-case width. | `PROVEN` from C9-5 and the radius theorem | Worst-case information claim, not average-case performance or hardness. |
| C9-8 | More training or model capacity cannot repair an exact collision while the input map is frozen. | `VERIFIED` | Model receives exactly the declared representation. |
| C9-9 | The same all-size collision theorem holds for the set-cover and 2-CNF feature maps. | `OPEN; NOT CLAIMED` | Only finite exact panels currently registered. |
| C9-10 | The all-size graph collisions are prevalent in public or production learned-optimizer datasets. | `OPEN; EXTERNAL EVIDENCE GATE` | Requires corpus audit with exact feature equality and exact targets. |
| C9-11 | Collision-guided refinement improves runtime, prediction, calibration, or downstream decisions. | `OPEN; EXTERNAL EXPERIMENT GATE` | Requires a frozen learned-optimization pipeline and matched feature-cost baseline. |
| C9-12 | The Häggkvist–Hell graph family or the general radius-of-information theorem is ORION novelty. | `DONOR_OWNED` | Residual is the frozen-representation collision theorem, exact audits, and refinement protocol. |
| C9-13 | Panel closure proves an all-size factorization through the refined feature. | `FORBIDDEN` | A finite panel cannot grant all-size sufficiency. |

## Current publication boundary

The former scaling blocker is closed for one exact, natural graph-colouring representation by an unbounded theorem. The remaining top-tier significance blocker is external and operational: establish whether audited collisions or near-collisions occur in learned-optimization feature pipelines and whether FiberGuard-guided enrichment/abstention changes a consequential decision relative to matched-cost baselines.
