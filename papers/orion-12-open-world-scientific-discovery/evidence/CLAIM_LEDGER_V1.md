# P2 claim ledger V1

> **Record of the pre-rewrite manuscript, 2026-08-22.** The manuscript was
> subsequently rewritten so that its claims are about the mechanism rather than
> about a named system, and so that internal status tokens do not appear in its
> prose. The claim sentences quoted below are the wording of the manuscript as it
> stood when this ledger was cut. **No number, authority, supporting artifact or
> status in this table changed in that rewrite**, and none has been edited here:
> a ledger is a record of what was allowed and on what evidence, so it is
> annotated rather than restated. The machine-checked binding of each claim
> sentence to its archived artifact lives in `protocol/CLAIM_LEDGER_V1.json`,
> which was rebound to the new wording and is what any automated check reads.

> **Later vocabulary migration.** On 2026-08-25 the canonical evaluator
> vocabulary was completed so that transport-censored tasks remain
> `CANNOT_CHECK` instead of being encoded by obsolete terminal labels. That
> migration changed status counts and content hashes but did not change recall,
> precision, route-stop values, the strongest baseline, or the headline
> scientific boundary. The exact pre-migration summary used by the historical
> rows below is preserved at
> `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json`
> (SHA-256 `ee414173bbc8da7a564d697a1bab280e856891a0750de93f660735772973c03b`).
> Current claims and counts are governed by `protocol/CLAIM_LEDGER_V1.json` and
> `evidence/offline_results/RESULTS_SUMMARY_V1.json`; this dated table must not
> be used as their current human-readable projection.

This ledger is intentionally narrower than the original paper ambition. A row is `SUPPORTED` only when the cited artifact exists in the repository and the stated authority matches that artifact. External discovery superiority remains `CANNOT_CHECK`; completed external rows are bounded probes, not a full multi-provider ORION superiority result.

| Claim surface | Claim allowed in this revision | Authority | Supporting artifact | Status |
| --- | --- | --- | --- | --- |
| Abstract | ORION's route/read/stopping governance is implemented and survives the controlled complete-gold mechanism tests. | 390-task offline companion, `TIER_B_committed` with the plan's mandatory underpowered label | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json`; frozen record digest `27b8e55b…` | `SUPPORTED` |
| Abstract | ORION improves real scientific-literature discovery over BM25/dense/agentic baselines. | Requires external Wide/Deep or other denominator-valid matched ORION result | No matched external superiority result archived | `CANNOT_CHECK` |
| Results | Full ORION mean complete-gold recall is 0.979487 on the frozen controlled index; strongest frozen confirmatory baseline is 0.666667; descriptive difference +0.31282. | `TIER_B_committed` (n=390 ≥ 385), achieved half-width 0.0496 exceeds the frozen superiority margin 0.03 ⇒ mandatory underpowered label; no superiority promotion | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json` | `SUPPORTED` |
| Results | Full ORION has zero premature task closures in the controlled companion; the strongest confirmatory baseline has rate 1.0. | `DESCRIPTIVE_ONLY` | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json` | `SUPPORTED` |
| Mechanism H2 | Removing route-independence governance lowers controlled-index recall to 0.444444 and closes prematurely on all tasks. | Negative ablation, descriptive only | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json` → `mechanism_checks.route_independence` | `SUPPORTED` |
| Mechanism H3 | Allowing a route stop to certify task closure lowers recall to 0.333333 and produces premature closure on all tasks. | Negative ablation, descriptive only | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json` → `mechanism_checks.route_task_stop_separation` | `SUPPORTED` |
| Mechanism H4 | Removing the question coordinate suppresses legitimate rereads on extraction-shift tasks (3.666667 → 1.0) but does not change aggregate recall in this controlled suite. | Mechanism diagnostic, descriptive only | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json` → `mechanism_checks.question_conditioned_read_ledger` | `SUPPORTED` |
| Safety | Treating an unavailable route as closed converts the 12 censored cases into asserted premature closures without changing aggregate recall. | Safety negative control, descriptive only | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json` → `mechanism_checks.unavailable_route_open_state` | `SUPPORTED` |
| Efficiency mechanism | Removing content-identity dedup raises duplicate processing to 0.101446 and creates 145 budget-exhaustion failures. | Mechanism diagnostic, descriptive only | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json` | `SUPPORTED` |
| Coverage estimator | Coverage diagnostics do not certify completeness; the negative authority ablation closes prematurely on all tasks. | Safety negative control, descriptive only | `evidence/offline_results/RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json` → `mechanism_checks.coverage_diagnostic_non_authority` | `SUPPORTED` |
| External Wide | AutoResearchBench Wide's official scorer is credential-free and exact for IoU/recall/precision. | Source/audit evidence only until a result archive exists | `protocol/EXTERNAL_ACCESS_AUDIT_V1.json`; `evidence/access/autoresearchbench_evaluator_layer_check.md` | `SUPPORTED` |
| External Deep official | The released LLM title judge executed for the keyless public-arXiv probe on all 600 Deep tasks; hit rate 0.000; judge control passed 9/9. | OFFICIAL_DEEP_LLM_TITLE_JUDGE via local protocol adapter; bounded probe (external_probe_not_full_multi_provider_orion) | evidence/external_results/DEEP_OFFICIAL_ARCHIVE_V1.json + DEEP_JUDGE_CONTROL_2026-08-17.json | SUPPORTED |
| External Deep exact-ID | A deterministic exact-target-ID deviation may be reported only if its frozen candidate/evaluator artifact is archived, and it may never be called the official Deep metric. | Declared non-official deviation | Candidate workflow/adapter exists; result row remains unpromoted until archive is committed | `CANNOT_CHECK` |
| Live provider | The frozen three-route arXiv/OpenAlex campaign has executed and supports a live discovery/cost claim. | Requires funded OpenAlex access before `EXECUTION_FROZEN` | `evidence/access/LIVE_PROVIDER_PREFLIGHT_2026-08-16.json` records absent `OPENALEX_API_KEY` | `CANNOT_CHECK` |
| SAGE | SAGE supports a result in this revision. | Needs published corpus/evaluator or a predeclared substitute | Corpus/evaluator absent in access audit | `CANNOT_CHECK` |
| MetaSyn | The credential-free 86-review external retrieval/screening probe completed under the pinned official MetaSyn ID-only evaluator: retrieval recall 0.7485, inclusion recall 0.5651, post-retrieval loss 0.1834, screening accuracy 0.7228. | `OFFICIAL_METASYN_ID_ONLY_EVALUATOR`; external probe, not full ORION | `evidence/external_results/METASYN_ID_ONLY_PROBE_V1.json`; corrected Actions run 31973786111 | `SUPPORTED` |
| MetaSyn errors | Across 1,677 reference-article links, the bounded MetaSyn probe has 598 retrieval false negatives, 343 additional post-retrieval screening false negatives, and 941 final false negatives. | Evaluator-side derivation that rechecks official deterministic metrics after candidate freeze | `evidence/external_results/METASYN_SCREENING_FN_LEDGER_V1.json` | `SUPPORTED` |
| Conclusion | The frozen controlled experiment supports the governance mechanisms and MetaSyn supplies completed bounded external retrieval/screening evidence; matched external discovery/stopping superiority remains open. | Offline result + bounded external probe | Historical pre-migration results summary + MetaSyn result/FN ledger | `SUPPORTED` |


| P2-X A1 | On 400 protected exact heterogeneous acquisition contracts, P2-X achieves 400/400 exact closure decisions versus 250/400 for the donor-complete available-route product; paired difference 0.375, 95% CI [0.3275, 0.4225], zero false task closures. | Protected exact P2-X result + independent verification; bounded contract only | `evidence/p2x/P2_X_PROTECTED_RESULT_V1.json`; `evidence/p2x/P2_X_INDEPENDENT_VERIFICATION_V1.json` | `SUPPORTED` |
| P2-X A2 | Route-local acquisition success and task-global scientific closure are distinct authority relations when material routes remain unresolved; an ideal product given identical semantics ties 400/400. | Protected exact P2-X result; no inherent-expressivity claim | same P2-X result/verification + `research/claim_expansion/p2/P2_X_CLAIM_EXPANSION_LEDGER_V1.md` | `SUPPORTED` |
| P2-X A3 | The same closure-authority layer improves safe stopping across genuinely different retrieval engines/providers/open-ended tasks. | No independent retriever implementations or new live multi-provider campaign | P2-X explicitly leaves deployed/retrieval-engine generality untested | `CANNOT_CHECK` |

## Promotion rule

No row marked `CANNOT_CHECK` may be rewritten as positive, negative, or null evidence. The offline +0.31282 recall difference is not promoted to H1 because the campaign's achieved `TIER_B_committed` half-width (0.0496) exceeds the frozen superiority margin (0.03), so the frozen statistical plan attaches its mandatory underpowered label to the primary offline result, and H1 itself requires externally relevant benchmark support under matched resources. The MetaSyn probe is likewise not promoted into a full ORION superiority claim because it is the declared keyless BM25 + deterministic screening probe rather than the matched multi-provider ORION system. Missing Deep-judge or OpenAlex credentials are authority failures, not zero scores, negative evidence, or zero-cost observations.
