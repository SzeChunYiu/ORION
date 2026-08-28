# ORION-12 journal package

**Scientific status:** the bounded `ORION-12.NARROWED` terminal is retained.  
**Historical root-package status:** `SUPERSEDED`.  
**Current package:** `current_revision/`.  
**Recursive-pipeline terminal:** `simulated_publication_ready_for_target`.

`journal_package/manuscript.pdf` is the independently inspected historical
24-page PDF with SHA-256
`90e424cff27f1a1cde8c37d774c3bcf17b7c1d98c0905c2f53e22b8753790fb3`.
The protected V3 renderer binds its complete tracked TeX input closure in
`RENDER_INPUT_CLOSURE.json`. `RENDER_CLOSURE_STATE.json`, regenerated from the
current tree, records that 13 of 31 inputs moved and that the retained PDF is
`SUPERSEDED`. It must not be relabelled or submitted as the current manuscript.

The additive `current_revision/` directory contains the current CAS
single-column review PDF, anonymous editable source, anonymous review archive,
cover letter and filing companions. `SUBMISSION_MANIFEST.json` records file
digests, byte counts and the exact PDF input closure. `RENDER_VISUAL_AUDIT.md`
and `VISUAL_CONTACT_SHEET.jpg` record the every-page inspection. Two clean
builds are byte-identical under the recorded source epoch.

External ORION-vs-baseline superiority remains `CANNOT_CHECK`; the
provider-invalid OpenAIRE/Crossref campaign is retained rather than used as
support. Author metadata, the final venue wrapper, DOI minting, and a literature
refresh after 2026-08-31 remain filing operations. Issue #283 continues to own
`ScientificResultVerification.v1`.

Verify the current inventory from the paper directory:

```bash
cd journal_package/current_revision
sha256sum -c SHA256SUMS
```

That integrity check establishes package identity only. It does not grant
novelty, external retrieval superiority, acceptance or external-review
authority. Human affiliation/declaration completion and filing remain outside
the scientific terminal.
