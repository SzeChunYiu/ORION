# ORION-25 provenance interoperability protocol V1

**Programme:** #977  
**Purpose:** close the real provenance/workflow interoperability gap without confusing provenance fidelity with scientific validity.

## Freeze chronology

This protocol and the real-receipt fixture file are committed before the interoperability adapter, scorer or independent verifier. The existing 18-case `P15_SEI_FAULT_PROTOCOL_V1` corpus remains immutable and is reused only as already-frozen hostile science/execution input.

**Pre-outcome correction:** the first protocol draft listed only seven normalized execution fields. Before any adapter/checker existed or any interoperability outcome was observed, that was corrected because the seven-field projection could not represent existing frozen SEI distinctions such as cleanup omission, finalization-before-reap, stale replay and coverage omission. The authoritative V1 execution vector below therefore contains every execution coordinate needed by the pre-existing SEI contract.

## Donor formats

### W3C PROV

Use the production Python `prov` library (3.x) to construct a PROV document containing at minimum:

- execution input/result entities;
- one execution activity;
- one software agent;
- `used` relation;
- `wasGeneratedBy` relation;
- `wasAssociatedWith` relation;
- execution identity/digest/status attributes required for round-trip recovery.

Serialize to PROV-JSON and deserialize through the library. ORION-25 may not use a private side channel to recover execution facts.

### RO-Crate 1.3 / Workflow Run shape

Emit RO-Crate 1.3 JSON-LD with:

- `@context = https://w3id.org/ro/crate/1.3/context`;
- root `Dataset`;
- `CreateAction` execution entity;
- software `instrument`;
- input `object`;
- output `result`;
- execution identity/digest/status encoded as explicit additional properties.

The current `rocrate` Python package documents support through RO-Crate 1.2, so this study must not claim library-certified 1.3 conformance. The independent checker validates the required 1.3/Workflow Run structural projection directly.

## Data

Two groups are evaluated.

### Group A — already-frozen SEI hostile corpus

All 18 cases from `sei_fault_cases_v1.jsonl` and their independent gold dispositions. These include complete-provenance-but-invalid-science and lane-agreement-but-wrong-science cases.

### Group B — real workflow receipts

Freeze at least four real ORION GitHub Actions executions with exact run/artifact/digest identities and bounded scientific disposition. Required semantic variety:

- bounded positive scientific result;
- bounded negative scientific result;
- valid execution whose stronger scientific claim remains `CANNOT_CHECK`;
- bounded result with independent two-implementation agreement.

The fixture stores only facts already bound by paper-local/programme receipts; it creates no new scientific authority.

## Round-trip execution fact set

Every donor representation must recover exactly the following execution-only coordinates when supplied by the source fixture:

`(execution_id, occurrence_id, tool_id, input_digest, output_digest, spawn_ok, host_ok, timeout, exit_zero, output_present, output_complete, reaped, finalized_after_reap, cleanup_complete, retry_accounting_valid, invocation_match, input_digest_match, result_digest_match, occurrence_unique, fresh, coverage_complete, replay_match, lane_applicable, lane_agree)`.

The provenance projection may additionally carry neutral transport metadata such as timestamps, software version, artifact URI and representation version, but those fields cannot participate in scientific admission.

Scientific fields are intentionally excluded:

`scientific_contract_available`, `scientific_contract_valid`, `claim_authority_available`, `claim_authority`, `scientific_disposition`.

If any scientific field appears in the provenance-only projection, the test fails for leakage.

## Scientific-admission comparison

For every case compute three dispositions:

1. **native SEI:** from original execution facts plus independent scientific/authority record;
2. **PROV-imported SEI:** from PROV round-trip execution facts plus the same independent scientific/authority record;
3. **RO-Crate-imported SEI:** from RO-Crate round-trip execution facts plus the same independent scientific/authority record.

The three must agree exactly.

Then compute **provenance-only** disposition using donor execution provenance without the independent scientific/authority record. When execution is valid but scientific validity/authority is not encoded, the result must be `CANNOT_CHECK`, not success.

## Real-receipt false-rejection rule

For the real receipt group, valid bounded scientific results that carry the required independent scientific record must not be rejected merely because they arrived via PROV or RO-Crate. The `CANNOT_CHECK` real case must remain `CANNOT_CHECK`; provenance completeness may not promote it.

## Interoperability endpoints

- exact execution-fact round-trip rate through PROV-JSON;
- exact execution-fact round-trip rate through RO-Crate 1.3 projection;
- scientific-field leakage count into donor provenance;
- native-vs-imported SEI disagreement count;
- provenance-only false scientific-success count;
- real-receipt false rejection count;
- real-receipt false promotion count;
- serialized bytes per normalized execution fact record;
- encode/decode wall time (informational, not a hard scientific endpoint because runner load is uncontrolled);
- deterministic output replay;
- structurally independent adapter/verifier agreement.

## Positive gate

`P15_PROVENANCE_INTEROP_V1_SUPPORTED` requires:

- 100% normalized execution-fact round-trip for both donor representations;
- zero scientific-field leakage into provenance-only donor records;
- zero native-vs-imported SEI disposition disagreements across all hostile and real cases;
- zero provenance-only false scientific successes;
- zero false rejection/promotion on the frozen real receipt group;
- exact preservation of the known complete-provenance/invalid-science and lane-agreement/wrong-science counterexamples;
- deterministic replay;
- independent verifier agreement.

A positive result closes interoperability/representation-independence only. It does not close production-scale host fault breadth, cryptographic attestation comparison, or independent external scientific adjudication.
