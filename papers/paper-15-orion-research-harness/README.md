# P15 — Scientific Execution Integrity: the ORION research harness

**Stable ID:** ORION-P15
**Paper issue:** none yet — this directory was opened ahead of one.
**Status:** `PROSPECTIVE_ACQUISITION_PROTOCOL_FROZEN / NO_SCIENTIFIC_RESULT`

`P15_ACTIVE_CLAIM_AUTHORITY_V2.json` is the machine-readable active lifecycle
record and `CLAIM_EVIDENCE_LEDGER.md` is its human-readable claim boundary. It
binds the prospectively frozen `P15A_RESEARCH_HARNESS_ACQUISITION_PROTOCOL_V1.md`
and its fail-closed preflight. P15 still has no H1 or protected experiment, so
this state is neither a failed result nor an unchecked scientific claim and
cannot be promoted as a positive empirical finding.
**Status:** `METHODS_SCOPE_ONLY / NO_SCIENTIFIC_RESULT`

`P15_ACTIVE_CLAIM_AUTHORITY_V1.json` is the machine-readable active lifecycle
record and `CLAIM_EVIDENCE_LEDGER.md` is its human-readable claim boundary. P15
has no H1 or protected experiment, so this state is neither a failed result nor
an unchecked scientific claim and cannot be promoted as a positive empirical
finding.
**Stable ID:** ORION-P15  
**Paper issue:** #979  
**Promotion programme:** #977 / `TOP_TIER_PROMOTION_V1.md`  
**Status:** `PAPER_ISSUE_OPEN / NO_PROTECTED_SEI_RESULT`

P15 is the systems paper for the two execution harnesses ORION research runs on and
the guarantees each provides. Its higher scientific object is **Scientific Execution
Integrity (SEI)**: separating what execution receipts can establish about
attribution/replay/agreement from what they cannot establish about scientific
validity or claim authority.

It carries no scientific superiority claim yet and grants no authority.

## Why P15 rather than a new namespace

The P-series already contains non-claim papers: #669 writes P14 (ORION-RSE) as a
methods/evaluation-contract paper, and the merged P10 technical note was evaluation
infrastructure. A systems paper is therefore in-series, not an exception.
`Q-paper-NN-*` stays reserved for the ORION-Q programme's own scientific numbering.

## Scientific separation ladder

The publication target is not generic provenance. P15 must formalize and test the
non-implications

`ATTRIBUTABLE_EXECUTION`
`!= REPLAYABLE_EXECUTION`
`!= AGREEMENT_BETWEEN_EXECUTIONS`
`!= SCIENTIFICALLY_VALID_RESULT`
`!= AUTHORIZED_SCIENTIFIC_CLAIM`.

Some implications may hold under additional premises; those premises must be stated
explicitly rather than smuggled into receipt semantics.

## What it covers

### 1. The ORION research harness

`packages/orion-research-harness/` — a turnkey local harness for tool-integrated
research sessions, landed through #725 and hardened afterwards. Its guarantee surface
is already under adversarial test:

| Concern | Test |
|---|---|
| host/capability failures never enter scientific evidence | `test_governance_hardening.py` |
| bounded file, process and directory output | `test_local_limits.py` |
| strict, non-coercing receipt schemas | `test_hardening.py` |
| race-safe receipt publication | `test_campaign_strictness.py` |
| recovery from invalid content | `test_invalid_content_recovery.py` |
| execution coverage accounting | `test_execution_coverage.py` |

The load-bearing boundary is that **a host or capability failure is reported without
being recorded as a scientific result**. The publication protocol must independently
freeze and test that boundary rather than treating implementation tests as paper
authority.

### 2. The ORION-Q dual harness

`development/orion-q-max-r0/` — a two-lane agreement benchmark with per-lane receipts
(`DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`, lane A/B receipt sets, and
content-addressed per-problem and per-request receipts).

The object of interest is **agreement between independently executing lanes**, which
is a different property from single-harness determinism and remains weaker than
independently validated correctness.

### 3. Shared and distinct semantics

Both harnesses bind results to content-addressed receipts. P15 must determine which
receipt/integrity semantics genuinely compose across them and which are only similar
implementations.

The top-tier protocol additionally compares/interoperates with generic structured
provenance, W3C PROV/RO-Crate-style workflow provenance, content-addressed execution,
deterministic replay and signed/attested execution systems where feasible. P15's
residual must be the **scientific evidence-admission boundary**, not ownership of
provenance interchange.

## What this paper must not claim

- that a harness makes a scientific result valid — attribution is strictly weaker;
- that replayability or dual-lane agreement establishes correctness;
- superiority over another research-execution system absent a matched protected
  comparison;
- that receipt or execution coverage implies evidence quality;
- generic novelty for provenance, workflow reproducibility or proof-of-execution.

A cautionary case already exists in the repository: the P1-U R6 campaign produced
fully receipted rows that were rejected wholesale by a digest-representation type
error. Receipts were complete and the result was scientifically unusable. See
`research/failures/2026-08-digest-representation-boundary-mixup/`.

## Before top-tier submission

Issue #979 now owns the paper identity and scientific question. Remaining scientific
work is explicit rather than administrative:

- [ ] claim/evidence ledger;
- [ ] donor/interoperability matrix;
- [ ] independent publication-specific hostile fault-injection protocol freeze;
- [ ] H15.1–H15.5 executable/formal closure;
- [ ] matched comparator benchmark;
- [ ] independent result adjudication;
- [ ] submission manuscript and reproducibility package;
- [ ] separate content-addressed `P15_TOP_TIER_SUBMISSION_READY` closure receipt.

Per #670's rule — research decomposition is fine-grained, publication synthesis is
coarse-grained — a directory is not an identity. The claim ledger now exists and
records no empirical authority. Promotion still needs a paper issue, a donor
matrix against existing research-execution and workflow-provenance systems, a
protected hostile corpus, a matched comparator or explicitly noncomparative
estimand, and evaluator separation. The protocol now exists; the other inputs
do not. `P15A_ACQUISITION_PREFLIGHT_V1.json` records that boundary without
turning locally authored labels into protected or independent evidence.
matrix against existing research-execution and workflow-provenance systems, and
a prospectively frozen protocol; none of those exists yet.
The planning protocol itself can never emit the final readiness terminal.
