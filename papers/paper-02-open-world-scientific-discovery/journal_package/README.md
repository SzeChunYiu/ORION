# ORION-P2 journal package

**Scientific status:** bounded terminal `PEER_REVIEW_READY`. **Static package
inventory:** `SUBMISSION_READY`. **Operational authority:** pending final P2
manuscript/repository/package CI and a successor exact-main render confirmation.

`journal_package/manuscript.pdf` is the independently inspected 24-page PDF with
SHA-256 `90e424cff27f1a1cde8c37d774c3bcf17b7c1d98c0905c2f53e22b8753790fb3`.
The protected V3 renderer also binds the complete tracked TeX input closure in
`RENDER_INPUT_CLOSURE.json`; the package does not infer source authority from
`main.tex` alone.

External ORION-vs-baseline superiority remains `CANNOT_CHECK`; the
provider-invalid OpenAIRE/Crossref campaign is retained rather than used as
support. Author metadata, the final venue wrapper, DOI minting, and a literature
refresh after 2026-08-31 remain filing operations. Issue #283 continues to own
`ScientificResultVerification.v1`.

Verify all manifest-required package and evidence files from the paper directory:

```bash
sha256sum -c journal_package/SHA256SUMS
```
