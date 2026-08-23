# ORION-RG X1-Q — the rank-2 line is published: four corrections

This atom retracts the novelty claims of X1-N, X1-O (rank-2 part), and X1-P. **The rank-2
`η` line is comprehensively published.** The proofs and computations in those atoms are
correct and were independently validated; what was wrong was the implied claim that any of
it was new. Four separate prior-art hits, taking this programme's total to **eleven**.

## Correction 1 — `D_2(C_n ⊕ C_n) = 3n - 1` is published (hit #8)

A special case of the rank-2 formula `D_k(C_{n_1} ⊕ C_{n_2}) = n_1 + k n_2 - 1`.
Source: **Geroldinger & Halter-Koch, *Non-Unique Factorizations*, 2006, Theorem 6.1.5**;
originally Halter-Koch, Colloq. Math. 63 (1992), 203–210. Restated verbatim in Zhong,
arXiv:2503.21231, abstract:

> "It is known that `D_k(G) = n_1 + k n_2 − 1` if `G ≅ C_{n_1} ⊕ C_{n_2}` is a rank 2 group,
> where `1 < n_1 | n_2`."

Equivalently Freeze–Schmid Remark 5.3(2), read from clean text:

> "2. If `r(G) ≤ 2`, or more generally if `η(G) ≤ D(G)+n` and `D(G) = D(G−)+n−1`,
> then `D_0(G) = D(G−) − 1` and `k_D(G) = 1`."

`n_1 = n_2 = n` gives `D_2 = 3n − 1`, for **all `n ≥ 2`** — no primality restriction, so the
composite values `n = 4, 6` are inside the published range too.

## Correction 2 — `f_n(C_n^2) = 3n - 3` is published (hit #9)

This was X1-N's headline. `f_n(C_n^2) = η(C_n ⊕ C_n) − 1`, and **Gao–Geroldinger survey,
Expo. Math. 24 (2006), Theorem 6.3**:

> "Theorem 6.3. Let `G = C_{n_1} ⊕ C_{n_2}` with `1 ≤ n_1 | n_2`. Then
> `η(G) = 2n_1 + n_2 − 2` and `s(G) = 2n_1 + 2n_2 − 3`."

giving `η(C_n ⊕ C_n) = 3n − 2`. It also exists literally in the `s_{≤ℓ}` phrasing —
Grynkiewicz & Liu, arXiv:2109.10309, citing Wang & Zhao, J. Number Theory 176 (2017):
`s_{≤mn+n−1−k}(C_n ⊕ C_{mn}) = mn + n − 1 + k` for `k ∈ [0, n−1]`; at `m = 1, k = n−1` this
is `s_{≤n}(C_n^2) = 3n − 2`.

`S_n` is the standard extremal witness for this bound, not a new construction.

## Correction 3 — rank-2 profile uniqueness is **Property C** (hit #10)

X1-O's "the extremal profile is unique at rank 2" is a named property in this literature.
Gao–Geroldinger–Grynkiewicz, arXiv:0801.3792, Definition 2.1.3:

> "We say that `G` has **Property C** if every sequence `S` over `G` of length
> `|S| = η(G) − 1`, with no zero-sum subsequence of length in `[1, n]`, has the form
> `S = T^{n−1}` for some sequence `T` over `G`."

Spelled out for our case by Grynkiewicz & Liu, arXiv:2109.10309:

> "any sequence `S` of `3n − 3` terms from `G = C_n ⊕ C_n` with `0 ∉ Σ_{≤n}(S)` must have
> the form `S = e_1^[n−1] · e_2^[n−1] · e_3^[n−1]` for some distinct `e_1, e_2, e_3 ∈ G`."

Established **unconditionally** — Schmid, Q. J. Math. 63 (2012) 477–487 for `k = n−1`, resting
on Reiher's proof of Property B and Gao–Geroldinger–Grynkiewicz multiplicativity. Not prime-
restricted, so `n = 4, 6` are covered.

## Correction 4 — the "which triples" characterisation is published (hit #11)

This is the sharpest one, because it is exactly X1-P **and** exactly the thing the first
draft of this document claimed as a new finding. Grynkiewicz & Liu, arXiv:2109.10309,
Conjecture 1.1 Part 4 — which they state explicitly is **known**, not open:

> "4. If `k = n − 1`, then either
> (a) `S = e_1^[n−1] · e_2^[sn−1] · (x e_1 + e_2)^[(m−s)n+n−1]`, for some `s ∈ [1,m]` and
> `x ∈ [1, n−1]` with `gcd(x, n) = 1`, or
> (b) `S = g_1^[n−1] · g_2^[n−1] · (g_1 + g_2)^[(m−1)n+n−1]`."

At `m = 1, s = 1` form (a) reads `e_1^(n−1) e_2^(n−1) (x e_1 + e_2)^(n−1)` with `gcd(x,n) = 1`.
The literature itself flags this as "a surprisingly nontrivial question", so the difficulty
was real — it had simply already been answered.

### The retracted claim

The first draft of X1-Q claimed as new: *"the shape `e_1^(n−1) e_2^(n−1) (e_1+e_2)^(n−1)`
exhausts the extremal set iff `φ(n) ≤ 2`."* That is a restatement of the published result:
the `x`-family has `φ(n)` members, so it collapses to the single `x = 1` shape exactly when
`φ(n) ≤ 2`. **Retracted.**

### What the computation is still good for — exact mutual confirmation

The two descriptions were checked against each other. Generating triples directly from the
literature's form `e_1^(n−1) e_2^(n−1) (x e_1 + e_2)^(n−1)`, `gcd(x,n) = 1`, over all bases:

| `n` | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|
| literature form | 24 | 48 | 720 | 144 | 5040 |
| **X1-P enumeration** | **24** | **48** | **720** | **144** | **5040** |

Exact agreement at five values including composites. This is no longer a discovery, but it
is a genuine independent computational confirmation of a known theorem whose full corrected
write-up was still "forthcoming" as of 2021 (Grynkiewicz, arXiv:2107.10619, corrects a
missing case in Inverse Zero-Sum Problems III). Recorded as verification, nothing more.

## Correction 5 (method) — grep/sed output in this environment is **not verbatim**

The first draft of this document presented quotes obtained via `grep`/`sed` as verbatim. They
are not: the display filter **strips stopwords**. The same Freeze–Schmid line came back as

- via `grep`: "2. If r(G) ≤ 2, more η(G) ≤ D(G)+n D(G) = D(G−)+n−1, D_0(G) = D(G−) − 1 kD (G) = 1."
- via Read tool: "2. If `r(G) ≤ 2`, **or more generally if** `η(G) ≤ D(G)+n` **and** `D(G) = D(G−)+n−1`, **then** `D_0(G) = D(G−) − 1` **and** `k_D(G) = 1`."

The stripped version drops "or more generally if", which changes a sufficient condition into
something else entirely. `rtk proxy` does **not** bypass this. **Every verbatim quote must
come from the Read tool.** All quotes in this document now do.

## What is NOT retracted

The following remain unchecked against the literature, and are a different question from
Property C — they concern the decomposition of extremal `D_2` witnesses, not `η`-extremal
sequences:

1. **X1-K** — the criterion `f_m(G) ≤ D_2(G) − 2 ⟹ decomposition`.
2. **X1-M** — its converse and the resulting iff for `m ≥ D − 2`, and the `C_2^4`
   characterisation (the 120 failing witnesses are exactly the punctured affine hyperplanes).
3. **X1-O rank 3** — `C_3^3` at `T = 4`. Note this is `s_{≤4}`, **not** `η(C_3^3)`
   (`exp(C_3^3) = 3`, so `η` is `T = 3`), so Property C does not apply to it.

No novelty is claimed for these either; they are simply not yet gated.
