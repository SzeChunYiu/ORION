# `D_2(C_p^3) = (9p−5)/2` for every prime `p ≥ 5`, self-contained — V3

Status: **proved**. The proof uses only the elementary polynomial-method identity of §1, Olson's `D(C_p^3) = 3p−2`, Lucas' theorem, and the explicit family `T_2(p)`. It does **not** use Zhao's Lemma 4.4, Freeze–Schmid Theorem 4.1, or any other text this host cannot read.
Machine check of every structural step, prime by prime: `tools/d2_digit_certificate_v3.py` (all primes `5 ≤ p ≤ 200`).
Novelty: **none claimed.** The *value* is donor-owned (`D2_PRIME_POWER_COROLLARY_V1.md` derives it from Freeze–Schmid + Zhao). What this record supplies is an independent, checkable proof of a statement the rest of the packet uses as an axiom.
Branch: `claude/orion-research-frontier-3ck9yt`.

## Why this matters to the packet

`D_2(C_p^3) = (9p−5)/2` is load-bearing for both lanes. `FINITE_FIRST_FAILURE_REDUCTION_V1.md` opens with "the donor-derived exact value `D_2(G) = (9p−5)/2`"; `GENERAL_CP3_MULTIWISE_MASTER_REDUCTION_V1.md`, `PACKING_DEFECT_CORE_FORMALISM_V1.md` and `CRITICAL_SHORTFREE_SUPPORT_MINIMUM_V1.md` all assume it; the `k ≥ 3` reductions inherit it. Until now the packet's only justification was `D2_PRIME_POWER_COROLLARY_V1.md`, which depends on Zhao Lemma 4.4 — a preprint that could not be fetched from this host, so the whole spine sat on an unverifiable premise. This record discharges that premise for every prime `p ≥ 5`.

## 1. The counting identity

**Theorem 1.** Let `p` be prime, `G = F_p^r`, and let `T = (g_1,…,g_N)` be a sequence over `G`. Put `D = r(p−1)+1`. For every multilinear `h ∈ F_p[x_1,…,x_N]` with `deg h ≤ N − D`,

    Σ_{I ⊆ [N], σ(I) = 0} (−1)^{|I|} h(1_I) ≡ 0   (mod p).

*Proof.* Put `F(x) = h(x) · Π_{j=1}^{r} (1 − (Σ_i x_i g_{ij})^{p−1})`. For `x = 1_I` the product equals 1 if `σ(I) = 0` and 0 otherwise, so `F(1_I) = h(1_I)·[σ(I)=0]`. Also `deg F ≤ (N−D) + r(p−1) = N − 1 < N`. Finally, for any polynomial `F` of degree `< N`, `Σ_{x ∈ {0,1}^N} (−1)^{|x|} F(x) = 0`: it suffices to check monomials, and every monomial of degree `< N` omits some variable `x_i`, whose two values contribute with opposite signs. ∎

Write `N_l = #{I : |I| = l, σ(I) = 0}` and `a_l = (−1)^l N_l`. Taking `h = e_d` (elementary symmetric, so `h(1_I) = C(|I|, d)`) gives

    (★)   Σ_l a_l C(l, d) ≡ 0 (mod p)      for every 0 ≤ d ≤ N − D.

## 2. The length window of a hypothetical extremal sequence

Let `p ≥ 5` and suppose, for contradiction, that some `S` over `G = C_p^3` has `|S| = (9p−5)/2` and **no two disjoint nonempty zero-sum subsequences**. Put `T = S · (−σ(S))`, so `T` is zero-sum of length

    N = (9p−3)/2.

If `T` had three pairwise disjoint nonempty zero-sums, at most one could contain the appended term, leaving two inside `S`. So `T` has at most two.

**Lemma 2.** Every zero-sum `U` with `∅ ≠ U ⊊ T` satisfies `(3p+1)/2 ≤ |U| ≤ 3p−2`.

*Proof.* `T U^{−1}` is a nonempty zero-sum. If it were not an atom it would contain a proper nonempty zero-sum `V`, and then `U`, `V`, `T(UV)^{−1}` would be three pairwise disjoint nonempty zero-sums. So `T U^{−1}` is an atom, whence `|T U^{−1}| ≤ D(C_p^3) = 3p−2` (Olson) and `|U| ≥ N − (3p−2) = (3p+1)/2`. Applying the same to `T U^{−1}` gives `|U| ≤ 3p−2`. ∎

So `N_l = 0` for `l ∉ S := {0} ∪ I ∪ {N}` where

    I = [(3p+1)/2, 3p−2],   |I| = (3p−3)/2,

and `N_0 = N_N = 1`. Note `m := N − D = (3p+1)/2`, so (★) holds for `0 ≤ d ≤ (3p+1)/2`, and `p ≤ m < 2p`.

## 3. The digit decomposition

Write `l = l_1 p + l_0` and `d = d_1 p + d_0` with `0 ≤ l_0, d_0 < p`; Lucas gives `C(l,d) ≡ C(l_1,d_1) C(l_0,d_0)`. Since `m < 2p`, only `d_1 ∈ {0,1}` occur.

**Level 0 (`d_1 = 0`, `d_0 ≤ p−1`).** `C(l_1,0) = 1`, so (★) reads `Σ_r A_r C(r,d_0) ≡ 0` with `A_r = Σ_{l ≡ r (p)} a_l`. The matrix `(C(r,d_0))_{d_0,r}` is unitriangular, hence invertible, so

    A_r = 0   for every residue r.

**Level 1 (`d_1 = 1`, `0 ≤ d_0 ≤ m − p = (p+1)/2`).** `C(l_1,1) = l_1`, so

    Σ_r B_r C(r, d_0) ≡ 0    for 0 ≤ d_0 ≤ (p+1)/2,   where  B_r = Σ_{l ≡ r (p)} l_1 a_l.

Since `C(·,d_0)` is a polynomial of degree exactly `d_0 < p`, these say **`B` is orthogonal to every polynomial of degree ≤ (p+1)/2**.

## 4. The residue classes of `S`

`|I| = (3p−3)/2 = p + (p−3)/2`, and `I` is an interval, so exactly `(p−3)/2` residues occur twice in `I` — namely the classes of `l` and `l+p` for `l ∈ [(3p+1)/2, 2p−2]` — and the rest once. Two elements of `S` lie outside `I`:

- `l = 0`, whose class also contains `2p ∈ I` (indeed `(3p+1)/2 ≤ 2p ≤ 3p−2` for `p ≥ 2`);
- `l = N = 4p + (p−3)/2`, whose class also contains `(5p−3)/2 ∈ I`, and only that.

For `p ≥ 5` these two classes are distinct (they coincide only when `(p−3)/2 = 0`, i.e. `p = 3`), and neither `2p` nor `(5p−3)/2` lies in a doubled pair of `I`. Hence

    |supp B| ≤ 2 + (p−3)/2 = (p+1)/2,

since every other class is a singleton `{l} ⊆ I`, where `A_r = a_l = 0` forces `B_r = l_1 a_l = 0`.

## 5. The contradiction

A vector supported on `k ≤ (p+1)/2` residues and orthogonal to all polynomials of degree `≤ (p+1)/2` vanishes: for each `r* ∈ supp B`, the Lagrange polynomial isolating `r*` inside the support has degree `k − 1 ≤ (p−1)/2 ≤ (p+1)/2`, so `B_{r*} = 0`. Hence `B ≡ 0`.

But the class of `0` is `{0, 2p}`, so `A_0 = a_0 + a_{2p} = 1 + N_{2p} = 0`, giving `N_{2p} ≡ −1`, and since `⌊2p/p⌋ = 2` and `⌊0/p⌋ = 0`,

    B_0 = 2·a_{2p} = 2·N_{2p} ≡ −2   (mod p),

which is nonzero for every prime `p ≥ 5`. This contradicts `B ≡ 0`. ∎

**Theorem 3.** For every prime `p ≥ 5`, `D_2(C_p^3) = (9p−5)/2`.

*Proof.* §2–§5 rule out a sequence of length `(9p−5)/2` with no two disjoint nonempty zero-sums, so `D_2 ≤ (9p−5)/2`. The family `T_2(p)` of `GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md` has length `(9p−7)/2` and packing number 1, so `D_2 ≥ (9p−5)/2`. ∎

## 6. Why `p = 3` escapes

At `p = 3` the two special classes merge: `(p−3)/2 = 0` is the class of `l = 0`, so `0`, `2p = 6` and `(5p−3)/2 = 6` collapse together and the count `B_0 = −2` is no longer forced. This is the same degeneration seen analytically in `D2_PRIME_POWER_COROLLARY_V1.md` (`a_2 ≡ 0 mod 3` by Lucas) and computationally in `SPECTRUM_CONGRUENCE_THEOREM_V2.md` (the system is consistent at `p = 3`). The three routes fail at `p = 3` for the same arithmetic reason, and `D_2(C_3^3) = 11 = (9·3−5)/2` nevertheless — so the formula holds at `p = 3` by a different argument (exhaustively, `EXHAUSTIVE_ANALOG_RESULTS_V2.md`).

## 7. What is checked mechanically

`tools/d2_digit_certificate_v3.py` verifies, for every prime `5 ≤ p ≤ 200`: the interval `I` and its length; that `2p` and `(5p−3)/2` lie in `I` and are distinct; the residue-class census (`(p−3)/2` doubled pairs, `(p−1)/2` singletons, the two special classes); that `m < 2p` and `m − p = (p+1)/2`; that the level-0 matrix has full rank `p`; that `|supp B| ≤ (p+1)/2`; that the Lagrange degree `|supp B| − 1 ≤ m − p`; and that `B_0 = −2 ≢ 0`. `spectrum_congruences_v2.py` independently solves the full linear system and finds it inconsistent for `p ∈ {5,…,43}`, agreeing with the proof.

## Claim ceiling

The value is not new. The proof given here is elementary and self-contained, and its purpose in this packet is to remove an unverifiable donor premise from the shared spine, not to claim priority. Whether this particular argument appears in the literature is `CANNOT_CHECK` from this host.
