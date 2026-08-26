# P2 supplement plan — narrowed IP&M track

Scientific terminal: `P2_NARROWED`.
Primary target: *Information Processing & Management* (IP&M).

The current IP&M Guide for Authors was recovered and checked on 2026-08-17; the binding submission requirements are summarized in `IPM_SUBMISSION_REQUIREMENTS_2026-08-17.md`. Review is double anonymized, author details go on a separate title page, editable LaTeX source is required, and IP&M points LaTeX authors to the Elsevier CAS single-column template. The guide does not justify carrying forward the retired TMLR 100 MB supplement assumption. Assemble the package below under the live Editorial Manager file constraints at upload time.

No item below is included unless it already exists in the repository. Unavailable future campaigns are listed as reopen/future-work items, not as missing evidence required by the narrowed paper.

## 1. Core reproducibility package

| Item | Source | Why it belongs |
| --- | --- | --- |
| Complete-gold world and tasks | `evidence/offline_gold/{topics.json,world-000.json,world-001.json,tasks-000.json,tasks-001.json}` | Manifest-declared synthetic denominator that makes misses and premature closure observable. |
| World manifest | `evidence/offline_gold/MANIFEST.json` | Task/document counts, seed, file hashes and suite fingerprint. |
| Run manifest + digest | `protocol/OFFLINE_RUN_MANIFEST_V1.{json,sha256}` | Prospective subject/data/system binding for the controlled campaign. |
| Subject code | `src/orion/study/p2/**` | Systems, ablations and evaluator under test. |
| Regeneration/check scripts | `scripts/run_offline_companion.py`, `render_offline_results.py`, `render_offline_mechanisms.py`, `render_route_stop_oracle.py`, `render_table_p2_1.py`, `render_figure_p2_2.py`, `check_claim_ledger.py`, `check_p2_assimilation.py` | Reviewer-verifiable evidence generation and integrity checks. |

## 2. Publication summaries, external probes, tables and figures

| Item | Source / authority |
| --- | --- |
| Offline publication summary | `evidence/offline_results/RESULTS_SUMMARY_V1.json` |
| Mechanism projection | `evidence/offline_results/OFFLINE_MECHANISMS_V1.json` |
| Route-stop oracle | `evidence/offline_results/ROUTE_STOP_ORACLE_V1.json` + `TABLE_P2-S1_route_stop_oracle.md` |
| Failure taxonomy | `evidence/offline_results/TABLE_P2-3_failure_taxonomy.md` |
| Freeze / licence / access manifest | `protocol/TABLE_P2-1_freeze_manifest.md` |
| MetaSyn bounded official ID-only probe | `evidence/external_results/METASYN_ID_ONLY_PROBE_V1.json` + screening FN ledger |
| AutoResearchBench Wide bounded credential-free probe | committed bounded Wide archive/results; stress-test authority only, not matched superiority |
| AutoResearchBench Deep bounded official-judge probe | committed Deep official archive; 0/600 with 9/9 judge control; negative candidate-generation diagnostic, not matched superiority |
| Donor assimilation | `protocol/P2_DONOR_ASSIMILATION_LEDGER_V1.json` + hostile checker/tests |
| Dated nearest-work freeze | `protocol/P2_LITERATURE_ASSIMILATION_FREEZE_2026-08-17.md` |

The controlled summaries bind the complete normalized record set and rich-artifact hashes. Raw controlled records can be emitted on demand with `run_offline_companion.py --write-raw DIR`; whether to ship them expanded is governed by `ARCHIVE_AND_COST_LEDGER.md` and the current venue/package limits.

Figures/tables should be shipped from their committed/generated sources only after the manuscript workflow has compiled the final source and the PDF visual audit has passed. Do not include a stale generated PDF when its generating source or evidence has moved.

## 3. Protocol and integrity layer

| Item | Reviewer question |
| --- | --- |
| `protocol/PROTOCOL_V1.json` | What was frozen before outcomes? |
| `protocol/STATISTICAL_PLAN_V1.json` | Why is the controlled result descriptive/underpowered rather than inferential superiority? |
| `protocol/MEASUREMENT_PLAN_V1.md` | How are metrics and non-emission conditions defined? |
| `protocol/EXTERNAL_ACCESS_AUDIT_V1.json` | Which external authorities were runnable, blocked or unavailable? |
| `protocol/CLAIM_LEDGER_V1.json` + `scripts/check_claim_ledger.py` | Which result-bearing manuscript sentence is bound to which evidence? |
| `protocol/P2_DONOR_ASSIMILATION_LEDGER_V1.json` + `scripts/check_p2_assimilation.py` | Which current donor mechanic removes/narrows P2 novelty, and can source/authority rebranding be detected? |
| `protocol/P2_NARROWED_PUBLICATION_TERMINAL_2026-08-17.md` | Why does the paper stop at a narrowed claim rather than fabricate unavailable matched superiority? |

## 4. Future-work / reopen items — visible, not publication blockers

The narrowed paper does not claim these results. Their absence must remain explicit but does not prevent submission of the bounded methods/system-design paper:

| Item | Current state / reopen condition |
| --- | --- |
| Matched AutoResearchBench Wide ORION-vs-baseline result | `CANNOT_CHECK`: frozen matched runner/scorer path is arXiv-native; reopen prospectively if an admissible denominator-valid runner is frozen before outcomes. |
| Matched multi-provider AutoResearchBench Deep result | `CANNOT_CHECK`: bounded official-judge probe exists, matched multi-provider comparison does not. |
| Official SAGE result | `CANNOT_CHECK/STRUCK`: published 200k corpus/evaluator unavailable; no substitute may be labelled official. |
| Final live-provider campaign and monetary/runtime/token ledger | `CANNOT_CHECK`: not required because the narrowed paper makes no live-provider superiority/cost claim. |
| Expert-review comparison cases | Optional future extension; not evidence for the present mechanism claim. |

## 5. Licence exclusions

Per `protocol/TABLE_P2-1_freeze_manifest.md`:

- SAGE benchmark data: `AVAILABLE_LICENSE_BLOCKED`; do not redistribute without a licence basis.
- AgentSLR code: `AVAILABLE_LICENSE_BLOCKED`; do not redistribute without a licence basis.
- MetaSyn data: redistribute only the project-authored material whose licence permits it; otherwise ship revision/content bindings and acquisition instructions.
- AutoResearchBench: even where upstream licensing permits redistribution, prefer pinned revisions/content digests over a stale fork unless the final venue/archive package has a reason to embed it.
- Live-provider response bodies: do not redistribute without checking provider terms; no final live campaign is claimed here anyway.

## 6. Pre-submission package checklist

1. `python3 papers/paper-02-open-world-scientific-discovery/scripts/run_offline_companion.py --check` exits 0.
2. Publication summary/mechanism/route-stop/table render checks exit 0.
3. `python3 papers/paper-02-open-world-scientific-discovery/scripts/check_claim_ledger.py --check` exits 0; review any known-defect notes rather than suppressing them.
4. `python3 papers/paper-02-open-world-scientific-discovery/scripts/check_p2_assimilation.py` exits 0.
5. `.github/workflows/p2-manuscript.yml` compiles the final manuscript and rejects unresolved citations/references; retain the PDF/log artifact for review.
6. Visually inspect every rendered page/figure and resolve clipping, overflow, broken glyphs or unreadable labels.
7. Repeat the primary-source nearest-work search within 14 days of the actual submission date. New material that changes the residual claim/baseline reopens the novelty gate.
8. Apply `IPM_SUBMISSION_REQUIREMENTS_2026-08-17.md`: separate anonymized manuscript and title page, editable source/CAS single-column wrapper, glossary, CRediT, separate figure captions, and author-approved generative-AI disclosure; re-check the live Editorial Manager fields for changes at upload time.
9. Insert actual author/affiliation/corresponding-author metadata only from the authors or the live submission form; automation must not invent it.
10. Confirm no licence-blocked material has been swept into the final supplement/archive.
11. Mirror expiring raw external evidence into a durable archive where redistribution is permitted, especially the MetaSyn Actions artifact before its recorded 2026-09-15 expiry.
