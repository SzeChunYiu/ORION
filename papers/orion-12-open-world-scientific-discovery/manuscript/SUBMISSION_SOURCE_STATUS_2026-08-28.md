# ORION-12 current submission-source status — 2026-08-28

Tracking issue: #1609

This file is publication metadata for the current manuscript tree. The canonical manuscript entry point remains `main.tex`; this file is not included in the paper text.

## Scientific scope to preserve

The submission claim is the narrowed methods / critical system-design result:

- fail-closed route/read/stopping authority semantics and controlled mechanism behavior are supported in the frozen controlled setting;
- external Wide/Deep ORION-vs-baseline superiority is **not** supported by the present evidence and is not part of the submission claim;
- the TREC-COVID registered recall/cost superiority gate failed and remains visible;
- the favorable nDCG@10 result is secondary and must not be used to rescue the failed registered gate;
- future valid multi-provider superiority studies are successor science, not a hidden prerequisite of this narrowed manuscript.

## Current package problem

`journal_package/MANIFEST.json` correctly marks the retained PDF as historical/superseded for the current manuscript and leaves `P2.CURRENT_PACKAGE` open. Wave 1 therefore requires a fresh exact-current render rather than reusing historical `PEER_REVIEW_READY` language.

## Closeout blockers

- [ ] `p1-p2-exact-main-render` passes on this exact PR head and emits a byte-reproducible current ORION-12 PDF.
- [ ] The exact render receipt and repository input-closure digest are retained for the current source.
- [ ] A page-level visual and claim audit is performed on that exact PDF.
- [ ] `journal_package/MANIFEST.json` is additively superseded/rebound to the current PDF only after the render+visual audit is complete; the historical PDF remains historical.
- [ ] Current IP&M wrapper/title-page requirements are checked without inventing human author metadata.
- [ ] Submission-date literature refresh is rerun only if the current freshness window has expired.
- [ ] Exact final submission bytes are bound before upload.

## Close criterion

`READY_TO_FILE_IPM` when the current narrowed manuscript—not a historical package—has a clean exact render, visual/claim audit and exact-byte submission manifest. No new exploratory science is required unless the current-source audit reveals a scientific contradiction.
