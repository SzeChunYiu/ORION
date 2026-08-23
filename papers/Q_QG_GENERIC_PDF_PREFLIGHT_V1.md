# Q/QG generic PDF preflight contract V1

Purpose: render the five content-ready cited masters into **generic audit PDFs** before target-journal wrappers are introduced.

These PDFs are not submission packages and grant no venue compliance. They exist to catch source-level rendering defects early:
- broken Unicode/glyphs;
- malformed equations/code spans;
- tables wider than a page;
- missing citations/bibliography rendering;
- clipped/overlapping text;
- pathological page breaks;
- invalid PDF output.

## Pipeline

1. Run `build_q_qg_cited_masters.py --clean`.
2. Convert each cited master with Pandoc + citeproc using the combined verified BibTeX.
3. Render with XeLaTeX in a generic 1-inch-margin article-style PDF.
4. Run `pdfinfo` / `pdffonts` sanity checks.
5. Render every page to PNG with Poppler (`pdftoppm`).
6. Upload PDFs + page PNGs + metadata as a GitHub Actions artifact.
7. Perform page-by-page visual inspection before any target wrapper is declared ready.

## Papers

- Q1 V3
- Q2 V3
- Q4 V3
- QG1 V3
- QG2 V3

Q3 is excluded because no final scientific results manuscript is authorized.

## Evidence boundary

Generic preflight is not a substitute for:
- Quantum final/arXiv source review;
- TMLR official template + anonymization audit;
- PRX Quantum REVTeX/APS Data Availability/popular-summary requirements;
- exact target bibliography/figure production rules.

A generic PDF may be visually green while a target package remains open.

## Visual audit checklist

For every page:
- [ ] no clipped text or table;
- [ ] no overlapping text/figures;
- [ ] no black boxes/missing glyphs;
- [ ] section headings are not stranded pathologically;
- [ ] inline mathematical identifiers remain legible;
- [ ] code/authority strings do not create unreadable overflow;
- [ ] citation markers render and bibliography entries are present;
- [ ] no internal audit-only block dominates the main narrative;
- [ ] page count and file hash recorded.

Any content-changing repair goes back to the final scientific master and re-runs publication CI. Layout-only repair belongs to the target/source generation layer.
