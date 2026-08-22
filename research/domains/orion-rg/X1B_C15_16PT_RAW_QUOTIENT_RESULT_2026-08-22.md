# X1-B — raw quotient verification closes the C15 16-point terminal residual

Parent: #900.
Protocol: `X1B_C15_16PT_RAW_QUOTIENT_PROTOCOL.md`.
Verifier: `x1b_c15_16pt_raw_quotient_verify.cpp`.

## Exact result

The verifier enumerates every raw 8-element support in `F_3^3\{0}` satisfying:

- no opposite pair;
- no three distinct support points summing to zero.

Because a 16-position terminal residual has multiplicity at most 2 and support size at most 8, each admissible support produces the unique candidate in which all eight support points are doubled.

Fresh exact census:

```text
supports8 702
candidates 702
packed4 702
failures 0
min_zero4_masks 96
max_zero4_masks 96
```

Thus:

- raw admissible 8-supports: **702**;
- total 16-position candidates: **702**;
- candidates admitting four pairwise-disjoint zero-sum blocks: **702**;
- failures: **0**.

Every candidate has exactly **96** zero-sum position subsets of size 4.

## Why checking 4-subsets is complete

The terminal greedy residual has no quotient zero sum of size <=3. If four pairwise-disjoint nonempty zero-sum subsequences exist in 16 positions, replace each by a minimal zero-sum subsequence. Every minimal zero-sum in `C_3^3` has length at most `D(C_3^3)=7`, but the four disjoint nonempty blocks together occupy at most 16 positions and each has length at least 4. Therefore all four must have length exactly 4 and partition the full 16 positions.

The verifier searches exactly for such four-block partitions.

## Consequence

In the m=9 branch of the corrected C15 residual tree, the nine previously removed quotient-zero-sum blocks plus the four residual blocks give 13 pairwise-disjoint quotient-zero-sum blocks. Their lifted sums in `C_5^3` force an upstairs zero sum because `D(C_5^3)=13`.

Hence the 16-point terminal residual branch is impossible, without relying on the old donor extremal diagram or inverse classification.

## Authority boundary

This closes one quotient branch of the candidate C15 proof. Full theorem promotion still requires end-to-end assembly and hostile review.