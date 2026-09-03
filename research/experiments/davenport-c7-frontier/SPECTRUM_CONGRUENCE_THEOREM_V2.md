# Zero-sum length-spectrum congruences and their consequences for `C_7^3` — V2

Status: **proved (classical technique, machine-checked instances with certificates)**; novelty of the technique: **none claimed** (Chevalley–Warning counting in the style of Olson / Alon–Dubiner / Zhao); novelty of the specific consequences: **CANNOT_CHECK** (priority not searched hostilely; Zhao arXiv:2506.21383 was not readable from this host).
Checker: `spectrum_congruences_v2.py` (pure Python, no dependencies; prints an explicit certificate for every inconsistency claim).
Branch: `claude/orion-research-frontier-3ck9yt`. Builds on `D2_PRIME_POWER_COROLLARY_V1.md`.

## 1. The congruence

Let `p` be prime, `G = C_p^r`, `D = D(G) = r(p-1)+1` (Olson), and let `T = g_1 ... g_N` be any sequence over `G`. For an index set `I ⊆ [N]` write `σ(I) = Σ_{i∈I} g_i` and `1_I ∈ {0,1}^N` for its indicator.

**Theorem 1.** For every `c ∈ G` and every multilinear polynomial `h ∈ F_p[x_1,…,x_N]` with `deg h ≤ N − D`,

    Σ_{I ⊆ [N], σ(I)=c} (−1)^{|I|} h(1_I) = 0   in F_p.

*Proof.* Put `P(x) = Π_{j=1}^{r} (1 − (Σ_i g_{ij} x_i^{p−1} − c_j)^{p−1}) · h(x_1^{p−1},…,x_N^{p−1})` in `F_p[x_1,…,x_N]`. For `x ∈ F_p^N` let `I = {i : x_i ≠ 0}`; then `x_i^{p−1} = [i ∈ I]`, so `P(x) = [σ(I) = c] · h(1_I)`. Each `I` arises from exactly `(p−1)^{|I|} ≡ (−1)^{|I|}` vectors `x`, hence `Σ_{x∈F_p^N} P(x) = Σ_{σ(I)=c} (−1)^{|I|} h(1_I)`. On the other hand `deg P ≤ r(p−1)^2 + (p−1) deg h = (p−1)(r(p−1) + deg h) < (p−1)N` as soon as `deg h ≤ N − r(p−1) − 1 = N − D`, and a monomial `Π x_i^{a_i}` has `Σ_{x∈F_p^N} Π x_i^{a_i} ≠ 0` only if every `a_i` is a positive multiple of `p−1`, which forces total degree `≥ N(p−1)`. So `Σ_x P(x) = 0`. ∎

**Corollary 2 (symmetric form).** Let `N_ℓ` be the number of index subsets `I` of size `ℓ` with `σ(I) = 0`. Then

    Σ_ℓ (−1)^ℓ · C(ℓ, d) · N_ℓ ≡ 0 (mod p)   for 0 ≤ d ≤ N − D.          (*)

If `T` is zero-sum then `N_N = 1` and `N_ℓ = N_{N−ℓ}` (complementation). Note that `N_ℓ` counts index subsets, i.e. a sub-multiset `b ≤ m` contributes `Π_v C(m_v, b_v)`; the checker cross-checks (*) on an explicit example with this weighting.

The checker treats `(*)` as a linear system over `F_p` in the unknowns `N_ℓ` for the lengths that are *not* forbidden, and decides consistency by Gaussian elimination. Inconsistency is certified by coefficients `λ_d` with `Σ_d λ_d·(equation d)` reading `0 = nonzero`.

## 2. Consequences (all machine-checked, certificates printed by the checker)

**Theorem A (independent proof of the D2 gate).** `D_2(C_7^3) ≤ 29`.

*Proof.* Let `|S| = 29` and `T = S·(−σ(S))`, a zero-sum sequence of length 30. If `T` had no zero-sum subsequence of length in `[1,10]`, then by complementation none in `[20,29]`, and `(*)` for `d = 0,…,11` in the unknowns `N_{11},…,N_{15}` (with `N_{16..19}` tied by symmetry and `N_0 = N_30 = 1`) is inconsistent modulo 7 (certificate `λ = (5,0,0,0,6,0,6,0,1,0,1,0)`, combination `0 = 3`). So `T` has a zero-sum `U` with `|U| ≤ 10`. Then `|T U^{−1}| ≥ 20`; delete one element `x`; the remaining `≥ 19 = D(C_7^3)` elements contain a zero-sum `V`; `R = T(UV)^{−1} ∋ x` is a nonempty zero-sum. Of the pairwise disjoint `U, V, R` at most one contains the appended element, so `S` has two disjoint nonempty zero-sum subsequences. ∎

This uses only Olson's `D(C_7^3) = 19` and Theorem 1; it does **not** depend on reading Zhao's Lemma 4.4. Together with the explicit length-28 packing-1 witness of `CUBE_FAMILY_LOWER_BOUNDS_V2.md`, `D_2(C_7^3) = 29` is now established inside this repository by two independent routes (this one and the enumeration route of `EXHAUSTIVE_ANALOG_RESULTS_V2.md`). The same computation succeeds for `p = 5, 11, 13` at `N = (9p−3)/2` with window `[1,(3p−1)/2]`, and is silent (consistent) for `p = 3`, exactly matching the Lucas degeneration `a_2 ≡ 0 (mod 3)` recorded in `D2_PRIME_POWER_COROLLARY_V1.md`.

**Theorem B (short zero-sums at the D3 target length).** Every zero-sum sequence of length 37 over `C_7^3` contains a nonempty zero-sum subsequence of length at most 10.

*Proof.* Forbidding lengths `[1,10] ∪ [27,36]` makes `(*)` (`d = 0,…,18`) inconsistent mod 7 (certificate printed by the checker: `0 = 6`). ∎

Forbidding only `[1,9]` is consistent, so this method alone cannot force a zero-sum of length `≤ 9`. The binary-cube sequences of `SUPPORT7_BINARY_CUBE_THEOREM_V1.md` (length 37, all multiplicities ≤ 6) have no zero-sum subsequence of length ≤ 7 at all, so **no** length-spectrum argument can push the bound below 8.

**Theorem B' (threshold table).** Let `k(N)` be the least `k` such that every zero-sum sequence of length `N` over `C_7^3` is forced by `(*)` to contain a zero-sum subsequence of length `≤ k`. The checker computes

    N : 20 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40
 k(N) : 10 10 10 10 11 12 10 14 10 10 10 11 12 10 14 10 10 10 11 12

(`N = 21` is not decided by `(*)` at all.) In particular `k(27) = k(29) = k(30) = k(31) = k(36) = k(37) = 10`.

**Theorem C (`p = 5` analogue).** Every zero-sum sequence of length 26 over `C_5^3` contains a zero-sum subsequence of length at most 7 (`k(26) = 7` for `C_5^3`; forbidding `[1,6]` is consistent).

**Proposition D (forced residues at length 29).** If a zero-sum sequence `B` of length 29 over `C_7^3` has no zero-sum subsequence of length `≤ 9`, then its spectrum satisfies

    N_10 ≡ 3, N_11 ≡ 3, N_12 ≡ 3, N_13 ≡ 0, N_14 ≡ 6 (mod 7)

(unique solution of `(*)`). In particular `N_10 ≠ 0`: `B` has a zero-sum subsequence of length exactly 10, whose complement is a minimal zero-sum sequence of the maximal length `D(C_7^3) = 19`. This is used in `OBSTRUCTION_REDUCTION_LEMMAS_V2.md`.

## 3. What this does and does not do

- It replaces the unread donor lemma in the D2 gate by a self-contained, certificate-carrying argument. Priority for the *statement* `D_2(C_p^3) = (9p−5)/2` remains with the donors named in `D2_PRIME_POWER_COROLLARY_V1.md` (Freeze–Schmid lower bound) and is otherwise CANNOT_CHECK.
- It narrows the D3 problem: a hypothetical length-36 obstruction yields, after appending `−σ`, a length-37 zero-sum sequence with a shortest zero-sum of length in `{8, 9, 10}` (Theorem B combined with the D2 gate; see the reduction lemmas). It does **not** decide `D_3(C_7^3)`.
- The residual windows for the complement lengths 27, 28, 29 are all consistent under `(*)` (nullity 2, 1, 0), so the symmetric congruences alone cannot close the residual; non-symmetric `h` (Theorem 1 with `h = x_J · e_d`) and multiplicity information are the next lever, and are **not** exploited here.
