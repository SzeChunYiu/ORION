# X1-B k=3 — support-size completeness audit for the raw replay

Parent: #900.
Independent raw verifier: `x1b_k3_raw_no_symmetry_replay.cpp`.
Committed before k=3 closure.

## Question

The raw replay enumerates support sizes 5 through 8 for a 10-position multiset with multiplicity at most 2. To ensure completeness, test whether a 9-element subset of

`F_3^3 \ {0}`

can satisfy the frozen support conditions:

1. no opposite pair `{x,-x}` (which would be a length-2 zero sum);
2. no three distinct support elements with sum zero.

If such a 9-set existed, a length-10 multiset with one doubled support point could lie outside the raw replay.

## Exact audit

A direct lexicographic backtracking enumeration over the 26 nonzero vectors was performed. At each extension x, reject x iff:

- `-x` is already selected; or
- some selected pair `a,b` satisfies `a+b+x=0`.

The search exhausts all candidate 9-subsets without symmetry reduction.

Result:

> **No admissible 9-element support exists.**

Thus every support satisfying the short-zero-sum gate has size at most 8.

For a 10-term multiset with multiplicity at most 2, support size is at least 5, so the raw verifier's range `5,6,7,8` is exhaustive.

## Consequence

The independently committed raw k=3 replay covers every 10-position multiset satisfying the frozen short-zero-sum conditions. No support-size case is omitted.

## Authority boundary

This is a finite completeness audit for the raw verifier, not a standalone C15 theorem or novelty claim.