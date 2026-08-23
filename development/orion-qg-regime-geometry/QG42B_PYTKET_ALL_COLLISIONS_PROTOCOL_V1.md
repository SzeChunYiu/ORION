# ORION-QG QG-42b — prospective pytket all-collision transfer

Date: 2026-08-22
Parent: QG-42 draft PR #950.
Status: **FROZEN AFTER QG-42 PANEL-CONSTRUCTION CANNOT_CHECK AND BEFORE ANY PYTKET ROUTING OUTCOME.**

QG-42 froze a quota of 12 consecutive non-isomorphic degree-summary collision pairs. Its compiler-blind panel construction found only 8 such consecutive pairs and correctly stopped before routing. QG-42 remains historical `QG42_CANNOT_CHECK_PANEL_CONSTRUCTION`; this successor does not rewrite it.

## Scientific target

Test the same held-out production-compiler information question without an arbitrary quota: among the complete structural collision universe, can two non-isomorphic six-qubit CX graphs with the same cheap relabelling-invariant degree summary have the same best routed two-qubit cost but different, or disjoint, optimal initial-layout sets?

No sign of the answer is predicted.

## Frozen compiler-blind universe

- logical qubits: 6;
- simple undirected graphs with exactly 7 edges;
- enumerate all `C(15,7)=6435` labelled graphs;
- canonical graph key: lexicographically minimum sorted edge tuple over all 720 vertex permutations;
- deduplicate to non-isomorphic graphs;
- summary: sorted six-entry degree sequence.

Retain every summary fiber containing at least two non-isomorphic canonical graphs. The QG-42 outcome-blind structural run established only the following admissible construction facts: 24 non-isomorphic graph classes total, 5 collision fibers, and that its old consecutive-pair quota yielded 8 pairs. No pytket routing was executed.

**QG-42b panel = every unordered pair of distinct canonical graphs inside every collision fiber.**

Sort fibers lexicographically by degree sequence and pairs lexicographically by their two canonical graph keys. There is no quota. Serialize the complete pair list and SHA-256 digest before importing or calling pytket. The panel builder must contain no `pytket` import.

If the complete collision panel is empty, terminal `QG42B_CANNOT_CHECK_EMPTY_COLLISION_UNIVERSE`.

## Compiler, choices, architectures and cost

Pin Python 3.12 and `pytket==2.18.1`.

For each unique graph, construct `Circuit(6)` and append one `CX(i,j)` for each sorted edge with `i<j` as the fixed direction.

Choice universe: all 720 logical-to-physical initial layouts, lexicographic order.

Architectures:
- Line-6: `(0,1),(1,2),(2,3),(3,4),(4,5)`;
- Ring-6: same plus `(5,0)`.

For each layout:
1. rebuild the pristine circuit;
2. apply the explicit layout with `place_with_map`;
3. route with `MappingManager(architecture).route_circuit(...,[LexiRouteRoutingMethod(10)])`;
4. treat the route return value as diagnostic only;
5. require every explicit two-qubit command to satisfy `Architecture.valid_operation`;
6. primary cost = post-routing `Circuit.n_2qb_gates()`;
7. `depth_2q()` is diagnostic only.

Cache results by `(canonical graph, architecture)`. Pair count must not multiply routing calls.

## Exact bounded quantities

For graph G and architecture A, exhaust all 720 layouts:
- `V(G,A)=min_p C(G,p,A)`;
- `Arg(G,A)={p:C(G,p,A)=V(G,A)}`.

For every complete collision pair `(G,H)` record same-value status, argmin sizes, intersection, Jaccard overlap, and complete cost-vector hashes.

Architecture-level selection separation exists iff at least one pair has equal `V` and unequal `Arg`. Strong separation additionally requires disjoint argmin sets. A topology-stable strong witness is the same pair disjoint on both architectures.

Honest terminals:
- `QG42B_PYTKET_ALL_COLLISIONS_SELECTION_SEPARATION_BOTH_TOPOLOGIES_MACHINE_CHECKED`
- `QG42B_PYTKET_ALL_COLLISIONS_SELECTION_SEPARATION_ONE_TOPOLOGY_ONLY`
- `QG42B_PYTKET_ALL_COLLISIONS_NO_SELECTION_SEPARATION`
- `QG42B_CANNOT_CHECK`

A negative is first-class and may not be widened beyond this frozen universe.

## Independent frontier verification

A separately implemented verifier must:
- independently enumerate the 6435 graphs, canonicalize isomorphism classes, reconstruct all collision fibers and **all** unordered within-fiber pairs;
- verify exact equality with the serialized compiler-blind panel;
- independently rerun all 720 layouts for every unique graph on both architectures;
- recompute every optimum value, argmin set and cost-vector hash;
- verify architecture validity after every route;
- verify all pair-level separation flags;
- pin pytket 2.18.1;
- perform deterministic replay.

Hostile controls:
- constant input CX count (=7) must be recognized as a dead instrument;
- layout-identity collapse cannot support a selection-set claim and must be rejected;
- at least one graph/architecture must show layout-dependent primary cost and at least one route must alter the two-qubit resource, otherwise `CANNOT_CHECK`.

## Authority ceiling

May authorize only the bounded information result for pytket 2.18.1, six-qubit seven-edge CX graphs in the complete degree-summary collision universe, all 720 explicit initial layouts, the two frozen architectures, LexiRouteRoutingMethod(10), and post-routing two-qubit-gate count.

Always false: all-circuit theorem; all-pytket-version claim; globally optimal routing; comparative compiler performance; hardware/FT claim; physical quantum advantage; generic symmetry/decision-theory novelty; external novelty authority.

The frontier harness remains the promotion boundary. Workflow success without independent full-layout agreement is not scientific GREEN.
