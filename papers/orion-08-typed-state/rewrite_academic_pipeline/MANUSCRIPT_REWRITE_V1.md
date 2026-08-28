# Epistemic Bindings in Scientific Decision-Making: Six Matched-Information Mechanism Tests

## Abstract

Scientific decision systems can retain the same factual information while differing in how that information is bound to type, applicability, uncertainty, transformation history or downstream decisions. We test whether such **epistemic bindings** change decisions when the visible factual world is otherwise matched. Six separately frozen exact-synthetic studies isolate type-conditioned priors, applicability scope, decision-relevant uncertainty, transformation lineage, decision-coupled acquisition and remint obligations. The studies are synthesized after completion as a benchmark taxonomy; they are not pooled into one universal effect.

The results show both value and absorption. Type-conditioned value-of-information improves mean utility by 1.111 over the same planner with a uniform prior, with a bootstrap 95% interval of 0.833 to 1.400. Scope-bound reopening avoids severe over-reopening under irrelevant context changes, but its intervals relative to a conservative never-reopen policy cross zero in both registered regimes. Targeting verification to unresolved decision ambiguity reduces scalarized regret by 0.142, with a 95% interval of 0.100 to 0.187, relative to matched-budget random verification. Full transformation-chain checks detect all 200 constructed laundering chains, including 68 deep splices, with no false positives on 200 honest chains. Decision-coupled acquisition avoids decision-irrelevant high-entropy probes and improves utility by 2.146, with a 95% interval of 1.976 to 2.299, over pure information gain, although a stronger deterministic proxy absorbs most of that margin. Typed reminting improves utility by 2.264, with a 95% interval of 1.717 to 2.825, in the mixed-transport regime and ties re-derivation exactly when reminting carries no value.

The contribution is a matched-information evaluation design rather than a priority claim for typed memory, provenance or value-of-information. The evidence supports a bounded principle: relations that determine whether information is applicable, transportable or decision-relevant can change scientific decisions even when the factual payload is fixed. All headline studies are synthetic; real scientific-agent transfer remains unestablished.

## 1. Introduction

A long-lived scientific workflow stores more than propositions. A failed candidate can be relevant only under one representation. A certificate may survive one transformation but not another. An uncertain resource coordinate may matter only if resolving it can change the current choice. A piece of evidence may be current yet irrelevant to the responsibility now being asked of the system.

These distinctions are increasingly represented in agent memory, provenance systems and decision-support tools. The question studied here is therefore not whether structured state is a new idea. We ask a narrower experimental question:

> When factual information is held fixed, which decisions change because relations such as applicability, lineage and decision relevance are represented explicitly?

Six exact-synthetic studies answer different parts of this question. Each study was frozen separately and has its own comparator and failure regime. Their synthesis into a common taxonomy occurred after the experiments. This chronology matters because the benchmark should not be read as a six-component preregistered theory test.

## 2. Matched-information evaluation

The common design principle is to hold the factual world fixed between primary non-oracle arms and vary the epistemic relation used by the decision rule. Strong comparators receive the same visible information and decision budget. Where a stronger known decision procedure can absorb an apparent gain, that absorption is retained rather than hidden.

Every family also contains a hostile or no-value regime. A scope mechanism should not help when no relevant scope changes. Transport metadata should not help when reminting is unnecessary. Decision-aware acquisition should ignore facts that are uncertain but cannot affect the decision. These controls are essential because a mechanism that wins in every constructed setting is difficult to distinguish from a benchmark designed around the method.

For stochastic generators, paired differences are reconstructed from the original fixed seeds and reported with bootstrap intervals as secondary uncertainty summaries. The original frozen outcomes remain the primary record. Exact constructed-chain studies are reported by complete counts rather than pseudo-statistical intervals.

## 3. Type information changes otherwise identical acquisition decisions

The first study considers a layered scientific interface whose unknown transitions have type-dependent feasibility. Two arms use the same myopic value-of-information algorithm over the same graph, costs and known facts. The only difference is whether the feasibility prior depends on the declared interface type or is replaced by a uniform prior.

Across 300 frozen episodes, mean utility is 3.291 with type-conditioned priors and 2.180 with the uniform prior. The paired difference is 1.111 with a bootstrap 95% interval from 0.833 to 1.400. The arms tie on 57.7% of episodes, showing that the type information matters only where it changes the selected acquisition or commit path.

This result does not introduce a new value-of-information algorithm. It shows that type information can be decision-relevant to an otherwise identical planner.

## 4. Applicability scope mainly prevents unnecessary reopening

The second study attaches a failure record to the context in which it is valid. Some context coordinates are deliberately irrelevant to the truth of that failure. A scope-aware rule reopens only when a coordinate within the recorded applicability scope changes.

The strongest contrast is against policies that reopen on any change. Scope-aware reopening improves mean round utility by 6.973, with a 95% interval of 5.740 to 8.255, in the stale-matters regime and by 15.050, with an interval of 13.624 to 16.451, in the regime where reopening is wasteful.

The comparison with never reopening is more cautious. The paired intervals cross zero in both regimes: 0.774 with an interval of -0.663 to 2.254 and 0.060 with an interval of -0.540 to 0.634. The supported conclusion is therefore that scope prevents severe over-reopening without a demonstrated penalty relative to the conservative policy in these panels, not that it universally dominates never reopening.

## 5. Decision-relevant uncertainty is different from uncertainty alone

The third study gives each arm the same verification budget over interval-valued costs. The treatment selects facts contributing to unresolved decision ambiguity; the comparator verifies random uncertain facts and then uses the same downstream estimator.

Mean scalarized regret is 0.110 for targeted verification and 0.252 for random verification. The paired regret reduction is 0.142 with a 95% interval from 0.100 to 0.187. Most episodes tie because many uncertainties do not affect the final ranking. The gain comes from avoiding a minority of costly verification choices.

The result is not a general theorem about active learning. It isolates one distinction that matters to scientific state: an unknown quantity can be large while having no effect on the current decision.

## 6. Evidence validity can depend on the whole transformation path

The fourth study constructs honest and invalid transformation chains. Some invalid evidence is spliced into an earlier stage while the final hop remains superficially consistent.

A full-chain transport rule detects all 200 invalid chains, including all 68 deep splices, and produces no false positives on 200 honest chains. A final-hop-only rule misses the deep attacks.

The construction is exact and synthetic. It is not a cryptographic security result. Its scientific point is that evidence validity after a sequence of transformations is a path property when earlier transformations can alter the premises on which later evidence depends.

## 7. Information gain can buy observations that cannot change the action

The fifth study compares next-probe selection under matched priors, costs and stopping rules. Two facts are deliberately high-entropy but decision-irrelevant. Pure information gain spends 36.6% of its probes on these decoys; the decision-coupled selector spends none.

Mean utility is 9.266 for decision-coupled acquisition and 7.121 for information gain. The paired difference is 2.146 with a 95% interval from 1.976 to 2.299. A stronger deterministic proxy performs much closer, with a paired difference of 0.277 and a 95% interval from 0.119 to 0.412. This absorption is important: most of the large advantage is against entropy-driven acquisition, not against every reasonable decision heuristic.

## 8. Reminting should disappear when it has no value

The sixth study examines evidence reuse after representation changes under a shared certification budget. In a mixed-transport regime, typed reminting and transport achieve mean utility 9.421 compared with 7.157 for matched-budget re-derivation. The paired difference is 2.264 with a 95% interval from 1.717 to 2.825.

The decisive control is the remint-unnecessary regime. There, the two methods tie exactly across all 200 episodes. This no-value control supports the mechanism interpretation: transport metadata helps when it distinguishes reusable from non-reusable evidence, and it vanishes when that distinction is irrelevant.

## 9. Synthesis and donor absorption

Across the six studies, the most stable common statement is not that one policy is superior. It is that flattening a relation between information and its scientific role can change a decision.

Two neighboring studies sharpen this conclusion by absorbing broader interpretations. Typed failure state can matter even when an ideal planner reproduces the resulting allocation policy; the state distinction, not the planner, is the residual. Likewise, a crossover policy that initially appears beneficial loses its advantage to a stronger model-selection donor in well-specified regimes.

The benchmark therefore separates **state representation value** from **policy novelty**. If a strong planner given the same structured state ties the proposed policy, the correct interpretation is that the state relation mattered and the allocation rule was donor-owned.

## 10. Limitations

All primary studies are synthetic. Exact truth and matched information make them useful for mechanism isolation, but they do not establish performance in real scientific workflows. The six axes are also not proved independent, necessary or sufficient, and the manuscript does not claim a minimal scientific-state schema.

The effect scales differ across studies and should not be pooled. The uncertainty summaries are secondary analyses of the original fixed-seed studies rather than independent replications. One scope comparison remains statistically compatible with a conservative never-reopen policy and is reported that way.

A real-domain matched-information study is therefore the decisive extension if a broader agent-performance claim is desired. Until then, the paper remains a mechanism and benchmark study.

## 11. Reproducibility and availability

The six study protocols, frozen generators, result records and paired analysis should be released as an anonymous, versioned benchmark package. The publication archive should expose the scientific task definitions, fixed seeds, comparator contracts and reproduction path without requiring readers to understand the development repository structure.

## 12. Conclusion

Scientific state can be decision-sensitive even when its factual payload is unchanged. Across six exact-synthetic tests, explicit type, applicability, lineage and decision-role relations alter acquisition, reopening, verification and transport decisions in the regimes where those relations carry value, while strong donors and no-value controls limit the interpretation. The result is a bounded matched-information benchmark for epistemic bindings, not evidence of universal benefit or real-agent transfer.