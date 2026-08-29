# ORION-07 journal-readiness record

**Current terminal:** `MANUSCRIPT_REVIEW_PASS / EVIDENCE_GATE_BLOCKED`.

The manuscript has been repaired through the writing/reviewer loop, but the frozen publication plan contains a scientific evidence gate that cannot be cleared by editing.

## Review cycle 1 — blockers found

- **ORION-03-R1, blocking:** V1 mixed the benchmark claim with a broad systems-harness claim now overlapping ORION-25.
- **ORION-03-R2, blocking:** V1 still listed defects D2/D3 as open even though current harness regression tests repair both failure reporting and audit-preserving invalid-content recovery.
- **ORION-03-R3, blocking evidence:** only Benchmark V0 exists, while `PUBLICATION_PLAN.md` requires at least 2–3 further question instances before standalone submission.
- **ORION-03-R4, major:** benchmark protocol and result were interleaved with architecture details, obscuring the measured construct and independence assumptions.
- **ORION-03-R5, major:** the related-work paragraph made a broad contrast with agent benchmarks without a fresh submission-date literature closure.

## Repairs completed

- Repositioned ORION-03 as a benchmark-definition paper; delegated general harness guarantees to ORION-25.
- Updated D2/D3 from open defects to repaired historical defects, grounded by `packages/orion-research-harness/tests/test_invalid_content_recovery.py`.
- Separated benchmark Methods, V0 Results, Discussion, Related Work, Limitations, Conclusion, Reproducibility, and Ethics/Resources.
- Narrowed all reliability/predictive-validity language to a single-instance first measurement.
- Kept the extra-instance gate explicit rather than weakening it post outcome.

## Review cycle 2

**Scientific clarity:** PASS.  
**Claim–warrant alignment:** PASS for benchmark definition + one measurement.  
**Cross-paper scope:** PASS against ORION-25 after systems-claim contraction.  
**Current implementation consistency:** PASS for D2/D3 status.  
**Standalone evidence sufficiency:** **BLOCKED** by ORION-03-R3.  
**Target-journal compliance:** UNRESOLVED.

## Resolution test for the remaining blocker

Run at least 2–3 additional prospectively frozen frontier-question instances using the same benchmark contract, preserving divergence as an admissible outcome. Report the series without treating agreement as success by definition. Until then, ORION-03 must not be labeled `PEER_REVIEW_READY` or presented as an evaluation of instrument reliability.

Fresh literature closure, final replay, rendering, and archive deposition remain ordinary submission gates after the evidence blocker closes.