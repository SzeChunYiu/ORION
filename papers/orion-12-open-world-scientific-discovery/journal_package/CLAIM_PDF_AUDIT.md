# ORION-12 claim/PDF audit — retained historical exact render

Date: 2026-08-21  
Historical package rebind base: `ca7df1055a43f97eaf8d142a62011c4c261af368`  
Exact-render subject: `060ed7e6528a592cd3bef3db149b93e94652b2ec`  
Exact-render run: `32510318915`  
Exact-render artifact: `9456829355` (`sha256:f4d213ab9d84bb4e5bf60099e63e765221d0f25f45449933436276526f69bd51`)  
Package status: `SUPERSEDED`  
Current submission authority: `false`

The V3 exact-render artifact independently reproduced PDF SHA-256
`90e424cff27f1a1cde8c37d774c3bcf17b7c1d98c0905c2f53e22b8753790fb3`
twice from clean TeX state under render-toolchain SHA-256
`4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`
and source-date epoch `1787312452`. Its complete 31-input closure has SHA-256
`91454e207b00a1de774264f0501e2032b7e3efdafebd58ba80040ec1b27d3ea9`.
All 24 pages of those exact bytes were independently inspected with no observed
clipping, overlap, glyph corruption, unreadable figure/table placement, or
page-edge contact.

`journal_package/manuscript.pdf` and `RENDER_INPUT_CLOSURE.json` retain that
historical record. The render subject is not relabelled as the current revision.
`RENDER_CLOSURE_STATE.json` records 13 changed inputs, so the inspected PDF is
not a render of the current manuscript.

The current manuscript requires a fresh immutable build plus page-level visual
and claim audit before any package can regain submission authority. Rebinding
the current inventory and passing CI do not perform that operation. The
scientific ceiling remains `P2_NARROWED`; external superiority remains
`CANNOT_CHECK`, and the provider-invalid campaign remains adverse evidence.

`ORION-12.CURRENT_PACKAGE` remains **OPEN** until the fresh immutable PDF and current page-level visual and claim audit exist.
