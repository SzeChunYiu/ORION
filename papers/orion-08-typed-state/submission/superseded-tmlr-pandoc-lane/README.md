# Superseded TMLR pandoc lane — ORION-08

**Relocated 2026-09-02** from `papers/orion-08-typed-state/submission_tmlr/`.

This directory is a dead build lane, retained as a record. It contains the
pandoc-based TMLR source builder (`build_tmlr_source.py` +
`tmlr_pandoc_template.tex`) and its era's cover letter and availability
statement.

Why it is dead:

1. `build_tmlr_source.py` consumes a Markdown master
   (`--cited-master`), and every Markdown master at the paper root is stale
   relative to the LaTeX the manuscript actually renders from — running it
   would omit references the LaTeX cites and reintroduce internal catalogue
   codes into a double-blind submission. This is recorded in
   `papers/publication_closure/FINDING_ORION08_BUILD_INPUT_IS_STALE_V1.md`.
2. The live TMLR journal form is produced from the canonical LaTeX tree by
   `papers/publication_closure/orion_all_submission_20260831/build_all_submission_materials.py`
   (`convert_to_tmlr` + `latexmk`), which assembles
   `submission/publication-ready-20260831/journal/` and, through
   `papers/publication_closure/tier_b_20260901/finalize_tier_b_package.py`,
   `submission/tier-b-final-20260901/`.

**Relocated 2026-09-03 (second pass).** The lane's own 6-page render and its
2026-08-28 manifests had been left behind at the `submission/` top level, where
`manuscript.pdf` was the first PDF a filer would reach. They now live here as
`manuscript.pdf` and `SUBMISSION_MANIFEST_20260828.{md,sha256}`. Those manifests
are stale against the live sources on every entry checked and disagree with each
other on `03-results.tex` and `06-limitations.tex`; they bind nothing. The only
filing surface is named in `../FILING_SURFACE.md`.

The current cover letter and availability statement governing the filing live
in `submission/tier-b-final-20260901/journal/` (and its source in
`submission/publication-ready-20260831/journal/`). Nothing in this directory
is an input to any package; do not build from it.

See also: `theory/binding-sufficiency-lattice-v1/THEOREM_CORRECTION_2026-09-01.md`
(V4 theorem correction the pandoc master predates) and
`../PUBLICATION_FREEZE_ADDENDUM_V2.md`.
