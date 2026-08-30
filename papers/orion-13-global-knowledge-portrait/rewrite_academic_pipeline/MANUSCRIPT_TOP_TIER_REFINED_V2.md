# Scientific Identity as an Authorization Relation for Structured Knowledge Integration

## Abstract

Structured scientific records can be representation-compatible without being scientifically identical. Schema alignment, canonical names, provenance and matched coordinates may establish that records can be compared; they do not by themselves establish that the records denote the same scientific object for the target integration decision. We study **scientific identity** as an authorization relation layered above representational compatibility.

The strongest evidence is a prospectively frozen 400-case exact-contract study spanning heterogeneous scientific artifact domains. A scientific-identity rule is correct on all 400 integration decisions. A strong semantic product carrying structured construct, measurement, context, provenance and missingness information is correct on 250 of 400, while canonical matching is correct on 50 of 400. The paired difference against the strong product is 0.375 with a domain-stratified bootstrap 95% interval of 0.3275–0.4225. An information-equivalent typed product carrying the same identity relation also reaches 400/400 with no mismatches, showing that the contribution is the relation rather than a particular architecture.

A separate public-reference lane gives bounded real-structure grounding but also exposes a coverage limitation. On a disjoint 32-case confirmatory holdout, the typed mapping rule makes zero false merges whereas flat predicate canonicalization makes six. Because every case in both 32-case holdouts is predicate-equal, that baseline is an always-merge rule on these corpora; the confirmatory discordance is therefore exactly six cases (`b=6,c=0`, two-sided exact McNemar `p=0.03125`), while the initial 32-case holdout alone has four discordances (`p=0.125`). Nine of ten registered coordinates decide no case on these holdouts, and the observed discrimination collapses to the polarity distinction in context. This is a corpus-coverage limitation, not evidence that the other coordinates are globally dispensable.

The paper therefore claims a scoped target-bound identity relation for structured integration, not end-to-end raw-text superiority, universal minimal coordinates, downstream answer-quality improvement, or deployed ontology-engine generality.

## 1. Compatibility is not identity authority

Scientific integration systems combine records using canonical identifiers, schema mappings, ontology correspondences, units, context, provenance and graph constraints. These are important compatibility mechanisms. The scientific operation “merge these records as one object,” however, is a stronger commitment.

Two records can be syntactically and semantically compatible while differing on a property that matters to the scientific responsibility being served. Conversely, surface-different records can be scientifically identical once a valid bridge is available.

We therefore treat identity as a target-bound authorization relation:

> integration is licensed only when the available structured evidence establishes that the records may be treated as the same scientific object for the current responsibility.

The paper is scoped to already-structured inputs and exact integration contracts. Raw-text extraction and downstream knowledge-portrait quality remain separate studies.

## 2. Decision states

For a pair of structured scientific records, the identity layer distinguishes three terminals:

1. **authorized identity** — the target relation is established and merge is licensed;
2. **authorized distinction** — the evidence establishes that the records should remain separate;
3. **unresolved** — representation compatibility exists but the information required to decide scientific identity is missing or non-identifying.

The unresolved state is important because “no detected mismatch” is not equivalent to positive scientific identity. A matcher that cannot represent unresolved evidence should not be credited with resolving it by default.

Identity is indexed by the target responsibility. The same two records may be interchangeable for one aggregate analysis and non-interchangeable for a different temporal, causal or calibration-sensitive use.

## 3. Exact-contract study: strong semantic compatibility can remain insufficient

The primary scientific lane contains 400 prospectively frozen exact-contract cases over heterogeneous scientific artifact domains. The strong comparator is deliberately information-rich: it receives structured construct, measurement, context, provenance and missingness information.

The question is therefore not whether ordinary semantic structure beats a weak string matcher. It is whether that semantic product already contains the relation needed for the **identity decision**.

The scientific-identity rule is correct on all 400 cases. The strong semantic product is correct on 250, and canonical matching on 50. The difference between identity-aware and strong semantic decisions is 0.375 with a domain-stratified 95% bootstrap interval of 0.3275 to 0.4225.

The registered errors of the weaker products are false integrations where representation compatibility remains high but target scientific identity is not established. The identity-aware rule preserves all registered clean integrations.

These are exact finite contracts, not an estimated error rate for open-world scientific knowledge graphs.

## 4. Information-equivalent implementations tie

An ideal competing product is supplied with exactly the same target-defining scientific-identity coordinates and terminal relation. It reaches 400/400 with no decision mismatches.

This tie is a required control. It rules out the interpretation that one centralized calculus has unique expressive power. Any system that represents the same decision-relevant relation should recover the same finite target map.

The scientific residual is therefore portable: **compatibility signals require an explicit target identity relation before they authorize a merge**.

## 5. Public-reference grounding and the baseline limitation

A second lane evaluates already-structured public-reference projections on two 32-case holdouts. The confirmatory result initially looks like a conventional method-versus-baseline comparison: the typed rule makes zero false merges and flat predicate canonicalization makes six, a false-merge-rate difference of -0.1875.

A hostile baseline audit changes how this should be read. Every case in each holdout is predicate-equal. The flat predicate rule therefore predicts “merge” for every case. Its 0.1875 false-merge rate is exactly the six-of-32 minority rate in the confirmatory set; any always-merge rule reproduces that headline number.

The paired evidence is correspondingly small and exact. On the confirmatory holdout there are six discordant cases, all favoring the typed rule (`b=6,c=0`), giving a two-sided exact McNemar `p=0.03125`. On the initial holdout there are four discordances (`b=4,c=0`, `p=0.125`). If the two sets are displayed together, the pooled ten-discordance calculation should be labelled pooled and should not replace the per-holdout results.

The correct scientific use of this lane is therefore **grounding and obstruction illustration**, not broad superiority over competitive entity-resolution systems.

## 6. The holdouts exercise only a narrow coordinate slice

A second hostile audit asks which registered identity coordinates actually determine these 64 public-reference cases. Nine of ten coordinates decide no case in either holdout. Every discriminating case is resolved at the polarity coordinate; predicate and modality provide context but do not create additional decision diversity.

A reduced rule using predicate, modality and polarity reproduces the full mapping decisions on all 64 cases.

This does **not** show that the other registered coordinates are globally unnecessary. It shows that these particular corpora do not exercise them. The paper therefore treats the public-reference study as narrow coverage and relies on the separately designed 400-case exact-contract lane for broader structured-identity discrimination.

Zero-effect coordinates on one benchmark are a reason to narrow the benchmark claim, not a license to delete scientific dimensions from the general model.

## 7. Obstruction and unresolved identity

The identity relation can refuse a merge even when conventional compatibility signals are favorable. In the public-reference lane, forcing compatibility where the mapping calculus records an obstruction increases false merges on the registered cases.

This supports a simple semantic point: a compatibility layer should be able to pass an object upward without simultaneously asserting that the object is scientifically identical to another. The identity layer may then authorize, distinguish or remain unresolved according to the target responsibility.

The paper does not claim obstruction checks, provenance, schema matching or cycle consistency as individually new mechanisms.

## 8. Relation to semantic integration

Entity resolution, record linkage, ontology alignment, schema matching, provenance and semantic interoperability are established research areas. They own the general problem of making heterogeneous representations comparable.

The residual question is one level higher: **when do those compatibility relations authorize scientific identity for a target operation?** The exact-contract study shows that a strong semantic product can remain target-insufficient; the information-equivalent tie shows that the missing object is a relation, not architecture.

This positions the paper as a scientific-knowledge integration and semantic-governance contribution rather than a claim of a universally superior matching engine.

## 9. Explicitly excluded claims

The current manuscript does not claim:

- end-to-end raw-text extraction superiority;
- expert-validated completeness across an eight-family scientific atlas;
- improved downstream answers from generated knowledge portraits;
- deployed ontology/schema-engine generality;
- necessity or dispensability of every semantic coordinate;
- a population error rate inferred from the 32-case holdouts.

Those questions require separate evidence and do not inherit authority from the structured identity result.

## 10. Reproducibility and release

The final scoped package should bind the 400-case exact contracts, target tables, strong-product and information-equivalent controls, public-reference holdout definitions, paired decisions, baseline audit, independent reconstruction and claim ledger to one versioned release.

For the public-reference lane, tables should expose the number of discordant cases and make baseline degeneracy visible rather than reporting only a rate difference. The manuscript and figures should also state that the holdouts exercise a narrow coordinate slice.

Exact-subject repository CI and the manuscript audit remain release checks. They do not require new science unless the scoped claim is changed.

## 11. Limitations

The primary 400-case study is a designed finite contract, not a sample from deployed knowledge graphs. The public-reference holdouts are small and structurally narrow. The identity relation is only as sound as the target responsibility and load-bearing coordinates represented by the contract; omitted semantics can invalidate an apparently exact integration rule in a richer setting.

The information-equivalent tie also means the paper should not claim a proprietary architectural advantage. A different representation may encode the same identity relation more efficiently or naturally.

## 12. Conclusion

Scientific knowledge integration requires a distinction between compatibility and identity authority. In a 400-case exact-contract study, a strong semantic product remains insufficient for the target identity decision while an information-equivalent product ties the identity-aware rule exactly. A public-reference holdout provides real-structure grounding but also reveals its own limitations: the flat baseline is always-merge on those corpora and only a narrow coordinate slice is exercised. The resulting paper is intentionally scoped. Its contribution is the target-bound identity relation and the discipline of refusing to turn representation compatibility into scientific sameness without an explicit warrant.