# P15 manuscript interoperability addendum V1

This addendum updates `MANUSCRIPT.md` after the prospectively frozen provenance-interoperability study. It does not rewrite the earlier 18-case SEI chronology and does not grant production-systems superiority.

## Revised contribution statement

P15 now contributes five bounded objects rather than four:

1. the five-level execution-to-science separation;
2. executable H15.1–H15.5 admission invariants;
3. the prospectively frozen 18-case hostile benchmark;
4. the bounded comparative SEI result;
5. **a real provenance-interoperability result showing that the SEI admission boundary survives representation through W3C PROV and RO-Crate/Workflow-Run structures.**

The fifth contribution is important because it removes a natural systems objection to the first four: the separation is not obtained only by forcing users into an ORION-specific receipt representation.

## New experiment — donor provenance interoperability

### Protocol

`top_tier/P15_PROVENANCE_INTEROP_PROTOCOL_V1.md` was frozen before the adapter and independent checker. One pre-outcome correction expanded the execution-only fact vector because the initial seven-field draft could not encode already-frozen lifecycle distinctions such as cleanup omission, finalization before reap, stale replay and coverage omission. No outcome existed when that correction was made.

The study evaluates 22 cases:

- all 18 existing hostile SEI cases;
- four real ORION workflow receipts representing a bounded positive, an authoritative negative, a two-checker formal result and a real execution whose stronger scientific claim is `CANNOT_CHECK`.

Execution-only facts are serialized independently from scientific fields. The production Python `prov==3.1.0` library performs W3C PROV-JSON serialization/deserialization. A separate RO-Crate 1.3 / Workflow-Run `CreateAction` projection carries the same normalized execution vector. Scientific-contract validity and claim authority are intentionally absent from both donor records.

### Results

The protected workflow returns `P15_PROVENANCE_INTEROP_V1_SUPPORTED`, and a structurally independent verifier returns `P15_PROVENANCE_INTEROP_SECOND_INDEPENDENT_CHECKER_GREEN`.

| Endpoint | Result |
|---|---:|
| PROV-JSON execution-fact round-trip | 1.000 |
| RO-Crate 1.3 / Workflow-Run execution-fact round-trip | 1.000 |
| Scientific fields leaked into provenance-only records | 0 |
| Native vs imported SEI disagreements | 0 |
| Provenance-only false scientific successes | 0 |
| Real-receipt false rejection | 0 |
| Real-receipt false promotion | 0 |
| Mean PROV-JSON bytes/case | 1619.64 |
| Mean RO-Crate JSON-LD bytes/case | 2014.64 |

The serialization sizes are descriptive only. Hosted wall time is not used as a performance claim.

### Decisive real and hostile cases

`SEI-COMPLETE-INVALID-SCIENCE` remains `INVALID_SCIENCE` after both donor provenance round trips even though the execution trace is complete. With provenance alone, it remains `CANNOT_CHECK` because scientific validity is not encoded by the execution record.

`SEI-DUAL-AGREE-WRONG` remains invalid despite lane agreement. `SEI-DUAL-DISAGREE-VERIFIED` remains scientifically valid when an independent verifier is present despite lane disagreement.

Most importantly for external validity, `REAL-P10-NATIVE-LEAN-CANNOT-CHECK` is a real successfully executed workflow record with complete provenance but insufficient registered scientific coverage. It remains `CANNOT_CHECK` after both provenance imports. Thus the admission boundary is not only a property of synthetic fault records.

## Revised related-work boundary

W3C PROV, RO-Crate and Workflow Run RO-Crate are now **executed interoperability donors**, not only related-work citations. P15 cedes to them:

- entity/activity/agent provenance;
- workflow/run packaging;
- provenance interchange;
- step/tool invocation representation.

P15's residual is the typed boundary by which such execution evidence becomes eligible—or remains ineligible—for scientific evidence and claim authority.

The paper should therefore avoid sentences implying that existing provenance systems are weak because they lack ORION metadata. The demonstrated point is different: even rich, correctly round-tripped provenance is a lower-layer object from scientific validity.

## Revised limitations

The V1+interop package still does not measure broad production-scale overhead, signal/nonblocking/process-race coverage across independent workflow engines, or cryptographically attested execution. It does not show superiority to every signed proof-of-execution system. Those are the correct next systems gates.

The result also assumes a scientific contract can be provided. For open-ended research, that contract may be an independent expert adjudication process and may legitimately return `CANNOT_CHECK`.

## Referee-facing headline

> **Execution provenance is necessary infrastructure for auditable research, but it is not scientific admission.** Across a prospectively frozen hostile benchmark and real workflow receipts, the same SEI dispositions survive lossless round trips through W3C PROV and RO-Crate/Workflow-Run representations. Complete provenance, replay and even execution agreement remain insufficient to infer scientific validity or claim authority without an independent scientific contract.

This headline is broader than the original fault-table result while explicitly absorbing, rather than competing with, mature provenance standards.

## Evidence authority

Canonical evidence:

- `top_tier/P15_SEI_RESULT_RECEIPT_V1.md`;
- `top_tier/P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md`;
- `top_tier/P15_INTEROP_LITERATURE_DELTA_2026-08-23.md`;
- `CLAIM_EVIDENCE_LEDGER_V1.md`.

No wording in this addendum grants `P15_TOP_TIER_SUBMISSION_READY`; the remaining production/attestation/cost gates in `TOP_TIER_PROMOTION_V1.md` remain authoritative.
