# ORION-13 compile instructions

From `papers/orion-13-global-knowledge-portrait/manuscript/`:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Public-reference figures/tables can be rebuilt with
`make paper03-public-reference-publication`. A local compile does not replace the
retained historical package. Do not copy `main.pdf` into `journal_package/` until
a fresh immutable build plus page-level visual and claim audit are complete.
