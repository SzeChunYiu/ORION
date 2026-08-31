#!/usr/bin/env python3
"""Atomic, release-bound claim inventory for the ORION-03 manuscript.

This module is deliberately data-only apart from small construction helpers.  It
is imported by both the independent-review candidate builder and the final
research-integrity ledger builder so that the reviewed inventory cannot silently
diverge from the released ledger.
"""

from __future__ import annotations

from typing import Any


def _claim(
    claim_id: str,
    location: str,
    text: str,
    claim_class: str,
    status: str,
    warrant_type: str,
    pointer: str | None = None,
    *,
    sources: tuple[str, ...] = (),
    risk: str = "normal",
    importance: str = "supporting",
    verification_method: str | None = None,
    support_status: str = "ENTAILS",
    scope_match: str = "MATCH",
    boundary: str = "Bounded to the exact proposition and stated manuscript scope.",
    dependencies: str = "The definitions, qualifiers, and evidence boundary stated at the cited location.",
    cross_sections: tuple[str, ...] = (),
) -> dict[str, Any]:
    if verification_method is None:
        verification_method = {
            "definition": "deterministic_derivation",
            "proof": "deterministic_derivation",
            "author_data": "deterministic_recompute",
            "analysis": "deterministic_recompute",
            "method_record": "authoritative_project_record",
            "literature": "independent_model_with_retrieved_source",
            "source": "independent_model_with_retrieved_source",
            "not_applicable": "human_review",
        }[warrant_type]
    return {
        "claim_id": claim_id,
        "location": location,
        "text": text,
        "claim_class": claim_class,
        "risk": risk,
        "importance": importance,
        "qualifiers_and_scope": boundary,
        "dependencies_and_hidden_premises": dependencies,
        "warrant_type": warrant_type,
        "artifact_pointer": pointer,
        "source_keys": list(sources),
        "verification_method": verification_method,
        "support_status": support_status,
        "scope_match": scope_match,
        "boundary_or_uncertainty": boundary,
        "cross_section_locations": list(cross_sections),
        "target_release_status": status,
        "counterevidence_search_required": risk == "high"
        or claim_class in {
            "causal",
            "clinical_or_safety",
            "novelty_or_priority",
            "quantitative_result",
            "legal_or_policy",
            "availability_or_compliance",
        },
        "release_action": "retain exactly as bounded" if status != "NOT_APPLICABLE" else "retain as justified not-applicable metadata",
    }


C: list[dict[str, Any]] = []


def add(*args: Any, **kwargs: Any) -> None:
    C.append(_claim(*args, **kwargs))


# ---------------------------------------------------------------------------
# Title, author metadata, abstract, and keywords
# ---------------------------------------------------------------------------

add("C_META_001", "Title", "The paper concerns typed evidence licenses for fail-closed nonpromotion.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#title", importance="headline", risk="high", boundary="The title is a scoped description of the declared finite-system contribution, not a generic provenance or security claim.")
add("C_META_002", "Title", "The paper's formal domain is finite rule systems.", "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#title", importance="headline")
add("C_META_003", "Short title", "The short title consistently identifies typed evidence licenses and nonpromotion.", "availability_or_compliance", "VERIFIED", "method_record", "MANUSCRIPT.md#short-title", risk="high")
add("C_META_004", "Author metadata", "Sze Chun Yiu is the sole named author.", "availability_or_compliance", "VERIFIED", "method_record", "review_records/AUTHOR_CONFIRMATION_V1.json", risk="high")
add("C_META_005", "Author metadata", "The author's stated affiliation is Independent Researcher.", "availability_or_compliance", "VERIFIED", "method_record", "review_records/AUTHOR_CONFIRMATION_V1.json", risk="high")
add("C_META_006", "Author metadata", "The corresponding email is sze-chun.yiu@fysik.su.se.", "availability_or_compliance", "VERIFIED", "method_record", "review_records/AUTHOR_CONFIRMATION_V1.json", risk="high")
add("C_META_007", "Keywords", "The manuscript supplies exactly six keywords: automated reasoning, evidence provenance, belief revision, fixed-point semantics, nonpromotion, and reproducible evaluation.", "availability_or_compliance", "VERIFIED", "method_record", "review_records/VENUE_REQUIREMENTS_V1.md", risk="high")
add("C_META_008", "Bibliography metadata", "The canonical bibliography input is references.bib.", "availability_or_compliance", "VERIFIED", "method_record", "submission/source/references.bib", risk="high")

abstract_claims = [
    ("001", "Derivability alone need not determine the evidential status assigned to a scientific claim.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Introduction", "headline"),
    ("002", "A conclusion can remain reachable through another route after one support route is invalidated while losing a license attached to the invalidated route.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-2", "headline"),
    ("003", "The formalization is bounded to finite positive conjunctive rule systems.", "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#Finite-typed-authority-system", "headline"),
    ("004", "Independent seeds carry subsets of a finite evidence-license universe.", "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#Claims-licenses-seeds-and-capped-rules", "major"),
    ("005", "Each rule transmits only licenses shared by every premise and admitted by the rule's cap.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Claims-licenses-seeds-and-capped-rules", "headline"),
    ("006", "Directly refuted claims are assigned the empty label by the declared operator.", "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#Finite-typed-authority-system", "major"),
    ("007", "The declared monotone operator has a finite least fixed point.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-1", "headline"),
    ("008", "License membership has an equivalent finite typed proof-tree semantics.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-2", "headline"),
    ("009", "Unsupported cycles remain empty under the declared least-fixed-point semantics.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Unsupported-cycles-and-license-conservation", "major"),
    ("010", "Adding direct refutations cannot add licenses.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-4", "headline"),
    ("011", "Retraction removes exactly the claim-license pairs whose typed proof trees no longer survive, relative to the declared algebra.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Corollary-5", "headline"),
    ("012", "A deterministic evaluator implements the declared algebra.", "method", "VERIFIED", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py", "major"),
    ("013", "The evaluator exercises three committed scientific-record cases.", "method", "VERIFIED", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/examples", "major"),
    ("014", "The OpenSSL instantiation is separately frozen at OpenSSL 3.6.4.", "method", "VERIFIED", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/SOURCE_BINDING_V2.json", "major"),
    ("015", "Flat trust-store union produced 46 hybrid authorizations among 1,962 frozen merge tasks.", "quantitative_result", "VERIFIED", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json", "headline"),
    ("016", "The origin-witness policy excludes hybrid authorizations by definition.", "formal_claim", "VERIFIED", "definition", "MANUSCRIPT.md#Native-engine-study-outcome-definitions", "headline"),
    ("017", "The origin-witness policy requires both parent-store evaluations.", "method", "VERIFIED", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json", "major"),
    ("018", "The origin-witness zero-error counts are analytic identities rather than learned performance.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C9", "headline"),
    ("019", "The contribution is a scoped evidence-license specialization with executable nonpromotion semantics.", "novelty_or_priority", "BOUNDED_INFERENCE", "literature", None, "headline"),
    ("020", "The empirical contribution is a third-party-corpus native-engine obstruction-and-cost instantiation.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json", "headline"),
    ("021", "The paper does not claim a new general provenance theory.", "novelty_or_priority", "BOUNDED_INFERENCE", "literature", None, "headline"),
    ("022", "The paper does not claim to be a security evaluation.", "clinical_or_safety", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C8", "headline"),
]
for suffix, text, cls, status, warrant, pointer, importance in abstract_claims:
    sources: tuple[str, ...] = ()
    if suffix in {"019", "021"}:
        sources = ("doyle1979", "martins1988", "agm1985", "kifer1992", "green2007", "cheney2009", "bourgaux2022", "abokhamis2022", "bonatti2011", "buneman2002", "meliou2010", "thapa2026minimal", "thapa2026stratified")
    add(f"C_ABS_{suffix}", "Abstract", text, cls, status, warrant, pointer, sources=sources, risk="high" if cls in {"quantitative_result", "novelty_or_priority", "clinical_or_safety"} else "normal", importance=importance, support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS", cross_sections=("Introduction", "Discussion", "Conclusion"))


# ---------------------------------------------------------------------------
# Introduction, related work, and contribution boundary
# ---------------------------------------------------------------------------

intro = [
    ("001", "A prospective route can be replaced by a distinct post-outcome route after the outcome is known.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Compact-nonpromotion-examples"),
    ("002", "A finite exact computation may support a bounded statement without proving a theorem-shaped generalization.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/bounded_frontier.json"),
    ("003", "An independent derivation can survive when a distinct derivation is withdrawn.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Corollary-5"),
    ("004", "Direct refutation of a conclusion fixes that conclusion's label to empty in the declared algebra.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Finite-typed-authority-system"),
    ("005", "Untyped reachability does not identify which evidence license an end-to-end derivation carries.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Typed-proof-trees"),
    ("006", "Promoting a post-outcome route to prospective status because it reaches the same conclusion is prohibited by the declared evidence typing.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/forecast_falsification.json"),
    ("007", "Combining theorem support with an unrelated bounded computation does not create an end-to-end theorem license when the common-license intersection is empty.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Compact-nonpromotion-examples"),
    ("008", "The contribution is narrower than generic fixed-point, proof-tree, provenance, minimal-support, and deletion-robustness theory.", "novelty_or_priority", "BOUNDED_INFERENCE", "literature", None),
    ("009", "Explicit rule caps make the paper's nonpromotion invariant executable.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("010", "Contribution 1 defines a finite positive conjunctive authority system with least-fixed-point powerset labels.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Finite-typed-authority-system"),
    ("011", "Contribution 2 comprises proof-tree equivalence, refutation monotonicity, and exact relative retraction.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Nonpromotion-cycles-and-retraction"),
    ("012", "Contribution 3 comprises a deterministic evaluator, schema validation, proof-tree reconstruction, and three bounded cases.", "method", "VERIFIED", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py"),
    ("013", "Contribution 4 is a frozen X.509 trust-store instantiation with hybrid authorizations and measured policy costs.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("014", "The origin-witness decision is exactly the disjunction of the parent-store decisions.", "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#Native-engine-study-outcome-definitions"),
    ("015", "The origin-witness zero unsafe-merge count is a logical consequence of its definition.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Native-engine-study-outcome-definitions"),
    ("016", "The origin-witness zero needless-rejection count is a logical consequence of its definition.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Native-engine-study-outcome-definitions"),
    ("017", "The X.509 evidence supports occurrence of the hybrid obstruction in the frozen tasks.", "empirical_result", "VERIFIED", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("018", "The X.509 evidence supports different outcomes for the fixed flat and conservative merge policies on the frozen tasks.", "empirical_result", "VERIFIED", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("019", "Retaining origin distinctions requires additional native-engine work in the measured design.", "quantitative_result", "VERIFIED", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("020", "The paper makes no attack or deployed-incident claim.", "clinical_or_safety", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C8"),
    ("021", "The paper makes no whole-PKI guarantee.", "clinical_or_safety", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C8"),
    ("022", "The paper makes no human-usability claim.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C11"),
]
for suffix, text, cls, status, warrant, pointer in intro:
    sources = ("doyle1979", "martins1988", "agm1985", "kifer1992", "green2007", "cheney2009", "bourgaux2022", "abokhamis2022", "bonatti2011", "buneman2002", "meliou2010", "thapa2026minimal", "thapa2026stratified") if suffix == "008" else ()
    add(f"C_INT_{suffix}", "Introduction", text, cls, status, warrant, pointer, sources=sources, risk="high" if cls in {"novelty_or_priority", "quantitative_result", "clinical_or_safety"} else "normal", importance="major", support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS")

literature_claims = [
    ("001", "Doyle's truth-maintenance system associates conclusions with justifications and revises beliefs when supporting assumptions change.", ("doyle1979",), "Related work: Belief maintenance and revision"),
    ("002", "Martins and Shapiro's belief-revision model retains multiple support contexts.", ("martins1988",), "Related work: Belief maintenance and revision"),
    ("003", "The AGM framework characterizes rational contraction and revision at an abstract level.", ("agm1985",), "Related work: Belief maintenance and revision"),
    ("004", "Truth maintenance and belief revision are donor traditions for dependency-sensitive update rather than novelty claimed by this paper.", ("doyle1979", "martins1988", "agm1985"), "Related work: Belief maintenance and revision"),
    ("005", "Generalized annotated logic programming studies atoms carrying values from an annotation domain.", ("kifer1992",), "Related work: Annotated logic and provenance"),
    ("006", "Provenance semirings describe composition of alternative and joint derivations.", ("green2007",), "Related work: Annotated logic and provenance"),
    ("007", "Semiring provenance has been developed for recursive Datalog.", ("bourgaux2022",), "Related work: Annotated logic and provenance"),
    ("008", "Work on Datalog over pre-semirings studies convergence.", ("abokhamis2022",), "Related work: Annotated logic and provenance"),
    ("009", "Provenance and trust annotations have been combined in linked-data reasoning.", ("bonatti2011",), "Related work: Annotated logic and provenance"),
    ("010", "The database-provenance literature distinguishes why-, how-, and where-provenance.", ("cheney2009",), "Related work: Annotated logic and provenance"),
    ("011", "Ordered annotation domains, positive fixed-point evaluation, and derivation trees are donor mathematics rather than novelty claimed here.", ("kifer1992", "green2007", "bourgaux2022", "abokhamis2022"), "Related work: Annotated logic and provenance"),
    ("012", "Deletion propagation studies how removing source facts changes query answers.", ("buneman2002",), "Related work: Annotated logic and provenance"),
    ("013", "Database causality studies which inputs explain query answers and non-answers.", ("meliou2010",), "Related work: Annotated logic and provenance"),
    ("014", "Recent recursive-Datalog work organizes minimal supports as a hypergraph used for causality, responsibility, and deletion robustness.", ("thapa2026minimal",), "Related work: Annotated logic and provenance"),
    ("015", "A stratified-negation extension identifies settings where positive support-based monotonic reasoning is insufficient.", ("thapa2026stratified",), "Related work: Annotated logic and provenance"),
    ("016", "The manuscript's retraction result is bounded to its declared algebra rather than claimed as generic causality or deletion-robustness theory.", ("buneman2002", "meliou2010", "thapa2026minimal", "thapa2026stratified"), "Related work: Annotated logic and provenance"),
    ("017", "The residual specialization interprets labels as bounded evidential permissions and enforces them with explicit caps.", ("doyle1979", "kifer1992", "green2007"), "Related work: residual specialization"),
    ("018", "Intersection across conjunctive premises enforces a common end-to-end license in the declared specialization.", (), "Related work: residual specialization"),
    ("019", "The powerset/intersection algebra is presented as one transparent policy design, not the only reasonable model of scientific authority.", ("kifer1992", "green2007"), "Related work: residual specialization"),
    ("020", "Cedar is an example of an authorization language with analyzable policy semantics and a native decision engine.", ("cutler2024",), "Related work: Authorization and domain instantiations"),
    ("021", "X.509 certificate validation has detailed path and revocation semantics.", ("rfc5280",), "Related work: Authorization and domain instantiations"),
    ("022", "Neither Cedar nor X.509 is reduced to the evidence-license calculus in this paper.", ("cutler2024", "rfc5280"), "Related work: Authorization and domain instantiations"),
    ("023", "The Cedar transfer attempt exposed no independently authored evidence-authority, license, or retraction field in the frozen fixtures.", ("cutler2024",), "Related work: Authorization and domain instantiations"),
    ("024", "The Cedar transfer attempt is retained as a null result.", ("cutler2024",), "Related work: Authorization and domain instantiations"),
    ("025", "The OpenSSL study treats native per-store decisions as fixed facts and tests origin erasure during merge.", ("openssl364", "rfc5280"), "Related work: Authorization and domain instantiations"),
    ("026", "The evidence-license layer preserves store-origin distinctions but does not replace the native X.509 engine.", ("rfc5280",), "Related work: Authorization and domain instantiations"),
]
for suffix, text, sources, location in literature_claims:
    if suffix in {"018"}:
        add(f"C_LIT_{suffix}", location, text, "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Claims-licenses-seeds-and-capped-rules", importance="supporting")
    elif suffix in {"023", "024"}:
        add(f"C_LIT_{suffix}", location, text, "empirical_result", "VERIFIED" if suffix == "023" else "BOUNDED_INFERENCE", "author_data" if suffix == "023" else "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json", sources=sources, support_status="ENTAILS" if suffix == "023" else "BOUNDS")
    elif suffix in {"025", "026"}:
        add(f"C_LIT_{suffix}", location, text, "method" if suffix == "025" else "interpretation", "VERIFIED" if suffix == "025" else "BOUNDED_INFERENCE", "method_record" if suffix == "025" else "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md", sources=sources, support_status="ENTAILS" if suffix == "025" else "BOUNDS")
    else:
        cls = "novelty_or_priority" if suffix in {"004", "011", "016", "017", "019"} else "literature_fact"
        add(f"C_LIT_{suffix}", location, text, cls, "BOUNDED_INFERENCE" if cls == "novelty_or_priority" else "VERIFIED", "literature", None, sources=sources, risk="high" if cls == "novelty_or_priority" else "normal", support_status="BOUNDS" if cls == "novelty_or_priority" else "ENTAILS")


# ---------------------------------------------------------------------------
# Formal system, proofs, examples, and formal restatements
# ---------------------------------------------------------------------------

definitions = [
    ("001", "Q is a finite set of claims."),
    ("002", "Lambda is a finite set of evidence licenses."),
    ("003", "A label is a subset of Lambda."),
    ("004", "Labels are ordered by set inclusion."),
    ("005", "The empty set is the bottom label."),
    ("006", "Union is the join operation on labels."),
    ("007", "Each claim q has an independent seed label sigma(q) contained in Lambda."),
    ("008", "A positive conjunctive rule comprises a nonempty finite antecedent set, a head claim, and a license cap."),
    ("009", "The registered rule set is finite."),
    ("010", "The declared system is the tuple (Q, Lambda, sigma, R)."),
    ("011", "Empty-body rules are represented as seeds rather than registered rules."),
    ("012", "A rule transfer intersects its cap with the labels of all antecedents."),
    ("013", "A license crosses a rule only if every premise label and the cap contain it."),
    ("014", "Disjunctive support is represented by multiple rules with a common head and union of their contributions."),
    ("015", "R is the set of directly refuted claims."),
    ("016", "F_R assigns the empty label to every directly refuted claim."),
    ("017", "For an unrefuted claim, F_R joins its seed label with all incoming rule transfers."),
    ("018", "Auth_Lambda(R) denotes bottom-up synchronous iteration of F_R to stabilization."),
    ("019", "The declared system S is held fixed when refutation sets are compared."),
    ("020", "Auth_Lambda(R) denotes consequences of a declared policy and does not assert that its seeds or caps are scientifically correct."),
]
for suffix, text in definitions:
    add(f"C_DEF_{suffix}", "Finite typed authority system: definitions", text, "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#Claims-licenses-seeds-and-capped-rules", importance="major" if suffix in {"001", "002", "008", "012", "016", "017"} else "supporting")

formal = [
    ("001", "F_R is monotone under pointwise label inclusion.", "MANUSCRIPT.md#Theorem-1", "headline"),
    ("002", "Bottom-up iteration of F_R can only add claim-license pairs.", "MANUSCRIPT.md#Theorem-1", "major"),
    ("003", "There are at most |Q||Lambda| distinct claim-license pairs.", "MANUSCRIPT.md#Theorem-1", "major"),
    ("004", "Synchronous iteration reaches a fixed point after at most |Q||Lambda| strict additions and one stability check.", "MANUSCRIPT.md#Theorem-1", "headline"),
    ("005", "Every bottom-up iterate is contained in every fixed point of F_R.", "MANUSCRIPT.md#Theorem-1", "major"),
    ("006", "The stabilized bottom-up assignment is the least fixed point of F_R.", "MANUSCRIPT.md#Theorem-1", "headline"),
    ("007", "Theorem 1 concerns the registered synchronous operator only.", "MANUSCRIPT.md#Finite-convergence", "supporting"),
    ("008", "An alternative evaluation schedule requires a separate argument that it computes the same operator.", "MANUSCRIPT.md#Finite-convergence", "supporting"),
    ("009", "A valid proof tree for (q, lambda) is finite and rooted at q.", "MANUSCRIPT.md#Typed-proof-trees", "major"),
    ("010", "No claim appearing in a valid proof tree belongs to the refutation set R.", "MANUSCRIPT.md#Typed-proof-trees", "major"),
    ("011", "Each valid proof-tree leaf carries lambda in its seed label.", "MANUSCRIPT.md#Typed-proof-trees", "major"),
    ("012", "Each valid proof-tree internal node applies a registered rule and supplies one child for every antecedent.", "MANUSCRIPT.md#Typed-proof-trees", "major"),
    ("013", "The license lambda belongs to every rule cap used by a valid proof tree.", "MANUSCRIPT.md#Typed-proof-trees", "major"),
    ("014", "If a claim-license pair first appears as a seed, a one-node valid proof tree witnesses it.", "MANUSCRIPT.md#Theorem-2", "supporting"),
    ("015", "If a claim-license pair first appears through a rule, earlier antecedent appearances yield finite child trees.", "MANUSCRIPT.md#Theorem-2", "supporting"),
    ("016", "Every fixed-point claim-license pair has a finite valid proof tree.", "MANUSCRIPT.md#Theorem-2", "headline"),
    ("017", "Every valid proof-tree leaf license is present from its seed.", "MANUSCRIPT.md#Theorem-2", "supporting"),
    ("018", "At a valid internal node, present child licenses plus a containing cap add the license to the head.", "MANUSCRIPT.md#Theorem-2", "supporting"),
    ("019", "Every finite valid proof tree yields fixed-point license membership.", "MANUSCRIPT.md#Theorem-2", "headline"),
    ("020", "Fixed-point license membership is equivalent to existence of a finite valid typed proof tree.", "MANUSCRIPT.md#Theorem-2", "headline"),
    ("021", "Proof-tree membership is memberwise: each claim-license pair has its own witness.", "MANUSCRIPT.md#Typed-proof-trees", "major"),
    ("022", "A multi-license label does not assert that one proof tree carries all licenses jointly.", "MANUSCRIPT.md#Typed-proof-trees", "major"),
    ("023", "Forgetting license and cap information yields an ordinary positive-reachability projection with nonempty seeds as Boolean facts.", "MANUSCRIPT.md#Typed-proof-trees", "major"),
    ("024", "The Boolean projection can overapproximate typed authorization because it forgets cap exclusions and common-license requirements.", "MANUSCRIPT.md#Typed-proof-trees", "headline"),
    ("025", "An unsupported two-node cycle with no licensed seed has an empty least fixed point.", "MANUSCRIPT.md#Unsupported-cycles-and-license-conservation", "major"),
    ("026", "A seeded license propagates around a cycle only through caps that admit it.", "MANUSCRIPT.md#Unsupported-cycles-and-license-conservation", "major"),
    ("027", "Every authorized license occurs in all leaves and caps of at least one valid proof tree for its conclusion.", "MANUSCRIPT.md#Corollary-3", "headline"),
    ("028", "The declared system cannot manufacture a license absent from every end-to-end derivation.", "MANUSCRIPT.md#Corollary-3", "headline"),
    ("029", "License conservation is relative to the declared tree semantics and is not a theorem about all annotation algebras.", "MANUSCRIPT.md#Corollary-3", "supporting"),
    ("030", "A theorem-only seed and a bounded-computation/external-replay seed have empty common license in the stated compact example.", "MANUSCRIPT.md#Compact-nonpromotion-examples", "major"),
    ("031", "The compact example's Boolean dependency graph can reach a proposed constant while its typed label remains empty.", "MANUSCRIPT.md#Compact-nonpromotion-examples", "major"),
    ("032", "A repair cap containing only POST_OUTCOME transmits no PROSPECTIVE license even when every premise carries both.", "MANUSCRIPT.md#Compact-nonpromotion-examples", "major"),
    ("033", "Before refutation, the two-route compact example gives q separate PROSPECTIVE and POST_OUTCOME witnesses.", "MANUSCRIPT.md#Compact-nonpromotion-examples", "major"),
    ("034", "Refuting the prospective seed p leaves only q's post-outcome route in the compact example.", "MANUSCRIPT.md#Compact-nonpromotion-examples", "major"),
    ("035", "Refuting q itself empties q regardless of its incoming routes.", "MANUSCRIPT.md#Compact-nonpromotion-examples", "major"),
    ("036", "If R is contained in R-prime, F_R-prime(x) is pointwise contained in F_R(x) for every assignment x.", "MANUSCRIPT.md#Theorem-4", "major"),
    ("037", "Bottom-up iteration preserves the containment between F_R-prime and F_R at every round.", "MANUSCRIPT.md#Theorem-4", "major"),
    ("038", "Adding direct refutations can only remove licenses from the least fixed point.", "MANUSCRIPT.md#Theorem-4", "headline"),
    ("039", "Ret_Lambda(R) is the set of claim-license pairs present before refutation and absent afterward.", "MANUSCRIPT.md#Monotone-loss-under-refutation", "major"),
    ("040", "A previously licensed pair is retracted exactly when every previously valid typed proof tree for it is destroyed by registered refutations.", "MANUSCRIPT.md#Corollary-5", "headline"),
    ("041", "A pair with at least one surviving valid typed proof tree remains licensed.", "MANUSCRIPT.md#Corollary-5", "headline"),
    ("042", "Exact retraction is claimed only for the declared seeds, rules, caps, and refutations.", "MANUSCRIPT.md#Corollary-5", "major"),
    ("043", "The retraction result is not claimed as generic minimal-support, causality, or belief-contraction theory.", "MANUSCRIPT.md#Corollary-5", "major"),
]
for suffix, text, pointer, importance in formal:
    add(f"C_FORM_{suffix}", "Formal system, Theorems 1-4 and Corollaries 3/5", text, "formal_claim", "VERIFIED", "proof", pointer, importance=importance)


# ---------------------------------------------------------------------------
# Executable evaluator and native-engine study definitions
# ---------------------------------------------------------------------------

evaluator = [
    ("001", "The evaluator accepts a machine-readable instance containing licenses, claims, seeds, rules, refutations, and optional expected outcomes.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("002", "The JSON Schema checks instance document shape.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_schema.json"),
    ("003", "Semantic validation rejects duplicate identifiers.", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py"),
    ("004", "Semantic validation rejects references to undeclared claims.", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py"),
    ("005", "Semantic validation rejects references to undeclared licenses.", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py"),
    ("006", "Semantic validation rejects empty rule bodies because independent facts are represented as seeds.", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py"),
    ("007", "The evaluator performs deterministic bottom-up iteration of F_R.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("008", "The evaluator records the iteration rank of each first claim-license appearance.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("009", "Proof reconstruction descends strictly through iteration ranks.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("010", "Strict rank descent prevents cyclic proof output even when the rule graph contains cycles.", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py"),
    ("011", "Retraction is computed by comparing unrefuted and refuted least fixed points.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("012", "Canonical ordering makes reports byte-stable for equal inputs.", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py"),
    ("013", "The implementation does not infer whether a license vocabulary is scientifically appropriate.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("014", "The implementation does not determine whether a seed deserves its label.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("015", "The implementation does not determine whether a rule cap represents a defensible evidential transition.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("016", "The forecast case withdraws a falsified equality while retaining independently supported bounds.", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/forecast_falsification.json"),
    ("017", "The forecast case prevents a post-outcome repair from regaining prospective status.", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/forecast_falsification.json"),
    ("018", "The query-specific case separates decision authority from exact-value authority.", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/query_specific_falsification.json"),
    ("019", "The query-specific case separates decision authority from witness authority.", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/query_specific_falsification.json"),
    ("020", "The bounded-frontier case prevents finite internal computation plus analytic support from licensing an unresolved exact theorem.", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/bounded_frontier.json"),
    ("021", "The three cases demonstrate only the declared algebra and do not establish general usability across scientific communities.", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C11"),
]
for suffix, text, pointer in evaluator:
    status = "BOUNDED_INFERENCE" if suffix in {"013", "014", "015", "021"} else "VERIFIED"
    add(f"C_EVAL_{suffix}", "Executable semantics: reference evaluator and case families", text, "interpretation" if status == "BOUNDED_INFERENCE" else "method", status, "analysis" if status == "BOUNDED_INFERENCE" else "method_record", pointer, support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS")

native_defs = [
    ("001", "v_A and v_B denote native-engine decisions for the two parent stores."),
    ("002", "v_U and v_I denote native-engine decisions for textual union and intersection."),
    ("003", "The parent-authorized reference P is v_A OR v_B."),
    ("004", "A hybrid authorization H is v_U AND NOT v_A AND NOT v_B."),
    ("005", "Hybrid authorization denotes an origin-mixing event and does not by itself imply a security vulnerability."),
    ("006", "For a method decision d, unsafe merge is d AND H."),
    ("007", "For a method decision d, needless rejection is NOT d AND P."),
    ("008", "The five fixed policies are textual union, set intersection, reject all, prefer side B, and typed origin witness."),
    ("009", "The typed origin-witness policy is defined by d=P."),
    ("010", "The typed origin-witness unsafe-merge count is identically zero for any task set."),
    ("011", "The typed origin-witness needless-rejection count is identically zero for any task set."),
    ("012", "The typed origin-witness identity is a specification check rather than empirical accuracy or superiority."),
    ("013", "Typed origin witness requires two parent evaluations per task."),
    ("014", "Textual union requires one merged-store evaluation per task."),
]
for suffix, text in native_defs:
    cls = "interpretation" if suffix in {"005", "012"} else ("method" if suffix in {"008", "013", "014"} else "definition")
    status = "BOUNDED_INFERENCE" if cls == "interpretation" else ("VERIFIED" if cls == "method" else "COHERENT_DEFINITION")
    warrant = "analysis" if cls == "interpretation" else ("method_record" if cls == "method" else "definition")
    pointer = "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md" if cls == "method" else "MANUSCRIPT.md#Native-engine-study-outcome-definitions"
    add(f"C_NATIVE_{suffix}", "Native-engine study outcome definitions", text, cls, status, warrant, pointer, importance="major" if suffix in {"004", "009", "010", "011", "012"} else "supporting", support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS")


# ---------------------------------------------------------------------------
# Cedar null/adverse result
# ---------------------------------------------------------------------------

cedar = [
    ("001", "The Cedar study used the complete official multi-policy fixture family at the frozen source revision.", "method", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/SOURCE_BINDING_V1.json"),
    ("002", "The native Cedar engine reproduced all five frozen fixtures.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("003", "The native Cedar engine reproduced all 15 frozen requests.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("004", "The 15 Cedar requests comprised nine allows and six denies.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("005", "Decision outputs agreed on all 15 Cedar requests.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("006", "Reason outputs agreed on all 15 Cedar requests.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("007", "Error outputs agreed on all 15 Cedar requests.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("008", "Validation outputs agreed on all 15 Cedar requests.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("009", "The typed origin-preserving projection retained native reason sets without changing a native decision.", "empirical_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("010", "The Cedar corpus exposed zero independently authored evidence-authority, license, or retraction fields.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("011", "Study-authored typed labels cannot establish a real-domain positive for the intended evidence-license residual.", "interpretation", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULT_V1.md"),
    ("012", "The Cedar outcome is retained as null or adverse rather than relabeled as validation.", "interpretation", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULT_V1.md"),
    ("013", "The first Rust invocation failed before parsing any fixture because a pinned source override received a directory rather than an exact file.", "empirical_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/PREEXECUTION_FAILURE_V1.json"),
    ("014", "The first Rust invocation adjudicated zero requests.", "quantitative_result", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/PREEXECUTION_FAILURE_V1.json"),
    ("015", "The corrected Cedar invocation changed path binding but did not change fixtures or expected outcomes.", "method", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
]
for suffix, text, cls, warrant, pointer in cedar:
    status = "BOUNDED_INFERENCE" if cls == "interpretation" else "VERIFIED"
    add(f"C_CEDAR_{suffix}", "Empirical instantiations: retained Cedar null", text, cls, status, warrant, pointer, sources=("cutler2024",) if suffix in {"001"} else (), risk="high" if cls in {"quantitative_result"} else "normal", importance="major", support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS")


# ---------------------------------------------------------------------------
# X.509 construction, results table, controls, and adverse observations
# ---------------------------------------------------------------------------

x509_methods = [
    ("001", "The X.509 study used OpenSSL 3.6.4 test materials.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/SOURCE_BINDING_V2.json"),
    ("002", "The X.509 study used the native OpenSSL verification engine.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PINNED_OPENSSL_BUILD.md"),
    ("003", "The source was bound to the official OpenSSL 3.6.4 tag.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/SOURCE_BINDING_V2.json"),
    ("004", "The source was bound to a published OpenSSL 3.6.4 tarball digest.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/SOURCE_BINDING_V2.json"),
    ("005", "The content rule selected 252 public certificate- or revocation-list-bearing files.", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/CORPUS_MANIFEST.json"),
    ("006", "The selection rule excluded private-key material.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/CORPUS_MANIFEST.json"),
    ("007", "The selection rule excluded auxiliary material.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/CORPUS_MANIFEST.json"),
    ("008", "The upstream verification table contained 192 parsed rows.", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/TASK_MANIFEST_V2.json"),
    ("009", "Of the 192 parsed upstream rows, 191 were statically usable.", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/TASK_MANIFEST_V2.json"),
    ("010", "One upstream row was excluded before task construction because it depended on setup-generated material.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/TASK_MANIFEST_V2.json"),
    ("011", "The upstream-pair task family paired distinct upstream-authored store states sharing a leaf, purpose, and option set.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("012", "The upstream-pair family contained 1,858 tasks.", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/TASK_MANIFEST_V2.json"),
    ("013", "The parity-partition family split selected certificate material into two deterministic stores.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("014", "The parity-partition family contained 104 tasks.", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/TASK_MANIFEST_V2.json"),
    ("015", "Evaluations used row-specific times when supplied.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("016", "Evaluations used a fixed timestamp when no row-specific time was supplied.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("017", "The frozen X.509 task population contained 1,962 merge tasks.", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/TASK_MANIFEST_V2.json"),
    ("018", "A diagnostic execution found that the structural control omitted the depth-zero same-subject, same-public-key anchor case under partial-chain evaluation.", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("019", "The structural-control model was amended before the result commit.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("020", "The corpus, task manifest, and expected method definitions remained unchanged during the structural-control repair.", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
]
for suffix, text, warrant, pointer in x509_methods:
    cls = "quantitative_result" if warrant == "author_data" and suffix in {"005", "008", "009", "012", "014", "017"} else ("empirical_result" if warrant == "author_data" else "method")
    add(f"C_XMETH_{suffix}", "X.509 corpus and task construction", text, cls, "VERIFIED", warrant, pointer, sources=("openssl364", "rfc5280") if suffix in {"001", "002"} else (), risk="high" if cls == "quantitative_result" else "normal", importance="major")

table_values = {
    "UNION": ("Textual union", 810, 46, 379),
    "INTERSECTION": ("Intersection", 250, 0, 970),
    "REJECT": ("Reject all", 0, 0, 1143),
    "SIDEB": ("Prefer side B", 699, 0, 444),
    "ORIGIN": ("Typed origin witness", 1143, 0, 0),
}
for key, (label, allows, unsafe, needless) in table_values.items():
    for metric, value in (("ALLOWS", allows), ("UNSAFE", unsafe), ("NEEDLESS", needless)):
        wording = {"ALLOWS": "allows", "UNSAFE": "unsafe hybrids", "NEEDLESS": "needless rejections"}[metric]
        add(f"C_TABLE_{key}_{metric}", f"Table 1, {label} row", f"{label} has {value:,} {wording} over the frozen 1,962 tasks.", "quantitative_result", "VERIFIED", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json", risk="high", importance="major")
add("C_TABLE_CAPTION_001", "Table 1 caption", "Table 1 reports policy outcomes over 1,962 frozen merge tasks.", "figure_or_table", "VERIFIED", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json", importance="major")
add("C_TABLE_CAPTION_002", "Table 1 caption", "Unsafe hybrids are union-authorized tasks that neither parent authorizes.", "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#Native-engine-study-outcome-definitions")
add("C_TABLE_CAPTION_003", "Table 1 caption", "Needless rejections are parent-authorized tasks rejected by the policy.", "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#Native-engine-study-outcome-definitions")
add("C_TABLE_CAPTION_004", "Table 1 caption", "The origin-witness row equals v_A OR v_B by definition and is not a performance estimate.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C9", importance="headline", support_status="BOUNDS")

x509_results = [
    ("001", "The 46 hybrid tasks comprised 42 upstream-pair tasks.", "quantitative_result", "author_data", "ROUND2_RESULTS_V2.json"),
    ("002", "The 46 hybrid tasks comprised four parity-partition tasks.", "quantitative_result", "author_data", "ROUND2_RESULTS_V2.json"),
    ("003", "Forty-five hybrid tasks were classified as native-policy cases.", "quantitative_result", "author_data", "ROUND2_RESULTS_V2.json"),
    ("004", "One hybrid task was structurally mixed.", "quantitative_result", "author_data", "ROUND2_RESULTS_V2.json"),
    ("005", "The structural issuance graph could be derived within at least one origin for each of the 45 policy cases.", "empirical_result", "author_data", "ROUND2_RESULTS_V2.json"),
    ("006", "Native policy conditions still caused both parent decisions to deny in the 45 policy cases.", "empirical_result", "author_data", "ROUND2_RESULTS_V2.json"),
    ("007", "The general evaluator represents the 45 policy cases only by treating native per-origin decisions as fixed oracle facts.", "method", "method_record", "PROTOCOL_V2.md"),
    ("008", "The manuscript does not claim to reproduce X.509 policy semantics inside the evidence-license algebra.", "interpretation", "analysis", "ROUND2_METRIC_STATUS_FINDING.md"),
    ("009", "Typed origin witness requires 3,924 parent-store requests over 1,962 tasks.", "quantitative_result", "author_data", "ROUND2_RESULTS_V2.json"),
    ("010", "Textual union requires 1,962 merged-store requests over the 1,962 tasks.", "quantitative_result", "author_data", "ROUND2_RESULTS_V2.json"),
    ("011", "The typed-origin requirement is exactly twice the textual-union per-task request requirement.", "quantitative_result", "analysis", "ROUND2_RESULTS_V2.json"),
    ("012", "The complete ground-truth basis evaluated both parents, union, and intersection.", "method", "method_record", "PROTOCOL_V2.md"),
    ("013", "Caching reduced unique engine invocations in the full run without changing the declared per-policy request requirement.", "method", "method_record", "ROUND2_RESULTS_V2.json"),
]
for suffix, text, cls, warrant, rel in x509_results:
    pointer = f"submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/{rel}" if rel not in {"ROUND2_METRIC_STATUS_FINDING.md"} else f"submission/artifact/papers/orion-03-typed-merge-falsification/{rel}"
    status = "BOUNDED_INFERENCE" if cls == "interpretation" else "VERIFIED"
    add(f"C_XRES_{suffix}", "X.509 method outcomes", text, cls, status, warrant, pointer, risk="high" if cls == "quantitative_result" else "normal", importance="major", support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS")

controls = [
    ("001", "Re-execution of the usable upstream verification table agreed on 186 of 191 rows.", "quantitative_result", "author_data"),
    ("002", "Five usable upstream rows disagreed with the frozen re-execution.", "quantitative_result", "author_data"),
    ("003", "All five anchor disagreements were FIPS-provider rows containing a runtime token not statically executable in the frozen harness.", "empirical_result", "author_data"),
    ("004", "The five anchor disagreements remain counted rather than excluded after inspection.", "method", "method_record"),
    ("005", "The 186/191 agreement equals 97.38 percent.", "quantitative_result", "analysis"),
    ("006", "The 97.38 percent agreement exceeded the prospectively registered 95 percent anchoring gate.", "quantitative_result", "analysis"),
    ("007", "The anchor result is not reported as full reproduction.", "interpretation", "analysis"),
    ("008", "Two complete runs produced byte-identical result receipts.", "empirical_result", "author_data"),
    ("009", "After the documented repair, the one-directional structural control had zero violations across 1,962 tasks.", "quantitative_result", "author_data"),
    ("010", "Three upstream revocation adjudications retained their expected failures.", "quantitative_result", "author_data"),
    ("011", "The positive revocation control authorized when revocation checking was disabled.", "empirical_result", "author_data"),
    ("012", "No tested merge resurrected a revoked chain.", "empirical_result", "author_data"),
    ("013", "The complete-alternative-origin control produced zero false flags.", "quantitative_result", "author_data"),
    ("014", "A deliberately split chain was detected and localized.", "empirical_result", "author_data"),
    ("015", "The deliberately split hostile case was authored by the study and is interpreted only as a mechanics check.", "interpretation", "analysis"),
    ("016", "An independent in-repository implementation re-derived per-task parent decisions without importing the primary evaluator.", "method", "method_record"),
    ("017", "The independent in-repository implementation re-derived per-task union decisions without importing the primary evaluator.", "method", "method_record"),
    ("018", "The independent in-repository implementation re-derived per-task intersection decisions without importing the primary evaluator.", "method", "method_record"),
    ("019", "The independent in-repository implementation re-derived aggregate counts without importing the primary evaluator.", "method", "method_record"),
    ("020", "The independent in-repository implementation is implementation-level reproduction, not external human peer review.", "interpretation", "analysis"),
    ("021", "The independent in-repository implementation is not cross-institution replication.", "interpretation", "analysis"),
]
for suffix, text, cls, warrant in controls:
    status = "BOUNDED_INFERENCE" if cls == "interpretation" else "VERIFIED"
    pointer = "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"
    if suffix in {"016", "017", "018", "019"}:
        pointer = "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/repro_independent.py"
    add(f"C_CTRL_{suffix}", "Controls and adverse observations", text, cls, status, warrant, pointer, risk="high" if cls == "quantitative_result" else "normal", importance="major", support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS")


# ---------------------------------------------------------------------------
# Discussion, limitations, reproducibility, conclusion, declarations
# ---------------------------------------------------------------------------

discussion = [
    ("001", "The formal result is bounded to finite positive conjunctive systems.", "interpretation", "MANUSCRIPT.md#What-the-formal-result-establishes"),
    ("002", "A license is authorized exactly when an unrefuted finite proof tree carries it through every required seed and cap.", "formal_claim", "MANUSCRIPT.md#Theorem-2"),
    ("003", "Unsupported cycles add no license.", "formal_claim", "MANUSCRIPT.md#Corollary-3"),
    ("004", "Adding direct refutations cannot add licenses.", "formal_claim", "MANUSCRIPT.md#Theorem-4"),
    ("005", "Relative retraction removes exactly pairs losing all typed proof trees.", "formal_claim", "MANUSCRIPT.md#Corollary-5"),
    ("006", "A cap can make nonpromotion fail closed even when an untyped graph reaches the conclusion.", "formal_claim", "MANUSCRIPT.md#Compact-nonpromotion-examples"),
    ("007", "The executable record distinguishes reachability from a surviving prospective license.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/forecast_falsification.json"),
    ("008", "The algebra does not assign probabilistic confidence.", "interpretation", "MANUSCRIPT.md#Finite-typed-authority-system"),
    ("009", "The algebra does not resolve arbitrary inconsistency.", "interpretation", "MANUSCRIPT.md#Limitations"),
    ("010", "A mechanically consistent evidence policy can still contain indefensible seeds or caps.", "interpretation", "MANUSCRIPT.md#Reference-evaluator"),
    ("011", "Hybrid authorizations occurred in upstream-authored certificate material under the pinned native engine.", "empirical_result", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("012", "The four non-origin-witness fixed policies produced different measured costs on the same frozen tasks.", "empirical_result", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("013", "Evaluating both parents required twice as many per-task engine calls as evaluating union once.", "quantitative_result", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("014", "The origin-witness result is not detector performance.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C9"),
    ("015", "The study does not estimate generalization.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C9"),
    ("016", "The study does not estimate calibration.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C9"),
    ("017", "The study does not estimate predictive performance.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C9"),
    ("018", "The empirical support comprises hybrid occurrence, comparator trade-offs, native-engine bindings, controls, and adverse observations.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("019", "No adversary was studied.", "clinical_or_safety", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C8"),
    ("020", "No deployed system was studied.", "clinical_or_safety", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C8"),
    ("021", "No operational incident was studied.", "clinical_or_safety", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C8"),
    ("022", "No threat model was studied.", "clinical_or_safety", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C8"),
    ("023", "The native X.509 engine remains the authority for certificate semantics once a store is fixed.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("024", "The evidence-license layer contributes only the origin distinction erased by a flat merge.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/ROUND2_METRIC_STATUS_FINDING.md"),
    ("025", "Production use of the origin distinction remains a separate policy and usability question.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C11"),
    ("026", "The Cedar transfer is non-informative for evidence licenses despite complete native fixture success.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULT_V1.md"),
    ("027", "Native Cedar reason identifiers preserved policy provenance in the frozen fixtures.", "empirical_result", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("028", "The Cedar corpus lacked independently adjudicated evidence-license or retraction fields.", "empirical_result", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("029", "Treating study-authored Cedar labels as a domain positive would be self-authorizing.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULT_V1.md"),
    ("030", "The X.509 study's positive evidential basis requires upstream material, a native adjudicator, and a predeclared origin-mixing event.", "interpretation", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
]
for suffix, text, cls, pointer in discussion:
    status = "VERIFIED" if cls in {"formal_claim", "empirical_result", "quantitative_result"} else "BOUNDED_INFERENCE"
    warrant = "proof" if cls == "formal_claim" else ("author_data" if cls in {"empirical_result", "quantitative_result"} else "analysis")
    add(f"C_DISC_{suffix}", "Discussion", text, cls, status, warrant, pointer, risk="high" if cls in {"quantitative_result", "clinical_or_safety"} else "normal", importance="major", support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS")

limitations = [
    ("001", "The formal system handles finite rules only."),
    ("002", "The formal system handles positive rules only."),
    ("003", "The formal system handles conjunctive rules only."),
    ("004", "The formal system does not model negation."),
    ("005", "The formal system does not model defaults."),
    ("006", "The formal system does not model probabilistic evidence."),
    ("007", "The formal system does not model inconsistency."),
    ("008", "The formal system does not model arbitrary scientific disagreement."),
    ("009", "The powerset/intersection transfer is one policy design rather than a universal authority algebra."),
    ("010", "Curated license vocabularies can be scientifically wrong even when evaluation is mechanically correct."),
    ("011", "Curated seeds can be scientifically wrong even when evaluation is mechanically correct."),
    ("012", "Curated caps can be scientifically wrong even when evaluation is mechanically correct."),
    ("013", "Curated direct refutations can be scientifically wrong even when evaluation is mechanically correct."),
    ("014", "The three scientific-record cases are bounded mechanism demonstrations."),
    ("015", "The cases do not establish cross-institution usability."),
    ("016", "The cases do not establish human interpretability."),
    ("017", "The cases do not establish improved scientific decision making."),
    ("018", "Repeated execution within one repository is not external replication."),
    ("019", "The X.509 tasks come from one pinned OpenSSL test corpus."),
    ("020", "The X.509 tasks use one native engine version."),
    ("021", "The 46 hybrids do not estimate production prevalence."),
    ("022", "Forty-five hybrids depend on native policy decisions not reproduced by the structural model."),
    ("023", "Observed policy costs are conditional on the frozen task construction."),
    ("024", "Observed policy costs are conditional on the frozen engine semantics."),
    ("025", "The origin-witness zero errors cannot support a superiority claim."),
    ("026", "The two-parent cost may be unacceptable under different latency requirements."),
    ("027", "The two-parent cost may be unacceptable under different trust requirements."),
    ("028", "No user study was performed."),
    ("029", "No deployment evaluation was performed."),
    ("030", "No security assessment was performed."),
]
for suffix, text in limitations:
    add(f"C_LIM_{suffix}", "Limitations", text, "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md", risk="high" if suffix in {"021", "025", "030"} else "normal", importance="major", support_status="BOUNDS")

repro = [
    ("001", "The artifact includes the complete reference evaluator.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"),
    ("002", "The artifact includes the instance schema.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence_license_schema.json"),
    ("003", "The artifact includes evaluator tests and case encodings.", "submission/artifact/papers/orion-03-typed-merge-falsification/test_evidence_license_evaluator.py"),
    ("004", "The artifact includes Cedar null-result records.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/ROUND1_RESULTS_V1.json"),
    ("005", "The artifact includes the X.509 protocol and task manifest.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/TASK_MANIFEST_V2.json"),
    ("006", "The artifact includes X.509 source bindings and result receipts.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("007", "The artifact includes the independent in-repository reproducer.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/repro_independent.py"),
    ("008", "The artifact includes selected third-party OpenSSL material.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/third_party/openssl-3.6.4-testcerts"),
    ("009", "The artifact includes OpenSSL attribution and license notices.", "submission/artifact/licenses/OPENSSL_LICENSE.txt"),
    ("010", "The source archive includes editable manuscript source.", "submission/source/MANUSCRIPT.md"),
    ("011", "The source archive includes the bibliography.", "submission/source/references.bib"),
    ("012", "The source archive includes the Springer Nature class and numeric bibliography style used for compilation.", "submission/source/sn-jnl.cls"),
    ("013", "The source archive includes build instructions.", "submission/source/build.sh"),
    ("014", "The component binding manifest records the canonical manuscript and PDF hashes and byte counts.", "COMPONENT_BINDING_MANIFEST.json"),
    ("015", "The component binding manifest records source-archive and artifact-archive hashes and exact member sets.", "COMPONENT_BINDING_MANIFEST.json"),
    ("016", "The X.509 protocol identifies the source tag and commit.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("017", "The X.509 protocol identifies the source tarball digest.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/SOURCE_BINDING_V2.json"),
    ("018", "The X.509 protocol identifies the fixed evaluation time.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("019", "The X.509 protocol identifies the selection rule.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PROTOCOL_V2.md"),
    ("020", "The X.509 record identifies the native-engine version.", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/PINNED_OPENSSL_BUILD.md"),
    ("021", "Missing external tools or source material are treated as unavailable rather than silently substituted.", "submission/artifact/packages/typed-merge-evaluator/REPRODUCTION.md"),
    ("022", "The package verifier checks hashes and archive membership.", "review_records/verify_release.py"),
    ("023", "Package verification grants no scientific authority beyond proved or measured claims.", "submission/artifact/packages/typed-merge-evaluator/REPRODUCTION.md"),
]
for suffix, text, pointer in repro:
    add(f"C_REPRO_{suffix}", "Reproducibility", text, "availability_or_compliance" if suffix not in {"023"} else "interpretation", "VERIFIED" if suffix not in {"023"} else "BOUNDED_INFERENCE", "method_record" if suffix not in {"023"} else "analysis", pointer, risk="high", importance="major", support_status="ENTAILS" if suffix not in {"023"} else "BOUNDS")

conclusion = [
    ("001", "Boolean reachability is too coarse for the paper's typed evidential-permission question.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Typed-proof-trees"),
    ("002", "The finite system attaches licenses to positive conjunctive derivations.", "definition", "COHERENT_DEFINITION", "definition", "MANUSCRIPT.md#Finite-typed-authority-system"),
    ("003", "A rule cannot transmit a license absent from a premise or excluded by its cap.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Corollary-3"),
    ("004", "Least-fixed-point and proof-tree semantics coincide.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-2"),
    ("005", "Refutation can only remove licenses.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-4"),
    ("006", "Retraction is exact relative to the declared algebra.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Corollary-5"),
    ("007", "The cases block prospective promotion in bounded scientific records.", "empirical_result", "VERIFIED", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/forecast_falsification.json"),
    ("008", "The cases block theorem-level promotion in bounded scientific records.", "empirical_result", "VERIFIED", "method_record", "submission/artifact/papers/orion-03-typed-merge-falsification/examples/bounded_frontier.json"),
    ("009", "The X.509 instantiation establishes non-vacuous origin mixing in the frozen corpus.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("010", "Alternative fixed merge policies have different measured costs on the frozen tasks.", "empirical_result", "VERIFIED", "author_data", "submission/artifact/papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json"),
    ("011", "The strongest supported conclusion is that explicit caps and origin witnesses make nonpromotion auditable in the declared finite positive system.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md",),
    ("012", "The results do not create a new general provenance theory.", "novelty_or_priority", "BOUNDED_INFERENCE", "literature", None),
    ("013", "The results do not certify a security system.", "clinical_or_safety", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md#D3-C8"),
    ("014", "The results do not replace scientific judgment.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/artifact/papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md"),
]
for suffix, text, cls, status, warrant, pointer in conclusion:
    sources = ("doyle1979", "martins1988", "agm1985", "kifer1992", "green2007", "cheney2009", "bourgaux2022", "abokhamis2022", "bonatti2011", "buneman2002", "meliou2010", "thapa2026minimal", "thapa2026stratified") if suffix == "012" else ()
    add(f"C_CONC_{suffix}", "Conclusion", text, cls, status, warrant, pointer, sources=sources, risk="high" if cls in {"novelty_or_priority", "clinical_or_safety"} else "normal", importance="headline" if suffix in {"011", "012", "013"} else "major", support_status="BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS")

declarations = [
    ("001", "No funding was received for conducting the study.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("002", "The author declares no competing interests relevant to the article.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("003", "The study used no human participants.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("004", "The study used no human data.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("005", "The study used no animals.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("006", "Consent to participate is not applicable.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("007", "Consent for publication is not applicable.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("008", "Sze Chun Yiu is the sole author.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("010", "Generative AI tools were used for drafting and editing assistance.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("011", "The author accepts responsibility for all scientific content.", "review_records/AUTHOR_CONFIRMATION_V1.json"),
    ("013", "The submission artifact contains the exact data files used to audit the reported results.", "COMPONENT_BINDING_MANIFEST.json"),
    ("014", "Third-party OpenSSL material remains under Apache License 2.0 with bundled attribution.", "submission/artifact/licenses/OPENSSL_LICENSE.txt"),
    ("015", "The manuscript source, evaluator, schema, cases, tests, independent reproducer, and reproduction instructions are present in the submission archives.", "COMPONENT_BINDING_MANIFEST.json"),
    ("016", "Selected OpenSSL test materials required for task construction are included with source binding, attribution, and license.", "COMPONENT_BINDING_MANIFEST.json"),
]
for suffix, text, pointer in declarations:
    add(f"C_DECL_{suffix}", "Statements and Declarations", text, "availability_or_compliance", "VERIFIED", "method_record", pointer, risk="high", importance="major")


# Every in-text citation occurrence is recorded separately from source receipts.
CITATION_USES: list[dict[str, Any]] = []


def cite(citation_id: str, source: str, location: str, *claim_ids: str) -> None:
    CITATION_USES.append({
        "citation_id": citation_id,
        "source_key": source,
        "location": location,
        "claim_ids": list(claim_ids),
    })


for key in ("doyle1979", "martins1988", "agm1985", "kifer1992", "green2007", "cheney2009"):
    cite(f"CITE_INTRO_{key}", key, "Introduction, donor-substrate sentence", "C_INT_008")
cite("CITE_RW_DOYLE", "doyle1979", "Related work, belief maintenance, sentence 1", "C_LIT_001")
cite("CITE_RW_MARTINS", "martins1988", "Related work, belief maintenance, sentence 2", "C_LIT_002")
cite("CITE_RW_AGM", "agm1985", "Related work, belief maintenance, sentence 3", "C_LIT_003")
cite("CITE_RW_KIFER", "kifer1992", "Related work, annotated logic, sentence 1", "C_LIT_005")
cite("CITE_RW_GREEN", "green2007", "Related work, annotated logic, sentence 2", "C_LIT_006")
cite("CITE_RW_BOURGAUX", "bourgaux2022", "Related work, annotated logic, sentence 2", "C_LIT_007")
cite("CITE_RW_ABOKHAMIS", "abokhamis2022", "Related work, annotated logic, sentence 2", "C_LIT_008")
cite("CITE_RW_BONATTI", "bonatti2011", "Related work, annotated logic, sentence 3", "C_LIT_009")
cite("CITE_RW_CHENEY", "cheney2009", "Related work, annotated logic, sentence 3", "C_LIT_010")
cite("CITE_RW_BUNEMAN", "buneman2002", "Related work, deletion and causality, sentence 1", "C_LIT_012")
cite("CITE_RW_MELIOU", "meliou2010", "Related work, deletion and causality, sentence 1", "C_LIT_013")
cite("CITE_RW_THAPA_MIN", "thapa2026minimal", "Related work, deletion and causality, sentence 2", "C_LIT_014")
cite("CITE_RW_THAPA_STRAT", "thapa2026stratified", "Related work, deletion and causality, sentence 2", "C_LIT_015")
cite("CITE_RW_CEDAR", "cutler2024", "Related work, authorization, sentence 1", "C_LIT_020")
cite("CITE_RW_RFC", "rfc5280", "Related work, authorization, sentence 2", "C_LIT_021")
cite("CITE_CEDAR_EMP", "cutler2024", "Cedar null result, opening sentence", "C_CEDAR_001")
cite("CITE_X509_OPENSSL", "openssl364", "X.509 construction, opening sentence", "C_XMETH_001")
cite("CITE_X509_RFC", "rfc5280", "X.509 construction, opening sentence", "C_XMETH_002")


def claim_specs() -> list[dict[str, Any]]:
    """Return a defensive copy of the immutable atomic inventory."""
    return [dict(item) for item in C]


def citation_uses() -> list[dict[str, Any]]:
    return [dict(item) for item in CITATION_USES]
