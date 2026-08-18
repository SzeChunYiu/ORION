# ORION-P2 independent claim / PDF audit

Audit subject: `b7cfaecfb55d9ad6c12fb59374935769ed8d8787`. Not a #283 verification record.

| ID | Claim | Artifact | Status |
|---|---|---|---|
| P2.OFFLINE | 390-task complete-gold recall 0.979487 vs 0.666667 | `evidence/offline_results/RESULTS_SUMMARY_V1.json` | BOUNDED (`TIER_B_committed`, underpowered, not H1 promotion) |
| P2.H1 | Real-world discovery superiority vs BM25/dense/agentic | no matched Wide/Deep ORION result | CANNOT_CHECK |
| P2.METASYN | MetaSyn ID-only probe 86 reviews | `evidence/external_results/METASYN_ID_ONLY_PROBE_V1.json` | BOUNDED |
| P2.DEEP | Official Deep LLM title judge, 600 tasks, hit rate 0.000 | `evidence/external_results/DEEP_OFFICIAL_ARCHIVE_V1.json` | BOUNDED |
| P2.PDF | Independent final PDF proofread | no TMLR PDF in tree | **OPEN** |

Machine-checked ledger: `protocol/CLAIM_LEDGER_V1.json` via `scripts/check_claim_ledger.py`. This audit does not promote the offline delta or MetaSyn probe into H1.
