# ORION-P1 journal package

**Status:** `SCAFFOLDING` — not `PEER_REVIEW_READY`, not a submission ZIP.

This directory is the Gate 7–9 inventory for Paper I. Required files, hashes, compile instructions, license gaps, and the independent claim/PDF audit live here. Missing PDFs, DOIs, cover letters, and independent reproduction receipts are listed as `CANNOT_CHECK` in `MANIFEST.json`.

Headline reproduction (tables only):

```bash
make paper01-results
```

See `../REPRODUCE.md`. Issue #283 owns `ScientificResultVerification.v1`; this package consumes those records if they appear under `evidence/` and does not fork the schema.
