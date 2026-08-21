# ORION papers

The paper tree is a first-class projection of the executable framework, not a historical publication archive.

## Publication identity rule

ORION has **exactly five numbered flagship papers**. A paper identity is determined by its canonical topic and directory below, not by a historical number that may appear in an old RAKL artifact.

| Canonical ID | Flagship paper | Canonical directory |
|---|---|---|
| ORION-P1 | Recursive Epistemic Reconstruction | `paper-01-recursive-epistemic-reconstruction/` |
| ORION-P2 | Open-World Scientific Knowledge Discovery | `paper-02-open-world-scientific-discovery/` |
| ORION-P3 | Global Knowledge Portrait | `paper-03-global-knowledge-portrait/` |
| ORION-P4 | Verified Scientific Discovery | `paper-04-verified-scientific-discovery/` |
| ORION-P5 | Self-ORION | `paper-05-self-orion/` |

The active `papers/` tree contains those five flagship paper directories, publication synchronization/alias files, and the candidate paper packages listed below. Historical redirect directories and the former `shadow-mechanics-v1/` paper-like path have been removed. Their mappings are recorded in `PAPER_ALIASES.md` and remain recoverable from Git history.

## Candidate paper packages

The candidate paper packages live directly under `papers/`, **one directory per paper**:

| Identity | Directory | Issue |
|---|---|---|
| ORION-P6 | `paper-06-formal-epistemic-structures-and-mechanics/` | #654 |
| ORION-P7 | `paper-07-epistemic-navigation-open-worlds/` | #655 |
| ORION-P8 | `paper-08-epistemic-authority-autonomous-science/` | #656 |
| ORION-P9 | `paper-09-structured-epistemic-learning/` | #662 |
| ORION-P10 | `paper-10-structured-problem-solving/` | #663 |
| ORION-P11 | `paper-11-state-as-computation/` | #471 |
| ORION-P12 | `paper-12-adaptive-state-reasoning/` | #665 |
| ORION-P13 | `paper-13-responsibility-carrying-state/` | #666 |
| ORION-P14 | `paper-14-orion-rse/` | #669 |
| ORION-P15 | `paper-15-orion-research-harness/` | none yet |

Three further directories under `papers/` are **not paper identities**:

- `orion-learning-machine/` — the shared P9/P10 lane: framework, experiments and committed results that the two vacated candidates below cite. Authority `LOCAL_REPRODUCIBLE_CORE_ONLY`. Recorded in `SHARED_LANES`.
- `paper-xx-executable-research-core/` — was P9; terminal `MERGED INTO P8/PROGRAMME`, no standalone manuscript.
- `paper-xx-content-bound-math-evaluation/` — was P10; terminal `TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME`.

The `paper-xx-` prefix vacates the number while keeping the record that each was a paper candidate. Neither is deleted: both hold results that live tests and other papers cite. See `PAPER_ALIASES.md` and `VACATED_PAPER_NUMBERS` in `src/orion/programme/superiority_terminals.py`.

This placement is a directory layout, not a publication identity: these packages remain **candidates** governed by the programme rules in `papers/candidates/README.md`, and nothing about the move changes the five-flagship identity rule above. The shared cross-paper apparatus (checkers, review/adjudication records, submission gate) remains under `papers/candidates/`; the ORION-Q programme has its own top-level `Q-paper-NN-*` namespace.

The former Shadow mechanics material is preserved as a **non-paper technical companion** at `research/technical-companions/mechanics-of-mechanics-v1/`. Its mechanic-cell/recursive-audit theory is owned by Paper I; its failure-learning and protected self-development theory is owned by Paper V. Discovery/stopping and authority interfaces remain owned by Papers II and IV respectively.

## Scientific synchronization rule

A paper may describe only mechanics present in the canonical ORION registry or explicitly label a mechanic as proposed/research-only. Framework-changing commits must update the paper snapshot when they alter a published mechanic, state coordinate, authority rule, saturation rule, or nearest-work/novelty boundary.

Nearest work is part of the scientific object, not a citation appendix. Each flagship claim must have a nearest-work case recording mechanisms to `ADOPT`, `ADAPT`, `COMPOSE`, `DEFER`, or `REJECT`; an open nearest-work route blocks a novelty conclusion.

Passing repository tests or obtaining a `CANDIDATE_DELTA` cannot authorize an external novelty or empirical-superiority claim. The flagship programme separates **local falsifier gates** from **external promotion gates**. A paper is not publication-ready while its external gate is `CANNOT_CHECK`.

## Current flagship status

1. **Paper I — Recursive Epistemic Reconstruction.** Scoped manuscript: explicit `K/W/M` state, typed responsibility-targeted reframing, dependency-directed reopening, the canonical mechanic-cell representation, recursive mechanic self-audit, and hidden formulation/search-universe falsification.
2. **Paper II — Open-World Scientific Knowledge Discovery.** Discovery/search paper: earned route independence, question-framed memory, route/task stopping, and recall-first evaluation.
3. **Paper III — Global Knowledge Portrait.** Absorption/synthesis paper: source projections, scientific meaning, identity/context/measurement mapping, GLUE/obstructions, typed ignorance, and recoverable portraits.
4. **Paper IV — Verified Scientific Discovery.** Scientific-authority paper: content-bound evidence, independent checks, protected evaluation, typed non-escalation, and `CANNOT_CHECK`.
5. **Paper V — Self-ORION.** Scoped manuscript: persistent failure/issue knowledge, causal discrimination, challenger/invention governance, isolated change control, replay/fresh transfer, protected assurance, negative-history retention, and no self-promotion.

## Flagship falsifier V1

The deterministic local five-paper suite passed at branch commit `8a8a7feed588363f8e2cd820d3399a33b7af3074`, CI run `31933432314`. It caused framework changes rather than merely producing scores: an over-broad Paper-I reframe gate was repaired, Paper III gained `ScientificMeaningProjection.v1`, and Paper V absorbed issue-centric persistence as `DevelopmentIssue.v1`.

The stronger external gates for **all five papers remain `CANNOT_CHECK`** until matched nearest-work baselines, fresh tasks/gold data, and protected evaluations are actually executed.

See `research/paper-programme-v1/FLAGSHIP_FALSIFIER_RESULTS_V1.md` and each paper's `evidence/FALSIFIER_V1.md`.

## Verified RSE successor synchronization — 2026-08-20

The paper programme now also consumes the bounded recursive-scientific-evolution falsifier as **successor research only**. The exact suite verifies task/standing separability, finite successor-state non-identifiability, delayed later-generation scientific errors from lost lineage, and a CEGAR refinement demonstration. Its strongest registered state-schema result is deliberately subtractive: a fixed generic justification condition language closes DPAIR-1..4 and therefore strikes bespoke projection-schema superiority on that scope.

No flagship headline claim is widened by this result. `JReach_B(F,x,C|kappa)`, mutable-framework/protected-constitution separation and reconstructive-lineage + task-relative-working-projection remain framework definitions/design principles, not newly proved universal theorems.

Canonical synchronization files:

- `RSE_VERIFIED_SUCCESSOR_HANDOFF_V1.md` — paper-tree boundary;
- `research/paper-programme-v1/RSE_P1_P10_HANDOFF_2026-08-20.md` — P1–P10 ownership map;
- `research/extensions/meta-orion-recursive-scientific-evolution/FORMAL_VERIFICATION_CLOSURE_V1.md` — executable theorem/definition disposition after final CI binding.

RAKL papers remain immutable provenance and are selectively remapped in `legacy-rakl-map.md`.
