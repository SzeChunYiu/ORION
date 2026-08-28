# Deferred-Outcome Evaluation for Scientific Decision Instruments

## Abstract

Scientific decision systems often act before the evidence needed to judge their decisions exists. Conventional benchmarks assume that a correct answer is already available to the evaluator, while agreement among multiple systems can reflect shared evidence, shared training data or shared conceptual biases rather than correctness. We introduce a deferred-outcome benchmark for prospective scientific decisions. A benchmark item freezes an unresolved scientific question, the evidence available at decision time, the diagnosis and action coordinates to be scored, and the rule by which later evidence can resolve those coordinates. Each instrument records its decision before the outcome is known; agreement and disagreement remain descriptive pre-outcome observations; scoring occurs only after later scientific work produces admissible resolving evidence.

We demonstrate the full lifecycle on one historically prospective quantum-compilation frontier. Two decision instruments with materially different decision machinery receive the same frozen evidence state and independently select regime characterization as the primary next move. Later exact results support that move under the scoring rule fixed for the item. This is one valid prospective measurement, not an estimate of reliability or of the probability that agreement predicts later correctness. A retrospective conversion of the historical item into the current generic schema reproduces the original decision without creating a second prospective observation.

Live use also reveals an integrity requirement for deferred benchmarks: a transport or capability layer can report syntactic success while the scientific content is invalid. The benchmark therefore distinguishes envelope-level execution from task-content validity and preserves invalid historical bytes when corrected evidence is later served. The present contribution is a benchmark and systems contract for evaluating decisions whose truth arrives later. Predictive validity, calibration of agreement and reliability rates remain open until a larger prospective series is observed.

## 1. Introduction

Many scientific decisions are made at a frontier rather than against an answer key. A system may need to decide which hypothesis to pursue, which representation to revise, what theorem obligation to attack or whether additional verification is worth its cost while the correct next move is genuinely unknown.

This creates a benchmark-design problem. If the evaluator waits until the outcome is known and then reconstructs the original question, development knowledge can leak into the item. If several instruments are run simultaneously and their agreement is treated as evidence of correctness, correlated bias can be mistaken for validation.

We separate three objects:

1. the unresolved frontier state observed at decision time;
2. the decision made by each instrument from that frozen state;
3. later evidence that determines how the original decision should be scored.

The benchmark is therefore temporal. Later evidence is allowed to score the old decision, but it is not allowed to rewrite the old question or scoring rule.

## 2. Benchmark object

### 2.1 Prospective frontier item

A frontier item records the unresolved scientific question, the exact evidence state available to the decision instruments, the diagnosis and next-move coordinates, the admissible outcome states and a deferred-scoring rule. Primary items require evidence that the resolving outcome was unavailable when the item was frozen.

Historical resolved tasks can be useful controls, but they cannot be relabeled as prospective observations.

### 2.2 Instrument decision

Each instrument binds its decision to the frozen item and evidence state. A decision may contain a diagnosis, a proposed next scientific move or an explicit statement that the available evidence is insufficient. These objects are recorded separately for each instrument before either can inspect the other's output.

Architectural heterogeneity does not imply statistical independence. Instruments can differ in control logic while still sharing evidence, vocabulary or upstream infrastructure. The benchmark records such common surfaces rather than claiming independence from implementation difference alone.

### 2.3 Deferred score

When later evidence becomes available, each original decision is scored against the original rule. The score can be aligned, misaligned, still unresolved or invalidated if a defect in the original item makes the scoring contract unusable.

Agreement between instruments is not itself a score. It is a relation among their frozen decisions and can only be evaluated as a predictor after enough later outcomes exist.

## 3. Benchmark lifecycle

A valid prospective item follows a fixed sequence.

First, the frontier is admitted while its resolving outcome remains unknown. Second, the evidence state, scoring rule and decision coordinates are frozen. Third, the instruments make their decisions without seeing one another. Fourth, those decisions are committed. Fifth, the benchmark waits for later scientific resolution rather than manufacturing a label. Sixth, the resolving evidence is bound to the old item. Finally, each decision is scored under the rule fixed at the start.

If the original item is defective, it remains in the record with an invalidated status instead of disappearing from the denominator. This preserves the distinction between a bad decision and an unscorable benchmark item.

## 4. First prospective case

The first live item concerns an unresolved exact quantum-compilation frontier. At the time of the decision, the registered question is which scientific layer is responsible for the remaining optimization gap and which research move should follow.

One instrument uses a tool-capable host-driven research loop. The other uses a typed campaign controller without free-form language-model reasoning in its final decision path. They share the evidence substrate and part of the project ontology, so their agreement cannot be treated as independent replication.

Both instruments select regime characterization as the primary next move. Later exact work establishes a support-two closure on the registered finite domains and derives an exact structural regime predicate. Under the scorer frozen for the item, the selected move is aligned with that later evidence.

This case establishes that the benchmark lifecycle can operate on a genuinely unresolved scientific decision. It does not estimate a reliability rate. With one primary item, quantities such as the probability of later alignment conditional on agreement are not empirically identifiable.

## 5. Why agreement is not validation

Agreement can arise from several mechanisms that do not imply correctness. Two instruments may read the same sources, inherit the same blind spot or use different implementations of the same underlying conceptual model. The benchmark therefore records agreement before outcomes but withholds any interpretation of that agreement until later evidence accumulates.

This separation is particularly important for multi-agent evaluation. A consensus mechanism can be useful for decision-making while still being a poor estimator of truth. Conversely, disagreement can reveal a useful ambiguity even when neither instrument can yet be scored.

The current paper therefore treats agreement as a candidate predictor to be evaluated, not an authority signal.

## 6. Integrity of the pre-outcome evidence state

Deferred scoring depends on reconstructing what an instrument actually saw. Live operation exposed a failure mode in which an outer interaction record was syntactically successful even though the enclosed scientific content failed strict validation. Replaying that record indefinitely would preserve deterministic identity but also preserve an invalid evidence state; overwriting it would erase the historical record.

The corrected benchmark semantics therefore distinguish transport success from task-content validity. Invalid content is archived with its failure reason, and a corrected result can later be associated with the same scientific request without deleting the original bytes.

This mechanism is not a security guarantee. Its benchmark role is narrower: the evidence state used by a scientific decision should remain reconstructable even when an upstream interaction is later found invalid.

## 7. What is established and what remains open

The current evidence establishes a typed prospective frontier-item, decision and deferred-score contract; an implemented lifecycle; one valid prospective case; and an integrity rule for preserving invalid historical evidence during correction.

It does not establish predictive validity, calibrated agreement, statistical independence, security or a reliability estimate. A generic typed reconstruction of the historical item is retrospective and contributes no additional prospective sample.

The decisive next study is a larger series of independent frontier questions frozen before their outcomes. The planned series requires multiple research programmes and enough valid items to estimate per-instrument alignment, disagreement outcomes and the behavior of explicit insufficiency decisions. Shared-evidence controls must remain visible so that agreement is not rewarded for common contamination.

## 8. Relation to existing evaluation approaches

Static benchmarks compare outputs with truth available to the evaluator when the task is constructed. Self-consistency and debate methods use agreement or interaction to improve decisions. Provenance systems preserve execution histories. The present benchmark uses these ideas but asks a different temporal question: how should an unresolved decision be measured now and scored only when later scientific evidence arrives?

The contribution is therefore an evaluation protocol, not a claim that multiple instruments are intrinsically better than one.

## 9. Reproducibility and availability

The submission package should provide the benchmark schema, the frozen first item, the two instrument decisions, the later resolving evidence, the scoring logic and the invalid-content recovery tests in an anonymous archive. The historical chronology must be reconstructable without exposing development-only repository organization in the manuscript.

## 10. Conclusion

A scientific benchmark need not begin with an answer key. Deferred-outcome evaluation allows a live frontier question to be frozen before resolution, records instrument decisions without converting agreement into authority, and scores those decisions only when later evidence arrives. The first prospective case demonstrates feasibility but is intentionally too small for reliability claims. The value of the benchmark will be determined by the future multi-item series, including the possibility that agreement proves uninformative once shared biases are controlled.