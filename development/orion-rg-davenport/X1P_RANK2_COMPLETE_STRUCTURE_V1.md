# ORION-RG X1-P — the complete rank-2 extremal structure, with an exact count

## What this closes

X1-O established that at rank 2 the extremal **profile** is unique — every extremal
sequence for `f_n(C_n ⊕ C_n)` is `a^(n-1) b^(n-1) c^(n-1)` — but left the
**configuration** unresolved: 720 extremals in `C_5^2` against only 80 "basis triangles"
`{a, b, a+b}`, and explicitly *not* "any pairwise-independent triple" (which would give
1280). This atom closes that gap with a characterisation and an exact count.

## The characterisation

Let `{a, b}` be a basis of `C_n ⊕ C_n` and `c = xa + yb`. A subsequence of
`a^(n-1) b^(n-1) c^(n-1)` is `αa + βb + γc`, which vanishes iff

```
α ≡ -γx,   β ≡ -γy   (mod n)
```

so for each `γ` the shortest zero-sum using `γ` copies of `c` has length
`((-γx) mod n) + ((-γy) mod n) + γ`. Hence:

> **`a^(n-1) b^(n-1) c^(n-1)` is extremal (no zero-sum of length `<= n`)**
> **iff**  `min_{1 <= γ <= n-1} [ ((-γx) mod n) + ((-γy) mod n) + γ ]  >=  n + 1`.

This part is **proved** — it is a direct computation, given the basis representation.

## The count

Let `V(n)` be the number of `(x,y)` satisfying the condition. Computed for `n = 2..15`:

| `n` | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `V(n)` | 1 | 3 | 3 | 9 | 3 | 15 | 9 | 15 | 9 | 27 | 9 | 33 | 15 | 21 |
| `3φ(n)-3` | 0 | 3 | 3 | 9 | 3 | 15 | 9 | 15 | 9 | 27 | 9 | 33 | 15 | 21 |

> **`V(n) = 3·φ(n) - 3` for every `n >= 3`**  (and `V(2) = 1`).

Each unordered extremal triple arises from 6 ordered basis choices, so

> **`N(C_n^2) = |GL(2, Z_n)| · (φ(n) - 1) / 2`   for `n >= 3`,   `N(C_2^2) = 1`.**

## Verification against complete enumeration

| `n` | `|GL(2,Z_n)|` | predicted `N` | **enumerated** | profile |
|---|---|---|---|---|
| 2 | — | 1 | **1** | `111` |
| 3 | 48 | 24 | **24** | `222` |
| 4 | 96 | 48 | **48** | `333` |
| 5 | 480 | 720 | **720** | `444` |
| 6 | 288 | 144 | **144** | `555` |
| 7 | 2016 | **5040** | **5040** | `666` |

Six values, primes and composites, exact agreement — **and `n = 7` was a prediction made
and recorded before the enumeration was run.** Every case has a single profile, so the
X1-O profile-uniqueness finding now covers `n = 2..7` including the composites `4` and `6`.

## Proof status — stated precisely

Three separate claims, with different standing:

1. **The extremality condition on `(x,y)`** — *proved*, by direct computation above.
2. **`V(n) = 3φ(n) - 3` for `n >= 3`** — *verified for `n = 3..15`* (13 consecutive values).
   Not proved here. The valid pairs always include `(1,1), (1,-1), (-1,1)`, and every valid
   `(x,y)` observed has `x, y` coprime to `n`; a proof would presumably run through that.
3. **That every extremal has profile `(n-1, n-1, n-1)` with `{a,b}` a basis** — *verified by
   complete enumeration for `n <= 7`*, **not proved in general**. What is easy is only the
   inequality: `|S| = 3n-3` and multiplicity `<= n-1` force **at least** 3 distinct
   elements. Ruling out 4-or-more-element profiles such as `(n-1, n-1, n-2, 1)` is exactly
   what the enumeration does empirically and what a proof would need to supply.

Claims 2 and 3 are the honest gaps. The exact-count agreement at `n = 7` (5040, predicted
first) is strong evidence for both, but evidence is not proof and this document does not
promote it.

## Instruments

`x1o_extremal_profile_enumerator.c` (complete enumeration by multiplicity profile,
cross-validated against an independent Python brute force at `C_3^2`: both 24, both
`(2,2,2)`) and `x1p_rank2_triple_characterisation.py` (the `(x,y)` condition and `V(n)`).

## Still open, carried forward

1. Proofs of claims 2 and 3 above.
2. The complete `C_5^3` profile set (rank 3 is heterogeneous — X1-O).
3. Why `C_2^r`, `r >= 3`, has slack in the criterion at all.
