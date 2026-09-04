# The last gap in Observation D, reduced to two short intervals — V5

Status: **two further facts proved; the remaining gap is now a single vanishing statement on `[1,h−1] ∪ [h+1,p−1]`.** Observation D is still not proved.
Checker: `verify_support_reduction_v5.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

`DUAL_SUPPORT_TWELVE_POINTS_V5.md` left one unproved claim: `supp Q ⊆ S`, the twelve-point set. This record shrinks it.

## 1. Fact 1 — the intervals merge (proved)

`Q` vanishes on the atom range `[p+1, 3p−2]` off `Z`. By the symmetry `Q(N−y) = (−1)^N Q(y)` it also vanishes on the image

`σ([p+1, 3p−2]) = [N−3p+2, N−p−1] = [2p+h+2, 4p+h−1]`

off `σ(Z)`. These two intervals **overlap**, since `2p+h+2 ≤ 3p−1 ⟺ h+3 ≤ p ⟺ p ≥ 3`. So `Q` vanishes on the single interval `[p+1, 4p+h−1]` off `Z ∪ σ(Z)`, and therefore

`supp Q ⊆ [0,p] ∪ (Z ∪ σZ) ∪ [4p+h, N]`.

Now `S ∩ [0,p] = {0, h, p}`, the top block `[4p+h, N]` is the `σ`-image of the bottom, and `Z ∪ σZ ⊆ S` when `Z` is a pair of special lengths. Hence

> **`supp Q ⊆ S` ⟺ `Q` vanishes on `[1, h−1] ∪ [h+1, p−1]`.**

Two short intervals inside the bottom base-`p` block, together `p−3` points. Verified for all 76 primes `5 ≤ p ≤ 397`, and the checker also confirms on real duals that the two conditions are literally the same condition, not merely both true.

## 2. Fact 2 — the shape of `P` (proved, Lucas)

`deg P ≤ A = N−D = 2p+h+2 < 3p`, so every `d ≤ A` has base-`p` digits `(d_1,d_0)` with `d_1 ≤ 2`. Writing `y = y_1 p + y_0`, Lucas gives `C(y,d) = C(y_1,d_1) C(y_0,d_0)`, so

> `P(y) = F_0(y_0) + y_1·F_1(y_0) + C(y_1,2)·F_2(y_0)`,

where `F_0, F_1` are **arbitrary** functions on `F_p` and `F_2` has degree `≤ h+2`. The degree cap `d ≤ A` bites only in the `d_1 = 2` block: the per-block caps on `d_0` are `(p−1, p−1, h+2)`. Checked against direct evaluation on every point, for `p = 11, 13, 17`.

On the bottom block `y_1 = 0`, so `P = F_0` there, and `P(p) = F_0(0) + F_1(0)`.

## 3. The remaining claim, explicitly

Combining: for `y ∈ [1,h−1]` we have `N−y = 5p + (h−y)`, digits `(5, h−y)`; for `y ∈ [h+1,p−1]` we have `N−y = 4p + (p+h−y)`, digits `(4, p+h−y)`. So the claim to prove is

- `F_0(y) + (−1)^N [ F_0(h−y) + 5F_1(h−y) + 10·F_2(h−y) ] = 0` for `1 ≤ y ≤ h−1`,
- `F_0(y) + (−1)^N [ F_0(p+h−y) + 4F_1(p+h−y) + 6·F_2(p+h−y) ] = 0` for `h+1 ≤ y ≤ p−1`,

as a **consequence** of the imposed conditions (`P = 0` on `[A, D]`, i.e. `F_0 + 2F_1 + F_2 = 0` on `[h+2, p−2]`; and `Q = 0` on the atom range off `Z`). Here `C(5,2) = 10` and `C(4,2) = 6`.

That is a finite system of linear relations among three functions on `F_p`, indexed by residues, with no dependence on `p` beyond the ranges — the form in which a uniform proof should be attempted.

## 4. Status of the chain

| Step | Status |
|---|---|
| duality: inconsistency ⟺ a dual `P` exists | **proved** (`LUCAS_CRITERION_V5.md`) |
| reduction to `Q = P + (−1)^N P∘σ`, its symmetry, `P = 0` on `[N−D,D]` | **proved** (`OBSERVATION_D_REDUCTION_V5.md`) |
| Lemma 1: `S ∩ [p+1,3p−2]` = the three special lengths | **proved** (`DUAL_SUPPORT_TWELVE_POINTS_V5.md`) |
| Fact 1: reduction of `supp Q ⊆ S` to the two bottom intervals | **proved** (here) |
| Fact 2: `P = F_0 + y_1F_1 + C(y_1,2)F_2` | **proved** (here) |
| `Q = 0` on `[1,h−1] ∪ [h+1,p−1]` | **verified for `p ≤ 23`, NOT proved** |
| **Observation D** | **verified for `5 ≤ p ≤ 31`, NOT proved** |

## Claim ceiling

Nothing here extends Observation D's verified range, and it remains unproved. The contribution is that the gap has gone from "a rank argument about a matrix" to one vanishing statement about three explicit functions on `F_p`, over `p−3` points, with every surrounding step proved.
