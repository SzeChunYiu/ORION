# ORION23.RESPONSIBILITY_CLOSURE_MINIMALITY.v1

## Question

Given a dependency/proof graph and a set of changed or invalidated evidence nodes, what is the smallest fail-closed set of downstream responsibilities that must lose reuse authority before revalidation?

## Model

Let `G=(V,E)` be a directed acyclic dependency graph. An edge `u -> v` means validity of `v` may depend on `u`. Let `R subseteq V` be the responsibility nodes whose certificates may authorize reuse. Let `C subseteq V` be the changed, revoked, stale, or otherwise invalidated nodes.

Define the transitive dependency set

`D(r) = {u in V : there is a directed path u -> ... -> r} union {r}`.

Define the **responsibility invalidation closure**

`A(C) = {r in R : D(r) intersects C}`.

Equivalently, `A(C)` is the responsibility-node portion of forward reachability from `C` when graph edges point from prerequisite to dependent.

The safety interpretation is worst-case and load-bearing: every declared dependency edge is allowed to matter to correctness. If the system possesses a proof that an edge is irrelevant to a particular responsibility, that edge should not be in the frozen dependency relation for that responsibility.

## Theorem 1 — exact closure characterization

A responsibility is in `A(C)` iff at least one changed node is an ancestor of that responsibility.

This is immediate from the definitions, but it gives a directly executable graph rule: multi-hop dependency invalidation is reverse-proof-subgraph reachability, not global reset.

## Theorem 2 — minimal fail-closed invalidation set

Under the load-bearing-edge model, every sound policy that must remain safe for **all** validity assignments consistent with the declared graph must invalidate every responsibility in `A(C)`. Therefore `A(C)` is the unique inclusion-minimal fail-closed invalidation set.

### Proof

Take `r in A(C)`. Then some `c in C` lies on a declared dependency path to `r`. Because declared edges are permitted to be load-bearing, there is an admissible assignment in which the validity of each node on that path depends on its predecessor and the changed value at `c` flips the validity condition reaching `r`. A policy that reuses `r` without revalidation in that world is unsound. Hence every universally sound policy contains `A(C)`.

Conversely, invalidating all of `A(C)` and retaining only responsibilities whose dependency closures are disjoint from `C` is fail-closed with respect to this change set: no retained responsibility has a declared dependency path from an invalidated node. Thus `A(C)` itself is sound under the declared dependency model. It is therefore the unique inclusion-minimal sound set. QED.

## Corollary 2.1 — exact cost floor for revalidation

If invalidating responsibility `r` incurs nonnegative revalidation cost `w(r)`, then every universally sound policy has cost at least

`sum_{r in A(C)} w(r)`.

The closure policy attains this lower bound when revalidations are separable at the responsibility level. Shared proof-subgraph computation may lower realized execution cost, but cannot remove a responsibility from the mandatory semantic invalidation set without additional proof.

## Corollary 2.2 — full reset is conservative, often non-minimal

Always invalidating all `R` is sound but is strictly more conservative whenever `A(C)` is a proper subset of `R`. The possible efficiency gain of responsibility-carrying state is therefore governed by graph locality: how much smaller `A(C)` is than `R`, not by certificate syntax alone.

## Corollary 2.3 — certificate sufficiency is conditional on dependency completeness

If a true load-bearing dependency is absent from the graph/certificate, the computed closure can omit a responsibility that should be invalidated. Therefore the theorem proves minimality **relative to the declared complete dependency relation**. It does not prove that a particular externally authored certificate is complete.

This is the exact place where independent gold remains necessary.

## Relation to the current ORION-23 evidence

The paper already has strong controlled finite evidence: authenticated RCS rejects scheduled certificate corruptions with zero gold-scored unsafe reuse in P13B; the composed P13C world rejects 2,457 scheduled corruptions over 12,288 episodes, records zero unnecessary reopens on 9,831 valid-certificate episodes, and costs 0.539x always-raw in that registered world.

Those measurements are preserved. This theorem supplies the missing structural statement behind an affected-proof-subgraph successor: once a dependency relation is accepted as complete, forward reachability from changed support is not merely a heuristic but the unique minimal fail-closed responsibility invalidation set.

## Successor design implication

A real-system successor should separately test two propositions:

1. **graph fidelity** — external gold verifies that the declared dependency relation contains all load-bearing dependencies; and
2. **closure efficiency** — on that externally grounded graph, measured `A(C)` is materially smaller than full reset while correctness is preserved.

Conflating these would allow a sparse but incomplete graph to look efficient.

## Claim boundary

Earned deductive claim:

> Relative to a complete declared dependency DAG, the responsibilities reachable from changed support are exactly the unique minimal fail-closed invalidation set.

Not earned:

- completeness of historical or future real-world certificates;
- external lifecycle gold;
- social or institutional responsibility;
- real-agent superiority.

`scientific_authority_delta: NONE`