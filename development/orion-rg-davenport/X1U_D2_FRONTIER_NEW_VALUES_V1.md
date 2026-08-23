# ORION-RG X1-U — the `D_2(C_2^r)` frontier: two new exact values, `f_4(C_2^7)`, and a closed-form conjecture

> **SUPERSEDED IN PART — PRIOR-ART HIT #15 (X1-V banner has the verbatim source).** The
> values `D_2(C_2^7) = 12` and `D_2(C_2^8) = 14` are **published**: Borello–Schmid–Scotti
> (arXiv:2406.04034, June 2024), Remark 5.15, as part of a list `r ≤ 17` deduced from
> their intersecting-code Table 2 via their Theorem 5.12. They were not new when derived
> here. What remains this atom's own: the explicit certificates and exhaustive searches
> (BSS print values, not witnesses — our routes are independent and agree), the
> `f_4(C_2^7) = 11` value (not in BSS; still gate-pending elsewhere), the min-ZS-5
> stratum census at `r = 7` with the second criterion failure, and the falsified
> conjecture record below.

Freeze–Schmid (Discrete Math. 310 (2010)) determine `D_2(C_2^r)` for `r ≤ 6` and state —
Read-tool verbatim — *"For larger `r` our bounds are far apart."* This atom decides the next
two ranks.

## New values

> **`D_2(C_2^7) = 12`. `D_2(C_2^8) = 14`. `f_4(C_2^7) = 11`** (equivalently
> `s_{≤4}(C_2^7) = 12`).

## Method: rank-forcing + basis-fixing + Lemma-A prunes

A length-`(r+k)` witness (no two disjoint nonempty zero-sums) is squarefree (a repeat is a
2-zero-sum whose complement, of length `≥ D`, contains a disjoint one) and has **rank `r`**
(rank `≤ r−1` embeds it in `C_2^{r−1}`, where its length is `≥ D_2(C_2^{r−1})`). So it
contains a basis; mod `GL` fix it standard. Lemma A gives min-ZS `≥ k`, hence the `k` extra
elements have weight `≥ k−1`, pairwise XORs of weight `≥ k−2`, triple XORs `≥ k−3`, 4-XORs
`≥ k−4`. The search (`x1u_d2_frontier_hunter.c`) enumerates exactly this space.

**Each rung's rank argument consumes the previous rung's value**: `r = 7` uses the published
`D_2(C_2^6) = 11`; `r = 8` uses our `D_2(C_2^7) = 12`; `r = 9` will use `D_2(C_2^8) = 14`.

### Instrument validation, both directions, before any open case

- Positive path: `r=6, k=4` returns 14,685 witnesses-containing-the-standard-basis —
  reproduced **exactly, with exact division**, from the X1-T orbit inventory via
  `Σ|orbit|·b(rep)/#bases`.
- Negative path: `r=6, k=5` returns 0, matching the published `D_2(C_2^6) = 11`.

## `D_2(C_2^7) = 12`

**Upper (the new content):** no length-12 witness. The search space is 5-subsets of the 64
weight-≥4 vectors of `F_2^7` under the min-ZS-≥5 conditions — and it is **empty**: the C
hunter reports `leaves = 0`, and an independently written Python DFS
(`x1u_independent_negative_check.py`), built from the definition
`|S| + wt(x_S) ≥ 5 ∀ S, |S| ≤ 4`, confirms **0** five-sets. So not only is no witness
disjoint-free — no candidate even satisfies the minimum-zero-sum conditions.

**Lower:** length-11 witnesses exist — the X1-T configuration `(f=1, C4, z=2)` gives the
explicit certificate `{e_1..e_7} ∪ {7,11,21,25}`, verified by a third code path
(`#ZS = 15`, min-ZS 4, no two disjoint). (The bound `≥ 12` is also Freeze–Schmid Thm 4.1.)

## `D_2(C_2^8) = 14`

**Lower:** the hunt at `r=8, k=5` found 3,971,520 length-13 disjoint-free sets; certificate
`{e_1..e_8} ∪ {15, 51, 85, 169, 205}` verified independently (`#ZS = 31`, min-ZS 5, no two
disjoint), so `D_2 ≥ 14`.

**Upper:** Freeze–Schmid Theorem 7.8, Read-tool verbatim: *"Let r ∈ N. Then
D2(C2r) < (3r + 6)/2."* At `r = 8`: `< 15`, so `≤ 14`. ∎

Note the jump: `12 = r+5` at `r=7` but `14 = r+6` at `r=8` — the first departure from the
`r+5` regime, located exactly.

## `f_4(C_2^7) = 11`, and a second criterion failure — outside the iff regime

The census at `r=7, k=4` splits by minimum zero-sum:

| stratum | witnesses containing the standard basis |
|---|---|
| min-ZS 4 | 685,020 |
| **min-ZS 5** | **21,840** |
| total | 706,860 |

The min-ZS-5 stratum is **nonempty** — explicit verified member
`{e_1..e_7} ∪ {15, 120, 51, 85}`. Consequences:

1. **`f_4(C_2^7) = 11`.** `≥ 11` from any stratum member (11 elements, no zero-sum of
   length `≤ 4`). `≤ 11` because a 12-element short-zero-sum-free set would have rank 7
   (`f_4(C_2^6) = 8 < 12`), hence contain a basis plus a 5-set satisfying exactly the
   conditions shown empty above.
2. **The X1-K criterion fails at `C_2^7`** — `f_m = 11 > D_2 − 2 = 10` — and the
   decomposition indeed fails (the 21,840 do not factor as 4-zero-sum · basis). This is the
   **second** criterion failure after `C_2^4`, and the **first outside the X1-M iff regime**
   (`m = 4 < D − 2 = 6`): it fills the previously-empty "undecided by theory" cell of the
   X1-M table, and it resolves to FAIL. X1-M's completeness observation and its
   "`C_2^4` is unique" framing are corrected in place.

## A closed-form conjecture, registered with its prediction before the test

> **FALSIFIED by X1-V (2026-08-23), at its first test.** `D_2(C_2^9) = 16`, not 15 — the
> length-15 witness is the parity-check view of the (reported unique) extremal binary
> minimal code of dimension 6, constructed and certified in X1-V before the search ran.
> The registered prediction below is retained as written; the formula and the rate-`1/4`
> reading are dead. The true growth is governed by the irregular minimum-redundancy
> function `ρ(k)` of intersecting codes — see X1-V.

All six known values fit one formula:

> **Conjecture.** `D_2(C_2^r) = r + 3 + ⌊(r+1)/3⌋` for all `r ≥ 3`.

| `r` | 3 | 4 | 5 | 6 | **7** | **8** |
|---|---|---|---|---|---|---|
| actual | 7 | 8 | 10 | 11 | **12** | **14** |
| formula | 7 | 8 | 10 | 11 | 12 | 14 |

Its asymptotic slope is `4/3 ≈ 1.333` — strictly inside the published asymptotic band
`[1.26, 1.40]` for `D_2(C_2^r)/r`, which it would sharpen to an exact constant.

**Registered prediction: `D_2(C_2^9) = 15`** — i.e. the running `r=9, k=6` hunt must find
**no** length-15 witness. The bracket is already `{15, 16}`: `≥ 15` by the padding lemma
(append `e_{r+1}` to any witness; no new zero-sums can use it — the padded `r=8` certificate
is verified), `≤ 16` by FS Thm 7.8. A 16 would falsify the conjecture at its first test.

## Prior-art status, stated honestly

FS explicitly present `r ≤ 6` as the settled range and `r ≥ 7` as open (2010). The earlier
gate (X1-Q scope) followed the citation graph through Zhong 2025, Grynkiewicz–Liu 2022,
Girard–Schmid 2018/2020 and found no later exact values for elementary 2-groups; its stated
gaps (no MathSciNet/zbMATH) carry over, and a targeted post-2010 search for `D_2(C_2^7)`,
`D_2(C_2^8)`, and `s_{≤4}(C_2^7)` specifically is REQUIRED before any external claim. The
computations and certificates stand regardless; every negative has an independent
reimplementation and every positive an independently verified certificate.
