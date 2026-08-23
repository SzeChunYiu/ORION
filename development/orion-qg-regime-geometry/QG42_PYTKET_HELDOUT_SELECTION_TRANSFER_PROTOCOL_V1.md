# ORION-QG QG-42 — prospective pytket held-out value/selection transfer

Date: 2026-08-22
Parent conceptual result: QG-38 exact query-indexed observation hierarchy.
Hypothesis generators only: bounded QG-40 Qiskit and QG-41 SixLCU records on a separate branch. They provide no QG-42 outcome authority.
Status: **FROZEN BEFORE ANY PYTKET ROUTING OUTCOME IS COMPUTED.**

## 1. Scientific question

TARE proves that a symmetry-invariant summary may determine the optimum value while not determining which optimizer realizes it. Bounded follow-ups saw related selection failures in Qiskit and SixLCU. QG-42 asks whether the selection failure survives prospectively in a second external production compiler on a different held-out circuit panel and topology pair.

The target is not comparative performance. It is an information question:

> Can two circuits that a cheap relabelling-invariant structural summary cannot distinguish have the same best achievable routed two-qubit cost but require different, even disjoint, optimal initial-layout sets?

Either outcome is first-class.

## 2. Frozen production compiler and API

Pin exactly:
- Python 3.12;
- `pytket==2.18.1`;
- `pytket.circuit.Circuit`;
- `pytket.architecture.Architecture`;
- `pytket.placement.place_with_map`;
- `pytket.mapping.MappingManager`;
- `pytket.mapping.LexiRouteRoutingMethod(10)`.

No automatic `GraphPlacement`, `LinePlacement`, or noise-aware placement is allowed in the primary cost oracle because initial placement is the explicit choice variable.

## 3. Held-out circuit universe selected without compiler calls

Use six logical qubits `{0,...,5}` and the 15 undirected simple edges `{i,j}`, `i<j`.

Enumerate **every simple graph with exactly seven edges**: `C(15,7)=6435` graphs, in lexicographic edge-combination order.

For each graph:
- cheap summary `S(G)` = sorted six-entry degree sequence;
- canonical isomorphism key `K(G)` = lexicographically smallest edge tuple over all 720 vertex permutations.

Deduplicate by canonical key. Within every degree-summary fiber, sort distinct canonical keys lexicographically.

Frozen pair panel:
1. retain fibers with at least two non-isomorphic members;
2. sort fibers lexicographically by degree sequence;
3. within each fiber take consecutive canonical-key pairs `(0,1)`, `(2,3)`, ...;
4. concatenate in that order;
5. take the first **12** pairs.

If fewer than 12 pairs exist, QG-42 terminates `CANNOT_CHECK_PANEL_CONSTRUCTION`; do not change graph size, edge count, summary, or quota.

The panel, its graph keys, summaries, and SHA-256 digest must be serialized **before** importing or calling pytket routing code. A workflow gate must verify that the panel-builder module has no `pytket` import.

## 4. Circuit construction

For a graph G, construct `Circuit(6)`. For each undirected edge `(i,j)` in sorted order append exactly one `CX(i,j)` with `i<j` as control/target. No one-qubit gates and no repeated edges.

The direction convention is part of the frozen instance definition and may not be optimized.

## 5. Choice universe and architectures

Choice = initial logical-to-physical layout, exactly all 720 permutations of six qubits, lexicographic order.

Evaluate each circuit independently on both frozen architectures:

### A. Line-6
Edges `(0,1),(1,2),(2,3),(3,4),(4,5)`.

### B. Ring-6
Edges `(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)`.

For each layout permutation `p`:
1. rebuild the pristine logical circuit;
2. map logical qubit `q` to architecture node `p[q]` with `place_with_map`;
3. call `MappingManager(architecture).route_circuit(circuit,[LexiRouteRoutingMethod(10)])`;
4. require routing success;
5. require every explicit two-qubit command to be architecture-valid after routing;
6. cost `C(G,p,A) = circuit.n_2qb_gates()` after routing.

Record also two-qubit depth as a diagnostic only; it cannot change the primary decision.

No stochastic seeds or heuristic-placement searches are part of the primary oracle.

## 6. Exact panel quantities

For each graph G and architecture A, exhaustively compute all 720 layout costs and define:
- `V(G,A)=min_p C(G,p,A)`;
- `Arg(G,A)={p : C(G,p,A)=V(G,A)}`.

For each frozen pair `(G,H)` with `S(G)=S(H)` record:
- whether `V(G,A)=V(H,A)`;
- `|Arg(G,A)|`, `|Arg(H,A)|`;
- `|Arg(G,A) intersection Arg(H,A)|`;
- Jaccard overlap;
- full 720-entry cost-vector digests.

## 7. Frozen decision hierarchy

Primary positive for architecture A:

`SELECTION_SEPARATION(A)` iff at least one frozen pair satisfies
- same frozen degree summary by construction;
- `V(G,A)=V(H,A)`;
- `Arg(G,A) != Arg(H,A)`.

Strong positive for A:

`DISJOINT_SELECTION_SEPARATION(A)` iff at least one such pair additionally has empty argmin intersection.

Cross-topology strong positive:

`TOPOLOGY_STABLE_DISJOINT_SELECTION` iff the **same frozen graph pair** is a disjoint selection witness on both Line-6 and Ring-6.

No sign is predicted for whether the cheap degree summary determines the optimum value. Report the number of summary fibers/pairs with unequal optimal values separately.

Honest terminals:
- `QG42_PYTKET_SELECTION_SEPARATION_BOTH_TOPOLOGIES_MACHINE_CHECKED`
- `QG42_PYTKET_SELECTION_SEPARATION_ONE_TOPOLOGY_ONLY`
- `QG42_PYTKET_NO_SELECTION_SEPARATION_ON_FROZEN_PANEL`
- `QG42_CANNOT_CHECK`

The first terminal does not require a topology-stable *same-pair* witness; that stronger property is an independent subresult.

## 8. Independent verification

Require a separately implemented verifier that:
- rebuilds all 6435 graphs and the first-12 pair panel from the protocol rules without reading the production panel as its source;
- independently recomputes canonical graph isomorphism keys;
- checks every paired graph is non-isomorphic and summary-equal;
- for every claimed witness, rebuilds both circuits from serialized edge lists and reruns all 720 layouts on the relevant architecture;
- checks route success and architecture validity;
- recomputes optimum values and complete argmin sets;
- requires exact equality with the production witness record.

For non-witness circuits, verify frozen cost-vector hashes by deterministic replay of at least one complete architecture arm. The full production run itself must be byte-identical on deterministic replay.

## 9. Instrument validity and hostile controls

Before interpreting a negative:
- at least one tested circuit/architecture must have layout-dependent primary cost (`max C > min C`), else terminal `CANNOT_CHECK_DEAD_INSTRUMENT`;
- at least one routing output must differ structurally from its pristine input, else `CANNOT_CHECK_ROUTER_NOT_EXERCISED`;
- deliberately replace primary cost by input CX count (constant seven) and require the validity gate to reject that dead instrument;
- deliberately collapse layout identity to a single representative and require the verifier to reject any selection claim based on that ablation.

These controls prevent repetition of QG-40's initially vacuous CX-only measurement.

## 10. Authority ceiling

May authorize only a bounded production-compiler information result on:
- pytket 2.18.1;
- the frozen 12 graph pairs;
- six qubits;
- seven-edge CX circuits;
- exhaustive 720 layouts;
- Line-6 and Ring-6;
- LexiRouteRoutingMethod lookahead 10;
- post-routing two-qubit-gate count.

Always false:
- all-circuit or all-n theorem;
- all-pytket-version claim;
- optimal routing claim beyond the 720 **initial-layout** choice under the fixed pytket routing method;
- comparative compiler performance;
- Qiskit superiority/inferiority;
- hardware noise or FT claim;
- physical quantum advantage;
- generic symmetry/decision-theory novelty;
- external novelty authority.

## 11. Frontier-harness promotion

The frontier harness must bind:
- protocol digest;
- compiler package version;
- pre-routing panel digest;
- production result digest;
- independent verifier result;
- deterministic replay;
- dead-instrument hostile control;
- layout-collapse hostile control;
- hard-false stronger fields.

No manuscript or cross-family theorem may treat QG-42 as positive before this harness returns GREEN.
