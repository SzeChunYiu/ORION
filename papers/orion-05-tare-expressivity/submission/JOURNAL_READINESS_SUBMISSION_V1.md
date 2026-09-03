# ORION-05 — submission readiness record

> **SUPERSEDED by `JOURNAL_READINESS_SUBMISSION_V2.md`** (terminal
> `PUBLICATION_PACKAGE_CLOSED__QUANTUM_FILING_METADATA_EXTERNAL`, 2026-08-31).
> V2 retires this record's central blocker: rechecked Quantum author guidance
> does **not** require `quantumarticle` at initial submission (encouraged, not
> mandatory), so the "venue class/style file" conversion below is not a filing
> gate. The real filing dependency — a public arXiv preprint in/cross-listed to
> `quant-ph` — is packaged and hash-bound at `final-20260831/` (2-row package,
> verified 2026-09-03 byte-audit). What remains open are portal/archive metadata
> only (final arXiv identifier, ORCID if supplied, funding statement,
> competing-interest declaration, licence/archive metadata). The
> `READY_PENDING_TEMPLATE` label and the remaining-inputs list below are
> historical. Supersession recorded 2026-09-03 (tier-B filing-surface closure
> pass).

**Terminal: `READY_PENDING_TEMPLATE`** (Wave-1 filing bar, defined in
`WAVE1_UPGRADE_LANE_VENUE_DECISIONS_V1.md` — PR #1692, pending). A complete
standalone manuscript exists and compiles with zero undefined references; it is
not in the venue class and carries no author block. What remains is mechanical,
not authorial.

Supersession note: the earlier label on this record,
`READY_TO_SUBMIT_SECOND_TIER`, named the venue tier reached but hid the
venue-format conversion that this record itself lists below as a remaining
input. That label is superseded by this one.

**Venue tier:** second tier.
Target venue _Quantum_; fallback npj Quantum Information. PRX Quantum was
assessed and declined on the significance gate (see `VENUE_DECISION.md`).
"Second tier" here names the venue tier reached, not a defect in the work.

## Basis for the terminal

| Gate | State | Evidence |
|---|---|---|
| Canonical manuscript designated | Closed | `CANONICAL_SOURCE_DECISION.md` |
| Compiles to submittable PDF | Closed | 7 pages, no undefined references, no overfull boxes |
| Headline numbers verified against artifacts | Closed | 4 headline figures traced to semantic keys in committed JSON; 0 numeric literals in the manuscript lack a repository trace |
| Claim ceiling respected | Closed | Claims Q1V3-1 … Q1V3-6 unchanged; no claim widened |
| House style | Closed | No machine tokens, internal identifiers, sibling-paper cross-references, or defensive scaffolding sections in narrative prose |
| Content binding | Unchanged | `BOUND_PARTIAL / PASS`, same as baseline; manuscript is not under any binding |
| Venue selected | Closed | `VENUE_DECISION.md` |
| Submission manifest | Closed | `SUBMISSION_MANIFEST.md` / `.sha256`, 12 files |
| Cover letter | Closed | `COVER_LETTER.md` |
| Data/code availability | Closed | `DATA_AND_CODE_AVAILABILITY.md` |

## Claims and their boundary, restated

The manuscript claims an exact support normal form for one frozen grammar under
one frozen objective, a zero-error static evaluator for the resulting family,
and a refutation-guided map of the remaining low-support coupling geometry. It
claims no full-circuit, hardware, or global block-encoding optimality. The
all-`n` finite-basis argument remains one pinned lemma short of closure, and the
manuscript says so rather than deferring the gap to a footnote.

Nothing in this packaging pass converted a null, an adverse result, or an
undetermined outcome into a pass. The refutation ladder is intact, including the
64 hostile hybrid witnesses that defeated the enlarged-borrow repair.

## What changed in this pass

Nothing in the manuscript body. ORION-05 was already free of machine tokens,
repository paths in narrative, internal identifiers, and sibling cross-references.
The pass added the submission package and recorded the canonical-source and
venue decisions.

## Venue-format conversion — named explicitly

The manuscript is `\documentclass[11pt]{article}` with `\author{Working framework
draft}`. It is a complete, sectioned, bibliography-resolved manuscript that
compiles cleanly, but it is **not** in Quantum's submission format: no venue
class or style file, no author block, and no anonymisation decision recorded.

Converting it requires quantumarticle, which is not obtainable from the toolchain used in
this pass, so this is left as an input rather than attempted and half-done.
Treat it as mechanical filing work, not evidence work: the science, the claim
ceiling, and the checks are complete and independent of the template.

## Remaining inputs — human only

These cannot be supplied from the repository and are the only things standing
between this package and a filed submission:

1. **Author list**, in final order. The manuscript currently reads
   "Working framework draft" on the title page; this must be replaced.
2. **Affiliations** for each author.
3. **ORCID** identifiers.
4. **Corresponding author** designation, email, and postal address.
5. **Funding statement** and grant numbers.
6. **Competing-interests declaration.**
7. **Author-contribution statement**, if the venue requests one.
8. **Suggested and excluded referees.**
9. **Public archival deposit.** The digests above reference an internal
   repository. Before filing, the five evidence artifacts and three generating
   modules should be deposited in a public archive (Zenodo or equivalent) and
   the resulting DOI substituted into the availability statement. The digests
   themselves do not change.
10. **Licence election** for the deposited artifacts.

Once 1–10 are supplied, the package is filable as it stands.

Also required before filing: **convert to Quantum's submission template** (quantumarticle) and record the anonymisation decision.
