# P2 claim ledger V1

This ledger is intentionally narrower than the original paper ambition. A row is `SUPPORTED` only when the cited artifact exists in the repository and the stated authority matches that artifact. External discovery benefit remains `CANNOT_CHECK`.

| Claim surface | Claim allowed in this revision | Authority | Supporting artifact | Status |
| --- | --- | --- | --- | --- |
| Abstract | ORION's route/read/stopping governance is implemented and survives the controlled complete-gold mechanism tests. | 20-task offline companion, descriptive only | `evidence/offline_results/RESULTS_SUMMARY_V1.json`; frozen record digest `611808dc…` | `SUPPORTED` |
| Abstract | ORION improves real scientific-literature discovery over BM25/dense/agentic baselines. | Requires external Wide/Deep or other denominator-valid benchmark result | No system result archived | `CANNOT_CHECK` |
| Results | Full ORION mean complete-gold recall is 0.994444 on the frozen controlled index; strongest frozen confirmatory baseline is 0.666667; descriptive difference +0.327777. | `DESCRIPTIVE_ONLY`, n=20 < frozen inferential n=97 | `RESULTS_SUMMARY_V1.json` | `SUPPORTED` |
| Results | Full ORION has zero premature task closures in the controlled companion; the strongest confirmatory baseline has rate 1.0. | `DESCRIPTIVE_ONLY` | `RESULTS_SUMMARY_V1.json`; `TABLE_P2-3_failure_taxonomy.md` | `SUPPORTED` |
| Mechanism H2 | Removing route-independence governance lowers controlled-index recall to 0.444444 and closes prematurely on all tasks. | Negative ablation, descriptive only | `RESULTS_SUMMARY_V1.json` → `mechanism_checks.route_independence` | `SUPPORTED` |
| Mechanism H3 | Allowing a route stop to certify task closure lowers recall to 0.333333 and produces premature closure on all tasks. | Negative ablation, descriptive only | `RESULTS_SUMMARY_V1.json` → `mechanism_checks.route_task_stop_separation` | `SUPPORTED` |
| Mechanism H4 | Removing the question coordinate suppresses legitimate rereads on extraction-shift tasks (4.0 → 1.0) but does not change aggregate recall in this controlled suite. | Mechanism diagnostic, descriptive only | `RESULTS_SUMMARY_V1.json` → `mechanism_checks.question_conditioned_read_ledger` | `SUPPORTED` |
| Safety | Treating an unavailable route as closed converts one censored case into an asserted premature closure without changing aggregate recall. | Safety negative control, descriptive only | `RESULTS_SUMMARY_V1.json` → `mechanism_checks.unavailable_route_open_state` | `SUPPORTED` |
| Efficiency mechanism | Removing content-identity dedup raises duplicate processing to 0.101429 and creates five budget-exhaustion failures. | Mechanism diagnostic, descriptive only | `RESULTS_SUMMARY_V1.json`; failure taxonomy | `SUPPORTED` |
| Coverage estimator | Coverage diagnostics do not certify completeness; the negative authority ablation closes prematurely on all tasks. | Safety negative control, descriptive only | `RESULTS_SUMMARY_V1.json` → `mechanism_checks.coverage_diagnostic_non_authority` | `SUPPORTED` |
| External Wide | AutoResearchBench Wide's official scorer is credential-free and exact for IoU/recall/precision; this is a runnability statement, not a system result. | Source/audit evidence | `protocol/EXTERNAL_ACCESS_AUDIT_V1.json`; `evidence/access/autoresearchbench_evaluator_layer_check.md` | `SUPPORTED` |
| External Deep | Official Deep scoring has been completed for ORION. | Needs OpenAI-compatible judge execution | No judge run archived | `CANNOT_CHECK` |
| SAGE | SAGE supports a result in this revision. | Needs published corpus/evaluator or a predeclared substitute | Corpus/evaluator absent in access audit | `CANNOT_CHECK` |
| MetaSyn | MetaSyn retrieval/screening result has been completed. | End-to-end execution required | Runnability audited, no system result archived | `CANNOT_CHECK` |
| Conclusion | The frozen controlled experiment supports the governance mechanisms; externally supported discovery/stopping superiority remains open. | Combination of offline result + access audit | Results summary + external access audit | `SUPPORTED` |

## Promotion rule

No row marked `CANNOT_CHECK` may be rewritten as positive, negative, or null evidence. The offline +0.327777 recall difference is not promoted to H1 because the frozen statistical plan classifies n=20 as `DESCRIPTIVE_ONLY`, and H1 itself requires externally relevant benchmark support under matched resources.
