# ORION-P5 claim ledger V1

Every abstract, results, limitations and conclusion claim in this revision maps to an archived artifact. A row is `SUPPORTED` only when the cited artifact exists and the stated authority matches that artifact. **H1–H4 remain `CANNOT_CHECK`.** The diagnostic attribution archive is **21/24**, not a perfect score.

| Claim surface | Claim allowed in this revision | Authority | Supporting artifact | Status |
| --- | --- | --- | --- | --- |
| Abstract | Local hostile tests establish implementation and governance semantics only. | IMPLEMENTED CONTRACT | `evidence/FALSIFIER_V1.md` | `SUPPORTED` |
| Abstract | Governed self-improvement on fresh development tasks remains `CANNOT_CHECK`. | EXTERNAL NOT EXECUTED | `protocol/PROTOCOL_V1.json` `execution_bindings=UNBOUND` | `SUPPORTED` |
| Abstract | Diagnostic glm-5.2 hidden-cause attribution scores 21/24 with three residual errors retained; this does not establish transferable self-improvement. | DESCRIPTIVE ONLY | `evidence/glm-5.2-attribution/results.jsonl` | `SUPPORTED` |
| Results | Raw-record accuracy is 21/24 with Wilson 95% interval in Table P5-3. | DESCRIPTIVE ONLY | `evidence/tables/P5-3_cause_confusion.json` | `SUPPORTED` |
| Results | Residual errors are `P5-HC-002` (RETRIEVAL_MISS → REPRESENTATION_GAP), `P5-HC-012` (ENVIRONMENT_DEPENDENCY_TOOL_FAILURE → IMPLEMENTATION_BUG), `P5-HC-018` (REPRESENTATION_GAP → METHOD_BASIS_GAP). | DESCRIPTIVE ONLY; FAILURES RETAINED | `evidence/tables/P5-ATTRIBUTION_RESIDUAL_ERRORS.json` | `SUPPORTED` |
| Results | Figures/tables P5-2, P5-4, P5-5, P5-6, P5-7 and Tables P5-T2/P5-T3 remain `CANNOT_CHECK`. | EXTERNAL NOT EXECUTED | `evidence/tables/INDEX.json` | `SUPPORTED` |
| Conclusion | H1 transferable protected fresh-task improvement versus matched baselines remains `CANNOT_CHECK`. | EXTERNAL NOT EXECUTED | `protocol/PROTOCOL_V1.json` | `SUPPORTED` |
| Limitations | The 21/24 archive is single-model, single-run, n=24, and is not a matched baseline/ablation campaign. | HONEST BOUNDARY | `manuscript/sections/10-limitations.tex` | `SUPPORTED` |

## Residual errors (not successes)

These three rows are incorrect attributions. They are not retries, exclusions, or successes.

| case_id | gold | attributed | confidence |
| --- | --- | --- | --- |
| P5-HC-002 | RETRIEVAL_MISS | REPRESENTATION_GAP | MEDIUM |
| P5-HC-012 | ENVIRONMENT_DEPENDENCY_TOOL_FAILURE | IMPLEMENTATION_BUG | HIGH |
| P5-HC-018 | REPRESENTATION_GAP | METHOD_BASIS_GAP | HIGH |

## Promotion rule

No row marked `CANNOT_CHECK` may be rewritten as positive evidence. The 21/24 attribution result is descriptive-only and does not support H1–H4. A stale perfect-score report is an `EXECUTION_IDENTITY_BOUNDARY_MIXUP`-class failure (`research/failures/2026-08-p5-live-artifact-branch-identity-mismatch/`) and is refused by `python -m orion.study.p5.tables`.

A new live campaign is `CANNOT_CHECK` in this revision: provider/verifier credentials are unset, and the #8 live-trial packet still has `corpus_revision: UNBOUND` on `origin/main`.
