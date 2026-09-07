# No `D_4(C_5^3)` obstruction contains a support-four maximal atom — V6

Status: **proved** (exhaustive, given the support-four maximal-atom classification). Closes the support-four branch of the only profile in the `D_4(C_5^3)` corridor that carries a maximal atom.
Checker: `verify_d4_c5_support4_maximal_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt` (uses lane A's classification).

## 1. Statement

> **Theorem M.** No zero-sum 5-short-free sequence of length 31 over `C_5^3` contains a maximal atom of support four. Consequently the `(6,6,6,13)` profile of `D4_C5_FOUR_ATOM_CORRIDOR_V4.md` requires its 13-atom to have support `≥ 5`.

## 2. Why this profile, and why now

`D4_C5_FOUR_ATOM_CORRIDOR_V4.md` reduced the open `D_4(C_5^3) ∈ {30,31}` branch to five four-atom profiles. Of those, `(6,6,6,13)` is the **only** one carrying a maximal atom (`13 = D(C_5^3)`) — the same phenomenon `COMBINED_COMPLETION_MAP_V6.md` identifies at every prime, where exactly one corridor triple has a maximal part. So it is the only profile lane A's support-four maximal-atom classification can reach, and this record reaches it.

## 3. Method

By the classification, every support-four maximal atom over `C_p^3` is, up to `GL(3,p)`,

`U = e_1^{p−1} e_2^{p−1} e_3^{a} g_4^{p−a}`,  `g_4 = e_3 − a^{−1}(e_1+e_2)`,  `1 ≤ a ≤ (p−1)/2`,

which at `p = 5` is `e_1^4 e_2^4 e_3^a g_4^{5−a}` with `a ∈ {1,2}`, of length 13. Containing a support-four maximal atom is a `GL(3,5)`-invariant property, so the two canonical types suffice.

The checker then enumerates **exhaustively** every 5-short-free multiset of length 31 containing `U`. State is carried as five 125-bit masks `S_k` = sums of `k`-element sub-multisets, `k ≤ 4`; adding `v` is legal exactly when `−v ∉ S_0 ∪ ⋯ ∪ S_4`, since a zero-sum of length `≤ 5` through `v` is precisely that. Multisets are enumerated in nondecreasing index order, so each is generated once.

## 4. Result

| `a` | compatible elements | length-31 extensions | **of these zero-sum** | distinct total-sums realised |
|---|---|---|---|---|
| 1 | 74 of 124 | 135 | **0** | 51 of 125 |
| 2 | 64 of 124 | 192 | **0** | 65 of 125 |

**Controls.** The test is not vacuous: length-31 extensions do exist (135 and 192 of them), and they realise 51 and 65 distinct total-sums out of 125 — so the enumeration reaches length 31 comfortably and the sum is genuinely varying. Zero is simply never among the sums realised.

## 5. What remains for `(6,6,6,13)`, and for `D_4(C_5^3)`

The profile survives only with a 13-atom of support `≥ 5`, which the classification does not cover. The other four profiles — `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)`, `(7,7,7,10)` — are **flat**: no part reaches `D = 13`, so no maximal-atom method applies to them at all. That is the same gap `COMBINED_COMPLETION_MAP_V6.md` §3 identifies for `D_3(C_p^3)` at `p ≥ 11`, appearing here at `p = 5` and `k = 4`.

So `D_4(C_5^3)` remains **open**. This record removes one branch of one profile of five.

## Claim ceiling

Exhaustive within the stated frame, and conditional on the support-four maximal-atom classification, which is lane A's result and is not re-proved here. Nothing is claimed about maximal atoms of support `≥ 5`, about the other four profiles, or about the value of `D_4(C_5^3)`.
