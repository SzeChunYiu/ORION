# Tier-B submission-day literature crosswalk — 2026-09-02

**Date:** 2026-09-02
**Authority:** unbound tier-level registry (ORION-paper issue #78 cross-cutting
box: "Submission-day literature refresh per paper"). It indexes where each
paper's filing-day nearest-work dispositions live. It adds no claim, edits no
frozen file, and sits outside every package `SHA256SUMS` manifest.

## Why a crosswalk

Five Tier-B objects carry their submission-day refresh inside **SHA256-bound**
package files (editing them would trigger a rebind cascade with zero content
benefit). Those files already contain per-work prose dispositions. Two objects
(orion-12, orion-13) previously had **no** submission-day refresh; their
filing-day refreshes are added today as unbound `submission/` records. This
crosswalk makes the whole tier auditable from one place.

## Registry

| Object | Filing-day refresh artifact | Bound? | Where dispositions live |
|--------|----------------------------|--------|-------------------------|
| ORION-01+05 (QIC-class) | `papers/orion-01-certificate-realization/submission/tier-b-final-20260901/LITERATURE_AND_PRIORITY_REFRESH.md` | bound (SHA256SUMS) | In-file, per work: TARE v4 (arXiv:2601.05740), Paulihedral, PCOAST, lazy synthesis, PBC compilation, 2025 tracking lib |
| ORION-02 (TMLR short) | `papers/orion-02-fiberguard-finite-fibre/submission/tier-b-final-20260901/LITERATURE_AND_LINEAGE_REFRESH.md` | bound (SHA256SUMS) | In-file, per work: 5 Crossref-DOI neighbours incl. JRSS-B qkaf016, AOS2510 |
| ORION-03 (JAR) | `papers/orion-03-typed-merge-falsification/submission/tier-b-final-20260901/LITERATURE_AND_LINEAGE_REFRESH.md` | bound (SHA256SUMS) | In-file: Cedar (doi:10.1145/3649835), semiring Datalog, 2025 FO provenance chapter |
| ORION-08 (TMLR) | `papers/orion-08-typed-state/submission/tier-b-final-20260901/LITERATURE_AND_LINEAGE_REFRESH.md` | bound (SHA256SUMS) | In-file: 6 arXiv neighbours 2608.25553 / 2605.06527 / 2608.10509 / 2607.20827 / 2606.22528 / 2604.20911 |
| ORION-09+10 (Quantum) | `papers/orion-10-certified-static-forecasting/submission/tier-b-final-20260901/LITERATURE_AND_LINEAGE_REFRESH.md` | bound (SHA256SUMS) | In-file: Campbell (arXiv:2604.01376), AutoQuREO (2608.12936), DeComp2 (2607.23990), Yang (2608.11579v2) |
| ORION-12 (IP&M) | `papers/orion-12-open-world-scientific-discovery/submission/LITERATURE_REFRESH_20260902.md` | **unbound (new)** | In-file, per work: 2607.00597, 2605.14306, 2606.15367, 2605.08956, 2608.23283 (Apodex 1.1, nearest in spirit), OpenScholar |
| ORION-13 (F1000) | `papers/orion-13-global-knowledge-portrait/submission/LITERATURE_REFRESH_20260902.md` | **unbound (new)** | In-file, per work: OAEI 2026 campaign, DISO-OAEI 2026 + arXiv:2608.21914, OAEI 2025 results, Bio-ML 2026, CausalFusion 2026, MI-based EA 2025, unified EA framework, WWW 2026 multi-modal EA |

## Tier-level statement

Each artifact above records, per work, an **ADAPT / COMPOSE / DELTA** line
and a statement of whether the work removes the object's residual. Sweep
conclusion across all seven objects: **no post-Aug-2026 work found on
2026-09-02 removes any Tier-B residual or requires a claim change.** The
refreshes are therefore referee-risk reduction (anchors and deltas stated
proactively), never a basis for claim widening.
