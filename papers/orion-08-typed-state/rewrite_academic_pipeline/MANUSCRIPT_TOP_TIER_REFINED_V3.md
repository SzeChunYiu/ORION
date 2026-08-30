# Matched-Information Tests of Epistemic State in Scientific Decision Systems

## Abstract

Scientific decision systems can receive the same factual propositions yet act differently because those facts carry different information about applicability, transformation history, uncertainty, decision role, or reuse obligations. We study whether such **epistemic bindings** alter decisions when factual payload and non-oracle resource opportunity are otherwise matched.

Six separately frozen exact-synthetic studies isolate type-conditioned priors, applicability scope, decision-relevant uncertainty, transformation lineage, decision-coupled acquisition, and remint obligations. Type-conditioned value of information improves mean utility by 1.111 over the same planner with a uniform prior (paired bootstrap 95% interval 0.833–1.400). Scope-aware reopening strongly outperforms reopen-on-any-change policies, but comparisons with a conservative never-reopen policy remain compatible with zero in both registered regimes: 0.774 (-0.663–2.254) and 0.060 (-0.540–0.634). Decision-targeted verification reduces scalarized regret by 0.142 (0.100–0.187). Full-chain checking detects all 200 constructed invalid transformations, including 68 deep splices, with zero false positives on 200 honest chains. Decision-coupled acquisition improves utility by 2.146 (1.976–2.299) over pure information gain, but a stronger deterministic decision-aware proxy absorbs most of that margin, leaving 0.277 (0.119–0.412). Typed reminting improves utility by 2.264 (1.717–2.825) in the mixed-transport regime and ties re-derivation exactly when reminting has no value.

The studies were frozen separately and are synthesized only afterward; their effects are not pooled and the six axes are not claimed to form a minimal ontology. The bounded result is that relations governing applicability, relevance and transport can alter scientific decisions even when factual content is matched. Strong donor absorption and no-value controls narrow this to a state-representation contribution rather than universal policy superiority. All headline studies are synthetic; real scientific-agent transfer remains open.

## 1. Question and contribution

A scientific system rarely consumes facts without context. A failure may apply only under one representation. A certificate may survive one transformation and fail under another. A quantity may be uncertain yet irrelevant to the current decision. Evidence may remain accurate while no longer supporting the responsibility now being asked of it.

The experimental question is deliberately narrower than “does structured state help?”:

> When two decision procedures receive the same factual world and matched non-oracle opportunities, can an explicit relation between a fact and its scientific role change the decision?

The paper answers this through six mechanism-isolation studies. Each has a matched-information comparator and, where appropriate, a no-value or strongest-donor control. The design separates two claims that are often conflated:

1. **state value** — a scientific relation changes the decision under information parity;
2. **policy novelty** — a particular algorithm extracts value that a strong known decision rule cannot reproduce.

A state distinction may be scientifically real even when policy novelty is absorbed by a stronger donor.

## 2. Matched-information contract

Treatment and primary comparator receive the same underlying facts, costs, resources and non-oracle access. The manipulated object is the relation connecting a fact to the current decision: type, applicability scope, decision relevance, path validity, acquisition role, or transport obligation.

This contract prevents an easy explanation in which one arm simply sees more scientific information. It also prevents a weak baseline from lending authority to a broad algorithmic claim. Whenever a stronger donor can consume the same structured state, its result is part of the main evidence.

The six studies were not preregistered as one grand unified experiment. They were frozen and executed separately and later synthesized as a taxonomy. Their native units and effect scales therefore remain separate. Bootstrap intervals are paired uncertainty summaries within fixed-seed studies, not cross-study replication intervals.

## 3. Type-conditioned acquisition

The first study holds the value-of-information planner fixed and changes only whether feasibility is conditioned on the declared interface type.

Across 300 frozen episodes, mean utility is 3.291 with the type-conditioned prior and 2.180 with the uniform prior. The paired difference is 1.111 with a 95% bootstrap interval of 0.833 to 1.400. The arms tie on 57.7% of episodes, showing that type matters only in cases where it changes the selected acquisition or commitment path.

The result isolates type as decision-relevant information. It is not a new value-of-information algorithm.

## 4. Applicability scope and the importance of the stronger control

A stored failure can remain applicable under some context changes and become stale under others. A scope-aware policy reopens only when an in-scope coordinate changes.

Relative to reopen-on-any-change, the scope-aware policy improves mean round utility by 6.973 (5.740–8.255) in the stale-matters regime and 15.050 (13.624–16.451) where broad reopening is wasteful.

The stronger comparison is never-reopen. There the intervals include zero: 0.774 (-0.663–2.254) and 0.060 (-0.540–0.634). The paper therefore does not state that scope-aware reopening universally dominates conservative reuse. The supported result is asymmetric: explicit scope prevents severe over-reopening in the constructed regimes where irrelevant context changes are common.

This correction is load-bearing because a paper that reports only the weaker reopen-any comparator would overstate policy novelty.

## 5. Decision-relevant uncertainty

The third study gives every arm the same verification budget over interval-valued costs. The treatment verifies quantities responsible for unresolved ambiguity in the current choice; the comparator verifies random uncertain quantities and uses the same downstream estimator.

Mean scalarized regret is 0.110 for targeted verification and 0.252 for random verification. The paired reduction is 0.142 with a 95% interval of 0.100 to 0.187.

Many episodes tie because much of the available uncertainty cannot alter the ranking. The result therefore distinguishes uncertainty magnitude from uncertainty that is causally capable of changing the decision under the registered rule.

## 6. Transformation validity is a path property

The fourth study contains 200 honest transformation chains and 200 invalid chains. Sixty-eight invalid chains contain a deep splice whose final hop is locally consistent even though an earlier transformation breaks the evidence path.

Full-chain validation detects all 200 invalid chains, including all 68 deep splices, and reports no false positives on 200 honest chains. A final-hop-only rule misses the deep splices.

These are exhaustive constructed counts, not independent population observations and not a cryptographic security estimate. Their scientific role is to establish a structural counterexample: final-hop validity does not imply path validity when earlier transformations can alter load-bearing premises.

## 7. Decision-coupled acquisition and donor absorption

The fifth study gives all arms matched priors, costs and stopping rules. Two high-entropy quantities are constructed so that learning them cannot affect the current action.

Pure information gain spends 36.6% of probes on these decoys; the decision-coupled selector spends none. Mean utility is 9.266 versus 7.121, a paired difference of 2.146 with interval 1.976 to 2.299.

A stronger deterministic decision-aware proxy closes most of the gap. The residual difference is 0.277 with interval 0.119 to 0.412.

The large first contrast therefore belongs mainly to avoiding entropy-driven acquisition. The smaller residual is the appropriate algorithmic comparison. The paper treats this donor absorption as a result rather than hiding it in a limitation section.

## 8. Reminting vanishes when the represented distinction has no value

The sixth study examines evidence reuse after representation change under a common certification budget. In a mixed-transport regime, typed reminting achieves mean utility 9.421 versus 7.157 for matched-budget re-derivation, a difference of 2.264 with interval 1.717 to 2.825.

The prespecified no-value control removes the reason reminting should help. In that regime the two methods tie exactly over all 200 paired episodes. This exact tie is the expected passing outcome, not an inconclusive comparison.

A useful mechanism should disappear when its defining information is irrelevant. The control provides that test.

## 9. Synthesis without pooled effects

Across six studies, explicit epistemic bindings alter acquisition, reopening, verification, transport and reuse decisions in regimes where the represented relation matters. The common scientific object is a boundary on information flattening: the factual payload can be identical while the decision changes because applicability or responsibility information differs.

The studies do **not** justify one pooled effect size. They differ in outcome scale, generated world, mechanism and scientific unit. Nor does the post-hoc six-axis synthesis prove that the axes are mutually independent, necessary, sufficient or minimal.

The strongest conclusion is therefore representational:

> scientific decision quality can depend on how facts are bound to their role, not only on which facts are present.

Policy novelty is assessed separately and narrows when an information-equivalent or stronger decision-aware donor ties or nearly ties.

## 10. Relation to prior work

Typed memory, provenance, truth maintenance, active acquisition, value of information, uncertainty-aware planning and evidence transport are established areas. The paper does not claim any one of those primitives as new.

The residual is a matched-information experimental architecture for testing whether a scientific relation remains decision-relevant after factual payload and resource opportunity are held fixed, together with explicit no-value controls and donor subtraction. This positions the contribution as a mechanism and evaluation study rather than a proposed universal memory architecture.

## 11. Limitations

All headline studies are synthetic. Exact truth and matched information make them useful for mechanism isolation, but they do not establish transfer to natural scientific workflows or deployed research agents. The six bindings are not a validated ontology. The bootstrap intervals summarize fixed-seed paired episodes and do not create external replication.

The decisive successor is a prospectively matched real-domain study in which competing systems truly receive equivalent scientific evidence while selected epistemic relations are manipulated without adding content. A null result must remain possible.

## 12. Reproducibility and TMLR release

The release should expose each study's frozen protocol, generator, matched comparator, strongest donor, exact or paired result object, and no-value control. Cross-study synthesis should remain separate from native per-study results.

For TMLR, the submission manuscript and reviewer-facing supplement remain anonymous. A named arXiv surface is separate and must not be used to identify the double-blind submission.

## 13. Conclusion

Facts are not the only state that matters to scientific decision systems. Across six separately frozen matched-information studies, type, applicability, decision relevance, transformation lineage and transport obligations change decisions in the regimes where those relations carry value. Null controls and stronger donors simultaneously narrow the claim: the evidence supports a bounded statement about epistemic bindings, not universal policy superiority or real-agent generalization. The central methodological discipline is to let structured state earn only the residual that remains after information parity, uncertainty reporting and donor absorption are enforced.