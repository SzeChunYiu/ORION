# ORION-P3 compile instructions

From `papers/paper-03-global-knowledge-portrait/manuscript/`:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Public-reference figures/tables (not a full-paper compile):

```bash
make paper03-public-reference-publication
```

Do not copy `main.pdf` into `journal_package/`.
