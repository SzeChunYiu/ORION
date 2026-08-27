# ORION-23 publication source

This directory is the editable publication source for ORION-23. Every conceptual chapter has one canonical Markdown source and a matching LaTeX wrapper. `main.tex` assembles the paper. The integrated `../MANUSCRIPT.md` remains the frozen peer-review snapshot that seeded this split. Historical negatives, protocols, result receipts and replay adjudication remain outside `paper/` so prose edits cannot alter scientific authority.

Edit the `.md` chapter first; the sibling `.tex` wrapper imports it via the LaTeX `markdown` package.