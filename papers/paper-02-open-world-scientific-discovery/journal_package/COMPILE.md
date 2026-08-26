# ORION-P2 compile and audit instructions

From `papers/paper-02-open-world-scientific-discovery/manuscript/`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
python ../scripts/check_manuscript_typography.py --log main.log
```

Fail if `main.log` contains an undefined citation/reference warning and inspect
`pdfinfo main.pdf`. This local check does not replace the retained historical
package or grant package authority.

The current `journal_package/manuscript.pdf` is a retained historical render and
must not be overwritten or relabelled by an unreviewed local build. A successor
package requires a fresh immutable build, a new render-input closure, and a
completed page-level visual and claim audit before its PDF is copied into a new
current package and bound by `SHA256SUMS`.

The evidence-bound review uses the neutral single-column source. A venue wrapper,
title page, and final identity-signal review are filing operations and may not
change claims or drop bounded/adverse language.
