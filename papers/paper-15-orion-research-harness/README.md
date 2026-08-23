# P15 — The ORION research harness

**Stable ID:** ORION-P15
**Paper issue:** none yet — this directory was opened ahead of one.
**Status:** `METHODS_SCOPE_ONLY / NO_SCIENTIFIC_RESULT`

`P15_ACTIVE_CLAIM_AUTHORITY_V1.json` is the machine-readable active lifecycle
record and `CLAIM_EVIDENCE_LEDGER.md` is its human-readable claim boundary. P15
has no H1 or protected experiment, so this state is neither a failed result nor
an unchecked scientific claim and cannot be promoted as a positive empirical
finding.

A systems paper introducing the two execution harnesses ORION research runs on, and
the guarantees each provides. It carries no scientific superiority claim and grants
no authority.

## Why P15 rather than a new namespace

The P-series already contains non-claim papers: #669 writes P14 (ORION-RSE) as a
"methods/evaluation-contract paper only", and the merged P10 technical note was
evaluation infrastructure. A systems paper is therefore in-series, not an exception.
`Q-paper-NN-*` stays reserved for the ORION-Q programme's own scientific numbering.

If a programme issue later assigns this subject a different number, that decision
wins; this README is not an authority over numbering.

## What it would cover

### 1. The ORION research harness

`packages/orion-research-harness/` — a turnkey local harness for tool-integrated
research sessions, landed through #725 and hardened afterwards. What makes it a
paper rather than a utility is the guarantee surface, which is already under test:

| Concern | Test |
|---|---|
| host/capability failures never enter scientific evidence | `test_governance_hardening.py` |
| bounded file, process and directory output | `test_local_limits.py` |
| strict, non-coercing receipt schemas | `test_hardening.py` |
| race-safe receipt publication | `test_campaign_strictness.py` |
| recovery from invalid content | `test_invalid_content_recovery.py` |
| execution coverage accounting | `test_execution_coverage.py` |

The load-bearing claim is a separation, not a feature: **a host or capability
failure is reported without being recorded as a scientific result.** That boundary
is what the hostile suite exists to defend.

### 2. The ORION-Q dual harness

`development/orion-q-max-r0/` — a two-lane agreement benchmark with per-lane
receipts (`DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`, lane A/B receipt
sets, and content-addressed per-problem and per-request receipts). The object of
interest is **agreement between independently executing lanes**, which is a
different guarantee from single-harness determinism.

### 3. What the two share, and where they differ

Both bind results to content-addressed receipts. Whether they share a receipt
semantics or merely resemble each other is an open question, and answering it
honestly is the paper's most likely real contribution.

## What this paper must not claim

- that a harness makes a scientific result valid — it makes a result *attributable*,
  which is a strictly weaker property;
- superiority over any other research-execution harness, absent a matched comparison
  that does not currently exist;
- that receipt coverage implies evidence quality.

A cautionary case sits in this repository already: the P1-U R6 campaign produced
fully receipted rows that were then rejected wholesale by a digest-representation
type error. Receipts were complete and the result was still unusable. See
`research/failures/2026-08-digest-representation-boundary-mixup/`.

## Before this becomes a paper

Per #670's rule — research decomposition is fine-grained, publication synthesis is
coarse-grained — a directory is not an identity. The claim ledger now exists and
records no empirical authority. Promotion still needs a paper issue, a donor
matrix against existing research-execution and workflow-provenance systems, and
a prospectively frozen protocol; none of those exists yet.
