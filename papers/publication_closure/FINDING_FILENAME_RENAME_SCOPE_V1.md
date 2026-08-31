# Renaming ORION-12's coded filenames is a 37-file change, not a tidy

**Terminal:** `FILENAME_DELABEL_OUT_OF_SCOPE_FOR_A_SURFACE_PASS`

## What I thought it was

One section file, `manuscript/sections/p2x_unresolved_route_successor.tex`, carrying an internal programme code in its name. Filenames are visible to reviewers at venues that accept `.tex` source, so it reads as a small surface repair: rename the file, fix the `\input{}`, re-bind.

## What it actually is

A naming convention across the whole paper. `manuscript/figures/` alone holds `P2-1_pipeline.svg`, `P2-1_pipeline.tex`, `P2-2_manifest.json`, `P2-2_recall_vs_queries.pdf`, `P2-2_recall_vs_queries.tex`, `P2-3_cumulative_discovery.svg` and more. **37 files under the paper reference a `P2-N_` or `p2x_` name.**

The references are not confined to LaTeX:

- `manuscript/main.tex` and `manuscript/ipm_submission.tex` (`\input{}` paths)
- `journal_package/MANIFEST.json`, `RENDER_INPUT_CLOSURE.json`, `RENDER_CLOSURE_STATE.json`, `SHA256SUMS`, `current_revision/SUBMISSION_MANIFEST.json`
- `protocol/PROTOCOL_V1.json`, `protocol/STATISTICAL_PLAN_V1.json`
- `scripts/build_wave1_package.py`, `manuscript/figures/pipeline_figure.py`
- `editorial/ATOMIC_CLAIM_LEDGER_2026-08-28.csv`
- **archived submission zips**: `ORION12_IPM_ANONYMOUS_SOURCE.zip`, `ORION12_ANONYMOUS_REVIEW_ARCHIVE.zip`

The zips are the hard stop. A rename that does not reach inside them leaves the archived submission describing files that no longer exist, and rewriting an archived submission artifact is a different kind of act from renaming a source file.

## An error worth recording

Partway through I ran `git mv figures/P2-1_pipeline.svg figures/pipeline.tex` --- renaming an **SVG to a `.tex` extension** because the target name was written from the section-file pattern without checking the source extension. Caught and corrected immediately, but it is the specific failure mode of bulk renames: the pattern is applied to the name and not to the thing.

## Disposition

Reverted in full; no partial rename is on any branch. A partial rename is worse than none, because a tree where `P2-1_pipeline.tex` sits beside `pipeline.svg` is harder to reason about than one that is uniformly coded.

If this is worth doing, it is a dedicated pass with its own verification: rename every file, update all 37 referencing files, rebuild the journal package, regenerate the archives from source rather than editing them, and confirm the render is byte-comparable. That is not a surface repair.

## Note on severity

This defect only reaches a reviewer at a venue that accepts `.tex` source. For a PDF-only submission it is invisible. That does not make it acceptable, but it does mean it should not outrank the rendered-text defects.
