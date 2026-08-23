# P12 publication source

This directory is the editable publication source for ORION-P12.

- Every chapter has one canonical human-editable Markdown file in `sections/`.
- Every chapter has a matching `.tex` wrapper with the same stem.
- `main.tex` assembles the paper.
- The historical integrated `../MANUSCRIPT.md` remains as the frozen peer-review snapshot that seeded this split.
- Scientific protocols, receipts, and replay adjudication remain outside `paper/` so prose edits cannot silently mutate evidence authority.

Edit the `.md` chapter first. The sibling `.tex` file is intentionally thin and imports that text via the LaTeX `markdown` package.

Build with `make` (requires `latexmk` and a LaTeX installation with the `markdown` package).