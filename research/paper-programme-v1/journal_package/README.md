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
python3 research/paper-programme-v1/journal_package/check_journal_package.py --write-hashes
pytest -q tests/unit/publication/test_journal_package.py
```

`package_status` stays `SCAFFOLDING` while compiled PDFs, DOIs, or paper-level `PEER_REVIEW_READY` evidence are absent from the tree. P1 H1 remains `NOT_SUPPORTED`.
