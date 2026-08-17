# ORION-P4 compile instructions

TMLR template. Official `tmlr.sty` / `tmlr.bst` are pinned from upstream commit `7bf90efe3a0debbba703c05c43f3ff7e4d4a2992` in the TMLR audit workflow; they are not vendored in this tree.

Clean-room compile is performed by `.github/workflows/p4_tmlr_submission_audit.yml`. Locally, after obtaining unmodified official style files:

```bash
cd papers/paper-04-verified-scientific-discovery/manuscript
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Figures regenerate from immutable public V2 aggregates:

```bash
python papers/paper-04-verified-scientific-discovery/figures/generate_figures.py
```

Do not copy a PDF into `journal_package/`. The audited release PDF identity is recorded as a missing in-tree artifact with its GitHub Release SHA in `MANIFEST.json`.
