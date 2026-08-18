# ORION-P2 compile and audit instructions

From `papers/paper-02-open-world-scientific-discovery/manuscript/`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
python ../scripts/check_manuscript_typography.py --log main.log
```

Then fail if `main.log` contains an undefined citation/reference warning and
inspect `pdfinfo main.pdf`. The canonical review build is copied byte-for-byte to
`journal_package/manuscript.pdf` and bound by `SHA256SUMS`.

The evidence-bound review PDF uses the neutral single-column article source.
The current IP&M CAS wrapper, title page, and final double-anonymization check are
filing operations performed with author-supplied metadata; they may not change
scientific claims or silently drop the bounded/failed-result language.
