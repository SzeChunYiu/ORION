# P2 claim/PDF audit — visual gate complete; package rebind pending

Date: 2026-08-21  
Source manuscript change: `714a7e771961c8ace08bb38d7dab6e2ba45b8ff7`  
Inspected render subject: `1d69fc230a358ded93699fdbe03b6ff2299cccf8`  
Current comparison head: `0164deb570e0daee2912e354cdb6d2df20896dc7`  
Package status: `SCAFFOLDING`  
PDF authority: `OPEN`

The repaired exact-render workflow produced P2 PDF SHA-256
`90e424cff27f1a1cde8c37d774c3bcf17b7c1d98c0905c2f53e22b8753790fb3`
from source SHA-256 `e25e8b4a18bec85d8031f67656977f94d42ea44d99862fb606e51aaebb41ccf3`,
source-date epoch `1787312452`, and render-toolchain SHA-256
`4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`.
The exact-render workflow rebuilt from clean state twice and required identical PDF hashes.

All 24 pages were independently inspected. No clipping, overlap, black-square/glyph
corruption, unreadable figure/table placement, or page-edge contact was observed.
The durable page-audit record is `evidence/FINAL_SATURATION_AUDIT.md` (SHA-256 `637e99b108c67025e71e3eaaa1ce1fb859dca2adc5b34534a7c6c8d0fab7fb78`).

A repository compare from the inspected render subject through `0164deb5...` shows
no paper-01 or paper-02 file changes, so no manuscript-byte drift was found after
the inspected render. This completes the visual-inspection gate for the exact PDF
hash above, but it does **not** complete package authority: `journal_package/manuscript.pdf`
is still absent, the package checksum inventory therefore does not bind the PDF, and
final P2 manuscript/repository/package CI has not yet passed.

The scientific ceiling remains `P2_NARROWED`. External ORION-vs-baseline superiority
remains `CANNOT_CHECK`; the provider-invalid OpenAIRE/Crossref campaign is retained
rather than used as support. `P2.PDF` remains `OPEN` until the inspected binary is
rebound and final package/repository checks pass.
