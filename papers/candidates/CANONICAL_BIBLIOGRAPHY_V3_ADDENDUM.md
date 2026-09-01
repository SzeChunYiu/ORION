# Canonical bibliography V3 addendum — donor sources for ORION-16 and ORION-18

**Date:** 2026-09-01
**Extends:** `CANONICAL_BIBLIOGRAPHY_V2.md`, which stays authoritative for entries 1–39.

V2 is strong on authorization, delegation and provenance, and it already carries the
truth-maintenance and belief-revision entries. It carries nothing from the static-analysis,
dependence-analysis or effect-system literature that the ORION-16 theorems restate, and
nothing from the proof-carrying, capability, timestamping or temporal-database literature
that ORION-18's revocation properties restate.

Both manuscripts cited **no source at all** before `FINAL_V6.md` and `FINAL_V4.md`: zero
author–year references, zero numbered references, zero DOIs. The entries below are what
those new attributions resolve against.

## Static analysis, dependence and effects — ORION-16

40. Patrick Cousot, Radhia Cousot. **Abstract Interpretation: A Unified Lattice Model for
    Static Analysis of Programs by Construction or Approximation of Fixpoints.** POPL 1977,
    pages 238–252. ACM Press. DOI `10.1145/512950.512973`.
41. A. J. Bernstein. **Analysis of Programs for Parallel Processing.** *IEEE Transactions on
    Electronic Computers*, 1966. DOI `10.1109/PGEC.1966.264565`.
42. John M. Lucassen, David K. Gifford. **Polymorphic Effect Systems.** POPL 1988, pages
    47–57. ACM Press. DOI `10.1145/73560.73564`.

## Proof-carrying authorization, capabilities and revocation — ORION-18

43. Andrew W. Appel, Edward W. Felten. **Proof-Carrying Authentication.** 6th ACM Conference
    on Computer and Communications Security, 1999. DOI `10.1145/319709.319718`.
44. Jack B. Dennis, Earl C. Van Horn. **Programming Semantics for Multiprogrammed
    Computations.** *Communications of the ACM*, 1966. DOI `10.1145/365230.365252`.
45. **Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP).** RFC 3161, IETF,
    2001.
46. Christian S. Jensen, Richard T. Snodgrass. **Temporal Database.** In *Encyclopedia of
    Database Systems*, Springer, 2009. DOI `10.1007/978-0-387-39940-9_395`.

## Verification provenance

Each entry was checked against a primary or publisher record rather than recalled, on
2026-09-01:

| entry | how checked | fields confirmed |
|---|---|---|
| 40 | publisher record and the authors' own POPL'77 page | title, venue, pages, DOI |
| 41 | IEEE record for the DOI | author, title, journal, year, DOI |
| 42 | ACM DL record | authors, title, venue, pages, DOI |
| 43 | the authors' own PDF, plus the ACM DL record | authors, title, venue, year, DOI |
| 44 | ACM DL record | authors, title, journal, year, DOI |
| 45 | the RFC itself | number, title, publisher, year |
| 46 | Springer reference-work record | authors, title, work, year, DOI |

Entry 41's volume and page range were **not** confirmed from a primary record and are
deliberately omitted rather than reconstructed. Whoever prepares the submission should add
them from the publisher's record.

## Deliberately excluded, pending verification

Assurance-case notation — Goal Structuring Notation and the safety-case literature around it
— is a plausible donor for the three-state blocker treatment and for the claim-to-evidence
argument structure. It is **not** listed above because no primary record for it was checked
on 2026-09-01, and an unverified entry is worse than a missing one. Resolve it before
submission rather than citing it from recollection.

## Submission rule, inherited from V2

Before submission, search for peer-reviewed versions of any cited preprint and replace the
preprint citation when an archival version exists.
