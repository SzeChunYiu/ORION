# X1-B k=4 — independent BFS confirmation protocol for ten-prefix nonexistence

Parent: #900.
Primary result: `X1B_K4_TEN_PREFIX_FORBIDDEN_SUM_RESULT_2026-08-22.md`.

## Independence requirement

This verifier must not reuse:

- canonical multiset ordering;
- the primary DFS `(sumset,depth,last-index)` memo key;
- the primary recursion tree or dead-state table.

It may reuse only the frozen mathematical problem and the justified normalization of one off-plane term to `e3=(0,0,1)`.

## Algorithm

Represent a subset-sum state by the exact 125-bit set `Sigma_0(T)` including 0.

Initialize depth 1 with the normalized state `{0,e3}`.

For each depth `d=1,...,9`:

1. for every distinct sumset state at depth d;
2. try **all 124 nonzero group elements** as the next sequence term, with no ordering restriction;
3. retain the extension iff the translated old sumset creates no value in the frozen seven-point forbidden set;
4. insert the resulting sumset into the next-depth set, deduplicating **only by the 125-bit sumset**.

Because subset-sum sets are independent of term order, this breadth-first state quotient is complete for existence: every admissible ordered extension path maps to one retained state, and deduplication cannot remove a future possibility because future legality depends only on the current represented-sum set.

## Required evidence

Record:
- number of distinct states at every depth;
- whether depth 10 is empty;
- a predecessor chain for one maximum-depth witness;
- primitive replay of that witness;
- digest of each sorted depth-state set (or equivalent deterministic aggregate).

Strong confirmation terminal:

`DEPTH10_EMPTY__MAX_LENGTH9_CONFIRMED_INDEPENDENTLY`.

A memory/resource cap before complete depth-10 construction is `CANNOT_CHECK_RESOURCE_BOUND`, not confirmation.