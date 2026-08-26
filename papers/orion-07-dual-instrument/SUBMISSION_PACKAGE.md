# ORION-03 submission package

**Current paper type:** research-systems architecture + benchmark definition + one frozen live measurement.  
**Future higher-claim path:** the preregistered >=20-item multi-frontier deferred-scoring series.

## Proposed title

**Dual-Instrument Research Control: Replayable Receipts, Typed Campaign Decisions, and a Deferred-Scoring Frontier Benchmark**

## One-sentence result

ORION implements two materially different research-decision instruments on a common immutable receipt substrate and defines a benchmark in which agreement/disagreement is frozen while a frontier question is unresolved and scored only after later scientific evidence exists; V0 supplies one live measurement and exposed defects that current main subsequently repaired.

## Significance statement

Research-agent benchmarks typically assume ground truth already exists. ORION-03 targets the setting where a scientific question is unresolved at decision time. It preserves two instruments' diagnoses and moves before the later evidence exists, treats disagreement as valid data, and separates the decision record from deferred outcome scoring. The first live use also exposed a deterministic-identity failure mode for successful-but-malformed receipts; current main now maps invalid reasoner content to structured failure and preserves invalid receipt bytes under explicit audited archival before retry.

## Editor pitch

We introduce a replayable host-capability research harness, a typed non-LLM campaign controller, and a prospective benchmark for inter-instrument decisions on live frontier questions. Rather than interpreting consensus as authority, the benchmark records AGREE/PARTIAL/DISAGREE/CANNOT_CHECK while the outcome is unknown and evaluates the recorded decision only after later scientific work produces evidence. Benchmark V0 is intentionally presented as one measurement, not a reliability estimate. During live use the architecture also revealed malformed-success receipt recovery defects; these are preserved historically and current main includes a reason-bound archival/retry path with regression tests. The paper therefore contributes a concrete auditable systems contract and benchmark definition while refusing a predictive-validity claim that the current sample cannot support.

## Machine-facing implementation contract

`packages/orion-research-harness/src/orion_research_harness/publication_contract.py`

binds the ORION-03 paper to current implementation and is tested by:

`packages/orion-research-harness/tests/test_publication_contract.py`.

## Data/code availability

The harness package, V0 frozen protocol/results/raw receipts, malformed-content regression tests, and Q-series sync checks are public in ORION. `REPRODUCE.md` lists the exact internal test routes.

## Current claim boundary

Allowed:

- architecture/contract on verified surfaces;
- benchmark definition with disagreement admissible;
- one frozen live V0 measurement and later `ALIGNED` score;
- historical defect discovery and current repair.

Not allowed:

- agreement implies correctness;
- reliability/calibration rate from one item;
- statistical independence of the instruments;
- security/tamper-proofing;
- result of the future multi-frontier protocol.

## Internal submission checklist

- [x] manuscript V2;
- [x] current-main D2/D3 repair reflected;
- [x] V2 claim ledger;
- [x] current literature boundary around consensus/agreement;
- [x] multi-frontier successor protocol frozen and labeled unexecuted;
- [x] machine-readable harness publication contract;
- [x] regression tests for the paper-facing harness contract;
- [x] reproduction guide;
- [x] Q-series framework/content sync.

At upload time: venue formatting, author metadata, current CI result and bibliography normalization.
