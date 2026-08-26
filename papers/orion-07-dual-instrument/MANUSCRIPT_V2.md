# Independent Scientific Decision Instruments with Deferred Outcome Scoring

**Manuscript V2 — 2026-08-22.** This paper defines and demonstrates a dual-instrument research-control benchmark. It does not claim that instrument agreement establishes correctness. `MANUSCRIPT_V1.md` is preserved as the historical version that documented the live defects before their subsequent repair.

---

## Abstract

Research agents increasingly operate on questions whose correct answer is not available when a decision must be made. Conventional ensemble evaluation is poorly matched to that setting: agreement among language models can reflect shared bias rather than truth, while ordinary benchmark accuracy assumes contemporaneous ground truth. We introduce a different experimental object: **prospective agreement between architecturally distinct scientific decision instruments, followed by deferred scoring against scientific outcomes that arise later**.

The first instrument is a receipt-replay research harness driven by a tool-capable host. External requests have deterministic content-derived identities; results are bound to exact requests and replayed from immutable normal receipts. The second instrument is a typed non-LLM campaign controller whose decision path consumes receipt-transcribed observations through production epistemic-control modules and cannot self-grant scientific authority. A frozen benchmark item presents both instruments with the same live frontier question while preventing either from reading the other's answer. `AGREE`, `PARTIAL`, `DISAGREE`, and `CANNOT_CHECK` are all admissible outcomes. Later scientific receipts score each instrument separately as aligned, misaligned, or unresolved.

Benchmark V0 was executed on an unresolved quantum-compilation frontier. Both instruments independently diagnosed the representation/regime-characterization layer and selected regime characterization as the next move; the typed controller additionally withheld a representation revision because its obligation remained unresolved. Later exact R6P/R6Q results were scored `ALIGNED` to the selected move. This is one first measurement, not an estimate of reliability. The live instrument use also exposed malformed-successful-receipt defects. Current main now maps invalid reasoner content to structured host-capability failure and provides explicit reason-bound archival of successful-but-invalid receipts, with regression tests showing that the deterministic identity can be safely re-serviced while the original bytes remain auditable.

Current multi-agent literature makes clear that agreement itself is only a weak and regime-dependent signal. We therefore preregister a stronger study requiring at least 20 live frontier decisions across multiple research programmes, deferred scoring, explicit disagreement and cannot-check analysis, and shared-bias controls. ORION-03's contribution is the benchmark and instrument contract that makes such a prospective measurement possible, not a claim that consensus confers scientific truth.

---

## 1. Scientific decisions before ground truth exists

Scientific research contains decisions that cannot be scored immediately. A researcher may need to decide which representation is responsible for a failure, which theorem gap to attack, whether a negative result is structural or merely benchmark-specific, or which expensive verification to perform next. The relevant ground truth may emerge only after days or weeks of subsequent work—and sometimes it never emerges.

This creates two problems for evaluating AI-assisted research.

First, ordinary task benchmarks supply a fixed answer at evaluation time. They therefore do not measure whether a research system's **frontier diagnosis** is useful before the answer exists.

Second, simply adding more language models does not solve the epistemic problem. Recent cross-model audits show that agreement can remain high on recurring errors, and multi-agent consensus can preserve correlated bias. Agreement may be empirically informative in some regimes, but it is not authority.

We therefore ask a narrower experimental question:

> If two materially different scientific decision instruments independently make a decision on the same unresolved frontier, does their agreement or disagreement contain information about what later scientific work establishes?

Answering that question requires the pre-outcome decision to be frozen and replayable, the instruments to be distinguishable in architecture, disagreement to remain observable, and later scoring to bind to evidence that did not exist at decision time.

---

## 2. Instrument A: receipt-replay host-driven research

The generic research harness separates the scientific kernel from capabilities it cannot own. The kernel emits a deterministic request; the host services it; the returned result is validated and persisted against the exact request.

### 2.1 Deterministic identity and binding

Request identity is derived from canonical request content. Request and result schemas recompute their own digests, and a result is cross-checked against the request id/digest it answers. Re-solving a completed workspace therefore re-derives the same requests and reuses existing receipts rather than silently creating a new experiment.

### 2.2 Normal immutability and explicit recovery

Ordinary successful receipts are persisted with create-only semantics and are not replaced in place. Failed results can be archived bytes-unchanged and retried.

Live use exposed a harder case: a host result could be syntactically successful at the capability-envelope level while containing task content that the reasoner's strict parser rejected. The historical V1 manuscript documented two consequences: an unstructured traceback and a deterministic identity pinned by a successful-but-invalid result.

Current main repairs both failure modes.

- `recursive_runner.py` catches reasoner `ValueError`, `TypeError`, and `KeyError` from invalid task content and maps them to the structured `HOST_CAPABILITY_FAILED` contract rather than allowing a raw traceback.
- `ResearchWorkspace.archive_invalid_result(request_id, reason=...)` provides an explicit audited override for a successful-but-invalid receipt. The original bytes are moved under `results/archived/*.invalid-*.json`, a reason sidecar is recorded, and the deterministic identity becomes pending again.
- `test_invalid_content_recovery.py` verifies both the structured failure and successful corrected re-ingest after archival.

This repair is intentionally narrower than mutable successful results: ordinary successful receipts remain immutable; invalid-content recovery requires an explicit request id and nonempty reason.

### 2.3 Authority and security boundary

Receipt integrity is not a proof of scientific correctness and the harness is not an operating-system sandbox. The instrument preserves/replays declared interactions and rejects malformed contracts; it does not prevent a dishonest host with full filesystem or evidence-control power from fabricating a false world. Scientific authority still requires evidence verification external to receipt integrity.

---

## 3. Instrument B: typed non-LLM campaign control

The second instrument runs over the same receipt substrate but has a different decision architecture. A frozen campaign manifest defines typed observations, candidate responsible layers, obligations, revisions and available computations. Production epistemic-control modules—not an LLM and not free-form natural-language reasoning—select the decision/control state.

This difference is deliberate. The point is not that one instrument is inherently superior; it is to create an architectural contrast that can disagree for reasons other than random sampling from the same model.

The typed controller also carries explicit non-authority constraints. Campaign states, decisions and transitions cannot self-grant scientific/novelty/promotion authority. Protected references remain unavailable until a validated release declaration is satisfied.

The manifest remains a limitation: its hypothesis vocabulary can be human/LLM-authored and may omit the correct explanation. Instrument B is therefore not independent of upstream scientific framing even if its per-cycle decision is non-LLM.

---

## 4. Benchmark definition

For a benchmark item, a protocol is committed before either instrument outcome exists.

It specifies:

1. the live frontier question;
2. the evidence both instruments may inspect;
3. normalized diagnosis and move coordinates;
4. the outcome vocabulary `AGREE/PARTIAL/DISAGREE/CANNOT_CHECK`;
5. later scoring coordinates and what evidence can resolve them;
6. disclosure of architectural/evidence dependencies.

The instruments execute separately. Their raw outputs are archived before comparison.

Later, once new scientific work exists, the deferred scorer binds the later receipt/commit and assigns each instrument independently:

- `ALIGNED`;
- `MISALIGNED`;
- `UNRESOLVED`;
- or `INVALIDATED_ITEM` if a pre-outcome protocol flaw made the item unscorable.

Agreement is not itself a score.

---

## 5. Benchmark V0: one live quantum-compilation frontier

V0 asks which epistemic layer is responsible for a remaining gap after a sequence of exact TARE-compilation results and what move should follow.

Instrument A, the host-driven lane, diagnoses `REPRESENTATION_REGIME_CHARACTERIZATION` and selects regime-predicate characterization with support-two closure as the complementary move.

Instrument B identifies `RESP:REPRESENTATION_REGIME_UNCHARACTERIZED` and selects `COMPUTE:REGIME_CHARACTERIZATION`. Its revision gate separately leaves `REV:SPLIT_REPRESENTATION_REGIME` unresolved because the predicate obligation is not yet licensed.

The normalized V0 outcome is therefore `AGREE` on the primary diagnosis/move coordinates.

Later ORION-Q work produces:

- R6P: exact support-two closure on the registered domains;
- R6Q: an exact finite-domain regime predicate.

Under the scoring rule frozen in the V0 protocol, the later coordinate is `ALIGNED` with the earlier move selection.

This is scientifically useful as a demonstration because the later outcome did not exist at decision time. It remains statistically only **one item**. V0 cannot establish that agreement predicts correctness.

---

## 6. Why agreement needs deferred calibration

Cross-model and multi-agent studies now provide a strong cautionary baseline. Agreement can correlate with correctness while remaining too weak or biased to serve as standalone confidence; multiple agents can share the same misconception, training-data artifact or option prior. Debate also does not reliably dominate simpler self-consistency/ensemble baselines.

ORION-03 therefore does not propose “agreement” as a confidence score. Instead it makes agreement/disagreement an independently frozen explanatory variable whose relationship to later scientific resolution must be measured.

The important quantities for a multi-item study are closer to

\[
P(\text{later aligned}\mid\text{AGREE})
\]

and

\[
P(\text{later aligned}\mid\text{DISAGREE/PARTIAL}),
\]

along with per-instrument alignment, cannot-check calibration, shared-bias controls and programme-stratified uncertainty.

---

## 7. Preregistered top-tier upgrade

`TOP_TIER_UPGRADE_PROTOCOL_2026-08-22.md` freezes the next research stage.

The primary target is at least 20 prospectively admitted frontier decisions, preferably 30 or more, across at least three materially different research programmes. Items must be admitted while the relevant outcome is genuinely unresolved. Already-known historical questions may appear only as controls.

The study records:

- AGREE/PARTIAL/DISAGREE/CANNOT_CHECK class;
- each instrument's deferred alignment;
- evidence and decision costs, including separate manifest-construction cost;
- calibration of withholding;
- disagreement-resolution matrix;
- shared-bias/adversarial controls;
- dependence of the typed controller on manifest coverage.

If the series cannot be collected without outcome leakage, ORION-03 remains a systems/benchmark-definition paper rather than being promoted to a predictive-validity study.

---

## 8. Related work boundary

**Multi-agent debate and self-consistency.** Existing work asks whether multiple model responses/debate improve answer quality or whether their agreement estimates confidence. ORION-03 differs because instruments do not negotiate before recording the measurement and because scientific scoring is deferred until later work creates evidence.

**Calibrated multi-agent verification.** Recent work explicitly controls hallucination risk when consensus can be correlated. This motivates ORION-03's refusal to treat consensus as authority.

**Research provenance.** Contemporary autonomous-science work increasingly treats provenance-complete experimentation as necessary for trust. ORION-03 uses provenance as infrastructure to preserve the temporal ordering of frontier decision and later score; it does not claim the general concept of research provenance.

**Agent benchmarks.** Most agent evaluations score against pre-existing ground truth. ORION-03 instead targets live research questions where the ground truth is intentionally absent at decision time.

A bounded literature map is recorded in `NOVELTY_RESEARCH_2026-08-22.md`.

---

## 9. Limitations

1. V0 is one item.
2. Both instruments share repository evidence and can share project-level conceptual biases.
3. Instrument B's manifest is externally authored and can omit the correct hypothesis.
4. Later research can be influenced by the selected move, complicating causal interpretation of `ALIGNED`.
5. Receipt replay preserves the decision record but does not validate the truth of host-supplied evidence.
6. The harness is an auditable process instrument, not a sandbox/security system.
7. The invalid-content repair covers declared schema/content failures, not arbitrary software corruption.

---

## 10. Claim boundary

The present paper may claim:

- a concrete dual-instrument architecture;
- receipt-replay and typed-control contracts on the explicitly verified surfaces;
- one prospectively frozen V0 agreement measurement with later `ALIGNED` scoring;
- live discovery and subsequent repair of malformed-success receipt recovery defects;
- a preregistered multi-frontier protocol for testing the benchmark's predictive/calibration value.

It may not claim:

- agreement implies correctness;
- a measured agreement or reliability rate;
- statistical independence of the instruments;
- autonomous scientific superiority;
- security/tamper-proofing;
- execution/results of the multi-frontier study before those prospective items actually exist.

---

## Related-work anchors

- K. Ding, *When LLMs Agree, Are They Right? Auditing Self-Consistency and Cross-Model Agreement as Confidence Signals*, arXiv:2607.08065 (2026).
- A. Kostka and J. A. Chudziak, *Controlling Uncertainty and Hallucination Risk in Multi-Agent Fact Verification*, UAI 2026 / PMLR 337.
- A. P. Smit et al., *Should We Be Going MAD? A Look at Multi-Agent Debate Strategies for LLMs*, ICML 2024.
