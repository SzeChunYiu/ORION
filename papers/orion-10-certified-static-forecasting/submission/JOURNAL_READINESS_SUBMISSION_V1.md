# ORION-10 — submission readiness record

**Terminal: READY_TO_SUBMIT_SECOND_TIER.** Target venue _Quantum_. QST was
considered under the routing's impact condition and is not warranted.

## Gate table

| Gate | State | Evidence |
|---|---|---|
| Canonical manuscript designated | Closed | `CANONICAL_SOURCE_DECISION.md` |
| Compiles to submittable PDF | Closed | 6 pages, no undefined references, no overfull boxes |
| Headline numbers verified | Closed | 9,547 compared instances at zero error, 64 witnesses, 10,481 compared instances, all re-derived from the evaluator and hybrid-family artifacts |
| Refutation preserved | Closed | The explanation-layer refutation is retained as a headline result and the explanation stays open |
| Claim hierarchy explicit | Closed | Theorem above finite benchmark above unresolved explanation, stated in that order |
| Claim ceiling respected | Closed | Bounded to the frozen grammar and objective; no physical quantum-advantage claim |
| House style | Closed | One sibling-paper reference removed from Related Work; the programme is named once, in Reproducibility |
| Content binding | **Unchanged and open** | `UNBOUND / CANNOT_CHECK`, same as baseline |
| Digest rows verified | Closed | Every quoted SHA-256 re-derived from the file |
| Venue, manifest, cover letter, availability | Closed | This directory |

## One gate that is open, stated plainly

Content-binding state is `UNBOUND / CANNOT_CHECK`. No committed digest watches
this manuscript, so the repository would not notice a change to its bytes. This
was true before this pass and remains true. It is not a venue requirement, but
it is a real coverage gap and is recorded as one rather than reported as a pass.

## What changed in the manuscript

One edit. The Related Work section attributed donor machinery to "the companion
technical results" and referred to the paper by an internal identifier; both were
replaced with plain prose that cites the underlying results as ordinary
references. No claim was affected.

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
5. **Concurrent-submission decision** for the three programme manuscripts routed
   to this journal in the same wave. See `VENUE_DECISION.md`.
6. **Public archival deposit** of the evaluator and hostile-search artifacts,
   with the DOI substituted into the availability statement.
7. **Licence election** for deposited artifacts.
8. **Optional:** add a content manifest for this paper so the binding gate can
   close.

Also required before filing: **convert to Quantum's submission template** (quantumarticle) and record the anonymisation decision.
