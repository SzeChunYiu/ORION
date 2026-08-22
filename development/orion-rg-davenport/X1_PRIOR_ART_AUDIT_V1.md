# ORION-RG X1 — hostile prior-art audit of every claim in this branch

Run after the results, before they are allowed to stand. One novelty claim was
killed by it; that outcome is recorded here rather than edited away.

Primary source consulted in full: **Freeze & Schmid, *Remarks on a
generalization of the Davenport constant*, Discrete Math. 310 (2010) 3373–3389**
([arXiv:0905.4248](https://arxiv.org/abs/0905.4248)). Extracted text was read,
not summarized from search results.

## Verdicts

| claim made in this branch | verdict |
|---|---|
| `D_{k+1}(G) <= max(eta_T, D_k + T)` presented as a new lemma | **KILLED.** Freeze–Schmid Prop. 3.2(3), and their form is stronger |
| `D_k` values for `C_2^2`, `C_2^3`, `C_2^4` | **KNOWN.** Replication; instrument validation only |
| coding-theory reading of these constants | **KNOWN.** Schmid, *An Application of Coding Theory to Estimating Davenport Constants* |
| `D_2(C_5^3) = 20` | **not found in the literature** |
| `D_3(C_5^3) = 25` | **not found in the literature** |
| exact `eta_T(C_5^3)` spectrum, `T = 6..12` | **not found in the literature** |
| complete enumeration of the 98,622 extremal length-19 witnesses | **rank 3 not covered.** Zhong 2025 (*Combinatorica*) solves the inverse problem for **rank 2** |

"Not found" is a statement about a search, not a proof of novelty. The searches
covered the Freeze–Schmid paper in full, the rank-2 inverse-problem literature,
the higher-rank Davenport surveys, and the coding-theory-to-Davenport line.

## What Freeze–Schmid actually establish (the relevant parts)

- **Prop. 3.2(2)** `D_{k+1}(G) <= D_k(G) + M`, with `M` the minimum length of a
  minimal zero-sum sequence dividing an extremal `B`. Sharper than 3.2(3), and
  the natural place a genuine refinement would live.
- **Prop. 3.2(3)** for each `l`, `D_{k+1}(G) <= max{D_k(G) + l, s_{<=l}(G) - 1}`.
  Their `s_{<=l}` is our `eta_l`.
- `D_k(G) = D_0(G) + k*exp(G)` for all sufficiently large `k`; this holds for all
  `k` when `r(G) <= 2`, and **fails for elementary 2- and 3-groups of rank >= 3**.
- Exact `D_k` for elementary 2-groups of **rank 4 and 5**; rank `<= 3` already
  known. `D_2(C_2^4)=8`, `D_3(C_2^4)=11`, `D_4(C_2^4)=13`; `D_2(C_2^5)=10`,
  `D_3(C_2^5)=13`, `D_4(C_2^5)=16`, `D_5(C_2^5)=19`.
- **`D_0(C_3^3) = 6`, `D_1(C_3^3) = 7`, `D_2(C_3^3) = 11`.**

## Instrument validation against known rank-3 elementary p-group values

The `C_3^3` row above is the single most valuable check available, because it is
the **same structural case** as our new results — elementary `p`-group, rank 3,
`p` odd — where the linear form is known to fail.

- `D_1(C_3^3) = 7` — **reproduced** by `x1f0_general_dk_and_fT.c`.
- `D_2(C_3^3) = 11` — check in progress; if the instrument disagrees, the
  `C_5^3` results must be treated as unverified until it is resolved.

## The question this reframes

Freeze–Schmid's `D_0(C_3^3) = 6` with `D_2(C_3^3) = 11` says the linear regime
has **not** begun by `k = 2` for `C_3^3` (`6 + 3*2 = 12 != 11`).

Our sequence is `D_1(C_5^3) = 13`, `D_2 = 20`, `D_3 = 25`, increments `7, 5`.
Since `exp(C_5^3) = 5`, the `k=2 -> 3` increment already equals `exp`. If the
linear regime begins at `k = 2`, then `D_0(C_5^3) = 25 - 15 = 10` and
`D_k(C_5^3) = 5k + 10` for `k >= 2`, predicting `D_4 = 30`.

So the interesting statement is not "one more constant" but **where the linear
regime begins for an elementary p-group of rank 3**, against the known contrast
that for `C_3^3` it has not begun by `k = 2`. `D_4(C_5^3)` decides it.

Note also that `20` and `25` exceed the naive linear values `18` and `23`, which
is consistent with the known failure of the linear form at rank `>= 3`. That is
a coherence check on our own numbers, not evidence of novelty.

## Standing rule this audit produced

Run the hostile prior-art check **before** investing in a direction, not after
writing it up. The killed claim here cost a protocol rewrite, a receipt rewrite,
a PR retitle, and a re-scoped agent — all of which a fifteen-minute search
beforehand would have avoided.
