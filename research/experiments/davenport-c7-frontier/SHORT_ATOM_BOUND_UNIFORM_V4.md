# A uniform short-atom bound, and both corridors cut in half — V4

Status: **proved**. Strengthens Proposition 4.3 / Hypothesis `(Z)` from "`|C| = 28` forces an atom of length `≤ 12`" to the uniform "`23 ≤ |C| ≤ 29` forces an atom of length `≤ 10`", by one argument covering every length at once. Consequences: the first corridor drops from **six** length triples to **four**, and the second from **six** profiles to **three**.
Checker: `verify_short_atom_bound_v4.py` (five steps, two independent decision procedures, three controls). Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Statement

> **Proposition 4.3′.** Let `C` be a zero-sum sequence over `C_7^3` with `23 ≤ |C| ≤ 29` and packing number `z(C) = 2`. Then `C` has an atom of length `≤ 10`.

The previous state of the art in this packet was: `≤ 10` for `|C| ∈ {27,29}` (symmetric congruences), `≤ 12` for `|C| = 28` (`HYPOTHESIS_Z_PROVED_V3.md`), and **nothing at all** for `|C| ∈ {23,24}` — the lengths that arise in the second corridor, where only the trivial `[8,19]` atom range was used.

## 2. Proof

Because `z(C) = 2`, every proper nonempty zero-sum subsequence of `C` is an atom and its complement is an atom too. So if every atom had length `≥ 11`, the proper zero-sum lengths would lie in the **two-sided** window

    S = [11, |C| − 11].

Fix an index `i` and apply the counting identity with the pointed multilinear polynomial

    h = x_i · e_d(x_{−i}),   deg h = d + 1 ≤ |C| − D,   so   d ≤ |C| − 20,

for which `h(1_I) = [i ∈ I]·C(|I|−1, d)`. Writing `M_l` for the number of zero-sum `l`-subsets through `i`, the zero-sum index sets containing `i` are those and `C` itself, so for every admissible `d`

> **(P)**  `Σ_{l ∈ S} (−1)^l M_l C(l−1, d) + (−1)^{|C|} C(|C|−1, d) ≡ 0  (mod 7)`.

For each `|C| ∈ {23,24,27,28,29}` this system is **inconsistent over `F_7`**, so some atom has length `≤ 10`. ∎

### 2a. The `|C| = 28` case by hand

Unknowns `M_11 … M_17`, degrees `d ≤ 8`. Six of the nine equations already contradict:

| `d` | equation `(mod 7)` |
|---|---|
| 6 | `M_14 ≡ 6` |
| 5 | `−M_13 − M_14 ≡ 1` |
| 4 | `M_12 + 2M_13 + M_14 ≡ 6` |
| 3 | `−M_11 − 3M_12 − 3M_13 − M_14 ≡ 1` |
| 0 | `−M_11 + M_12 − M_13 + M_14 − M_15 + M_16 − M_17 ≡ 6` |
| 7 | `−M_11 + M_12 − M_13 + M_14 − 2M_15 + 2M_16 − 2M_17 ≡ 4` |

`d = 6` gives `M_14 ≡ 6`; then `d = 5` gives `−M_13 ≡ 7 ≡ 0`, so `M_13 ≡ 0`; then `d = 4` gives `M_12 ≡ 0`; then `d = 3` gives `−M_11 ≡ 7 ≡ 0`, so `M_11 ≡ 0`. Substituting into `d = 0` leaves `−M_15 + M_16 − M_17 ≡ 0`. Finally `d = 7` reads

    6 − 2(M_15 − M_16 + M_17) = 6 − 0 = 6 ≢ 4   (mod 7),

a contradiction. ∎

The rigidity is again a Lucas phenomenon: `13 = (1,6)_7` and `14 = (2,0)_7` make the top-degree columns nearly empty, so the equations peel the unknowns off one at a time from `d = 6` downwards.

## 3. Why pointing is what buys this

`SPECTRUM_CONGRUENCE_THEOREM_V2.md` records that at `N = 37` the pointed congruences give **exactly** the symmetric threshold — "pointing at one element buys nothing". That observation is correct, and it is about the **one-sided** window `[1,w]` at the obstruction length itself.

The regime here is different: on the complement `C` the window is **two-sided**, `[w+1, |C|−w−1]`, and there complementation identifies `l` with `|C|−l`. The symmetric identity can therefore only ever see the sums `N_l = N_{|C|−l}` — it has half as many unknowns, but its equations are correspondingly degenerate. Pointing breaks that pairing: `M_l` and `M_{|C|−l}` are independent unknowns, and the extra equations more than pay for the extra unknowns. The checker confirms the separation directly: at `|C| = 28` the symmetric system is feasible even at `w = 13`, while the pointed one is infeasible already at `w = 10`.

**The transferable structure: point the polynomial exactly when the window is two-sided.** This is the same shape as the QG47 → QG48 move (an empty frontier revived by raising the slice dimension) — a symmetry that looks like it is helping is actually collapsing the information, and deliberately breaking it re-opens the problem.

## 4. Consequence 1 — the first corridor: 6 triples → 4

Let `A` be a shortest atom of the obstruction `T`, `|A| = s ∈ {8,9,10}` (Lemma 2.3), and `C = T A^{−1}`, `|C| = 37 − s ∈ {29,28,27}`. By §1, `C` has an atom `E` with `|E| ≤ 10`; and `F = C E^{−1}` is zero-sum with `|F| ≤ 19`, because otherwise `F` splits and `A, E` plus two blocks of `F` are four disjoint blocks of `T`. Since `A` is shortest, `|E| ≥ s`. So `T = A·E·F` is a three-atom factorization with

| `s` | `|C|` | admissible `|E|` | triple |
|---|---|---|---|---|
| 8 | 29 | `[10,10]` | `(8,10,19)` |
| 9 | 28 | `[9,10]` | `(9,9,19)`, `(9,10,18)` |
| 10 | 27 | `[10,10]` | `(10,10,17)` |

> **First corridor (tightened).** `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(10,10,17)`.

`(9,11,17)` and `(9,12,16)` are **eliminated**, by congruence alone and with no search. Note also that this derivation uses one uniform statement in place of the three separate inputs the V1 corridor used (Zhao Lemma 4.4 twice, Zhang's `s_{≤12}(C_7^3) = 26` once) — all three were donor-owned, and none is needed now.

## 5. Consequence 2 — the second corridor: 6 profiles → 3

`ATOM_SPECTRUM_CONGRUENCE_V3.md` forces an atom `B` with `|B| ∈ {13,14}`. Its complement `C = T B^{−1}` has length `24` or `23`, and `SECOND_CORRIDOR_V3.md` classified the factorization through `B` using only the trivial atom range `[8,19]`, getting six profiles. Applying §1 to these lengths — which is new; the bound had never been pushed below `|C| = 27` — gives an atom `E` of `C` with `|E| ≤ 10`, and as above `F = C E^{−1}` is an atom. With `|E| = 8` excluded exactly as in `SECOND_CORRIDOR_V3.md` §2 (an 8 in the profile forces `s = 8`, so the profile would have to be a first-corridor triple, and none of these is):

> **Second corridor (tightened).** `(9,13,15)`, `(9,14,14)`, `(10,13,14)`.

`(11,12,14)`, `(11,13,13)` and `(12,12,13)` are **eliminated** — precisely the three "flat" profiles that `SECOND_CORRIDOR_V3.md` §3 flagged as the hardest, since none carries a near-maximal atom for the support-four classification to bite on. What remains all have a part of length `≤ 10` and a part of length `≥ 13`.

## 6. Verification

`verify_short_atom_bound_v4.py`:

1. brute-forces the pointed identity over `C_3^3` on random length-15 zero-sum sequences, **and** checks it fails one degree higher, so the bound `d ≤ n − D − 1` is sharp;
2. for each `|C| ∈ {23,24,27,28,29}` decides the `w = 10` system by Gaussian elimination over `F_7` **and** by exhaustive search over all `7^{|S|}` assignments, requiring the two to agree — infeasible in every case;
3. checks the `w = 9` system is feasible in every case (exactly one solution each), so the bound `≤ 10` is the best this argument gives and step 2 is not vacuous;
4. checks the symmetric system at `|C| = 28` is feasible at `w = 10` and at `w = 13`, isolating the gain to pointing;
5. re-derives both corridors and asserts the exact triple/profile lists;
6. runs a real packing-number-3 object over `C_5^3` through the analogous `p = 5` bound: all 56 atom complements satisfy the predicted bound.

## Claim ceiling

This tightens the corridors; it does not by itself close anything that was open. `D_3(C_7^3) = 36` was already proved in this packet (`HYPOTHESIS_Z_PROVED_V3.md`, `verify_D3_C7_end_to_end_v3.py`) and does not depend on the strengthening — the strengthening shrinks the case analysis that proof performs. Its value is (a) a shorter and fully uniform route to the same theorem, (b) removal of three donor-owned inputs from the corridor derivation, and (c) a smaller search space for the primes where the analogous programme is not yet finished. The `p ≥ 11` consequences are recorded separately.
