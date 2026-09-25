# Target-Sufficient Verification for Scientific Claim Promotion in AI Systems

## Abstract

AI-assisted scientific workflows increasingly accumulate provenance, verification, version, authorization, and reproducibility signals before deciding whether a scientific claim may be promoted. More favorable signals do not necessarily make that decision recoverable: if the representation given to the decision rule erases a distinction on which the target scientific terminal depends, no downstream optimization can reconstruct it.

We formalize scientific claim promotion as a target-specific decision problem. In a finite state space, exact promotion from a representation is possible only when the target terminal is constant on every positive-mass representation fibre and the required terminal is expressible by the output alphabet. Mixed fibres impose an irreducible Bayes-error floor. Information adequacy is therefore logically prior to classifier strength, search, or aggregation of generic verification signals.

Two protected finite campaigns test the consequence. In the first, 60 clean cases and 360 hostile or insufficient-evidence cases are evaluated under a fixed promotion contract. The target-sufficient rule promotes all 60 clean cases and makes no false promotions among the 360 hostile opportunities, whereas the strongest frozen generic mechanism proxy makes 180 false promotions on that hostile set. A prespecified non-discriminating hypothesis remains negative and is retained as such. In a second study spanning five scientific artifact domains, eight case archetypes, and ten protected variants, the target-sufficient rule is correct on all 400 cases. A strong generic product carrying provenance, local verification, version, evaluator custody, epoch, and generic authorization information is correct on 250 of 400; the paired accuracy difference is 0.375 with a domain-stratified bootstrap 95% interval of 0.3275 to 0.4225. An ideal competing product supplied with the same target-defining scientific coordinates ties exactly at 400 of 400.

The bounded conclusion is that scientific promotion is a target-bound relation rather than a scalar accumulation of generic assurance. The contribution is the sufficiency boundary and a non-compensatory evaluation contract, not universal scientific authority, a universally minimal coordinate system, deployed-agent generalization, or architectural superiority.

## 1. Introduction

Modern scientific software can answer many local questions with high assurance. A provenance record can identify the origin of an artifact. A verifier can establish a property of a proof, program, or data product. Version and evaluator-custody records can establish which object was checked and under which process. Authorization can establish that an action is permitted.

A different question is whether a **scientific claim may be promoted**. Promotion can depend on obligations that are not interchangeable with local assurance: an admissible evidence source, a valid scope bridge, a particular measurement interpretation, or an explicit indeterminate terminal when evidence is insufficient. A system that treats many favorable local signals as compensation for one missing hard obligation can therefore promote a claim that its own information does not support.

We ask an information question before an algorithm question:

> What distinctions must a verification interface preserve for a specified scientific-promotion decision to be recoverable at all?

The answer has a simple finite-space form. A representation partitions scientific states into fibres. If two states in the same visible fibre require different target terminals, the interface has already erased information needed by the decision. No classifier trained downstream can recover that distinction from the representation alone.

### 1.1 Contributions and claim boundary

The paper contributes:

1. **an exact finite-space sufficiency criterion** for target-specific promotion;
2. **a non-compensatory decision contract** for hard scientific obligations;
3. **two protected campaigns** showing that rich generic assurance can remain target-insufficient; and
4. **an information-equivalent control** that ties exactly, ruling out a proprietary-architecture interpretation.

One prespecified hypothesis in the first campaign is non-discriminating and remains negative. The paper does not convert that null into a mechanism claim. The current empirical authority is bounded to the protected finite contracts described below.

## 2. A sufficiency boundary for promotion

Let the underlying scientific state be \(s\in S\), the visible representation be \(r(s)\), and the target promotion terminal be \(y(s)\) in a declared output alphabet. The representation induces fibres containing states indistinguishable to any downstream decision rule using only \(r\).

For finite \(S\), the minimum achievable target error given \(r\) is the fibrewise Bayes error. Exact recovery requires two conditions on every positive-mass fibre:

1. the target terminal is constant throughout the fibre; and
2. that terminal is expressible by the interface's output alphabet.

If either condition fails, exact promotion is impossible from that interface. The limitation is informational rather than computational.

This theorem also gives a strong equivalence control. If a competing implementation is enriched until it receives the same target-defining scientific coordinates and terminal semantics, it should tie extensionally. A tie is expected evidence of representation independence, not a failed superiority test.

## 3. Promotion is non-compensatory when obligations are hard

Many assurance products are naturally compositional. More provenance, checks, or authorization records can increase confidence in the properties they actually certify. Scientific promotion, however, can contain hard obligations.

Suppose the target contract requires an admissible evidence source and a scope bridge. Five successful execution or provenance checks cannot logically replace the missing source or bridge unless an explicit scientific rule connects those checks to the missing obligation. The same applies to indeterminate states: an interface that can emit only approve/deny cannot faithfully realize a target whose correct terminal is “insufficient evidence.”

The proposed decision contract therefore treats favorable dimensions as evidence for their own obligations rather than generic credits in a compensatory score.

## 4. Protected campaign I: local verification versus promotion

The first exact campaign contains 420 mechanically determined cases: 60 clean positives and 360 hostile or insufficient-evidence opportunities. Every arm is judged against the same frozen promotion contract.

The target-sufficient rule promotes all 60 clean cases and makes zero false promotions in the hostile set. The strongest frozen generic mechanism proxy also preserves the clean positives but falsely promotes 180 of the 360 hostile opportunities.

The result is not interpreted as a population performance estimate. It is a bounded exact demonstration that a mechanism can succeed at important local verification tasks while lacking a distinction required by the scientific target.

A prespecified hypothesis in the same campaign is non-discriminating because its eligible family is saturated by construction. That null remains a null. Later work with a more informative interface does not retroactively convert the frozen test into positive evidence.

## 5. Protected campaign II: a stronger generic product remains insufficient

The second campaign strengthens the comparator. It spans five heterogeneous scientific artifact domains, eight case archetypes, and ten protected variants, giving 400 exact cases.

The generic product carries provenance, local verification, artifact and version binding, evaluator custody, epoch information, and generic authorization. It is therefore not a straw baseline. Nevertheless, it is correct on 250 of 400 cases because some target-defining scientific distinctions remain absent. The target-sufficient rule is correct on all 400.

The paired accuracy difference is 0.375. A domain-stratified bootstrap gives a 95% interval of 0.3275 to 0.4225. The target-sufficient rule also produces no false promotions on the registered hostile cases while preserving the registered clean promotions.

A compensatory rule that allows favorable dimensions to offset missing hard obligations performs substantially worse, illustrating the failure mode the contract is designed to expose.

## 6. Information-equivalent systems must tie

The most important control is an ideal competing product given exactly the same target-defining scientific coordinates and promotion relation. It is correct on all 400 cases and matches the target-sufficient rule exactly.

This result removes an architectural interpretation. The scientific object is the target-sufficient information and decision relation, not where that information is stored or which software component evaluates it. Any information-equivalent implementation should realize the same terminal map.

This also narrows the novelty claim. The paper does not argue that provenance, authorization, versioning, or verification are weak mechanisms. It argues that their native judgments cannot license a different scientific terminal unless the required target relation is represented.

## 7. Interface failure is not scientific inferiority

Some comparators cannot express every scientific terminal in the target contract. In particular, an interface may support generic success/failure while lacking an explicit indeterminate state.

Such a mismatch should not be scored by relabelling a parse failure or generic block state as the missing scientific terminal after seeing the answer. The correct conclusion is that the interface is not expressive enough for the specified decision boundary. This keeps representational insufficiency separate from scientific evidence about the underlying artifact.

## 8. Relation to verification, provenance, and governance

Provenance, source-aware verification, artifact identity, evaluator auditing, abstention, authorization, assurance cases, and reproducibility infrastructure are established mechanisms. They are treated here as donor capabilities rather than inventions of the paper.

The residual question appears one layer above those mechanisms: after their native signals are available, what information is still necessary to determine a particular scientific-promotion terminal? The fibre condition gives an exact answer for the declared finite model, while the protected campaigns show how missing target distinctions can survive even in a rich generic product.

For learning and intelligent systems, this can also be viewed as an evaluation-task formalization: the benchmark target is not “verification score” but a typed scientific terminal whose recoverability depends on the information exposed to the decision system.

## 9. Limitations

The theorem assumes a declared finite state space, representation, target map, and output alphabet. It does not determine whether those objects faithfully model every real scientific domain. The protected campaigns are finite and contract-driven; they do not estimate generalization to deployed agents or an open population of scientific claims.

The registered target coordinates are not proved universally minimal. A different domain may require fewer, more, or differently organized distinctions. An absent historical 400-row reduction artifact is not reconstructed or used as evidence. A naturalistic successor study remains unresolved because source eligibility, rights, pairing, and independent custody have not all been established at the required scale; it contributes no authority to the current paper.

An indeterminate terminal is also not a rejection of the scientific claim. It records that the present evidence is insufficient for the specified promotion decision and can change when new admissible evidence arrives.

## 10. Reproducibility and availability

The release package should bind the finite formal definitions, protected-case generators, comparator contracts, exact target tables, result records, and independent reconstruction to one versioned archive. Numeric claims in the abstract and main text should be generated from the same bound result objects used by reviewer-facing tables.

The submission and supplementary archive should remain double-blind. A named preprint can exist as a separate surface, but the anonymous submission should not link identity-bearing artifacts during review.

The current journal package must be rebuilt against this manuscript version and its claim-to-PDF audit rerun before filing.

## 11. Conclusion

Scientific promotion cannot be made sound merely by accumulating favorable verification signals. For a fixed target decision, the prior question is whether the visible representation preserves every distinction on which that decision depends. In finite spaces, mixed fibres impose an exact irreducible error floor. In two protected campaigns, target-sufficient state realizes the frozen promotion contract while a strong generic assurance product remains incomplete, and an information-equivalent product ties exactly. The resulting claim is intentionally narrow: target-sufficient verification is a decision layer for the tested promotion contracts, not a universal authority mechanism for science.