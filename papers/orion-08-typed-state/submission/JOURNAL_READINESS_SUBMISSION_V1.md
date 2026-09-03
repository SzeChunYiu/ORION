# ORION-08 — submission readiness record

**Terminal: `READY_PENDING_TEMPLATE`** (Wave-1 filing bar, defined in
`WAVE1_UPGRADE_LANE_VENUE_DECISIONS_V1.md` — PR #1692, pending). A complete
standalone manuscript exists and compiles with zero undefined references; it is
not in the venue class and carries no author block. What remains is mechanical,
not authorial.

Supersession note: the earlier label on this record,
`READY_TO_SUBMIT_SECOND_TIER`, named the venue tier reached but hid the
venue-format conversion that this record itself lists below as a remaining
input. That label is superseded by this one.

**Venue tier:** second tier. Target venue TMLR.

## Gate table

| Gate | State | Evidence |
|---|---|---|
| Canonical manuscript designated | Closed | `CANONICAL_SOURCE_DECISION.md` |
| Compiles to submittable PDF | Closed | 6 pages, no undefined references, no overfull boxes |
| Headline numbers verified | Closed | All six re-derived from `N4_A`, `N1_C`, `N2_F5B` result artifacts; values match to the digit printed |
| Negatives preserved | Closed | Exact allocator tie at 0.9866 and donor tie at 0.9948 retained at equal prominence |
| Hostile validity gates | Closed | All five gates in the headline family report true in the artifact |
| Claim ceiling respected | Closed | Exact-synthetic scope unchanged; no deployment or novelty claim |
| House style | Closed | Two machine tokens removed from Results and Methods; internal paper identifiers removed |
| Content binding | Unchanged | `BOUND_PARTIAL / PASS` |
| Digest rows verified | Closed | Every quoted SHA-256 re-derived from the file |
| Venue, manifest, cover letter, availability | Closed | This directory |

## What changed in the manuscript

1. Replaced two machine tokens with prose: the typed arm identifier in Results
   and the proxy-heuristic label in Methods.
2. Removed internal paper identifiers from Introduction and Related Work, and
   rewrote the sibling-paper boundary paragraph so it distinguishes subjects
   rather than naming companion papers.
3. Replaced an internal identifier in the ethics section with plain English.

No claim was widened and no gate was moved.

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
4. **Funding statement**, **competing-interests declaration**.
5. **TMLR-specific:** public-discussion opt-in; conflicting-reviewer exclusions.
6. **Public archival deposit** of the N-lane results and protocols, with the DOI
   substituted into the availability statement.
7. **Licence election** for deposited artifacts.
8. **Fresh literature closure** on the typed/scoped-state composition claim,
   dated at submission. The manuscript makes no priority claim, so this is
   confirmatory rather than blocking.

Also required before filing: **convert to TMLR's submission template** (tmlr.sty) and record the anonymisation decision.
