# ORION-12 mirror package sync record — 2026-09-03

## Diagnosis

Mirror `v1-papers/orion-12-open-world-scientific-discovery/SUBMIT_THIS` (26 files) was stale: last content sync `0cc6c8cbb` 2026-09-02T09:38Z (mirror PR #71, skill refinement register). Canonical authoritative package `papers/orion-12-open-world-scientific-discovery/submission/publication-final-20260901/` (26 files, identical layout) was last touched `6282848d6` 2026-09-02T16:30Z — the IP&M honesty pass (#2126): "evidence only" phrasing, 400-of-400 closure-label split with authored-comparator 250/400, same-programme/single-author disclosure, offline-companion underpowered disclosure, frontier figure. Canonical postdated mirror by ~7 h. `2fa89e013` (#2138) touched only `submission/LITERATURE_REFRESH_20260902.md`, outside the package.

## Merge applied (same rules as the orion-09/10 sync, 2026-09-03)

- Canonical wholesale (5): `arxiv/manuscript.pdf`, `arxiv/source.zip`, `journal/manuscript_anonymous.pdf`, `journal/source_anonymous.zip`, `arxiv/metadata.json`.
- Mirror scholarly register kept (3): `SKILLS_APPLIED.md` (academic-paper-pipeline 1.23.0 rev `d5b61b5b`; canonical carried 1.21.0), `REVIEWER_AUDIT.md` (strict superset incl. the 2026-09-02 submission-surface re-closure section), `MANUSCRIPT_ELEMENT_JUSTIFICATION.json` (`ORION-12-IPM-20260902`).
- Regenerated (2): `PACKAGE_MANIFEST.json` (canonical arxiv/journal digest+page blocks — 21/16 pages; mirror register fields and date applied; payload digests recomputed; source manifests round-trip byte-identical, order-preserving dump), `SHA256SUMS` (canonical line order, recomputed digests).
- Net vs prior mirror: 7 files changed, 0 removed.

## Push and verification

- Push: git data API, blobs → tree (base_tree = repository ROOT tree `17907e77e`, not the subtree) → commit `6d66b3469` → `PATCH git/refs/heads/main`.
- Verified live: recursive tree 8,847 paths (unchanged count; in-place replacement), sibling `orion-08` folder intact (197 paths), `orion-13` untouched (22), `orion-09/10` intact (216); `SHA256SUMS` 25/25 lines OK locally; live fetch-back of `arxiv/manuscript.pdf` and `SHA256SUMS` byte-identical to the merged package (`d5657fb2…`, `59d54636…`).

## Disclosed, not fixed here (authority stays canonical)

`arxiv/metadata.json` abstract says "the opposing results do not establish overall superiority" while the rebuilt tex/PDF abstract says "that secondary result cannot replace the recall and cost criteria" — one sentence, same evidential direction. The merged package mirrors canonical faithfully; the alignment belongs to a canonical one-line commit.

## Human inputs

Filing to the venue remains HUMAN_INPUTS_REQUIRED (external custody); no part of this sync files anything.
