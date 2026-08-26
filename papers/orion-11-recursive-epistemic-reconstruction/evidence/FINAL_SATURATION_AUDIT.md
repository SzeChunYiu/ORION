# ORION-11 final saturation audit — inspected bytes rebound; final CI pending

- Audit date: 2026-08-21
- Package rebind base: `ca7df1055a43f97eaf8d142a62011c4c261af368`
- Protected exact-render subject: `060ed7e6528a592cd3bef3db149b93e94652b2ec`
- Exact-render run: `32510318915`
- Exact-render artifact: `9456829355`
- Exact-render artifact digest: `sha256:f4d213ab9d84bb4e5bf60099e63e765221d0f25f45449933436276526f69bd51`
- PDF SHA-256: `06a60f0f6ec69bc142952b4fc9dc1030fcd0f80de41f941958debe375e6ea99e`
- Entrypoint SHA-256: `dcba4f80bd3c09c51e7062d4695baccfff4b2ef1f9dbc24b7cabb00fad0dcadd`
- Repository input closure SHA-256: `3bb45ad8961a53d555a7e6592c359e9b0cf080fe00cf7a5e8c2fbff2915cebf2`
- Repository input count: 31
- Render toolchain SHA-256: `4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`
- Source-date epoch: `1787318056`
- Pages inspected: 33/33
- Visual defects found: 0
- Package binary rebind: `COMPLETE_ON_THIS_PR`
- PDF-inclusive checksum inventory: `COMPLETE_ON_THIS_PR`
- Static manifest state: `SUBMISSION_READY`
- Operational submission authority: `PENDING_FINAL_CI_AND_SUCCESSOR_EXACT_MAIN_CONFIRMATION`

The protected V3 exact-render receipt records
`pdf_byte_reproducibility_checked=true`. The PDF was produced twice from clean
TeX state under the pinned environment, and the full tracked repository input
closure consumed by TeX was content-addressed. Every page of the exact PDF hash
above was inspected independently; pages 11, 20, and 21 received
full-resolution follow-up because of logged overfull boxes. No clipping,
overlap, broken glyphs, black squares, figure/table illegibility, or page-edge
contact was observed.

The V3 artifact was minted at `060ed7e6528a592cd3bef3db149b93e94652b2ec`, while
this rebind starts from `ca7df1055a43f97eaf8d142a62011c4c261af368`. That
distinction is preserved. The repository compare across that interval contains
no ORION-11/ORION-12 manuscript-input change; the only ORION-11/ORION-12 changes are durable audit/package
text. `RENDER_INPUT_CLOSURE.json` preserves the protected closure itself, so
authority is transferred by byte identity of the complete tracked TeX input
closure and exact PDF hash, not by pretending the two Git SHAs are the same.

This PR binds the inspected binary into `journal_package/manuscript.pdf` and
regenerates `SHA256SUMS` to cover the PDF, source closure, final audit, and every
other manifest-required file. The PR remains non-terminal until final
repository/package CI succeeds and a successor exact-main render confirms the
same input closure and PDF hash. A changed closure or PDF hash reopens the
visual/package gate.

The ORION-11 scientific claim ceiling is unchanged. `ORION-11.H1` remains `NOT_SUPPORTED`;
no model-general or open-ended superiority is added.
