# Target-Sufficient Verification for Scientific Claim Promotion

## Abstract

Verification is often treated as if stronger provenance, more checks, or higher confidence must monotonically strengthen a scientific conclusion. That inference is unsafe when the decision to promote a claim depends on obligations that are not represented by the verification record itself. We study scientific claim promotion as a target-specific decision problem. For a finite decision space, we show that exact promotion is attainable from a representation only when the correct terminal is constant on every representation fibre with positive mass and is expressible by the available output alphabet. Mixed fibres impose an irreducible Bayes-error floor, so optimization downstream of an information-losing interface cannot recover a distinction that the interface has erased.

We test this separation in two bounded protected campaigns. In the first, 60 clean cases and 360 hostile or insufficient-evidence cases are evaluated under a fixed promotion contract. The target-aware rule produces no false promotions among the 360 hostile opportunities while preserving all 60 clean promotions; the strongest frozen mechanism proxy produces 180 false promotions on the same hostile set. A prespecified third hypothesis remains negative because its eligible family was saturated by construction, and we retain that null rather than reinterpret it after later work. In a second, more demanding exact-contract study spanning five heterogeneous scientific artifact domains, eight case archetypes and ten protected variants, the target-aware rule is correct on all 400 cases. A strong product carrying provenance, verification, version, evaluator-custody, epoch and generic authorization information is correct on 250 of 400 cases, while an ideal product supplied with the same target-defining scientific coordinates ties exactly at 400 of 400. The paired accuracy difference against the strong generic product is 0.375, with a domain-stratified bootstrap 95% interval of 0.3275 to 0.4225.

These results support a bounded conclusion: scientific claim promotion is a distinct target-bound relation, not a scalar accumulation of generic verification signals. The contribution is the sufficiency boundary and a non-compensatory decision contract, not a claim that one software architecture has inherent expressive advantage or that the tested finite domains establish universal scientific authority.

## 1. Introduction

Scientific workflows increasingly record provenance, version identity, test outcomes, evaluator state, authorization, confidence and reproducibility information. These records are useful, but they answer different questions. A valid execution record can establish that a computation ran. A provenance record can establish where an artifact came from. A verifier can establish a local property of an object. None of these statements alone determines whether a broader scientific claim may be promoted.

The gap matters because scientific promotion is often non-compensatory. A claim may have excellent provenance and a successful local verification while still lacking an independent evidence source, an admissible scope bridge or the information required to distinguish a supported conclusion from an unsupported one. Treating many favorable lower-level signals as compensation for one missing hard obligation can therefore create false scientific promotion.

We ask a narrower question than whether verification is generally useful:

> What information must a verification interface preserve for a specified scientific-promotion decision to be recoverable at all?

We answer this question at two levels. First, we give an exact finite-space sufficiency result that separates information adequacy from downstream optimization. Second, we test the resulting decision structure in protected finite campaigns that include positive, hostile, indeterminate and deliberately non-discriminating regimes.

The analysis leads to three principles. First, promotion is identifiable only when the visible representation separates states that require different scientific decisions. Second, an information-equivalent alternative implementation must tie; the contribution therefore cannot be an architectural centralization claim. Third, a good evaluation must preserve negative and non-identifying regimes because those regimes reveal when a verification axis cannot support the intended scientific inference.

## 2. Scientific promotion as a target-specific decision

Let a scientific state be mapped to an observable representation and let the target promotion rule assign one of the admissible scientific terminals. The representation partitions the state space into fibres: states that look identical to the decision procedure.

For a finite state space, the optimal terminal risk given a representation is the fibrewise Bayes error. Exact promotion is possible if and only if two conditions hold on every positive-mass fibre: the target terminal is constant within that fibre, and the required terminal can be expressed by the output alphabet. If a fibre contains states that require different scientific decisions, no downstream classifier, search procedure or optimizer using only that representation can recover the lost distinction.

This result gives a useful control. Suppose a competing system is enriched until it receives exactly the same target-sufficient scientific coordinates and the same decision relation. It must then agree extensionally with the proposed rule. A tie in that condition is evidence that the scientific object is representation-independent; it is not a failure of the contribution.

The same reasoning also distinguishes interface failure from scientific inferiority. A comparator that cannot express an indeterminate outcome should not have its parse failure, generic block state or free-text uncertainty relabeled after the fact as the target terminal. The correct conclusion is that the interface cannot realize the requested decision at that evidence boundary.

## 3. Protected evaluation design

The empirical studies use exact finite contracts so that every case has a mechanically determined target under the registered rules. The evaluation separates four objects that are often conflated: the evidence available to each arm, the terminal alphabet the arm can express, the scientific obligations that define the target, and the decision rule that maps the visible state to the target.

Comparators receive the same case content wherever the scientific comparison requires it. Strong comparators are deliberately given ordinary provenance, verification, artifact and version identity, evaluator-custody information, freshness or epoch information and generic authorization capabilities before the target-specific relation is tested. An ideal typed product receives the same target-defining scientific coordinates as the proposed rule and serves as an equivalence control.

The studies also include negative cases by design. Missing or insufficient evidence is not silently converted into denial or approval. A non-identifying panel is retained as non-identifying. Later evidence is not used to rewrite the outcome of an earlier frozen test.

## 4. A bounded campaign separates local verification from scientific promotion

The first protected campaign contains 420 exact mechanical-gold cases: 60 clean positives and 360 opportunities for hostile or insufficient-evidence promotion. The target-aware rule makes no false promotions in the hostile set and promotes all clean cases. The strongest frozen mechanism proxy promotes all clean cases as well, but falsely promotes 180 of the 360 hostile opportunities.

The paired difference on the hostile set is therefore large, but the important interpretation is structural rather than merely numerical. The competing mechanism can verify important local properties and still lack a target-defining scientific obligation. Favorable local evidence does not compensate for that missing relation.

One prespecified hypothesis in the same campaign does not discriminate the systems because its eligible family is saturated by construction. We retain that result as a null. Later work that creates a more expressive interface does not retroactively turn the original test into a positive result.

## 5. Stronger generic verification still does not determine the target decision

The second protected study raises the comparator standard. It spans five heterogeneous scientific artifact domains, eight case archetypes and ten protected variants, for 400 exact cases in total. The target-aware rule is correct on 400 of 400 cases. A strong generic product that includes provenance, local verification, artifact and version binding, evaluator custody, epoch information and generic authorization is correct on 250 of 400. A compensatory rule that allows favorable evidence dimensions to offset missing hard obligations is correct on 50 of 400.

The paired difference between the target-aware rule and the strong generic product is 0.375; a domain-stratified bootstrap gives a 95% interval from 0.3275 to 0.4225. The target-aware rule produces no false promotions and retains a clean promotion rate of 1.0 on the registered clean cases.

The ideal typed product is correct on all 400 cases and matches the target-aware rule exactly. This equivalence is load-bearing. It shows that the result is not that one implementation has privileged access to scientific truth. The result is that the decision becomes recoverable when the representation contains the information required by the target relation.

## 6. What the experiments establish

The two campaigns support four bounded claims.

First, generic verification success and scientific-promotion entitlement are distinct. Second, hard scientific obligations should not be replaced by compensation among unrelated favorable signals. Third, an interface that merges states requiring different promotion decisions imposes an irreducible decision error regardless of downstream optimization. Fourth, an information-equivalent product must tie, so the scientific contribution is portable across implementations.

They do not establish that the registered coordinates are universally minimal, that the rule is superior on deployed scientific systems, or that every external verifier can be embedded without loss. A larger naturalistic evaluation has been designed but has not produced admissible outcome evidence and therefore contributes no empirical authority to the present paper.

## 7. Relation to existing verification and governance mechanisms

The paper does not claim provenance, source-aware verification, artifact identity, evaluator auditing, contamination detection, abstention, assurance cases or generic authorization as new mechanisms. Those capabilities are treated as inputs to the comparison.

The residual question is narrower: after those mechanisms are available, what additional information is required to decide whether a particular scientific claim may be promoted? The fibre condition provides an exact answer for the finite decision model, and the protected campaigns show why the distinction matters in heterogeneous exact contracts.

This framing also explains why stronger engineering can legitimately produce a tie. If a competing system is enriched with the same target-sufficient state and promotion relation, the scientific decision should be identical. The paper therefore argues for a decision contract, not for a proprietary architecture.

## 8. Limitations

The empirical evidence is finite and contract-driven. It does not estimate performance on an open population of scientific tasks, and no deployed-agent or provider-level generalization is claimed. The exact fibre theorem assumes a declared target map and representation; it does not determine whether those objects faithfully capture an external scientific domain. The naturalistic successor remains unresolved because source eligibility, rights, pairing and independent custody have not all been established at the required scale.

The evaluation also does not show that every uncertain case should be rejected. An indeterminate terminal is a statement about missing decision-relevant evidence, not a negative scientific conclusion. New admissible evidence may later resolve it.

## 9. Reproducibility and availability

The formal statements, protected-case definitions, comparator contracts, result tables and independent reconstruction are preserved in a versioned research package. The final submission should bind the anonymous manuscript, exact result artifacts and reproduction environment to one archived release. Reviewer-facing materials should expose scientific descriptions rather than internal project identifiers.

## 10. Conclusion

Scientific promotion cannot be inferred by simply accumulating favorable verification signals. For a fixed target decision, the decisive question is whether the visible representation preserves the distinctions on which that decision depends. In finite spaces, mixed representation fibres impose an exact error floor. In two bounded protected campaigns, target-sufficient state supports exact promotion while strong generic verification remains insufficient, and an information-equivalent typed product ties exactly. The resulting claim is deliberately narrow: target-sufficient verification is a necessary decision layer for the tested promotion contracts, not a universal authority mechanism for science.