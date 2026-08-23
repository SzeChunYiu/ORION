# ORION-RG X1-N — rank-2 groups sit *exactly* on the criterion boundary, for every `n`

> **CORRECTED by X1-Q (2026-08-23).** The headline value `f_n(C_n^2) = 3n-3` of this
> document is **published, not new**: it equals `η(C_n ⊕ C_n) - 1`, and `η(C_p ⊕ C_p) =
> 3p-2` is classical (Freeze–Schmid Prop. 3.5 proof gives `s_{≤p}(C_p^2) ≤ 3p-2` and notes
> the bound is sharp at `r = 2`). `D_2(C_n ⊕ C_n) = 3n-1` is likewise published
> (Geroldinger–Halter-Koch Thm 6.1.5; Freeze–Schmid Remark 5.3(2)), for **all `n`**, so the
> composite values `n = 4, 6` are inside the published range too. `S_n` is the standard
> extremal example for `η`. The proofs
> and computations below are correct; the implied claim of discovery was not. See
> `X1Q_PRIOR_ART_CORRECTION_AND_ETA_BOUNDARY_V1.md`.

## The question this answers

X1-M left a dichotomy as a bare observation over nine groups. Writing X1-K's criterion as
`D_2 >= f_m + 2`, some groups meet it **tightly** (`D_2 = f_m + 2`) and some with slack:

| tight | slack |
|---|---|
| `C_2^2`, `C_3^2`, `C_3^3`, `C_5^2`, `C_5^3` | `C_2^3`, `C_2^4`, `C_2^5`, `C_2^6` |

This atom **explains the rank-2 half** — not by fitting the pattern, but by exhibiting the
extremal object.

## The construction

For `G = C_n ⊕ C_n` with basis `e_1, e_2`, let

```
S_n  :=  e_1^(n-1) · e_2^(n-1) · (e_1 + e_2)^(n-1)          |S_n| = 3n - 3
```

**Claim.** The minimum zero-sum length of `S_n` is `n + 1`.

*Proof.* A subsequence `a·e_1 + b·e_2 + c·(e_1+e_2)` with `0 <= a,b,c <= n-1` is zero-sum iff
`a + c ≡ 0` and `b + c ≡ 0 (mod n)`, i.e. `a ≡ b ≡ -c`. For `c = 0` this forces `a = b = 0`
(empty). For `1 <= c <= n-1` it forces `a = b = n - c`, giving length

```
2(n - c) + c  =  2n - c,
```

minimised at `c = n - 1`, where the length is `n + 1`. ∎

Since `m = D_2 - D = (3n-1) - (2n-1) = n`, the sequence `S_n` has **no zero-sum of length
`<= m`**, so it witnesses

> **`f_m(C_n^2) >= 3n - 3 = D_2(C_n^2) - 2`   for every `n`.**

That is: rank-2 groups can never do better than tight. The criterion `f_m <= D_2 - 2` holds
for them with **zero slack or not at all**.

## Exhaustive confirmation of equality

Complete search (`x1n_cn2_ftau_searcher.c`) gives the exact values:

| `n` | `f_n(C_n^2)` | `3n - 3` | |
|---|---|---|---|
| 2 | 3 | 3 | ✓ |
| 3 | 6 | 6 | ✓ |
| 4 | 9 | 9 | ✓ **composite** |
| 5 | 12 | 12 | ✓ |
| 6 | 15 | 15 | ✓ **composite** |
| 7 | **18** | 18 | ✓ **predicted before computing** |

Six values, primes and composites, all exactly `3n - 3`. Combined with the proved lower
bound, `f_n(C_n^2) = 3n - 3` on the whole tested range.

### The `n = 7` case was a genuine prediction

`f_7(C_7^2) = 18` was written down as a falsifiable prediction *before* the computation, on
the strength of the construction plus `D_2(C_n^2) = 3n - 1`. The search returned 18 — and
independently rediscovered the construction itself as the extremal object:

```
BEST 18 : (0,1)^6 (1,0)^6 (1,1)^6
f_7(C_7^2) = 18
```

which is `e_2^6 · e_1^6 · (e_1+e_2)^6`, i.e. `S_7`.

## The `D_2 = 3n - 1` side, verified independently

The consequence above needs `D_2(C_n^2) = 3n - 1`, which was originally a fit to three
points. It was re-derived with the X1-L searcher rather than assumed:

| `n` | `D_2(C_n^2)` found | `3n - 1` |
|---|---|---|
| 2 | 5 | 5 |
| 3 | 8 | 8 |
| 4 | **11** | 11 |
| 5 | 14 | 14 |

**A trap worth recording:** the `C_4^2` extremal witness is `(0,1)^7 · (1,0)^3`, using
multiplicity **7 = 2n - 1**. A search capped at the natural-looking bound `mult <= n - 1`
(the largest multiplicity that avoids creating *any* zero-sum) returns a wrong, smaller
value. The `D_2` problem forbids only *two disjoint* zero-sums, so one repeated element may
legitimately carry a zero-sum inside it. The run used `M = 2n - 1`.

Whether `D_2(C_n ⊕ C_n) = 3n - 1` is a published theorem for all `n` is under the prior-art
gate; the four values above are this programme's own.

## What this does and does not explain

**Explained.** Every rank-2 group is tight, for every `n`, prime or composite — by an
explicit extremal family, not by pattern-matching.

**Still open.** Two things, and neither should be read as covered by the above:

1. `C_3^3` and `C_5^3` are also tight (`f_m = 9, 18` against `D_2 - 2 = 9, 18`) but the
   rank-2 family does not apply and no rank-3 analogue is identified here. The two values
   fit `f_m(C_p^3) = 9(p-1)/2`, but that is a **fit to two points** and is recorded as a
   guess, not a result.
2. `C_2^r` for `r >= 3` has slack (1, 2, 2, 1 for `r = 3,4,5,6`) and is non-monotone. Note
   that "`p = 2` forces multiplicity 1" is *not* on its own the explanation, since `C_2^2`
   is tight with multiplicity 1 as well.

## Instrument validation, before use

`x1n_cn2_ftau_searcher.c` was validated against the three `f_m` values already settled in
the X1-K table before being run on any new `n`:

| case | X1-K table | searcher |
|---|---|---|
| `f_2(C_2^2)` | 3 | 3 |
| `f_3(C_3^2)` | 6 | 6 |
| `f_5(C_5^2)` | 12 | 12 |

3 of 3, and the `D_2` re-derivation reproduced the known `C_3^2 = 8` as a control in the
same run that produced the new `C_4^2 = 11`.
