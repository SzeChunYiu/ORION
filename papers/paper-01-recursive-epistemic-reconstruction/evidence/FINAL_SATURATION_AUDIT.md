# P1 final saturation audit — inspected bytes, package rebind pending

- Audit date: 2026-08-21
- Manuscript source change: `714a7e771961c8ace08bb38d7dab6e2ba45b8ff7`
- Inspected exact-render subject: `1d69fc230a358ded93699fdbe03b6ff2299cccf8`
- Comparison head: `6818dcf67d6ce7a7123c6c09c7f4251d5828461b`
- Exact-render artifact: `9455070902`
- PDF SHA-256: `06a60f0f6ec69bc142952b4fc9dc1030fcd0f80de41f941958debe375e6ea99e`
- Source SHA-256: `dcba4f80bd3c09c51e7062d4695baccfff4b2ef1f9dbc24b7cabb00fad0dcadd`
- Render toolchain SHA-256: `4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`
- Pages inspected: 33/33
- Visual defects found: 0
- Package rebind: `PENDING`
- Submission authority: `OPEN`

The V2 exact-render receipt recorded `pdf_byte_reproducibility_checked=true`; the PDF
was produced twice from clean TeX state under the pinned render environment. Every
page was then inspected independently. Pages 11, 20, and 21 received full-resolution
follow-up because the TeX log reported overfull boxes; none showed clipping or edge loss.
No overlap, broken glyphs, black squares, figure/table illegibility, or raster-edge
contact was observed.

A repository compare from the artifact subject through the comparison head contains
no paper-01 or paper-02 changes. The visual gate is therefore durably bound to the
exact PDF hash above. This audit intentionally does not claim package completion:
the PDF binary is not yet present in `journal_package`, so #489 still requires binary
rebind, checksum regeneration including that binary, and final repository/package CI.
The P1 scientific claim ceiling is unchanged.
