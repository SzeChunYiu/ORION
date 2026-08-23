# ORION-RG X1-M — the extremal `D_2` decomposition criterion is an *iff*, and the sole counterexample is forced

## What X1-K left open

X1-K established a **sufficient** criterion:

> if `f_m(G) <= D_2(G) - 2` then every extremal `D_2` witness has minimum zero-sum length
> exactly `m`, and splits `S = A · B` with `A` a minimal zero-sum of length `m` and `B` a
> maximal zero-sum-free sequence of length `d(G) = D - 1`.

It predicted the direct test correctly on 8 of 8 groups, including the one negative
(`C_2^4`). But it was recorded honestly as *sufficient, not necessary a priori* — the
`C_2^4` failure was an **observation**, not an explanation. This atom closes that gap.

## Notation

`G` finite abelian, `D = D(G)`, `d(G) = D - 1`, `D_2 = D_2(G)`, `m := D_2 - D`.
`f_m(G)` = max length of a sequence with no nonempty zero-sum subsequence of length `<= m`.
An **extremal `D_2` witness** is a sequence of length `D_2 - 1` with no two disjoint
nonempty zero-sum subsequences.

## Theorem X1-M (converse, in a regime)

> **If `m >= D - 2` and `f_m(G) >= D_2(G) - 1`, then the decomposition FAILS** — there
> exists an extremal `D_2` witness whose minimum zero-sum length is `> m`, so it admits no
> factorisation `A · B` with `A` a zero-sum of length `m`.

*Proof.* Take `T` of length `f_m(G)` with no zero-sum of length `<= m`, and truncate it to
`S` of length `D_2 - 1` (possible because `f_m >= D_2 - 1`). Truncation preserves the
property, so every nonempty zero-sum subsequence of `S` has length `>= m + 1`.

Suppose `S` contained two disjoint nonempty zero-sums `A`, `B`. Then

```
|S| >= |A| + |B| >= 2m + 2,     and     |S| = D_2 - 1 = D + m - 1,
```

so `D + m - 1 >= 2m + 2`, i.e. `m <= D - 3` — contradicting `m >= D - 2`.

Hence `S` has no two disjoint zero-sums: `S` **is** an extremal `D_2` witness, and its
minimum zero-sum length is `>= m + 1 > m`. ∎

## Corollary — the criterion is an iff whenever `m >= D - 2`

Combining with X1-K (which supplies `<=`):

> **For every `G` with `m >= D - 2`: the extremal `D_2` decomposition holds
> if and only if `f_m(G) <= D_2(G) - 2`.**

This converts five rows of the X1-K table from *observations that matched a prediction*
into *theorems*.

## The `C_2^4` counterexample is forced — and completely accounted for

For `C_2^4`: `D = 5`, `D_2 = 8`, `m = 3`, `D - 2 = 3`, so `m >= D - 2` holds, and
`f_3(C_2^4) = 8 >= D_2 - 1 = 7`. The theorem fires: the decomposition **must** fail.

The proof is constructive, and its construction turns out to produce *exactly* the observed
anomalies. In `F_2^4`, a sequence with no zero-sum of length `<= 3` is a set of distinct
nonzero vectors with no three summing to zero. The affine hyperplanes

```
H_phi = { v in F_2^4 : phi(v) = 1 },    phi a nonzero functional
```

each have size 8 and satisfy this (any `k` of them sum to a vector of last coordinate
`k mod 2`, so `k = 3` cannot give `0`), realising `f_3 = 8`. Truncating to 7 gives an
extremal witness whose zero-sums all have even length, hence minimum zero-sum `4 > m = 3`.

Counting: **15 functionals × 8 ways to delete one element = 120.**

Verified computationally by complete enumeration (`x1m_verify.py`):

```
C_2^4 witnesses: 3480   min-ZS histogram: {3: 3360, 4: 120}
converse construction yields: 120 distinct 7-sets
observed anomalous witnesses (min ZS > m): 120
construction == anomalous set: True
f_3(C_2^4) = 8    D_2-1 = 7    D_2-2 = 6
```

The last line is the point: the construction does not merely match the *count* 120, it
matches the *set*. Every witness that violates the X1-K decomposition is a punctured
affine hyperplane, and nothing else is.

## The regime condition is real, and it bites exactly at `C_2^6`

| group | `D` | `D_2` | `m` | `D-2` | `m >= D-2` | `f_m` | `D_2-2` | status |
|-------|-----|-------|-----|-------|------------|-------|---------|--------|
| `C_2^2` | 3 | 5 | 2 | 1 | ✓ | 3 | 3 | **iff** → holds |
| `C_2^3` | 4 | 7 | 3 | 2 | ✓ | 4 | 5 | **iff** → holds |
| `C_2^4` | 5 | 8 | 3 | 3 | ✓ | **8** | 6 | **iff** → **fails, forced** |
| `C_2^5` | 6 | 10 | 4 | 4 | ✓ | 6 | 8 | **iff** → holds |
| `C_3^2` | 5 | 8 | 3 | 3 | ✓ | 6 | 6 | **iff** → holds |
| `C_3^3` | 7 | 11 | 4 | 5 | ✗ | 9 | 9 | criterion only → holds |
| `C_5^2` | 9 | 14 | 5 | 7 | ✗ | 12 | 12 | criterion only → holds |
| `C_5^3` | 13 | 20 | 7 | 11 | ✗ | 18 | 18 | criterion only → holds |
| `C_2^6` | 7 | 11 | 4 | 5 | ✗ | **8** | 9 | criterion only → **holds** (resolved below) |

For elementary 2-groups, `m >= D - 2` holds for `r = 2,3,4,5` and **fails first at
`r = 6`** (`m = 4`, `D - 2 = 5`). So `C_2^6` is the first elementary 2-group where the iff
does not apply and the criterion is genuinely one-directional. That makes `f_4(C_2^6)` the
informative next number rather than an arbitrary one:

- `f_4(C_2^6) <= 9` → criterion fires → decomposition holds (sufficiency needs no regime).
- `f_4(C_2^6) >= 10` → criterion silent **and** converse silent → undecided by theory,
  needs direct witness enumeration.

### Resolved: `f_4(C_2^6) = 8`

Computed by complete backtracking search (`fast.c`, 4.0 s):

```
BEST 8 : 1 2 4 8 15 16 32 51
f_4(C_2^6) = 8
```

`8 <= D_2 - 2 = 9`, so the **criterion fires** and the decomposition **holds** for `C_2^6`.
Note this is a *theorem-derived* conclusion — X1-K's criterion is proved, and its
sufficiency carries no regime condition — not a direct enumeration of the `C_2^6`
witnesses, which was not run.

So the first elementary 2-group outside the iff regime still decomposes, and it does so
with slack 1 rather than tightly.

### A dichotomy the ninth row sharpens

Writing the criterion as `D_2 >= f_m + 2`, ask when it is **tight** (`D_2 = f_m + 2`):

| tight (`D_2 = f_m + 2`) | slack (`D_2 > f_m + 2`) |
|---|---|
| `C_2^2`, `C_3^2`, `C_3^3`, `C_5^2`, `C_5^3` | `C_2^3`, `C_2^4`, `C_2^5`, `C_2^6` |

Every odd-`p` group tested is tight; every elementary 2-group of rank `>= 3` has slack.
On the present evidence this is an **observation over nine groups, not a theorem** — the
odd-`p` side rests on four groups (`C_3^2`, `C_3^3`, `C_5^2`, `C_5^3`). The obvious test is
`C_7^2`: the rank-2 values `5, 8, 14` for `n = 2, 3, 5` fit `D_2(C_n^2) = 3n - 1`, which
would give `D_2(C_7^2) = 20`, `m = 7`, and so predict `f_7(C_7^2) = 18` under tightness.
That prediction is recorded here as falsifiable and **not yet tested**.

## Instrument validation, before use

`f4_c26.c` (backtracking max-length search over `F_2^r \ {0}`) was validated against the
four elementary-2-group values already settled in X1-K **before** being run on `C_2^6`:

| case | X1-K table | `f4c2r` |
|---|---|---|
| `f_2(C_2^2)` | 3 | 3 |
| `f_3(C_2^3)` | 4 | 4 |
| `f_3(C_2^4)` | 8 | 8 |
| `f_4(C_2^5)` | 6 | 6 |

4 of 4. The first build of this searcher returned `f_2(C_2^2) = 2`, a wrong value caused by
an off-by-one in the pruning bound (`N - start` excludes the candidate `v = start` itself;
correct is `N - start + 1`). It was caught by this validation table and fixed before any
new value was computed — the wrong build's numbers are not used anywhere.

## Status of the novelty claim

The mathematics above is verified independently of the literature. Whether Theorem X1-M or
the X1-K criterion is **new** is a separate question, currently under a prior-art gate
(inverse problems for `D_k`, Zhong 2025 rank-2, Freeze–Schmid, Gao–Geroldinger survey).
This programme has taken **seven prior-art hits**; no novelty claim is made here until that
gate reports. The theorem, the proof, and the `C_2^4` characterisation stand regardless.
