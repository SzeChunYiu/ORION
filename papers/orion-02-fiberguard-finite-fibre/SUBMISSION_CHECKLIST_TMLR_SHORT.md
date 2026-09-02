# ORION-02 TMLR submission checklist — short theory note (decision (a))

**Prepared:** 2026-09-02, for the human filer. Decision (a) of SzeChunYiu/ORION-paper#78 is final: the TMLR filing is the SHORT note, not the full-length manuscript.  
**Package status (honest, fail-closed):** `TEXT_SURFACES_COMPLETE__RENDERING_AND_PORTAL_PENDING`. The short note exists as repository text only; no TMLR-style PDF has been built for it in this lane (no LaTeX builds were permitted here). Nothing below asserts a submission ID, DOI, or filing date.

## What to file (decision-(a) surface)

| Artifact | Exact path (from `/Users/billy/ORION-tierb/papers/orion-02-fiberguard-finite-fibre/`) | State |
|---|---|---|
| Manuscript source (short note) | `MANUSCRIPT_SHORT_V1.md` | Complete text; needs typesetting into the mandatory unmodified TMLR LaTeX style before upload |
| Canonical parent (do not file; provenance) | `MANUSCRIPT_V3.md` + `CLAIM_LEDGER_V3.md` | Untouched, canonical; the short note is derived from them |
| Cover letter | `COVER_LETTER_TMLR_SHORT_V1.md` | Editor-facing (identified); paste into the OpenReview cover-letter field or upload as instructed by the portal |
| Freeze authority | `PUBLICATION_FREEZE_ADDENDUM_V2.md` | Current; `PUBLICATION_FREEZE_ADDENDUM_V1.md` is superseded and header-marked |
| Ledger record of decision (a) | `CLAIM_LEDGER_V3.md`, section "Dated addendum — 2026-09-02" | Additive; canonical tables unchanged |
| Prior TMLR requirement notes | `TMLR_FILING_CHECKLIST_V4.md` (venue URLs checked 2026-08-31) | Reuse its official-source list; re-open them before filing |

**Do not file the full-length surface.** `submission/tier-b-final-20260901/journal/` (7-page PDF) was built from the full `MANUSCRIPT_V3.md` before decision (a). It remains a valid checksum-closed package for that surface, but decision (a) designates the short note. If the short note is filed, the full-length PDF is not uploaded to TMLR in the same submission. Leave `submission/README.md` exactly as the P0 fix placed it.

## Repository-side steps that remain before upload (build lane, not done here)

- [ ] Typeset `MANUSCRIPT_SHORT_V1.md` into the mandatory unmodified TMLR LaTeX style (double-blind; no layout-altering changes). Strip the HTML provenance comment at the top when converting; it is repo metadata, not manuscript text.
- [ ] Rebuild/refresh the anonymous supplementary archive so its evidence paths mirror the boundary table (V3-E1..E3 under `extensions/r18`, `extensions/r19`, `experiments/results`; V3-E5 under `rounds/r23-density-backoff-revival`; V3-E6/E7 under `rounds/r24-arm-conditional-fibres-revival`), with manifest and SHA-256 digests.
- [ ] Re-run anonymity and checksum closure on the new rendered set; record the venue-budget ledger entry for the measured page count (TMLR guidance checked 2026-08-31 allowed any length; re-open the official pages before filing).
- [ ] Verify the boundary table numbers against the receipts one final time in the rendered PDF (key values: 0/99; 35->70 and 0/50; 0.210/0.331, 0.169/0.182; zero coverage; 32/44 vs 39/44, p=0.0923; 20/44; 14/44, (14,6,0,24), p=0.03125; r=-0.144, p=0.353).

## Human confirmation before upload (portal-only; no scientific authority)

- [ ] Approve final title, abstract, author order and contribution of the short note.
- [ ] Confirm every author satisfies TMLR authorship criteria, has a complete active OpenReview profile, and has sufficient annual TMLR quota.
- [ ] Confirm no overlapping publication or disallowed dual submission (the full-length ORION-02 PDF must NOT be simultaneously under review elsewhere).
- [ ] Complete conflicts, funding and competing-interest declarations; human-subject/IRB and broader-impact responses; Action Editor suggestions.
- [ ] Upload the rendered anonymous PDF plus anonymous supplement; paste/upload the cover letter.
- [ ] Inspect the portal-rendered files before final submission; preserve the issued OpenReview identifier (record it only after the portal issues it).

## Internal-only fallback (NOT for the cover letter or any venue-visible material)

If TMLR length norms or editorial routing fight the short-note compression (they should not: guidance checked 2026-08-31 sets no length limit), the named fallback is a methodology-note venue that accepts bounded theory contributions with explicit negative results (for example a JMLR-family technical-note track or an ML-methodology venue accepting short papers). That fallback is an internal decision aid for the author only; the cover letter names TMLR alone.

skills-applied: nature-writing, nature-polishing, nature-publication-closure
