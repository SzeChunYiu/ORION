# ORION-02 PDF visual QA V4

**TMLR review artifact:** journal_package_final/submission/When_a_Representation_Can_Certify.pdf
**TMLR PDF SHA-256:** `aeb0ec1b091fc5de7defaeb83b4043657627c2d07519f660940be692d121cfae`
**Public arXiv artifact:** journal_package_final/submission/When_a_Representation_Can_Certify_arxiv.pdf
**arXiv PDF SHA-256:** `4b72b2fa0340b9bfaa257288f1474d4f3b56bfc80c1cdbe8a809214425de3d88`
**Render:** 7 pages per route, 150 dpi, all 14 route pages inspected on 2026-08-31
**Build reproducibility:** both route PDFs are produced deterministically with `SOURCE_DATE_EPOCH=1788134400`; the public source is an exact route-metadata transformation of the anonymous review source.

## Checks

- [x] The TMLR title, anonymous author line and double-blind header render correctly.
- [x] The arXiv title and named author render correctly, with no review header or anonymous-review statement.
- [x] Abstract is one paragraph and contains proper mathematical symbols.
- [x] Section and subsection numbering is not duplicated.
- [x] Theorem, corollary and proof environments are legible and consistently numbered.
- [x] Display equations use mathematical typesetting; no private plain-text symbol leakage remains.
- [x] The adverse-results table fits on one page, has readable columns, and preserves all six boundaries.
- [x] Citations and bibliography are legible; no reference spills to a sparse final page.
- [x] No clipped text, overlapping objects, missing glyphs, blank pages, orphaned heading or overfull box.
- [x] Final page ends cleanly with the complete bibliography.
- [x] TMLR PDF metadata contains only the title and Anonymous author identity.
- [x] arXiv PDF metadata contains the title and Sze Chun Yiu author identity.
- [x] Extracted text is non-empty and contains all theorem and adverse-result sections.

The post-correction build logs have no LaTeX error, undefined reference/citation, overfull box, underfull box or BibTeX warning. Tectonic emits only its known internal repeated-bibliography consistency notice while returning success. Page 5 of both routes was inspected at full render resolution to confirm that the corrected R24 row, contingency and $p$-value remain legible and unclipped; page 7 was inspected separately to confirm the prose limitations, disclosure and complete bibliography.
