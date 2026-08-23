# Manuscript house style: agreed changes, not yet applied

Recorded 2026-08-21 from review feedback. **Not yet done.** Parked behind the
primary goal (drive the harnesses until every negative scientific result is
resolved, and fix paper contents). Written down here so the decisions survive.

## The structural decision

**Papers 1–14 must not presuppose that the composed system exists.** Each is a
standalone contribution: a mechanism, its theory, and an experiment. The system
is assembled and named only in Paper 15. A paper that needs a result from a
sibling **cites it** like any other reference; there are no internal
cross-references to "Paper II", "P2-X" or a shared programme.

## What that means per manuscript

1. **Remove the system name from the body.** In P2 it appears 38 times as the
   subject of claims. Rewrite so the claim is about the mechanism: "routes count
   as independent only when independence is earned", not "<system> counts routes
   as independent". Name the implementation once, in Methods or Availability,
   as the artifact under test.

2. **No machine tokens in prose.** `CANNOT_CHECK`, `TIER_B_committed`,
   `P2_WIDE_EXTERNAL_CANNOT_CHECK` and similar are internal vocabulary. P2's
   body carries 18 of the first alone and 60 `\texttt{}` spans in total. The
   *idea* is a real methodological contribution and stays: outcomes are
   three-valued, and "we could not determine this" is reported separately from
   "we determined this is false". State that once, in plain English, in Methods.
   Then say "remains undetermined" in prose rather than printing the token.

3. **No repository paths or artifact filenames in the narrative.** P2's body
   names 19 `.json` files. Those belong in Data Availability, which is exactly
   where a reader looks for them.

4. **Drop the defensive scaffolding sections.** `\section{Problem and claim
   boundary}` is an Introduction. `\section{Nearest work}` is Related Work, and
   should position the contribution among neighbours rather than enumerate
   "this paper does not claim X as novel" for a dozen values of X. The boundary
   is real and stays — it belongs in Limitations, stated once, in prose.

5. **No table of open-literature checks.** Discuss the neighbouring work and
   cite it. (Present in P1's `sections/06-related-work-boundary.tex`; P2 carries
   the prose equivalent inside "Nearest work".)

6. **Internal identifiers out of the prose.** "P2-X" is an experiment; call it
   one and give it a name a reader can hold, e.g. "the exact-contract battery".

## Scope

P2 first, reviewed, then the same treatment paper by paper as each is finished.
