# Interaction Tax for Product Certificates — R10

Date: 2026-08-26

Status: abstract shortening-system theorem. Maximum independent set, vertex cover, weighted variants, and bounded-treewidth algorithms are classical donor-owned graph theory. The paper-specific role is to quantify exactly how cross-component shortening moves destroy an otherwise additive certificate budget.

## 1. From independent component terminals to a cross-move graph

Suppose `r` independently realized components each contribute one terminal unit to a product witness. Without cross-component moves, the product terminal support is `r`.

Let `V={1,...,r}` index these terminal units. Let a simple graph `H=(V,E)` encode **reducing cross moves**:

- a state is a subset `S subseteq V` of surviving component-terminal units;
- if `{u,v} in E` and `u,v in S`, the production language contains a sound cross move that strictly reduces support and removes the simultaneous survival of `u` and `v`;
- no other cross move is present in this reduced terminal-level model.

The exact lower-level semantics of the cross move belong to the production realization. This theorem studies the induced shortening system once the sound move registry has been proved.

A state is terminal exactly when it contains no graph edge.

## 2. Exact interaction budget

### Theorem AB-R10.4 — graph interaction tax

The maximum terminal support of the cross-coupled product is

`beta(H)=alpha(H)`,

the independence number of the interaction graph.

Therefore the amount by which cross moves destroy the naive additive product budget is

`tax(H)=|V|-alpha(H)=tau(H)`,

the minimum vertex-cover number.

### Proof

A state `S` is terminal iff no edge of `H` has both endpoints in `S`, which is exactly the definition of an independent set. Hence the largest terminal state has size `alpha(H)`. The complement of an independent set is a vertex cover and vice versa, giving Gallai's identity `alpha(H)+tau(H)=|V|`. ∎

This gives an exact quantitative refinement of the earlier statement “cross moves can break product additivity.”

## 3. Weighted interaction tax

Let terminal unit `v` carry nonnegative certificate weight `w_v`. Define the product certificate weight as the sum of surviving unit weights.

### Corollary AB-R10.5

The maximum terminal certificate weight equals maximum-weight independent set:

`beta_w(H)=max_{S independent} sum_{v in S} w_v`.

Equivalently, the destroyed certificate weight is the minimum-weight vertex-cover value when cover weights use the same nonnegative `w_v`.

Thus cross interactions can preferentially destroy expensive or cheap certificate components depending on graph structure, rather than merely reducing component count.

## 4. Computational boundary

### Corollary AB-R10.6

Computing the exact product certificate budget in this pairwise cross-move model is NP-hard, already for unweighted terminal units, because it is maximum independent set.

This is not presented as new graph-complexity theory. Its interpretation is:

> even when every component certificate is trivial and locally realized, the exact global certificate budget can become computationally hard solely because of the cross-move interaction registry.

### Tractable interaction classes

Classical graph algorithms immediately give useful production corollaries once the interaction graph is verified:

- forests: exact linear-time dynamic programming;
- bipartite graphs: `alpha(H)=|V|-tau(H)` with `tau(H)` equal to maximum matching size by König's theorem;
- bounded-treewidth graphs: exact dynamic programming exponential only in treewidth;
- disconnected interaction graphs: budgets add across connected components.

These algorithms/theorems are donor-owned. The framework contribution is the reduction from a verified cross-move registry to the appropriate graph quantity.

## 5. Hypergraph generalization

If a sound cross move requires an entire set `e subseteq V` of component terminals to coexist before it can reduce support, let `mathcal H` be the hypergraph of minimal reducing cross-move supports.

A state is terminal exactly when it contains no hyperedge. Hence the exact terminal budget is the hypergraph independence number

`alpha(mathcal H)`,

and the interaction tax is the minimum transversal/vertex-cover number

`|V|-alpha(mathcal H)`

in the unweighted case.

Again, the hypergraph must consist of **proved minimal reducing interactions**. Merely observing that two move schemas share state does not create a hyperedge.

## 6. Interaction graphs versus schema-interaction graphs

The manuscript uses two different graphs that must not be conflated.

1. **Schema-interaction graph:** vertices are move schemas; edges indicate possible overlap/shared auxiliaries/precondition-effect dependence and identify which schemas require joint critical analysis.
2. **Terminal interaction graph:** vertices are realized component terminal units; edges/hyperedges encode proved reducing combinations and determine the surviving global certificate budget.

The first is an audit dependency graph. The second is a quantitative certificate object.

A paper or tool should only construct the terminal interaction graph after the relevant schema interactions have been semantically resolved.

## 7. Production experiment

A strong equality-saturation/parity-synthesis experiment should report both objects.

For a nested real rewrite registry:

1. generate component terminal certificates under the weak/local language;
2. identify which combinations are collapsed by full-registry cross moves;
3. build the terminal interaction graph/hypergraph;
4. compare predicted `alpha`-budget with independently enumerated full-language terminal states;
5. measure the resulting candidate/search reduction;
6. report whether a sparse/low-treewidth interaction structure makes global certification tractable.

This experiment would make the interaction theorem scientifically useful. Without it, the graph correspondence is an exact abstraction theorem, not evidence about production compilers.

## 8. Publication boundary

The paper must credit independent set, vertex cover, König's theorem, treewidth algorithms, and hypergraph transversals as classical.

The residual integrated A+B contribution is the chain:

- component proof-language certificates have explicit ownership;
- complete-move realization determines whether they survive production;
- reducing cross moves induce an interaction object;
- that object exactly quantifies the nonadditivity of the global certificate;
- a real rewrite registry can then be audited and priced rather than assumed modular.
