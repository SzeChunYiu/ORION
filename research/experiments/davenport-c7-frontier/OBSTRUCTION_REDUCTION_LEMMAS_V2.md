# Necessary structure of a hypothetical length-36 obstruction over `C_7^3` — V2

Status: **proved** (elementary arguments on top of `D(C_7^3) = 19` [Olson], `D_2(C_7^3) = 29` [`SPECTRUM_CONGRUENCE_THEOREM_V2.md` Theorem A + `CUBE_FAMILY_LOWER_BOUNDS_V2.md`], and Theorem B / Proposition D of the spectrum record). Novelty: the reformulation in §1 is donor-owned (Halter-Koch 1992 / Freeze–Schmid); the specific reductions in §2–§4 are bookkeeping that any hostile reviewer would regard as routine; they are recorded because they fix exactly what a `D_3` search has to enumerate.
Branch: `claude/orion-research-frontier-3ck9yt`.

Throughout, `G = C_7^3`, `pk(·)` is the zero-sum packing number, `B(G)` the monoid of zero-sum sequences, `A(G)` its atoms (minimal zero-sum sequences), and `L(B)` the set of factorization lengths of `B ∈ B(G)` into atoms.

## 1. Block reformulation (folklore)

**Lemma 1.1.** For any sequence `S` over `G` and `g = −σ(S)`: `pk(S·g) = pk(S) + 1`.

*Proof.* If `U_1,…,U_k` are disjoint zero-sums in `S`, then `S·g·(U_1⋯U_k)^{−1}` contains `g`, is nonempty and zero-sum, giving `k+1` blocks in `S·g`. Conversely, among `k+1` disjoint blocks of `S·g` at most one contains `g`; the others lie in `S`. ∎

**Lemma 1.2.** For `B ∈ B(G)`, `pk(B) = max L(B)`. Consequently `D_k(G) = max{ |B| : B ∈ B(G), max L(B) ≤ k }`, and

    D_3(C_7^3) ≥ 37  ⇔  there is a zero-sum sequence T of length 37 over C_7^3 with pk(T) = 3 (i.e. max L(T) = 3).

*Proof.* A factorization into `k` atoms is a `k`-packing; conversely a maximal packing `U_1⋯U_k` has zero-sum complement, which must be empty (else `k+1` blocks), and refining each `U_i` into atoms gives a factorization of length `≥ k`, hence `= k`. For the equivalence: if `|S| = 36` and `pk(S) ≤ 2` then `T = S·(−σ(S))` has `pk(T) ≤ 3` by Lemma 1.1 and `pk(T) ≥ 3` because `|T| ≥ 30 = D_2 + 1` (delete one element, apply `D_2`, the rest is a third block); conversely if `pk(T) = 3` then for **every** `g ∈ T`, `pk(T·g^{−1}) ≤ 2` (three blocks in `T·g^{−1}` plus the zero-sum remainder containing `g` would be four). ∎

So a counterexample to `D_3(C_7^3) = 36` is the same thing as a zero-sum sequence of length 37 that is a product of three atoms in every factorization.

## 2. Reductions for `T` (zero-sum, `|T| = 37`, `pk(T) = 3`)

**Lemma 2.1 (multiplicities).** Every element of `T` has multiplicity `≤ 6`, so `|supp T| ≥ 7`; the support spans `G` (otherwise `T` lies in a plane `H ≅ C_7^2` and `|T| = 37 ≥ D_4(C_7^2) = 34` already gives `pk(T) ≥ 4`, using `D_k(C_n^2) = (k+1)n − 1`).

*Proof.* If `v^7 | T` then `T·v^{−7}` has length `30 ≥ D_2 + 1`; delete an element `x`, find two disjoint blocks in the remaining `≥ 29` elements, and the complement of everything is a fourth block containing `x`. ∎

**Lemma 2.2 (no short zero-sums).** `T` has no zero-sum subsequence of length `≤ 7`.

*Proof.* If `|U| ≤ 7` then `|T U^{−1}| ≥ 30 ≥ D_2 + 1`; delete an element `x` of `T U^{−1}`, obtain two disjoint blocks `V, W` in the remaining `≥ 29`, and `R = T(UVW)^{−1} ∋ x` is a fourth block. ∎

The binary-cube sequences of length 37 with multiplicities `≤ 6` have no zero-sum of length `≤ 7` either, so Lemma 2.2 cannot be sharpened by length considerations alone (`SUPPORT7_BINARY_CUBE_THEOREM_V1.md` shows those sequences nevertheless have `pk = 4`).

**Lemma 2.3 (a shortest block has length 8, 9 or 10).** `T` has a zero-sum subsequence `U` with `8 ≤ |U| ≤ 10`. Every zero-sum subsequence of `T` has length in `[8, 29]`.

*Proof.* Theorem B of the spectrum record gives `|U| ≤ 10`; Lemma 2.2 gives `≥ 8`; complementation gives the upper end. ∎

**Lemma 2.4 (the complement of a shortest block).** Let `U` be a zero-sum subsequence of minimal length `u ∈ {8,9,10}` and `B = T U^{−1}`, `|B| = 37 − u ∈ {29, 28, 27}`. Then

1. `B` is zero-sum with `L(B) = {2}`: every proper nonempty zero-sum subsequence `V` of `B` has `B V^{−1} ∈ A(G)`;
2. every proper zero-sum subsequence of `B` has length in `[max(u, |B| − 19), 19]`, i.e. in `[10,19]`, `[9,19]`, `[10,19]` for `u = 8, 9, 10` respectively;
3. for every `x ∈ B`, `B x^{−1}` has `pk = 1` and length `|B| − 1 ≤ 28`;
4. if `u = 8` (`|B| = 29`): `B = A·A'` with `A ∈ A(G)` of length `19 = D(G)` and `A'` of length 10, and `B x^{−1}` is a `D_2`-extremal sequence (length 28, `pk = 1`) for **every** `x ∈ B`;
5. if `u = 10` (`|B| = 27`): `B = A·A'` with `|A'| = 10`, `|A| = 17`.

*Proof.* (1) If `V` is a proper zero-sum subsequence of `B` and `B V^{−1}` were not an atom, it would split into two blocks, giving four blocks `U, V, ·, ·` in `T`. (2) `|B V^{−1}| ≤ D(G) = 19` because it is an atom, and `|V| ≥ u` because `V | T`. (3) Two disjoint blocks in `B x^{−1}` plus the remainder (containing `x`) give three blocks in `B`, four in `T`. (4) By (2) the spectrum of `B` avoids `[1,9]`, so Proposition D applies: `N_10 ≡ 3 (mod 7)`, hence `B` has a zero-sum subsequence `A'` of length exactly 10 and `A = B A'^{−1}` is an atom of length 19. (5) Theorem B' gives `k(27) = 10`, so `B` has a zero-sum subsequence of length `≤ 10`, and by (2) it has length exactly 10. ∎

**Lemma 2.5 (planes).** For every 2-dimensional subspace `H ≤ G`, `|T ∩ H| ≤ D_4(C_7^2) − 1 = 33` and, for the underlying `S = T g^{−1}`, `|S ∩ H| ≤ D_3(C_7^2) − 1 = 26`, using `D_k(C_n^2) = (k+1)n − 1` (Halter-Koch / Delorme–Ordaz–Quiroz, donor).

## 3. What a complete search must cover

By Lemmas 1.2 and 2.1–2.4 it suffices to enumerate zero-sum sequences `T` of length 37 with multiplicities `≤ 6`, no zero-sum of length `≤ 7`, and to test `pk(T) ≤ 3`; equivalently sequences `S` of length 36 with multiplicities `≤ 6`, no zero-sum subsequence of length `≤ 7`, spanning support, plane occupancy `≤ 26`, and `pk(S) ≤ 2`. This is exactly the search frame implemented in `tools/enum_packing_v2.c` (parameters `p=7 L=36 cap=6 s=7 kmax=2 --planecap 26`).

Alternatively (Lemma 2.4), it suffices to classify the zero-sum sequences `B` with `L(B) = {2}` and `|B| ∈ {27, 28, 29}` and to test their length-`(37 − |B|)` zero-sum extensions. The case `|B| = 29` is controlled by the inverse problem for `D_2(C_7^3)` (length-28 sequences with `pk = 1`, equivalently length-28 sequences with no zero-sum subsequence of length `≤ 9` and `pk = 1`).

## 4. Analogues for `p = 5` and `p = 3`

The same arguments, with `D(C_5^3) = 13`, `D_2(C_5^3) = 20` and Theorem C (`k(26) = 7` for `C_5^3`), show that a counterexample to `D_3(C_5^3) = 25` would be a zero-sum sequence of length 26 with multiplicities `≤ 4`, no zero-sum subsequence of length `≤ 5`, a shortest block of length 6 or 7, and `pk = 3`; equivalently a length-25 sequence with multiplicities `≤ 4`, no zero-sum of length `≤ 5`, plane occupancy `≤ 18` and `pk ≤ 2`. For `p = 3` (`D = 7`, `D_2 = 11`) the corresponding frame is length 14, multiplicities `≤ 2`, no zero-sum of length `≤ 3`, `pk ≤ 2`. These frames are the ones executed in `EXHAUSTIVE_ANALOG_RESULTS_V2.md`.

## Claim ceiling

Nothing here decides `D_3(C_7^3)`. The lemmas bound the search; they do not perform it.
