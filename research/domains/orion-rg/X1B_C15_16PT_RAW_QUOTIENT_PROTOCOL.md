# X1-B — prospective raw quotient verification for the C15 16-point terminal residual

Parent: #900.

## Evidence status

**PROSPECTIVE RAW VERIFICATION.** No complete raw four-packing census described below has been computed before this protocol is committed.

## Candidate universe

In the corrected greedy residual tree, the m=9 branch leaves exactly 16 quotient positions and the greedy terminal residual has no nonempty zero sum of length <=3.

Consequences:

- zero is absent from support;
- each nonzero support element has multiplicity at most 2;
- no opposite support pair;
- no three distinct support elements sum to zero;
- the independently audited support cap is at most 8;
- length 16 with multiplicity at most 2 therefore forces support size exactly 8 and every support element to occur exactly twice.

Thus a complete raw enumeration need only list every admissible 8-element support in `F_3^3\{0}` and double every element.

## Primitive four-packing test

For each 16-position multiset:

1. enumerate all nonempty position subsets of sizes 4 through 7;
2. retain those whose primitive coordinate sum is zero mod 3;
3. determine whether four pairwise-disjoint retained zero-sum subsets exist.

Sizes 4 through 7 suffice because the terminal residual has no zero sum of length <=3 and every nonempty zero-sum sequence contains a minimal zero-sum subsequence of length at most `D(C_3^3)=7`.

## Required output

- raw admissible 8-support count;
- total 16-position candidates;
- count having four disjoint quotient zero sums;
- count failing four-packing;
- explicit failure if one exists.

No `GL(3,3)` orbit quotient or donor extremal diagram is used.

## Interpretation

If every candidate has four disjoint quotient zero sums, then together with the nine already removed quotient blocks the m=9 branch yields 13 quotient blocks and closes by `D(C_5^3)=13`.

## Authority boundary

This is a finite quotient-side verification only. It does not by itself prove `D(C_15^3)=43`.