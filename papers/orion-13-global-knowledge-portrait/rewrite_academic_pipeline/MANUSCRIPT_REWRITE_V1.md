# Scientific Identity as an Authorization Relation for Structured Knowledge Integration

## Abstract

Structured scientific records can be representation-compatible without being scientifically identical. Schema alignment, canonical names, provenance and matching coordinates can establish that two records *could* be compared or merged; they do not by themselves establish that the records denote the same scientific object for the decision currently being made. We study this distinction through a scoped scientific-identity authorization relation layered above representational compatibility.

The evidence comprises two separately frozen lanes. In a disjoint 32-case public-reference holdout of already-structured scientific projections, a typed mapping calculus produces zero false merges compared with 0.1875 for flat predicate canonicalization, a paired difference of -0.1875 with a 95% interval from -0.34375 to -0.0625. The false-split difference relative to an exact-coordinate conservative control is zero, satisfying the predeclared confirmatory rule. In a separate prospectively frozen 400-case exact-contract study spanning heterogeneous scientific artifact domains, the scientific-identity rule is correct on all 400 integration decisions. A strong semantic product carrying structured construct, measurement, context, provenance and missingness information is correct on 250 of 400, while canonical matching is correct on 50 of 400. The paired difference against the strong product is 0.375, with a domain-stratified bootstrap 95% interval of 0.3275 to 0.4225. An information-equivalent typed product carrying the same identity relation also reaches 400/400 with no mismatches.

The ideal-product tie is essential to the interpretation: the result is not an expressivity claim for one architecture. It is a target-bound authorization result. Explicit scientific identity prevents false integrations in the registered structured contracts while preserving every clean integration, and any implementation that represents the same relation should make the same decisions. Raw-text extraction, end-to-end knowledge-portrait construction, downstream answer quality and deployed ontology-engine generality remain separate unexecuted or insufficiently authorized studies.

## 1. Introduction

Scientific integration systems must decide when two records may be treated as one object. Existing methods offer many useful signals: canonical identifiers, schema mappings, matching units, compatible measurement semantics, provenance, context, missingness and graph consistency. These signals establish increasingly rich forms of compatibility.

Compatibility is not yet identity. Two records can be well aligned syntactically and semantically while referring to measurements whose scientific roles differ under the question being asked. Conversely, records that differ in surface representation can still denote the same scientific object once a valid bridge is supplied.

We therefore treat **scientific identity** as an authorization relation rather than a side effect of representation matching. The central question is not whether two records look similar enough to merge. It is whether the available structured evidence licenses the claim that they should be treated as the same scientific object for the target integration decision.

The paper is intentionally scoped. It evaluates already-structured scientific representations and exact integration contracts. It does not claim end-to-end raw-text extraction or broad ontology-engine superiority.

## 2. Representation compatibility and identity authority

Let two structured records carry fields describing their constructs, measurements, contexts, provenance, missingness and other integration-relevant coordinates. A representation layer can determine whether those fields are syntactically compatible or connected by declared mappings.

The scientific-identity layer asks a stronger question: do the records satisfy the target relation that licenses them to be merged for the scientific responsibility at hand?

This distinction makes three terminal states useful.

1. **Authorized identity:** the target relation is established and integration is licensed.
2. **Authorized distinction:** the available evidence establishes that the records should remain separate.
3. **Unresolved:** representation compatibility exists but the evidence needed to decide scientific identity is missing or non-identifying.

The third state prevents a matching system from turning “no detected conflict” into positive identity authority.

## 3. Public-reference mapping study

The first evidence lane evaluates the mapping calculus on a disjoint, prospectively execution-frozen holdout of 32 already-structured public-reference cases. The primary outcome distinguishes false merge from false split because the two errors have different scientific consequences.

The typed mapping rule produces no false merges. Flat predicate canonicalization produces a false-merge rate of 0.1875. The paired difference is -0.1875, with a 95% interval from -0.34375 to -0.0625.

A conservative exact-coordinate control provides the false-split comparison. The typed rule and the conservative control have identical false-split outcomes on the registered holdout, giving a difference of 0 with interval [0,0]. The predeclared confirmatory rule therefore passes: the stronger identity semantics reduce false integration without buying that reduction through additional false separation on this panel.

A secondary obstruction ablation reinforces the interpretation. Forcing compatibility where the mapping calculus records an obstruction increases false merges by 0.1875. Obstruction information is therefore decision-relevant in the registered mapping cases.

## 4. Strong semantic products are not automatically identity authority

The second evidence lane is deliberately harder. The 400-case exact-contract successor gives a strong comparator structured information about construct, measurement, context, provenance and missingness. The comparison therefore does not ask whether adding ordinary semantic structure beats a weak string matcher. It asks whether that semantic product is sufficient for the *identity decision* itself.

Across all 400 cases, the scientific-identity rule is correct on 400. The strong semantic product is correct on 250, and canonical matching is correct on 50. The difference between the identity rule and the strong product is 0.375, with a domain-stratified bootstrap 95% interval of 0.3275 to 0.4225.

The errors of the weaker products are false integrations in cases where the representation remains compatible but the target scientific-identity relation is not established. The scientific-identity rule produces no false integration and retains clean-merge coverage of one on the registered cases.

These are exact-contract results. They do not estimate performance on an open population of scientific knowledge graphs.

## 5. Information-equivalent implementation must tie

A crucial control gives a competing typed product exactly the same scientific-identity coordinates and decision relation. That product also reaches 400/400 and has no mismatches with the focal rule.

This tie rules out an architectural interpretation. The paper does not claim that scientific identity requires a centralized calculus or a proprietary state representation. If another system represents the same decision-relevant relation, the scientific prediction is equivalence.

The contribution is therefore the separation between representation compatibility and target-bound identity authority. The implementation is one realization of that distinction.

## 6. Why identity is target-bound

Scientific identity depends on what downstream claim or operation the merge is intended to support. Two measurements may be interchangeable for one aggregate analysis and non-interchangeable for a different causal, temporal or calibration-sensitive question. A record may preserve enough information for one responsibility while being under-specified for another.

The identity decision must therefore be indexed by the scientific responsibility and its load-bearing coordinates. This prevents a global “same object” flag from accumulating authority beyond the task for which it was established.

The present studies instantiate this principle in finite structured contracts. They do not prove a universal ontology of identity coordinates.

## 7. Relation to semantic integration and knowledge representation

Entity resolution, schema matching, ontology alignment, record linkage, provenance, graph constraints and semantic interoperability are established research areas. The paper does not claim canonicalization, provenance, obstruction checks or schema correspondence as new primitives.

The residual question lies one level above those mechanisms: **when does compatibility authorize scientific identity for a target integration decision?** The public-reference study shows that a typed relation can reduce false merges relative to flat canonicalization without increasing false splits on the frozen holdout. The exact-contract successor shows that even a strong semantic product can remain insufficient when the target identity relation is not represented.

This framing makes the paper suitable as a semantic-integration and scientific-knowledge methodology contribution rather than as a general claim about knowledge-graph quality.

## 8. What is deliberately outside the paper

A broader programme considers raw-text extraction, expert annotation over multiple scientific families, global-portrait construction and downstream answer quality. Those studies are scientifically interesting but are not part of the current claim surface.

The manuscript therefore does not claim:

- end-to-end raw-text integration superiority;
- improved downstream answers from generated knowledge portraits;
- expert-validated cross-domain construct completeness;
- deployed ontology or schema-engine generality;
- necessity of every semantic coordinate from zero-effect ablations.

Keeping these questions separate prevents unexecuted or under-authorized successor science from borrowing authority from the complete structured-integration result.

## 9. Reproducibility and release contract

The final submission package should bind the exact manuscript, public-reference holdout definitions, mapping outputs, 400-case successor contracts, result receipt, independent reconstruction and claim ledger to one release. The anonymous or review-facing package should use reader-facing scientific descriptions rather than development identifiers.

A current exact-subject CI and manuscript audit remain release checks. They do not require new science unless the bounded identity claim is changed.

## 10. Limitations

Both evidence lanes operate on structured inputs. The 32-case public-reference holdout is small, and the 400-case successor is an exact finite contract rather than a sample from deployed scientific integration systems. The identity relation is only as sound as the coordinates and scientific responsibility encoded by the contract; omitted load-bearing semantics can still make an apparently exact rule wrong for a richer external task.

The study also does not establish that the chosen relation is universally minimal. An information-equivalent product ties, as it should, and a different representation may encode the same scientific distinction more efficiently.

## 11. Conclusion

Scientific integration requires more than compatible representations. A merge is justified only when the available evidence authorizes identity for the scientific responsibility being served. Across a prospectively frozen public-reference holdout and a separate 400-case exact-contract study, making that relation explicit eliminates the false integrations produced by weaker matching products while preserving every registered clean merge. The exact tie with an information-equivalent implementation shows that the contribution is portable: scientific identity is the decision relation, not the software architecture that happens to encode it.
