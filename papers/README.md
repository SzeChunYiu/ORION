# ORION papers

The paper tree is a first-class projection of the executable framework, not a historical publication archive.

Canonical identities across the whole tree follow the single flat `ORION-NN`
registry in `PAPER_ALIASES.md`. “Flagship” below is a programme role, not a
separate numbering system. In particular, the former AB/C/D/NQ/Q1 studies are
now **ORION-01–05** (Certificate Realization, FiberGuard Finite Fibre,
Typed-Merge Falsification, Rooted Completion Certificates, and TARE
Expressivity). Their current evidence hierarchy and science-first closure gates
are controlled by `../research/orion-01-05-convergence-v1/README.md` and
`../research/orion-01-05-convergence-v1/SCIENCE_STATUS_V1.json`.

## Publication identity rule

ORION has **exactly five flagship papers**, assigned ORION-11–15 in the flat
registry. A paper identity is determined by its canonical topic and directory
below, not by a historical number that may appear in an old RAKL artifact.

| Canonical ID | Flagship paper | Canonical directory |
|---|---|---|
| ORION-11 | Recursive Epistemic Reconstruction | `orion-11-recursive-epistemic-reconstruction/` |
| ORION-12 | Open-World Scientific Knowledge Discovery | `orion-12-open-world-scientific-discovery/` |
| ORION-13 | Global Knowledge Portrait | `orion-13-global-knowledge-portrait/` |
| ORION-14 | Verified Scientific Discovery | `orion-14-verified-scientific-discovery/` |
| ORION-15 | Self-ORION | `orion-15-self-orion/` |

The active `papers/` tree contains those five flagship paper directories, publication synchronization/alias files, and the candidate paper packages listed below. Historical redirect directories and the former `shadow-mechanics-v1/` paper-like path have been removed. Their mappings are recorded in `PAPER_ALIASES.md` and remain recoverable from Git history.

## Candidate paper packages

The candidate paper packages live directly under `papers/`, **one directory per paper**:

| Identity | Directory | Issue |
|---|---|---|
| ORION-16 | `orion-16-formal-epistemic-structures-and-mechanics/` | #654 |
| ORION-17 | `orion-17-epistemic-navigation-open-worlds/` | #655 |
| ORION-18 | `orion-18-epistemic-authority-autonomous-science/` | #656 |
| ORION-19 | `orion-19-structured-epistemic-learning/` | #662 |
| ORION-20 | `orion-20-structured-problem-solving/` | #663 |
| ORION-21 | `orion-21-state-as-computation/` | #471 |
| ORION-22 | `orion-22-adaptive-state-reasoning/` | #665 |
| ORION-23 | `orion-23-responsibility-carrying-state/` | #666 |
| ORION-24 | `orion-24-orion-rse/` | #669 |
| ORION-25 | `orion-25-orion-research-harness/` | none yet |

Three further directories under `papers/` are **not paper identities**:

- `orion-learning-machine/` — the shared ORION-19/ORION-20 lane: framework, experiments and committed results that the two vacated candidates below cite. Authority `LOCAL_REPRODUCIBLE_CORE_ONLY`. Recorded in `SHARED_LANES`.
- `paper-xx-executable-research-core/` — was ORION-19; terminal `MERGED INTO ORION-18/PROGRAMME`, no standalone manuscript.
- `archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation/` — was ORION-20; terminal `TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME`.

The `paper-xx-` prefix vacates the number while keeping the record that each was a paper candidate. Neither is deleted: both hold results that live tests and other papers cite. See `PAPER_ALIASES.md` and `VACATED_PAPER_NUMBERS` in `src/orion/programme/superiority_terminals.py`.

This placement is a directory layout, not a publication identity: these packages remain **candidates** governed by the programme rules in `papers/candidates/README.md`, and nothing about the move changes the five-flagship identity rule above. The shared cross-paper apparatus (checkers, review/adjudication records, submission gate) remains under `papers/candidates/`; the ORION-Q programme has its own top-level `Q-paper-NN-*` namespace.

The former Shadow mechanics material is preserved as a **non-paper technical companion** at `research/technical-companions/mechanics-of-mechanics-v1/`. Its mechanic-cell/recursive-audit theory is owned by Paper I; its failure-learning and protected self-development theory is owned by Paper V. Discovery/stopping and authority interfaces remain owned by Papers II and IV respectively.

## Scientific synchronization rule

A paper may describe only mechanics present in the canonical ORION registry or explicitly label a mechanic as proposed/research-only. Framework-changing commits must update the paper snapshot when they alter a published mechanic, state coordinate, authority rule, saturation rule, or nearest-work/novelty boundary.

Nearest work is part of the scientific object, not a citation appendix. Each flagship claim must have a nearest-work case recording mechanisms to `ADOPT`, `ADAPT`, `COMPOSE`, `DEFER`, or `REJECT`; an open nearest-work route blocks a novelty conclusion.

Passing repository tests or obtaining a `CANDIDATE_DELTA` cannot authorize an external novelty or empirical-superiority claim. The flagship programme separates **local falsifier gates** from **external promotion gates**. A paper is not publication-ready while its external gate is `CANNOT_CHECK`.

The full framework/paper/Q-series rules are in `SYNC_CONTRACT.md`.

## Current flagship status

1. **Paper I — Recursive Epistemic Reconstruction.** Scoped manuscript: explicit `K/W/M` state, typed responsibility-targeted reframing, dependency-directed reopening, the canonical mechanic-cell representation, recursive mechanic self-audit, and hidden formulation/search-universe falsification. Its broad historical H1 remains unsupported at 1/48 root successes for both subject and strongest baseline. A narrower credential-free mechanical successor replays exactly, but R4 shows that a faithful ordered-search comparator matches the governed policy on all 480 primary hidden-shift worlds. Comparative mechanism necessity is therefore withdrawn; the R4 replication remains `CANNOT_CHECK` after its anchor gate failed, and local replay creates neither external authority nor submission readiness.
2. **Paper II — Open-World Scientific Knowledge Discovery.** Discovery/search paper: earned route independence, question-framed memory, route/task stopping, and recall-first evaluation.
3. **Paper III — Global Knowledge Portrait.** Absorption/synthesis paper: source projections, scientific meaning, identity/context/measurement mapping, GLUE/obstructions, typed ignorance, and recoverable portraits.
4. **Paper IV — Verified Scientific Discovery.** Scientific-authority paper: content-bound evidence, independent checks, protected evaluation, typed non-escalation, and `CANNOT_CHECK`.
5. **Paper V — Self-ORION.** Scoped manuscript: persistent failure/issue knowledge, causal discrimination, challenger/invention governance, isolated change control, replay/fresh transfer, protected assurance, negative-history retention, and no self-promotion.

## Flagship falsifier V1

The deterministic local five-paper suite passed at branch commit `8a8a7feed588363f8e2cd820d3399a33b7af3074`, CI run `31933432314`. It caused framework changes rather than merely producing scores: an over-broad Paper-I reframe gate was repaired, Paper III gained `ScientificMeaningProjection.v1`, and Paper V absorbed issue-centric persistence as `DevelopmentIssue.v1`.

The stronger external gates for **all five papers remain `CANNOT_CHECK`** until matched nearest-work baselines, fresh tasks/gold data, and protected evaluations are actually executed.

See `research/paper-programme-v1/FLAGSHIP_FALSIFIER_RESULTS_V1.md` and each paper's `evidence/FALSIFIER_V1.md`.

## Verified RSE successor synchronization — 2026-08-20

The paper programme now also consumes the bounded recursive-scientific-evolution falsifier as **successor research only**. The exact suite verifies task/standing separability, finite successor-state non-identifiability, delayed later-generation scientific errors from lost lineage, and a CEGAR refinement demonstration. Its strongest registered state-schema result is deliberately subtractive: `GENERIC_JUSTIFICATION_DONOR_SUFFICIENT`. A fixed generic justification condition language closes DPAIR-1..4 and therefore removes bespoke projection-schema superiority on that scope.

This is earned scope narrowing and must remain visible as negative science. It is not a setup failure, and no flagship headline or superiority claim is widened by it. `JReach_B(F,x,C|kappa)`, mutable-framework/protected-constitution separation and reconstructive-lineage + task-relative-working-projection remain framework definitions/design principles, not newly proved universal theorems.

Canonical synchronization files:

- `RSE_VERIFIED_SUCCESSOR_HANDOFF_V1.md` — paper-tree boundary;
- `research/paper-programme-v1/RSE_P1_P10_HANDOFF_2026-08-20.md` — ORION-11–ORION-20 ownership map;
- `research/extensions/meta-orion-recursive-scientific-evolution/FORMAL_VERIFICATION_CLOSURE_V1.md` — executable theorem/definition disposition after final CI binding.

## ORION-Q publication wave — final internal spec 2026-08-22

The historical ORION-Q programme has a separate four-paper publication wave.
These packages are outside the five-paper **flagship** programme, but their
canonical identities are ORION-05–08 in the same flat `ORION-NN` registry.
“Closed” in the older wave record refers only to that bounded internal spec; it
does not override the current ORION-05 science and authority gates linked
above.

The machine-readable publication contract is `Q_SERIES_FINAL_SPEC_V1.json`; the human readiness record is `Q_SERIES_FINAL_READINESS_2026-08-22.md`. Canonical publication bytes are protected by `Q_SERIES_CONTENT_BINDING_V1.json`, and the framework/harness checks are defined in `src/orion/programme/q_series_sync.py` and `packages/orion-research-harness/src/orion_research_harness/publication_contract.py`.

| Q paper | Role | Canonical manuscript | Current bounded internal status |
|---|---|---|---|
| `orion-05-tare-expressivity/` | quantum-compilation mathematics | `MANUSCRIPT_SUBMISSION_DRAFT.md` | bounded `kappa_R6M=2` core/package complete; current science closure, runtime candidate, external-authority, and submission gates remain open under convergence V1 |
| `orion-06-recursive-recovery/` | negative-result recovery methodology | `MANUSCRIPT_V2.md` | complete single-programme case study; cross-domain protocol is optional successor research |
| `orion-07-dual-instrument/` | scientific decision instruments / deferred scoring | `MANUSCRIPT_V2.md` | complete systems/benchmark-definition paper with one V0 measurement; calibration study deferred |
| `orion-08-typed-state/` | typed/scoped epistemic state under partial knowledge | `MANUSCRIPT_V2.md` | complete exact-synthetic mechanism/benchmark paper; real-domain study deferred |

Each Q directory now carries a `REPRODUCE.md` and `SUBMISSION_PACKAGE.md` in addition to its canonical manuscript/ledger materials.

The owner elected to skip a separate external quantum-expert pre-review for ORION-05. The final spec records `SKIPPED_BY_OWNER`; this is not encoded as a scientific PASS and does not create external novelty/quantum authority.

### ORION-05 theorem status

For the frozen R6M shared-Tag TARE-M2 grammar/support-count objective:

- an analytic all-`n` exchange proof gives support <=2 sufficiency;
- the complete support-one family has an exact `n=2` counterexample (`5 < 6`);
- therefore the intrinsic uniform frame-support number is exactly `kappa_R6M = 2`;
- the proof's only weight-two parity obstruction is realized by the exact frame-for-Tag coupling witness;
- the original large finite enumerations remain independent verification, not the logical basis of the publication proof;
- a final exact-statement literature refresh records `NOT_LOCATED_IN_BOUNDED_SEARCH__NOT_NOVELTY_CERTIFICATE` rather than claiming absolute novelty.

Canonical proof/novelty artifacts include `HUMAN_PROOF_R6S_2026-08-22.md`, `CLAIM_LEDGER_V2.md`, `NOVELTY_RESEARCH_2026-08-22.md`, `NOVELTY_REFRESH_FINAL_2026-08-22.md`, and `FIGURES_PLAN_V2.md`.

### Q/QG claim boundary

ORION-QG remains a separate successor publication wave. Q papers may cite QG to disclose later limitations/follow-up, but must not back-port QG novelty into Q claims. In particular, later R6I support-one, objective cones, SixLCU/StabPrep results and refined support-two TARE subregimes belong to QG papers.

RAKL papers remain immutable provenance and are selectively remapped in `legacy-rakl-map.md`.
