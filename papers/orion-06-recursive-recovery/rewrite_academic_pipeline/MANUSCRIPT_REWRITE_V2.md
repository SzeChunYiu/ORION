# Recovering from Negative Results in AI-Assisted Scientific Search

## Abstract

AI-assisted research systems can propose hypotheses, run analyses, and revise plans, but iterative automation creates a governance problem after an adverse result. If a failed hypothesis, its comparator, and its success criterion can all be revised together after the outcome, repeated search can mutate failure into apparent success. If every negative result instead terminates the programme, the system discards information that may identify the next scientifically meaningful question.

We present a **claim-episode recovery protocol** in which each research episode freezes its question, evidence boundary, strongest registered comparator, evaluation rule, and stopping condition before interpretation. An adverse, absorbed, mixed, saturated, or unresolved terminal remains immutable. A successor is a new episode and is licensed only when the parent result identifies a specific open scientific obligation.

We examine the protocol through a complete single-programme case study in exact quantum compilation. The sequence begins with donor saturation, moves to an explanatory conjecture, records two exact counterexamples, obtains finite support-two closure, commits a prediction on a previously unread public Hamiltonian before opening the exact referee, and ends with an all-size normal-form theorem. None of the earlier failed conjectures is relabelled after the theorem appears. Seven additional adverse episodes provide a control on the temptation to manufacture positive recovery: two yield bounded successor improvements, one is absorbed by stronger prior work, and four remain negative.

The study does not establish that the recovery protocol improves scientific productivity, reduces false novelty, or outperforms ordinary iteration. It establishes a narrower object relevant to AI reasoning and autonomous research: negative and absorbed outcomes can be represented as persistent scientific state that constrains which successor question is licensed next. Cross-domain comparative evidence remains necessary for any stronger causal claim.

## 1. Introduction

Research automation is often summarized as a loop: propose, test, evaluate, revise. That description leaves a critical ambiguity. After a result fails, what exactly is allowed to change?

If the original question, comparator, resource definition, and success criterion are all editable after the outcome is known, a sequence of failures can be rewritten into a coherent positive story. The danger is not unique to AI, but automation can increase its scale because a system can generate and test many variants with little friction.

At the opposite extreme, treating every adverse result as terminal wastes scientific information. A counterexample can identify a missing mechanism. Donor saturation can show that another optimization variant is unlikely to contain the residual contribution. A mixed result can motivate regime characterization. An unresolved result can identify exactly which evidence must be acquired next.

We therefore model a research programme as a graph of **claim episodes** rather than as one continuously edited hypothesis. Each episode has a fixed evaluand and an immutable terminal. Later work may be motivated by that terminal, but it cannot change what the parent episode established.

The contribution has two parts. First, we define a post-terminal transition contract for AI-assisted scientific search. Second, we show through a deep exact case study that this contract can preserve failure while still enabling a sequence of scientifically distinct successors.

## 2. Claim-episode recovery contract

### 2.1 Freeze the evaluand

Before outcome interpretation, a result-bearing episode records the scientific question, admissible evidence, available tools, strongest registered comparator, resource definition, success and refutation criteria, controls, and stopping rule.

A later scientific insight can justify a new episode. It cannot rewrite the old gate.

### 2.2 Give strong prior work first right of refusal

A candidate earns incremental scientific credit only after the strongest relevant known mechanism is given the same information and resource opportunity. If that donor explains or matches the apparent gain, the candidate is classified as absorbed rather than rescued by weakening the comparator.

The distinction is between beating a convenient baseline and leaving a residual after strongest-donor subtraction. Only the latter supports an incremental mechanism claim.

### 2.3 Preserve typed adverse terminals

The protocol distinguishes several terminal classes because they authorize different next moves: negative, absorbed, mixed, saturated, lower-bound, positive, and unresolved.

A refutation can license a successor aimed at the missing mechanism exposed by the witness. An absorbed result can license subtraction, reframing, or stopping. A mixed result can license regime analysis. Saturation can license a different scientific question. An unresolved result licenses acquisition of the missing evidence, not a relabelled negative or positive conclusion.

### 2.4 Productive recovery

A successor counts as productive recovery only when:

1. the parent terminal is preserved;
2. the parent identifies a specific unresolved obligation;
3. the successor is frozen as a new episode with its own gate; and
4. the successor yields a materially different validated object, such as a counterexample, regime boundary, prospective prediction, or theorem.

Repeated search followed by choosing whichever positive result appears does not satisfy this definition.

## 3. Case study: exact quantum compilation

Exact quantum compilation provides an unusually transparent test bed because candidate mechanisms, counterexamples, and optima can be checked mechanically or mathematically. The final compilation theorem is not claimed as the novelty of this methodology paper; it serves as the endpoint through which the recovery trace can be audited.

### 3.1 Donor saturation changes the question

Several increasingly expressive candidate families collapse onto already available donor envelopes on the registered open instances. The correct interpretation is not that another optimizer variant should be tried indefinitely. The residual optimization claim has been saturated under the registered comparison.

This adverse terminal motivates a different question: why does unrestricted optimization repeatedly collapse onto low-support constructions?

### 3.2 A local regularity does not license global closure

The first explanatory successor tests a support-dominance conjecture. Exhaustive evaluation over 688,041,472 local configurations finds no violation of its local inequality. That regularity is genuine within the local test.

The global closure conjecture nevertheless fails. An exact construction uses a shared coupling coordinate to achieve cost 8 where the donor family requires 9. The programme records both facts: the local regularity survives, while the proposed global conclusion is refuted.

The counterexample identifies a missing coupling mechanism and thereby licenses a successor that represents that mechanism explicitly.

### 3.3 Repair reveals a converse coupling currency

The repaired family closes the first witness but fails on a second exact construction. The second witness spends larger local support on one branch to reduce a different global cost, reaching cost 5 where the repaired donor requires 6.

The two counterexamples act in opposite directions. Together they show that the original explanation omitted complementary coupling currencies. Neither failed parent is rewritten after this interpretation becomes available.

### 3.4 Finite closure is kept finite

A complete support-two family then matches the unrestricted optimum on every registered finite domain, including the earlier refuting cases.

The protocol does not promote this equality into an all-size theorem. The finite result closes the registered domains and leaves a new obligation: can support greater than two ever be necessary outside them?

### 3.5 A prospective prediction is committed before exact opening

The next episode freezes a structural predictor and applies it to a previously unread public chemistry subject. The predicted regime is committed before the unrestricted exact referee is opened. The prediction agrees with the exact outcome on all 15 registered matchings.

This result has a different evidentiary role from the earlier finite closure. It demonstrates prospective use on a frozen subject, not mathematical generality.

### 3.6 The final successor is an all-size theorem

The remaining obligation is mathematical. An exchange argument proves that support greater than two is unnecessary for the frozen compilation grammar. Together with an exact support-one counterexample, the endpoint is a sharp support-two normal form for arbitrary admitted size.

The programme trace is therefore:

> donor saturation → explanatory conjecture → exact refutation → repaired conjecture → second exact refutation → finite closure → prospective prediction → all-size theorem.

Later success never changes the status of the failed parents.

## 4. Negative outcomes do not always recover into positives

A recovery framework that always produces a positive successor would be difficult to distinguish from outcome-driven search. We therefore examine seven additional adverse episodes at the mechanism level.

Two yield bounded successor improvements. One is correctly absorbed by a stronger donor. Four remain negative after the relevant follow-up. This distribution is important because the protocol permits stopping and persistent failure.

Other programme records illustrate the same discipline. A favorable proxy can disappear under a fuller resource model. Different downstream resource projections can reverse a preference. Specialized policies can beat weak controls and then lose their apparent novelty when a stronger planner or model-selection donor receives the same information. These are not failures of the protocol; they are cases in which subtraction prevents a weak comparison from becoming a scientific claim.

## 5. What the case study establishes

The observed programme demonstrates that adverse terminals can remain immutable while successors are developed; that a successor can be tied to a specific obligation exposed by the parent; that strongest-donor subtraction can terminate apparent novelty; and that exact counterexamples can guide a later question without being erased by later success.

The case study also demonstrates a useful epistemic distinction for autonomous research systems: a negative result can be **state**, not merely a score. It can constrain which hypotheses remain live, which comparators must be included, and which successor questions are scientifically licensed.

These observations do not show that the protocol causes better science. There is no matched counterfactual programme using ordinary iteration, a human-only process, or a simpler donor-stopping rule.

## 6. Relation to neighboring approaches

Preregistration, provenance, experiment tracking, falsification, negative-result publication, strong-baseline methodology, truth maintenance, reflection, and self-correction each address parts of the problem. The paper treats them as donor ideas rather than claiming them individually as new.

The residual contribution is the **post-terminal transition contract**: a parent terminal is immutable; the strongest donor has first right of refusal; and a successor must answer a newly registered obligation instead of changing the old success criterion.

This framing places the work within AI reasoning and research-agent governance rather than as a claim of a new quantum-compilation method.

## 7. Limitations and decisive test

The evidence comes from one deep programme. Its multiple episodes are not independent research domains and do not support a cross-domain productivity estimate. The exact setting also makes refutation and closure unusually clean compared with many empirical sciences.

The decisive next study is comparative. Materially different research programmes should be prospectively assigned to matched recovery, naive-iteration, and donor-stopping workflows with predeclared measures such as claim mutation, unsupported novelty, productive recovery, evidence cost, and terminal calibration.

A null result would be informative. If strong baselines and provenance alone reproduce the benefits, the additional episode-transition machinery should not retain an incremental superiority claim.

## 8. Reproducibility and availability

The release should bind episode definitions, frozen gates, adverse terminals, counterexamples, donor comparisons, prospective commitments, exact replays, and the final theorem trace to one versioned archive. Reviewer-facing prose should use scientific episode descriptions rather than internal repository labels.

For AIJ, the manuscript should present the protocol as a general AI reasoning/governance object while keeping the quantum programme explicitly as the single deep case study. A named arXiv surface remains a separate release requirement and is not closed by this prose rewrite.

## 9. Conclusion

Negative results are most useful to an AI-assisted research system when they cannot be rewritten away. The claim-episode protocol preserves each adverse or absorbed terminal and permits a successor only when that terminal identifies a new scientific obligation. In the exact compilation case study, this produces an auditable path from saturation through counterexamples and prospective prediction to a theorem while every failed parent remains failed. The current evidence establishes a recovery representation and transition rule, not that the rule universally improves scientific productivity. That broader claim requires a prospective cross-domain comparison.