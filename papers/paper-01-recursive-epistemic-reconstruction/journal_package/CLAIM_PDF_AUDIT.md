# P1 claim/PDF audit — exact binary rebound; final CI pending

Date: 2026-08-21  
Package rebind base: `ca7df1055a43f97eaf8d142a62011c4c261af368`  
Exact-render subject: `060ed7e6528a592cd3bef3db149b93e94652b2ec`  
Exact-render run: `32510318915`  
Exact-render artifact: `9456829355` (`sha256:f4d213ab9d84bb4e5bf60099e63e765221d0f25f45449933436276526f69bd51`)  
Package status: `SUBMISSION_READY`  
Operational submission authority: `PENDING_FINAL_CI_AND_SUCCESSOR_EXACT_MAIN_CONFIRMATION`

The V3 exact-render artifact independently reproduced P1 PDF SHA-256
`06a60f0f6ec69bc142952b4fc9dc1030fcd0f80de41f941958debe375e6ea99e`
twice from clean TeX state under render-toolchain SHA-256
`4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`
and source-date epoch `1787318056`. Its complete tracked TeX input closure is
`3bb45ad8961a53d555a7e6592c359e9b0cf080fe00cf7a5e8c2fbff2915cebf2`
over 31 committed inputs.

All 33 pages of those exact PDF bytes were independently inspected. Pages 11, 20,
and 21 also received full-resolution follow-up because the TeX log reported
overfull boxes. No clipping, overlap, black-square/glyph corruption, unreadable
figure/table placement, or page-edge contact was observed.

`journal_package/manuscript.pdf` now contains those exact inspected bytes.
`journal_package/RENDER_INPUT_CLOSURE.json` preserves the V3 repository-input
closure from the protected artifact. The render subject is **not** relabelled as
the rebind base: the authority bridge is the complete tracked TeX input closure.
The repository compare from the render subject to `ca7df1055a43f97eaf8d142a62011c4c261af368`
changes only durable P1/P2 audit/package text and no manuscript input, so the
closure and PDF hash remain applicable. Any later change to the closure or PDF
hash requires renewed render/inspection before package authority can be reused.

The static journal-package inventory is now rebound and PDF-inclusive, but this
PR does not by itself grant final merge/submission authority. Final ordinary
repository/package CI and the successor exact-main render check are still
required before issue #489 may be completed.

`P1.H1` remains `NOT_SUPPORTED`. The bounded credential-free mechanical
mutation-necessity result is unchanged; no model-general or open-ended
superiority is added.
