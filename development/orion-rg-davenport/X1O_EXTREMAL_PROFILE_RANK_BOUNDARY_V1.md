# ORION-RG X1-O — the extremal shape is unique at rank 2 and **not** at rank 3

## What was being tested

X1-N proved that rank-2 groups sit exactly on the criterion boundary via the explicit
family `S_n = e_1^(n-1) e_2^(n-1) (e_1+e_2)^(n-1)`, and left two things open. The first was
whether a rank-3 analogue exists — `C_3^3` and `C_5^3` are also tight (`f_m = 9, 18`) and
the two values fit `f_m(C_p^3) = 9(p-1)/2`, which was recorded as a **guess from two
points**, not a result.

That fit suggested a structural reading: an extremal of `3` elements at multiplicity
`(p-1)/2` and `3` at multiplicity `p-1`, since `3·(p-1)/2 + 3·(p-1) = 9(p-1)/2`. This atom
tests that hypothesis by **complete enumeration of the extremal set**, and reports what
survived.

## Method

`x1o_extremal_profile_enumerator.c` enumerates *every* length-`L` sequence over `C_p^r`
with no zero-sum of length `<= T`, and histograms them by **multiplicity profile** (the
sorted multiset of multiplicities). Profile is the right invariant here: it is what a
"construction" of the `g_1^{a_1} ··· g_k^{a_k}` form fixes, and it is invariant under the
`GL(r,p)` action.

**Validation.** The enumerator's `C_3^2` output was cross-checked against an independent
brute-force Python enumeration:

| | total extremals | profiles |
|---|---|---|
| C enumerator | 24 | `{(2,2,2): 24}` |
| Python brute force | 24 | `{(2,2,2): 24}` |

Agreement on both the count and the profile histogram.

## Result 1 — at rank 2 the profile is **unique**

| group | `T` | `L` | total extremals | distinct profiles | profile |
|---|---|---|---|---|---|
| `C_3^2` | 3 | 6 | 24 | **1** | `(2,2,2)` |
| `C_5^2` | 5 | 12 | 720 | **1** | `(4,4,4)` |

Every single extremal sequence is `g_1^(p-1) g_2^(p-1) g_3^(p-1)` — three elements, each at
full multiplicity `p-1`. This is a considerably stronger statement than X1-N: `S_n` is not
merely *an* extremal object, its **shape is the only shape**.

### But the *configuration* is not unique — only the profile is

This distinction matters and is easy to get wrong. There are only `480/6 = 80` unordered
triples of the "basis triangle" form `{a, b, a+b}` in `C_5^2`, against **720** extremals.
So the extremal set is `9×` larger than the `S_n` family, and other linear configurations
qualify — verified directly:

```
{a,b,a+b}      len=12  min zero-sum=6  extremal(>5)=True
{a,b,2a+b}     len=12  min zero-sum=6  extremal(>5)=True
{a,b,3a+b}     len=12  min zero-sum=6  extremal(>5)=True
{a,b,2a+3b}    len=12  min zero-sum=6  extremal(>5)=True
```

The exact characterisation of which triples `{a,b,c}` are extremal is **open**; note it is
not simply "pairwise independent", since that would give `20 · 4^3 = 1280 > 720`.

## Result 2 — at rank 3 the profile is **not** unique, and the hypothesis fails

| group | `T` | `L` | total extremals | distinct profiles |
|---|---|---|---|---|
| `C_3^3` | 4 | 9 | 20,124 | **2** |

```
profile 111222   count 13104
profile 12222    count  7020
```

The hypothesised profile — `3` at multiplicity `(p-1)/2 = 1` and `3` at multiplicity
`p-1 = 2`, i.e. `111222` — **is** the dominant one, carrying 65% of the extremals. So the
guess was not empty. But it is **not the only** profile: `12222` accounts for the other
7,020, and no `g_1^{a_1} ··· g_k^{a_k}` construction with a fixed profile can generate the
extremal set.

**The hypothesis is therefore falsified as stated.** There is no single rank-3 analogue of
`S_n`, and `f_m(C_p^3) = 9(p-1)/2` — still a two-point fit — has no single-construction
explanation.

Corroborating, at `C_5^3` the length-18 extremal recovered by the X1-F0 searcher has
profile `1112444`:

```
[1,0,0]·1 [0,1,0]·1 [0,0,1]·1 [0,1,4]·2 [1,0,4]·4 [1,4,1]·4 [4,1,0]·4 [4,2,0]·1
```

a **third** shape, neither `222444` (what the hypothesis would predict at `p=5`) nor either
`C_3^3` profile. That run was `complete_search: false`, so this establishes only that the
shape `1112444` occurs — **not** the full `C_5^3` profile set, which was not enumerated.

## What this settles

The clean "one extremal shape" story is a **rank-2 phenomenon, and it stops at rank 3**.
That boundary is now established by complete enumeration rather than asserted, and it
explains why X1-N found a construction for rank 2 and none for rank 3: at rank 3 the
extremal set is genuinely heterogeneous, so no such construction exists to be found.

The `9(p-1)/2` fit is left standing as a **fit**, explicitly not upgraded.

## Open, and not covered above

1. Exact characterisation of the extremal triples `{a,b,c}` at rank 2 (720 of 1280 in
   `C_5^2`).
2. Whether rank-2 profile uniqueness holds for **all** `n` — verified here only for
   `p = 3, 5`. Composite `n` was not enumerated by profile.
3. The complete `C_5^3` profile set.
4. Why `C_2^r`, `r >= 3`, has slack at all (carried over from X1-N, untouched here).
