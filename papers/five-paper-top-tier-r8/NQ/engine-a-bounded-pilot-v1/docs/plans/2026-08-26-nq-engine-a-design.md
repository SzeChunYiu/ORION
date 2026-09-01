# NQ Engine A Engineering-Staging Design

## Authority boundary

This tree carries `ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK` and
`EXPECTED_OUTCOME_EXPOSURE`. It cannot be described as clean-room, blinded, or
independent. It will not consume the published full counts as tests, stop conditions,
tuning targets, or acceptance criteria. Only small synthetic domains and explicitly
permitted lower witnesses are controls.

## Considered approaches

1. **Enumerate the whole automorphism group.** Simple and exact on tiny groups, but
   `|GL(3,5)|=1,488,000` makes repeated orbit scans unsuitable.
2. **Support-basis canonicalization (selected).** For a multiset of rank `r`, enumerate
   ordered independent `r`-tuples from its support, express all elements in each basis,
   embed the coordinates into the first `r` axes, sort, and choose the lexicographic
   minimum. This is exact under `GL(d,p)` and avoids enumerating irrelevant actions on
   the ambient complement.
3. **Stabilizer-chain canonical augmentation.** Best eventual route for the full census,
   but it adds a substantial proof and implementation surface. It is intentionally left
   as a disclosed full-scale optimization gap rather than improvised.

Canonical orderly generation enumerates nondecreasing multisets from the finite group and
retains exactly those equal to their support-basis canonical form. Range/coverage counters
make partial traversal explicit. This is complete but not claimed practical at the frozen
full scale without a separately proved augmentation/pruning layer.

## Exact factorization engine

For sequence `a_1,...,a_n` in `F_p^d` and `k` bins, dynamic programming processes one
item at a time. A state is a sorted tuple of `k` bin summaries `(used, sum)`, where each
item is either unused or assigned to exactly one bin. Bin sorting quotients only the
permutation of indistinguishable bins. The transition is

`(S_1,...,S_k) -> (S_1,...,S_j+a_i,...,S_k)`

plus the unused transition. A positive terminal has every bin used and every sum zero.
One deterministic index-set witness is retained per reachable state. Exhaustion without a
terminal is a valid negative only when every layer completed; state/time limits yield
`CANNOT_CHECK_RESOURCE_BOUND`. Certificates contain disjoint original indices and are
verified independently of DP state.

## Schemas, receipts, and testing

Versioned JSON Schemas cover inputs, certificates, receipts, coverage, and source
manifests. Receipts always include both exposure markers and the independence terminal.
A fail-closed builder refuses negative promotion from partial coverage, missing digests,
invalid certificates, or resource exits.

Tests are written before implementation and cover primitive arithmetic, rank and canonical
orbits, duplicate-free orderly output, brute-force equality on tiny domains, positive and
negative controls, certificate mutation, malformed hostile inputs, resource cutoffs,
deterministic manifests, and schema validation. Coverage hooks record raw candidate
indices/counts, accepted canonical counts, completion, and terminal reason.
