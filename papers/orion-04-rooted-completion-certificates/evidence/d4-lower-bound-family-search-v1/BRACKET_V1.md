# ORION-04: an unconditional bracket `28 <= D_4(C_5^3) <= 52`

Companion to `FINDING_V1.md`. Derived, not searched; both endpoints verified.

## Upper bound: `D_k(G) <= k * D(G)`

**Claim.** For any finite abelian `G` and `k >= 1`, `D_k(G) <= k * D(G)`.

**Proof.** Let `|S| = k * D(G)`. Take a *maximal* family of pairwise-disjoint
minimal nontrivial zero-sum subsequences of `S`, of size `j`. Suppose
`j <= k - 1`. By maximality the remainder `R` (what is left after removing the
family) is zero-sum-free, so `|R| <= D(G) - 1`. Each removed subsequence is a
minimal zero-sum sequence, so has length `<= D(G)`. Hence

```
|S| <= (k-1) * D(G) + D(G) - 1 = k * D(G) - 1 < k * D(G),
```

contradicting `|S| = k * D(G)`. So `j >= k`, i.e. every sequence of length
`k D(G)` has `k` disjoint nontrivial zero-sum subsequences, giving
`D_k(G) <= k D(G)`. []

Two ingredients only: `D(G)` bounds the length of a minimal zero-sum sequence,
and maximality forces the remainder zero-sum-free. Both are definitional.

**Validation.** Checked against every value the rank-<=2 formulas give:

| G | D(G) | k=1..5 | `k D(G)` | holds |
|---|---|---|---|---|
| `C_5` | 5 | 5,10,15,20,25 | 5,10,15,20,25 | yes, with **equality** |
| `C_5+C_5` | 9 | 9,14,19,24,29 | 9,18,27,36,45 | yes |

The bound is **tight for cyclic groups** — `D_k(C_n) = kn = k D(C_n)` exactly —
so it is not a vacuous over-estimate. It is loose at rank 2 and gets looser as
rank grows, which is the honest characterisation of what it gives at rank 3.

## Lower bound: `D_4(C_5^3) >= 28`

Witness `e1^9 e2^9 e3^9`, length 27, packing exactly 3 (recomputed here: 3).
Its companion `e1^4 e2^4 e3^4` is zero-sum-free (packing 0), confirming
`D(C_5^3) = 13` in the same run.

## The bracket, and what it does not do

```
28 <= D_4(C_5^3) <= 52
```

Both endpoints are verified: the lower by explicit witness, the upper by the
proof above with its premises re-checked computationally.

**It does not settle the target.** `N-C11` (`=30`) and `N-C12` (`=31`) both sit
strictly inside the bracket, so this adjudicates nothing between them and gives
no support to either. Its value is that the open question previously had no
stated unconditional upper bound at all; it now has one, with a proof short
enough to check by eye.

Closing the gap from above requires the rank-3 structure `k D(G)` discards
entirely — it uses only that minimal zero-sums are short, never that `C_5^3` has
rank 3. That is exactly where the remaining work is.

`scientific_authority_delta: NONE`.

**Terminal:** `UNCONDITIONAL_BRACKET_28_52__DOES_NOT_ADJUDICATE_30_VS_31`
