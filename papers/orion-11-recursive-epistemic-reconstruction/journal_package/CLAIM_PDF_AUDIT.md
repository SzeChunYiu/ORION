# ORION-11 claim/PDF audit — historical exact binary superseded by a pinned-renderer rebuild; current package open

Historical render audit date: 2026-08-21  
Current authority update: 2026-08-24  
Package rebind base: `ca7df1055a43f97eaf8d142a62011c4c261af368`  
Exact-render subject: `060ed7e6528a592cd3bef3db149b93e94652b2ec`  
Exact-render run: `32510318915`  
Exact-render artifact: `9456829355` (`sha256:f4d213ab9d84bb4e5bf60099e63e765221d0f25f45449933436276526f69bd51`)  
Package status: `SUPERSEDED`  
Current submission authority: `false`  
Current package claim: `ORION-11.CURRENT_PACKAGE = OPEN`

The V3 exact-render artifact independently reproduced ORION-11 PDF SHA-256
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

`journal_package/manuscript.pdf` no longer holds those bytes, and this line previously
claimed it did. On 2026-08-28 the package was rebuilt through the pinned renderer
(commit `7ae62c87c`, render run `33175368554`, which compiles twice under a pinned TeX
toolchain and a git-derived reproducible epoch and compares the outputs). That rebuild
replaced `06a60f0f...` with
`cda6ceb1ea69c2470d8d1df5fa886d6654de30bf96aee9ca0b293703c63823e0`, which is what
`journal_package/SHA256SUMS` records and what the working tree contains. The rebuild was
deliberate: the guards required the package to be rebuilt rather than re-hashed, so that
the evidence of the move was not deleted.

The historical exact-render binary `06a60f0f...` is therefore preserved in git history at
commit `3a1a83178`, not in the working tree. Nothing in the paragraph above is withdrawn —
that inspection genuinely happened against those bytes — but it describes a binary this
directory no longer carries, and the 33-page inspection has not been repeated against the
current one.
`journal_package/RENDER_INPUT_CLOSURE.json` preserves the V3 repository-input
closure from the protected artifact. The render subject is **not** relabelled.
At the original rebind base, the complete tracked TeX input closure supplied the
historical authority bridge. The generator-owned
`journal_package/RENDER_CLOSURE_STATE.json` now records `SUPERSEDED` because
tracked inputs later changed. The historical closure and PDF hash remain valid
records of the earlier render, but they do not authorize the current manuscript.

The `OPEN` current-package claim requires a fresh immutable PDF and page-level
visual audit for the enlarged source, an archive/DOI, repository-level
redistribution terms, and admissible clean-checkout custody for every cited
external handoff. Retaining the historical PDF does not close any of those
requirements.

`ORION-11.H1` remains `NOT_SUPPORTED`. The bounded credential-free mechanical
mutation-necessity result is unchanged; no model-general or open-ended
superiority is added.
