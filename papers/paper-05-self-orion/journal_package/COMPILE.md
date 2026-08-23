# ORION-P5 compile instructions

From `papers/paper-05-self-orion/`, render the tracked SVG source to the publication PDF asset first:

```bash
rsvg-convert -f pdf -o figures/p5_1_governed_development_loop.pdf figures/p5_1_governed_development_loop.svg
```

Then from `papers/paper-05-self-orion/manuscript/`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The build is accepted only after LaTeX converges with no undefined citations/references, the rendered governance-loop PDF is byte-bound by the package, and the rebuilt manuscript PDF is copied byte-for-byte into `journal_package/manuscript.pdf`. The journal-package checker then regenerates and verifies `journal_package/SHA256SUMS` against the exact scoped source, rendered figure, and manuscript PDF.

Headline regeneration for the bounded attribution probe reads archived JSONL only. No fresh-transfer/self-improvement performance figure or result may be generated because the protected H1–H4 campaign remains unexecuted. The scoped PDF concerns the diagnosis/proposal/adoption authority separation and the retained 21/24 diagnostic archive only.
