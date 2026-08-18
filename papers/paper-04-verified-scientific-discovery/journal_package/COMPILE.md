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

The generator emits SVG; `main.tex` includes PNG. Rasterise before compiling, or
every `\includegraphics` fails on a file that does not exist:

```bash
F=papers/paper-04-verified-scientific-discovery/figures
for stem in p4_2_false_promotion p4_3_coverage_frontier p4_4_detection_by_attack \
            p4_5_attribution_vs_support p4_6_cost_false_promotion; do
  rsvg-convert -w 1440 -o "$F/$stem.png" "$F/$stem.svg"
done
```

This is the same step `.github/workflows/p4_tmlr_submission_audit.yml` performs,
which is why the clean-room compile passes there while the sequence documented
here previously did not run locally.

Do not copy a PDF into `journal_package/`. The audited release PDF identity is recorded as a missing in-tree artifact with its GitHub Release SHA in `MANIFEST.json`.
