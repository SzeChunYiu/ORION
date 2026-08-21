# P7 literature evidence

Retrieval records for the sources cited in `manuscript/FINAL.md`, mirroring
`papers/paper-02-open-world-scientific-discovery/evidence/literature/`.

## Why this directory exists

Section 2.3 opened with a claim about a body of work and cited none of it:

> Planning research has long shown that representation and abstraction affect
> solvability, search complexity and solution preservation.

A grep across P7 for the obvious sources — Knoblock, Bacchus, Sacerdoti, CEGAR,
"change of representation" — returned zero hits. That is a desk-reject
independent of whether P7's own contribution is novel: a reviewer does not have
to dispute the contribution to object that the related-work section
characterises a field without a reference.

## Verdict vocabulary

`verdict` records **how the citation was checked**, not how good the work is.

| verdict | meaning |
|---|---|
| `VERIFIED` | the primary source was retrieved and its title/authors/venue read from it |
| `UNVERIFIED_SECONDARY` | identified from search results or a bibliographic index; the primary source has **not** been retrieved |

`UNVERIFIED_SECONDARY` is deliberately not a soft `VERIFIED`. A record carrying
it is a lead, and citing it in the manuscript without promoting it first would
put a claim in the paper that nothing in this directory backs.

## Current state

| key | verdict | role in 2.3 |
|---|---|---|
| `knoblock1994` | `VERIFIED` | solution preservation under abstraction (ordered monotonicity) |
| `bacchus1991downward` | `UNVERIFIED_SECONDARY` | the downward refinement property itself |
| `backstrom1995` | `UNVERIFIED_SECONDARY` | **counterweight**: abstraction can be exponentially *worse* |
| `stateabstraction2021` | `UNVERIFIED_SECONDARY` | modern synthesis; route into TAMP |

`backstrom1995` is the one that changes what 2.3 should say. As written the
section is one-directional — abstraction helps. The negative result says
abstraction hierarchies can make planning exponentially less efficient, and a
paper that transports certificates across abstractions inherits that risk. A
related-work section that cites only the favourable half is not a survey.
