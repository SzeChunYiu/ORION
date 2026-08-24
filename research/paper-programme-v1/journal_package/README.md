# Journal-package scaffolding (issue #160)

Gate 7–9 inventory for P1–P5. Each paper owns `papers/*/journal_package/`:

- `MANIFEST.json` — `orion.journal-package.v1` file list, missing-artifact `CANNOT_CHECK` rows, claim/PDF audit rows
- `SHA256SUMS` — hashes of present required files plus package docs
- `COMPILE.md` — how to compile; does not mint a PDF
- `LICENSE.md` — license/restriction statement, including the missing root LICENSE
- `CLAIM_PDF_AUDIT.md` — independent claim vs artifact table

This schema is **not** `ScientificResultVerification.v1`. Issue #283 owns that record. Packages consume it if JSON with that `schema_version` appears under `evidence/`.

```bash
python3 research/paper-programme-v1/journal_package/check_journal_package.py
python3 research/paper-programme-v1/journal_package/check_journal_package.py --paper P1
python3 research/paper-programme-v1/journal_package/check_journal_package.py --paper P1 --write-hashes
python3 research/paper-programme-v1/journal_package/check_journal_package.py --write-hashes
pytest -q tests/unit/publication/test_journal_package.py
```

`package_status` has three non-overlapping authority states:

- `SCAFFOLDING`: no PDF is retained; at least one package claim remains `OPEN`.
- `SUPERSEDED`: a required and checksummed historical PDF is retained, the
  generator-owned `RENDER_CLOSURE_STATE.json` says `SUPERSEDED`, current
  submission authority is explicitly false, and at least one current package
  claim remains `OPEN`.
- `SUBMISSION_READY`: a required and checksummed current PDF is present and no
  package-level missing artifact or `OPEN` claim remains.

`SUPERSEDED` preserves an earlier inspected record without relabelling it as a
current render. It is not an alias for `SCAFFOLDING` or a weakened
`SUBMISSION_READY`. P1 H1 remains `NOT_SUPPORTED` under every package state.
