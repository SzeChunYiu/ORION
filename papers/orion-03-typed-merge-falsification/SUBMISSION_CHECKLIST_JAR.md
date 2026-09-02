# JAR submission checklist — ORION-03 Tier-B closure (2026-09-02)

**Target:** Journal of Automated Reasoning (Springer Nature), original research article,
identified/single-blind. **No portal action has been taken.** No submission ID, DOI, or
filing date exists yet and none is invented here.

## Step 0 — REBUILD REQUIRED BEFORE FILING (blocking)

The 2026-09-02 clarification edits changed `MANUSCRIPT_V3.md` (Related Work deltas +
Limitations expressiveness-gate paragraph, incl. new `dekleer1986` citation) and
`publication_closure_20260831/references.bib`. Every packaged PDF/source/checksum below
predates them.

- [ ] On a **build-capable host** (laptop billy or LUNARC — never the Mac mini), rerun
      the release build from `publication_closure_20260831/build_release.py`
      (it stages `MANUSCRIPT_V3.md` + `publication_closure_20260831/references.bib`).
- [ ] Confirm the rebuilt PDF renders the new Limitations paragraph and the de Kleer
      reference; refresh `SHA256SUMS`, `PACKAGE_MANIFEST.json`,
      `PUBLICATION_RELEASE_MANIFEST.json`, and the digest line in
      `CANONICAL_SUBMISSION_V3.md` (its current digest names the pre-clarification PDF).
- [ ] Rerun `python verify_references.py --output CITATION_METADATA.json` (closure dir)
      so `dekleer1986` enters the machine-verified citation record
      (`CITATION_VERIFICATION_V1.md` standard: Crossref/DOI field check; the entry was
      human-verified 2026-09-02 via ACM DL + ScienceDirect, DOI
      `10.1016/0004-3702(86)90080-9` — check digit `-9`).
- [ ] Replace the packaged `submission/tier-b-final-20260901/journal/COVER_LETTER.md`
      with `COVER_LETTER_JAR.md` (2026-09-02 refresh) in the rebuilt package.

## Filing artifacts (exact paths, post-rebuild)

- [ ] Manuscript PDF: `submission/tier-b-final-20260901/journal/manuscript.pdf` (rebuild;
      pre-clarification digest `4a1b7460…f0dc9`)
- [ ] Editable source archive: `submission/tier-b-final-20260901/journal/source.zip` (rebuild)
- [ ] Cover letter: `COVER_LETTER_JAR.md` at paper root (use this one)
- [ ] Title page: `submission/tier-b-final-20260901/journal/TITLE_PAGE.md`
- [ ] Declarations: `submission/tier-b-final-20260901/journal/DECLARATIONS.md`
- [ ] Metadata: `submission/tier-b-final-20260901/journal/metadata.json`
- [ ] Artifact archive: `submission/tier-b-final-20260901/journal/artifact.zip`
- [ ] Review materials: `submission/tier-b-final-20260901/journal/review-materials.zip`
- [ ] Package checksums: `submission/tier-b-final-20260901/SHA256SUMS` (refresh at rebuild)

## Claim authority (read before filing; answer referee queries from these)

- [ ] `CLAIM_LEDGER_V3.md` — frozen statuses: D3-C1–C6 PROVEN, D3-C7 VERIFIED, D3-C8
      MEASURED (46 hybrids / 1,962 tasks), D3-C9–C15 forbidden/null/adverse/refuted/cannot-check
- [ ] `SCIENCE_ITEM_DISPOSITION_20260902.md` — disposition ladder outcome (landed rung 3,
      honest narrowing; expressiveness gate OPEN)
- [ ] `FORMAL_SEPARATION_ATTEMPT_20260902.md` — why no separation theorem is claimed
- [ ] `PUBLICATION_FREEZE_ADDENDUM_V2.md` — current frozen surface (V3, narrowing-only)
- [ ] `NOVELTY_SUBTRACTION_20260828.md` and `VENUE_POSITIONING_V1.md` — positioning
      context (extend, never contradict)

## Venue compliance (repository-verified 2026-08-31/09-01)

- [ ] Reopen the live official guidelines page in a browser immediately before filing:
      https://link.springer.com/journal/10817/submission-guidelines
      (the 2026-09-01 automated recheck met Springer's JavaScript challenge; the
      repository snapshot is `publication_closure_20260831/VENUE_REQUIREMENTS_V1.md`,
      resolution record `submission/tier-b-final-20260901/VENUE_RESOLUTION.md`)
- [ ] Numeric citation style via `sn-mathphys-num`; every cited key resolves (rebuild check)

## Human-filer-only actions (portal facts; never synthesized)

- [ ] Portal account, corresponding-author confirmation, and portal classifications
- [ ] ORCID only if desired/mandatory; no identifier is invented
- [ ] Suggested/opposed reviewers
- [ ] Exclusivity confirmation ("not under consideration elsewhere") in the live portal
- [ ] Record the submission identifier after filing (leave a dated line in this file)

## Internal fallback lane (NOT for the cover letter)

- [ ] Fallback journal per the 2026-09-02 closure directive: **JAAMAS** (named here,
      internally only). NOTE: earlier positioning docs
      (`NOVELTY_SUBTRACTION_20260828.md`, `VENUE_POSITIONING_V1.md`) name ACM TOCL as the
      fallback — the filer should confirm which fallback lane is active before any
      fallback filing. This discrepancy is flagged, not silently resolved.

skills-applied: nature-publication-closure
