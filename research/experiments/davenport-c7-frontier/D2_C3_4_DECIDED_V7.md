# `D_2(C_3^4) = 14`

**Status: decided.** Checker: `verify_d2_c3_4_v7.py`. This is the conjecture's **first test at
rank 4** — `CLOSED_FORM_CONJECTURE_V7.md` was previously supported only at ranks 2, 3 and 5 — and
it was a prediction before it was a computation.

    conjecture:  D_2(C_3^4) = (3/2)·4·2 + 2 = 14        computed:  14

---

## 1. Lower bound: `D_2(C_3^4) ≥ 14`

The exhaustive DFS in `tools/witness_optimum_v6.c` returns `M*(4,3) = 5` with the family

    V = (1100), (1010), (0110), (1101), (1011),   each of multiplicity 1

so the Theorem-W construction gives, with `q = r(p−1) = 8`,

    S = e₁²e₂²e₃²e₄² · V,      |S| = q + M* = 8 + 5 = 13.

**Verified independently of the criterion.** Enumerating all `2^13` subsets and running an exact
packing computation: `S` has **109 blocks** and `z(S) = 1`. So `D_2(C_3^4) ≥ 14`.

The witness also **saturates its atom-size window**: sizes run 5..9 with no gaps, the window
`[n−q, q+1]` is exactly `[5, 9]`, and the core is empty as Theorem Y requires. That is a sixth
instance of the pattern in `CLOSED_FORM_CONJECTURE_V7.md` §5, and the first at rank 4.

## 2. Upper bound: `D_2(C_3^4) ≤ 14`

Every length-14 sequence over `C_3^4` has `z ≥ 2`. Two reductions make the search finite and small:

1. **Short zero-sums are excluded, losslessly.** If `z(S) ≤ 1` and `|S| = 14`, the complement
   lemma gives every block length `≥ |S| − q = 6`, so `S` has **no zero-sum of length `≤ 5`**.
   Searching only such sequences therefore loses nothing.
2. **`S` spans, so a basis may be assumed.** Otherwise `S` lies in a subgroup `≅ C_3^s` with
   `s ≤ 3`, and `z(S) ≤ 1` would force `|S| ≤ D_2(C_3^3) − 1 = 10 < 14`. So `S` contains a basis,
   which `GL(4,3)` carries to `e_1,…,e_4`; the remaining 10 terms are enumerated as a
   non-decreasing multiset over the 80 nonzero elements. (`0 ∉ S`, since `0` would be a block of
   length 1, and `1 ≥ 6` is false.)

The sweep, `enum_rank_generic_v3 3 4 14 5`:

| | |
|---|---|
| nodes | **987,944** |
| leaves (complete sequences reaching length 14) | **10,852** |
| leaves with `z ≤ 1` | **0** |

The 10,852 leaves are each tested by an exact layered DP over pairs of disjoint sub-multisets, so
the result is not vacuous — ten thousand candidates were examined and every one had two disjoint
zero-sum subsequences.

### The enumerator is calibrated in both directions

A search that returns zero proves nothing unless it can return non-zero. At `C_3^3`, where
`D_2 = 11` is known:

| run | expectation | result |
|---|---|---|
| `3 3 10 3` — a witness exists | `found > 0` | **found = 5006** |
| `3 3 11 4` — no witness can exist | `found = 0` | **found = 0**, leaves = 0 |

So the tool reproduces `D_2(C_3^3) = 11` exactly, from both sides.

## 3. It closes a gap in `D_2(C_3^5) = 17`

This is not only a test of the conjecture. `D2_C3_5_DECIDED_V6.md` step 2 — the reduction that
lets the rank-5 sweep assume a spanning sequence — cited `D_2(C_3^4) = 14` **before that value was
proved**. The bound actually available then was `D_2(C_3^4) ≤ 2·D(C_3^4) = 18`, capping a `z ≤ 1`
sequence at length 17, one short of excluding `|S| = 17`. So the `s = 4` branch of that argument
was open and the rank-5 result was incomplete there.

The present computation closes it. No length-14 sequence over `C_3^4` has `z ≤ 1`; by monotonicity
— blocks of a subsequence are blocks of the whole — no length-17 one does either, which is what
step 2 needs. See the correction appended to `D2_C3_5_DECIDED_V6.md`.

## 4. What it does and does not settle

**Does.** `D_2(C_3^4) = 14`, a new exact value; and the closed form of
`CLOSED_FORM_CONJECTURE_V7.md` now agrees with **25** known exact values across ranks 2, 3, 4
and 5 rather than 24 across ranks 2, 3 and 5.

**Does not.** Rank 4 is where two of the conjecture's three shortfalls live. This point is
`p = 3`, where the construction *achieves* the conjectured value; the open cases are `(4,7)` —
construction 37, conjecture 38 — and `(5,5)`, and this computation says nothing about either.
Confirming the conjecture where the construction already reaches it is much weaker evidence than
deciding a point where it does not. `D_2(C_7^4) ∈ {37, 38}` remains the sharp test.

Novelty unchecked, as everywhere in this packet: whether `D_2(C_3^4)` is already in the
literature has not been verified. See `EXTERNAL_PRIOR_ART_V5.md` §V7.
