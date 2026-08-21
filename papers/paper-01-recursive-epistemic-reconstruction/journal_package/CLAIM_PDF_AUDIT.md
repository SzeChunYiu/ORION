# P1 claim/PDF audit — visual gate complete; package rebind pending

Date: 2026-08-21  
Source manuscript change: `714a7e771961c8ace08bb38d7dab6e2ba45b8ff7`  
Inspected render subject: `1d69fc230a358ded93699fdbe03b6ff2299cccf8`  
Repository comparison anchor: `d1f58d4fd5581c1977bcd89acd12f80edbb47287`  
Package status: `SCAFFOLDING`  
PDF authority: `OPEN`

The repaired exact-render workflow produced P1 PDF SHA-256
`06a60f0f6ec69bc142952b4fc9dc1030fcd0f80de41f941958debe375e6ea99e`
from source SHA-256 `dcba4f80bd3c09c51e7062d4695baccfff4b2ef1f9dbc24b7cabb00fad0dcadd`,
source-date epoch `1787318056`, and render-toolchain SHA-256
`4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`.
The exact-render workflow rebuilt from clean state twice and required identical PDF hashes.

All 33 pages were independently inspected, including full-resolution follow-up of
the logged overfull-box pages 11, 20, and 21. No clipping, overlap, black-square/glyph
corruption, unreadable figure/table placement, or page-edge contact was observed.
The durable page-audit record is `evidence/FINAL_SATURATION_AUDIT.md` (SHA-256 `0f848456e44b05b90851bf5e6e097c7567e79980be02b28c2739dba5e8f90978`).

A repository compare from the inspected render subject through the comparison anchor
shows no paper-01 or paper-02 file changes, so no manuscript-byte drift was found after
the inspected render. A later `main` advance may reuse this visual evidence only when
the exact-main renderer independently reproduces the identical PDF SHA-256; changed PDF
bytes require renewed page inspection.

This completes the visual-inspection gate for the exact PDF hash above, but it does
**not** complete package authority: `journal_package/manuscript.pdf` is still absent,
the package checksum inventory therefore does not bind the PDF, and final
repository/package CI has not yet passed.

`P1.H1` remains `NOT_SUPPORTED`. The bounded credential-free mechanical
mutation-necessity result is unchanged; no model-general or open-ended superiority
is added. `P1.PDF` remains `OPEN` until the inspected binary is rebound and final
package/repository checks pass.
