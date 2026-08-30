# Deferred-Outcome Evaluation of AI-Assisted Scientific Decisions

## Abstract

AI-assisted scientific systems increasingly make decisions at frontiers where no answer key yet exists: which hypothesis to pursue, which representation to revise, which verification to buy, or which theorem obligation to attack next. Standard benchmarks are poorly matched to this setting because they normally construct tasks after the correct answer is known. Agreement among multiple systems is not a substitute: shared evidence, training data, infrastructure, or conceptual bias can make different systems agree for the same wrong reason.

We formalize **deferred-outcome evaluation**, a benchmark protocol in which the scientific question, decision-time evidence, scored decision coordinates, and outcome-resolution rule are frozen while the target remains unresolved. Each system commits its decision before observing the later scientific evidence that will score it. Agreement and disagreement are recorded as pre-outcome relations, not as correctness signals.

We demonstrate the complete lifecycle on one genuinely prospective exact quantum-compilation frontier. Two decision systems with materially different control mechanisms receive the same frozen evidence state and independently select regime characterization as the next scientific move. Later exact results satisfy the preregistered scorer for that choice. This is one prospective observation: it establishes operational feasibility of the protocol, not reliability, calibration, statistical independence, or the probability that agreement predicts later correctness. A retrospective encoding of the same historical item into the generic schema reproduces the decision but does not create a second sample.

The live study also exposes an integrity requirement: successful transport of a result cannot be equated with valid scientific content. Deferred-outcome evaluation must therefore preserve the exact evidence state presented to a decision system, including invalid historical content and later corrections. The contribution is a temporal evaluation contract for AI-assisted scientific decisions whose labels arrive later. Predictive validity requires a larger prospective series and remains open.

## 1. Introduction

Most AI benchmarks assume that the evaluator already knows what a correct output looks like. Scientific decision-making often violates that assumption. At a live research frontier, the useful decision may be a diagnosis of what is missing, a next experiment, a representation change, or a choice to stop and seek new evidence. Whether that decision was good may become knowable only after later scientific work.

Retrospective benchmark construction creates a leakage risk. Once the resolution is known, it is difficult to reconstruct the original frontier without allowing outcome knowledge to influence the question, available evidence, or scoring rule. Multi-system agreement does not solve the problem. Two systems can differ architecturally while sharing the same evidence substrate, vocabulary, pretraining, or blind spot.

We therefore treat evaluation as a temporal contract. Three objects are kept separate:

1. the unresolved frontier state available at decision time;
2. each system's committed decision from that state; and
3. later evidence that resolves how the original decision should be scored.

The paper makes three bounded contributions. First, it defines a typed prospective benchmark object and a deferred scorer that cannot be rewritten after the outcome. Second, it demonstrates the complete protocol on one historically prospective scientific frontier. Third, it identifies an evidence-integrity rule needed to reconstruct what a system actually saw when transport succeeds but scientific content is later found invalid.

The paper does **not** estimate reliability or validate consensus. With one primary prospective item, those quantities are not empirically identifiable.

## 2. Evaluation object

### 2.1 Prospective frontier item

A prospective item is admitted only while its resolving outcome is still unavailable. The item freezes the scientific question, the evidence state visible to the evaluated systems, the decision coordinates to be scored, the admissible terminal states, and the rule by which later evidence can resolve those coordinates.

Historical solved tasks can be useful controls. They are not prospective items because their outcome existed before the benchmark decision was frozen.

### 2.2 Committed decision

Each system binds its output to the same frozen item. A decision can include a diagnosis, a proposed next scientific move, or an explicit statement that the current evidence is insufficient. Decisions are committed separately before either system can inspect the other's output.

Different implementations do not imply independent evidence. The benchmark records shared substrates and common information surfaces so that architectural heterogeneity is not converted into a statistical-independence claim.

### 2.3 Deferred score

When admissible later evidence arrives, the original decision is evaluated under the original rule. A decision can become aligned, misaligned, unresolved, or unscorable if a defect in the item invalidates the scoring contract.

Agreement is deliberately absent from this definition. It is a relation between decisions, not a label supplied by the future outcome.

## 3. Lifecycle and fail-closed integrity

A valid item follows a fixed chronology:

> unresolved frontier → frozen evidence and scorer → independent decisions → committed records → later scientific resolution → bound outcome evidence → deferred score.

The chronology is substantive. Later evidence may score an earlier decision but cannot modify what information the system had, which coordinate was being evaluated, or which rule counted as success.

The protocol also distinguishes an incorrect decision from an invalid benchmark item. If the original item is later found malformed or scientifically uninterpretable, the item remains in the record with an unscorable or invalidated terminal. It is not deleted from the history merely because it is inconvenient.

Live use revealed a second distinction. An interaction layer can report successful transport even when the enclosed scientific content fails strict validation. Replaying the invalid bytes indefinitely preserves identity but preserves a defective evidence state; overwriting them erases history. We therefore preserve the original content and its failure record while allowing corrected content to be associated with the same scientific request. This is an auditability rule, not a security theorem.

## 4. First prospective scientific case

The first primary item concerns an unresolved exact quantum-compilation frontier. At the time of freezing, the scientific question is which structural layer explains the remaining optimization gap and which research move should follow from the available exact evidence.

The two evaluated systems use materially different decision machinery. One is a tool-capable host-driven research loop. The other is a typed campaign controller whose final decision path does not use free-form language-model reasoning. They nevertheless share the scientific evidence substrate and part of the project ontology. Their outputs therefore cannot be treated as independent replications.

Both systems commit to **regime characterization** as the primary next move. Subsequent exact work closes the relevant support-two behavior on the registered finite domains and establishes a structural regime predicate. Under the scorer frozen with the item, the selected next move is aligned with the later evidence.

The evidentiary interpretation is intentionally small. The case demonstrates that a frontier can be frozen before resolution, independently acted on, and later scored without reconstructing the task after the fact. It does not show that agreement is predictive, that either system is reliable across frontiers, or that the same protocol improves scientific productivity.

## 5. Why one prospective agreement is not validation

Consensus can arise from common contamination as easily as from independent insight. Shared sources can impose the same omission. Shared training corpora can encode the same default explanation. Shared infrastructure can expose both systems to the same preprocessing error. Even an explicit multi-agent debate can improve a decision procedure without turning consensus into a calibrated estimator of truth.

Deferred-outcome evaluation therefore records agreement before the outcome and postpones its interpretation. Only a future series with enough independent frontier items can estimate quantities such as per-system alignment, the frequency and value of disagreement, or the conditional behavior of agreement after shared-evidence controls are considered.

This design also makes negative future findings usable. If later items show that agreement is uninformative once shared evidence is controlled, the benchmark should reveal that result rather than reward agreement by construction.

## 6. Retrospective reconstruction is a control, not another sample

The historical case has also been translated into the generic typed benchmark representation. The translated item reproduces the original decision and is useful for checking that the schema can express the scientific object.

It contributes no additional prospective evidence. The underlying frontier, decision, and later outcome are the same event. Counting both representations as separate observations would inflate the evidence by duplicating one chronology.

## 7. Relation to existing evaluation approaches

Static supervised benchmarks provide labels at construction time. Self-consistency, debate, and ensemble methods use repeated or interacting outputs to improve decisions. Provenance systems preserve execution and artifact histories. Prospective study designs separate pre-outcome commitments from later observations.

Deferred-outcome evaluation combines these concerns around a different unit of analysis: a scientific decision made while its correctness is genuinely unresolved. The residual contribution is not a new consensus method. It is the contract that freezes the evaluand before the future label exists and prevents later agreement or hindsight from rewriting that evaluand.

## 8. Limitations and decisive next study

The current study contains one valid primary prospective item. It cannot support a population reliability estimate, calibration curve, comparative accuracy claim, or statistical-independence claim. The case also comes from one research programme, so scientific-domain transfer is untested.

The decisive next study is a larger prospective series spanning materially different scientific programmes. Items should be frozen before their outcomes, and shared evidence surfaces should be recorded explicitly. The series should retain disagreements, insufficiency decisions, invalid items, and unresolved outcomes rather than filtering them from the denominator.

## 9. Reproducibility and availability

A release package for this paper should contain the benchmark schema, the frozen first item, the two committed decisions, the later resolving evidence, the scorer, and the invalid-content recovery tests. The public artifact should make chronology and scientific semantics reconstructable without requiring readers to understand development-repository organization.

For a double-blind TMLR submission, the reviewer-facing artifact and manuscript should remain anonymous; a named preprint can remain a separate release surface.

## 10. Conclusion

Scientific decisions can be evaluated even when their answer keys do not yet exist. Deferred-outcome evaluation freezes an unresolved frontier before resolution, records decisions without converting agreement into authority, and scores them only when later admissible evidence arrives. The first prospective case establishes feasibility and exposes a necessary evidence-integrity rule, but it is intentionally too small for reliability claims. The value of the protocol must be decided by a larger prospective series that is allowed to show that agreement, disagreement, or the benchmark itself may be less informative than expected.