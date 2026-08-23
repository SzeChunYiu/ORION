# P2 claim/PDF audit — exact binary rebound; final CI pending

Date: 2026-08-21  
Package rebind base: `ca7df1055a43f97eaf8d142a62011c4c261af368`  
Exact-render subject: `060ed7e6528a592cd3bef3db149b93e94652b2ec`  
Exact-render run: `32510318915`  
Exact-render artifact: `9456829355` (`sha256:f4d213ab9d84bb4e5bf60099e63e765221d0f25f45449933436276526f69bd51`)  
Package status: `SUBMISSION_READY`  
Operational submission authority: `PENDING_FINAL_CI_AND_SUCCESSOR_EXACT_MAIN_CONFIRMATION`

The V3 exact-render artifact independently reproduced P2 PDF SHA-256
`90e424cff27f1a1cde8c37d774c3bcf17b7c1d98c0905c2f53e22b8753790fb3`
twice from clean TeX state under render-toolchain SHA-256
`4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`
and source-date epoch `1787312452`. Its complete tracked TeX input closure is
`91454e207b00a1de774264f0501e2032b7e3efdafebd58ba80040ec1b27d3ea9`
over 31 committed inputs.

All 24 pages of those exact PDF bytes were independently inspected. No clipping,
overlap, black-square/glyph corruption, unreadable figure/table placement, or
page-edge contact was observed.

`journal_package/manuscript.pdf` now contains those exact inspected bytes.
`journal_package/RENDER_INPUT_CLOSURE.json` preserves the V3 repository-input
closure from the protected artifact. The render subject is **not** relabelled as
the rebind base: the authority bridge is the complete tracked TeX input closure.
The repository compare from the render subject to `ca7df1055a43f97eaf8d142a62011c4c261af368`
changes only durable P1/P2 audit/package text and no manuscript input, so the
closure and PDF hash remain applicable. Any later change to the closure or PDF
hash requires renewed render/inspection before package authority can be reused.

The static journal-package inventory is now rebound and PDF-inclusive, but this
PR does not by itself grant final merge/submission authority. Final P2 manuscript,
ordinary repository/package CI, and the successor exact-main render check are
still required before issue #490 may be completed.

The scientific ceiling remains `P2_NARROWED`. External ORION-vs-baseline
superiority remains `CANNOT_CHECK`; the provider-invalid OpenAIRE/Crossref
campaign is retained rather than used as support.
