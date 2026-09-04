# The pointed polynomial method for generalized Davenport constants of `C_p^3`

**Author.** Sze Chun Yiu.
**Status.** Draft V1. Internal machine verification complete; external prior-art pass and independent mathematical review outstanding (see §9).

---

## Abstract

For a finite abelian group `G`, the generalized Davenport constant `D_k(G)` is the least `ℓ` such that every sequence over `G` of length `ℓ` has `k` pairwise disjoint nonempty zero-sum subsequences. We determine `D_2(C_p^3) = (9p−5)/2` for every prime `p ≥ 5`, with Olson's `D(C_p^r) = r(p−1)+1` as the only external input, and we determine `D_3(C_7^3) = 36` on the same footing.

The method is a *pointed* form of the Chevalley–Warning counting identity, and we reduce it to arithmetic. Dualising the pointed system, rewriting the dual vector by Newton's forward-difference formula about the left end of the window, and applying Lucas' theorem shows that the system on the window `[w+1, m−w−1]` is inconsistent **exactly when** some integer `d ∈ [m−2w−1, m−3p+1]` has all base-`p` digits dominated by those of `m−1−w`. No linear algebra survives: deciding a case is a digit comparison. From this the short-atom bound follows in closed form at every prime — generically `(3p−1)/2`, about half the Davenport constant, degrading on the residue run `r ∈ [(p+1)/2, p−2]` to at most `2p−2`. The symmetric identity constrains the numbers `N_ℓ` of zero-sum subsequences of each length; on a complement of an atom these numbers are tied in pairs by `N_ℓ = N_{m−ℓ}`, and the identity sees only the pairs. Replacing the symmetric polynomial `e_d` by `x_i·e_d(x_{−i})` breaks that pairing at the cost of one extra unknown per length and one fewer usable degree. We show the trade is favourable exactly when the admissible length window is two-sided: over `C_7^3`, on a zero-sum sequence of length `m ∈ {23,24,27,28,29}` with packing number 2, the symmetric identity yields no atom shorter than `m/2 − 1`, while the pointed identity forces an atom of length at most 10. This single statement replaces three separately-sourced inputs in the previous derivation and halves both length corridors of the `p = 7` analysis.

The bound needs no hypothesis on the packing number — only that a proper zero-sum and its complement each contain an atom — so the same machine runs at every `k`. At `k = 4` it yields new structure for an open question: a length-31 obstruction over `C_5^3`, the object that decides `D_4(C_5^3) ∈ {30,31}` and with it the conjectured line at `p = 5`, must factor into four atoms of lengths `(6,6,6,13)`, `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)` or `(7,7,7,10)` — five profiles where previously only a minimum atom length was known.

We then run the whole apparatus uniformly in `p`. Calling `L ∈ [p+1, 3p−2]` *special* when `p | L` or `p | (N−L)`, where `N = (11p−3)/2`, there are exactly three special lengths for every prime, `3(p−1)/2`, `2p` and `(5p−3)/2`; equivalently their base-`p` low digit is `0` or `(p−3)/2`, which is what makes Lucas' theorem collapse either their own column or their complement's. For every prime `5 ≤ p ≤ 31` we verify that excluding any two special lengths makes the spectrum congruences inconsistent, so a `D_3` obstruction must carry atoms of at least two of the three; for `11 ≤ p ≤ 19` these three pairs are exactly the minimal forced sets. We state this as a verified finite computation, not a theorem for all `p`: the contradiction uses essentially every degree in `[p+2, (5p+1)/2]`, so no short certificate exists and a uniform proof needs a rank argument we do not have.

**Keywords.** generalized Davenport constants; zero-sum sequences; elementary abelian groups; polynomial method; Chevalley–Warning; Lucas' theorem.

---

## 1. Introduction

Zero-sum problems ask how long a sequence over a finite abelian group must be before a prescribed combinatorial pattern of zero sums is unavoidable. The Davenport constant `D(G)` — the shortest length forcing one nonempty zero-sum subsequence — is classical, and Olson determined it for elementary abelian groups: `D(C_p^r) = r(p−1)+1`. The generalized constants `D_k(G)`, forcing `k` pairwise *disjoint* zero sums, are far less tractable. Rank two is well understood; rank three is where the expected arithmetic progression can fail, and where individual values are still being decided one at a time.

For `G = C_p^3` the expected line is `D_k(C_p^3) = ((2k+5)p−5)/2`. Its `k = 2` and `k = 3` cases read `(9p−5)/2` and `(11p−5)/2`. At `p = 5` these are `20` and `25`, both known; at `p = 7` they are `29` and `36`, and `36` is the first value of the line that had not been settled.

**The bottleneck.** The standard route to an upper bound is the polynomial method: for a zero-sum sequence `T` of length `n` over `C_p^r` and a multilinear `h` of degree at most `n − D(G)`, the Chevalley–Warning argument gives

> **(C)**  `Σ_{I ⊆ [n], σ(I) = 0} (−1)^{|I|} h(1_I) ≡ 0 (mod p)`.

Taking `h = e_d` turns this into linear congruences on the counts `N_ℓ` of zero-sum index sets of each size, and inconsistency of the resulting system rules out length spectra. The bottleneck is that this system is weak exactly where the analysis needs it most. In the `p = 7` problem one must control a zero-sum sequence `C` of length 28 with packing number 2; the symmetric congruences yield only "some atom has length `≤ 14`", which is vacuous, where "`≤ 10`" is what the corridor argument needs. Previous work closed that gap by importing three separate external statements (two applications of a short-subsequence lemma and one instance of `s_{≤12}(C_7^3) = 26`), and an in-repository audit had recorded, correctly for the regime it examined, that pointing the polynomial "buys nothing".

**The move.** That audit examined a *one-sided* window: forbidding short zero sums, `N_ℓ = 0` for `ℓ ≤ w`, at the obstruction length itself. There the pointed and symmetric thresholds coincide. The situation on a complement is different in a way that turns out to be decisive. If `C` is zero-sum with packing number 2, every proper nonempty zero-sum subsequence of `C` is an atom and so is its complement, so the admissible lengths form a *two-sided* window `[w+1, m−w−1]` closed under `ℓ ↦ m−ℓ`. Complementation then forces `N_ℓ = N_{m−ℓ}`, and the symmetric identity can only ever see those sums: it has half as many unknowns, but correspondingly degenerate equations. The pointed polynomial `h = x_i · e_d(x_{−i})` counts only zero-sum sets through a fixed index `i`, and complementation does not identify `M_ℓ` with `M_{m−ℓ}`. The extra equations more than pay for the extra unknowns.

**What follows.** §5 proves the resulting bound in the form we need: over `C_7^3`, every zero-sum sequence of length `m ∈ [23,29]` with packing number 2 has an atom of length at most 10 — one statement, uniform in `m`, replacing the three imported ones, and strictly stronger than the previous best at `m = 28`. §6 assembles `D_3(C_7^3) = 36`. §7 runs the apparatus at every prime and isolates the three special lengths. §8 says plainly what is proved, what is verified over a finite range, and what is open.

**Contributions.**

1. `D_2(C_p^3) = (9p−5)/2` for every prime `p ≥ 5`, self-contained given Olson (§4).
2. An exact digit criterion for the pointed system (Theorem G, §5.5): inconsistency holds iff some `d ∈ [m−2w−1, m−3p+1]` is base-`p` digit-dominated by `m−1−w`. This removes linear algebra from the method and makes the short-atom bound a theorem at every prime rather than a per-prime computation.
2b. The resulting short-atom bound in closed form — generic value `(3p−1)/2`, about half the Davenport constant — which at `p = 7` removes three external inputs and halves both length corridors (§5).
3. `D_3(C_7^3) = 36`, with Olson as the only external input (§6).
3b. A four-atom corridor of five length profiles for the length-31 obstruction over `C_5^3`, constraining the open `D_4(C_5^3) ∈ {30,31}` (§6.5).
4. A uniform-in-`p` identification of three *special* atom lengths, with the Lucas mechanism that explains them, verified for `5 ≤ p ≤ 31` (§7).
5. A correction to the record: pointed congruences do add strength, in the two-sided regime specifically (§5.3).

---

## 2. Setting, notation, and terminology

We fix the following canonical forms and use them throughout.

| Term | Definition |
|---|---|
| sequence | a finite multiset over `G`; `\|S\|` is its length |
| `σ(S)` | the sum of the terms of `S` |
| zero-sum / block | a sequence with `σ = 0` |
| atom | a nonempty zero-sum sequence with no proper nonempty zero-sum subsequence (a minimal zero-sum sequence) |
| `D(G)` | Davenport constant; `D(C_p^r) = r(p−1)+1` (Olson) |
| `D_k(G)` | least `ℓ` forcing `k` pairwise disjoint nonempty zero-sum subsequences |
| `z(S)` | packing number: the largest number of pairwise disjoint nonempty zero-sum subsequences of `S` |
| obstruction | for the `D_3` problem over `C_p^3`: a zero-sum `T` with `\|T\| = N` and `z(T) = 3` (see §2.1) |
| `N` | `(11p−3)/2`; at `p = 7`, `N = 37` |
| `D` | `3p−2`; at `p = 7`, `D = 19` |
| `amin` | `p+1`, the minimum atom length in an obstruction |
| `w(S)` | the multinomial weight `Π_g C(v_g(T), v_g(S))` of a sub-multiset `S` of `T` |
| `N_ℓ`, `M_ℓ` | weighted counts of zero-sum sub-multisets of length `ℓ`; `M_ℓ` counts only those through a fixed index |
| special length | `L ∈ [amin, D]` with `p \| L` or `p \| (N−L)` (§7) |

`C(a,b)` denotes a binomial coefficient. Base-`p` digits are written `(a_1, a_0)_p`.

### 2.1 The reduction to a zero-sum object

`D_3(C_p^3) > (11p−5)/2` means there is a sequence `S` of length `(11p−5)/2` with `z(S) ≤ 2`. Appending `−σ(S)` gives a zero-sum `T` of length `N = (11p−3)/2` with `z(T) = 3`. So a proof of `D_3(C_p^3) = (11p−5)/2` amounts to showing no such `T` exists, given the matching lower bound. The lower bound is supplied by an explicit family (`T_k(n)`, §4.3) and needs no external input.

Two reductions are uniform in `p` and used throughout.

**Lemma 2.1 (no short zero sums).** An obstruction `T` has no zero-sum subsequence of length `≤ p`.

*Proof.* If `U ⊆ T` is zero-sum with `|U| ≤ p`, then `|T U^{−1}| ≥ N − p = D_2 + 1`. Delete an element `x` from `T U^{−1}`; the remaining `≥ D_2` terms contain two disjoint blocks `V, W`, and `R = T(UVW)^{−1} ∋ x` is a fourth block, contradicting `z(T) = 3`. ∎

**Lemma 2.2 (multiplicities).** Every element of `T` has multiplicity `≤ p−1`.

*Proof.* If `v^p | T` then `|T v^{−p}| = N − p = D_2 + 1`, and the same deletion argument produces a fourth block. ∎

Both proofs consume `D_2(C_p^3) = (9p−5)/2`, which §4 supplies.

---

## 3. The two counting identities

Let `T` be zero-sum over `C_p^r` with `|T| = n` and let `h` be multilinear of degree `≤ n − D(G)`. The Chevalley–Warning argument gives **(C)** above. Two choices of `h` are used.

**Symmetric form.** `h = e_d`, `deg h = d ≤ n − D`, and `h(1_I) = C(|I|, d)`. Then

> **(S)**  `Σ_ℓ (−1)^ℓ N_ℓ C(ℓ, d) ≡ 0 (mod p)`,  `0 ≤ d ≤ n − D`.

**Pointed form.** Fix an index `i` and take `h = x_i · e_d(x_{−i})`, so `deg h = d+1 ≤ n − D`, i.e. `d ≤ n − D − 1`, and `h(1_I) = [i ∈ I]·C(|I|−1, d)`. Then

> **(P)**  `Σ_ℓ (−1)^ℓ M_ℓ C(ℓ−1, d) ≡ 0 (mod p)`,  `0 ≤ d ≤ n − D − 1`,

where `M_ℓ` counts zero-sum index sets of size `ℓ` containing `i`.

The pointed form costs one degree and, on a two-sided window, doubles the unknowns; it gains the loss of the symmetry `ℓ ↦ n−ℓ`. §5 shows when the gain wins.

Both identities, and the sharpness of both degree bounds, are verified by brute-force enumeration over `C_3^3` (§9).

---

## 4. `D_2(C_p^3) = (9p−5)/2` for every prime `p ≥ 5`

### 4.1 Statement

> **Theorem A.** For every prime `p ≥ 5`, `D_2(C_p^3) = (9p−5)/2`.

The value is not new — it is available in the literature for `p = 5` and by a short-subsequence lemma in general — but the proof below is self-contained given Olson, which matters here because every later reduction in this paper consumes `D_2` and we do not wish to import it.

### 4.2 Upper bound

Suppose `T` is zero-sum over `C_p^3`, `|T| = (9p−3)/2`, with `z(T) = 2`. Atoms of `T` then have lengths in the window `I = [(3p+1)/2, 3p−2]`. Applying **(S)** and splitting the resulting system by base-`p` digit:

- at digit level 0, Lucas gives `A_r ≡ 0` for every residue `r`;
- at level 1, the surviving vector `B` is orthogonal to every polynomial of degree `≤ (p+1)/2` while `|supp B| ≤ (p+1)/2`, hence `B ≡ 0`;
- but `B_0 = 2N_{2p} ≡ −2 ≢ 0`.

The contradiction gives the upper bound. The argument degenerates at `p = 3` exactly because `(p−3)/2 = 0` collides with residue `0`, which is why the theorem starts at `p = 5`.

The three bullets above are a summary; the digit-level argument is carried out in full in `D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md`, and `tools/d2_digit_certificate_v3.py` re-checks its structural steps for all 44 primes `5 ≤ p ≤ 200`. A referee should read that record, not this paragraph, as the proof.

### 4.3 Lower bound

For odd `n ≥ 3` and `k ≥ 2` set, in the basis `e_1,e_2,e_3` with `e_{ij} = e_i + e_j`,

`T_k(n) = e_1^{(k−1)n−1} · e_2^{n−1} · e_3^{n−1} · e_12^{(n+1)/2} · e_13^{(n−1)/2} · e_23^{(n−1)/2}`,

of length `((2k+5)n − 7)/2`.

> **Lemma A′.** `z(T_k(n)) = k−1` for every odd `n ≥ 3` and every `k ≥ 2`. Hence `D_k(C_n^3) ≥ ((2k+5)n−5)/2`.

*Proof sketch.* Write `c_j` for the `j`-th coordinate sum: `c_1 = kn−1`, `c_2 = 2n−1`, `c_3 = 2n−2`. For `≥`: the `k−2` blocks `e_1^n` together with `e_1^{(n−1)/2} e_2^{(n−1)/2} e_12^{(n+1)/2}` are `k−1` disjoint blocks. For `≤`: every block has each `c_j` a multiple of `n`; since `c_2, c_3 < 2n`, at most one block meets `c_2` and at most one meets `c_3`, so at most two blocks are non-unary (a *unary* block is a power of `e_1`), and counting the `c_1`-budget `kn−1` against the `n` each non-unary block consumes bounds the total by `k−1` in each case. ∎

Only oddness of `n` is used, not primality. The `k = 2` case gives `D_2(C_p^3) ≥ (9p−5)/2`. The full case analysis is in `GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md`, and `verify_tk_family_v3.py` recomputes `z(T_k(n))` exactly for `n ∈ {3,5,7}`, `k ≤ 6`. ∎

---

## 5. The pointed short-atom bound

### 5.1 Statement

> **Proposition B.** Let `p ≥ 5` be prime and let `C` be zero-sum over `C_p^3` with `3p−2 < |C| = m ≤ (11p−3)/2`, every atom of length `≥ p+1`. Write `r = m mod p` and `h = (p−1)/2`. Then `C` has an atom of length at most
>
> `w(p,m) = (3p−1)/2` if `r ≤ h` or `r = p−1`;  `(3p−1)/2 + r − h` if `h+1 ≤ r ≤ p−2`.
>
> In particular at `p = 7` the bound is 10 for `m ∈ {23,24,27,28,29}` (and 11, 12 at `m = 25, 26`).

This is a corollary of the digit criterion of §5.5, so it holds at every prime; the closed form above is the bookkeeping carried out on the range `m ≤ (11p−3)/2` that the applications use.

Before this, the available bounds at `p = 7` were `≤ 10` for `|C| ∈ {27,29}` (from the symmetric congruences), `≤ 12` for `|C| = 28` (from a specialization of `s_{≤12}(C_7^3) = 26`), and nothing at all for `|C| ∈ {23,24}`. The generic value `(3p−1)/2` is roughly `D/2`, and the exceptional residues raise it to at most `2p−2`.

### 5.2 Proof

Since `z(C) = 2`, every proper nonempty zero-sum subsequence of `C` is an atom and so is its complement. So if every atom had length `≥ 11`, the proper zero-sum lengths would lie in the two-sided window `S = [11, |C| − 11]`. Apply **(P)** with `d ≤ |C| − 20`. The zero-sum index sets containing `i` are those of lengths in `S` together with `C` itself, so for every admissible `d`

`Σ_{ℓ ∈ S} (−1)^ℓ M_ℓ C(ℓ−1, d) + (−1)^{|C|} C(|C|−1, d) ≡ 0 (mod 7)`.

For each `|C| ∈ {23,24,27,28,29}` this system is inconsistent over `F_7`; the general statement follows the same route at every prime. ∎

**The case `|C| = 28` by hand.** Unknowns `M_11 … M_17`, degrees `d ≤ 8`. Six equations suffice:

| `d` | equation `(mod 7)` |
|---|---|
| 6 | `M_14 ≡ 6` |
| 5 | `−M_13 − M_14 ≡ 1` |
| 4 | `M_12 + 2M_13 + M_14 ≡ 6` |
| 3 | `−M_11 − 3M_12 − 3M_13 − M_14 ≡ 1` |
| 0 | `−M_11 + M_12 − M_13 + M_14 − M_15 + M_16 − M_17 ≡ 6` |
| 7 | `−M_11 + M_12 − M_13 + M_14 − 2M_15 + 2M_16 − 2M_17 ≡ 4` |

From `d = 6`, `M_14 ≡ 6`; then `d = 5` gives `−M_13 ≡ 7 ≡ 0`, so `M_13 ≡ 0`; then `d = 4` gives `M_12 ≡ 0`; then `d = 3` gives `M_11 ≡ 0`. Substituting into `d = 0` leaves `−M_15 + M_16 − M_17 ≡ 0`, and `d = 7` then reads `6 − 2·0 = 6 ≢ 4 (mod 7)`. ∎

The rigidity is a Lucas phenomenon: `13 = (1,6)_7` and `14 = (2,0)_7` make the top-degree columns nearly empty, so the equations peel unknowns off one at a time from `d = 6` downwards.

### 5.5 The criterion: from linear algebra to digits

Everything above decides a linear system over `F_p`. It need not.

> **Theorem G.** Let `p ≥ 5` be prime, `D = 3p−2`, `m > D`, `w ≥ p`. The pointed system on the window `S = [w+1, m−w−1]` is inconsistent over `F_p` **iff** some integer `d` with `m − 2w − 1 ≤ d ≤ m − 3p + 1` has all base-`p` digits dominated by the corresponding digits of `m − 1 − w`.

*Proof.* Write `dmax = m − D − 1`. By Fredholm the system is inconsistent iff some `λ` kills the columns and not the right-hand side. Put `P(y) = Σ_d λ_d C(y,d)`, an integer-valued function. Killing the columns says `P(l−1) = 0` for every `l ∈ S`; for `w ≥ p` the set `{l−1 : l ∈ S}` is the integer interval `[w, m−w−2]`, of size `L = m−2w−1`. Not killing the right-hand side says `P(m−1) ≠ 0`.

Rewrite `P` about the left end by Newton's forward-difference formula, `P(y) = Σ_d μ_d C(y−w,d)` with `μ_d = (Δ^d P)(w)` — a bijection on coefficients, under which `λ_e = 0` for `e > dmax` corresponds to `μ_d = 0` for `d > dmax`. Since `C(j,d) = 0` for `j < d`, vanishing on `[w, w+L−1]` is *exactly* `μ_0 = ⋯ = μ_{L−1} = 0`. So the admissible `P` are `Σ_{d=L}^{dmax} μ_d C(y−w,d)` with `μ` free, and

`P(m−1) = Σ_{d=L}^{dmax} μ_d C(m−1−w, d)`.

Such a `P` with `P(m−1) ≠ 0` exists iff `C(m−1−w, d) ≢ 0` for some `d ∈ [L, dmax]`; Lucas turns that into the digit condition. ∎

Three consequences. Deciding a case is now a digit comparison rather than an elimination, at any prime and any length. The closed form of Proposition B follows by digit bookkeeping — the generic value `(3p−1)/2` and the exceptional run `r ∈ [(p+1)/2, p−2]` record when the interval `[m−2w−1, m−3p+1]` first catches a digit-dominated integer — and the periodicity in `m mod p` is immediate, since the digit condition sees only residues and carries. Finally the hand-proof of §5.2 is demystified: the peeling `d = 6 ⇒ M_14`, `d = 5 ⇒ M_13`, … is the triangular unwinding of the Newton step, one coefficient at a time.

### 5.3 Why pointing is what buys this — and a correction

An earlier record in this programme states that at the obstruction length `N = 37` the pointed congruences reproduce *exactly* the symmetric threshold, and concludes that pointing buys nothing. That statement is correct for the regime it examines: a **one-sided** window `[1,w]`, where the pairing `ℓ ↦ N−ℓ` does not act on the forbidden set.

On a complement the window is **two-sided** and complementation identifies `ℓ` with `|C|−ℓ`. The symmetric identity then sees only the sums `N_ℓ = N_{|C|−ℓ}`. Pointing breaks the pairing. The separation is direct and we record it as a control: at `|C| = 28` the symmetric system remains feasible even at `w = 13`, while the pointed system is already infeasible at `w = 10`.

The transferable rule: **point the polynomial exactly when the admissible window is two-sided.** A symmetry that appears to be helping — halving the unknown count — is in fact collapsing the information, and deliberately breaking it re-opens the problem.

### 5.4 Consequences: both corridors halve

Let `A` be a shortest atom of an obstruction `T` at `p = 7`, `|A| = s ∈ {8,9,10}`, and `C = T A^{−1}`. By Proposition B, `C` has an atom `E` with `|E| ≤ 10`; and `F = C E^{−1}` is an atom, since otherwise `A`, `E` and two blocks of `F` are four disjoint blocks. As `A` is shortest, `|E| ≥ s`. Hence:

> **First corridor.** Every obstruction has a three-atom factorization of type `(8,10,19)`, `(9,9,19)`, `(9,10,18)` or `(10,10,17)`.

This eliminates `(9,11,17)` and `(9,12,16)` from the previous list of six, by congruence alone and with no search, and it replaces three external inputs by one internal statement.

The spectrum congruences (§7, at `p = 7`) force an atom `B` with `|B| ∈ {13,14}`. Applying Proposition B to `C = T B^{−1}`, of length 24 or 23 — lengths at which no short-atom bound had previously been available — and excluding profiles containing an 8 as before:

> **Second corridor.** Every obstruction also has a three-atom factorization of type `(9,13,15)`, `(9,14,14)` or `(10,13,14)`.

This eliminates `(11,12,14)`, `(11,13,13)` and `(12,12,13)` — precisely the three "flat" profiles that carry no near-maximal atom and were the hardest for geometric methods to reach.

---

## 6. `D_3(C_7^3) = 36`

> **Theorem C.** `D_3(C_7^3) = 36`. The only external input is Olson's `D(C_p^r) = r(p−1)+1`.

The lower bound is `T_3(7)` (§4.3). For the upper bound, suppose an obstruction `T` exists: zero-sum, `|T| = 37`, `z(T) = 3`. Then:

1. multiplicities are `≤ 6` and `T` has no zero-sum of length `≤ 7` (Lemmas 2.1, 2.2, on `D_2(C_7^3) = 29` from Theorem A);
2. the zero-sum sub-multisets of `T` are exactly `∅`, `T`, the atoms, and the complements of atoms, overlapping only at lengths 18 and 19; this yields 19 congruences over `F_7` in `W_8, …, W_19`, whose solution has `W_13 = 2s` and `W_14 = 1−s`, so **every obstruction has an atom of length 13 or 14**;
3. the shortest atom has length in `{8,9,10}`, and Proposition B gives the first corridor (§5.4);
4. the forced 13- or 14-atom gives the second corridor (§5.4);
5. the feasible length spectra are enumerated; closure under the corridors and the complement systems leaves a finite list, and every member is eliminated.

Steps 1–5 are reproduced end to end by a single program (§9), which asserts each step and prints the conclusion. ∎

**Where the weight of this proof sits.** Steps 1–4 are human-checkable arguments, and step 3 is now a corollary of Theorem G. Step 5 is a finite computation: an enumeration of spectra followed by an elimination of the survivors. It is the step a referee should press hardest, and it is the one place in this paper where a single implementation carries a load-bearing claim. We state that plainly rather than let the end-to-end checker's `PASS` imply more than it does. Step 5 has since been **double-implemented**: a C program recomputes it from the mathematical statement using Pascal's triangle mod 7 rather than exact binomials, the dual (Fredholm) consistency test of §5.5 rather than primal elimination, and bitmask enumeration rather than Python combinations. It reproduces the recorded figures exactly — 548 feasible spectra, 8 after the closure and corridor cut, all 8 eliminated — and, fed the tightened corridor of §5.4, leaves 5 and eliminates all 5. That removes ordinary implementation-error risk. It does not remove *systematic* risk, since both programs were written by the same author from the same understanding: step 5 is double-implemented, not independently verified, and third-party review of it remains a submission prerequisite (§9).

**Relation to the corridor literature.** A parallel line of work classifies the three-atom factorizations that contain a *maximal* atom, prime-uniformly, as `(p+j, p+(p+1)/2−j, 3p−2)` for `1 ≤ j ≤ ⌊(p+1)/4⌋`. At `p = 7` that is `(8,10,19)` and `(9,9,19)`. Proposition B recovers those two and adds the triples with no maximal atom, `(9,10,18)` and `(10,10,17)`; at `p = 11` it gives nine triples of which that classification supplies three. The two results are complementary: the maximal-atom branch carries a support classification that the others do not.

### 6.5 The method at `k = 4`: a corridor for `D_4(C_5^3)`

Proposition B was stated for `z(C) = 2`, where every proper zero-sum is an atom. That hypothesis is not needed, and dropping it is what lets the method leave `k = 3`.

> **Lemma E.** Let `C` be zero-sum over `C_p^3` with `|C| = m` and suppose every atom of `C` has length `≥ w+1`. Then every proper nonempty zero-sum subsequence of `C` has length in `[w+1, m−w−1]`.

*Proof.* A proper nonempty zero-sum `B` contains an atom, so `|B| ≥ w+1`; its complement `C B^{−1}` is zero-sum and nonempty, so it contains an atom too, giving `m − |B| ≥ w+1`. ∎

No packing number appears, so the window is two-sided at every `k`, and **(P)** applies. At `p = 5` (`D = 13`) the resulting table is uniform: every zero-sum sequence over `C_5^3` of length `m ∈ [14,31]` has an atom of length `≤ 8`, and of length `≤ 7` unless `m ≡ 4 (mod 5)`.

`D_4(C_5^3) ∈ {30,31}` is open, and the value 31 would falsify the conjectured line at `p = 5`. The `= 31` branch requires a zero-sum `T` over `C_5^3` with `|T| = 31` and no five pairwise disjoint blocks; its atoms have length in `[6,13]`, and until now nothing further was known about how the 31 terms distribute across atoms. Peeling a shortest atom and then two more by the table, and observing that the fourth part must itself be an atom — a split would give five disjoint blocks — gives:

> **Theorem F.** A length-31 obstruction over `C_5^3` factors into four atoms whose lengths are one of `(6,6,6,13)`, `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)`, `(7,7,7,10)`.

In particular `T` has at least three atoms of length `≤ 8`. `(6,6,6,13)` is the only profile carrying a maximal atom, so maximal-atom support classifications reach it and no other; `(6,7,8,10)` and `(7,7,7,10)` are flat, and are exactly the profiles such methods do not reach — the same shape of difficulty as at `p = 7`. Theorem F does not decide `D_4(C_5^3)` and excludes none of the five profiles; it turns an unstructured 31-term search into five constrained completion problems, orthogonal to the support-based evidence already available for this object.

---

## 7. Uniform structure at a general prime

### 7.1 The spectrum system, uniformly in `p`

With `N = (11p−3)/2`, `D = 3p−2`, `amin = p+1`, the zero-sum sub-multisets of an obstruction are `∅`, `T`, the atoms (lengths in `[amin, D]`) and the complements of atoms; a multiset that is both has length in `[N−D, D]`. Writing `W_L` for the weighted atom count and `X_L` for the weighted count of the doubly-counted ones, **(S)** gives for `0 ≤ d ≤ N−D`

> **(S`_p`)**  `C(0,d) + (−1)^N C(N,d) + Σ_L (−1)^L W_L [C(L,d) + (−1)^N C(N−L,d)] − Σ_{L ∈ [N−D,D]} (−1)^L X_L C(L,d) ≡ 0`.

`N` changes parity with `p` (`37` odd, `26` and `70` even), so the sign must be carried rather than specialized.

### 7.2 The three special lengths

> **Definition.** `L ∈ [amin, D]` is *special* when `p | L` or `p | (N−L)`.

There are exactly three for every prime `p ≥ 5`:

| special `L` | base `p` | complement | base `p` |
|---|---|---|---|
| `3(p−1)/2` | `(1, (p−3)/2)` | `4p` | `(4,0)` |
| `2p` | `(2, 0)` | `(7p−3)/2` | `(3, (p−3)/2)` |
| `(5p−3)/2` | `(2, (p−3)/2)` | `3p` | `(3,0)` |

At `p = 7` these are `9, 14, 16`; at `p = 11`, `15, 22, 26`; at `p = 13`, `18, 26, 31`. Since `N = (5, (p−3)/2)_p`, a length is special exactly when its base-`p` low digit is `0` or `(p−3)/2` — the condition under which Lucas collapses either its own column or its complement's. This is the same mechanism that makes `14 = (2,0)_7` the pivot of the `|C| = 28` argument in §5.2, now identified as prime-independent rather than an accident of `p = 7`.

### 7.3 The verified statement

> **Observation D (verified for every prime `5 ≤ p ≤ 31`).** In `(S_p)`: the unrestricted system is consistent; forbidding **any two** special lengths makes it inconsistent; and for `11 ≤ p ≤ 19` those three pairs are the **only** minimal inconsistent length sets of size `≤ 2`. Consequently every obstruction carries atoms of at least two of `3(p−1)/2`, `2p`, `(5p−3)/2`.

The two smallest primes are richer, not weaker: at `p = 5` and `p = 7` there are 18 minimal forced pairs, the three special ones among them. At `p = 7` the extra ones include `{13,14}`, the pair on which §6 step 2 rests. So the uniform statement is a floor that small primes exceed.

We deliberately do **not** state Observation D as a theorem for all `p`. The duality of §5.5 applies here too, and identifies the obstacle precisely: the spectrum system dualises to *find an integer-valued `P` vanishing on the interval `[N−D, D]`, satisfying `P(L) = −(−1)^N P(N−L)` for every `L ∈ [p+1, N−D−1]`, with `P(0) + (−1)^N P(N) ≠ 0`.* Unlike the pointed case, this is a functional equation and not a plain interval-vanishing condition, so the Newton step does not finish it. Greedy minimization is consistent with that: the contradiction uses essentially every degree in `[p+2, (5p+1)/2]`, so no short certificate exists. The dual certificates are dense, though their right-hand sides sit in the constant ratio `4 : 2 : 3 (mod p)` across the three pairs at every prime tested. That functional equation now has a name and a shape. Setting `Q(y) = P(y) + (−1)^N P(N−y)`, one checks (for every prime and special pair tested) that `P` vanishes on the whole **integer interval** `[N−D, D]` — of length `2D − N + 1 = (p−3)/2`, exactly the low base-`p` digit of `N = (5,(p−3)/2)_p`, so the Newton step of §5.5 applies to it — that `Q(N−y) = (−1)^N Q(y)`, and that `Q` vanishes on the entire atom range **except at the two excluded lengths, where it is nonzero at both**, and at `0`. So:

> "the pair `Z` is forced" says exactly that the `(−1)^N`-antisymmetry of the spectrum can be broken at the two lengths of `Z` and at `0`, and nowhere else on the atom range.

That is the structural reason the special lengths are special, and it explains why the dual certificates looked dense: the density is an artefact of examining `P` rather than `Q`. What remains is to construct such a `Q` for a special pair, and to show none exists for any other pair or any single length — questions about one explicitly described symmetric function rather than about a matrix rank.

---

## 8. Discussion and boundaries

**What is proved.** Theorem A (`D_2(C_p^3)` for all primes `p ≥ 5`), Theorem G and its corollary Proposition B, Theorem C (`D_3(C_7^3) = 36`), Lemma E and Theorem F. Olson's theorem is the only external mathematical input to any of them.

**What is verified over a finite range.** Observation D, for `5 ≤ p ≤ 31` (minimality for `p ≤ 19`). We claim no more, and specifically not that the pattern continues. §7.3 now states the exact functional equation whose solution would close it.

**What is open.** `D_4(C_5^3) ∈ {30,31}`, now narrowed to five length profiles (§6.5) but not decided; it settles the conjectured line at `p = 5`. And `D_3(C_p^3)` for `p ≥ 11`. The distance is honest and large: the first corridor has nine triples at `p = 11` against four at `p = 7`, and the support classifications that close individual `p = 7` branches have no general-`p` analogue yet. Narrowing the target is not hitting it.

**Method transfer.** The rule isolated in §5.3 — point the polynomial when the window is two-sided — is not specific to Davenport constants. It applies wherever a counting identity is applied to an object whose admissible configurations are closed under complementation, since that is exactly when the symmetric identity is silently halving its own information.

**Prior-art position.** This paper is `D_2` for all primes and `D_3` at `p = 7`, unconditional. It is complementary to, not a strengthening of, the conditional `C_5^3` analysis that settles `D_4(C_5^3)` to one bit under two hypotheses. Theorem A does discharge, for every prime, a `D_2` premise that several reductions in that line assume on the strength of an external lemma, and Theorem F adds atom-length structure to the branch that analysis develops.

---

## 9. Verification, reproducibility, and data availability

Every claim above is backed by a checker in `research/experiments/davenport-c7-frontier/`. Each is designed so that a real object must survive it, and each carries a non-vacuity control.

| Claim | Checker | Controls |
|---|---|---|
| identities **(C)**, **(S)**, **(P)** | `verify_short_atom_bound_v4.py` step 1 | brute force over `C_3^3`; both degree bounds shown sharp by exhibiting failure one degree higher |
| Theorem A | `tools/d2_digit_certificate_v3.py` | structural steps re-checked for all 44 primes `5 ≤ p ≤ 200` |
| Theorem G | `verify_lucas_criterion_v5.py` | Lucas and Newton steps checked separately; the criterion checked against Gaussian elimination on all 2,916 `(p,m,w)` cases across six primes, 0 disagreements; the closed form re-derived from the criterion with no linear algebra |
| Proposition B | `verify_short_atom_law_v5.py`, `verify_short_atom_bound_v4.py` steps 2–4 | every system decided **twice**, by Gaussian elimination over `F_7` and by exhaustive search over all `7^{\|S\|}` assignments, required to agree; `w = 9` shown feasible so the bound is not vacuous; symmetric system shown feasible at `w = 13` to isolate the gain to pointing |
| corridors | `verify_short_atom_bound_v4.py` step 5 | exact triple and profile lists asserted |
| Theorem C | `verify_D3_C7_end_to_end_v3.py` | 8 asserted steps; a real packing-3 object over `C_5^3` (144 zero-sum multisets) must satisfy every congruence, and does, exactly |
| Theorem F | `verify_d4_c5_corridor_v4.py` | all 18 bounds decided by Gaussian elimination, 12 cross-checked by exhaustive search; `w−1` feasible at every length; a real `z = 3` object over `C_5^3` satisfies the predicted bound on all 57 of its zero-sum subsequences of length `≥ 14` |
| Observation D | `verify_general_spectrum_v4.py` | agreement with the independently written `p = 7` checker on **all 298** length subsets of size `≤ 3`; conclusion unchanged under the alternative modelling `X_L = X_{N−L}`; unrestricted system shown consistent at every prime |

**Independent-replication status.** The `(8,10,19)` corridor companion counts (`0/24/538`) were reproduced by a separately written program from the predicate alone, matching a parallel lane's counts exactly. The remaining checks are single-implementation but double-method where a second decision procedure exists, as noted above.

**Outstanding.** (i) *Prior-art verification.* A literature **search** has been run (`EXTERNAL_PRIOR_ART_V5.md`): the references are identified, the nearest prior work is located and lies on a disjoint family of groups, and nothing found asserts our results. But the host blocks page fetching, so **no primary text has been read** and every attribution is unverified. A person with library access must confirm the reference list and answer two questions — is `D_3(C_7^3)` known, and is a short-atom bound near `D/2` for `C_p^3` known. No priority claim should be read into this draft until then. (ii) *Independent mathematical review* of Theorem C, in particular the step-5 enumeration (§6). (iii) *Third-party review of the step-5 enumeration.* It is now double-implemented (`D3_STEP5_SECOND_IMPLEMENTATION_V5.md`) — two programs in different languages, with different arithmetic and different decision procedures, agreeing exactly — which retires implementation-error risk but not systematic risk, both having the same author. All three remain prerequisites for submission.

---

## References

Identified by literature search; **none has been read**, because the authoring host permits search but blocks page fetching (`WebFetch` returns `EGRESS_BLOCKED` for every domain tried). Attributions are therefore unverified against the primary text — see §9 and `EXTERNAL_PRIOR_ART_V5.md`.

1. J. E. Olson, *A combinatorial problem on finite abelian groups*, J. Number Theory (1969). — `D(C_p^r) = r(p−1)+1`, the only external input used here.
2. M. Freeze, W. A. Schmid, *Remarks on a generalization of the Davenport constant*, arXiv:0905.4248. — `D_k(G) = D_0(G) + k·exp(G)` for large `k`.
3. Y. Fan, W. Gao, G. Wang, Q. Zhong, J. Zhuang, *On short zero-sum subsequences of zero-sum sequences*, Electron. J. Combin. **19**(3) (2012) #P31; arXiv:1108.2866.
4. B. Girard, W. A. Schmid, *Direct zero-sum problems for certain groups of rank three*, J. Number Theory **197** (2019) 297–316; arXiv:1806.07636.
5. B. Girard, W. A. Schmid, *Inverse zero-sum problems for certain groups of rank three*, Acta Math. Hungar. (2019); arXiv:1809.03178.

**Positioning.** Reference 4 is the nearest prior work: rank three, multiwise Davenport constants. It treats `G ≃ C_2 ⊕ C_{n_2} ⊕ C_{n_3}` with `2 | n_2 | n_3` — rank-three groups of even exponent containing a `C_2` factor — so `C_p^3` with `p` an odd prime is not of that form and the overlap is empty. Multiwise Davenport constants are otherwise reported as settled for elementary `p`-groups of rank at most two and for `C_3^3`; the frequently quoted "known for rank at most three" refers to elementary 2-groups.
