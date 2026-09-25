# Conservative Revalidation under Scientific Change: Certificate Lifting and Dependency-Graph Quality

## Abstract

Scientific and AI workflows increasingly reuse execution certificates, provenance records, typed effects, authorization receipts, and reproducible traces across multiple stages of reasoning. Two distinct errors arise after change. A lower-level certificate can remain natively valid while no longer supporting the current scientific claim; and a dependency graph can be conservative or incomplete, changing the amount and safety of revalidation even when the revalidation rule itself is correct.

We develop a bounded theory of **conservative scientific revalidation** that separates these layers. First, native certificates keep their own verdicts, while scientific standing is carried forward only when claim-specific lift conditions required by the new state remain satisfied. In a registered five-coordinate finite model, revalidating the complete affected set of scientific lift coordinates is sufficient to restore the lifted conclusion, while every proper subset is unsound for at least one admissible state. The donor-independent checker covers all 31 nonempty affected-coordinate patterns and all 211 strict-subset failures; repeated donor-family realizations are treated as implementation coverage rather than independent evidence. Second, for dependency-closed revalidation on a true DAG \(G^*\), we prove an exact graph-quality law. Over-approximating \(G^*\) is always sound and costs exactly the additional reachable nodes; under-approximating \(G^*\) is unsound exactly for nodes whose every true path from the change set uses a missing edge; and with nonnegative obligation weights, no sound revalidation set can beat the affected closure itself. Exhaustive verification over all DAGs on three to five nodes finds no violations and includes non-degenerate planted controls.

A separate commutation result shows that fully separated deterministic mechanics can yield the same current scientific projection under either execution order even though their audit histories differ by swaps of independent events. Information-equivalent implementations tie extensionally. The contribution is therefore a set of portable repair laws for selective revalidation, not a universal ontology, deployed cost-saving claim, or proof that any particular real dependency extractor recovers the true semantic graph.

## 1. Introduction

Scientific workflows preserve many locally valid objects across time. A program can still have executed exactly as recorded. A theorem prover can still accept the same proof object. A data artifact can retain its provenance. An authorization receipt can still describe a valid past action. Yet the scientific conclusion that once depended on those objects may cease to follow after the question, measurement meaning, evidence standard, or inferential obligation changes.

A second problem appears when revalidation is dependency-directed. Even with a sound closure rule, the result depends on the quality of the dependency graph. Conservative edges may cause extra work. Missing edges can silently retain artifacts whose validity should have been reopened. A weighting scheme cannot repair a graph that omits a load-bearing dependency.

These problems are related but distinct. The first asks **which scientific bridge must be reopened after semantic change**. The second asks **which artifacts must be revisited after structural change, given an imperfect dependency graph**. We treat both as conservative revalidation problems and keep their authorities separate.

### 1.1 Main contributions and assumptions

The paper makes three bounded contributions.

1. **Claim-specific certificate lifting.** Preserve native certificate validity while reopening exactly the scientific lift coordinates affected by a change. In the registered five-coordinate model, complete affected-set repair is sufficient and every strict subset is unsound somewhere.
2. **Exact dependency-graph quality law.** For dependency-closed revalidation, graph inclusion orders cost and safety in opposite directions: over-approximation is sound with exact localized extra work; under-approximation fails exactly on missing-path nodes; the true affected closure is cost-minimal among sound sets for every nonnegative weighting.
3. **Order-independence of fully separated mechanics.** Under disjoint writes, reciprocal read exclusions, and scientific noninterference, independent mechanics commute on the current scientific projection while retaining order-sensitive audit histories.

The results assume the explicit finite lifting model for the first theorem family and finite DAG dependency semantics for the second. Real software dependency extraction, stochastic systems, and deployed scientific workflows require additional evidence and are not inferred from the formal results.

## 2. Native validity and scientific lifting

A lower-level certificate is associated with its own object identity, premises, and validity predicate. Scientific use adds another relation: the certificate is being used to support a particular claim under a particular scientific interpretation.

The registered lifting model represents five forms of continuity relevant to this bridge: exact claim/content identity, measurement semantics, evidence semantics, inferential obligation, and scientific epoch. These coordinates are a finite study model, not a proposed universal ontology.

If none of the required scientific coordinates changes, a valid native certificate can remain lifted. If some coordinates change, the native certificate need not be revoked. Instead, the scientific lift becomes open on exactly the affected bridge coordinates.

This yields a non-laundering principle:

> Additional lower-level certificates cannot discharge a missing scientific lift condition unless an explicit rule connects their native judgments to the changed scientific obligation.

The principle is conservative toward existing assurance systems. It does not weaken what they certify; it prevents their verdicts from silently acquiring a broader scientific meaning.

## 3. Selective repair law in the registered lifting model

Let \(A\) be the set of scientific lift coordinates changed by a transition. Assume that native validity survives on unchanged premises and unaffected lift coordinates remain valid.

### 3.1 Sufficiency

Revalidating every coordinate in \(A\) restores the lifted scientific conclusion.

### 3.2 Necessity within the registered model

For every proper subset \(B\subset A\), there exists an admissible model state in which a coordinate in \(A\setminus B\) is precisely the missing condition that breaks the lift. Therefore no strict subset of the affected set is sound for every registered state.

With five coordinates, there are 31 nonempty affected sets. Enumerating every strict subset gives 211 incomplete repair choices. The donor-independent checker verifies all 31 complete repairs and rejects all 211 strict-subset alternatives through explicit countermodels.

Historical implementations realize the same patterns inside five donor families, producing 155 complete successes and 1,055 strict-subset failures. Those counts are repeated realizations of the same scientific configurations and are not presented as 1,210 independent observations.

## 4. Product assurance cannot create a missing scientific bridge

A natural alternative is that the apparent need for a scientific lifting layer disappears once enough lower-level assurance mechanisms are combined. We therefore construct product states in which provenance, execution, authorization, and related native certificates are simultaneously valid.

Thirty-one distinct non-laundering countermodels show that product accumulation alone does not restore a scientific bridge whose changed obligation is absent from the representation. The lower-level product can remain fully valid in its native semantics while the current scientific conclusion is unsupported.

This is not a claim that product assurance is weak. The missing object is different: a relation from locally valid evidence to the present claim.

## 5. Dependency-closed revalidation

We next consider structural change. Let \(G\) be a finite DAG, \(\Delta\) a set of changed nodes, and

\[
A_G(\Delta)=\{v: v\text{ is reachable from some node of }\Delta\text{ in }G\},
\]

including \(\Delta\). A revalidation policy selects a set \(R\). It is sound when every artifact whose validity could change belongs to \(R\). Write \(G^*\) for the true semantic dependency graph.

A previously established separation-witness result gives the base closure law: \(A_{G^*}(\Delta)\) is sound, and every proper subset is unsound under the declared dependency semantics. The remaining question is how graph approximation changes safety and cost.

## 6. Exact graph-quality law

### Theorem 1 — monotonicity

If \(G\subseteq G'\), then

\[
A_G(\Delta)\subseteq A_{G'}(\Delta)
\]

for every \(\Delta\). Every path in \(G\) is also a path in \(G'\).

### Theorem 2 — over-approximation is sound and its price is exact

If \(G'\supseteq G^*\), revalidating \(A_{G'}(\Delta)\) is sound. The extra work is exactly

\[
|A_{G'}(\Delta)\setminus A_{G^*}(\Delta)|.
\]

Every extra node is reachable in \(G'\) from the head of at least one conservative edge in \(G'\setminus G^*\). Conservative edges therefore cost only the additional reachability they create; they do not impose an unspecified global penalty.

### Theorem 3 — under-approximation fails exactly on missing-path nodes

If \(G''\subseteq G^*\), a node \(v\) is wrongly retained if and only if

\[
v\in A_{G^*}(\Delta)\quad\text{and}\quad v\notin A_{G''}(\Delta).
\]

Equivalently, every \(G^*\)-path from \(\Delta\) to \(v\) uses at least one edge absent from \(G''\). A missing edge that is bypassed by another complete path creates no error; a missing edge that lies on every true path to a node does.

### Theorem 4 — nonnegative weights do not move the optimum

For any nonnegative weighting \(w\) of revalidation obligations, the minimum-weight sound set is \(A_{G^*}(\Delta)\) itself.

Because every proper subset of the affected closure is unsound, every sound set contains the closure. Nonnegative weights therefore cannot make a larger sound set cheaper. Once soundness is noncompensatory, cost optimization has no remaining freedom inside the exact graph; achievable savings come from graph quality rather than from priority weights.

### Corollary — quality ladder

Graph inclusion orders cost and safety in opposite directions. Enlarging beyond \(G^*\) buys only additional work. Shrinking below \(G^*\) may save work but forfeits soundness exactly according to Theorem 3. The true graph is the unique point that is simultaneously exact in safety and closure cost under the declared semantics.

## 7. Exhaustive verification and hostile controls

The graph-quality laws are analytic. A prospectively frozen exhaustive verifier independently exercises them over all DAGs on three to five nodes, every change set, and both over- and under-approximations.

No violations are found for monotonicity, over-approximation soundness and localization, under-approximation set equality, or weighted cost minimality. The coverage is intentionally non-degenerate: 119,038 strict over-approximations have positive extra work; 310,002 strict under-approximations have nonempty wrongly-retained sets; 559,233 comparisons test exact set equality for the under-approximation law; all 310,002 planted unsound cases trigger the same soundness predicate used by the main checker; and all 32,760 registered zero-weighting controls correctly do not alarm.

These enumerations validate the implementation and boundary cases. General authority comes from the proofs, not from extrapolating the finite enumeration.

## 8. Information-equivalent implementations tie

For the lifting layer, an ideal competing product enriched with the same scientific coordinates and lift predicate agrees on every registered state. For dependency revalidation, any implementation given the same exact graph \(G^*\), change set, and closure semantics computes the same minimal safe affected set.

These ties are required controls. The paper does not claim a centralized architecture or proprietary representation is necessary. The contribution lies in the semantic repair laws and the information they require.

## 9. Commutation of independent scientific mechanics

Scientific systems also execute multiple mechanics whose order can vary. A naïve commutation theorem might require the entire state, including ordered audit history, to be identical after swapping independent actions. That is too strong because a correct audit log should preserve chronology.

We instead distinguish the current scientific projection from history. For deterministic admissible mechanics with disjoint writes, reciprocal read exclusions, and full scientific noninterference, executing the mechanics in either order produces the same current scientific projection. Histories are equivalent only up to swaps of adjacent independent events.

A serialized kernel derivation replays this theorem from primitive rules. A separate solver check refutes the negation under the translated assumptions. Mutation controls are informative: removing either cross-read exclusion admits a countermodel, showing that the theorem depends on genuine separation rather than notation.

## 10. Real-system boundary

The formal graph-quality law does **not** establish that a particular extractor recovers \(G^*\). A Python import graph, for example, is naturally an over-approximation of semantic dependency and therefore falls under Theorem 2: closure over it can be conservative and sound while still doing extra work. It cannot certify that no semantically relevant dependency is missing.

Historical real-system comparisons were accessed before the graph-quality theory was frozen. They are therefore treated only as labelled consistency observations and contribute no prospective authority to the theorem or to a deployed performance claim.

A broader real-system result requires authoritative dependency semantics, native required-revalidation gold, and independently checked extraction. Until then, no claim is made about deployed cost savings or exactness of real dependency graphs.

## 11. Relation to prior assurance and incremental computation

Proof-carrying actions, certified execution, workflow provenance, authorization, effect systems, truth maintenance, dependency-directed recomputation, build systems, incremental testing, and selective invalidation are established mechanisms. They solve important native problems and are treated as donor infrastructure here.

The residual contribution lies in two exact boundaries above those donors: claim-specific scientific lifting after semantic change, and graph-quality laws that separate conservative over-revalidation from unsafe omission under structural approximation.

## 12. Limitations

The five-coordinate lifting model is finite and deliberately explicit. The current evidence does not prove that those coordinates are universally necessary, sufficient, independent, or minimal. Real systems may require different scientific state or conservatively reopen more than the finite model predicts.

The graph results assume finite DAG dependency semantics and a well-defined true graph \(G^*\). Cycles, probabilistic dependencies, dynamic runtime dependencies, and uncertain ground truth require additional theory. Most importantly, the theorem does not make a non-authoritative extractor authoritative.

The independent implementation and fresh-kernel replay are same-programme replications, not external custodianship. The manuscript does not establish wall-clock savings, reduced scientific error, or superior deployed-agent performance.

## 13. Reproducibility and availability

The release package should include the formal lifting definitions, all 31 affected-set cases, strict-subset countermodels, independent reconstruction, graph-quality proofs, exhaustive verifier, planted controls, commutation kernel proof, solver check, and mutation controls. Repeated donor loops should be documented as implementation coverage while the manuscript reports distinct scientific configurations.

Reviewer-facing prose should describe the scientific semantics rather than repository-internal module or test names. Any future real-system campaign must remain a separate evidence identity and must not overwrite the bounded formal terminal.

## 14. Conclusion

Scientific change should not force a choice between discarding every prior certificate and carrying every certificate forward unchanged. Conservative revalidation preserves native assurance while reopening the scientific bridge or dependency closure that change actually makes uncertain. In the registered lifting model, complete affected-set repair is sufficient and every strict subset is unsound. In dependency graphs, over-approximation is safely conservative with exactly localized extra work, under-approximation fails exactly on missing-path nodes, and nonnegative weighting cannot beat the true affected closure. Together these results define a bounded formal mechanics of selective scientific revalidation without converting formal correctness into an unsupported deployed-system claim.