# ORION-21 publication source

This directory is the editable publication source for ORION-21.

Each conceptual chapter has a canonical Markdown source and a matching LaTeX wrapper with the same stem. `main.tex` assembles the paper. The integrated `../MANUSCRIPT.md` is a synchronized review surface, not a competing authority. `../P11_ACTIVE_CLAIM_AUTHORITY_V2.json` is the sole current claim authority; protocols, receipts, hostile negatives and replay artifacts remain outside `manuscript/` so prose/typesetting changes cannot mutate evidence authority.

Edit the `.md` chapter first. The sibling `.tex` file imports it via the LaTeX `markdown` package.
