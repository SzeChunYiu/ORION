# Falsifiable Scientific Governance for Research Agents: A Specification-Separated Conformance Study

**ORION-24 — recursive academic-paper-pipeline final editorial master**  
**Scientific cut:** internal specification-separated governance conformance  
**Primary route:** JAAMAS  
**Specialist fallback:** agent-governance / empirical software-engineering venue  
**Authority:** `P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`; external validity open

## Abstract

Research agents can generate hypotheses, retrieve literature, run experiments and draft interpretations faster than they can determine what those outputs scientifically warrant. We study a narrower object than autonomous discovery: a **fail-closed scientific-governance contract** for deciding when a candidate claim may be promoted, retained as negative, classified as interaction-only or donor-subsumed, or left `CANNOT_CHECK`.

The evaluation history is preserved because it changes the interpretation. A first preregistered mixed benchmark returned a negative terminal, but later support analysis showed that both failing thresholds read the same rare discriminator and were unattainable over the protocol's own declared sampling support; the result is therefore `CANNOT_CHECK`, not evidence for or against the contract. A balanced successor gives equal weight to seven scientific dispositions and yields zero false promotions and perfect disposition accuracy for the full contract versus 14.29% false promotion and 0.8571 accuracy for the strongest partial-review baseline. That benchmark remains diagnostic because the focal policy reused the same adjudication function that generated gold.

The central empirical authority is a third, specification-separated study. Twenty-eight explicit gold cases—four precedence variants for each of seven semantic strata—are frozen in a separate adjudication artifact before an independently coded policy implementation is evaluated. Policies receive only factual booleans, not case identity, rationale, stratum or gold label. The full governance contract is correct on 28/28 cases with zero false promotion and full useful-discovery recall. `MULTI_REVIEW` is correct on 24/28 with 14.29% false promotion; every registered component ablation is worse. Two fresh executions produce identical canonical output. The benchmark's terminal is attainable in both directions: among the seven registered implementations admitted to the graded slot, only the full contract clears every gate.

The 28 rows are deterministic specification variants rather than independent population draws, so the result is exact conformance, not an estimated generalization rate. The contribution is a falsifiable promotion contract and benchmark-design discipline: hard scientific obligations remain non-compensatory, valid discoveries are scored so blanket abstention cannot win, and implementation is separated from the authority that defines gold. Whether this specification improves open-ended real science remains a prospectively blinded external-adjudication question.

## 1. Introduction

Scientific research is not equivalent to producing a plausible hypothesis or a positive result. A claim may fail because its apparent novelty belongs to a stronger donor, its evidence supports only an interaction, a live negative predecessor has not been materially reopened, the protocol changed after outcome, or the available evaluator lacks authority to close the question.

Research agents amplify these risks. They can search more ideas and run more analyses, but they can also generate more widened claims, forgotten negatives, same-evidence reinterpretations and self-certified discoveries. A useful governance layer must therefore separate candidate generation from scientific promotion.

We ask:

> Can an explicit scientific-governance contract make more specification-conformant promotion decisions than strong partial-review contracts under matched information, while preserving every valid discovery in the registered cases?

The object is the **promotion decision**. The paper does not evaluate creativity, prose quality, general research productivity or autonomous-science superiority.

## 2. Governance contract

Each research atom contains a bounded claim or question, parent identity, nearest donors, protected discriminator, protocol identity, evidence and resource receipts, evaluator identity, authority owner, scientific disposition, and stop/reopen conditions.

The disposition vocabulary includes:

- `SUPPORTED_RESIDUAL` — a bounded positive contribution not fully donor-owned;
- `SUBSUMED` — the apparent residual belongs to a stronger donor;
- `INTERACTION_ONLY` — evidence supports a joint effect but not a standalone atom;
- `REDUNDANT_EQUIVALENT`;
- `OVERREACH_HARMFUL`;
- `NON_IDENTIFIABLE`;
- `CANNOT_CHECK`;
- negative/null states;
- `RETAIN_NEGATIVE` — later material does not justify reopening a live negative.

The contract is non-compensatory. Strong provenance or many favorable checks cannot offset a missing hard scientific obligation.

## 3. Donor subtraction and protected chronology

Before novelty promotion, nearest prior mechanisms are identified and the candidate residual is classified as adopted, adapted, composed, deferred or subsumed. Positive evidence and novel contribution remain separate coordinates.

The discriminator and terminal rules are frozen before protected outcomes. A material post-outcome change creates a new protocol identity. A negative result may motivate a successor, but later success cannot rewrite the parent's original terminal.

This chronology prevents a recursive system from revising the question, comparator and interpretation together until every failure appears to have been a positive step.

## 4. Negative history and reopening

Negative, null and donor-subsumed outcomes remain active scientific state. Reopening requires material new evidence or a changed regime. Re-reading the same evidence through a more favorable narrative is insufficient.

This rule supplies the central distinction between the full contract and the strongest partial-review baseline in the registered specification. Both can check evidence validity, protocol freeze, identifiability, donor ownership and interaction status. The full contract additionally separates legitimate material reopening from same-evidence resurrection of a live negative.

## 5. Authority separation

Candidate models, automated judges and verifiers can evaluate evidence but do not automatically own scientific authority. A separately frozen specification can own a benchmark label; a real publication claim remains externally governed.

This distinction blocks two circular routes.

1. A policy cannot become correct merely by calling the same function that generates its gold label.
2. Same-programme agents cannot manufacture external scientific authority by agreeing with one another.

The external-validity question therefore remains separate even after exact internal conformance.

## 6. Evaluation contract

All policies receive the same factual case information and matched decision-check budget. The comparison ladder contains:

1. `RAW_POSITIVE` — promote any positive observation;
2. `REFLECTION_CHECKLIST` — add evidence/freeze/identifiability checks;
3. `DONOR_AWARE_REVIEW` — add donor subtraction;
4. `MULTI_REVIEW` — add interaction-only handling;
5. `ORION_RSE_FULL` — add negative-history and material-reopen semantics;
6. six component ablations.

The primary safety endpoint is false scientific promotion. The productivity endpoint is useful-discovery recall among gold `SUPPORTED_RESIDUAL` cases. Full disposition accuracy is also reported. The productivity endpoint prevents an always-abstain system from winning by rejecting everything.

## 7. P14A: a terminal whose positive branch was unreachable

The first benchmark uses held-out generated families with independently varied fact rates. The full contract produces zero false promotion, perfect disposition accuracy and full valid-discovery recall. `MULTI_REVIEW` produces false promotion and an accuracy deficit of 0.018375.

The preregistered comparison nevertheless requires comparator false promotion at least 0.05 and accuracy separation at least 0.08. Both gates fail.

A later support analysis shows that these gates are not merely missed by one unlucky draw. They read the frequency of the same single discriminator state. Its supremum over the protocol's declared sampling support is 0.042326, below both thresholds. The seven-gate conjunction therefore has no reachable positive state within the frozen support.

The original terminal remains unchanged. Its scientific disposition is `CANNOT_CHECK`: the instrument could not take the measurement encoded by its thresholds. It is neither rescued as positive nor cited as evidence against the governance contract.

The lesson is general. A threshold and the support of the statistic it reads must be frozen together; otherwise the protocol can freeze an outcome rather than a test.

## 8. P14B: semantic separation with circular gold

A fresh balanced benchmark gives equal protected weight to seven dispositions: clean support, material reopening, retained negative history, donor subsumption, interaction-only evidence, `CANNOT_CHECK`, and negative evidence.

The full contract yields:

- false promotion 0;
- disposition accuracy 1.0000;
- useful-discovery recall 1.0000.

`MULTI_REVIEW` yields:

- false promotion 0.142857;
- disposition accuracy 0.857143;
- useful-discovery recall 1.0000.

However, the original focal implementation invokes the same decision function used as protected gold. The benchmark demonstrates that the chosen semantics distinguish full and partial contracts, but it cannot serve as independent conformance evidence. Its result is retained as diagnostic history.

Additional audit also shows that only four of the advertised eight gates are discriminating over the registered arm set; the others are preconditions or unconditional in that benchmark. The gate count is therefore not treated as eight independent pieces of evidence.

## 9. P14C: specification-separated conformance

The third study is frozen after the circularity finding and separates specification from implementation.

`P14C_ADJUDICATION_CASES_V1.json` contains 28 explicit cases: four precedence variants for each of seven semantic strata. Before a policy call, the harness strips case identity, rationale, stratum and gold disposition. The policy receives only factual booleans. Every policy is coded independently from the case table.

The variants test decision precedence—for example donor status versus interaction or history, evidence-invalid cases, and negative evidence—so success requires the full decision order rather than one marginal rule.

The inference unit is the semantic stratum. The 28 rows are deterministic variants, not 28 independent samples, and no population interval is computed from them.

## 10. P14C results

The full governance contract is correct on all 28 registered cases:

- disposition accuracy: **1.0000**;
- false promotion: **0.0000**;
- useful-discovery recall: **1.0000**.

`MULTI_REVIEW` is correct on 24/28:

- disposition accuracy: **0.857143**;
- false promotion: **0.142857**;
- useful-discovery recall: **1.0000**.

`DONOR_AWARE_REVIEW`, `REFLECTION_CHECKLIST` and `RAW_POSITIVE` are progressively worse. Every component ablation fails at least one specification distinction that the full contract handles.

The V1 runner originally omitted the registered two-run byte-identity condition from its own terminal. A V2 adjudicator executes the unchanged scientific runner twice in fresh subprocesses and refuses authority unless all original gates pass and the complete result bytes agree. Both outputs have canonical SHA-256

`74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63`.

No case, gold label, policy, threshold, metric or result is changed by this correction.

## 11. Gate attainability and negative controls

A useful benchmark must allow the focal implementation to fail. Among the seven implementations the P14C protocol admits in the graded slot, one clears every gate and six fail at least one. The terminal therefore takes both values over the registered subject family.

The two thresholds inherited unchanged from P14A are also live on P14C. The relevant separation is 0.142857, above both the 0.05 difficulty bar and the 0.08 margin bar. The 0.08 bar fails for several component ablations, demonstrating refutation capacity.

This does not relabel P14A. It shows that a later benchmark can measure the original intended contrast without altering the earlier terminal.

## 12. What the conformance result establishes

The strongest supported statement is:

> Against the separately frozen 28-case governance specification, the complete contract conforms more exactly than the tested partial review contracts without suppressing registered valid discoveries.

The study does **not** establish that the specification is the uniquely correct model of science. Another scientific authority could disagree with its dispositions. It also does not establish causal improvement in real research truth, novelty, productivity or safety.

This narrower framing is stronger than an inflated autonomous-agent claim because the scientific object and its authority are explicit.

## 13. Relation to prior work

Preregistration owns prospective endpoint discipline. Truth-maintenance systems own dependency-aware belief history. Provenance owns evidence lineage. Reflection, reviewer agents and multi-agent debate own iterative critique. Research-agent systems own recursive generation and tool use. Authorization systems own separation of actor capability from permitted action.

The residual is the integrated **scientific-promotion lifecycle plus its falsifiable evaluation**: donor subtraction, protected chronology, negative-history semantics, non-identifiability, `CANNOT_CHECK`, authority separation, stopping and material-change reopening are scored as decisions rather than listed only as design principles.

## 14. External-validity boundary

A prospectively frozen external successor requires evaluator-held incidents, blinded gold adjudication, thresholds, trusted custody and conflict controls. The required acquisition artifacts were unavailable. Zero external cases executed.

The active authority remains P14C. The blocked external campaign is neither negative evidence nor an excuse to promote internal specification conformance into open-ended scientific validity.

The broader consolidated lifecycle-contract study likewise requires independent experts and an external gold derivation over pinned repositories. Those requirements remain open and do not merge into the present paper by prose.

## 15. Reproducibility and venue framing

The release should include:

- the governance contract and disposition semantics;
- P14A result and attainability adjudication;
- P14B circularity and gate-count corrections;
- P14C case specification, independently coded policies and ablations;
- V2 replay adjudicator and exact result hashes;
- blocked P14D acquisition record.

The JAAMAS-facing manuscript should frame the contribution as agent governance and decision conformance. A named arXiv surface and final current venue package remain release gates.

## 16. Limitations

The central benchmark is finite and specification-based. Its gold originates within the programme even though specification, policy implementation and replay adjudication are separated. The component vocabulary may be incomplete, and different scientific institutions can choose different authority policies.

No claim is made about external reviewer agreement, real-agent superiority, causal reduction of false discoveries, autonomous-science safety or research productivity.

## 17. Conclusion

Scientific governance for research agents should be evaluated as a falsifiable decision contract rather than a checklist of desirable principles. An initial benchmark fails because its comparison gates are unattainable. A balanced successor exposes gold/implementation circularity. A specification-separated third study repairs both defects.

On the frozen 28-case specification, the complete contract handles every registered disposition with zero false promotion and full valid-discovery recall, while partial review contracts fail on the distinctions they omit. The supported claim is exact internal conformance—not universal scientific superiority—and that bounded claim is what makes the result auditable.

---

## Editorial production note — not manuscript prose

Adoption must reconcile this master with `MANUSCRIPT.md`, `CLAIM_EVIDENCE_LEDGER.md`, `P14_ACTIVE_CLAIM_AUTHORITY_V1.json`, the P14A/P14B corrections and P14C V2 adjudication. Rebuild the JAAMAS/arXiv surfaces, bibliography, figures, PDF, visual audit, manifest and archive from the adopted bytes. Keep P14D and the broader lifecycle-gold programme visibly prospective and blocked.
