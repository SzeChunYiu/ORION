# Matched-Information Tests of Epistemic State in Scientific Decision Systems

## Abstract

Scientific decision systems can possess the same factual propositions yet behave differently because those facts are bound to different information about applicability, transformation history, uncertainty, or decision role. We ask whether such **epistemic state** can change decisions when the factual payload is otherwise matched. Six separately frozen exact-synthetic studies isolate type-conditioned priors, applicability scope, decision-relevant uncertainty, transformation lineage, decision-coupled acquisition, and remint obligations. The studies are synthesized after completion as a mechanism taxonomy; their effect scales are not pooled, and the taxonomy is not claimed to be minimal.

The results show both mechanism value and donor absorption. Type-conditioned value-of-information improves mean utility by 1.111 over the same planner with a uniform prior (bootstrap 95% interval 0.833–1.400). Scope-aware reopening strongly improves on reopen-on-any-change policies, while comparisons with a conservative never-reopen policy remain compatible with zero in both registered regimes. Targeting verification to unresolved decision ambiguity reduces scalarized regret by 0.142 (0.100–0.187) relative to matched-budget random verification. Full transformation-chain checking detects all 200 constructed invalid chains, including 68 deep splices, with no false positives on 200 honest chains. Decision-coupled acquisition improves utility by 2.146 (1.976–2.299) over pure information gain, but a stronger deterministic proxy absorbs most of that margin. Typed reminting improves utility by 2.264 (1.717–2.825) in the mixed-transport regime and ties re-derivation exactly when reminting has no value.

The bounded conclusion is not that a particular memory architecture or policy is universally superior. Relations that determine whether information is applicable, transportable, or decision-relevant can change scientific decisions even when factual payloads are matched; when a stronger donor supplied with the same structured state ties or nearly ties the proposed policy, algorithmic novelty is correspondingly narrowed. All headline studies are synthetic. Real scientific-agent transfer, necessity or sufficiency of the six axes, and a minimal scientific-state schema remain unestablished.

## 1. Introduction

A scientific agent does not use facts in isolation. A failure can apply only under a particular representation. A certificate can survive one transformation but not another. A highly uncertain quantity can be irrelevant to the action currently under consideration. Evidence can remain accurate while no longer carrying the responsibility required by a new decision.

These distinctions are often discussed under memory, provenance, uncertainty, active acquisition, or typed state. The present question is narrower and experimentally testable:

> If two decision procedures receive the same factual world, can an explicit relation between a fact and its scientific role change the resulting decision?

We answer this through six exact-synthetic studies. Each freezes a world, decision problem, comparator, and scoring rule. Primary non-oracle arms see matched factual information; the manipulated object is the relation that makes some facts applicable, reusable, or decision-relevant. Each family contains a no-value or hostile regime so that a mechanism is not rewarded merely because the benchmark was built around it.

### 1.1 Contributions and evidence boundary

The paper makes three bounded contributions.

1. **Matched-information evaluation.** State arms are compared only after the underlying factual payload and resource opportunity are matched.
2. **Mechanism-isolation studies.** Six separately frozen studies identify situations in which type, applicability, decision relevance, lineage, or transport relations alter decisions.
3. **Donor-absorption discipline.** Stronger policies receive the same structured state; when they tie or nearly tie, the result is attributed to representation rather than to an unnecessarily broad policy-superiority claim.

The six studies were not preregistered as one omnibus hypothesis. Their post-completion synthesis is descriptive and mechanistic; it does not create a pooled effect, a minimal ontology, or cross-domain generality.

## 2. Matched-information design

The common design principle is information parity. Treatment and primary comparator receive the same underlying facts, costs, resources, and non-oracle access. They differ in whether a relation between those facts and the current scientific decision is represented explicitly.

This restriction matters. A method that wins because it sees more semantic information has not isolated the value of epistemic structure. Likewise, a policy that beats only a weak baseline should not retain a broad algorithmic novelty claim after a stronger donor receives the same structured inputs.

The six studies were frozen and executed separately. We therefore report their original outcomes at native scales. Bootstrap intervals reconstructed from fixed-seed paired differences are secondary uncertainty summaries; exact constructed-chain studies are reported as complete counts rather than population estimates.

## 3. Type changes acquisition under an otherwise identical planner

The first study considers a layered scientific interface with type-dependent feasibility. Both arms use the same myopic value-of-information planner over the same graph, costs, and known facts. One arm conditions feasibility on the declared interface type; the other replaces that prior with a uniform prior.

Across 300 frozen episodes, mean utility is 3.291 with the type-conditioned prior and 2.180 with the uniform prior. The paired difference is 1.111 with a bootstrap 95% interval of 0.833 to 1.400. The arms tie on 57.7% of episodes, showing that the type field matters only where it changes the selected acquisition or commitment path.

The result is not a new value-of-information algorithm. It isolates type as decision-relevant information under an otherwise unchanged planner.

## 4. Applicability scope prevents severe over-reopening

The second study attaches each failure record to the context in which it remains scientifically applicable. Some context coordinates are deliberately irrelevant to the truth of the stored failure. A scope-aware policy reopens the failure only when an in-scope coordinate changes.

Against policies that reopen on any context change, scope-aware reopening improves mean round utility by 6.973 (95% interval 5.740–8.255) in the stale-matters regime and by 15.050 (13.624–16.451) in the regime where reopening is wasteful.

The stronger comparison is against never reopening. There the paired intervals cross zero in both regimes: 0.774 (-0.663–2.254) and 0.060 (-0.540–0.634). The supported conclusion is therefore asymmetric: scope prevents severe over-reopening in the constructed panels, but these experiments do not establish universal superiority over a conservative never-reopen policy.

## 5. Decision-relevant uncertainty is not uncertainty alone

The third study gives each arm the same verification budget over interval-valued costs. The treatment verifies quantities responsible for unresolved ambiguity in the current decision; the comparator verifies random uncertain quantities and then uses the same downstream estimator.

Mean scalarized regret is 0.110 for targeted verification and 0.252 for random verification. The paired regret reduction is 0.142 with a 95% interval of 0.100 to 0.187. Many episodes tie because much of the uncertainty cannot change the final ranking. The gain comes from avoiding verification that is uncertain but decision-irrelevant.

This result is narrower than a general active-learning claim. It identifies a scientific-state distinction between uncertainty magnitude and uncertainty that can alter the current action.

## 6. Evidence validity can depend on transformation history

The fourth study constructs 200 honest transformation chains and 200 invalid chains. Sixty-eight invalid cases contain a deep splice: the final hop is superficially consistent even though an earlier transformation invalidates the evidence path.

A full-chain rule detects all 200 invalid chains, including all 68 deep splices, and produces no false positives on the 200 honest chains. A final-hop-only rule misses the deep attacks.

Because the cases are exact constructions, these counts are not treated as independent population samples or as a cryptographic security estimate. The scientific point is structural: when earlier transformations can change the premises on which later evidence depends, validity is a path property rather than a property of the final hop alone.

## 7. Decision-coupled acquisition and donor absorption

The fifth study compares next-probe selection under matched priors, costs, and stopping rules. Two quantities are deliberately high-entropy but cannot affect the current action.

Pure information gain spends 36.6% of its probes on these decoys; the decision-coupled selector spends none. Mean utility is 9.266 versus 7.121, a paired difference of 2.146 with a 95% interval of 1.976 to 2.299.

A stronger deterministic proxy performs much closer. The paired difference relative to that proxy is 0.277 with a 95% interval of 0.119 to 0.412. This donor result changes the interpretation. Most of the large gain belongs to avoiding entropy-driven acquisition, not to a broad claim that the focal selector dominates reasonable decision-aware heuristics.

The residual contribution is the decision-role representation and the matched-information test that reveals policy absorption.

## 8. Reminting disappears when transport has no value

The sixth study examines evidence reuse after representation change under a shared certification budget. In a mixed-transport regime, typed reminting and transport achieve mean utility 9.421 compared with 7.157 for matched-budget re-derivation. The paired difference is 2.264 with a 95% interval of 1.717 to 2.825.

The decisive control removes the value of reminting. In that regime, the two methods tie exactly across all 200 episodes. The mechanism therefore vanishes when the represented distinction is irrelevant, as it should.

## 9. Synthesis: state value versus policy novelty

Across the six studies, the common result is not a ranking of policies. It is a boundary on information flattening. Removing a relation between a fact and its scientific role can change acquisition, reopening, verification, transport, or reuse decisions even when the factual payload is unchanged.

The benchmark also shows why strong donors belong in the main result. A typed failure state can matter even when an ideal planner reproduces the resulting allocation. A decision-coupled acquisition policy can look substantially better than information gain while losing most of its apparent novelty to a stronger proxy. In both cases, the correct scientific residual is smaller than the first comparison suggests.

Representation value and policy novelty should therefore be adjudicated separately.

## 10. Relation to neighboring work

Typed memory, provenance, uncertainty-aware planning, value-of-information, active acquisition, truth maintenance, and evidence transport are established research areas. The paper does not claim priority over those mechanisms.

The residual is a matched-information benchmark architecture for asking which scientific relations matter after factual payload and resource opportunity are held fixed, together with explicit no-value controls and strongest-donor subtraction. This positions the work as a mechanism/evaluation study rather than a universal state architecture.

## 11. Limitations

All six headline studies are synthetic. Exact truth and matched information make them useful for mechanism isolation, but they do not establish performance in natural scientific workflows or deployed agents. The six axes are neither proved independent nor proved necessary or sufficient, and their post-hoc synthesis is not evidence of a preregistered minimal ontology.

Effect scales differ across studies and should not be pooled. The bootstrap intervals are secondary analyses of fixed-seed episodes rather than independent replications. The applicability comparison with never reopening remains compatible with zero and is reported that way.

The decisive extension is a real-domain matched-information study in which competing systems receive genuinely equivalent scientific evidence while the epistemic bindings are manipulated or ablated prospectively. That extension is not required for the bounded mechanism claim made here.

## 12. Reproducibility and availability

The reviewer-facing release should expose each study's frozen protocol, exact or fixed-seed generator, comparator contract, outcome record, and paired analysis. The six studies should remain independently reconstructible rather than being collapsed into one pooled benchmark score.

The submission and supplementary archive should be anonymized for double-blind review. Identity-bearing repository links or named release artifacts should be separated from the anonymous review surface.

## 13. Conclusion

Scientific decisions can depend on more than factual payload. Across six exact-synthetic matched-information studies, explicit type, applicability, decision-role, lineage, and transport relations alter decisions in the regimes where those relations carry value. Strong donors and no-value controls simultaneously narrow the interpretation: the evidence supports a bounded claim about epistemic state, not universal policy superiority or real-agent transfer. The central discipline is to let structured state earn only the scientific residual that remains after information parity and donor absorption are enforced.