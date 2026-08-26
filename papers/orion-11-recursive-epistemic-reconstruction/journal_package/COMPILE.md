# ORION-ORION-11 compile and visual-verification instructions

From `papers/orion-11-recursive-epistemic-reconstruction/manuscript/`:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Requirements: a TeX distribution with `amsmath`, `graphicx`, `booktabs`,
`longtable`, `hyperref`, and `underscore`.

Before replacing `journal_package/manuscript.pdf`, require all citations and
cross-references to resolve, render every page with Poppler, and inspect the
title/abstract, both figures, all result tables, the multi-page nearest-work
matrix, section transitions, bibliography, margins, and page numbering. Then
refresh `journal_package/SHA256SUMS` and run its check.
