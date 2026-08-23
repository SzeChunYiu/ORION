# X1-B k=4 — prospective ten-prefix search for the three rank-3 forbidden-set classes

Parent: #900.
Input classes: `X1B_K4_RANK3_FORBIDDEN_GL_CLASSES_2026-08-22.md`.

## Evidence status

**PROSPECTIVE FROZEN DISCRIMINATOR.** No length-10 existence outcome for R3-10, R3-11, or R3-12 has been computed before this packet is committed.

## Exact problem

For each canonical forbidden set `S` of size 10, 11, or 12, determine whether there exists a ten-term sequence T over `F_5^3` such that every nonempty subset sum of T avoids S.

This condition is exactly equivalent to simultaneous zero-sum-freeness of the ten fixed block sums with every residual block-pair type represented by the corresponding rank-3 lift class.

## Search discipline

Because the three S span `F_5^3`, no symmetry normalization is assumed unless separately proved.

Authoritative enumeration:

1. start with represented-sum set `{0}`;
2. enumerate the ten terms as a nondecreasing multiset in one fixed ordering of the 124 nonzero group elements;
3. adding x is legal iff `(Sigma_0(T)+x)` is disjoint from S;
4. update exactly by union with the translated sumset;
5. memoization by `(sumset, depth, last canonical index)` is allowed; permutation canonicalization is the only quotient assumed;
6. complete depth 10 or return `CANNOT_CHECK_RESOURCE_BOUND`.

For every class record node count, maximum length, and an explicit witness if length 10 exists. Any NO intended for theorem use requires an independent replay or a substantially different exact verifier.

## Interpretation

- NO for a class eliminates every rank-3 completion in that GL class.
- YES yields a concrete ten-block-sum obstruction and restores the next condition: full group-algebra/factor replay (which the subset-sum condition already implies for maximal extensions) and then original 43-index realization.

The rank-2 radical family is outside this packet.