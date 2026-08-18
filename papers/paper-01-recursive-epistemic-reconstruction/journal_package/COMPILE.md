# ORION-P1 compile instructions

This is a working-draft compile path, not a journal-template conversion.

From `papers/paper-01-recursive-epistemic-reconstruction/manuscript/`:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Requirements: a TeX distribution with `amsmath`, `graphicx`, `booktabs`, `longtable`, `hyperref`.

`main.pdf` is gitignored. Do not copy a compiled PDF into `journal_package/`. The independent PDF proofread remains OPEN until a journal-formatted PDF exists in a permanent archive.
