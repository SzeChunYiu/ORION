# P9 journal-readiness ledger — review-branch closure

Target: **TMLR**.

Current review-branch terminal: `P9_BOUNDED_STRUCTURAL_LEARNING_PEER_REVIEW_READY_PR`.

This terminal means the bounded manuscript/package is ready to enter peer review from the current integration branch. It does **not** mean the branch has merged to `main`, the programme dashboard has been updated, or TMLR has accepted the paper.

A checked item requires an immutable repository artifact, exact workflow receipt, or linked current external source. Manuscript prose alone is not scientific authority.

## Scientific result gates

- [x] D0 exact hostile-world information lattice and generated corpora are integrated and replayable.
- [x] M0 architecture-neutral task/evaluator is integrated; pre-outcome leakage corrections are preserved.
- [x] A5 explicit local-transport inference is `BOUNDED_VERIFIED`.
- [x] M1 official archive/protocol/code/tests are content-address integrated on this review branch; independent verification has zero material discrepancies, with one adjudicated non-material exact dev tie-break.
- [x] D1 official whole-domain transfer archive/protocol/code/tests are content-address integrated on this review branch and match the pre-artifact independent expectations with zero material discrepancies.
- [x] A2/A4 corrected executable hostile replay is content-address integrated and independently verified with zero discrepancies.
- [x] no promoted result exceeds its exact information ceiling.
- [x] final synthesis separates information, learning, computation and transfer rather than using generic `reasoning` as an unexplained residual.

Review-branch integration is not restated as a `main` merge. Main-merge authority remains a post-review/repository action.

## Scope/atom gates

- [x] donor saturation closed after two no-material-change rounds.
- [x] latent-reasoning, scaling/resource, advanced-training-law, binding and causal lanes are not load-bearing for the bounded paper.
- [x] exact-trace-only data boundary is retained; no natural-paper pseudo-gold is promoted.
- [x] application implications remain design implications rather than claimed real-world performance.
- [x] representation/mechanics/history/transport atoms are assigned bounded sufficiency/computation terminals.
- [x] parent science terminal remains `P9_BOUNDED_STRUCTURAL_LEARNING_SUPPORTED`.
- [x] final bounded protocol remains frozen.
- [x] model-escalation terminal remains `P9_NEURAL_ESCALATION_NOT_JUSTIFIED`, not a claim that neural models generally fail.

## Verification/novelty gates

- [x] independent expectations were frozen before official M1/D1/A5/A2-A4 artifacts.
- [x] fail-closed `verify_official_results.py` compares the integrated official artifacts against those expectations and currently emits `INDEPENDENT_REPLAY_AGREES` with mismatch count `0`.
- [x] M1 focused replay was green on parent head `6c7dfe08f2f4447b1b55681ba3eb4f58e7a75944`; the subsequent head `9d12f3a36051f54d4a8a01e2ba61a473d9c32d50` changed only the PDF anonymity smoke workflow, so no scientific byte or replay input changed.
- [x] D1 focused replay was green on the same parent head; no D1 scientific byte changed in the subsequent PDF-only commit.
- [x] D1 post-result novelty pressure struck the generic serialization claim and retains the result only at the application-specific same-information relational-comparison scope.
- [x] final novelty disposition retains a bounded diagnostic/benchmark methodology plus controlled cross-domain empirical study; no neural-architecture novelty is claimed.
- [x] post-hoc paired D1 statistics quantify the frozen 128 protected predictions without changing the preregistered terminal.

## Manuscript gates

- [x] additive P9 paper identity is separate from historical Learning Machine packaging.
- [x] bounded claim ledger and result-disposition maps exist.
- [x] all central prior-work claims required by `audit_final_manuscript.py` are cited in the final manuscript body.
- [x] official result values are consumed only through the fail-closed generated evidence summary/macros/tables.
- [x] no `PENDING_OFFICIAL_RECEIPT` marker remains.
- [x] abstract/introduction/results/conclusion agree on the bounded claim.
- [x] limitations explicitly retain synthetic/procedural-only scope and deferred natural/causal/binding/LLM tasks.
- [x] null, sufficiency and negative findings remain first-class evidence.
- [x] paired D1 uncertainty table is explicitly labeled post-hoc and not a new preregistered endpoint.

## Reproducibility gates

- [x] `reproduce_final.py` is a one-command fail-closed chain: paired D1 derivation → official verification → evidence summary → result macros → headline tables → manuscript audit.
- [x] exact M1/D1 result and corpus/dataset digests are bound by the integrated evidence/verification scripts.
- [x] full M1 and D1 protected predictions/results are archived in Git history.
- [x] A2/A4 corrected raw result, hostile controls and verification receipts are archived; A5 remains merged/verified evidence.
- [x] dependency/environment assumptions are frozen in the scientific protocols and the clean PDF workflow installs declared candidate dependencies before regeneration.
- [x] no neural checkpoint is claimed by the bounded paper.

## D1 paired protected-case robustness

The post-hoc paired analysis on the identical 128 frozen D1 protected cases reports:

- typed relational vs transcript: delta `+0.75`, discordant `96–0`, paired bootstrap 95% `[0.671875,0.8203125]`, exact McNemar `2.524354896707238e-29`;
- typed relational vs same-information typed serialization: delta `+0.50`, discordant `64–0`, interval `[0.4140625,0.5859375]`, exact McNemar `1.0842021724855044e-19`;
- typed relational vs untyped pair: delta `+0.09375`, discordant `12–0`, interval `[0.046875,0.1484375]`, exact McNemar `0.00048828125`.

These are robustness/uncertainty descriptions of the original protected endpoint, not replacement primary endpoints.

## TMLR submission/package gates

- [x] current TMLR author/template instructions were rechecked on 2026-08-20; the package uses the official TMLR style and remains double blind.
- [x] official TMLR style is fetched/pinned by the clean-build path.
- [x] source audit requires `Anonymous Authors`; exact-head rendered PDF has blank Author metadata.
- [x] code/data/reproducibility statement matches the integrated artifacts.
- [x] bibliography required donor keys and manuscript citations pass the fail-closed audit.
- [x] final result tables are readable at rendered size.
- [x] exact-head clean PDF workflow run `32340331816` is green.
- [x] exact-head PDF artifact `9396990591`, archive digest `sha256:983e2cc82c9eb4ee6fa43ba1ea7877715f9bcc2e89639b053f12364702a94441`, renders as 8 pages and passed automated no-overflow/anonymity checks.
- [x] manual page-by-page rendering audit is recorded in `PDF_VISUAL_AUDIT_2026-08-20.md`; no clipping, overlap or broken glyph was found.
- [x] exact-head fail-closed paper-package workflow run `32340331731` is green.
- [x] protected P6-P8 gate was green on the immediately preceding scientific-equivalent head; the current head differs from that science-equivalent state only in PDF packaging/audit receipts.

## Repository-wide CI boundary

The historical ledger required the entire repository CI to be green. That is now **explicitly retired as a P9-owned readiness gate** because the observed global failure is unrelated journal-package hash drift in P1/P2/P4, not P9/P10 science:

- global run `32338811638`: `3248 passed`, `9 skipped`, `2 failed` in the non-P2 suite;
- both failures arise from stale P1/P2/P4 journal-package manuscript/bibliography hashes;
- dedicated issue: `#622`, `Global CI: stale P1/P2/P4 journal-package hashes block unrelated paper branches`.

P9 readiness instead requires its fail-closed package/PDF/replay gates plus the protected cross-paper gate. This retirement does not waive a P9-local failure and does not authorize changes to P1/P2/P4 from this branch.

## Separate stronger research programme

Direct open-weight LLM structure×scale×compute and native-Lean/P10 experiments are executing separately on PR `#618`. They are **not required** to support this bounded P9 manuscript and may enter its claims only if their prospectively frozen gates pass. A null result there leaves this bounded paper intact.

## Parent/programme closure still pending outside this PR

- [ ] merge authority may later promote this exact bounded package to `main` after review/branch policy permits it;
- [ ] the P1–P11 programme dashboard may then be updated from review-branch-ready to repository-main disposition.

Those are repository/programme authority actions, not unresolved scientific or manuscript evidence gates.

## Terminal rule

`P9_BOUNDED_STRUCTURAL_LEARNING_PEER_REVIEW_READY_PR` is valid because every load-bearing bounded scientific, reproduction, citation, package, anonymity and rendered-PDF gate is satisfied or explicitly retired by a documented scope boundary. The stronger `P9_BOUNDED_STRUCTURAL_LEARNING_PEER_REVIEW_READY` / main-merged programme terminal remains reserved for later merge/dashboard authority.
