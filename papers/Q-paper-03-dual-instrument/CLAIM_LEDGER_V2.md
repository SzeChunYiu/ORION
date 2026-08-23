# Paper Q3 claim ledger V2

**Date:** 2026-08-22
**Status:** updates V1 for current-main instrument behavior and the top-tier prospective study. V1 remains historical.

## Preserved core claims

All V1 claims about deterministic request identity, request/result digest binding, create-only normal receipt persistence, project-root confinement, typed campaign control, protected-reference custody limits, authority non-escalation, the four-cycle R6 drive, and Benchmark V0 remain bounded exactly as in `CLAIM_LEDGER.md` unless superseded below.

## Updated claims

| ID | Maximum permitted claim | Authority | Status / forbidden upgrade |
|---|---|---|---|
| Q3V2-1 | Successful LLM/capability receipts whose content violates the reasoner's task schema no longer escape as an unstructured traceback in the recursive solve path: `ValueError`, `TypeError`, and `KeyError` from strict reasoner parsing are mapped to structured `HOST_CAPABILITY_FAILED` with the error labeled `reasoner content invalid`. | `packages/orion-research-harness/src/orion_research_harness/recursive_runner.py` current main; regression `tests/test_invalid_content_recovery.py` | REPAIRED CONTRACT. Do not generalize beyond the caught schema/content error classes. |
| Q3V2-2 | A successful receipt with invalid task content can be explicitly archived through `archive_invalid_result(request_id, reason=...)` / `retry-failed --invalid-content --reason ...`; the original bytes are preserved under `results/archived/*.invalid-*.json`, a reason sidecar is written, the deterministic identity becomes pending, and a corrected receipt can be ingested. | `workspace.py::archive_invalid_result`; `tests/test_invalid_content_recovery.py::test_invalid_content_archive_frees_identity_for_corrected_receipt` | REPAIRED CONTRACT. This is an explicit audited override, not ordinary successful-receipt mutability and not tamper-proof storage. |
| Q3V2-3 | V1 defects D2 and D3 are therefore historical defects discovered in live use and subsequently repaired/regression-tested; they must not be described as open defects of current main. | C1/C2 plus historical `MANUSCRIPT_V1.md`/`CLAIM_LEDGER.md` | HISTORICAL DEFECT + REPAIR. Do not erase them from the provenance narrative. |
| Q3V2-4 | Benchmark V0 remains exactly one prospectively frozen live frontier measurement: instruments agree on the registered diagnosis/move and the later R6P/R6Q coordinates are scored ALIGNED. | V1 benchmark protocol/results and receipts | ONE MEASUREMENT ONLY. No rate/calibration claim. |
| Q3V2-5 | Current literature establishes that model self-consistency/cross-model agreement can be a weak, regime-dependent signal and that consensus can preserve correlated errors. Q3 therefore treats AGREE/DISAGREE as variables to score later, never as scientific authority. | `NOVELTY_RESEARCH_2026-08-22.md` and cited external literature | POSITIONING. Not an empirical claim from ORION. |
| Q3V2-6 | A prospective multi-frontier protocol is frozen for a future >=20-item series across >=3 research programmes, with deferred ALIGNED/MISALIGNED/UNRESOLVED scoring and explicit CANNOT_CHECK outcomes. No outcome exists yet under this protocol. | `TOP_TIER_UPGRADE_PROTOCOL_2026-08-22.md` | REGISTERED RESEARCH ONLY. Do not describe the series as executed. |

## Updated allowed headline

> We present a receipt-replay research harness and a typed non-LLM campaign controller together with a prospective scientific-instrument agreement benchmark. In the first frozen live frontier instance, the instruments independently agreed on the responsible layer and next move and the later registered scientific outcomes aligned with that move. The live run also exposed malformed-receipt recovery defects that current main now repairs with structured failure and audited invalid-content archival. V0 is one measurement; a preregistered multi-frontier study is required before any calibration or predictive-validity claim.

## Still prohibited

- “Agreement proves correctness.”
- “Two instruments are independent in the causal/statistical sense.”
- Any agreement-rate or reliability claim from V0.
- “The harness is secure/tamper-proof/sandboxed.”
- “Successful receipts can be freely replaced.” Invalid-content archival is an explicit reason-bound recovery path only.
- “Q3 demonstrates autonomous scientific superiority.”
