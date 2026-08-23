# X1-B exploratory finding — no 14-point no-short residual survives packing number <3

Parent: #900.
Context: correction packet `X1B_C15_GREEDY_RESIDUAL_TREE_HOSTILE_AUDIT_2026-08-22.md`.

## Evidence status

**EXPLORATORY — outcome seen before a confirmatory protocol was frozen.** This packet records the derivation honestly and must not be used as theorem evidence until independently replayed.

## Exact quotient question

A missing branch of the C15 greedy reduction can leave 14 projected positions after ten previously removed short quotient-zero-sum blocks. Because the greedy process is terminal, the 14-position residual R has **no nonempty quotient zero sum of length at most 3**.

To avoid the ordinary 13-block contradiction, R would also need to fail to contain three pairwise-disjoint nonempty quotient zero sums.

Thus ask whether any 14-position multiset over `F_3^3` satisfies simultaneously:

1. no quotient zero sum of length <=3;
2. packing number below 3.

## Structural finite reduction

The no-short condition implies:

- zero is absent;
- every multiplicity is at most 2;
- the distinct support has no opposite pair and no three distinct points summing to zero;
- by the exact 9-point support-cap audit, support size is at most 8;
- length 14 and multiplicity <=2 imply support size at least 7.

Therefore only support sizes 7 and 8 are possible.

An exploratory exact support enumeration under elementary generators of `GL(3,3)` found:

- raw admissible 7-supports: `18,720`, forming **4** linear orbits;
- raw admissible 8-supports: `702`, forming **1** linear orbit.

For support size 7, length 14 forces every support point to occur twice. Primitive position-subset replay on all four orbit representatives finds three disjoint quotient zero sums in every case.

For support size 8, length 14 means exactly six support points are doubled and two are single. Testing **all 28 choices** of the two single positions on the unique support orbit finds three disjoint quotient zero sums in every case.

Exploratory outcome:

> **No 14-position no-short residual with packing number below 3 exists.**

## Relation to donor `D_3(C_3^3)=15`

This does not contradict the donor lower bound. `D_3(C_3^3)=15` asserts existence of some 14-position multiset without three disjoint zero sums; it does **not** require that extremal to be free of all zero sums of length <=3.

The C15 terminal residual has the extra no-short condition created by the greedy extraction, and that extra condition appears to eliminate the entire 14-point layer.

## Required confirmation

Before using this result to repair the full C15 residual tree, independently enumerate all raw support/multiplicity cases without `GL(3,3)` orbit reduction and replay the packing condition from primitive position sums.

## Authority boundary

No 14-point branch closure, k=4 theorem expansion, C15 theorem, or novelty authority follows from this exploratory packet alone.