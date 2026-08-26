# ORION paper alias registry (machine-readable)

Single source of truth for historical ORION paper-directory and paper-id aliases.
All `old_dir`/`new_dir` values below are relative to `papers/` (no `papers/`
prefix, so this registry never matches repo-wide old-path gates).

- date: 2026-08-27 (moves executed 2026-08-26)
- reason: operator naming-unification directive 2026-08-26 — "rename all papers,
  too many namings like pn and alphabets and others"
  (`PAPER_PORTFOLIO_REFACTOR_PLAN_V1.md` §2, Wave R0)
- receipt: `PAPER_RENAME_RECEIPT_V1.json` (schema `ORION.Papers.RenameReceipt.v1`)
- one flat series `ORION-NN` ↔ directory `orion-NN-<slug>/`; ORION-26..28 are
  reserved for the future P16/P17/P18 candidates (set at authorization).

```yaml
schema: ORION.Papers.AliasRegistry.v1
id_aliases:
  # old bare id -> new ORION-NN id
  - {old: NQ,            new: ORION-04}
  - {old: theory-A,      new: ORION-01}
  - {old: theory-B,      new: ORION-01}
  - {old: theory-C,      new: ORION-02}
  - {old: theory-D,      new: ORION-03}
  - {old: Q1,            new: ORION-05}
  - {old: Q2,            new: ORION-06}
  - {old: Q3,            new: ORION-07}
  - {old: Q4,            new: ORION-08}
  - {old: QG1,           new: ORION-09}
  - {old: QG2,           new: ORION-10}
  - {old: P1,            new: ORION-11}
  - {old: P2,            new: ORION-12}
  - {old: P3,            new: ORION-13}
  - {old: P4,            new: ORION-14}
  - {old: P5,            new: ORION-15}
  - {old: P6,            new: ORION-16}
  - {old: P7,            new: ORION-17}
  - {old: P8,            new: ORION-18}
  - {old: P9,            new: ORION-19}
  - {old: P10,           new: ORION-20}
  - {old: P11,           new: ORION-21}
  - {old: P12,           new: ORION-22}
  - {old: P13,           new: ORION-23}
  - {old: P14,           new: ORION-24}
  - {old: P15,           new: ORION-25}
dir_aliases:
  # old_dir -> new_dir, both relative to papers/; archived targets keep old basenames
  - {old_dir: theory-A-multitag-constraint-rank,          new_dir: orion-01-certificate-realization, kind: merged-into}
  - {old_dir: theory-B-certificate-complexity,            new_dir: orion-01-certificate-realization, kind: merged-into}
  - {old_dir: theory-C-low-order-information,             new_dir: orion-02-fiberguard-finite-fibre, kind: renamed}
  - {old_dir: theory-D-falsification-authority,           new_dir: orion-03-typed-merge-falsification, kind: renamed}
  - {old_dir: nonquantum-c5cubed-davenport,               new_dir: orion-04-rooted-completion-certificates, kind: renamed}
  - {old_dir: Q-paper-01-tare-expressivity,               new_dir: orion-05-tare-expressivity, kind: renamed}
  - {old_dir: Q-paper-02-recursive-recovery,              new_dir: orion-06-recursive-recovery, kind: renamed}
  - {old_dir: Q-paper-03-dual-instrument,                 new_dir: orion-07-dual-instrument, kind: renamed}
  - {old_dir: Q-paper-04-typed-state,                     new_dir: orion-08-typed-state, kind: renamed}
  - {old_dir: QG-paper-01-compilation-regime-geometry,    new_dir: orion-09-compilation-regime-geometry, kind: renamed}
  - {old_dir: QG-paper-02-certified-static-forecasting,   new_dir: orion-10-certified-static-forecasting, kind: renamed}
  - {old_dir: paper-01-recursive-epistemic-reconstruction,   new_dir: orion-11-recursive-epistemic-reconstruction, kind: renamed}
  - {old_dir: paper-02-open-world-scientific-discovery,      new_dir: orion-12-open-world-scientific-discovery, kind: renamed}
  - {old_dir: paper-03-global-knowledge-portrait,            new_dir: orion-13-global-knowledge-portrait, kind: renamed}
  - {old_dir: paper-04-verified-scientific-discovery,        new_dir: orion-14-verified-scientific-discovery, kind: renamed}
  - {old_dir: paper-05-self-orion,                           new_dir: orion-15-self-orion, kind: renamed}
  - {old_dir: paper-06-formal-epistemic-structures-and-mechanics, new_dir: orion-16-formal-epistemic-structures-and-mechanics, kind: renamed}
  - {old_dir: paper-07-epistemic-navigation-open-worlds,         new_dir: orion-17-epistemic-navigation-open-worlds, kind: renamed}
  - {old_dir: paper-08-epistemic-authority-autonomous-science,  new_dir: orion-18-epistemic-authority-autonomous-science, kind: renamed}
  - {old_dir: paper-09-structured-epistemic-learning,            new_dir: orion-19-structured-epistemic-learning, kind: renamed}
  - {old_dir: paper-10-structured-problem-solving,               new_dir: orion-20-structured-problem-solving, kind: renamed}
  - {old_dir: paper-11-state-as-computation,                     new_dir: orion-21-state-as-computation, kind: renamed}
  - {old_dir: paper-12-adaptive-state-reasoning,                 new_dir: orion-22-adaptive-state-reasoning, kind: renamed}
  - {old_dir: paper-13-responsibility-carrying-state,            new_dir: orion-23-responsibility-carrying-state, kind: renamed}
  - {old_dir: paper-14-orion-rse,                                new_dir: orion-24-orion-rse, kind: renamed}
  - {old_dir: paper-15-orion-research-harness,                   new_dir: orion-25-orion-research-harness, kind: renamed}
  - {old_dir: QG-paper-03-intrinsic-support-numbers,          new_dir: candidates/qg-paper-03-stub, kind: stub-to-candidates}
  - {old_dir: paper-02-global-knowledge-portrait,             new_dir: archive/2026-08-pre-unification/paper-02-global-knowledge-portrait, kind: archived}
  - {old_dir: paper-03-verified-discovery,                    new_dir: archive/2026-08-pre-unification/paper-03-verified-discovery, kind: archived}
  - {old_dir: paper-04-self-orion,                            new_dir: archive/2026-08-pre-unification/paper-04-self-orion, kind: archived}
  - {old_dir: paper-xx-content-bound-math-evaluation,         new_dir: archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation, kind: archived}
file_aliases:
  # theory-A/B collision files (kept both, prose NOT merged) + archived manuscript cuts
  - {old: theory-A-multitag-constraint-rank/MANUSCRIPT_V2.md,    new: orion-01-certificate-realization/theory-A-MANUSCRIPT_V2.md}
  - {old: theory-A-multitag-constraint-rank/CLAIM_LEDGER.md,     new: orion-01-certificate-realization/theory-A-CLAIM_LEDGER.md}
  - {old: theory-A-multitag-constraint-rank/CLAIM_LEDGER_R2.md,  new: orion-01-certificate-realization/theory-A-CLAIM_LEDGER_R2.md}
  - {old: theory-B-certificate-complexity/MANUSCRIPT_V2.md,      new: orion-01-certificate-realization/theory-B-MANUSCRIPT_V2.md}
  - {old: theory-B-certificate-complexity/CLAIM_LEDGER.md,       new: orion-01-certificate-realization/theory-B-CLAIM_LEDGER.md}
  - {old: theory-B-certificate-complexity/CLAIM_LEDGER_R2.md,    new: orion-01-certificate-realization/theory-B-CLAIM_LEDGER_R2.md}
  - {old: theory-A-multitag-constraint-rank/MANUSCRIPT_V1.md,    new: archive/2026-08-pre-unification/theory-A-multitag-constraint-rank/MANUSCRIPT_V1.md}
  - {old: theory-B-certificate-complexity/MANUSCRIPT_V1.md,      new: archive/2026-08-pre-unification/theory-B-certificate-complexity/MANUSCRIPT_V1.md}
  - {old: Q-paper-01-tare-expressivity/MANUSCRIPT_V3_REFINED.md, new: orion-05-tare-expressivity/MANUSCRIPT_V3_REFINED.md, note: canonical Q1 manuscript}
  - {old: Q-paper-01-tare-expressivity/MANUSCRIPT_V1.md,         new: archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V1.md}
  - {old: Q-paper-01-tare-expressivity/MANUSCRIPT_V2.md,         new: archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V2.md}
  - {old: Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md,         new: archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_V3.md}
  - {old: Q-paper-01-tare-expressivity/MANUSCRIPT_SUBMISSION_DRAFT.md, new: archive/2026-08-pre-unification/Q-paper-01-tare-expressivity/MANUSCRIPT_SUBMISSION_DRAFT.md}
archived_root_files:
  # old papers/<name> -> papers/archive/2026-08-pre-unification/<name>
  - FIVE_PAPER_REVIEW_SYNTHESIS_2026-08-24.md
  - FIVE_THEORY_PAPERS_FIGURE_CONTRACTS_2026-08-24.md
  - Q_QG_VENUE_TARGET_MATRIX_V1.md
  - Q_QG_PUBLICATION_READINESS_V2.md
  - Q_QG_TARGET_PACKAGE_MANIFESTS_V1.json
  - check_q_qg_target_packages.py
  - build_q_qg_figures.py
retained_outside_series:
  # infrastructure / snapshots that intentionally keep their names
  - paper-xx-executable-research-core   # live ASlib benchmark harness (ORION-02 lane)
  - candidates/paper-06..paper-14       # preserved pre-refactor candidate snapshots
  - candidates/qg-paper-03-stub         # QG3 stub (moved from the retired QG-paper-03 dir)
```

Historical ids inside `research/orion-v1-freeze/` (digest-bound, never edited)
and inside archived material keep their original spelling; this registry is the
bridge. Pre-ORION ids such as `paper-01-epistemic-mechanics/` refer to the
external RAKL repository (`SzeChunYiu/RAKL`) and are NOT part of this mapping.
