# Build and visual-QA receipt

Date: 2026-08-28

## Exact object

- Article: *Regime maps for exact quantum compilation separate expressivity, certificates and feature transfer*
- Article PDF: 9 A4 pages
- Supplementary Information PDF: 9 A4 pages
- Source archive: 18 sorted, plain-named entries; both bibliography outputs included
- Review-material archive: 13 sorted, plain-named entries

Exact byte counts and SHA-256 bindings are recorded in `SUBMISSION_MANIFEST.json` and `SHA256SUMS` in this private audit directory.  Those bindings are not included on reader- or reviewer-facing surfaces.

## Build checks

- Article and Supplementary Information built successfully with Tectonic.
- Final logs contain zero overfull boxes, undefined references, undefined citations, stuck floats or LaTeX errors.
- The source archive was extracted in a clean directory and rebuilt both 9-page PDFs with the same zero-defect gate.
- The manuscript binding verifier passed 48/48 checks.
- The clean review-material verifier passed 31/31 checks in an isolated extraction.
- The review table generator reproduced the included generated tables exactly.
- The panel exporter reproduced 119 cells, 32 lookup errors, coverage 2 and empirical probability 0.51.

## Reader-surface leakage gate

The final article PDF text, Supplementary Information PDF text, embedded PDF strings, manuscript source, clean source archive, clean review-material archive, archive entry names, cover letter and availability statement were scanned for project/paper codes, internal machine terminals, repository paths, content hashes, branch/CI/issue/pull-request history, release strings, placeholders and replacement characters.  Matches: zero.

## Visual inspection

Every page of the exact final article PDF (pages 1--9) and Supplementary Information PDF (pages 1--9) was rendered and inspected.  No clipping, overlap, unreadable table, broken reference, missing glyph, replacement character, misplaced float or reader-facing internal identifier was observed.  The nearest-work table is small but legible and no longer overlaps adjacent columns.

## Authority boundary

These checks establish same-team build, consistency and visual quality.  They are not external replication, independent proof review, a novelty certificate, journal acceptance or filing authorization.
