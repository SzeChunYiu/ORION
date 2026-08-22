# X1-B k=4 — exact minimum-last dominance for the frozen forbidden-prefix search

Parent: #900.
Prerequisite state quotient: `X1B_K4_FORBIDDEN_PREFIX_ILLEGAL_STATE_QUOTIENT_2026-08-22.md`.
Committed before use in the authoritative layerwise search.

## Canonical multiset state

Under the frozen nondecreasing element ordering, a partial prefix at fixed depth d is represented for future search by

`(I, last)`,

where I is the exact illegal-next-term set and `last` is the smallest canonical element index allowed for the next term.

## Dominance lemma

Suppose two depth-d prefixes reach the same illegal set I with last indices `a<b`.

The continuation set from `(I,b)` is a subset of the continuation set from `(I,a)`, because:

1. legality of a candidate x depends only on `x notin I`;
2. both states have the same transition `I -> I union (I-x)`;
3. every candidate index `x>=b` is also allowed by the ordering constraint `x>=a`.

Therefore:

> At fixed depth and fixed illegal set I, retaining only the **minimum** reachable last index is exact for the existence question.

If the minimum-last state cannot reach depth 10, no larger-last realization of the same I can do so. Conversely, any witness from a larger-last state is also a valid continuation from the minimum-last state.

## Layerwise exact DP

The frozen search may therefore be implemented as:

- layer 0: one state `(F,0)`;
- from every layer-d state `(I,last)`, enumerate every legal canonical element x with index at least last;
- compute `J=I union (I-x)`;
- in layer d+1, store `min(existing_last[J], index(x))`;
- if layer 10 is nonempty, serialize an explicit predecessor chain as a witness;
- if a layer becomes empty before depth 10, the class is exactly NO.

This is a dominance compression of the already admitted canonical multiset search. It introduces no `GL(3,5)` quotient, heuristic pruning, or altered success criterion.

## Claim boundary

This is an exact finite-search optimization only. It carries no C15 theorem or novelty authority.