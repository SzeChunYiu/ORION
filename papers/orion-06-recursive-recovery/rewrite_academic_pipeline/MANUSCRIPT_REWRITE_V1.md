# Negative Results as Research State: A Recovery Protocol for AI-Assisted Science

## Abstract

AI-assisted research systems are increasingly able to propose hypotheses, run analyses and revise their own plans. A less studied problem is what should happen after a candidate is refuted, absorbed by a stronger existing method, limited to a narrow regime or left unresolved by the available evidence. Treating every adverse result as a prompt to try again encourages post-outcome claim mutation; treating every adverse result as a terminal failure discards information that can determine a better successor question.

We present a recovery protocol in which each research episode freezes its scientific question, comparator, evidence contract and stopping rule before the result; records the outcome without overwriting earlier failures; and permits a successor only when the parent result identifies a specific unresolved obligation. We examine the protocol through a complete single-programme case study in exact quantum compilation. The sequence moves from donor saturation to an explanatory conjecture, two exact counterexamples, a finite support-two closure, a prospectively frozen prediction on a previously unread public Hamiltonian and finally an all-size normal-form theorem. Earlier failed conjectures remain failed throughout. Across seven additional recorded negative episodes, two successor mechanisms improve the relevant bounded objective, one result is correctly absorbed by prior work and four negatives remain unchanged.

The study does not establish that the protocol improves research productivity, reduces false novelty or outperforms ordinary scientific iteration. It establishes a narrower object: negative and absorbed results can be represented as persistent scientific state that constrains what successor question is licensed next. Cross-domain comparative evidence remains necessary for any broader claim.

## 1. Introduction

Research automation is often described as a loop of proposal, experiment, evaluation and revision. That description leaves an important ambiguity. When a candidate fails, what exactly is being revised? If the original hypothesis, its evaluation criterion and its failure record can all be edited together, a sequence of failed ideas can be rewritten after the fact into an apparently coherent positive trajectory.

Scientific practice already contains safeguards against this failure mode. Preregistration separates planned analyses from outcome-informed changes. Strong baselines prevent a weak comparison from being mistaken for a contribution. Negative results and counterexamples narrow the space of live explanations. Provenance and versioning preserve what was actually executed. The remaining design question is how these pieces should control an iterative research system after an adverse terminal.

We treat a research programme as a graph of **claim episodes** rather than one continuously edited hypothesis. Each episode has a fixed question, evidence boundary, comparator, evaluation rule and terminal state. A later successor is a new episode. It may be motivated by the parent result, but it cannot change what the parent result established.

This separation supports two goals. First, it makes research history auditable. Second, it turns negative evidence into a constraint on future work rather than a result to be forgotten.

## 2. Recovery contract

### 2.1 Freeze the evaluand before observing the result

A result-bearing episode records the scientific question, admissible data and tools, strongest registered comparator, resource definition, positive and negative controls, success/refutation criteria and stopping rule before the outcome is interpreted.

A later result may motivate a different question. It does not retroactively change the gate that judged the earlier one.

### 2.2 Give strong prior work first right of refusal

A candidate receives incremental scientific credit only after comparison with the strongest relevant known mechanism that can be given the same information and resource opportunity. If that mechanism explains or matches the apparent gain, the contribution is subtracted rather than rescued by changing the comparator.

This distinguishes two questions:

- Does a candidate beat a weak baseline?
- Does a scientific residual remain after the strongest relevant known method is given the same opportunity?

Only the second supports a claim of incremental mechanism value.

### 2.3 Preserve adverse outcomes as typed scientific state

The protocol distinguishes positive, negative, absorbed, mixed, saturated, lower-bound and unresolved outcomes. These labels are not claims of universal ontology; they encode different permissions for the next research move.

A refutation can motivate a search for the missing mechanism. An absorbed result motivates subtraction or stopping. A mixed result motivates regime characterization. Saturation within a registered class motivates either stopping or a new scientific question. An unresolved result motivates acquisition of the missing evidence rather than being counted as a negative observation.

### 2.4 Productive recovery

We call a recovery productive when four conditions are met:

1. the parent episode ends adversely, is absorbed, or remains unresolved;
2. the parent outcome identifies a specific open obligation;
3. the successor is registered separately and changes that obligation rather than the parent gate;
4. the successor yields a materially different validated object, such as a counterexample, explanation, regime boundary, prospective prediction or theorem.

A positive result found by unconstrained repeated search does not satisfy this definition.

## 3. A complete recovery trace in exact quantum compilation

The main case study is an exact quantum-compilation programme. We use it because exact referees and mathematical witnesses make the sequence unusually auditable. The compilation theorem at the end of the sequence is not the contribution claimed by this paper; it is the endpoint through which the recovery protocol can be inspected.

### 3.1 Saturation changes the scientific question

Several increasingly expressive exact candidate families collapse onto already available donor envelopes on the registered open instances. The resulting evidence does not justify another more complicated optimizer. It instead motivates a new question: why does unrestricted optimization repeatedly collapse onto low-support constructions?

This is the first important transition. Recovery changes the question only after the optimization residual has been exhausted under the registered comparison.

### 3.2 The first explanatory conjecture fails at a specific coupling mechanism

A support-dominance conjecture is then tested exhaustively over 688,041,472 local configurations without a violation of its local inequality. That local regularity is real, but the proposed global closure is not. An exact counterexample uses a shared coupling coordinate to reach cost 8 where the donor family requires 9.

The programme records both facts: the local dominance pattern and the global counterexample. The failure identifies the missing coupling mechanism and motivates a successor that explicitly represents it.

### 3.3 Repair exposes a converse mechanism

The repaired family closes the first counterexample but fails on a second exact construction. That construction spends a larger local support on one frame branch to reduce a different global cost, reaching cost 5 where the repaired donor requires 6.

The two counterexamples point in opposite directions. Together they show that the original low-support explanation omitted two complementary coupling currencies. They are retained as scientific results rather than treated as embarrassing intermediate drafts.

### 3.4 Finite closure remains finite

A support-two family then matches the unrestricted optimum on every registered finite domain, including all previously refuting cases. The programme still does not infer an all-size theorem from finite equality. The distinction between finite closure and mathematical generality remains explicit.

### 3.5 Prediction precedes exact opening

The next successor freezes a structural predictor and applies it to a previously unread public chemistry subject. The predicted regime is committed before the unrestricted exact referee is opened. The prediction is then confirmed on all 15 registered matchings.

This step matters because it changes the evidentiary role of the result: the structural rule is used prospectively rather than merely summarizing a panel already inspected.

### 3.6 The final successor is an all-size theorem

The remaining open obligation is whether support larger than two can ever be necessary. An analytic exchange argument proves that it cannot for the frozen compilation grammar. Together with an exact support-one counterexample, the endpoint is a sharp support-two normal form for arbitrary system size.

The scientific trace is therefore:

> donor saturation → explanatory conjecture → exact refutation → repaired conjecture → second exact refutation → finite closure → prospective prediction → all-size theorem.

The parent failures are not relabeled after the theorem appears.

## 4. Other negative outcomes do not all recover positively

A useful recovery protocol must allow a negative result to remain negative. Seven additional standalone adverse episodes have now been re-examined at the mechanism level. Two admit bounded successor improvements. One is correctly absorbed by a stronger known method. Four remain negative after the relevant mechanism tests.

This distribution is important. A system that always turns a negative result into a later positive one would be difficult to distinguish from outcome-driven search. Here, recovery can terminate with no incremental value.

Other programme examples illustrate why typed outcomes matter. In one case, a favorable proxy disappears under a fuller resource model. In another, different downstream resource projections reverse which candidate looks preferable. Several specialized policies beat weak controls but are matched once a stronger planning or model-selection donor receives the same information. These are not failed papers inside the case study; they are examples of subtraction doing its job.

## 5. What the case study establishes

The observed record establishes that:

- adverse and absorbed results can remain immutable while later successors are developed;
- successor questions can be separated from parent hypotheses in time and content;
- strong prior work can eliminate apparent incremental contributions without erasing the experimental record;
- exact counterexamples can determine the mechanism changed by the next successor;
- an iterative programme can terminate some lines as negative while progressing elsewhere.

The case study does not establish a causal benefit of the protocol. There is no matched counterfactual programme showing what would have happened under ordinary iteration, human-only research or a simpler donor-stopping policy. The evidence therefore cannot support claims about productivity, reliability or reduced false novelty across science.

## 6. Relation to neighboring approaches

The protocol depends on ideas with mature prior literatures. Provenance and experiment tracking make the history reconstructable. Preregistration separates pre-outcome decisions from later revision. Baseline methodology gives strong prior work first right of refusal. Falsification and negative-result publication treat counterexamples as scientific information. Agent reflection and self-correction provide mechanisms for generating successors.

The residual contribution is the combination of these ideas into a post-terminal transition contract: the parent terminal is immutable, a successor must answer a newly registered obligation, and later success cannot rewrite the evidentiary status of the parent.

## 7. Limitations and decisive next study

The present evidence is one deep programme. Its internal diversity does not make it cross-domain evidence. The decisive next study is therefore comparative rather than cosmetic: materially different research programmes should be run under matched recovery, naive-iteration and donor-stopping workflows, with predeclared measures of claim mutation, false novelty, productive recovery, evidence cost and terminal calibration.

A null result in that comparison would be informative. If simpler iteration performs equally well once strong baselines and provenance are enforced, the extra recovery machinery should be treated as unnecessary for that setting.

## 8. Reproducibility and availability

The episode protocols, result records, counterexamples, exact-replay artifacts and programme closure map are preserved in a versioned research archive. The submission package should expose a permanent release containing the scientifically necessary evidence and reproduction route while keeping development-only project organization outside the manuscript narrative.

## 9. Conclusion

Negative results are most useful to an automated research system when they remain part of its scientific state. The case study shows an auditable trajectory in which saturation, absorption and exact refutation constrain what successor question is asked next, while failed parents remain failed. The result is a bounded methodology and case study, not evidence that recovery machinery universally improves science. That broader claim requires a prospective cross-domain comparison.