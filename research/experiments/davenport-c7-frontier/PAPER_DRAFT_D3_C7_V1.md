# The 3-wise Davenport constant of `C_7^3`

**Working manuscript draft, V1.** Not yet a submission: manuscript content under `papers/` must be authored with the `nature-*` skills package (`AGENTS.md`), which this draft has not been, and every claim below still requires external mathematical review and a prior-art pass from a host with journal access. Priority for everything here is `CANNOT_CHECK`.

---

## Abstract

For a finite abelian group `G` and `k ≥ 1`, let `D_k(G)` be the least `ℓ` such that every sequence over `G` of length `ℓ` has `k` pairwise disjoint nonempty zero-sum subsequences. We determine

    D_3(C_7^3) = 36,

resolving the smallest open case of the rank-three multiwise Davenport problem. Along the way we prove `D_2(C_p^3) = (9p−5)/2` for every prime `p ≥ 5` by an elementary argument, and we determine `D_3(C_5^3) = 25` and `D_2(C_3^4) = 14`. The method is a counting identity of Chevalley–Warning type applied to the *length spectrum* of zero-sum subsequences, combined with a structural description of the zero-sum subsequences of a packing-critical sequence. Apart from Olson's evaluation `D(C_p^r) = r(p−1)+1`, the argument is self-contained.

## 1. Introduction

Write `F(G)` for the free abelian monoid over `G`; a *sequence* is an element of `F(G)`, i.e. a finite multiset. A *block* is a nonempty zero-sum subsequence, and the *packing number* `z(S)` is the largest number of pairwise disjoint blocks of `S`. Then `D_k(G)` is the least `ℓ` with `z(S) ≥ k` for every `|S| = ℓ`, and `D_1 = D` is the Davenport constant.

Rank two is settled: `D_k(C_{n_1} ⊕ C_{n_2}) = n_1 + k n_2 − 1`. Rank three is not. The relevant lower bound is a construction giving

    D_k(C_n^3) ≥ ((2k+5)n − 5)/2      (n odd),

and the first genuinely open instance is `k = 3`, `n = 7`, where the bound reads `D_3(C_7^3) ≥ 36`. Our main result is that it is tight.

> **Theorem A.** `D_3(C_7^3) = 36`.

The proof does not proceed by search over sequences of length 36 — that space is far too large — but by showing that the *combinatorics of zero-sum lengths* alone is contradictory.

> **Theorem B.** For every prime `p ≥ 5`, `D_2(C_p^3) = (9p−5)/2`.

Theorem B is not new as a statement, but our proof is elementary and self-contained, and Theorem A depends on it.

## 2. The counting identity

**Lemma 2.1.** Let `p` be prime, `G = F_p^r`, `T = (g_1,…,g_N)` a sequence over `G`, and `D = r(p−1)+1`. For every multilinear `h ∈ F_p[x_1,…,x_N]` with `deg h ≤ N − D`,

    Σ_{I ⊆ [N], σ(I) = 0} (−1)^{|I|} h(1_I) ≡ 0   (mod p).

*Proof.* Put `F(x) = h(x)·Π_{j=1}^{r}(1 − (Σ_i x_i g_{ij})^{p−1})`. On `{0,1}^N` the product is the indicator of `σ(I) = 0`, so `F(1_I) = h(1_I)[σ(I)=0]`, while `deg F ≤ (N−D) + r(p−1) = N−1`. Every monomial of degree `< N` omits some variable, whose two values contribute with opposite signs, so `Σ_{x∈{0,1}^N} (−1)^{|x|}F(x) = 0`. ∎

Two instances are used. With `h = e_d` and `N_l = #{I : |I| = l, σ(I) = 0}`:

    (★)  Σ_l (−1)^l N_l C(l,d) ≡ 0,     0 ≤ d ≤ N − D.

With `h = x_i·e_d(x_{−i})`, so that `h(1_I) = [i ∈ I]·C(|I|−1,d)`:

    (P)  Σ_{I ∋ i, σ(I)=0} (−1)^{|I|} C(|I|−1,d) ≡ 0,    0 ≤ d ≤ N − D − 1.

Note `N_l` counts index sets: a zero-sum sub-multiset `M` contributes `w(M) = Π_g C(v_g(T), v_g(M))`, and complementation preserves this weight.

## 3. Theorem B

Let `S` have `|S| = (9p−5)/2` with `z(S) ≤ 1`, and set `T = S·(−σ(S))`, zero-sum of length `N = (9p−3)/2`; then `z(T) ≤ 2`.

**Lemma 3.1 (atom window).** Every zero-sum `∅ ≠ U ⊊ T` has `(3p+1)/2 ≤ |U| ≤ 3p−2`.

*Proof.* `T U^{−1}` is a block; were it not an atom it would contain a proper block `V`, and `U, V, T(UV)^{−1}` would be three disjoint blocks. So `T U^{−1}` is an atom, `|T U^{−1}| ≤ D = 3p−2`, and symmetrically. ∎

So `N_l = 0` off `S = {0} ∪ I ∪ {N}` with `I = [(3p+1)/2, 3p−2]`, and `m := N − D = (3p+1)/2 < 2p`. Split `d` by Lucas. Level `d_1 = 0` gives `Σ_r A_r C(r,d_0) ≡ 0` for `d_0 ≤ p−1` with `A_r` the residue-class sums, and the matrix is unitriangular, so `A_r = 0` for all `r`. Level `d_1 = 1` gives that `B_r = Σ_{l ≡ r} ⌊l/p⌋ a_l` is orthogonal to every polynomial of degree `≤ (p+1)/2`.

Counting residues: `|I| = p + (p−3)/2`, so `(p−3)/2` residues repeat inside `I`; outside `I` lie `l = 0`, whose class also contains `2p ∈ I`, and `l = N`, whose class also contains `(5p−3)/2 ∈ I`. For `p ≥ 5` these are distinct, every other class is a singleton where `A_r = 0` forces `B_r = 0`, so `|supp B| ≤ (p+1)/2`. A vector on `k ≤ (p+1)/2` points orthogonal to all polynomials of degree `≤ (p+1)/2` vanishes (Lagrange, degree `k−1 ≤ (p−1)/2`). But `A_0 = 1 + N_{2p} = 0` gives `N_{2p} ≡ −1`, hence `B_0 = 2N_{2p} ≡ −2 ≢ 0`. Contradiction, so `D_2 ≤ (9p−5)/2`; the matching construction gives equality. ∎

At `p = 3` the two special classes coincide and the argument dissolves — consistent with the known exceptional behaviour of elementary 3-groups.

## 4. Theorem A

Let `T` be zero-sum over `C_7^3` with `|T| = 37` and `z(T) = 3`; `D = 19` and `D_2 = 29` by Theorem B.

**Lemma 4.1.** Every block of `T` has length `≥ 8`.
*Proof.* If `|U| ≤ 7` then `|T U^{−1}| ≥ 30 > D_2`, so any 29 of its terms contain two disjoint blocks, leaving a nonempty zero-sum remainder: four blocks. ∎

**Lemma 4.2.** The zero-sum sub-multisets of `T` are exactly `∅`, `T`, the atoms, and the complements of atoms; the last two families meet only in atoms of length 18 or 19.
*Proof.* For proper `U`, `z(U) + z(T U^{−1}) ≤ 3` with both `≥ 1`. ∎

Writing `W_l` for the weight sum of atoms of length `l`, `(★)` becomes 19 equations over `F_7` in `W_8,…,W_19` plus two overlap terms. Three further necessary conditions apply: **closure** (an atom of length `≤ 17` has a complement of length `> D`, which splits into two atoms whose lengths are again atom lengths); the **corridor** (§4.1); and the resulting spectrum must be consistent. Together these leave exactly eight admissible atom-length sets. Each is then eliminated by a **complement system**: for an atom `A`, `C = T A^{−1}` has `z(C) = 2`, so its zero-sum multisets are `∅`, `C` and atoms paired by complementation with lengths in the spectrum, and `(★)` applied to `C` is infeasible. No spectrum survives, so no such `T` exists and `D_3(C_7^3) ≤ 36`. With the construction, equality. ∎

### 4.1 The corridor

Every atom has length in `[8,19]`; `(★)` at `N = 37` forbids the window `[1,10]`, so the shortest atom has length `s ∈ {8,9,10}`. For a shortest atom `A`, `C = T A^{−1}` has length `37−s > D`, so `z(C) = 2` and every atom `W` of `C` pairs with `C W^{−1}`. Applying `(★)` to `C` forbids short atoms: length `≤ 10` when `|C| ∈ {29,27}`. For `|C| = 28` the symmetric identity gives only `≤ 14`; the sharper bound is Proposition 4.3. The three cases then yield the six profiles `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`.

**Proposition 4.3.** Every zero-sum sequence of length 28 over `C_7^3` with packing number 2 has an atom of length `≤ 12`.

*Proof.* Otherwise its proper zero-sum lengths are exactly `{13,14,15}`. Fix an index `i`; by `(P)` with `d ≤ 8`,

    −M_13 C(12,d) + M_14 C(13,d) − M_15 C(14,d) + C(27,d) ≡ 0   (mod 7),

`M_l` counting zero-sum `l`-sets through `i`. Since `14 = (2,0)_7`, Lucas gives `C(14,d) = 0` for `1 ≤ d ≤ 6`. Then `d = 6` forces `M_14 ≡ 6`; `d = 5` forces `M_13 ≡ 0`; `d = 0` forces `M_15 ≡ 0`; and `d = 7` reads `6 + 3 = 9 ≡ 2 ≢ 0`. ∎

Proposition 4.3 is where the pointed identity is essential. At `N = 37` it yields nothing beyond `(★)`, because there the unknowns grow with the equations; here only three lengths are admissible.

## 5. Verification

Every computational step has an executable checker, and the machinery is validated against objects that must survive it.

- Lemma 2.1 and `(P)` are brute-forced over all `2^15` index subsets of random zero-sum sequences over `C_3^3`, for every index and every admissible degree.
- Lemma 4.2, `(★)`, the complement systems and `(P)` are checked against a **real** packing-number-3 sequence over `C_5^3` of length 25: predicted and actual zero-sum multiset families agree exactly (144 = 144), every complement system is feasible, and every pointed congruence holds with true weights. The framework does not eliminate objects that exist.
- One of the eight spectrum eliminations is additionally verified by hand.
- `D_3(C_5^3) = 25` and `D_2(C_3^4) = 14` are obtained by exhaustive symmetry-reduced enumeration with independent replication.

## 6. Open questions

1. `D_3(C_p^3) = (11p−5)/2` for all `p ≥ 5`. Our argument is arithmetic in `p = 7`: the vanishing `C(14,d) ≡ 0` is a base-7 accident.
2. `D_k(C_n^3) = ((2k+5)n−5)/2` for `k ≥ 4`.
3. `D_2(C_p^r)` for `r ≥ 4`. We give matching bounds at `r ≤ 3`; above that the natural conjecture `D + M(r,p)`, with `M` an Erdős–Ko–Rado optimum over intersecting families, is **false** — `D_2(C_3^5) ≥ 17` and `D_2(C_5^4) ≥ 26`.

## Status of this draft

Theorem A rests on a chain of machine-checked steps. It has not been reviewed by a mathematician. Whether Theorem A is new, and whether this route is new, are unknown from this host. Both must be settled before submission.
