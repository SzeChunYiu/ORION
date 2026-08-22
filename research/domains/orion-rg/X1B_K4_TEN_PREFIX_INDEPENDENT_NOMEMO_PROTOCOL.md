# X1-B k=4 — independent no-memo multiset confirmation protocol

Parent: #900.
Primary result: exact DFS+memo NO for length 10.
BFS attempt: resource-bounded/inconclusive and grants no confirmation authority.

## Independence target

This verifier is designed to falsify bugs in the primary memo/state quotient.

It must:
- use **no memoization or hash-based dead-state pruning**;
- enumerate the remaining nine terms directly as a nondecreasing multiset;
- use a different fixed canonical element order from the primary implementation;
- recompute each extension's translated represented-sum set exactly;
- retain the same mathematically justified normalization of one off-plane term to e3.

## Algorithm

Start with distinguished `e3=(0,0,1)`.

Order the 124 nonzero elements with all plane elements first, followed by off-plane elements in reverse z/coordinate order (different from the primary off-plane-first order).

Recursively choose the remaining nine terms with nondecreasing order indices. At every extension:

`Sigma_0(Tx)=Sigma_0(T) union (Sigma_0(T)+x)`

and reject iff the translated part meets the frozen seven-point forbidden set.

No state deduplication is permitted. Thus every canonical multiset path is visited explicitly.

Required outputs:
- exhaustive completion / resource bound;
- raw canonical-multiset node count;
- maximum depth;
- whether any length-10 witness exists;
- explicit length-9 witness if maximum is 9.

Strong confirmation requires complete traversal and no length-10 witness. Resource exhaustion is `CANNOT_CHECK_RESOURCE_BOUND`.