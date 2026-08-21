# P2 final saturation audit — inspected bytes, package rebind pending

- Audit date: 2026-08-21
- Manuscript source change: `714a7e771961c8ace08bb38d7dab6e2ba45b8ff7`
- Inspected exact-render subject: `1d69fc230a358ded93699fdbe03b6ff2299cccf8`
- Repository comparison anchor: `d1f58d4fd5581c1977bcd89acd12f80edbb47287`
- Exact-render artifact: `9455070902`
- PDF SHA-256: `90e424cff27f1a1cde8c37d774c3bcf17b7c1d98c0905c2f53e22b8753790fb3`
- Source SHA-256: `e25e8b4a18bec85d8031f67656977f94d42ea44d99862fb606e51aaebb41ccf3`
- Render toolchain SHA-256: `4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`
- Pages inspected: 24/24
- Visual defects found: 0
- Package rebind: `PENDING`
- Submission authority: `OPEN`

The V2 exact-render receipt recorded `pdf_byte_reproducibility_checked=true`; the PDF
was produced twice from clean TeX state under the pinned render environment. Every
page was then inspected independently. No clipping, overlap, broken glyphs, black
squares, figure/table illegibility, or raster-edge contact was observed.

A repository compare from the artifact subject through the comparison anchor contains
no paper-01 or paper-02 changes. The visual gate is therefore durably bound to the exact
PDF hash above. A later `main` advance may reuse this page inspection only when the
exact-main renderer independently reproduces the same PDF SHA-256; changed PDF bytes
require renewed inspection.

This audit intentionally does not claim package completion: the PDF binary is not yet
present in `journal_package`, so #490 still requires binary rebind, checksum regeneration
including that binary, and final P2 manuscript plus repository/package CI. External ORION
superiority remains `CANNOT_CHECK`.
