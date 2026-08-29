# Parallel Wave-1 closeout draft (retained, non-canonical)

> Canonical version is `WAVE1_CLOSEOUT_2026-08-28.md`. This is an independently written
> draft from the chatgpt lane, retained because it records one result the canonical
> draft does not: the Protected V3 exact-axis `CANNOT_CHECK` terminal selection
> (ORION 30/30, H1-selected comparator 0/30, escalation-capable comparator 15/30),
> with its own scope limit. Not authoritative; do not cite in place of the canonical file.

# ORION-14 Wave 1 submission closeout — 2026-08-28

Tracking issue: #1609

## Publication objective

Prepare the **current** ORION-14 manuscript for TMLR filing. Historical V2 readiness and release artifacts remain evidence records; they do not substitute for an audit of the current manuscript bytes.

## Current scientific authority

- Protected V2 H1 remains supported: 0/360 false promotions for ORION versus 180/360 for the strongest frozen comparator mechanism.
- Protected V2 H2 remains supported: both systems cover 60/60 clean positives.
- Protected V2 H3 remains a retained saturated-axis `NOT_SUPPORTED` historical result.
- Protected V3 adds a distinct exact-axis result: ORION selects the correct `CANNOT_CHECK` terminal on 30/30 cases; the H1-selected comparator selects it on 0/30 and the escalation-capable comparator on 15/30. This is **terminal/interface expressiveness under the frozen non-compensatory gate lattice**, not a general scientific-judgement superiority claim.
- The two H3 identities must not be pooled or used to relabel the V2 result.

Authoritative sources for this distinction are `CLAIM_LEDGER_V4.md`, `evidence/protected_v3/`, and `journal_package/CLAIM_PDF_AUDIT.md`.

## Closeout blockers

- [ ] `p4-tmlr-submission-audit` passes on this exact PR head.
- [ ] Current TMLR PDF is rebuilt by the clean-room workflow and its SHA-256 is retained.
- [ ] Independent final proofread is performed on the **exact current PDF hash**, including abstract, all headline numbers, V2/V3 H3 distinction, limitations, figures and tables.
- [ ] Current claim/evidence map is checked for H1/H2/V2-H3/V3-H3 consistency.
- [ ] Current archive/release is either proven to contain these exact current submission bytes or a new archive is produced; historical releases remain historical.
- [ ] Submission-date nearest-work review is refreshed if filing occurs after the current freshness window.
- [ ] Human-only filing metadata is supplied at upload time.
- [ ] OpenReview submission ID is recorded only after a real submission exists.

## Close criterion

`READY_TO_FILE_TMLR` only when the exact current PDF has a green clean-room audit and an independent proofread. No new exploratory science is required merely for Wave 1 closeout unless that audit exposes a scientific defect.
