# RAKL paper salvage ledger

Source snapshot: `SzeChunYiu/RAKL@bd4ce50f48bbfd7d36e9a41ded9566f77d8105ca` (V2 series per `publication/PUBLICATION_SERIES_V2.md`, migration `#475`).

This ledger answers one question mechanically: **which content classes of each legacy paper are salvageable, into which ORION home, under which authority rule.** It complements `papers/legacy-rakl-map.md` (paper-level dispositions) and `MIGRATION_LEDGER.md` (artifact-level dispositions).

## Salvage classes

| Class | Meaning | Authority rule |
|---|---|---|
| `MIGRATE-MECHANICS` | Formalism, contracts, typed state machinery re-derived inside ORION | Re-derivation required; the ORION version is authoritative, the RAKL text is provenance |
| `REFERENCE-EVIDENCE` | Empirical results, receipts, benchmark packets | Citable by immutable reference; mint no ORION authority until re-audited under ORION evaluation |
| `PRESERVE-NEGATIVE-HISTORY` | Failed instruments, refuted claims, invalidated diagnostics, negative frontiers | Transfer verbatim by reference; monotone — may never be weakened or reinterpreted |
| `REFERENCE-DESIGN` | Preregistrations, protocols, figure plans not yet executed | Usable as design input; execution obligations restart under ORION |
| `NOT-TRANSFERRED` | Publication statuses, review states, saturation claims, empirical headlines | Never transfer; each must be re-earned inside ORION |

## Per-paper salvage map

Every row binds the salvage to the ORION mechanic cells (`src/orion/mechanics/decomposition.py`) that consume it, so the mechanics program can treat legacy recovery as typed research input rather than prose.

### Paper I — Epistemic Mechanics (`paper-01-epistemic-mechanics/`)

| Content | Class | ORION home | Mechanic-cell binding |
|---|---|---|---|
| Claim/evidence/authority state calculus, authority ladder, noninterference boundary | MIGRATE-MECHANICS | Paper 01 manuscript; `docs/03-evaluation` | `CROSS.AUTHORITY.v0`, `ABSORB.EVIDENCE_BIND.v0` |
| Provenance/supersession/addressability rules | MIGRATE-MECHANICS | `docs/03-evaluation`; storage/provenance contracts | `CROSS.MEMORY.v0` |
| Formal recursion/fibre mechanics | MIGRATE-MECHANICS | Paper 01 §recursive engine | `FRAME.DECOMPOSE.v0`, `REOPEN.FIBRE.v0` |
| ArXiv-readiness, review posture | NOT-TRANSFERRED | — | — |

Salvage fraction: **high** — the mechanics are already load-bearing in ORION's authority rules; the manuscript's formal core is the richest single source for Paper 01.

### Paper II — Structural Mechanics / Directional Structural Witnesses (`paper-02-structural-mechanics/`)

| Content | Class | ORION home | Mechanic-cell binding |
|---|---|---|---|
| Directional witness formalism, GLUE/JUMP portals, preservation contracts | MIGRATE-MECHANICS | Paper 02 (global knowledge portrait) | `RECONSTRUCT.GLUE.v0`, `RECONSTRUCT.ATLAS_UPDATE.v0`, `ABSORB.REPRESENTATION_MAP.v0` |
| Fail-closed cross-domain transfer gates | MIGRATE-MECHANICS | Paper 02; evaluation docs | `DETECT.CONTRADICTION.v0` |
| External-validation transfer results (strongest RAKL empirical lineage; includes the absorbed sID-parent line) | REFERENCE-EVIDENCE | Paper 02 evidence ledger by reference | `CROSS.BENCHMARK.v0` |
| `READY_WITH_EXPLICIT_LIMITATIONS` status | NOT-TRANSFERRED | — | — |

Salvage fraction: **high** for formalism; evidence is reference-only until re-audited.

### Paper III — Method-Evolution Mechanics (`paper-03-method-evolution-mechanics/`)

| Content | Class | ORION home | Mechanic-cell binding |
|---|---|---|---|
| failure→diagnosis→lesson→method pipeline; episode/lesson typing | MIGRATE-MECHANICS | Paper 04 (Self-ORION); `orion.experience` substrate | `CROSS.EXPERIENCE.v0`, `DETECT.FAILURE.v0`, `DIAGNOSE.ATTRIBUTION.v0` |
| Four-arm causal attribution design; prospective metrology | MIGRATE-MECHANICS + REFERENCE-DESIGN | Paper 04; failure-learning benchmarks | `DIAGNOSE.DISCRIMINATOR.v0`, `CROSS.BENCHMARK.v0` |
| Fresh-assurance protection (anti-adaptive-reuse) | MIGRATE-MECHANICS | `docs/03-evaluation` | `CROSS.REVIEW.v0` |
| Self-application episodes (E3/E4/E9 repair licensing) | REFERENCE-EVIDENCE | Paper 04 history by reference | `REFRAME.METHOD.v0` |
| Method-promotion readiness claims | NOT-TRANSFERRED | — | — |

Salvage fraction: **high** — this paper is the direct ancestor of ORION's failure-learning substrate; its mechanics should be systematically mined before new failure-learning contracts are frozen.

### Paper IV — Structural Learning Mechanics (`paper-04-structural-learning-mechanics/`)

| Content | Class | ORION home | Mechanic-cell binding |
|---|---|---|---|
| v1 Phase-0/1 packet: generator defect, invalidated diagnostic | PRESERVE-NEGATIVE-HISTORY | `research/failures/` conventions; cited as the canonical instrument-defect exemplar | `DETECT.FAILURE.v0`, `DIAGNOSE.ATTRIBUTION.v0` |
| Preregistered protocol, learnability gate design (`#455/#461/#462/#466–468`) | REFERENCE-DESIGN | Future training-time extension only after a repaired generator | `CROSS.BENCHMARK.v0` |
| Any mechanism/capability inference from v1 | NOT-TRANSFERRED (explicitly forbidden) | — | — |

Salvage fraction: **low for claims, high for negative history** — the invalidated-instrument record is exactly the class of knowledge ORION's failure-learning must retain: an instrument negative is not a mechanism negative.

### Paper V — Verified Discovery in Mathematics (`paper-05-verified-discovery-in-mathematics/`)

| Content | Class | ORION home | Mechanic-cell binding |
|---|---|---|---|
| Assurance architecture; strict promotion path; content-identity binding (V3/V4 addenda) | MIGRATE-MECHANICS | Paper 03 (verified discovery) | `ABSORB.EVIDENCE_BIND.v0`, `CROSS.AUTHORITY.v0`, `CROSS.EXECUTION.v0` |
| Verified Transformation Geometry preregistration | REFERENCE-DESIGN (open obligation) | Paper 03 open-questions ledger; requires hidden-route held-out theorem families | `CROSS.BENCHMARK.v0` |
| Mathematical assurance receipts | REFERENCE-EVIDENCE | Paper 03 evidence by reference | — |
| `ARXIV_PREPRINT_READY` status | NOT-TRANSFERRED | — | — |

Salvage fraction: **high** — ORION Paper 03 shares this paper's target; its assurance mechanics are the natural spine.

### Paper VI — Orion Scientific Research Engine (`paper-06-rakl-scientific-research-engine/` + `publication/UNIFIED_PROBLEM_SOLVING_CROSS_PAPER_INTEGRATION.md`)

| Content | Class | ORION home | Mechanic-cell binding |
|---|---|---|---|
| Unified problem-solving cross-paper map (operational map, path-cost, solver-compilation, solution-assembly sidecars) | REFERENCE-ARCHITECTURE | Input to the mechanics decomposition and capability routing | `ORION_SOLVE.v1`, `FRAME.DECOMPOSE.v0`, `CROSS.EXPERIMENT_SELECTION.v0` |
| Engine integration narrative | REFERENCE-ARCHITECTURE | ORION repository itself (clean-generation successor) | — |
| `CAPSTONE_NOT_READY`; competitive/utility evidence | NOT-TRANSFERRED (still open in ORION too) | — | — |

Salvage fraction: **architectural only** — the ORION repo is this paper's successor; nothing in it should be migrated as settled results.

## Aggregate answer

Across the six papers, essentially **all mechanics/formalism content is salvageable** under `MIGRATE-MECHANICS` re-derivation, **all negative history is salvageable verbatim** (and is among the most valuable content, per the failure-learning doctrine), and **empirical results are salvageable as referenced receipts only**. What cannot be saved, by construction, are statuses, review states, and empirical headlines — those must be re-earned inside ORION's own evaluation. Nothing needs to be discarded.

## Open obligations created by this ledger

1. Mine Paper I/II/III/V formal cores into their ORION manuscript homes (one PR per paper; each PR must cite exact RAKL section paths).
2. Register the Paper IV instrument-defect packet as a canonical `research/failures/` exemplar with its RAKL path.
3. When the mechanics program freezes step-specific contracts for the bound cells above, the freeze packet must cite this ledger's row as recovered incumbent knowledge (development protocol step: "recover incumbent RAKL/ORION mechanics and negative history").
