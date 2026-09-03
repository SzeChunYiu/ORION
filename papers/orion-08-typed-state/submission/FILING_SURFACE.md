# ORION-08 — the only filing surface

**Read this before uploading anything.** Written 2026-09-03.

The filing surface is `submission/tier-b-final-20260901/`, and nothing else in
this directory tree is uploadable. Scientific authority remains
`papers/orion-08-typed-state/CLAIM_LEDGER_V4.md`; the canonical source is the
LaTeX tree `papers/orion-08-typed-state/manuscript/` per
`CANONICAL_SOURCE_DECISION.md`. This file adds no claim and changes no result.

## Upload these bytes

Target venue **TMLR** (OpenReview, double-blind); arXiv route prepared alongside.

| Route | File | Bytes | SHA-256 |
|---|---|---:|---|
| journal (TMLR) | `tier-b-final-20260901/journal/manuscript.pdf` | 268,512 | `eb966292a43a2ceda739bfe5530054cddb4532ef82b2367e350942425aba17f4` |
| journal (TMLR) | `tier-b-final-20260901/journal/source.zip` | 29,762 | `c16235e24981d5e254c537e2ebccc75ee9a9d82cdfc2416b5e0819090a969864` |
| journal (TMLR) | `tier-b-final-20260901/journal/review-materials.zip` | 6,949 | `bcdb431ba6c737ecd0e031f9fa5c2d2ef2b8f2a9a5efa16cb0916be68a2ed6c8` |
| arXiv | `tier-b-final-20260901/arxiv/manuscript.pdf` | 258,246 | `4a505463f60bbc8c9287258cf28a5923d81f61b43b13c1788278c1c4c3e384dd` |
| arXiv | `tier-b-final-20260901/arxiv/source.zip` | 21,623 | `3fe8b4e8fff2a4607f7ef95c4bafd5c44bd8ea478a47b3a4089c5b5598f82e28` |

The package is checksum-closed: `tier-b-final-20260901/SHA256SUMS` (28 rows)
verified with zero mismatches on 2026-09-03. Re-verify before filing with:

```sh
cd papers/orion-08-typed-state/submission/tier-b-final-20260901 && shasum -a 256 -c SHA256SUMS
```

Per-route filing steps, declarations and checklists live in
`tier-b-final-20260901/journal/` (`SUBMISSION_CHECKLIST.md`,
`TMLR_OPENREVIEW_CHECKLIST.md`, `COVER_LETTER.md`, `DECLARATIONS.md`,
`TITLE_PAGE.md`) and `tier-b-final-20260901/arxiv/`. Portal identifiers, author
metadata and licence choices remain author-controlled and are not in the repo
(`tier-b-final-20260901/HUMAN_INPUTS_REQUIRED.md`).

## Do NOT upload

`submission/superseded-tmlr-pandoc-lane/manuscript.pdf` (57,551 bytes,
`07b8c3412bd03700b483ec96117831c3fc5fd50163701e99ca043ba973f0de28`) is the
retired pandoc lane's 6-page render. Until 2026-09-03 it sat at this directory's
top level as `submission/manuscript.pdf`, where it was the first PDF a filer
would reach. It is disqualified on four independent counts:

1. superseded title — "… Six Matched-Information Mechanism Studies", without the
   "and Real-Data Boundaries" scope the live paper carries;
2. marked **"Working framework draft"** on its title page;
3. **not in TMLR double-blind form** — it carries neither the "Under review as
   submission to TMLR" banner nor the "Anonymous authors / Paper under
   double-blind review" block that the live journal route carries (verified by
   text extraction; it also contains no author name, so this is a formatting
   disqualification, not an identity leak);
4. predates the V4 theorem correction
   (`theory/binding-sufficiency-lattice-v1/THEOREM_CORRECTION_2026-09-01.md`) and
   the multiplicity disclosure, so it states claims the live ledger has narrowed.

Its 2026-08-28 manifests moved with it
(`superseded-tmlr-pandoc-lane/SUBMISSION_MANIFEST_20260828.{md,sha256}`) and are
stale against live sources on every entry checked; they bind nothing and must not
be repaired.
