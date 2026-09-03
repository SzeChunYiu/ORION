# ORION-09 — submission readiness record

**Terminal: `READY_PENDING_TEMPLATE`** (Wave-1 filing bar, defined in
`WAVE1_UPGRADE_LANE_VENUE_DECISIONS_V1.md` — PR #1692, pending). A complete
standalone manuscript exists and compiles with zero undefined references; it is
not in the venue class and carries no author block. What remains is mechanical,
not authorial.

Supersession note: the earlier label on this record,
`READY_TO_SUBMIT_SECOND_TIER`, named the venue tier reached but hid the
venue-format conversion that this record itself lists below as a remaining
input. That label is superseded by this one.

**Venue tier:** second tier. Target venue _Quantum_; PRX Quantum
assessed and declined (see `VENUE_DECISION.md`). Fallback Quantum Science and
Technology.

## Gate table

| Gate | State | Evidence |
|---|---|---|
| Canonical manuscript designated | Closed | `CANONICAL_SOURCE_DECISION.md` |
| Compiles to submittable PDF | Closed | 6 pages, no undefined references, no overfull boxes |
| Headline numbers verified | Closed | Error floor 43 and the 1,146-instance exhaustive domain re-derived from the predicate-language artifact; terminal reads zero-unachievable-at-any-budget |
| Refutation preserved | Closed | The StabPrep negative transfer is retained as a headline result, not relegated |
| Claim ceiling respected | Closed | No universal low-order law claimed; no physical quantum-advantage claim |
| House style | Closed | No machine tokens, internal identifiers, or sibling cross-references in prose |
| Content binding | **Unchanged and open** | `UNBOUND / CANNOT_CHECK`, same as baseline |
| Digest rows verified | Closed | Every quoted SHA-256 re-derived from the file |
| Venue, manifest, cover letter, availability | Closed | This directory |

## One gate that is open, stated plainly

This paper's content-binding state is `UNBOUND / CANNOT_CHECK`. No committed
digest watches its manuscript, so a change to its bytes would not be noticed by
any repository check. That was true before this pass and is true after it.

This is not a submission blocker for _Quantum_, which does not ask about it. It
is recorded because "nothing watched" and "nothing changed" both report zero,
and the difference matters to anyone relying on this repository's own
guarantees. Closing it means adding a manifest for this paper's manuscript.

## What changed in the manuscript

Nothing. ORION-09 was already free of machine tokens, internal identifiers,
sibling cross-references, and defensive scaffolding. Its one use of "companion"
refers to a rank-2 companion grammar, which is a technical term rather than a
sibling paper.

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

1. **Author list** in final order; the title page reads "Working framework draft".
2. **Affiliations** and **ORCID** identifiers.
3. **Corresponding author** and email.
4. **Funding statement**, **competing-interests declaration**.
5. **Concurrent-submission decision.** Two sibling manuscripts are routed to the
   same journal in this wave; the filer must decide whether to stagger or
   disclose. See `VENUE_DECISION.md`.
6. **Public archival deposit** of the analyzers and results, with the DOI
   substituted into the availability statement.
7. **Licence election** for deposited artifacts.
8. **Optional:** add a content manifest for this paper so the binding gate above
   can close.

Also required before filing: **convert to Quantum's submission template** (quantumarticle) and record the anonymisation decision.
