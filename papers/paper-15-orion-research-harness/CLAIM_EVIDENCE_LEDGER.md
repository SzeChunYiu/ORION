# P15 Claim–Evidence Ledger

**Stable ID:** ORION-P15

**Active authority:** `P15_ACTIVE_CLAIM_AUTHORITY_V3.json`

**Lifecycle:** `BOUNDED_SCIENTIFIC_RESULT_EARNED` · **Terminal:** `P15_BOUNDED_SEI_PROVENANCE_ATTESTATION_EARNED` · `promotion_allowed=false`

Historical authorities, preserved and superseded (see the evidence correction
below):

| Superseded authority | Lifecycle when it was in force |
| --- | --- |
| `P15_ACTIVE_CLAIM_AUTHORITY_V2.json` | `PROSPECTIVE_ACQUISITION_PROTOCOL_FROZEN / NO_SCIENTIFIC_RESULT` |
| `P15_ACTIVE_CLAIM_AUTHORITY_V1.json` | `METHODS_SCOPE_ONLY / NO_SCIENTIFIC_RESULT` |

| Candidate statement | Current authority | Maximum authorized wording |
|---|---|---|
| the repository contains a local research harness and a dual-lane agreement protocol | DESCRIPTIVE / CONTENT-BOUND | identify the two artifact surfaces and their intended guarantees |
| host or capability failures are kept outside scientific evidence | METHODS GUARANTEE CANDIDATE | describe the tested software contract; do not call it an empirical P15 result |
| P15A has a prospectively frozen evaluation path | ACQUISITION CONTRACT / CONTENT-BOUND | the question, required inputs and fail-closed terminal are frozen; execution is not authorized |
| the two harnesses share a receipt semantics | OPEN DESIGN QUESTION | no equivalence claim until a P15 protocol defines and tests it |
| either harness is more reliable or scientifically valid | NO CLAIM AUTHORITY | never state without a matched, protected comparison |

P15 has no H1, protected input corpus or scientific result. Therefore it has no
negative hypothesis to relabel and no positive hypothesis to claim. The typed
prospective state prevents an inventory from counting the directory as an
unchecked hypothesis while also preventing a fabricated empirical pass. The
frozen P15A protocol and preflight make the remaining acquisition requirements
executable and explicit.
| the two harnesses share a receipt semantics | OPEN DESIGN QUESTION | no equivalence claim until a P15 protocol defines and tests it |
| either harness is more reliable or scientifically valid | NO CLAIM AUTHORITY | never state without a matched, protected comparison |

P15 has no H1, protected protocol, or scientific result. Therefore it has no
negative hypothesis to relabel and no positive hypothesis to claim. The typed
methods-only state prevents an inventory from counting the directory as
`CANNOT_CHECK` or `FAIL`, while also preventing a fabricated `PASS`.

## Evidence correction (2026-08-24, issue #1086 P13–P15 lane)

The active-authority lines above predate the bounded scientific result and are
superseded without deletion: the active authority is
`P15_ACTIVE_CLAIM_AUTHORITY_V3.json` (terminal
`P15_BOUNDED_SEI_PROVENANCE_ATTESTATION_EARNED`, lifecycle
`BOUNDED_SCIENTIFIC_RESULT_EARNED`, scientific result state
`BOUNDED_EMPIRICAL_SUPPORTED`, `promotion_allowed=false`). V1 and V2 are
retained as historical authorities.

New rows:

| Candidate statement | Current authority | Maximum authorized wording |
|---|---|---|
| the P15 result layers (bounded fault injection, provenance round-trip, attestation composition) constitute internal evidence about the instrument | **SUPPORTED_INTERNAL_PANEL / population_inference:false** (`P15_INTERNAL_PANEL_EVIDENCE_BINDING_V1.json`) | internal unit-test evidence over registered internal panels; no population-level, production-scale, external-replication or site-independence inference |
| the issue #1086 "P15B" label maps to a distinct repository artifact | **FALSE / NO_DISTINCT_ARTIFACT** (repo-wide content + git-log search, 2026-08-24) | no P15B protocol, result, receipt or terminal exists; none was invented; the box is governed by the internal-panel binding instead |
| blocked, adverse and not-run failures are recorded and retained | **SUPPORTED / LEDGER-BOUND** (`P15_FAILURE_LEDGER_V1.md`) | P15A blocked preflight; full-key-compromise boundary (6 attempts / 0 signature detections; CHAIN_AS_SCIENCE 6/6 and CHAIN_PLUS_SEI 6/6 false promotions; 12 total); external boxes OPEN |
| P15 and Q3 form one software/instrument paper | **CONSOLIDATED D8 / EDITORIAL** (`papers/ISSUE_1086_PORTFOLIO_DISPOSITION_V1.json` decision D8) | portfolio structure only; no scientific authority delta |
