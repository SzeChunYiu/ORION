# ORION-25 — Scientific Execution Integrity

The installable ORION-25 evaluator is composed with ORION-03's typed frontier records in
`../P15_Q3_SHARED_INSTRUMENT_PACKAGE_V1.json`. This is an in-repository 0.1.0
release candidate under Apache-2.0, not an external release or a new scientific
result. Independent replay, public runtime evidence and site independence remain
`CANNOT_CHECK`.

**Stable ID:** ORION-25  
**Paper issue:** #979  
**Promotion programme:** #977  
**Current lifecycle:** `BOUNDED_SCIENTIFIC_RESULT_EARNED`  
**Current authority:** `P15_ACTIVE_CLAIM_AUTHORITY_V3.json`

**Status (2026-08-24):** `SEI_FAULT_V1 + PROVENANCE_INTEROP_V1 + ATTESTATION_COMPOSITION_V2 EXECUTED / PRODUCTION_COMPARATORS_PENDING`

Three bounded studies are now executed and receipt-bound on the frozen 22-case
corpus (18 hostile SEI cases + 4 real workflow receipts): the SEI fault benchmark
(run `32645458435`), the W3C PROV / RO-Crate 1.3 interoperability study
(run `32655587115`), and the Ed25519 attestation-composition study V2 (canonical
run `32664075763`, plus an independent deterministic-replay execution run
`32665597624` whose artifact-member SHA-256 digests are identical to the
canonical run's), each with an independent second implementation and
deterministic replay. The attestation study's load-bearing negative is frozen:
composed-signature validity is evidence about the key set, not about key custody
or fact truth — full key-set compromise is detected `0/6` at the signature layer,
hostile chain-as-science collapse false-promotes `12` cases, and the properly
scoped cryptographic-only reading stays `CANNOT_CHECK`. False rejection over the
full valid workload is `0/11` chain-layer and `0/5` disposition-level. Evidence:
`top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md` and
`top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2_RUN2.md` (claim C15.8).
Production Sigstore/in-toto-class comparator work, hardware-backed custody and
production-scale characterization remain open; C15.5 superiority stays `CANNOT_CHECK`.

ORION-25 is the systems paper for **Scientific Execution Integrity (SEI)**: what execution receipts, provenance records, replay, lane agreement and cryptographic attestations can establish—and what they still cannot establish—about a scientific claim.

The core separation is:

`ATTRIBUTABLE_EXECUTION`
`!= REPLAYABLE_EXECUTION`
`!= AGREEMENT_BETWEEN_EXECUTIONS`
`!= ATTESTED_EXECUTION`
`!= SCIENTIFICALLY_VALID_RESULT`
`!= AUTHORIZED_SCIENTIFIC_CLAIM`.
Additional premises can connect some layers, but those premises must be explicit. A receipt, a replay, an agreement or a valid signature must never silently become scientific truth.

## Current bounded evidence

### 1. Scientific Execution Integrity fault study

`top_tier/P15_SEI_RESULT_RECEIPT_V1.md` binds the prospectively frozen 18-case hostile fault study.

| system | exact disposition accuracy | false authorized science |
|---|---:|---:|
| plain logs + exit/output | 0.2778 | 13 |
| structured receipt/provenance | 0.7222 | 5 |
| replay + lane agreement | 0.7222 | 4 |
| SEI reference contract | **1.0000** | **0** |

The study contains direct witnesses that complete execution evidence does not imply valid science and that lane agreement does not imply correctness. It also retains two `CANNOT_CHECK` cases rather than coercing missing scientific authority into either success or failure.

### 2. Real provenance interoperability

`top_tier/P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md` tests the same scientific-admission separation after exporting/importing execution facts through real provenance representations.

Across 22 cases (18 hostile SEI cases + 4 real ORION workflow receipts):

- W3C PROV-JSON normalized execution-fact round trip: **1.0**;
- RO-Crate 1.3 / Workflow-Run projection round trip: **1.0**;
- native-vs-imported SEI disagreements: **0**;
- scientific fields leaked into donor provenance: **0**;
- provenance-only false scientific successes: **0**;
- real-receipt false rejection: **0**;
- real-receipt false promotion: **0**;
- structurally independent implementation: GREEN.

This establishes that ORION-25's scientific-admission layer does not require a proprietary provenance format. Provenance carries execution facts; the separate scientific/authority record decides whether those facts license a claim.

### 3. Chained Ed25519 attestation composition

`top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md` binds the canonical GitHub Actions run `32664075763` / artifact `9499830847`; `top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2_RUN2.md` binds the independent deterministic-replay run `32665597624` / artifact `9500055966` (artifact-member SHA-256 digests identical to the canonical run's).

Each case carries a three-link chain:

`execution -> environment -> publication`.

Observed on the frozen 22-case corpus:

- untampered chain verification: **1.0**;
- truncation: **66/66 detected**;
- substitution: **22/22 detected**;
- splice: **22/22 detected**;
- reorder: **22/22 detected**;
- cross-occurrence replay: **22/22 detected**;
- stale-chain reuse: **22/22 detected**;
- valid-workload chain false rejection: **0**;
- valid-workload scientific-disposition false rejection: **0**;
- chain + SEI agreement with frozen gold: **22/22**;
- scientific-field leakage into the cryptographic/provenance layer: **0**;
- independent endpoint checker: GREEN.

#### Full-key-compromise boundary

The frozen `A-COMPROMISE-FULL` arm deliberately asks the question signatures cannot answer. Six forged-clean fact sets are re-signed with the genuine keys:

- signature-layer detections: **0/6**;
- false promotions if a valid chain is treated as scientific truth: **6/6**;
- false promotions even after chain + SEI if key custody is silently assumed: **6/6**.

Therefore the current paper must state:

> **Composed-signature validity is evidence about the key set, not about key custody or fact truth. Key custody is an additional premise, not a consequence of a valid signature.**

This negative boundary is part of the result, not a defect to tune away.

## Strongest paper-level claim

> At bounded scope, execution integrity, provenance representation, cryptographic attestation, scientific validity and claim authority are distinct layers. SEI prevents execution/replay/agreement evidence from self-authorizing science on the frozen fault corpus; that separation survives W3C PROV and RO-Crate/Workflow-Run transport; and a three-link Ed25519 chain detects the registered non-compromise tamper/replay attacks with zero observed false rejection while explicitly failing under full key compromise, where signature validity has no authority over fact truth.

## What ORION-25 does not own

ORION-25 does not claim generic provenance, W3C PROV, RO-Crate, cryptographic signatures, content addressing or deterministic replay as new primitives. Those are donors.

ORION-25's residual object is the **scientific evidence-admission boundary above those primitives**: which execution facts are attributable/replayable/attested, which scientific validity/authority facts remain separate, and how failure of one layer is prevented from laundering into another.

## Historical lifecycle

The old lifecycle records are preserved and remain reproducible:

- `P15_ACTIVE_CLAIM_AUTHORITY_V1.json` — methods-only state before a ORION-25 protected result existed;
- `P15_ACTIVE_CLAIM_AUTHORITY_V2.json` — prospectively frozen acquisition state before protected execution;
- `P15_ACTIVE_CLAIM_AUTHORITY_V3.json` — **current** bounded scientific authority after SEI + provenance interoperability + attestation composition.

The earlier `NO_SCIENTIFIC_RESULT` states are historical, not current. They are retained so the paper's promotion path remains auditable rather than rewritten after success.

## Core artifacts

- `P15_ACTIVE_CLAIM_AUTHORITY_V3.json` — current machine-readable authority;
- `CLAIM_EVIDENCE_LEDGER.md` — human-readable claim boundary;
- `MANUSCRIPT.md` — manuscript surface;
- `top_tier/P15_SEI_RESULT_RECEIPT_V1.md`;
- `top_tier/P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md`;
- `top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md`;
- `top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2_RUN2.md`;
- `top_tier/P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md`;
- `top_tier/P15_INTEROP_LITERATURE_DELTA_2026-08-23.md`;
- `top_tier/P15_NEAREST_WORK_DELTA_2026-08-23.md`.

The shared ORION-25+ORION-03 package surface is bound by
`../P15_Q3_SHARED_INSTRUMENT_PACKAGE_V1.json`. It emits only `DECLARED_*`
science labels from caller-supplied booleans and binds the complete execution
record digest. Its Apache-2.0 expression is mechanically declared; rights-holder
relicensing authority for pre-existing package files remains `CANNOT_CHECK`.

## Remaining top-tier work

The main missing layer is now **production breadth and cost**, not another toy attestation example:

- broader host/process fault injection: races, truncation/caps, cleanup, retry accounting, timeout/reap/finalization, stale publication and other production failure modes;
- runtime/storage overhead and false-rejection characterization on larger valid workloads;
- clean-environment independent replay of the final bounded stack;
- immediate pre-submission provenance/attestation/systems literature refresh;
- final manuscript/figure/evidence/environment/PDF byte binding.

Do not infer production-scale reliability, trusted key custody, universal execution correctness, scientific truth from signatures, external validation, superiority over a real production attestation stack, or `TOP_TIER_SUBMISSION_READY` from the current bounded evidence.
