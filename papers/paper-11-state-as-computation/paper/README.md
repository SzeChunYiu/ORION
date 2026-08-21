# P11 publication source

This directory is the editable publication source for ORION-P11.

Each conceptual chapter has a canonical Markdown source and a matching LaTeX wrapper with the same stem. `main.tex` assembles the paper. The integrated `../MANUSCRIPT.md` remains the frozen peer-review snapshot that seeded this split; protocols, receipts, hostile negatives and replay artifacts remain outside `paper/` so prose/typesetting changes cannot mutate evidence authority.

Edit the `.md` chapter first. The sibling `.tex` file imports it via the LaTeX `markdown` package.