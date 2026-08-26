# Q3 refinement round 1 — foundation, analogue calibration and review preflight

**Frozen manuscript:** `papers/orion-07-dual-instrument/MANUSCRIPT_V2.md`  
**Stretch:** Nature Computational Science  
**Fallback:** npj Artificial Intelligence  
**Relevant npj AI Collection:** “From Theory to Application: Advances in Multi-Agent Systems/Frameworks” (open; deadline 26 Mar 2027 as checked 2026-08-22)  
**Reviewer isolation:** `MUTUAL_BLINDNESS_NOT_GUARANTEED`.

## 1. Foundation spine

### Question

How can scientific decision instruments be evaluated on live frontier questions when the correct answer does not exist at decision time, and can disagreement remain an observable rather than being erased by consensus?

### Answer

Freeze the same unresolved scientific question and admissible evidence for architecturally distinct decision instruments, record their decisions independently, and score each decision only after later scientific work produces resolving evidence. A receipt-replay host instrument and a typed non-LLM campaign controller implement the first benchmark instance and expose the required provenance, authority and recovery surfaces.

### Decisive evidence chain

1. Deterministic/digest-bound capability requests/results and create-only receipt persistence.
2. Typed campaign state/decision/transition schemas with explicit non-authority fields and protected-reference custody.
3. Benchmark protocol in which AGREE/PARTIAL/DISAGREE/CANNOT_CHECK are all admissible and later scoring is separate.
4. V0: one frontier decision frozen before R6P/R6Q, later scored ALIGNED.
5. Live use exposed malformed-success receipt defects; current main repaired and regression-tested them.

### Boundary

V0 is one item. Q3 does not estimate reliability, predictive validity, independence, security, or autonomous-scientist superiority. The multi-frontier study is preregistered but not executed.

### Meaning

Scientific-agent evaluation needs temporal benchmarks where the outcome is genuinely unavailable at decision time. Deferred outcome scoring can separate “the instruments agreed” from “later evidence supported either instrument” and can preserve informative disagreement/cannot-check states.

## 2. Terminology ledger

| Canonical term | Meaning | Boundary |
|---|---|---|
| scientific decision instrument | a procedure that maps frozen evidence to diagnosis/move | not necessarily an autonomous scientist |
| Instrument A / host-driven receipt-replay lane | tool-capable host over the ORION harness | not statistically independent of Instrument B |
| Instrument B / typed non-LLM campaign controller | typed production controller over frozen manifest/receipts | manifest can be externally authored |
| prospective frontier item | item frozen before relevant resolving evidence exists | V0 only in current evidence |
| deferred outcome scoring | later alignment score bound to later evidence | not agreement-as-truth |
| AGREE/PARTIAL/DISAGREE/CANNOT_CHECK | pre-outcome relation between instruments | not correctness labels |
| ALIGNED/MISALIGNED/UNRESOLVED | later per-instrument score | not causal proof of decision quality |
| receipt integrity | auditability of declared interactions | not world truth or security |

## 3. Close-analogue calibration

### Analogue A — npj Artificial Intelligence, AgenticSciML (2026)

Observed evidence architecture:

- multi-agent framework contribution is paired with several scientific benchmark families;
- comparisons against single-agent and human-designed baselines are prominent;
- the paper can make a strong empirical framework claim because the evaluation object is large enough to estimate performance.

Q3 implication:

- one live frontier item cannot support an npj-level claim that agreement predicts correctness;
- Q3 should either (a) remain a benchmark-definition/instrument paper with strong systems validation, or (b) add a materially larger temporal evaluation series.

### Analogue B — Nature Machine Intelligence, benchmarking framework for embodied neuromorphic agents (2026)

Observed transferable functions:

- benchmarking papers make the **measurement contract** itself a contribution;
- tasks, metrics, platform/reproducibility and scaling path are explicit;
- a framework paper can be valuable before one universal winner exists, but the benchmark must be concrete and reusable.

Q3 adoption:

- formalize the benchmark-item schema, admissibility rules, deferred scorer and invalidation rules as a reusable resource;
- separate benchmark-definition evidence from predictive-validity evidence.

### Analogue C — npj AI multi-agent framework Collection

Implication:

- Q3 is thematically aligned with a current multi-agent systems/frameworks venue;
- fit does not remove the need for sufficient evaluation.

## 4. Editorial triage — Nature Computational Science

**Posture:** `TECHNICAL_CASE_NOT_REVIEW_READY` for a validation claim.

The central empirical question “does agreement/disagreement contain calibrated information about later scientific resolution?” is unanswered at `N=1`.

**Stretch-target blocker:** `ADD_DECISIVE_EVIDENCE` via the preregistered >=20 prospective series.

## 5. Editorial triage — npj Artificial Intelligence

**Posture:** `TECHNICAL_CASE_NOT_REVIEW_READY` as a predictive benchmark Article, but potentially `SEND_TO_REVIEW_POSITIONING_RISK` as a **systems/benchmark resource** if the implementation/adversarial validation package is expanded and the one-item evidence is kept explicitly demonstrative.

The current paper needs to make its reusable artifact the headline:

`frontier item schema + independent instrument contract + deferred scorer + invalidation/authority rules + adversarial systems tests`.

## 6. Reviewer lens 1 — VALIDITY

### Q3-R1-V1 — one item cannot answer the abstract's opening empirical question

- Class: `TECHNICAL_BLOCKER` for any calibration/prediction claim.
- Repair: `ADD_DECISIVE_EVIDENCE` (>=20 prospective items) or `NARROW_CLAIM` to benchmark definition / first measurement.
- Current correct route: `NARROW_CLAIM` for the present paper.

### Q3-R1-V2 — “architecturally distinct” needs measurable decomposition

- Class: `MAJOR_REPAIRABLE`.
- Concern: Instrument A and B share repository evidence and ontology; the paper should define what is actually different and what is shared.
- Resolution test: table of shared inputs, decision engine, manifest dependence, LLM dependence, storage substrate, authority semantics and failure modes.
- Repair: `CLARIFY_OR_RESTRUCTURE`.

### Q3-R1-V3 — benchmark item invalidation must be first-class

- Class: `MAJOR_REPAIRABLE`.
- Resolution test: formal schema/algorithm for item admission, pre-outcome digest freeze, later scorer, and `INVALIDATED_ITEM`; demonstrate it on resolved controls and malformed evidence controls even if they do not count as primary prospective items.
- Repair: `CLARIFY_OR_RESTRUCTURE` + systems tests.

## 7. Reviewer lens 2 — POSITIONING / SIGNIFICANCE

### Q3-R1-P1 — relation to self-consistency/debate/agent evaluation

- Class: `MAJOR_REPAIRABLE`.
- Concern: distinction is currently prose. Need a compact comparison table:
  - contemporaneous ground truth?
  - agents communicate?
  - agreement used as score?
  - outcome deferred?
  - CANNOT_CHECK admissible?
  - instrument architecture intentionally heterogeneous?
- Repair: `CLARIFY_OR_RESTRUCTURE`.

### Q3-R1-P2 — systems contribution is stronger than current title/abstract admits

- Class: `CLARITY_OR_REPORTING`.
- Concern: live discovery and repair of malformed-success receipt handling is a useful auditability result, but it feels appended rather than integrated into the benchmark validity contract.
- Resolution test: frame failure-recovery semantics as part of preserving a benchmark item's temporal identity and audit trail.

## 8. Reviewer lens 3 — REPRODUCIBILITY / BOUNDARY / READABILITY

### Q3-R1-R1 — formal benchmark schema missing from main paper

- Class: `MAJOR_REPAIRABLE`.
- Resolution test: one boxed schema/algorithm plus machine-readable example of V0 and one invalidated/control item.
- Repair: `CLARIFY_OR_RESTRUCTURE`.

### Q3-R1-R2 — experimental sample size and uncertainty are currently inapplicable

- Class: `CLAIM_RECALIBRATION`.
- Concern: do not introduce confidence intervals or apparent statistics around N=1. Label V0 demonstration only.
- Repair: maintain the current boundary.

### Q3-R1-R3 — data/code availability

- Class: `CLARITY_OR_REPORTING`.
- Resolution test: explicit code/benchmark-artifact availability, exact harness contract, and command to reproduce V0/control validation.

## 9. Editor synthesis

### Current strongest honest paper

A **benchmark-definition + research-instrument systems paper**, not a predictive-validity paper.

### Evidence blockers

- Nature Computational Science stretch: yes, >=20 prospective scientific frontier items.
- npj AI predictive-calibration claim: yes, same.

### Repairable without future evidence

- formal benchmark schema and item lifecycle;
- heterogeneous-instrument comparison table;
- adversarial systems/control validation;
- clearer related-work delta;
- stronger reproduction/data package.

These repairs can materially raise the paper even while leaving the empirical calibration question unresolved.

## 10. Round-one engineering scores

| Dimension | Score /10 |
|---|---:|
| problem_and_question | 8.6 |
| contribution_clarity | 7.4 |
| claim_evidence_alignment | 8.0 |
| technical_rigor | 7.9 |
| novelty_positioning | 7.4 |
| significance_or_field_advance | 7.1 |
| generality_and_boundaries | 5.8 |
| reproducibility_and_availability | 8.7 |
| figure_data_statistics_quality | 5.5 |
| writing_and_evaluability | 7.6 |
| venue_fit | 6.3 |

**Mean:** 7.30/10.

### Round-one terminal

- Nature Computational Science: `EVIDENCE_BLOCKED`
- npj Artificial Intelligence predictive Article: `EVIDENCE_BLOCKED`
- npj-level systems/benchmark-definition route: `CONTINUE_REFINEMENT__NARROWED_CLAIM`
