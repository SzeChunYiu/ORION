# Supersede note — 2026-08-16 journal-readiness audit, Paper III only

**Date:** 2026-08-17  
**Subject audit:** `research/paper-programme-v1/JOURNAL_READINESS_AUDIT_2026-08-16.md`  
**Issue:** #100  
**Does not close:** issue #280 (adversarial V2 atlas), issue #209 / PR #269 (Phase-3 protocol prefreeze)

## What is superseded

The 2026-08-16 audit recorded that none of the five papers had run external evaluation, and that superiority claims must remain `CANNOT_CHECK` until those experiments exist. For **ORION-P3 public-reference mapping V1/V1.1** that sentence is no longer true.

Verified on `origin/main` (this note does not re-run the mapping evaluator):

| Artifact | Identity |
|---|---|
| Initial portable gold | `gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl` SHA-256 `35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8` (32 lines) |
| Confirmatory portable gold | `gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl` SHA-256 `13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b` (32 lines, zero case-id overlap) |
| Custody | `evidence/public-reference-v1/SHA256SUMS` and `evidence/public-reference-v1.1-confirmatory/SHA256SUMS` |
| Provenance | `evidence/public-reference-v1/PROVENANCE.env` and `evidence/public-reference-v1.1-confirmatory/PROVENANCE.env` |
| Confirmatory analysis | `evidence/public-reference-v1.1-confirmatory/CONFIRMATORY_ANALYSIS.json` |

`CLAIM_LEDGER_V1.md` P3.C5 remains the authority for the confirmatory numbers. This supersede note does not promote P3.C7/C8.

## What is not superseded

- Independently annotated eight-family expert gold (`annotator-a`/`annotator-b` files: 0).
- `gold/adjudicated/P3.*.gold.json` seed-to-gold-v1 templates. Those files are not expert gold.
- Raw-text / RAG / long-context / SCOPE-SCION / schema-contract baselines.
- Original figures P3-1..P3-7.
- `PEER_REVIEW_READY`.

An LLM cannot become gold. Issue #280 owns any V2 adversarial atlas.
