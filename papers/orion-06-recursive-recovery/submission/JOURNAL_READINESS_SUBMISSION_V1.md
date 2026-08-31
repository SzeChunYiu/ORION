# ORION-06 — submission readiness record

**Terminal: READY_TO_SUBMIT_SECOND_TIER.** Target venue TMLR; AIJ assessed and
declined on scope (see `VENUE_DECISION.md`).

## Gate table

| Gate | State | Evidence |
|---|---|---|
| Canonical manuscript designated | Closed | `CANONICAL_SOURCE_DECISION.md`; five competing Markdown drafts retired from submission role |
| Checkers pass | Closed | `check_transition_graph.py` exit 0; `verify_orion06_negative_coverage.py` prints `ORION06_NEGATIVE_COVERAGE=PASS` |
| Compiles to submittable PDF | Closed | 6 pages, no undefined references, no overfull boxes |
| Claim ceiling respected | Closed | `CLAIM_LEDGER_V3.md`; audit `scientific_authority_delta = NONE` |
| Undetermined results preserved | Closed | Cross-domain general-method verdict left undetermined, not converted |
| House style | Closed | Machine token removed from Discussion; internal paper identifiers and sibling cross-references removed; programme named once, in Reproducibility, as the artifact under test |
| Content binding | Unchanged | `BOUND_PARTIAL / PASS` |
| Digest rows verified | Closed | All quoted SHA-256 values re-derived from the files |
| Venue, manifest, cover letter, availability | Closed | This directory |

## What changed in the manuscript

1. Removed `CANNOT_CHECK` from Discussion prose, replaced with plain English.
2. Removed all internal paper identifiers from narrative text.
3. Removed sibling-paper cross-references; the results generated inside the
   programme are now cited as ordinary references rather than routed to named
   companion papers.
4. Moved the single naming of the programme under test into Reproducibility.

No claim was widened. The manuscript's central claim remains descriptive and
one-programme, and the undetermined cross-domain verdict is untouched.

## Venue-format conversion — named explicitly

The manuscript is `\documentclass[11pt]{article}` with `\author{Working framework
draft}`. It is a complete, sectioned, bibliography-resolved manuscript that
compiles cleanly, but it is **not** in TMLR's submission format: no venue
class or style file, no author block, and no anonymisation decision recorded.

Converting it requires tmlr.sty, which is not obtainable from the toolchain used in
this pass, so this is left as an input rather than attempted and half-done.
Treat it as mechanical filing work, not evidence work: the science, the claim
ceiling, and the checks are complete and independent of the template.

## Remaining inputs — human only

1. **Author list** in final order; the title page reads "Working framework draft".
2. **Affiliations** and **ORCID** identifiers.
3. **Corresponding author** and email.
4. **Funding statement** and grant numbers.
5. **Competing-interests declaration.**
6. **TMLR-specific:** public-discussion opt-in; conflicting-reviewer exclusions.
7. **Public archival deposit** of the inventory, transition graph, and audit
   records, with the DOI substituted into the availability statement.
8. **Licence election** for deposited artifacts.
9. **Regenerate `RECEIPT_INDEX.md`** against the final manuscript, as the
   Reproducibility section itself requires, once the author list is fixed and
   no further text changes are expected.

Also required before filing: **convert to TMLR's submission template** (tmlr.sty) and record the anonymisation decision.
