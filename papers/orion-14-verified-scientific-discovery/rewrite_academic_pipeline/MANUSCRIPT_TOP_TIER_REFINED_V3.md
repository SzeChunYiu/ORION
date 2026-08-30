# Target-Sufficient Verification for Scientific Claim Promotion in AI Systems

## Abstract

AI-assisted scientific workflows increasingly accumulate provenance, verification, version, authorization and reproducibility signals before deciding whether a claim may be promoted. More favorable assurance signals do not guarantee that the promotion decision is recoverable: if the representation exposed to the decision rule merges scientific states requiring different terminals, no stronger classifier can reconstruct the missing distinction.

We formalize scientific claim promotion as a target-specific finite decision problem. Exact recovery from a representation is possible only when the target terminal is constant on every positive-mass representation fibre and the required terminal is expressible by the output alphabet. Mixed fibres impose an irreducible Bayes-error floor. Information adequacy is therefore logically prior to classifier strength or aggregation of generic assurance.

Two protected finite campaigns test this boundary. In the first, 60 clean cases and 360 hostile or insufficient-evidence cases are evaluated under a fixed promotion contract. The target-sufficient rule promotes all 60 clean cases and makes no false promotions among the 360 hostile opportunities, whereas the strongest frozen generic mechanism proxy falsely promotes 180. Because the 360 cases are clustered within 12 attack families, the top-tier analysis uses family-respecting inference: the family-level contrast remains -0.5, a 20,000-resample family bootstrap gives a 95% interval of -0.75 to -0.25, and six of 12 families are discordant, all favoring the target-sufficient rule (two-sided exact cluster test `p=0.03125`). A prespecified non-discriminating hypothesis remains negative.

In a second study spanning five scientific artifact domains, eight case archetypes and ten protected variants, the target-sufficient rule is correct on all 400 cases. A strong generic product carrying provenance, local verification, version, evaluator custody, epoch and generic authorization is correct on 250 of 400; the paired accuracy difference is 0.375 with a domain-stratified bootstrap 95% interval of 0.3275–0.4225. An information-equivalent product supplied with the same target-defining scientific relation ties exactly at 400/400.

The contribution is a sufficiency boundary and non-compensatory evaluation contract, not universal scientific authority, a universally minimal coordinate system, deployed-agent generalization, or architectural superiority.

## 1. Scientific promotion is an information problem before an algorithm problem

A provenance record can establish where an artifact came from. A verifier can establish a local property. An authorization system can establish whether an action is permitted. A reproducibility record can establish whether an execution can be repeated. None of these native judgments automatically answers whether a **scientific claim may be promoted** under a target evidentiary responsibility.

Promotion can require hard obligations: an admissible evidence source, a scope bridge, a measurement interpretation, an authority relation, or an explicit unresolved terminal when evidence is insufficient. A system that sums favorable generic signals can therefore produce a confident answer even though the information needed for the target decision is absent.

We ask:

> What distinctions must a verification interface preserve for a specified scientific-promotion terminal to be recoverable at all?

The answer is a finite representation-sufficiency condition. The empirical campaigns then test whether strong generic assurance products can fail exactly at that boundary.

## 2. Fibre sufficiency theorem

Let `S` be a finite scientific state space, `r:S->Z` the representation visible to the promotion rule, and `y:S->Y` the target terminal. The representation partitions states into fibres `F_z={s:r(s)=z}`.

Any downstream decision using only `z` must return the same output for every member of a fibre. Therefore exact target recovery requires that the target be constant on each positive-mass fibre and that the required terminal be expressible in the interface output alphabet.

**Theorem 1 (target-sufficiency condition).** Exact promotion from `r` is possible if and only if every positive-mass fibre is target-homogeneous and its target terminal lies in the output alphabet.

When a fibre contains conflicting target terminals, the minimum achievable error is the fibrewise Bayes error. The limitation is informational, not computational: more model capacity cannot distinguish states that the interface maps to the same representation.

The theorem also predicts an equivalence control. Any competing product enriched with the same target-defining coordinates and terminal semantics should tie extensionally.

## 3. Hard obligations make promotion non-compensatory

Generic assurance often behaves additively: more checks can increase confidence in the properties they actually certify. Scientific promotion can instead be non-compensatory.

If the target requires an admissible evidence source and a valid scope bridge, several successful execution or provenance checks do not logically replace the missing source or bridge. Likewise, a binary approve/deny interface cannot exactly realize a target whose correct state is “insufficient evidence.”

The evaluation contract therefore scores each assurance signal only against the obligation it actually supports. A favorable local coordinate cannot erase a missing hard scientific relation.

## 4. Protected campaign I

The first campaign contains 420 mechanically determined cases: 60 clean positives and 360 hostile or insufficient-evidence opportunities. All arms are evaluated against the same fixed promotion target.

The target-sufficient rule promotes all 60 clean cases and makes zero false promotions in the hostile set. The strongest frozen generic mechanism proxy also preserves the clean positives but falsely promotes 180 of the 360 hostile cases.

### 4.1 Cluster-respecting uncertainty

The 360 hostile cases are organized into 12 attack families, so treating every case as an independent draw produces an interval that is too narrow for a family-level scientific interpretation.

A landed reanalysis uses the family as the independent cluster. The per-family contrast is zero in six families and -1 in six; all six discordant families favor the target-sufficient rule. The average difference remains -0.5. A 20,000-resample family bootstrap yields a 95% interval of -0.75 to -0.25. The exact two-sided cluster sign/McNemar-style test over the six discordant families gives `p=0.03125`.

This reanalysis preserves the direction of the result while correctly widening uncertainty to reflect dependence. The paper reports the family-level analysis as primary and retains the case-level arithmetic only as descriptive implementation evidence.

### 4.2 A negative prespecified hypothesis stays negative

A separate prespecified hypothesis in the same campaign is non-discriminating because its eligible family is saturated by construction. That test remains negative. Later success with a more informative representation does not retroactively convert the original frozen question into evidence.

## 5. Protected campaign II: a strong product remains target-insufficient

The second campaign strengthens the comparator and broadens the finite contract. It spans five artifact domains, eight archetypes and ten protected variants, yielding 400 exact cases.

The strong generic product carries provenance, local verification, artifact/version binding, evaluator custody, epoch and generic authorization. It is correct on 250 of 400 cases. The target-sufficient rule is correct on all 400.

The paired accuracy difference is 0.375 with a domain-stratified bootstrap 95% interval of 0.3275 to 0.4225. The target-sufficient rule also preserves every registered clean promotion and makes no registered false promotion.

The comparator is intentionally not weak. Its failures show that a rich collection of correct generic assurance signals can remain insufficient when the target scientific relation is not represented.

## 6. Information-equivalent product ties exactly

An ideal competing product is then supplied with the same target-defining scientific coordinates and promotion relation. It reaches 400/400 and matches every decision.

This is the expected result if the contribution is informational rather than architectural. The paper therefore does not claim that a centralized verifier is uniquely expressive. Any implementation carrying equivalent scientific state should reproduce the target map.

The tie also prevents a common benchmark overinterpretation: the scientific residual is not “our product beats all verification products,” but “generic assurance is insufficient until the target relation is represented.”

## 7. Interface mismatch is not scientific inferiority

Some comparators cannot emit all terminals in the target contract, especially an explicit indeterminate state. When the scientifically correct disposition is insufficient evidence, a binary interface is representationally incapable of matching the target without an added semantic bridge.

Such cases should not be scored by relabelling a generic block or parse failure as the missing scientific terminal after the outcome. The correct conclusion is interface insufficiency for the declared task.

This keeps scientific evidence about the underlying artifact separate from expressivity of the decision surface.

## 8. Relation to verification, provenance and AI evaluation

Provenance, authorization, source-aware verification, version binding, evaluator auditing, abstention and reproducibility are established donor mechanisms. The paper does not claim them as new.

The residual question appears one layer above: after these native signals are available, what information is still required for a particular scientific promotion decision? The fibre theorem gives an exact finite answer, and the campaigns show that strong generic products can remain target-insufficient.

For learning and intelligent systems, the result can also be viewed as an evaluation-task formalization: the benchmark target is a typed scientific terminal, not an aggregate verification score.

## 9. Limitations

The theorem assumes a declared finite state space, representation and target map. It does not establish that these objects capture every real scientific domain. The protected campaigns are contract-driven finite studies and do not estimate deployed-agent generalization.

The five/further target coordinates used by the experiments are not proved universally minimal, independent or complete. A different domain may need fewer, more or differently organized relations. A naturalistic successor remains externally blocked and contributes no authority to this paper.

The cluster-respecting campaign-I analysis addresses dependence across attack families; it does not transform the finite campaign into a population sample of scientific failures.

## 10. Reproducibility and TMLR release

The release should bind the finite theorem definitions, campaign generators, family identities, exact target tables, cluster reanalysis, comparator contracts, 400-case result records and independent reconstruction. Numeric abstract statements should be generated from the same bound objects used by figures and tables.

For TMLR, the manuscript and supplementary material remain double-blind. Identity-bearing locators belong only to the separate named release surface.

## 11. Conclusion

Scientific promotion cannot be made sound merely by accumulating favorable assurance signals. The prior question is whether the decision interface preserves every distinction on which the target terminal depends. In finite spaces, mixed representation fibres impose an irreducible error floor. In two protected campaigns, target-sufficient state realizes the frozen promotion contract while a strong generic product remains incomplete, and an information-equivalent product ties exactly. Family-respecting reanalysis preserves the first campaign's contrast without pretending its cases are independent. The result is a bounded sufficiency theory for scientific promotion, not universal authority or architectural superiority.