# The 2-wise Davenport constant of elementary abelian *p*-groups: a two-sided framework

**Working draft, V1.** Not a manuscript: manuscript content in `papers/` must be authored under the `nature-*` skills package (`AGENTS.md`, paper-writing rule), which this draft has not been. It is the mathematical core assembled in one place so that the argument can be read end to end and attacked.

**Priority status: `CANNOT_CHECK`.** No claim of novelty is made for anything below. This host cannot reach arXiv, ScienceDirect, ResearchGate or Semantic Scholar; the `r = 2` and `r = 3` values are donor-owned (Freeze–Schmid, Discrete Math. 310 (2010); Zhao, arXiv:2506.21383; Geroldinger–Halter-Koch Thm 6.1.5), and the higher-rank statements have not been checked against the literature. In-repo prior art is reconciled in `PRIOR_WORK_RECONCILIATION_V3.md`.

---

## 1. Setting

Let `p` be prime and `G = C_p^r`. A *sequence* over `G` is a finite multiset; a *block* is a nonempty zero-sum subsequence; the *packing number* `pk(S)` is the largest number of pairwise disjoint blocks in `S`. Then

- `D(G)` is the least `ℓ` such that every sequence of length `ℓ` has a block; Olson: `D(C_p^r) = r(p−1)+1`, written `D` throughout.
- `D_k(G)` is the least `ℓ` such that every sequence of length `ℓ` has `k` pairwise disjoint blocks, so `D_1 = D`.

This draft is about `D_2`. Its two published values are `D_2(C_p^2) = 3p−1` and `D_2(C_p^3) = (9p−5)/2`. We give a framework that recovers both from scratch and bounds `D_2(C_p^r)` on both sides for every rank.

## 2. Upper bound

**Lemma 2.1 (atom window).** Let `T` be a zero-sum sequence with `pk(T) ≤ 2` and `|T| = N`. Then every block `U ⊊ T` satisfies `N − D ≤ |U| ≤ D`.

*Proof.* `T U^{−1}` is a block. Were it not an atom it would contain a proper block `V`, and `U, V, T(UV)^{−1}` would be three pairwise disjoint blocks. So `T U^{−1}` is an atom and `|T U^{−1}| ≤ D`; apply the same to `T U^{−1}`. ∎

**Lemma 2.2 (counting identity).** Let `T = (g_1,…,g_N)` be a sequence over `G` and `h` a multilinear polynomial over `F_p` with `deg h ≤ N − D`. Then `Σ_{I: σ(I)=0} (−1)^{|I|} h(1_I) ≡ 0 (mod p)`.

*Proof.* Set `F(x) = h(x)·Π_{j=1}^{r}(1 − (Σ_i x_i g_{ij})^{p−1})`, so `F(1_I) = h(1_I)·[σ(I)=0]` and `deg F ≤ (N−D) + r(p−1) = N−1`. Every monomial of degree `< N` omits a variable, so its alternating sum over `{0,1}^N` vanishes. ∎

With `h = e_d` and `N_l = #{I : |I| = l, σ(I) = 0}`, `a_l = (−1)^l N_l`:

> **(★)** `Σ_l a_l C(l,d) ≡ 0 (mod p)` for every `0 ≤ d ≤ N − D`.

**Theorem 2.3.** Suppose `S` has `|S| = N−1` and `pk(S) ≤ 1`. Then `T = S·(−σ(S))` is zero-sum of length `N` with `pk(T) ≤ 2`, so by Lemma 2.1 all proper block lengths lie in `[N−D, D]`, and `N_0 = N_N = 1`. If the resulting linear system (★) is infeasible over `F_p`, no such `S` exists, i.e. `D_2(G) ≤ N−1`.

Infeasibility is a finite certificate, computed per `(p,r,N)` by `tools/d2_rank_bounds_v3.py`. Writing `N*(p,r)` for the least infeasible `N`, the computation gives, for all 60 tested pairs with `2 ≤ r ≤ p ≤ 23`,

    D_2(C_p^r) ≤ N*(p,r) − 1 = (3D+1)/2      (r odd),
                               (3D+r−1)/2    (r even).

For `r > p` the method weakens; the statement is confined to `r ≤ p`.

### 2.4 A uniform proof at rank 3

At `r = 3` the certificate can be replaced by a proof valid for all `p ≥ 5` at once. Here `N = (9p−3)/2`, `D = 3p−2`, `m := N−D = (3p+1)/2`, and Lemma 2.1 confines proper block lengths to `I = [(3p+1)/2, 3p−2]`, so `N_l = 0` off `S = {0} ∪ I ∪ {N}`.

Split `d` by Lucas: `C(l,d) ≡ C(l_1,d_1)C(l_0,d_0)` with `l = l_1p+l_0`. As `m < 2p`, only `d_1 ∈ {0,1}` occur.

- **Level 0** (`d_1 = 0`, `d_0 ≤ p−1`): `(★)` becomes `Σ_r A_r C(r,d_0) ≡ 0` with `A_r = Σ_{l≡r} a_l`. The matrix `(C(r,d_0))` is unitriangular, so `A_r = 0` for every residue.
- **Level 1** (`d_1 = 1`, `d_0 ≤ m−p = (p+1)/2`): `Σ_r B_r C(r,d_0) ≡ 0` with `B_r = Σ_{l≡r} l_1 a_l`, i.e. `B` is orthogonal to all polynomials of degree `≤ (p+1)/2`.

Now count residues. `|I| = p + (p−3)/2`, so exactly `(p−3)/2` residues occur twice in `I`. Outside `I` lie `l = 0`, whose class also contains `2p ∈ I`, and `l = N = 4p+(p−3)/2`, whose class also contains `(5p−3)/2 ∈ I`; for `p ≥ 5` these two classes are distinct. Every other class is a singleton `{l} ⊆ I`, where `A_r = a_l = 0` forces `B_r = 0`. Hence `|supp B| ≤ 2 + (p−3)/2 = (p+1)/2`. A vector supported on `k ≤ (p+1)/2` residues and orthogonal to all polynomials of degree `≤ (p+1)/2` vanishes, since the Lagrange polynomial isolating a support point has degree `k−1 ≤ (p−1)/2`. So `B ≡ 0`. But `A_0 = a_0 + a_{2p} = 1 + N_{2p} = 0` gives `N_{2p} ≡ −1`, whence

    B_0 = 2·a_{2p} = 2N_{2p} ≡ −2 ≢ 0   (p ≥ 5),

a contradiction. Every structural step is machine-checked for all primes `5 ≤ p ≤ 200` (`tools/d2_digit_certificate_v3.py`).

At `p = 3` the two special classes merge (`(p−3)/2 = 0`) and the argument dissolves — the same degeneration as `a_2 ≡ 0 mod 3` in the Zhao route, and as the observed consistency of the system at `p = 3`.

## 3. Lower bound: intersecting families

**Theorem 3.1.** Let `F` be an intersecting family of nonempty subsets of `[r]` and `m : F → Z_{≥0}` with `Σ_{A ∋ i} m_A ≤ p` for every `i`. Let `v_A ∈ {0,1}^r ⊂ G` be the indicator of `A`. Then

    W = e_1^{p−1} ⋯ e_r^{p−1} · Π_{A∈F} v_A^{m_A}

has `pk(W) = 1`, so `D_2(C_p^r) ≥ r(p−1) + Σ_A m_A + 1`.

*Proof.* Each coordinate sum is `(p−1) + Σ_{A∋i} m_A ≤ 2p−1 < 2p`. A block's `i`-th coordinate sum is a multiple of `p`, so at most one block can have nonzero `i`-th coordinate sum: **each coordinate serves at most one block.** A block using no `v_A` is `Π e_i^{a_i}` with all `a_i ≡ 0 (mod p)` and `a_i ≤ p−1`, hence empty; so every block's coordinate set contains some `A ∈ F` with `m_A > 0`. Two disjoint blocks would then have disjoint coordinate sets and so contain disjoint members of `F`, contradicting intersectingness. ∎

Define `M(r,p) = max{ Σ_A m_A }` over all such `(F,m)`. Then `D_2(C_p^r) ≥ D + M(r,p)`.

`M(r,p)` is `p` times the fractional matching number of the best intersecting family on `[r]`, up to integrality — Erdős–Ko–Rado data. Computed exactly for `r ≤ 5` by enumerating all maximal intersecting families (2, 4, 12, 81) and solving the integer program on each:

| r | optimal support | `ν*` | `M(r,p)` |
|---|---|---|---|
| 2 | `{12}` | 1 | `p` |
| 3 | `{12,13,23}` (triangle) | 3/2 | `(3p−1)/2` |
| 4 | `{12,13,14,234}` | 5/3 | `⌊5p/3⌋` |
| 5 | 16-set maximal family | 9/5 | 9 (`p=5`), 12 (`p=7`) |

The rank-4 optimum is a star of three edges at a vertex together with the complementary triple; its fractional matching puts `p/3` on each edge and `2p/3` on the triple.

## 4. The two sides meet at ranks 2 and 3

| r | p = 5 | 7 | 11 | 13 |
|---|---|---|---|---|
| 2 lower / upper | 14 / 14 | 20 / 20 | 32 / 32 | 38 / 38 |
| 3 lower / upper | 20 / 20 | 29 / 29 | 47 / 47 | 56 / 56 |
| 4 lower / upper | 25 / 27 | 36 / 39 | 59 / 63 | 70 / 75 |
| 5 lower / upper | 30 / 32 | 43 / 47 | — | — |

**Theorem 4.1.** For `r ∈ {2,3}` and every prime `p ≤ 13`, `D_2(C_p^2) = 3p−1` and `D_2(C_p^3) = (9p−5)/2`, with the lower bound from Theorem 3.1 and the upper bound from Theorem 2.3. At `r = 3` the upper bound holds for every prime `p ≥ 5` by §2.4. Modulo Olson's theorem, both values are established here without donor input.

**Theorem 4.2.** `D_2(C_3^4) = 14`.

*Proof.* Lower bound: Theorem 3.1 with `F = {12,13,14,234}` and `m = (1,1,1,2)` gives the length-13 sequence `e_1^2e_2^2e_3^2e_4^2·e_12e_13e_14·(e_2+e_3+e_4)^2` with packing number 1, and `M(4,3) = 5`. Upper bound: a length-14 sequence with packing number `≤ 1` has rank 4 (else it embeds in `C_3^3`, where `D_2 = 11`), so contains a basis; by Lemma 2.1 it has no zero-sum of length `≤ 5`, forcing all multiplicities `≤ 2`. Exhaustive search over all such multisets — 987,944 nodes, 10,852 survivors — finds none with packing number `≤ 1`. ∎

Note `D + M(4,3) = 9 + 5 = 14`.

**Theorem 4.3 (refutation).** `D_2(C_3^5) ≥ 17 > 16 = D + M(5,3)`.

*Proof.* The search at `(p,r,L,s) = (3,5,16,5)` returns 22,843 sequences of length 16 with packing number 1; five were re-checked by an independent atom recursion. ∎

So the natural conjecture `D_2(C_p^r) = D + M(r,p)` — true at `r = 2, 3` and at `(4,3)` — is **false**. Theorem 3.1 is unaffected: its capacity hypothesis is sufficient, not necessary, and the rank-5 witnesses escape it. Each has the form `e_1^2 ⋯ e_5^2 · Π_S v_S` with `S` running over the six 3-subsets of `[5]` through a fixed coordinate: the supports are intersecting, but that coordinate carries `2+6 = 8 ≥ 2p`.

The two constructions scale differently — the capacity family contributes `M(r,p) ≈ p·ν*(r)`, the star of `k`-sets contributes `C(r−1,k−1)` independent of `p` — so neither dominates: at `(3,5)` the star wins (16 against 15), at `(5,5)` capacity wins (29 against 26).

**Open problem 4.4.** Determine `D_2(C_p^r)` for `r ≥ 4`. The framework brackets it; the lower side is an optimisation over admissible configurations for which no single closed form survives.

## 5. Reading: where the halves come from

`D_2(C_p^3) = D + p + (p−1)/2` exceeds the naive `D + exp(G)` by `(p−1)/2`. At ranks 2 and 3 that excess is `M(3,p) − p = (3p−1)/2 − p = (p−1)/2`, i.e. `p(ν*(triangle) − 1)` up to integrality, and `ν*(triangle) = 3/2` because the triangle is the unique intersecting graph with fractional matching number above 1. An equivalent linear-algebra reading — the `(e_12,e_13,e_23)` minor of the cube incidence matrix has determinant `−2`, so the relevant polytope is half-integral — is the same fact: that minor *is* the triangle's incidence matrix. The combinatorial reading is the more useful one, because it survives contact with higher rank: the excess is a supremum over admissible configurations, of which intersecting families with bounded capacity are only one kind — as Theorem 4.3 shows, at rank 5 a different kind wins.

## 6. Status of each claim

| # | Claim | Status |
|---|---|---|
| 2.1, 2.2, 3.1 | Lemmas and the lower-bound construction | proved |
| 2.3 | Upper bound per `(p,r)` | proved, 60 certificates |
| §2.4 | Rank-3 upper bound for all `p ≥ 5` | proved; structure machine-checked to `p = 200` |
| 3.x | `M(r,p)` for `r ≤ 5` | computed exactly |
| 4.1 | `D_2` at ranks 2, 3 | proved (rank 2 for `p ≤ 13`; rank 3 for all `p ≥ 5`) |
| 4.2 | `D_2(C_3^4) = 14` | proved (exhaustive; controls reproduce ranks 2, 3) |
| 4.3 | `D_2(C_3^5) ≥ 17`, refuting `D_2 = D + M` | proved (22,843 witnesses, 5 independently re-checked) |

## 7. What this draft does not contain

`D_3(C_7^3)` is untouched here and remains open; it is the subject of the rest of the packet and of the ChatGPT lane's much deeper reduction. The rank-`≥ 4` gap is open. Whether any statement above is new is unknown and must be settled by a literature pass from a host with access, together with an external mathematical review of §2.4 and §3.
