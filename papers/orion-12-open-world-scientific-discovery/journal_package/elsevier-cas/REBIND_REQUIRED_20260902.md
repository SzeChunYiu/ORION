# REBIND REQUIRED — 2026-09-02 (IP&M full-commit sweep)

Lane: ORION-12 Tier-B close-out (superiority-language sweep + statistical-authority
limitations paragraph + abstract frontier-figure reference + Elsevier-CAS cover
letter). This note is internal package bookkeeping, not a submission surface.

## What changed on disk

- `manuscript/ipm_submission.tex` — edited by hand (source edit, not a render):
  1. Abstract, controlled-index sentence: "supplies descriptive mechanism
     evidence" → "evidence only", and "but the study does not establish
     superiority" → "and the study does not establish superiority".
  2. Abstract, new sentence referencing the controlled-index frontier figure:
     `Figure~\ref{fig:p2-2}` (label defined in `manuscript/sections/results.tex`).
  3. Abstract, exact-contract sentence rewritten to neutral parallel form
     ("matches 400 of 400 … matches 250 of 400"; exclusion stated as the
     comparator's aggregation rule, not as an excuse).
  4. Abstract, nDCG sentence: "Although … , that secondary result" →
     "… ; that secondary result".
  5. Conclusion, TREC-COVID sentence: dropped "nevertheless" / "while";
     now "shows lower recall and higher read cost; the favorable nDCG@10
     difference does not establish overall superiority".
  6. New limitations paragraph on offline-companion statistical authority
     (underpowered flag macro, 0.03 frozen margin vs achieved 0.0496
     half-width, topic as the honest unit, preregistered per-precision
     requirements 1068 / 385 / 171 / 97) — inserted between the "declared route
     registry" paragraph and the TREC-COVID stress-test paragraph.
- `journal_package/elsevier-cas/cover_letter_ipm_20260902.md` — new (this
  package's cover letter; internal fallback-venue note at its foot).
- `journal_package/elsevier-cas/REBIND_REQUIRED_20260902.md` — this note.

No hash, manifest, or SHA256SUMS file was hand-edited. All rebinds below belong
to the one-shot rebind workflow in CI.

## Bindings already verified as NOT touched

- `journal_package/SHA256SUMS` binds the render-input closure of
  `manuscript/main.tex` + shared sections + `generated/suite_facts.tex`; it does
  not list `ipm_submission.tex` by name, so none of its 40 lines is invalidated
  by this edit (they remain stale-or-valid exactly as before this change).
- `journal_package/MANIFEST.json` references `manuscript/ipm_submission.tex`
  only as a `SUBMISSION_OPERATION` item without a content hash.

## Bindings now stale — rebind in the one-shot CI workflow

1. `manuscript/arxiv_submission.tex` — generated adapter is now behind the
   canonical source. `scripts/build_ipm_submission.py --check` will exit nonzero
   until `python3 scripts/build_ipm_submission.py` is rerun. All six adapter
   anchors (documentclass header, IPM-ONLY block, title/author/shorttitle/
   hypersetup) are untouched by this edit, so regeneration is deterministic;
   do not hand-edit the adapter.
2. `journal_package/current_revision/SUBMISSION_MANIFEST.json` — two sha256
   entries for `manuscript/ipm_submission.tex` (bytes 13599 /
   `a6968291…`; bytes 13609 / `4777345a…`) plus the `target_adapter` pointer
   are now historical.
3. All PDF surfaces — `manuscript/ipm_submission.pdf`, `submission/manuscript.pdf`,
   and the publication-final anonymous/attributed PDFs must be re-rendered before
   `tests/test_submission_surface_labels.py` rescans them (the test pdftotext-scans
   each PDF). The edited `.tex` source and both new package files already pass
   the surface regex (no internal precision-label compound; the word "frontier"
   is not a match by regex construction), but the PDFs on disk still carry the
   pre-edit text.
4. Claim and render checks reopened by the byte change (per the submission-source
   status rule that any byte change reopens affected render and claim checks):
   atomic claim ledger checker, claim ledger checker, render-input closure, and
   the abstract-length record (the abstract grows by roughly a dozen words; keep
   it within IP&M's guidance in the pre-upload editorial pass).

## Pre-existing drift (not caused by this edit)

`journal_package/RENDER_CLOSURE_STATE.json` already listed drifted inputs before
this change (other concurrent lanes). The rebind workflow should reconcile the
full closure rather than only `ipm_submission.tex`.
