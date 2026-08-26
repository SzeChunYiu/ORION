# Issue #157 closure receipt — 2026-08-17

Lane: `cursor/paper-157`. Additive evidence only. Does not mutate P2 V1 and does not fork issue #279 V2 files.

Machine-readable twin: `evidence/external_results/ISSUE_157_CLOSURE_RECEIPT_V1.json`.

## Verified

### Complete-gold 390-task (reproduced)

`python papers/paper-02-open-world-scientific-discovery/scripts/run_offline_companion.py --check` exited 0. The original publication projection is preserved byte-for-byte at `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json`. Receipt frozen against `main` `09929f208f581cda6985575ca419a7181a1f03ba` (P2 summary hashes unchanged through that commit).

| Binding | Value |
| --- | --- |
| Tasks / systems / repeats / records | 390 / 14 / 3 / 16,380 |
| Authority | `TIER_B_committed` (not a promoted primary) |
| ORION complete-gold recall | 0.979487 |
| Strongest confirmatory baseline | `protocol_driven_systematic_review` 0.666667 |
| Paired difference | 0.312821 |
| ORION premature task closure | 0.0 |
| Suite fingerprint | `2f6936ba52fb12dbee7614b6409fe35ee8f34f443088a11fe5f8916552649c1c` |
| Record digest | `27b8e55b68a65906fe0971ed2f24a814d31d66a1423d38782bb121c7f06e1525` |
| Raw artifact hash-list digest | `ed5cf7bd823fcabd6a57658a05560bd5f1e30256aa3f8eb8404325c493ed3cfe` |
| Summary file SHA-256 | `ee414173bbc8da7a564d697a1bab280e856891a0750de93f660735772973c03b` |

The table above is the historical 2026-08-17 receipt. On 2026-08-25 the
canonical terminal vocabulary was completed: censored transport cases remain
`CANNOT_CHECK` instead of being encoded by obsolete terminal labels. The
machine-readable twin now binds the current `RESULTS_SUMMARY_V1.json` hashes
and carries a `canonical_vocabulary_reprojection` block containing these
original hashes and the exact 319/12 to 260/71 PASS/`CANNOT_CHECK`
reclassification. Recall, the strongest-baseline result, premature-closure
rate, and the no-promotion boundary did not change; this was not a new
scientific execution.

Targeted tests: `test_p2_offline_analysis_snapshot.py` (3) plus `test_regeneration_reproduces_the_committed_fingerprint` and `test_the_suite_meets_the_frozen_power_commitment` — 5 passed.

### Deep official (null on main)

PR #266 merge `ebf5fcfe4d9f3ff57cf53763bf95a39d9631cb24` is on `main`. Archive `DEEP_OFFICIAL_ARCHIVE_V1.json`: **hit rate 0.000** (0/600) under `OFFICIAL_DEEP_LLM_TITLE_JUDGE`. Judge control `CONTROL_PASSED` (9/9). Stage attribution on main: candidate generation, not a dead judge. **Not relabelled positive.** Matched multi-provider Deep remains `CANNOT_CHECK`.

### Wide

The archived credential-free official Wide probe (arXiv public API, 400 tasks) remains a **null**: average IoU 0.005226, average recall 0.020012. That is a single-candidate probe, not a matched ORION-vs-baseline result.

A matched keyless run **without** the arXiv API was not executed. Exact blockers:

1. **`FROZEN_ADAPTER_REQUIRES_ARXIV`.** `run_autoresearchbench_wide_comparison.py` hardcodes `arxiv_route` in both systems. `orion.study.p2.arb_systems.Backends` exposes only arXiv and OpenAlex.
2. **`OFFICIAL_SCORER_ARXIV_ID_IOU`.** The official scorer is arXiv-id set IoU. A 3-task OpenAIRE/DBLP/Crossref connectivity probe (no arXiv call; public split hash `af795b78…`; HTTP 200 on 9/9) did not yield a scorer-native identity bridge: OpenAIRE/DBLP 0 arXiv-id regex matches; DBLP empty; Crossref DOIs. The adapter regex over Crossref JSON is a false-positive trap, not a join.
3. **`NO_ARXIV_MATCHED_RUNNER_ON_MAIN`.** A replacement runner would be P2 V2. Sibling **#279** already has WIP `one_stage_attribution.py` and `emit_issue279_revival_receipts.py` on `cursor/issue-279`. This lane cites those files and does not fork them.

Campaign outputs: `/tmp/paper-157-wide/`. Sanitized probe: `evidence/external_results/ISSUE_157_KEYLESS_BACKEND_PROBE_V1.json`.

## Remaining `CANNOT_CHECK`

- matched AutoResearchBench Wide ORION-vs-baseline without arXiv API (owned scientifically by #279)
- matched multi-provider official Deep comparison
- SAGE official 200k corpus/evaluator (already STRUCK)
- final live-provider campaign

Issue #157 stays **open**. Offline 390-task positivity and the Deep 0.000 null do not close it.
