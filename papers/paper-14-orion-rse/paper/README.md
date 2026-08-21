# P14 publication source

This directory is the editable publication source for ORION-P14 / ORION-RSE. Every conceptual chapter has one canonical Markdown source and a matching LaTeX wrapper. `main.tex` assembles the paper. The integrated `../MANUSCRIPT.md` remains the frozen peer-review snapshot that seeded this split. P14A/P14B/P14C protocols, results, corrections and replay adjudication remain outside `paper/` so prose/typesetting changes cannot alter evidence authority.

Edit the `.md` chapter first; the sibling `.tex` wrapper imports it via the LaTeX `markdown` package.