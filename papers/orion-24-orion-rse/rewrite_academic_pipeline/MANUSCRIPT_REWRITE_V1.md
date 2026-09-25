# Falsifiable Scientific Governance for Research Agents: A Specification-Separated Conformance Study

## Abstract

Research agents can generate hypotheses, retrieve literature, run experiments and draft interpretations faster than they can determine what those outputs scientifically warrant. We study a narrower object than autonomous discovery: a **fail-closed scientific-governance contract** for deciding when a candidate claim may be promoted, retained as negative, marked interaction-only, classified as donor-subsumed, or left `CANNOT_CHECK`.

The evaluation history is deliberately preserved because it changes the interpretation. A first preregistered mixed benchmark returned a negative terminal, but later analysis showed that both failing thresholds read the same rare discriminator and were unattainable over the protocol's own sampling support; the result is therefore reclassified `CANNOT_CHECK`, not positive or negative evidence about the contract. A balanced successor gives equal weight to seven scientific dispositions and yields zero false promotions and perfect disposition accuracy for the full contract versus 14.29% false promotion and 0.8571 accuracy for the strongest partial-review baseline. That benchmark is retained only as a semantic discriminator because the focal policy reused the same adjudication function as gold.

The central empirical authority is a third, specification-separated study. Twenty-eight explicit gold cases—four precedence variants for each of seven semantic strata—are frozen in a separate adjudication artifact before an independent policy implementation is evaluated. Policies receive only factual booleans, not case identity or gold labels. The full governance contract is correct on 28/28 cases with zero false promotions and full useful-discovery recall. `MULTI_REVIEW` is correct on 24/28 with 14.29% false promotion; every registered component ablation is worse. Two executions produce identical canonical output. Because the 28 cases are specification variants rather than independent population draws, the result is reported as exact conformance rather than a generalization rate.

The contribution is a falsifiable promotion contract and a benchmark-design lesson: a governance mechanism should be evaluated against an independently frozen specification, with valid discoveries scored so blanket abstention cannot win. Whether this specification improves open-ended real scientific research remains an external blinded-adjudication question.

## 1. Introduction

Scientific research is not equivalent to producing a plausible hypothesis or a positive result. A claim can fail because its apparent novelty belongs to prior work, its evidence supports only an interaction, a negative predecessor remains binding, the protocol changed after outcome, or the available evaluator lacks authority to close the question.

Research agents amplify these risks. They can search more ideas, but they can also generate more widened claims, forgotten negatives, same-evidence reinterpretations and self-certified “discoveries.” A useful governance layer must therefore separate candidate generation from scientific promotion.

We ask a falsifiable decision question:

> Can an explicit scientific-governance contract make more specification-conformant promotion decisions than strong partial-review contracts under matched information, while preserving every valid discovery in the registered cases?

The object is not prose quality, agent creativity or general research productivity. It is the **promotion decision**.

## 2. Governance contract

The contract treats each research atom as a bounded claim/question with a parent identity, nearest donors, protected discriminator, protocol identity, evidence receipts, evaluator identity, authority owner, scientific disposition, and stop/reopen conditions.

The disposition vocabulary includes:

- `SUPPORTED_RESIDUAL` for a bounded positive contribution not absorbed by a stronger donor;
- `SUBSUMED` when the apparent contribution is donor-owned;
- `INTERACTION_ONLY` when the evidence supports a joint effect but not a standalone component;
- `REDUNDANT_EQUIVALENT`;
- `OVERREACH_HARMFUL`;
- `NON_IDENTIFIABLE`;
- `CANNOT_CHECK`;
- negative/null states;
- `RETAIN_NEGATIVE` when later material does not justify reopening.

The contract is non-compensatory. A favorable signal on one coordinate cannot offset a missing hard scientific obligation on another.

## 3. Donor subtraction and protected chronology

Before novelty promotion, the nearest prior mechanisms are recorded and the candidate residual is classified as adopted, adapted, composed, deferred or subsumed. Positive evidence and novel contribution are separate coordinates.

The discriminator and terminal rules are frozen before protected outcomes. A material post-outcome change creates a new protocol identity. A negative result may motivate a successor but remains a negative result under its own identity.

This chronology is essential for recursive research systems. Without it, a system can revise the question, comparator and interpretation together until a failure appears to have been a successful step all along.

## 4. Negative history and reopening

Negative, null and donor-subsumed outcomes remain active scientific state. Reopening requires material new evidence or a changed regime. Re-reading the same evidence with a more favorable narrative is not sufficient.

This rule produces the main distinction between the full contract and the strongest partial-review baseline in the registered specification. Both systems can handle validity, preregistration, donor subtraction and interaction-only evidence. The full contract additionally distinguishes legitimate material reopening from same-evidence resurrection of a live negative.

## 5. Authority separation

Automated judges, verifiers and candidate models can evaluate evidence but do not automatically own scientific authority. Synthetic gold or a separately frozen adjudication specification can own a benchmark label; a real publication claim remains externally governed.

This separation prevents a system from becoming “correct” merely by implementing the same function that generates its own gold labels. It also explains why later external acquisition remains necessary for a claim about open-ended science.

## 6. Evaluation design

All policies receive the same factual case information and matched decision resources. The policy ladder includes a raw-positive rule, a reflection/checklist baseline, donor-aware review, interaction-aware multi-review, the full governance contract, and component ablations.

The primary safety endpoint is false scientific promotion. The productivity endpoint is useful-discovery recall among gold `SUPPORTED_RESIDUAL` cases. Full disposition accuracy is also reported. Including valid-positive retention prevents an always-reject policy from obtaining a perfect safety score.

The benchmark sequence contains three studies because the first two expose design defects that the third repairs.

## 7. First benchmark: an unattainable comparison gate

The first mixed benchmark uses held-out generated families with independently varied fact rates. The full contract produces zero false promotions and retains every valid discovery. The strongest partial-review comparator produces false promotion of 0.018375 and disposition accuracy of 0.981625.

The preregistered comparison nevertheless fails because the protocol requires comparator false promotion at least 0.05 and accuracy separation at least 0.08.

A later support analysis shows that these are not merely thresholds the realized sample happened to miss. Both gates read the frequency of the same single discriminator state, and the supremum of that state's prevalence over the protocol's declared sampling support is 0.042326—below both bars. The conjunction therefore had no positive reachable state before the seed was drawn.

The original terminal is retained. Its evidentiary interpretation is `CANNOT_CHECK`: the frozen instrument was unable to measure the proposed comparison. This result is neither rescued as positive nor reported as evidence against the contract.

## 8. Balanced benchmark: semantic distinction but circular implementation

A fresh balanced benchmark gives equal protected weight to seven dispositions: clean support, material reopening, retained negative history, donor subsumption, interaction-only evidence, `CANNOT_CHECK`, and negative evidence.

The full contract yields zero false promotions, disposition accuracy 1.0 and useful-discovery recall 1.0. `MULTI_REVIEW` yields false promotion 0.142857, disposition accuracy 0.857143 and useful-discovery recall 1.0.

However, the first implementation of the full policy directly invokes the same adjudication function used as protected gold. The result therefore shows that the intended semantics distinguish the full contract from its partial ablations, but it is too circular to serve as implementation-independent conformance evidence.

The benchmark is retained as diagnostic history, not hidden or promoted.

## 9. Specification-separated conformance benchmark

The third study is frozen after the circularity problem is identified. It separates specification from implementation.

Twenty-eight explicit cases are stored in an adjudication artifact: four precedence variants for each of seven semantic strata. Before a policy call, case identifiers, rationales, stratum labels and gold dispositions are removed. The policy receives only factual booleans. Every policy is independently implemented from the case table rather than by calling the gold function.

The cases include precedence conflicts—for example donor status versus interaction/history, evidence-validity failure, and negative evidence—so a policy must implement the full decision ordering rather than memorize one marginal rule.

The inference unit is the semantic stratum, not the individual case. The 28 rows are deterministic specification variants, not 28 independent population samples.

## 10. Results

The full governance contract is correct on all 28 registered cases:

- disposition accuracy: **1.0000**;
- false promotion: **0.0000**;
- useful-discovery recall: **1.0000**.

The strongest non-full comparator, `MULTI_REVIEW`, is correct on 24/28:

- disposition accuracy: **0.857143**;
- false promotion: **0.142857**;
- useful-discovery recall: **1.0000**.

`DONOR_AWARE_REVIEW` and `REFLECTION_CHECKLIST` are progressively worse, while `RAW_POSITIVE` false-promotes more than half of the registered nonpromotable cases. Every component ablation is worse than the full contract on at least one specification stratum.

Two evaluations produce identical canonical output, and the benchmark's terminal is attainable in both directions: among the seven implementations admitted to the graded slot, only the full contract clears every gate.

These values are exact conformance counts. They should not be interpreted as estimated accuracy on open-ended scientific research tasks.

## 11. What the conformance result establishes

The study supports a precise claim: **against the registered scientific-governance specification, the complete contract conforms more exactly than the tested partial review contracts without suppressing registered valid discoveries**.

It does not establish that the specification itself is the uniquely correct model of science. A different scientific authority could disagree with the frozen dispositions. It also does not establish causal improvement in real research productivity, novelty or truth.

This distinction turns an apparent agent-performance paper into a governance-conformance paper, which is the stronger claim actually supported by the evidence.

## 12. Relation to prior work

Preregistration owns prospective endpoint discipline. Truth-maintenance systems own dependency-aware belief history. Provenance systems own evidence lineage. Multi-agent debate, reflection and reviewer agents own iterative critique. Research-agent systems already own recursive generation and tool use.

The residual contribution is the integrated **scientific-promotion lifecycle** plus its falsifiable evaluation: donor subtraction, protected chronology, explicit negative-history semantics, non-identifiability, `CANNOT_CHECK`, authority separation, stopping and material-change reopening are scored as decision outputs rather than presented only as software features.

## 13. External-validity boundary

A prospectively frozen successor requires independently held research incidents, gold adjudication, thresholds and custody. Those external artifacts were not available in the later acquisition attempt, and zero external cases executed.

This absence does not weaken the internal conformance result, but it blocks any claim that the governance contract improves open-ended scientific decisions. Retrospective development incidents cannot substitute for prospectively unseen evaluator-held cases.

## 14. Reproducibility and venue framing

The release package should contain the contract, frozen specification cases, independently implemented policies, exact result receipt, replay hashes, and ablations. The JAAMAS-facing version should frame the contribution as agent governance and decision conformance rather than as autonomous-science superiority.

A named arXiv release and final current venue-package verification remain release gates; they do not justify widening the bounded claim.

## 15. Limitations

The central benchmark is specification-based and finite. The gold dispositions originate inside the research programme even though their artifact and implementation are separated. The study therefore tests conformance to a declared governance contract, not truth about a natural population. The component set may be incomplete, and different research institutions may choose different authority policies.

No claim is made about external reviewer agreement, causal reduction of false discoveries, real-world productivity, or general autonomous-agent safety.

## 16. Conclusion

Scientific governance for research agents should be evaluated as a falsifiable decision contract, not as a list of desirable principles. An initial benchmark failed because its comparison gates were unattainable; a balanced successor exposed an implementation/gold circularity; and a specification-separated third study repairs both defects. On the frozen 28-case specification, the full contract handles every registered disposition with zero false promotion and full valid-discovery recall, while partial review contracts fail on the distinctions they omit. The supported claim is conformance, not universal scientific superiority—and that narrower claim is exactly what makes the result auditable.
