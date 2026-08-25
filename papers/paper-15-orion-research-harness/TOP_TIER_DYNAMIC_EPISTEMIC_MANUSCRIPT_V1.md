# P15 Top-Tier Dynamic-Epistemic Manuscript V1

## Candidate title

**Execution Integrity Is Not Scientific Authority: Dynamic Noninterference for Research Harnesses**

```text
status = MANUSCRIPT_READY_FOR_RESULT_BINDING
paper_authority_delta = NONE
job = P15-DES-01
```

## Abstract

Perfect provenance does not make a scientific claim true. P15 models occurrence identity, content, environment, chronology, replay, agreement, attestation, numerical outcome identity, scientific validity, and claim authority as separate dynamic coordinates. It absorbs W3C PROV, research objects, supply-chain attestation, reproducible workflows, and Byzantine systems. We prove execution–science noninterference, receipt insufficiency, occurrence binding, full-key-compromise limits, and publication linearizability. Production-scale fault injection and cross-site replay will compare provenance, replay, multi-lane agreement, attestation products, and an ideal execution/science product.

## Theory

- `P15-T1`: execution-coordinate changes cannot alter scientific validity or authority without a scientific bridge.
- `P15-T2`: identical complete receipts may accompany valid and invalid scientific payloads.
- `P15-T3`: attribution binds exact occurrence, content, environment, chronology, and custody epoch.
- `P15-T4`: a valid signature proves key possession and signed facts, not truthful execution or scientific validity under full compromise.
- `P15-T5`: publication requires one linearizable event binding final content, execution receipt, claim state, and authority epoch.

## Decisive computation

`P15-DES-01`: host/process/key/custody faults, cross-site replay, production attestations, claim-relevant numerical changes, race conditions, overhead, and false rejection. Intended terminal: `DYNAMIC_EXECUTION_INTEGRITY_NONINTERFERENCE_PRODUCTION_REPLICATED`.
