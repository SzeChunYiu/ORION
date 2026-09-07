# Hypothesis `(Z)` proved: `D_3(C_7^3) = 36` is now unconditional — V3

Status: **proved**. The last donor dependency of `D3_C7_CONDITIONAL_CLOSURE_V3.md` is discharged. The only external input remaining anywhere in the chain is Olson's `D(C_7^3) = 19`.
Checkers: `verify_hypothesis_Z_v3.py`, `verify_pointed_identity_v3.py`. Priority CANNOT_CHECK.

## 1. What was needed

`(Z)` *every zero-sum sequence of length 28 over `C_7^3` with packing number 2 has an atom of length `≤ 12`.*

This was the specialisation of Zhang's `s_{≤12}(C_7^3) = 26` used by the corridor argument, and the one input this packet could neither read nor reproduce — the symmetric congruences give only "`≤ 14`".

## 2. Proof

Suppose `C` is a counterexample: zero-sum, `|C| = 28`, `z(C) = 2`, no atom of length `≤ 12`. Since `z(C) = 2`, every proper nonempty zero-sum of `C` is an atom and its complement is an atom too, so proper zero-sum lengths lie in `[13, 28−13] = {13,14,15}`.

Fix an index `i` and apply the counting identity with the **pointed** multilinear polynomial

    h = x_i · e_d(x_{−i}),    deg h = d+1 ≤ |C| − D = 9,  so d ≤ 8,

for which `h(1_I) = [i ∈ I]·C(|I|−1, d)`. The zero-sum index sets containing `i` are the 13-, 14- and 15-sets through `i` — write `M_13, M_14, M_15` for their numbers — together with `C` itself. Hence for every `0 ≤ d ≤ 8`

> **(P)**  `−M_13·C(12,d) + M_14·C(13,d) − M_15·C(14,d) + C(27,d) ≡ 0  (mod 7)`.

Nine equations in three unknowns. They are inconsistent, and one can see it by hand using Lucas (`12 = (1,5)_7`, `13 = (1,6)_7`, `14 = (2,0)_7`, `27 = (3,6)_7`):

| `d` | `C(12,d)` | `C(13,d)` | `C(14,d)` | `C(27,d)` | equation |
|---|---|---|---|---|---|
| 0 | 1 | 1 | 1 | 1 | `−M_13 + M_14 − M_15 + 1 ≡ 0` |
| 5 | 1 | 6 | 0 | 6 | `−M_13 + 6M_14 + 6 ≡ 0` |
| 6 | 0 | 1 | 0 | 1 | `M_14 + 1 ≡ 0` |
| 7 | 1 | 1 | 2 | 3 | `−M_13 + M_14 − 2M_15 + 3 ≡ 0` |

From `d = 6`: `M_14 ≡ 6`. Substituting into `d = 5`: `−M_13 + 36 + 6 = −M_13 + 42 ≡ −M_13`, so `M_13 ≡ 0`. Then `d = 0` gives `0 + 6 − M_15 + 1 = 7 − M_15 ≡ −M_15`, so `M_15 ≡ 0`. Finally `d = 7` reads

    −0 + 6 − 0 + 3 = 9 ≡ 2 ≢ 0   (mod 7),

a contradiction. So no counterexample exists and `(Z)` holds. ∎

Note `C(14,d) = 0` for `1 ≤ d ≤ 6`, because `14 = (2,0)_7` and Lucas then forces the factor `C(0,d) = 0` — this is what makes the system so rigid, and it is special to length 14 in characteristic 7.

## 3. Why the pointed identity works here when it failed before

`SPECTRUM_CONGRUENCE_THEOREM_V2.md` records a retained negative: at length 37 the pointed congruences reproduce the symmetric threshold exactly and buy nothing. That is still true. They bite here because the structure is far tighter — only three admissible zero-sum lengths, so three unknowns against nine equations, whereas at length 37 the unknowns grow with the equations.

## 4. Validation

The identity carries the whole argument, so it is checked before being used (`verify_pointed_identity_v3.py`):

1. **Brute force.** For random zero-sum sequences over `C_3^3` and *every* index `i`, the pointed congruence is verified over all `2^15` index subsets, for every admissible `d`. No violations.
2. **Real object.** For the packing-number-3 sequence over `C_5^3` of length 25, the true counts of zero-sum index sets of each size through each of the 25 indices are computed by a size-graded convolution, and the pointed congruence checked with those counts for every index and every `d ≤ 11`. No violations.

So the machinery is correctly implemented and does hold on an object that exists.

## 5. Consequence

With `(Z)` proved, `D3_C7_CONDITIONAL_CLOSURE_V3.md` becomes unconditional:

> **Theorem.** `D_3(C_7^3) = 36`.

The chain, with every input's provenance: Olson's `D(C_7^3) = 19` (classical, external); `D_2(C_7^3) = 29` (this packet, `D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md`); minimum atom length 8, shortest-atom bound `≤ 10`, and the `|C| = 29, 27` short-atom bounds (this packet's congruences); `(Z)` (above); the corridor (assembled from those); the atom-spectrum characterisation, closure, and the complement systems (this packet). **Olson's theorem is the only external ingredient.**

## Claim ceiling

This is a machine-assisted proof with several computational steps, each with its own checker and each validated against objects that must survive it. It has not been reviewed by a mathematician, and no novelty is claimed: whether `D_3(C_7^3) = 36` is already known, and whether this argument is new, are both `CANNOT_CHECK` from this host. External review and a literature pass remain necessary before any submission.
