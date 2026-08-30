# Deferred-Outcome Evaluation of AI-Assisted Scientific Decisions

## Abstract

Scientific decision systems are often evaluated after the answer is already known. At a live research frontier, however, the relevant output may be a diagnosis of what is missing or a choice of what experiment, proof obligation, or regime to investigate next, while the evidence that can score that decision does not yet exist. Retrospective benchmark construction risks contaminating the question, evidence state, or scoring rule with outcome knowledge. Agreement among multiple systems is also insufficient: different systems may share evidence, ontology, training data, or blind spots.

We formalize **deferred-outcome evaluation** as a temporal benchmark contract. A frontier question, decision-time evidence, scored decision coordinates, and deferred scoring map are frozen before the resolving scientific outcome exists. Each instrument commits independently before later evidence is opened. Agreement is recorded as a pre-outcome relation, not as a correctness signal.

The current evidence is a three-frontier prospective case series. Two materially different instruments—a tool-capable host-driven research process and a typed deterministic controller—agree on the primary diagnosis and next move in all three valid units. Deferred outcomes do not validate that consensus. On two units both diagnoses align with the frozen scoring map; on the third, both diagnoses are wrong while both instruments nevertheless select the subsequently aligned next move. This gives a prospective counterexample to the claim that inter-instrument agreement validates a scientific diagnosis. With only three live frontier units, the study does not estimate reliability, calibration, inter-instrument independence, or the probability that agreement predicts correctness.

The benchmark also preserves contaminated candidate items and invalid-content states rather than silently deleting them. The contribution is a prospective evaluation contract for scientific decisions whose labels arrive later, together with an explicit demonstration that agreement and correctness are distinct evidentiary coordinates. Larger prospective series across independent scientific programmes remain necessary for predictive-validity claims.

## 1. Evaluation before the answer exists

Most benchmarks define a task after the evaluator knows the target. Scientific research often reverses that chronology. A system must decide what to do *while the scientific question is still unresolved*, and only later work establishes whether the original diagnosis or action was appropriate.

Reconstructing the frontier after the outcome is known creates a leakage problem. Outcome knowledge can influence which evidence is presented, how alternatives are worded, which decision coordinate is scored, or which terminal is declared correct. Multi-system agreement does not repair this problem. Two systems can agree because they share the same upstream evidence or conceptual omission.

Deferred-outcome evaluation therefore separates four objects:

1. an unresolved frontier question;
2. the evidence state available before resolution;
3. the committed decisions of the evaluated instruments; and
4. later evidence used by a scoring map frozen before that evidence existed.

The scientific unit is one prospectively frozen frontier question, not a receipt, run, matching, generated row, or pair of instrument outputs.

## 2. Prospective item contract

A valid item is admitted only while its resolving outcome is unavailable. Before either instrument can inspect the later scientific result, the benchmark freezes:

- the scientific frontier question;
- the evidence state visible to both instruments;
- the responsibility/diagnosis coordinate;
- the next-move coordinate;
- admissible abstention or unresolved states;
- the map from later scientific terminals to the scored coordinates.

The two instruments commit separately. Their pre-outcome relation—agreement, disagreement, or abstention—is recorded before the scientific outcome is opened.

Historical solved tasks can test schema expressivity, but they are not prospective units because the answer existed before the benchmark decision was frozen.

## 3. Instrument heterogeneity does not imply statistical independence

The two instruments are materially different. One is a tool-capable host-driven research loop. The other is a typed deterministic controller whose final decision path does not depend on free-form language-model reasoning.

They nevertheless share the scientific evidence substrate, parts of the project ontology, and upstream research history. The paper therefore makes no statistical-independence claim. Architectural heterogeneity is useful for testing whether one implementation artifact explains a decision, but it does not transform two outputs on one frontier into two independent scientific observations.

This distinction is central to the benchmark design. Consensus is a property of the instruments; correctness is supplied only by the deferred scientific outcome.

## 4. Three prospectively frozen frontier units

The authoritative series contains three valid units. Two earlier candidate units are retained as contaminated and excluded rather than replaced invisibly.

### 4.1 V0 — regime characterization is aligned

In the first unit, both instruments diagnose the remaining problem as one of representation/regime characterization and select regime characterization as the next scientific move. Later exact work establishes the corresponding finite-domain structural predicate and complementary support-two closure under the frozen scoring coordinates.

Both diagnosis and move are therefore deferred-aligned for this unit.

### 4.2 QG-19 — certificate silence remains open

The second unit asks about an objective just outside a known sufficient-cone face. Before the exact panel is opened, both instruments diagnose the state as certificate silence with sharpness still open and select a targeted exact outside-cone panel.

The later exact study finds no unrestricted-versus-support-two gap on the 53 frozen rows. Under the predeclared zero-gap branch of the scoring map, both the diagnosis and selected move align.

This is exact finite-panel evidence only. It does not enlarge the all-size sufficient cone.

### 4.3 QG-20 — agreement is wrong on diagnosis

The third unit is the key falsifier. Both instruments diagnose the reweighted boundary as objective-scoped and select a complete reweighted census. The later exact census over the complete frozen `n=1,2` domain instead supports the alternate diagnosis that the registered predicate is structurally invariant under the selected rescaling on that finite domain.

Thus both instruments **agree and both are diagnosis-misaligned**. Their selected next move—the complete reweighted census—is nevertheless aligned because it is exactly the experiment that discriminates the two possibilities.

This unit gives a prospective counterexample to the shortcut

`agreement -> diagnostic correctness`.

It does not estimate how often agreement is wrong.

## 5. What the three-case series supports

Across all three valid units, the instruments agree on the primary diagnosis and next move. Diagnosis aligns on two units and fails for both instruments on one. The selected next move aligns descriptively on all three.

These are case-series facts, not a reliability estimate. Reporting “100% move accuracy,” a binomial confidence interval, or a calibrated consensus probability would imply a sampling model that the live non-random frontier series does not provide.

The scientifically useful result is structural:

- agreement can be observed prospectively;
- correctness can be deferred without rewriting the original question;
- consensus and correctness can diverge;
- a wrong diagnosis can still select a scientifically useful discriminating action.

The last point is important for research-agent evaluation. A benchmark that scores only final diagnosis may miss the value of an action that resolves the uncertainty, while a benchmark that rewards agreement would falsely validate the wrong diagnosis.

## 6. Agreement non-identifiability

A descriptive re-reading of the three frozen units makes the agreement problem explicit. Agreement is observed in every unit, while deferred diagnosis alignment is two of three for each instrument. At observed agreement one, the corresponding non-identifiability calculation leaves mean accuracy unconstrained over the full `[0,1]` interval unless the deferred outcomes themselves are used.

The point is not the numerical estimate from three cases. It is that agreement supplies no independent authority for correctness in this series. The correctness information comes from later scientific resolution.

This motivates an evaluation principle: treat consensus as a feature to study, not as the gold label.

## 7. Contamination and invalid items are benchmark outcomes

Two originally proposed prospective slots became unsafe because result-oriented successor material was visible before the instrument freeze. They are retained as contaminated audit objects and excluded from the valid prospective denominator. They are not silently substituted with clean items and then forgotten.

The benchmark likewise distinguishes an incorrect instrument decision from an invalid benchmark item. If the pre-outcome evidence state is malformed or the scoring contract becomes scientifically uninterpretable, the item should fail closed rather than be retrospectively repaired in place.

This preservation rule is part of the measurement design. A benchmark that drops contaminated or invalid cases after outcome inspection can make its prospective chronology look cleaner than it actually was.

## 8. Relation to existing evaluation methods

Static supervised benchmarks assume labels exist at construction time. Ensemble, self-consistency and debate methods use repeated or interacting outputs to improve decisions. Prospective studies separate commitments from later outcomes. Provenance systems preserve chronology and identity.

The residual object here is a benchmark unit centered on a **live scientific decision whose correctness is not yet known**, with heterogeneous instrument outputs frozen before a later scientific result is generated. The paper does not claim generic delayed-ground-truth evaluation, consensus measurement, or multi-agent review as new.

## 9. Limitations and decisive next study

Three valid frontier questions are enough to establish protocol operation and to produce a prospective agreement/correctness counterexample. They are not enough to estimate reliability, calibration, disagreement value, domain generalization, or comparative performance. The questions also arise inside one research programme and share upstream scientific context.

The decisive extension is a substantially larger prospective series drawn from materially different scientific programmes, with shared evidence surfaces recorded explicitly. The denominator must retain disagreements, abstentions, contaminated items, invalid items and unresolved outcomes. Only such a series can support predictive statements about agreement or instrument reliability.

A negative result must remain possible. If agreement contributes no information after shared evidence is controlled, deferred-outcome evaluation should expose that rather than define consensus as success.

## 10. Reproducibility and TMLR release

The release package should expose the benchmark schema, all valid and contaminated item identities, pre-outcome evidence records, committed instrument decisions, deferred scoring maps, later scientific-result bindings and final scores. The artifact should make chronology reconstructable without requiring repository-development knowledge.

For TMLR, the submission manuscript and reviewer-facing supplement remain anonymized under the journal's double-blind policy. A named arXiv preprint is a separate release surface and must not be used to identify the anonymous submission.

## 11. Conclusion

Scientific decisions can be evaluated prospectively even when their answer keys do not yet exist. Deferred-outcome evaluation freezes the frontier, evidence and scorer before resolution and keeps agreement separate from correctness. In three prospectively frozen units, two heterogeneous instruments agree throughout, yet one deferred outcome shows both diagnoses wrong while their chosen experiment remains useful. That counterexample is the present paper's strongest result: consensus is not scientific authority. Predictive validity remains a future empirical question requiring a much larger independent prospective series.