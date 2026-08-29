# Canonical build recipe for `papers/orion-??-*/manuscript/main.pdf`

A committed `manuscript/main.pdf` is **not** just "a PDF of the manuscript". CI treats it as
a byte-reproducible artifact and fails if it does not match a clean rebuild:

```bash
git diff --exit-code -- ':(glob)papers/orion-??-*/manuscript/main.pdf' || {
  echo '::error::tracked manuscript PDF bytes are stale relative to the clean pinned rebuild'
  exit 1
}
```

This note exists because that constraint is invisible from the paper directory, and building
a perfectly good PDF with the wrong toolchain makes CI **worse**, not better: a paper with no
committed PDF is silent in that diff, while a paper with a non-reproducible one fails it.

## The build CI compares against

From `.github/workflows/manuscript-clipping-audit.yml`. It globs
`papers/orion-??-*/manuscript/main.tex`, **asserts there are exactly 21**, and for each:

```bash
source_epoch="$(git log -1 --format=%ct -- "$manuscript_dir" ":(exclude)$manuscript_dir/main.pdf")"
export SOURCE_DATE_EPOCH="$source_epoch"
export FORCE_SOURCE_DATE=1
latexmk -C main.tex >/dev/null
latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error main.tex
```

Two details matter and are easy to miss:

- **The epoch is derived from the manuscript directory while excluding `main.pdf` itself.**
  Otherwise committing a PDF would move its own render epoch and create a circular mismatch.
- **`SOURCE_DATE_EPOCH` + `FORCE_SOURCE_DATE`** are what make the output byte-stable. Without
  them the PDF embeds a build timestamp and can never match.

## The toolchain is pinned to exact package versions

The workflow installs and version-checks specific Ubuntu packages, including
`texlive-base 2023.20240207-1`, `texlive-latex-base 2023.20240207-1`,
`texlive-latex-extra 2023.20240207-1`, `texlive-binaries 2023.20230311.66589-9build3`,
`latexmk 1:4.83-1`, `lmodern 2.005-1`, `fonts-texgyre 20180621-6`, and more.

**A different TeX engine cannot produce matching bytes.** `tectonic` and `pdflatex` differ in
object ordering, compression and font embedding, so a `tectonic`-built PDF will fail the diff
even when it renders correctly and passes the clipping audit.

## What this means in practice

- **Do not commit `manuscript/main.pdf` built outside that environment.** Build it on
  `ubuntu-24.04` with the pinned packages, or let CI produce it.
- **Adding a new `manuscript/main.tex` changes the entry-point count** and trips the
  `-eq 21` assertion. Update that number in the same change.
- **Editing manuscript sources without rebuilding the PDF makes it stale**, which is the same
  failure from the other direction.
- Paths *not* matching `papers/orion-??-*/manuscript/main.pdf` — for example
  `journal_package_A/main.pdf` — are outside both the rebuild and the diff, so a review render
  there is fine.

## Papers with no committed PDF

ORION-06, 07, 08 and 10 have `manuscript/main.tex` and currently no committed
`manuscript/main.pdf`. PDFs built with `pandoc --pdf-engine=tectonic` were prepared for them
and then withdrawn, because they rendered correctly and passed the clipping audit but could
never satisfy the byte-reproducibility diff. Producing the canonical artifacts needs the pinned
environment above; that work is outstanding, not done.
