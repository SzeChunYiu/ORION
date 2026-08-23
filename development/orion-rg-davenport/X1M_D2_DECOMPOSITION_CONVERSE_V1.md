# ORION-RG X1-M — the extremal `D_2` decomposition criterion is an *iff*, and the sole counterexample is forced

> **PARTIALLY CORRECTED by the prior-art gate (2026-08-23), hit #13.** The 120-element
> family below — punctured affine hyperplanes of `F_2^4` — is **published**, as the `r = 4`,
> length-7 shadow of Davydov–Tombak's 1989 classification of large sum-free sets, restated
> as **Freeze–Schmid Theorem 7.2**. It is a known object in the *cap / coding* literature,
> not a new construction, and a referee in this area will recognise it on sight.
> **What is not published:** the total 3480, the `3360 / 120` split, and the identification
> of the 120 as the minimum-zero-sum-4 stratum of the `D_2` witness set. The defensible
> content here is the `D_2` framing and the 3360 — **not** the punctured hyperplanes.

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

## Why there is exactly *one* negative — `C_2^4` is the unique firing

> **SUPERSEDED IN PART by X1-U (2026-08-23).** The claims below were scoped to the 12
> groups with settled numbers at the time. X1-U settles `C_2^7` (`D_2 = 12`,
> `f_4 = 11 > D_2 − 2 = 10`) and it is the **second** group where the decomposition fails
> (21,840 basis-containing min-ZS-5 witnesses; explicit verified example) — the first with
> the criterion violated **outside** the regime `m ≥ D − 2`, i.e. the first genuinely
> "undecided by theory" row, and it resolves to FAIL. The theorem (the iff inside the
> regime) is untouched; the completeness observation and the uniqueness framing below are
> what this supersedes.

The converse needs **both** `m >= D - 2` (regime) and `f_m >= D_2 - 1` (criterion violated).
Across every group with settled numbers, only one satisfies both:

| group | `D` | `D_2` | `m` | `D-2` | `f_m` | `D_2-1` | regime | crit. violated | outcome |
|---|---|---|---|---|---|---|---|---|---|
| `C_2^2` | 3 | 5 | 2 | 1 | 3 | 4 | ✓ | ✗ | holds |
| `C_2^3` | 4 | 7 | 3 | 2 | 4 | 6 | ✓ | ✗ | holds |
| `C_2^4` | 5 | 8 | 3 | 3 | **8** | 7 | ✓ | **✓** | **FAILS (forced)** |
| `C_2^5` | 6 | 10 | 4 | 4 | 6 | 9 | ✓ | ✗ | holds |
| `C_2^6` | 7 | 11 | 4 | 5 | 8 | 10 | ✗ | ✗ | holds |
| `C_3^2` | 5 | 8 | 3 | 3 | 6 | 7 | ✓ | ✗ | holds |
| `C_3^3` | 7 | 11 | 4 | 5 | 9 | 10 | ✗ | ✗ | holds |
| `C_4^2` | 7 | 11 | 4 | 5 | 9 | 10 | ✗ | ✗ | holds |
| `C_5^2` | 9 | 14 | 5 | 7 | 12 | 13 | ✗ | ✗ | holds |
| `C_6^2` | 11 | 17 | 6 | 9 | 15 | 16 | ✗ | ✗ | holds |
| `C_5^3` | 13 | 20 | 7 | 11 | 18 | 19 | ✗ | ✗ | holds |
| `C_7^2` | 13 | 20 | 7 | 11 | 18 | 19 | ✗ | ✗ | holds |

Two things worth reading off this table.

**1. Criterion plus converse decide every case.** No row is *undecided* — there is no group
here with the criterion violated but outside the regime, which is the one combination the
theory does not settle. So on the tested range the pair is not merely sound but complete.

**2. The failure mechanism is confined to small groups.** For elementary 2-groups
`D = r + 1`, and the published asymptotic band is `1.26r <= D_2(C_2^r) <= 1.40r`, so
`m = D_2 - D` lies in roughly `[0.26r - 1, 0.40r - 1]` while `D - 2 = r - 1`. The regime
`m >= D - 2` would need `0.40r - 1 >= r - 1`, i.e. `0.40r >= r` — false. So **for all large
`r` the regime fails and the converse cannot fire.** (That band is asymptotic and says
nothing at `r = 4`, where the exact values `D_2 = 8`, `m = 3 = D - 2` put the group on the
regime boundary; the argument is about large `r` only.)

Together: `C_2^4` is not merely the one negative observed, it sits at the only place a
negative of this kind can occur — on the regime boundary, at a rank small enough for `m` to
still reach `D - 2`, and with `f_3 = 2^3 = 8` inflated by the affine-hyperplane construction
just past `D_2 - 1 = 7`.

## Prior-art status of the `C_2^4` family (hit #13)

**The classification is published; the `D_2` identification is not.**

Freeze–Schmid, Discrete Math. 310 (2010), Lemma 7.1 gives the bridge from zero-sums to
caps, and Theorem 7.2 (a restatement of Davydov & Tombak, *Problemy Peredachi Informatsii*
25(4), 1989, via Grynkiewicz–Lev, SIAM J. Discrete Math. 24 (2010)) classifies the large
sum-free sets:

> "Theorem 7.2. Let `r ∈ N`. Let `S` be a squarefree sequence over `C_2^r` with `0 ∤ S` and
> `|S| ≥ 9(2^{r−5})`. Then the following statements are equivalent
> • `S` has no non-empty zero-sum subsequence of length 3.
> • `supp(S)` is contained in the non-zero coset of a subgroup of index 2 or `supp(S)` is
> contained in `{e_1, e_2, e_3, e_4, (e_1+e_2+e_3+e_4)} + G'` where `G'` is a subgroup of
> index 16 and `C_2^r = ⟨e_1,…,e_4⟩ ⊕ G'`."

At `r = 4`: the threshold is `9·2^{-1} = 4.5 ≤ 7`, so it applies; the second alternative
needs an index-16 subgroup of a group of order 16, i.e. the trivial one, giving a 5-element
set — excluded since `|supp(S)| = 7`. So `supp(S)` lies in the non-zero coset of an
index-2 subgroup, an 8-element affine hyperplane, and `|supp(S)| = 7` forces exactly one
deletion: `15 × 8 = 120`.

**Terminology, easy to get wrong:** the 8-element affine hyperplane is the *complete*
(maximal, non-extendable) cap of `PG(3,2)`. The 120 objects are that **minus one point**, so
they are *not* complete caps — they extend by replacing the deleted point. Correct
description: **a maximum cap of `PG(3,2)` with one point deleted.**

### What the `D_2` framing adds

The step connecting the cap classification to `D_2` is not in that literature: minimum
zero-sum length 4 means two disjoint zero-sums would need `≥ 8` terms against `|S| = 7`, so
every min-zs-4 sequence is *automatically* a `D_2`-extremal witness. Hence the 120 are
simultaneously the `s_{≤3}`-extremal objects and the anomalous stratum of the `D_2` witness
set. That bridge — and the 3360 — is what is unclassified.

## A gap this exposed: squarefreeness was assumed, not argued

The enumeration above ranged over `combinations(V, 7)`, i.e. **distinct** elements only. That
restriction was never justified in this document. It is in fact forced, and the argument is
one line: a repeat `g·g` is a zero-sum of length 2, so the remaining 5 terms must be
zero-sum-free; but `d(C_2^4) = D − 1 = 4`, so any 5 terms contain a zero-sum, giving two
disjoint zero-sums. Hence no witness has a repeat.

Independently confirmed by an enumeration that *did* allow repeats: 3480 witnesses, of which
**0** contain a repeated element.

This is also published in general form — Freeze–Schmid Proposition 7.5.2:

> "2. If `B` is a sequence over `C_2^r` with `max L(B) ≤ k_D(C_2^r)` and
> `|B| = D_{k_D(C_2^r)}(C_2^r)`, then `B` is squarefree and `0 ∤ B`."

The result was right; the write-up had a hole where a justification should have been.

## Why Property B / Property C say nothing here

Worth recording so this is not re-attempted: for `C_2^r`, `exp(G) = 2`, so a "short zero-sum"
has length `≤ 2` and a short-zero-sum-free sequence is just a squarefree sequence missing 0 —
whence `η(C_2^r) = 2^r`, with the product of all non-zero elements the unique extremal. Property
C's conclusion `S = T^{exp−1} = T` is then vacuous. The machinery is **degenerate** on
elementary 2-groups, not merely unapplied.

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
