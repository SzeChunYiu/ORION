# X1-B — prospective raw confirmation protocol for the missing 14-point residual

Parent: #900.
Exploratory finding: `X1B_C15_14PT_NO_SHORT_EXPLORATORY_CLASSIFICATION_2026-08-22.md`.

## Evidence status

**PROSPECTIVE INDEPENDENT CONFIRMATION.** The exploratory outcome is known, but the raw algorithm below and its exact census are frozen before execution.

## Frozen candidate universe

Enumerate directly over the 26 nonzero elements of `F_3^3`, with no linear-equivalence quotient.

A 14-position terminal greedy residual has no zero sum of length <=3. Therefore:

- multiplicity of every support element is at most 2;
- no opposite support pair is allowed;
- no three distinct support elements may sum to zero;
- support size is at least 7 and, by the independently audited support cap, at most 8.

Thus enumerate exactly:

1. every raw admissible 7-element support, with every point doubled;
2. every raw admissible 8-element support, with every choice of exactly six doubled points and two single points.

No `GL(3,3)` canonicalization, orbit representative, or stabilizer reduction is allowed.

## Primitive packing replay

For each resulting 14-position multiset:

1. enumerate position subsets of sizes 4 through 7;
2. retain those summing to zero by primitive coordinate addition mod 3;
3. search for three pairwise-disjoint retained zero-sum subsets.

Why sizes 4 through 7 suffice:

- the terminal residual has no zero sum of size <=3;
- every nonempty zero-sum sequence contains a minimal zero-sum subsequence;
- `D(C_3^3)=7`, so every minimal zero-sum subsequence has length at most 7;
- therefore, if three disjoint zero-sum subsequences exist, three disjoint zero-sum subsequences of sizes in `[4,7]` exist.

## Required output

- raw admissible 7-support count;
- raw admissible 8-support count;
- total 14-position multiplicity candidates;
- number containing three disjoint zero sums;
- number failing three-disjoint packing;
- explicit witness if any candidate fails.

## Interpretation

- zero failures independently closes the 14-point terminal residual;
- any failure is a genuine new quotient obstruction and must be serialized before any kernel-lift analysis.

## Authority boundary

This is a finite quotient-side confirmation. It does not by itself prove `D(C_15^3)=43`; it repairs one exhaustiveness gap in the end-to-end reduction.