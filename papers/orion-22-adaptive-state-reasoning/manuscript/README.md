# ORION-22 publication source

This directory is the editable publication source for ORION-22.

- Every chapter has one canonical human-editable Markdown file in `sections/`.
- Every chapter has a matching `.tex` wrapper with the same stem.
- `main.tex` assembles the paper.
- The historical integrated `../MANUSCRIPT.md` is explicitly noncanonical.
- `../P12_ACTIVE_CLAIM_AUTHORITY_V4.json` is the sole current claim authority.
- Scientific protocols, receipts, and replay adjudication remain outside `paper/` so prose edits cannot silently mutate evidence authority.

Edit the `.md` chapter first. The sibling `.tex` file is intentionally thin and imports that text via the LaTeX `markdown` package.

Build with `make` (requires `latexmk` and a LaTeX installation with the `markdown` package).
