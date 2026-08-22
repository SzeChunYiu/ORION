# Deferred Outcome Scoring for Scientific Decision Instruments: A Benchmark Protocol and First Live Case

**Recursively refined V3 — 2026-08-22**  
**Current contribution class:** systems / benchmark definition  
**Stretch target after multi-item validation:** Nature Computational Science  
**Current target path:** npj Artificial Intelligence / multi-agent systems and evaluation venue

## Abstract

Scientific agents often make decisions before the relevant ground truth exists. Standard benchmarks assume an answer is already available, while model agreement can reflect shared bias rather than correctness. We introduce a benchmark protocol for **prospective scientific decisions with deferred outcome scoring**. A frontier item freezes an unresolved question, the exact evidence available at decision time, diagnosis and move coordinates, and a rule for how later scientific evidence can resolve those coordinates. Architecturally distinct instruments then record decisions independently. Agreement, disagreement and cannot-check are preserved as pre-outcome observations; each instrument is scored only after later work produces resolving evidence.

We implement the protocol with two ORION research instruments. Instrument A is a receipt-replay host-driven research harness with content-derived request identity, digest-bound results and create-only normal receipt persistence. Instrument B is a typed non-LLM campaign controller over a frozen manifest and receipt-transcribed observations with explicit non-authority semantics. A machine-readable benchmark schema binds frontier item, instrument decision and later deferred score without allowing agreement itself to confer authority. Benchmark V0 was frozen on an unresolved quantum-compilation frontier. Both instruments selected regime characterization as the primary next move, and later exact R6P/R6Q results are aligned with that move under the preregistered scoring rule. V0 is **one demonstration**, not a reliability estimate.

Live use also exposed a benchmark-integrity failure mode: a capability receipt could be syntactically successful while its task content was invalid. The current harness now converts declared parser failures to structured host-capability failure and supports reason-bound archival of successful-but-invalid receipt bytes before corrected re-service. We treat these recovery semantics as part of preserving the temporal identity of a frontier benchmark. The present paper establishes the benchmark and instrument contract, not predictive validity. A separately frozen multi-frontier study requiring at least 20 prospective decisions is needed to test whether agreement, disagreement or cannot-check states contain calibrated information about later scientific resolution.

---

## 1. Evaluating scientific decisions before the answer exists

A research system may need to decide what failed, which representation should be changed, what theorem obligation to attack or which expensive verification to purchase before the correct move is known. If evaluation begins only after ground truth exists, the benchmark no longer measures frontier decision-making. If several agents are asked the question simultaneously, their agreement is also not a substitute for truth: common training data, shared evidence and similar ontologies can produce correlated mistakes.

We therefore separate two events:

1. **pre-outcome measurement** — what did each instrument diagnose and choose from the same frozen evidence state?;
2. **deferred scientific score** — what did later evidence establish about each frozen decision?

The benchmark is designed so disagreement remains observable. It is not a consensus protocol.

### Benchmark question

> Given a live scientific frontier and an evidence state frozen before resolution, can heterogeneous decision instruments be compared now and scored later without rewriting the question after the outcome is known?

---

## 2. Typed frontier benchmark object

The implementation exposes three content-bound records.

### 2.1 Frontier item

A `FrontierDecisionItem` contains:

- item and programme identity;
- the unresolved scientific question;
- digest of the exact evidence state;
- admissible evidence references;
- diagnosis coordinates;
- move coordinates;
- a deferred-scoring rule;
- a freeze epoch;
- an item digest.

Primary frontier items require an explicit declaration that the relevant outcome is unknown at freeze. Historical resolved items may be controls, but they are not primary prospective evidence.

### 2.2 Instrument decision

Each `FrontierInstrumentDecision` binds to the item digest and the same evidence digest. It carries instrument identity, diagnosis, move, decision epoch and a `cannot_check` state. A cannot-check decision cannot simultaneously claim a diagnosis/move.

### 2.3 Deferred score

A later `FrontierDeferredScore` binds:

- the original item;
- one frozen instrument decision;
- the resolving evidence digest;
- the original scorer rule;
- resolution epoch;
- one of `ALIGNED`, `MISALIGNED`, `UNRESOLVED` or `INVALIDATED_ITEM`.

Agreement is not a field in the score. It is derived from the pair of pre-outcome decisions and analyzed separately.

This type separation makes one temporal error difficult to hide: later evidence can score the old decision, but it cannot silently rewrite the old item.

---

## 3. Two intentionally heterogeneous instruments

### Instrument A — receipt-replay host-driven research

The generic harness emits capability requests whose identity is derived from canonical request content. Requests and results validate their own digests, and a result is cross-bound to the request id/digest it answers. Completed interactions can therefore be replayed rather than silently re-issued as a new experiment.

Normal receipt persistence is create-only. Failed receipts may be archived before retry; successful receipts are not ordinarily mutable.

### Instrument B — typed non-LLM campaign control

The second instrument consumes a frozen campaign manifest and receipt-transcribed observations through typed decision/control modules rather than free-form LLM reasoning. Campaign state, decisions and transitions serialize all scientific/novelty/promotion authority-grant fields as false. Protected references are withheld under the declared custody checks until a registered release condition applies.

### What is shared and what differs

| Property | Instrument A | Instrument B |
|---|---|---|
| repository evidence | shared | shared |
| receipt substrate | shared | shared |
| ontology/project vocabulary | partly shared | partly shared |
| decision engine | tool-capable host / LLM-guided research loop | typed non-LLM controller |
| manifest hypothesis vocabulary | implicit in host reasoning | explicit and externally authored |
| natural-language reasoning in final decision path | yes | no |
| authority self-grant | no | no |
| causal/statistical independence | **not claimed** | **not claimed** |

Architectural heterogeneity is therefore bounded: the instruments differ materially in decision machinery but can still share upstream evidence and conceptual biases.

---

## 4. Benchmark lifecycle

A primary item follows this sequence.

1. **Admit unresolved frontier.** Confirm that the resolving outcome is not yet known to the benchmark operators under the declared record.
2. **Freeze evidence.** Bind evidence digest, admissible references, diagnosis/move coordinates and scorer rule.
3. **Run instruments separately.** Neither instrument reads the other's decision.
4. **Freeze decisions.** Persist raw decisions and derive `AGREE`, `PARTIAL`, `DISAGREE` or a cannot-check relation.
5. **Wait for scientific resolution.** No score is manufactured if the research remains unresolved.
6. **Bind later evidence.** Record the resolving receipt/commit/public source.
7. **Score each instrument independently.** `ALIGNED`, `MISALIGNED`, `UNRESOLVED` or `INVALIDATED_ITEM`.
8. **Analyze relation to later scores.** Only after a sufficient series exists.

An item is invalidated rather than dropped when a pre-outcome protocol defect makes the original scorer unusable.

---

## 5. Benchmark V0 — first live measurement

V0 was registered while an exact TARE-compilation frontier remained unresolved. The question asked which epistemic layer was responsible for the remaining gap and which scientific move should follow.

Instrument A diagnosed a representation/regime-characterization problem and selected regime characterization with support-two closure as a complementary move. Instrument B selected the same primary move while withholding a representation revision whose obligation was not yet licensed.

The normalized pre-outcome relation was `AGREE` on the primary diagnosis/move coordinate.

Later work produced:

- R6P: exact support-two closure across the registered finite domains;
- R6Q: an exact finite-domain regime predicate.

Under the scorer rule frozen for V0, the selected move is `ALIGNED` with the later evidence.

This establishes that the benchmark lifecycle can be executed on a live scientific question. It does **not** establish

\[
P(\text{later aligned}\mid\text{AGREE}),
\]

because there is only one primary item.

---

## 6. Failure semantics are part of benchmark validity

Live operation exposed a subtle deterministic-replay problem. A host result could satisfy the outer capability schema while containing task content rejected by the strict scientific reasoner. If such a result were treated as ordinary success, deterministic identity would replay malformed content indefinitely; simply overwriting it would destroy the audit trail.

The current harness therefore distinguishes envelope success from task-content validity.

- Declared reasoner `ValueError`, `TypeError` and `KeyError` failures map to structured `HOST_CAPABILITY_FAILED` rather than an unstructured traceback.
- `archive_invalid_result(request_id, reason=...)` moves the original successful receipt bytes into an invalid archive with a reason sidecar.
- The original deterministic request identity becomes pending and can receive a corrected result.
- Regression tests verify corrected re-ingest while preserving the invalid receipt history.

This is not a security boundary and does not make the host trustworthy. Its benchmark role is narrower: **the evidence state seen by the scientific decision should remain reconstructable even when an interaction is later declared invalid.**

---

## 7. Relation to existing agent evaluation

### Static task benchmarks

Conventional agent benchmarks compare an output against ground truth available to the evaluator at task time. Q3 instead admits live research questions whose resolution is intentionally absent at freeze.

### Self-consistency and multi-agent debate

These methods commonly use repeated/model-to-model answers or debate to improve performance or estimate confidence. Q3 does not allow instruments to negotiate before measurement and does not interpret agreement as a score.

### Provenance and autonomous-science infrastructure

Provenance is a prerequisite for freezing the pre-outcome decision and later evidence. Q3 does not claim provenance itself. Its benchmark object is the **temporal coupling of independently recorded decision and deferred scientific score**.

### Multi-agent systems/frameworks

The contribution is not “two agents are better than one.” The instruments are deliberately heterogeneous and may disagree; the scientific question is whether their relation is informative after later resolution.

---

## 8. What remains unmeasured

The present evidence cannot answer the benchmark's eventual empirical question. A preregistered successor requires at least 20 prospectively admitted frontier decisions across at least three research programmes, with no single programme contributing more than half.

The intended measurements include:

- per-instrument later alignment;
- `P(ALIGNED | AGREE)` when counts permit;
- disagreement-resolution matrix;
- cannot-check calibration;
- shared-evidence-bias controls;
- manifest-coverage ablations;
- decision/evidence cost, with manifest construction reported separately.

A negative result is valid. If agreement loses predictive value after shared-bias controls, that is a substantive limitation of multi-instrument confidence rather than a failed benchmark.

---

## 9. Claim boundary

The current paper establishes:

- a typed prospective frontier-item / instrument-decision / deferred-score schema;
- two implemented decision instruments with explicit shared/different surfaces;
- one live V0 measurement frozen before its later resolving evidence;
- an auditable invalid-content recovery contract discovered through live use;
- a preregistered multi-frontier evaluation protocol.

It does not establish reliability, calibrated agreement, statistical independence, autonomous-scientist superiority, security/tamper-proofing, or results of the future multi-frontier series.

---

## Code and benchmark availability

The harness implementation, Q3 publication contract, frontier benchmark record types, V0 protocol/results, invalid-content recovery regression tests and reproduction instructions are committed in the ORION repository. Before journal publication, these artifacts should be tagged/deposited with a permanent identifier and the DOI inserted here.

## AI-assisted research and writing disclosure

The benchmark explicitly studies AI-assisted research and the manuscript was refined with language-model tooling. Such systems are not authors and do not confer correctness. Human authors remain responsible for benchmark design, scientific interpretation, literature claims and the final manuscript. Final disclosure wording should follow the target journal's current policy.
