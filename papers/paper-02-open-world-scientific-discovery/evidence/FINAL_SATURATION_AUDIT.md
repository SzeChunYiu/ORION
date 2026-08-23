# P2 final saturation audit — inspected bytes rebound; final CI pending

- Audit date: 2026-08-21
- Package rebind base: `ca7df1055a43f97eaf8d142a62011c4c261af368`
- Protected exact-render subject: `060ed7e6528a592cd3bef3db149b93e94652b2ec`
- Exact-render run: `32510318915`
- Exact-render artifact: `9456829355`
- Exact-render artifact digest: `sha256:f4d213ab9d84bb4e5bf60099e63e765221d0f25f45449933436276526f69bd51`
- PDF SHA-256: `90e424cff27f1a1cde8c37d774c3bcf17b7c1d98c0905c2f53e22b8753790fb3`
- Entrypoint SHA-256: `e25e8b4a18bec85d8031f67656977f94d42ea44d99862fb606e51aaebb41ccf3`
- Repository input closure SHA-256: `91454e207b00a1de774264f0501e2032b7e3efdafebd58ba80040ec1b27d3ea9`
- Repository input count: 31
- Render toolchain SHA-256: `4139104188327db25c3b85dad72fad0bf4d036ac675f1fe2a38c31946dff2b32`
- Source-date epoch: `1787312452`
- Pages inspected: 24/24
- Visual defects found: 0
- Package binary rebind: `COMPLETE_ON_THIS_PR`
- PDF-inclusive checksum inventory: `COMPLETE_ON_THIS_PR`
- Static manifest state: `SUBMISSION_READY`
- Operational submission authority: `PENDING_FINAL_CI_AND_SUCCESSOR_EXACT_MAIN_CONFIRMATION`

The protected V3 exact-render receipt records
`pdf_byte_reproducibility_checked=true`. The PDF was produced twice from clean
TeX state under the pinned environment, and the full tracked repository input
closure consumed by TeX was content-addressed. Every page of the exact PDF hash
above was independently inspected. No clipping, overlap, broken glyphs, black
squares, figure/table illegibility, or page-edge contact was observed.

The V3 artifact was minted at `060ed7e6528a592cd3bef3db149b93e94652b2ec`, while
this rebind starts from `ca7df1055a43f97eaf8d142a62011c4c261af368`. That
distinction is preserved. The repository compare across that interval contains
no P1/P2 manuscript-input change; the only P1/P2 changes are durable audit/package
text. `RENDER_INPUT_CLOSURE.json` preserves the protected closure itself, so
authority is transferred by byte identity of the complete tracked TeX input
closure and exact PDF hash, not by pretending the two Git SHAs are the same.

This PR binds the inspected binary into `journal_package/manuscript.pdf` and
regenerates `SHA256SUMS` to cover the PDF, source closure, final audit, and every
other manifest-required file. The PR remains non-terminal until final P2
manuscript and ordinary repository/package CI succeed and a successor exact-main
render confirms the same input closure and PDF hash. A changed closure or PDF
hash reopens the visual/package gate.

The scientific ceiling remains `P2_NARROWED`. External ORION-vs-baseline
superiority remains `CANNOT_CHECK`; the provider-invalid Wide result is not
converted into support or a valid null.
