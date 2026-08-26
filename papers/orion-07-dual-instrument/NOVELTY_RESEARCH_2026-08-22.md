# Q3 fresh novelty research — 2026-08-22

Purpose: position the dual-instrument paper against consensus, multi-agent debate, provenance and scientific-agent evaluation literature. This is a bounded search record, not a novelty certificate.

## Candidate residual contribution

Q3 should not claim that agreement among AI systems implies correctness, that multi-agent verification is new, or that content-addressed provenance is unique. The strongest residual is narrower:

> A benchmark in which **architecturally different scientific decision instruments** receive the same prospectively frozen live frontier question, record AGREE/PARTIAL/DISAGREE/CANNOT_CHECK without forcing consensus, preserve receipt-level provenance for each diagnosis/move, and are scored later against scientific outcomes that did not exist at decision time.

The object of measurement is therefore not ordinary ensemble accuracy. It is whether **pre-outcome inter-instrument agreement/disagreement on a live research decision contains calibrated information about later scientific resolution**.

## Closest/current literature threats

### Cross-model agreement is not correctness

Kaihua Ding, **“When LLMs Agree, Are They Right? Auditing Self-Consistency and Cross-Model Agreement as Confidence Signals,”** arXiv:2607.08065 (2026), reports a large cross-runner audit in which agreement is a positive but weak and regime-dependent predictor of correctness, with highly consistent frontier models still producing recurring confident errors.

This directly forbids any Q3 headline of the form “agreement validates a scientific diagnosis.” Q3 must treat agreement as a quantity to calibrate against deferred outcomes, not as authority.

### Consensus can preserve correlated error

Adam Kostka and Jaroslaw A. Chudziak, **“Controlling Uncertainty and Hallucination Risk in Multi-Agent Fact Verification,”** UAI 2026 / PMLR 337, emphasizes that consensus among aligned agents can reflect shared bias rather than truth and develops calibrated risk control for factual verification.

Q3's differentiator must therefore be the **architectural and epistemic separation** of the two instruments plus deferred frontier scoring, not the mere use of more than one judge.

### Multi-agent debate/ensembling is already established

Andries Smit et al., **“Should We Be Going MAD? A Look at Multi-Agent Debate Strategies for LLMs,”** ICML 2024, finds that multi-agent debate does not reliably outperform self-consistency/other prompting strategies without careful tuning.

Yilun Du et al. and other multi-agent debate work already study independent responses, iterative debate and consensus. Q3 is not a debate paper: its two instruments do not negotiate a shared answer before the measurement is recorded.

### Provenance is a current autonomous-science priority

Recent autonomous-science work explicitly treats complete provenance as foundational for trust. Q3 should present content-addressed capability receipts as infrastructure required to replay the measurement, not as the broad novelty thesis.

## Revised novelty thesis

The strongest defensible positioning is:

> Existing multi-agent work asks whether agreement among model samples or agents improves answer accuracy. Q3 instead defines a prospective **scientific-instrument agreement experiment**: two different decision architectures independently act on an unresolved research frontier, all outcomes including disagreement are admissible, and correctness/alignment is scored only after later scientific work resolves the relevant coordinates. Receipt binding makes the pre-outcome decision and the deferred score auditable.

The distinction becomes meaningful only with a multi-instance prospective series. V0 alone remains a benchmark definition with one first measurement.

## What the current V0 establishes

The current frozen V0 can claim only:

- both instruments independently selected the same responsible layer/move on one live frontier question;
- the typed controller withheld an unresolved revision;
- later R6P/R6Q outcomes were scored `ALIGNED` to that move;
- divergence would have been a valid terminal;
- all raw decision/evidence receipts are preserved.

It cannot establish an agreement rate, predictive validity, calibration or superiority.

## Top-tier research target

The top-tier successor should estimate quantities such as

\[
P(\text{later aligned}\mid\text{AGREE}),\qquad
P(\text{later aligned}\mid\text{DISAGREE}),
\]

and instrument-specific conditional accuracy/calibration over a prospectively assembled corpus of live research decisions.

The crucial design requirement is **deferred truth**: benchmark items may not be selected after the scientific resolution is known.

See `TOP_TIER_UPGRADE_PROTOCOL_2026-08-22.md`.
