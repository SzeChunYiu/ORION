# An exact packing criterion for generalized Davenport constants of `C_p^r` above rank three

**Author.** Sze Chun Yiu.
**Status.** First draft. Internal machine verification complete; external prior-art pass and independent mathematical review outstanding (see §11).

---

## Abstract

For a finite abelian group `G`, the generalized Davenport constant `D_k(G)` is the least `ℓ` such that every sequence over `G` of length `ℓ` contains `k` pairwise disjoint nonempty zero-sum subsequences. For elementary abelian `G = C_p^r` the constant is understood at ranks one and two, and rank three has recently been settled prime by prime; at rank four and above no exact value appears to have been recorded, and the standard brackets widen with the rank. This paper attacks that regime with two reformulations.

The first is a dictionary. Indexing subsequences by *positions* rather than by group elements identifies the zero-sum subsequences of a sequence with the nonzero **binary** codewords of the kernel of the matrix whose columns are its terms, and identifies disjointness of subsequences with disjointness of supports. The extremal problem becomes: how long can a code of codimension `r` be while its binary support system has no `k` pairwise disjoint members? That system is an intersecting antichain, and — the useful constraint — above the Davenport constant it is **star-free**: if some position lies in every block of a sequence possessing a block, that sequence has length at most `D(C_p^r) = r(p−1)+1`, and this is sharp. The entire star construction is worth exactly `D` and not one term more, which is a structural reason why lower-bound constructions here are irregular.

The second is an exact criterion. On the algebraic family `S = ∏_i e_i^{p−1} · ∏_A v_A^{m_A}` the zero-sum subsequences are indexed by the multiplicity vector of the extra part alone, the rest being forced; two of them are disjoint precisely when their forced parts add with no carry. This gives a biconditional test for the packing condition, and a `k`-fold form covering every `k` at once. It contains the previously used sufficient condition as its one-set case, and because it is an equivalence it also bounds the construction optimum from above — yielding two zero-sum-freeness bounds, a sunflower threshold at exactly `p+1` petals, and a rigidity statement forcing at most one repeated set when `p = 3`.

The consequences are two exact values, `D_2(C_3^4) = 14` and `D_2(C_3^5) = 17`, the first of which repairs the proof of the second; five improved lower bounds at ranks four to seven, each better by one than the load-capped construction gives and each propagating to every `k`; and three brackets of width at most three at ranks four and five.

We close with a closed form, `D_k(C_p^r) = (3/2)·r(p−1) + (k−2)p + 2`, whose constants are forced by the rank-two formula alone and which agrees with every exact value we know, including the four hardest. We do not prove it, and we state the tension against it plainly: the criterion's own optimum, computed exhaustively, falls short of what the closed form requires at three points, and the rank-four shortfall **grows** with the prime. Either the closed form fails above rank three, or the algebraic family class is not extremal there. One cheap computation decides which.

**Keywords.** generalized Davenport constants; zero-sum sequences; elementary abelian groups; intersecting families; linear codes; sunflower-free families.

---

## 1. Introduction

A *sequence* over a finite abelian group `G` is a finite multiset of elements of `G`, repetition allowed. It is *zero-sum* if its elements sum to `0`. The Davenport constant `D(G)` is the least `ℓ` such that every sequence of length `ℓ` has a nonempty zero-sum subsequence; Olson determined it for elementary abelian groups,

    D(C_p^r) = r(p−1) + 1.

The generalized constants `D_k(G)` ask for more: the least `ℓ` forcing `k` **pairwise disjoint** nonempty zero-sum subsequences. Write `z(S)` for the largest number of pairwise disjoint nonempty zero-sum subsequences of `S` — the *packing number* — so that `D_k(G) − 1` is the greatest length of a sequence with `z(S) ≤ k − 1`, and `D_1 = D`.

For `C_p^r` these constants are understood at rank two, where `D_k(C_p^2) = p + kp − 1`. Rank three has been settled one value at a time: `D_2(C_p^3) = (9p−5)/2`, and individual higher-`k` values by dedicated arguments. Rank four is where the subject currently stops. We know of no exact value of `D_k(C_p^r)` recorded for `r ≥ 4` and odd `p`, and the reason is visible in the tools: the polynomial method controls the *length spectrum* of zero-sum subsequences, which is enough to pin the answer when the group is small relative to the spectrum's resolution and progressively less so as `r` grows; while lower bounds come from explicit constructions whose supply of good shapes runs out.

**What makes rank four hard, made precise.** §3 gives a structural answer. Read positionally, the zero-sum subsequences of a sequence are a set system on `[n]`, and when `z(S) ≤ 1` that system is an intersecting antichain. Intersecting families have an obvious extremal shape — the *star*, everything through one fixed element — and stars are exactly what a naive construction produces. Theorem Y says a star is worth precisely `D(C_p^r)` and stops: any sequence with a block, some position of which lies in every block, has length at most `r(p−1)+1`. So every construction beating `D + 1` must live in the star-free regime, where intersecting families stop being easy. That is not a proof of anything about `D_2`, but it explains an experience: the constructions in this subject are irregular because the regular ones are provably worth nothing.

**The criterion.** The known route to lower bounds at general rank fixes a family `F` of subsets of `[r]` and forms

    S = e_1^{p−1} ⋯ e_r^{p−1} · ∏_{A ∈ F} v_A^{m_A},    v_A the indicator of A,     (†)

then shows `z(S) = 1` under two hypotheses: `F` is intersecting, and every coordinate carries load `Σ_{A ∋ i} m_A ≤ p`. Both are sufficient; neither is necessary. §4 replaces them by a condition that is **exactly equivalent** to `z(S) ≤ 1`. The mechanism is arithmetic carrying. Blocks of `(†)` are indexed by the multiplicity vector `b` of the `v`-part, because the `e`-part is then forced to `a_i(b) = ⟨−(Mb)_i⟩`; and two blocks are disjoint exactly when their `e`-parts add without carrying in any coordinate. A coordinate that forces a carry is a *witness*, and Theorem W says `z(S) ≤ 1` iff every admissible pair has one.

Dropping the load cap is what buys the improvements. The rank-five optimum is the six triples through a fixed coordinate; that coordinate carries load `6 = 2p` at `p = 3`, twice the cap, and the family is nevertheless admissible because every split is obstructed by a carry rather than by a small load.

**Both directions.** Because Theorem W is an equivalence and not merely a sufficient condition, it bounds the construction optimum from above as well as below. §5 extracts four such bounds. Two are zero-sum-freeness statements — the extra part `V` can contain no proper zero-sum sub-multiset (Theorem X), and each of its projections `{1_{A∩B}}` must be zero-sum free (Theorem X′) — and they are what make the searches terminate at all. The other two are set-theoretic and of a different flavour: an admissible family contains no sunflower with `p+1` petals, and at `p = 3` at most one of its sets may be repeated. The two families of bounds pull against each other, X′ forcing the sets to be large and sunflower-freeness forbidding them to be large in the same place, and that tension is why the extremal families are heterogeneous.

**Contributions.**

1. **Theorem C** (§3.1), the positional dictionary: blocks of `S` are the nonzero binary codewords of `ker M`, disjointness is disjointness of supports, and `D_k(C_p^r) = 1 + max{n : some `M ∈ F_p^{r×n}` has no `k` pairwise disjoint binary codewords}`. The statement is elementary and we claim it as a translation, not as a discovery; its role is to make the problem statable in the language of the coding-theoretic literature on this invariant.
2. **Theorem Y** (§3.3): a sequence with a block, some position of which meets every block, has length at most `D(C_p^r)`; sharp, with an explicit family attaining it. Hence (Corollary Y1) every witness for `D_2 > D + 1` has atoms with empty common intersection.
3. **Theorem W** (§4.2) and **Theorem W_t** (§4.4), an exact packing criterion for the family `(†)`, valid for every `t` and every `(p,r)`, containing the previously used sufficient condition as the case of one-element pairs.
4. **Theorems X and X′**, **Lemma R** and **Corollaries 4, 4′, 5, 5a** (§5): what the criterion forbids, including a sunflower threshold sharp at `p+1` petals and the monotonicity of the construction optimum in the rank.
5. **`D_2(C_3^4) = 14`** (§6.1), an exact value at rank four, whose upper bound is an exhaustive search with a calibrated enumerator; and the observation that it **repairs** the proof of the next item, whose spanning reduction had cited it before it was available.
6. **`D_2(C_3^5) = 17`** (§6.2), an exact value at rank five.
7. Improved lower bounds at ranks four to seven and their propagation to every `k` (§7), and three brackets of width at most three (§7.2).
8. A **closed form** (§8) matching all 25 known exact values with constants forced at rank two, presented together with the exhaustive computations that contradict its implied construction optimum at three points (§8.3) and with the mechanism that would have explained its critical scale and does not hold (§8.5).
9. Three **negative results** (§9): neither natural uniform family shape achieves the optimum; the two necessary conditions of §5.6 do not characterise admissibility; and the half-budget mechanism that would have explained the closed form's critical scale is refuted by the extremal families themselves. §9.1 additionally reports the one place where this paper found the underlying evidence packet to be wrong, and what survives it.

**What this paper is not.** It contains no proof of a general upper bound at rank four or above. Every rank-`≥ 4` upper bound quoted here is either the trivial `D_2 ≤ 2D`, a finite congruence certificate for one pair `(p,r)`, or an exhaustive search. The closed form of §8 is a conjecture and we argue against it as carefully as for it.

---

## 2. Setting and notation

Throughout `p` is prime and `G = C_p^r` with fixed basis `e_1, …, e_r`; from §4 onwards `p` is odd. We write

- `D = D(G) = r(p−1) + 1` (Olson) and `q = D − 1 = r(p−1)`;
- `⟨x⟩` for the representative of `x mod p` in `{0, 1, …, p−1}`;
- `1_A ∈ {0,1}^r` for the indicator vector of `A ⊆ [r]`.

A *sequence* `S = (g_1, …, g_n)` over `G` is a finite multiset; its *length* is `|S| = n`. A **block** of `S` is a nonempty zero-sum subsequence; an **atom** is a minimal block. Two subsequences are *disjoint* when they use disjoint sets of positions, so repeated group elements occupying different positions may be used independently. The **packing number** `z(S)` is the largest number of pairwise disjoint blocks, and

    D_k(G) = min{ ℓ : every S over G with |S| = ℓ has z(S) ≥ k }.

Two elementary facts are used throughout and we record them once.

**Complement lemma.** If `z(S) ≤ 1` and `A` is a block of `S`, then `S·A^{-1}` is zero-sum free, so `|S| − |A| ≤ D − 1` and every block has length `≥ |S| − q`.

*Proof.* A block of `S·A^{-1}` would be a block disjoint from `A`. ∎

**Monotonicity.** If `T` is a subsequence of `S` then `z(T) ≤ z(S)`, since a block of `T` is a block of `S`. In particular `z(S) ≤ 1` implies `z(T) ≤ 1`, which is what lets an exhaustive search at one length settle all greater lengths.

Combining the complement lemma with Olson's bound on atom length gives the bracket used as a baseline below:

    D + 1  ≤  D_2(C_p^r)  ≤  2D.                                        (2.1)

---

## 3. The positional dictionary and the shape of an extremal family

### 3.1 Theorem C

Let `S = (g_1, …, g_n)` be a sequence over `C_p^r` and let `M ∈ F_p^{r×n}` be the matrix whose `i`-th **column** is `g_i`. Let `C = ker M ⊆ F_p^n`, a linear code of length `n` and codimension at most `r`. Write `𝔅(S)` for the set of supports of the nonzero **binary** vectors of `C` — the codewords all of whose coordinates lie in `{0,1}`.

> **Theorem C.**
> **(a)** The blocks of `S` are exactly the nonzero binary codewords of `C`, matched by support.
> **(b)** Two blocks are disjoint as subsequences precisely when their supports are disjoint; hence `z(S)` is the maximum number of pairwise disjoint members of `𝔅(S)`.
> **(c)** For every `k ≥ 1`,
>
>     D_k(C_p^r) = 1 + max{ n : some M ∈ F_p^{r×n} has no k pairwise disjoint binary codewords }.

*Proof.* A subsequence of `S` is a choice of a set `T` of positions, so it is the `0/1` indicator vector `x_T ∈ F_p^n`, and its sum is `Σ_{i∈T} g_i = M x_T`. Hence `T` is a block iff `x_T ≠ 0` and `M x_T = 0`, that is, iff `x_T` is a nonzero binary codeword; this is (a). Disjointness of subsequences is by definition disjointness of position sets, which is (b). Part (c) is the definition of `D_k` read through (a) and (b). ∎

The content is entirely in the choice of index. Formalisms that index by *multiplicity vectors over the distinct group elements* make the relevant kernel vectors **box-constrained**, with entries in `[0, m_g]`, and the surrounding apparatus becomes conformal decomposition in an affine semigroup. Indexing by *positions* makes them strictly `0/1`. The cost is that repeated elements are no longer collapsed; the gain is that `𝔅(S)` is an ordinary set system, so the vocabulary of extremal set theory applies without translation. §3.2 and §3.3 are what that buys.

**Where cap sets enter.** A binary codeword of weight `w` is a block of length `w`. For `p = 3`, a weight-three binary codeword on distinct columns is a triple of points summing to zero, so a sequence of distinct elements with no weight-three binary codeword is exactly a cap set in `AG(r,3)`. This is the bridge through which cap-set bounds enter the subject.

### 3.2 Blocks form an intersecting antichain

> **Lemma A.** If `z(S) ≤ 1` then no block of `S` properly contains another; equivalently, every block is an atom.

*Proof.* If `A ⊊ B` are blocks then `B \ A` is nonempty and `sum(B\A) = sum(B) − sum(A) = 0`, so `B \ A` is a block disjoint from `A`, giving `z(S) ≥ 2`. ∎

> **Corollary C1.** `z(S) ≤ 1` if and only if the atoms of `S` pairwise intersect.

*Proof.* Forward is Lemma A together with the definition of `z`. Conversely, two disjoint blocks would contain two disjoint atoms. ∎

So the object of study is not an intersecting family in a loose sense: it is an **intersecting antichain** of subsets of `[n]` arising as the binary support system of an `F_p`-code of codimension at most `r`.

### 3.3 Above `D`, the family is star-free

> **Theorem Y.** Let `S` be any sequence over `C_p^r` of length `n` possessing at least one block. If some position lies in **every** block of `S`, then `n ≤ D(C_p^r) = r(p−1) + 1`.

There is no hypothesis on `z(S)`; this is a statement about arbitrary sequences.

*Proof.* Suppose position `i` lies in every block, and let `S'` be `S` with that one term deleted, so `|S'| = n − 1`. A block of `S'` would be a block of `S` avoiding `i`, so `S'` is zero-sum free and `n − 1 ≤ D − 1 = r(p−1)` by Olson. ∎

> **Corollary Y1.** If `z(S) ≤ 1` and `n ≥ D + 1 = r(p−1) + 2`, the atoms of `S` have empty common intersection.

**Theorem Y is sharp.** Take `T = ∏_i e_i^{p−1}`, which is zero-sum free of length `r(p−1)`, and append `g = −sum(T)`. The only block of the result is the whole sequence, so every position lies in every block, and `n = r(p−1) + 1 = D` exactly.

**Why this is the point.** An intersecting family with an element common to all its members is a *star*, and stars are the trivial extremal examples in extremal set theory — they are also the only ones a naive construction finds. Theorem Y says the entire star construction is worth exactly `D(C_p^r)`. Every witness for `D_2 > D + 1` must therefore have atoms that pairwise meet with **no** element common to all of them: the Hilton–Milner regime, in which intersecting families stop being easy. This is a structural explanation for an experience — that lower-bound constructions here are irregular, and that neither natural uniform family shape works (§9.2).

### 3.4 The extremal problem, restated

Collecting §3.1–§3.3: `D_2(C_p^r) − 1` is the largest `n` for which there is a matrix `M ∈ F_p^{r×n}` whose binary support system is a family that is

1. **intersecting** (Corollary C1),
2. an **antichain** (Lemma A),
3. **star-free** once `n ≥ r(p−1) + 2` (Corollary Y1),
4. with every member of size at most `r(p−1) + 1` (Olson: atoms are short), and
5. with every member of size at least `n − r(p−1)` (complement lemma).

Constraints 4 and 5 give `n ≤ 2r(p−1) + 1`, which is the upper half of (2.1). That bound is weak — at `C_3^5` it gives `D_2 ≤ 22` against the true value `17` — and closing the gap uniformly in `(p,r)` is the main open problem this paper leaves. What §3.4 contributes is that the gap is now a question about a *named class of set systems* rather than about sequences.

---

## 4. The witness-coordinate criterion

From here `p` is an odd prime.

### 4.1 Blocks of the algebraic family are indexed by the extra part

Fix vectors `v_1, …, v_κ ∈ F_p^r` and multiplicities `m_1, …, m_κ ≥ 0`, and consider

    S  =  e_1^{p−1} ⋯ e_r^{p−1} · v_1^{m_1} ⋯ v_κ^{m_κ}.                     (†)

Let `M` be the `r × κ` matrix with columns `v_1, …, v_κ`, and for `b ∈ Z^κ` with `0 ≤ b ≤ m` write `c(b) = Mb ∈ F_p^r` for the **load vector**.

> **Lemma 1.** The zero-sum subsequences of `(†)` are exactly
>
>     B(b) = e_1^{a_1(b)} ⋯ e_r^{a_r(b)} · v_1^{b_1} ⋯ v_κ^{b_κ},     a_i(b) = ⟨−c(b)_i⟩,
>
> one for each `b` with `0 ≤ b ≤ m`; and `B(b)` is empty exactly when `b = 0`.

*Proof.* A sub-multiset of `(†)` is given by multiplicities `a_i ∈ [0, p−1]` and `b_A ∈ [0, m_A]`. Its sum is `Σ_i (a_i + c(b)_i)e_i`, which vanishes iff `a_i ≡ −c(b)_i (mod p)` for every `i`; since `a_i ∈ [0, p−1]` this determines `a_i = ⟨−c(b)_i⟩` uniquely. If `b = 0` then `c(b) = 0` and every `a_i = 0`. ∎

The choice of `v`-part already fixes the block: the `e`-part is not free. This is what makes the question finite and independent of `|G|`.

> **Lemma 2.** `B(b)` and `B(b′)` are disjoint iff `b + b′ ≤ m` and `a_i(b) + a_i(b′) ≤ p−1` for every `i`.

*Proof.* Disjointness of sub-multisets is exactly the statement that the multiplicities add to at most those of `S`, which are `p−1` for each `e_i` and `m_A` for each `v_A`. ∎

### 4.2 The criterion

Call a coordinate `i` a **witness** for the ordered pair `(b, b′)` when

    ⟨c(b)_i⟩ ≠ 0,    ⟨c(b′)_i⟩ ≠ 0,    and    ⟨c(b)_i⟩ + ⟨c(b′)_i⟩ ≤ p.

> **Theorem W.** For `S` as in `(†)`,
>
>     z(S) ≤ 1   ⟺   every pair b, b′ ∈ Z_{≥0}^κ \ {0} with b + b′ ≤ m has a witness coordinate.

*Proof.* By Lemmas 1 and 2, `z(S) ≥ 2` iff some pair `b, b′ ≠ 0` with `b + b′ ≤ m` satisfies `⟨−c(b)_i⟩ + ⟨−c(b′)_i⟩ ≤ p−1` for **every** `i`. Fix `i` and put `u = ⟨c(b)_i⟩`, `u′ = ⟨c(b′)_i⟩`, so that `⟨−c(b)_i⟩` is `0` when `u = 0` and `p − u` otherwise. There are four cases:

| `u` | `u′` | `⟨−c(b)_i⟩ + ⟨−c(b′)_i⟩` | is it `≤ p−1`? |
|---|---|---|---|
| `0` | `0` | `0` | yes |
| `0` | `≠ 0` | `p − u′` | yes |
| `≠ 0` | `0` | `p − u` | yes |
| `≠ 0` | `≠ 0` | `2p − u − u′` | iff `u + u′ ≥ p+1` |

So coordinate `i` obstructs the disjointness of `B(b)` and `B(b′)` precisely when `u, u′ ≠ 0` and `u + u′ ≤ p`, that is, precisely when `i` is a witness. Hence `z(S) ≥ 2` iff some admissible pair has no witness at all. ∎

The mechanism is **carrying**: `⟨x⟩ + ⟨y⟩ ≤ p−1` iff `⟨x⟩ + ⟨y⟩ = ⟨x+y⟩`, so two blocks are disjoint iff their `e`-parts add with no carry in any coordinate, and a witness is a coordinate that forces a carry.

**An equivalent form.** Since `|B(b)| = |b| + w(b)` with `w(b) = Σ_i ⟨−c(b)_i⟩`, and `|b| + |b′| = |b+b′|`, Theorem W reads

> `z(S) ≤ 1` ⟺ `|B(b)| + |B(b′)| ≥ |B(b+b′)| + p` for every nontrivial split of every `s ≤ m`.

The union of two disjoint blocks is never the shortest block carrying its load vector; it overshoots by at least `p`.

### 4.3 What the criterion contains

Take `v_A = 1_A` for a family `F` of subsets of `[r]` — the *indicator* case.

> **Corollary 1 (intersecting families are the singleton case).** Taking `b = e_A`, `b′ = e_B` with `A ≠ B` and `m_A, m_B ≥ 1` gives `c(b) = 1_A`, `c(b′) = 1_B`, and a witness is an `i ∈ A ∩ B`, where `1 + 1 = 2 ≤ p`. So the criterion forces `A ∩ B ≠ ∅`: the support of any admissible family is intersecting. ∎

> **Corollary 2 (multiplicity cap).** `m_A ≤ p` for every `A`.

*Proof.* If `m_A ≥ p+1`, take `b = e_A` and `b′ = p·e_A`; then `c(b′) = p v_A = 0`, so no coordinate can witness. Concretely, `v_A^p` is a block disjoint from `v_A`. ∎

> **Corollary 3.** If the `v_A = 1_A` are intersecting and `Σ_{A ∋ i} m_A ≤ p` for every coordinate `i`, then `z(S) ≤ 1`.

*Proof.* Given `b, b′ ≠ 0` with `b + b′ ≤ m`, pick `A ∈ supp b`, `B ∈ supp b′` and `i ∈ A ∩ B`. Then `c(b)_i ≥ 1`, `c(b′)_i ≥ 1` and `c(b)_i + c(b′)_i ≤ Σ_{A′ ∋ i}(b+b′)_{A′} ≤ Σ_{A′ ∋ i} m_{A′} ≤ p`; in particular each is `< p`, so both residues are nonzero and sum to at most `p`, and `i` witnesses. ∎

Corollary 3 is the previously used sufficient condition, reproved in three lines. Write `M_load(r,p)` for the largest `Σ_A m_A` admitted by *its* hypotheses and `M*(r,p)` for the largest admitted by Theorem W, so `M_load ≤ M*` and

    D_2(C_p^r)  ≥  r(p−1) + M*(r,p) + 1.                                  (4.1)

The coordinate load cap is what Corollary 3 needs and what Theorem W does not, and every improvement in §7 comes from a point where `M_load < M*`.

### 4.4 Every `k` at once

Nothing in §4.1 used `t = 2`. A packing of size `t` is a set of `t` pairwise disjoint blocks `B(b^{(1)}), …, B(b^{(t)})`, which by Lemmas 1 and 2 means `Σ_j b^{(j)} ≤ m` together with `Σ_j a_i(b^{(j)}) ≤ p−1` for every `i` — the `t` forced `e`-parts must add with no carry.

> **Theorem W_t.** For `S` as in `(†)`,
>
>     z(S) ≥ t   ⟺   there are b^{(1)}, …, b^{(t)} ≠ 0 with Σ_j b^{(j)} ≤ m
>                     and  Σ_j ⟨−(M b^{(j)})_i⟩ ≤ p−1  for every coordinate i.

*Proof.* (⇐) Form the blocks `B(b^{(j)})` of Lemma 1; each is nonempty because `b^{(j)} ≠ 0`. They are pairwise disjoint as sub-multisets of `S`: the `v`-parts use `Σ_j b^{(j)} ≤ m` copies in total, and coordinate `i` of the `e`-part uses `Σ_j a_i(b^{(j)}) ≤ p−1` copies of `e_i`, which is all that `(†)` supplies.

(⇒) Let `B_1, …, B_t` be pairwise disjoint blocks. By Lemma 1 each is `B(b^{(j)})` for a unique `b^{(j)} ≤ m`, nonzero since `B_j ≠ ∅`. Disjointness bounds the total use of each `v_A` by `m_A`, giving `Σ_j b^{(j)} ≤ m`, and the total use of each `e_i` by `p−1`, giving `Σ_j ⟨−(Mb^{(j)})_i⟩ ≤ p−1`. ∎

Theorem W is the case `t = 2`, where the four-case table of §4.2 rearranges the condition into witness form. For `t ≥ 3` no such two-term rearrangement is available, so the summed form is the one to use; the "witness coordinate" language is a convenience special to pairs.

Writing `M*_k(r,p)` for the largest `Σ_A m_A` admitting no such `k`-tuple, `D_k(C_p^r) ≥ r(p−1) + M*_k(r,p) + 1`.

**The criterion reproduces every exact value we have, across three values of `k`.**

| value | `r(p−1)` | `M*_k` computed | bound obtained | known value |
|---|---|---|---|---|
| `D_2(C_3^2)` | 4 | 3 | 8 | 8 |
| `D_2(C_5^2)` | 8 | 5 | 14 | 14 |
| `D_2(C_7^2)` | 12 | 7 | 20 | 20 |
| `D_2(C_3^3)` | 6 | 4 | 11 | 11 |
| `D_2(C_5^3)` | 12 | 7 | 20 | 20 |
| `D_2(C_7^3)` | 18 | 10 | 29 | 29 |
| `D_2(C_3^4)` | 8 | 5 | 14 | 14 (§6.1) |
| `D_3(C_5^3)` | 12 | 12 | 25 | 25 |
| `D_3(C_7^3)` | 18 | 17 | 36 | 36 |
| `D_4(C_5^3)` | 12 | 17 | 30 | 30 |

Ten exact values, three ranks, three values of `k`, four primes, no case fitted. This is the strongest evidence we have that the algebraic class `(†)` is not merely a source of lower bounds but is **extremal** for `D_k(C_p^r)` — every value we know is attained inside it. §8.3 records the computation that puts that reading under strain.

**The `k`-direction collapses to `k = 2`.** The computed optima satisfy `M*_k = M*_2 + (k−2)p`, observed at `(r,p,k) = (3,5,3), (3,5,4), (3,7,3), (4,3,3)`. This direction is not new. Freeze and Schmid proved that `(D_k(G))_{k∈ℕ}` is eventually an arithmetic progression with difference `exp(G)`; the relation above is that theorem seen from inside the construction class, and the `≥` half is its standard proof read through Theorem W_t. Given an admissible family for `k`, append a new set at multiplicity `p`: its extra part contributes the single block `v_A^p`, whose load `p·v_A` vanishes so that its `e`-part is empty, raising the packing number by at most one while increasing `Σ m_A` by `p`. The `k = 4` optimum for `C_5^3` displays this literally, containing `e_2^5 = e_2^p`.

Consequently all the content sits at `k = 2`, and every `D_2` improvement propagates to every `k`.

---

## 5. What the criterion forbids

Theorem W is an equivalence, so it constrains the construction from above as well as below. This section extracts what it forbids: two zero-sum-freeness bounds, a monotonicity fact, a sunflower threshold, a multiplicity rigidity special to `p = 3`, and a separation showing that the first two do not between them characterise admissibility. Write `V` for the multiset `{v_A^{m_A}}` of the extra part, so `|V| = Σ_A m_A` and `|S| = r(p−1) + |V|`.

### 5.1 The extra part has no proper zero-sum

> **Theorem X.** If `S` as in `(†)` has `z(S) ≤ 1`, then `V` has no nonempty *proper* zero-sum sub-multiset — `V` is zero-sum free, or `V` is a single atom. Hence `M*(r,p) ≤ D(C_p^r) = r(p−1)+1`.

*Proof.* Suppose `0 < b < m` with `Mb = 0`. Then `c(b) = 0`, so `a_i(b) = 0` for every `i` and `B(b)` consists of `v`'s alone; it is nonempty since `b ≠ 0`. Put `b′ = m − b ≠ 0`. No coordinate witnesses `(b, b′)`, because a witness needs `⟨c(b)_i⟩ ≠ 0`. By Theorem W, `z(S) ≥ 2`. ∎

Consequently `|S| ≤ r(p−1) + (r(p−1)+1) = 2D − 1`, so this construction class can never beat the trivial bound `D_2 ≤ 2D` of (2.1) — a consistency check, and an explanation of where the class stops.

### 5.2 Projections are zero-sum free

Theorem X is loose: at `p = 3` it gives `2r+1` against an observed `r+1`. Pairing `b` against a **single set** rather than against the complement sharpens it considerably.

> **Theorem X′.** Let the family be an indicator family satisfying Theorem W. Then for every `A` with `m_A ≥ 1`, the projected multiset `{ 1_{A∩B} : B ∈ V \ {A} }` is zero-sum free in `Z_p^A`. Hence
>
>     |V| ≤ |A|(p−1) + 1  for every A,   so   M*(r,p) ≤ a(p−1) + 1,  where a = min_{A ∈ F} |A|.

*Proof.* Take `b′ = e_A`, so `c(b′) = 1_A`. A coordinate `i` witnesses `(b, e_A)` iff `i ∈ A`, `⟨c(b)_i⟩ ≠ 0` and `⟨c(b)_i⟩ + 1 ≤ p`, the last being automatic since `⟨c(b)_i⟩ ≤ p−1`. So Theorem W says exactly: for every nonempty `b ≤ m − e_A` there is an `i ∈ A` with `c(b)_i ≢ 0`. Restricting to the coordinates of `A` turns `c(b)` into `Σ_B b_B 1_{A∩B}`, so the multiset `{1_{A∩B}}` over `B ∈ V \ {A}` has no zero-sum sub-multiset at all: it is zero-sum free in `Z_p^A`, hence of length at most `D(C_p^{|A|}) − 1 = |A|(p−1)`. Adding back the removed copy of `A` gives `|V| ≤ |A|(p−1) + 1`. ∎

Against the computed optima, Theorem X′ is tight in half the cases:

| group | `M*` | `a = min\|A\|` | `a(p−1)+1` | Theorem X | |
|---|---|---|---|---|---|
| `C_3^2` | 3 | 1 | **3** | 5 | tight |
| `C_3^3` | 4 | 2 | 5 | 7 | |
| `C_3^4` | 5 | 2 | **5** | 9 | tight |
| `C_3^5` | 6 | 3 | 7 | 11 | |
| `C_3^6` | 7 | 3 | **7** | 13 | tight |
| `C_5^4` | 9 | 2 | **9** | 17 | tight |
| `C_7^4` | 12 | 2 | 13 | 25 | |
| `C_5^5` | 10 | 3 | 13 | 21 | |

Theorem X′ also explains the *shape* of the extremal families and makes one search terminate. To reach `M* = r+1` at `p = 3` one needs `2a + 1 ≥ r + 1`, so every set must have size at least `r/2` — and the computed optima sit exactly at that threshold, with `a = 2` at `r = 3, 4` and `a = 3` at `r = 5, 6`. Small sets are cheap to intersect but cap `|V|`; large sets lift the cap but leave too few of them. The same inequality is what makes `r = 7` decidable at all (§9.1): a family with `Σ m_A ≥ 8` needs `2a+1 ≥ 8`, hence minimum set size `a ≥ 4`, while families with `a ≤ 3` are capped at `7` outright, which reduces an otherwise intractable search to the 64 subsets of `[7]` of size at least four.

### 5.3 The optimum does not decrease with the rank

One small fact is used below and is worth isolating, because it is what makes a *drop* in the computed sequence `M*(r,3)` impossible and therefore turns any such drop into a computational error rather than a discovery.

> **Lemma R.** `M*(r,p) ≤ M*(r+1,p)` for every `r` and `p`.

*Proof.* Let `F` be an admissible indicator family on `[r]` with multiplicities `m`, and read each `A ∈ F` as a subset of `[r+1]`. The vectors `1_A ∈ {0,1}^{r+1}` all have last coordinate `0`, so `c(b)_{r+1} = 0` for every `b` and coordinate `r+1` never witnesses anything. Every other coordinate carries the same load as before, so a witness for a pair in `[r]` is still a witness in `[r+1]`. Hence `F` remains admissible and `Σ_A m_A` is unchanged. ∎

So `M*(·, p)` is non-decreasing, and the computed values `M*(r,3) = 3, 4, 5, 6, 7` for `r = 2, …, 6` force `M*(7,3) ≥ 7` before any rank-seven search is run. What a rank-seven search can decide is only whether the value is 7 or more.

### 5.4 Admissible families are sunflower-free

Theorem X′ came from pairing `b` against one set. Pairing two against two gives a condition of a different flavour. For `b = e_A + e_B` the load is `2` on `A ∩ B` and `1` on `A △ B`, and likewise for `b′ = e_C + e_D`. At `p = 3` a witness fails only where both loads equal `2`, so `(b,b′)` has no witness precisely when

    (A ∪ B) ∩ (C ∪ D)  =  A ∩ B ∩ C ∩ D.

> **Corollary 4.** No four members of `V` (repetitions allowed) satisfy that identity. In particular, an admissible family over `C_3^r` contains no four-petal sunflower — four sets with a common core `K` and pairwise disjoint petals, for which both sides equal `K`.

The `4` is `p+1`, and the statement is uniform in `p`.

> **Corollary 4′.** An admissible indicator family contains no sunflower with `p+1` petals, and `p` petals is the largest that can survive.

*Proof.* Let `A_1, …, A_{p+1} ∈ V` have common core `K` and pairwise disjoint petals `A_j \ K`. Split them into groups of sizes `u` and `v` with `u + v = p+1` and `1 ≤ u, v ≤ p−1` — take `u = 2`, `v = p−1` — and let `b, b′` be the corresponding sums of `e_{A_j}`, which are disjoint. Since the petals are pairwise disjoint, a petal coordinate lies in exactly one group, so `supp c(b) ∩ supp c(b′) = K`, and there `⟨c(b)_i⟩ + ⟨c(b′)_i⟩ = u + v = p+1 > p`. No coordinate witnesses, so `z(S) ≥ 2`. Conversely with only `p` petals every split has `u + v ≤ p` with `u, v ≥ 1`, so any `i ∈ K` witnesses. ∎

This is a genuinely different constraint from intersectingness: it forbids families that are *too* uniformly intersecting, meeting in the same place every time. Combined with the Erdős–Rado sunflower lemma it bounds the number of distinct sets outright — if every set has size at most `s`, a family with more than `s!·p^s` distinct sets contains a `(p+1)`-sunflower and is inadmissible, so `M* ≤ p·s!·p^s`.

The two bounds squeeze from opposite directions. Theorem X′ says the sets must be large; Corollary 4′ says they must not be large in the same way, since they cannot share a common core. That tension is why the extremal families of §9.2 are irregular and why `M*` resists a closed form.

### 5.5 At `p = 3`, multiplicity is almost never repeated

Pairing `b` against two copies of one set, `b′ = 2e_A`, available whenever `m_A ≥ 2`, needs a coordinate `i ∈ A` with `⟨c(b)_i⟩ ≠ 0` and `⟨c(b)_i⟩ + 2 ≤ p`.

> **Corollary 5.** If `m_A ≥ 2` then every nonzero `b ≤ m − 2e_A` has a coordinate `i ∈ A` with `1 ≤ ⟨c(b)_i⟩ ≤ p−2`.

At `p = 3` the window `[1, p−2]` collapses to the single value `1`, which is rigid enough to force a global structure: taking `b = 2e_C` for any other set with `m_C ≥ 2` gives a load of `2` on `C` and `0` elsewhere, which never takes the value `1`, so no coordinate can witness.

> **Corollary 5a (`p = 3` only).** At most one set of an admissible family over `C_3^r` has multiplicity `≥ 2`, and since Corollary 2 caps that one at `p = 3`, `Σ_A m_A ≤ |F| + 2`.

For `p ≥ 5` the same `b = 2e_C` is harmless, since `2 ≤ p−2`, and the contrast is visible in the data: every `C_3^r` optimum carries at most one repeated set, while the `C_5^4` and `C_7^4` optima each carry three. The same pairing with `b = e_C + e_D` gives a second `p = 3` consequence: if `m_A ≥ 2` then the traces `C ∩ A` over the other members of `V` are pairwise distinct, since `A ∩ (C △ D) = (A∩C) △ (A∩D)` must be nonempty.

### 5.6 The necessary conditions do not characterise admissibility

Corollary 1 (intersecting) and Theorem X (no proper zero-sum in `V`) are both necessary and both purely combinatorial, so one might hope they characterise admissibility. They do not. Let `B(r,p)` be the largest `|V|` over multisets of `0/1` vectors whose supports pairwise intersect and which have no proper nonempty zero-sum — a quantity defined without reference to blocks or packing. Then `M* ≤ B`, and the gap grows:

| `r` | `M*(r,3)` | `B(r,3)` | `D(C_3^r) = 2r+1` |
|---|---|---|---|
| 2 | 3 | 4 | 5 |
| 3 | 4 | 6 | 7 |
| 4 | 5 | **9** | 9 |

At `r = 4` the combinatorial ceiling has already risen to Theorem X's bound while the truth sits at `r+1`. The carry structure of Theorem W therefore does work that intersectingness and zero-sum-freeness cannot do between them, and a proof of a formula for `M*(r,3)` will have to use the criterion itself rather than these two shadows of it.

---

## 6. Two exact values, at ranks four and five

### 6.1 `D_2(C_3^4) = 14`

> **Theorem 6.1.** `D_2(C_3^4) = 14`.

**Lower bound.** Exhaustive depth-first search over indicator families satisfying Theorem W returns `M*(4,3) = 5`, attained by

    V = 1100, 1010, 0110, 1101, 1011,   each of multiplicity 1,

so with `q = r(p−1) = 8` the family `(†)` gives `S = e_1^2 e_2^2 e_3^2 e_4^2 · V` of length `13`. Independently of the criterion, enumerating all `2^13` subsets and running an exact packing computation shows `S` has 109 blocks and `z(S) = 1`. Hence `D_2(C_3^4) ≥ 14`.

The witness also **saturates its atom-size window**: sizes run `5..9` with no gaps, the admissible window `[n−q, q+1]` is exactly `[5,9]`, and the common core is empty as Corollary Y1 requires. This is the sixth instance of the saturation pattern of §8.4 and the first at rank four.

**Upper bound.** We show every length-14 sequence over `C_3^4` has `z ≥ 2`. Two reductions make the search finite and small, and both are lossless.

1. *Short zero-sums are excluded.* If `z(S) ≤ 1` and `|S| = 14`, the complement lemma gives every block length `≥ |S| − q = 6`, so `S` has no zero-sum of length at most 5. Searching only such sequences loses nothing.
2. *`S` spans, so a basis may be assumed.* Otherwise `S` lies in a subgroup isomorphic to `C_3^s` with `s ≤ 3`, where `z(S) ≤ 1` forces `|S| ≤ D_2(C_3^3) − 1 = 10 < 14`. So `S` contains a basis, which `GL(4,3)` carries to `e_1, …, e_4`; the remaining ten terms are enumerated as a non-decreasing multiset over the 80 nonzero elements. (`0 ∉ S`, since `0` would be a block of length 1.)

The sweep visits **987,944 nodes** and reaches **10,852 leaves** — complete sequences of length 14 surviving the prune — of which **none** has `z ≤ 1`. Each leaf is tested by an exact layered dynamic programme over pairs of disjoint sub-multisets, so the result is not vacuous: ten thousand candidates were examined and every one had two disjoint zero-sum subsequences. ∎

**The enumerator is calibrated in both directions.** A search returning zero proves nothing unless it can return non-zero. Run at `C_3^3`, where `D_2 = 11` is known, it returns `5006` witnesses at length 10, where witnesses must exist, and `0` witnesses and `0` leaves at length 11, where none can. It therefore reproduces `D_2(C_3^3) = 11` from both sides.

### 6.2 `D_2(C_3^5) = 17`

> **Theorem 6.2.** `D_2(C_3^5) = 17`. Equivalently, the longest sequence over `C_3^5` with no two disjoint nonempty zero-sum subsequences has length 16.

**Lower bound.** The optimal family at `r = 5` is the six triples through coordinate 1, giving

    S = e_1^2 e_2^2 e_3^2 e_4^2 e_5^2 · ∏_{2 ≤ i < j ≤ 5} (e_1 + e_i + e_j),      |S| = 16,

and `z(S) = 1` was confirmed by an exact packing computation independent of the criterion. All six triples contain coordinate 1, whose load is therefore `6 = 2p` — twice the cap of Corollary 3, which is exactly why the load-capped construction reaches only 16.

**Upper bound.** Suppose `|S| = 17` over `C_3^5` with `z(S) ≤ 1`. By the complement lemma every block has length at least `17 − 10 = 7`, so `S` has no zero-sum of length at most 6. If `S` did not span, it would lie in `C_3^s` with `s ≤ 4`; for `s ≤ 3` the value `D_2(C_3^3) = 11` caps the length at 10, and for `s = 4` Theorem 6.1 caps it at 13, both below 17. So `S` spans, contains a basis, and after applying `GL(5,3)` the remaining twelve terms are enumerated in non-decreasing index order.

An exhaustive depth-first search over that normal form, pruned on the short-zero-sum condition, was run to completion in 49 shards: **2,730,591,635 nodes, zero leaves, zero witnesses**. No length-17 sequence even survives the prune, let alone has `z ≤ 1`. ∎

Shard coverage is exact: a 16-way shard `i` takes first-free-element `g ≡ i (mod 16)`; a 64-way sub-shard `j` takes `g ≡ j (mod 64)` and so lies inside class `j mod 16`, and the four `j ≡ i` partition class `i`.

### 6.3 Why 6.1 has to come first

Theorem 6.1 is not only a value; it repairs Theorem 6.2. The spanning reduction above needs an upper bound on `D_2(C_3^4)` to eliminate the `s = 4` branch, and before Theorem 6.1 the only available bound was the trivial `D_2(C_3^4) ≤ 2D(C_3^4) = 18`, which caps a `z ≤ 1` sequence at length **17** — exactly one short of excluding `|S| = 17`. The `s = 4` branch was therefore genuinely open, and an earlier version of this argument asserted the rank-four value before it had been established.

Theorem 6.1 closes the branch. No length-14 sequence over `C_3^4` has `z ≤ 1`, and by monotonicity (§2) no length-17 one does either, since every 14-term subsequence of such a sequence would itself have `z ≤ 1`. Nothing else in §6.2 changes; what changes is that its upper bound no longer rests on an assumed value.

These are, to our knowledge, the first exact values of `D_2(C_p^r)` for `r ≥ 4` and odd `p`. That statement is a novelty claim and it is unverified — see §11.

---

## 7. Improved bounds and brackets above rank three

### 7.1 Five improved lower bounds

Dropping the load cap of Corollary 3 improves five recorded lower bounds by one each. In every case the improvement is exactly the difference `M* − M_load`.

| group | load-capped bound | **Theorem W bound** | optimal family (all `m_A = 1` unless shown) |
|---|---|---|---|
| `C_3^5` | `≥ 16` | **`= 17`** (exact, §6.2) | the six triples through `1`: `{1,i,j}`, `2 ≤ i < j ≤ 5` |
| `C_3^6` | `≥ 19` | **`≥ 20`** | `123, 124, 125, 345, 136, 146, 156` |
| `C_5^4` | `≥ 25` | **`≥ 26`** | `12, 13, 14, 123^2, 124^2, 134^2` |
| `C_7^4` | `≥ 36` | **`≥ 37`** | `12, 13, 23^2, 123, 124^4, 234^3` |
| `C_5^5` | `≥ 30` | **`≥ 31`** | `123, 124, 134^2, 125^2, 135, 145^2, 2345` |

Every witness was confirmed by an exact packing computation, an algorithm independent of the criterion. By §4.4 each improvement propagates to every `k`:

    D_k(C_3^5) ≥ 17 + 3(k−2),   D_k(C_3^6) ≥ 20 + 3(k−2),   D_k(C_5^4) ≥ 26 + 5(k−2),
    D_k(C_7^4) ≥ 37 + 7(k−2),   D_k(C_5^5) ≥ 31 + 5(k−2).

At rank seven, Lemma R alone gives `M*(7,3) ≥ M*(6,3) = 7` and hence `D_2(C_3^7) ≥ 22`, with no rank-seven search required; whether the true value is 7 or 8 is left open in §9.1.

### 7.2 Three narrow brackets

Upper bounds at rank four and five come from a congruence certificate. If `S` has `|S| = N−1` and `z(S) ≤ 1`, then `T = S·(−σ(S))` is zero-sum of length `N` with `z(T) ≤ 2`, so every proper nonempty zero-sum of `T` has length in `[N−D, D]`; feeding that window into the Chevalley–Warning counting identity gives linear congruences on the counts `N_ℓ`, and inconsistency of the resulting system over `F_p` certifies that no such `S` exists. Writing `N*(p,r)` for the least inconsistent `N`, we have `D_2(C_p^r) ≤ N*(p,r) − 1` for each pair, by a finite certificate.

Computed over the pairs with `2 ≤ r ≤ 6` and `p ∈ {5,7,11,13}`, the threshold obeys

    N*(p,r) − 1  =  (3D+1)/2      if r is odd,
                    (3D+r−1)/2    if r is even,

for every pair with `r ≤ p`, degrading for `r > p`. At `r = 2` and `r = 3` this reproduces the known values `3p−1` and `(9p−5)/2` exactly, which is the method's calibration. Combining with §7.1:

| group | lower bound | upper bound | bracket |
|---|---|---|---|
| `C_5^4` | 26 (§7.1) | 27 | **`D_2(C_5^4) ∈ {26, 27}`** |
| `C_7^4` | 37 (§7.1) | 39 | **`D_2(C_7^4) ∈ {37, 38, 39}`** |
| `C_5^5` | 31 (§7.1) | 32 | **`D_2(C_5^5) ∈ {31, 32}`** |
| `C_11^4` | 60 | 63 | `D_2(C_11^4) ∈ [60, 63]` |

The certificate is weak at `p = 3`, where it gives only the trivial `2D`, which is why ranks four and five at that prime were settled by search instead (§6).

Note the shape of the odd-rank formula: `(3D+1)/2` is exactly the closed form of §8. So for odd rank the conjecture of §8 says precisely that this congruence bound is attained, and at `(r,p) = (5,3)` — where the certificate degrades but the search does not — it *is* attained, since `D_2(C_3^5) = 17 = (3·11+1)/2`.

---

## 8. A closed form, and the tension against it

### 8.1 The statement, and why its constants are not fitted

> **Conjecture.** For an odd prime `p`, rank `r ≥ 2` and `k ≥ 2`,
>
>     D_k(C_p^r)  =  (3/2)·r(p−1)  +  (k−2)·p  +  2.
>
> Equivalently, with `D = r(p−1)+1`, `D_2(C_p^r) = (3D+1)/2`.

The right-hand side is an integer exactly when `r(p−1)` is even, which for odd `p` is automatic.

The three constants are forced. Write the general shape `α·r(p−1) + β·p(k−2) + γ`. Imposing only the rank-two formula `D_k(C_p^2) = p + kp − 1` at three points determines `(α, β, γ) = (3/2, 1, 2)` uniquely over `Q`, and that solution then fits `D_k(C_p^2)` for every `p` and `k` tested. **Every value of rank three or more below is therefore an out-of-sample prediction, not a degree of freedom.**

### 8.2 Agreement with all 25 known exact values

| family | count | source | agrees |
|---|---|---|---|
| `D_k(C_p^2)`, `p ∈ {3,5,7,11}`, `k ∈ {2,…,5}` | 16 | rank-two formula | ✅ (this is the fit) |
| `D_2(C_p^3)`, `p ∈ {3,5,7,11}` | 4 | `(9p−5)/2` | ✅ prediction |
| `D_2(C_3^4) = 14` | 1 | §6.1 | ✅ prediction |
| `D_2(C_3^5) = 17` | 1 | §6.2 | ✅ prediction |
| `D_3(C_5^3) = 25` | 1 | exhaustive | ✅ prediction |
| `D_3(C_7^3) = 36` | 1 | companion work | ✅ prediction |
| `D_4(C_5^3) = 30` | 1 | companion work | ✅ prediction |

The rank-three row is a one-parameter family, not a point: the conjecture reproduces `(9p−5)/2` identically in `p`.

**It repairs a known failure.** The naive guess suggested by the rank-two shape, `D_k = r(p−1) + (k−1)p + 1`, is documented to fail for elementary `2`- and `3`-groups of rank at least three. On this data it agrees at all 16 rank-two points and fails at **all nine** points of rank at least three; the conjecture agrees at all 25. It is a candidate replacement for a shape known to break, and it breaks nowhere the truth is known.

**It is consistent at `k = 1` in the right way.** The formula is exact at `k = 1` for `r = 2` and wrong for every `r ≥ 3` tested. That is required rather than a defect: since `(D_k(G))_k` is only *eventually* an arithmetic progression with difference `exp(G)`, a formula linear in `k` must fail at small `k` in high rank.

**It respects the proved bracket.** `D + 1 ≤ (3D+1)/2 ≤ 2D` at every computed `(r,p)`, so the conjecture is compatible with Olson and the complement lemma.

### 8.3 The tension, and a dichotomy

Through `D_2 = r(p−1) + M* + 1`, the conjecture is equivalent to `M*(r,p) = r(p−1)/2 + 1`. The computed optima disagree, and **the disagreement grows with `p`**:

| `(r,p)` | computed `M*` | conjecture needs | construction gives | conjecture says | shortfall |
|---|---|---|---|---|---|
| `(4,3)` | 5 | 5 | `D_2 = 14` | 14 | 0 |
| `(4,5)` | 9 | 9 | `D_2 ≥ 26` | 26 | 0 |
| `(4,7)` | 12 | 13 | `D_2 ≥ 37` | 38 | **1** |
| `(4,11)` | **19** | 21 | `D_2 ≥ 60` | 62 | **2** |
| `(7,3)` | 7 or 8 (§9.1) | 8 | `D_2 ≥ 22` | 23 | 1, if `M* = 7` |
| `(5,5)` | 10 | 11 | `D_2 ≥ 31` | 32 | 1 |

`M*(4,11) = 19` is an exhaustive optimum, not a search that stalled: the enumeration ran to completion and returned a family of six sets with multiplicities summing to 19.

This kills the reading that "short by exactly one" invites — that the family class is incomplete by a hair. At rank four the shortfall runs `0, 0, 1, 2` across `p = 3, 5, 7, 11`: the construction's growth rate in `p` is genuinely below what the conjecture requires. Two competing patterns for `M*(4,p)` separate cleanly:

| `p` | computed | `⌊9p/5⌋` | `r(p−1)/2 + 1` |
|---|---|---|---|
| 3 | 5 | 5 | 5 |
| 5 | 9 | 9 | 9 |
| 7 | 12 | **12** | ~~13~~ |
| 11 | 19 | **19** | ~~21~~ |

**Does this refute the conjecture? No — and the distinction matters.** `M*` is the optimum over one construction class. It bounds `D_2` from below and says nothing about what `D_2` is. The conjecture survives every value that has actually been decided. What the table establishes is a dichotomy:

> At `(r,p) = (4,7)` — and equally at `(4,11)` and `(5,5)` — either the closed form of §8.1 is false, or the algebraic family `(†)` is not extremal for `D_2`.

Both branches are consequential. §4.4 records that every exact value we know is attained inside `(†)`; if the second branch holds, that agreement is a low-rank coincidence and every lower bound in §7.1 is loose. If the first holds, the closed form's support collapses to ranks two and three.

**One computation decides it.** The smallest instance is `C_3^7`, where the construction gives `D_2 ≥ 22` and the closed form predicts `23`. These are not a proved bracket — all that is proved there is `22 ≤ D_2(C_3^7) ≤ 30` — but they are the two candidate answers, and one search separates them. If some length-22 sequence over `C_3^7` has `z ≤ 1`, the conjecture survives at that point and the family `(†)` is provably not the whole story; if none does, the conjecture is false. Rank seven at `p = 3` is also where the pattern of §9.1 breaks, so it is the point where the construction class is already known to behave unexpectedly.

### 8.4 Extremal witnesses saturate the size window

Writing `q = r(p−1) = D − 1`, the conjecture says `n_max = (3q+2)/2`, so the admissible atom-size window `[n − q, q+1]` becomes exactly `[(q+2)/2, q+1]` — floor at half the ceiling. Every extremal witness we can enumerate saturates that window:

| group | `q` | window | atom sizes attained | blocks | common core |
|---|---|---|---|---|---|
| `C_3^2` | 4 | `[3,5]` | 3,4,5 | 13 | empty |
| `C_3^3` | 6 | `[4,7]` | 4,…,7 | 43 | empty |
| `C_5^2` | 8 | `[5,9]` | 5,…,9 | 521 | empty |
| `C_7^2` | 12 | `[7,13]` | 7,…,13 | 24,865 | empty |
| `C_3^4` | 8 | `[5,9]` | 5,…,9 | 109 | empty |
| `C_3^5` | 10 | `[6,11]` | 6,…,11 | 289 | empty |

Six for six: the sizes fill the interval with no gaps, both ends are attained, and the common core is empty as Corollary Y1 requires. Saturating every elementary constraint of §3.4 simultaneously is the expected shape of an extremal object, and it is a regularity rather than a single observation.

### 8.5 The mechanism that would explain the factor, and does not hold

There is a tempting explanation for the scale `q/2`. No-carry requires `⟨a_i⟩ + ⟨a′_i⟩ ≤ p−1` in every coordinate; summing over `i`, two **disjoint** blocks must satisfy

    |e(b)| + |e(b′)| ≤ r(p−1) = q,    where |e(b)| = Σ_i ⟨−(Mb)_i⟩.

So `|e(b)| > q/2` for every admissible `b` is a genuine *sufficient* condition for `z(S) ≤ 1`, and it would name `q/2` as the critical scale for free.

**It is refuted by the extremal families themselves.** Every recorded optimum has blocks whose `e`-part is far below the half-budget:

| `(r,p)` | `q/2` | `min |e(b)|` |
|---|---|---|
| `(2,3)` | 2 | 2 |
| `(3,3)` | 3 | 2 |
| `(5,3)` | 5 | **3** |
| `(4,5)` | 8 | **3** |
| `(4,7)` | 12 | **5** |
| `(5,5)` | 10 | **2** |
| `(6,3)` | 6 | **3** |

Not one family satisfies the condition. The sum bound is a correct necessary condition for disjointness, but the extremal families sit far inside it and are held together by Theorem W's *coordinate-wise* condition, which is strictly stronger than any bound on the total. The `q/2` scale is therefore not explained this way, and this is not a route to the conjecture. We offer no proof of the conjecture in any rank.

---

## 9. Negative results

We record four failures explicitly, because each one closed off a line of attack that looked promising.

### 9.1 The pattern `M*(r,3) = r+1` does not survive to rank seven — with a caveat we state

The value `M*(r,3) = r+1` holds for `2 ≤ r ≤ 6`, and its natural reading — that `D_2(C_3^r) = 3r+2` for all `r`, which matches the four ranks where the value is known — predicts `M*(7,3) = 8`.

What is certain at `r = 7` is one inequality in each direction. Lemma R gives `M*(7,3) ≥ M*(6,3) = 7` with no search at all, by reading the rank-six optimum as a family on `[7]`. In the other direction, Theorem X′ says a family with `Σ m_A ≥ 8` needs `2a+1 ≥ 8`, hence minimum set size `a ≥ 4`, while families with `a ≤ 3` are capped at `7` outright; so `M*(7,3) ≥ 8` requires a family all of whose sets have at least four elements, which reduces the question to the 64 subsets of `[7]` of size at least four and makes it decidable.

**We report that search as unresolved here, and we say why.** The evidence packet records it as returning 7, which would give `D_2(C_3^7) ≥ 22` rather than the `23` the pattern predicts, and prints an optimal family attaining it. Re-tested against Theorem W while this paper was being written, **that printed family is not admissible**: it has 28 obstructed pairs, among them the split of the three five-element sets against the four four-element sets, whose loads share no coordinate where both are nonzero and sum to at most `3`. The family is therefore a transcription error, and we decline to rest a refutation on the record that carries it. The recomputation is running and is not reported here.

So the honest statement at rank seven is: `M*(7,3) ∈ {7, 8}`, the pattern predicts `8`, and one bounded search decides it. Nothing else in this paper depends on which way it goes — the dichotomy of §8.3 rests on `(4,7)`, where `M*(4,7) = 12` was recomputed independently for this paper against a conjectural requirement of 13.

A related observation, recorded with its failures attached rather than as a pattern to lean on: `M*(r,p) = ⌊ν_r p⌋` with `ν_r = 3(r−1)/(r+1)` — giving `1, 3/2, 9/5, 2` at `r = 2,3,4,5` — reproduces every computed optimum at `r ≤ 5`, including `M*(4,11)`, and **fails at `(6,3)`**, where it predicts 6 and 7 is computed. Its status at `(7,3)` depends on the same unresolved search.

### 9.2 The extremal families have no uniform shape

`M*(r,3) = r+1` is clean for `r ≤ 6`, but the families achieving it are not. Two natural uniform shapes suggested by the small cases both fail:

| candidate shape | works at | fails at |
|---|---|---|
| all `(r−1)`-subsets of `[r]` together with `[r]` itself — `r+1` sets | `r = 3` only | `r = 2, 4, …, 12` |
| `{ {1} ∪ e : e ∈ E }` for a graph `E` on the other `r−1` vertices with `r+1` edges | `r = 5` only, uniquely `E = K_4` | `r = 6, 7`: no graph works |

The first dies transparently: taking `b = {[r]}` and `b′` the sum of all `r` of the `(r−1)`-subsets gives `deg_i(b′) = r−1` in every coordinate, which is `≡ 0 (mod 3)` whenever `r ≡ 1 (mod 3)`, so no coordinate can witness. The second has no such clean cause — at `r = 6` all 120 seven-edge graphs on five vertices fail, and at `r = 7` all 6,435 eight-edge graphs on six vertices fail.

So the optimum is attained by genuinely heterogeneous families — the `r = 6` optimum mixes one set avoiding coordinate 1 with six containing it — and a closed form for `M*(r,p)` is not going to come from guessing a family shape. The asymptotic version is a fractional relaxation whose constraint involves *fractional parts* of the loads, hence is not a linear programme, which is why the load-capped optimum of Corollary 3, whose value is the fractional matching number of an intersecting family, undershoots.

### 9.3 The two necessary conditions do not characterise admissibility

Recorded as §5.6.

### 9.4 The half-budget mechanism is refuted

Recorded as §8.5.

### 9.5 General vectors do not close the shortfall — where the search runs

Theorem W never requires `v_A` to be a `0/1` vector, so the class was widened to all of `F_p^r` and searched exhaustively:

| `(r,p)` | indicator `M*` | all of `F_p^r` | verdict |
|---|---|---|---|
| `(3,3)` | 4 | 4 | no gain |
| `(4,3)` | 5 | 5 | no gain |
| `(5,3)` | 6 | **6** | no gain — and the optimum returned *is* the indicator family |

The `(5,3)` row is a falsification test of a proved result rather than a convenience. `D_2(C_3^5) = 17` means no family there may reach `Σ m_A ≥ 7`, since that would give `D_2 ≥ 18`; the exhaustive general-vector search caps at 6 and returns exactly the six triples through coordinate 1. Had it returned 7, either the sweep of §6.2 or the criterion would have been wrong.

Beyond rank five the exhaustive route does not run: `(3,5)` required roughly two hours over 242 vectors, and `(3,7)` has 2,186. Randomised searches at `r ≥ 6` are **uncalibrated** — two independently written ones both fail to recover the known `M*(6,3) = 7` — so we report `(7,3)` as genuinely undecided over general vectors rather than negatively decided. This is the reason §8.3's dichotomy is stated as a dichotomy.

---

## 10. Discussion and boundaries

**What is proved, uniformly in `(p,r)`.** Theorem C, Lemma A, Corollary C1, Theorem Y and Corollary Y1 (§3); Lemmas 1 and 2, Theorem W and Theorem W_t, Corollaries 1–3 (§4); Theorems X and X′ and Corollaries 4, 4′, 5, 5a (§5). These are the paper's uniform content, and none of them depends on a computation.

**What is proved for a specific group.** `D_2(C_3^4) = 14` and `D_2(C_3^5) = 17` (§6). Both are machine-assisted: the lower bounds are explicit witnesses re-verified by an exact packing algorithm that does not use the criterion, and the upper bounds are exhaustive searches whose enumerator is calibrated in both directions at `C_3^3`. Both rest on Olson's theorem, and §6.2 additionally rests on §6.1.

**What is computed for a finite range.** Every value of `M*(r,p)` and `M*_k(r,p)`; the brackets of §7.2; the saturation table of §8.4. These are exhaustive over the stated class and the stated parameters, and are lower bounds on what a wider class could give.

**What is conjectured.** §8.1, and the `ν_r` observation in §9.1. The conjecture is not proved in any rank and we have given the evidence against it as carefully as the evidence for it.

**Open problems, in order of what they would settle.**

1. **Is `D_2(C_3^7)` equal to 22 or to 23?** The cheapest decisive test, by §8.3; what is proved there is only `22 ≤ D_2(C_3^7) ≤ 30`. The search is at `3^7 = 2187` group elements and length 22, which is beyond the enumerator used in §6 but not obviously beyond a better one.
2. **A uniform upper bound at rank `≥ 4`.** §3.4 reduces this to bounding the size of an intersecting, star-free antichain realizable as the binary support system of an `F_p`-code of codimension `r`, with all member sizes in `[n−q, q+1]`. Constraints 4 and 5 give only `2D`; the question is what constraint 3 is worth.
3. **`D_2(C_5^4)`: 26 or 27?** The bracket is width two and the group has `5^4 = 625` elements; the corresponding search was measured and is out of reach of the present enumerator.
4. **Is `M*(r,3)` equal to `r+1` for all `r`?** It is for `2 ≤ r ≤ 6`; Lemma R makes the sequence non-decreasing, and §9.1 leaves `M*(7,3) ∈ {7,8}` as the first undecided term.
5. **Does widening `(†)` beyond indicator families gain anything at `r ≥ 6`?** §9.5 leaves this open, and it is the second branch of §8.3's dichotomy.

**Relation to the coding-theoretic literature.** §3.1 is the natural bridge to work that studies `D_k` for elementary `p`-groups through linear-code parameters and cap sets. That route bounds `D_k` through weight-spectrum data — minimum distance, cap-set size — and constraints 4 and 5 of §3.4 are exactly such parameter bounds; together they give only `D_2 ≤ 2D`. The improvements of §7.1 come instead from constraint 3, star-freeness, which is a combinatorial property of the support system rather than a weight-spectrum property of the code. We expect the two lines to be complementary, but we have not verified this and state it as an expectation only.

---

## 11. Verification, reproducibility, and outstanding prerequisites

Every claim above is backed by a checker with a non-vacuity control, and every checker is designed so that a real object must survive it.

| Claim | How it is checked | Control |
|---|---|---|
| Theorem C (a), (b) | the block set of a sequence is computed twice — by brute-force subset sums, and by Gaussian elimination over `F_p` followed by enumeration of the code — on 60 random sequences; `z(S)` likewise on 96 | 0 disagreements on either path |
| Lemma A, Corollary C1 | 84 sequences with `z ≤ 1` checked for a block that is not an atom; the biconditional checked on all 305 sequences possessing a block | 246 sequences with `z ≥ 2` as a negative control |
| Theorem Y | 3,074 random sequences with a block; 734 had a position lying in every block | none of those 734 exceeded `n = r(p−1)+1`; sharpness exhibited at `C_3^3`, `C_3^5`, `C_5^3`, `C_7^2` |
| Theorem W, `W_t` | the criterion's verdict compared against an exact packing dynamic programme that does not use it, on every optimum reported | the ten exact values of §4.4 recovered, none fitted |
| `M*` values | exhaustive depth-first enumeration with immediate pruning; the multiplicity box is bounded and overflow is fatal rather than silent | overflow guard shown to fire under a deliberately reduced bound while the production build returns the same optimum |
| `D_2(C_3^4) = 14` | 987,944 nodes, 10,852 leaves, 0 with `z ≤ 1`; both reductions re-derived | enumerator reproduces `D_2(C_3^3) = 11` from both sides (5,006 witnesses where they must exist; 0 where none can) |
| `D_2(C_3^5) = 17` | 2,730,591,635 nodes across 49 shards, 0 leaves; shard coverage checked to partition the residue classes | the length-16 witness re-verified by exact packing |
| §8 arithmetic | the constants shown forced by a rank-two solve over `Q`; agreement with all 25 known values asserted; the naive formula's 9 failures asserted; the shortfall table asserted term by term | the conjecture checked to lie inside `[D+1, 2D]` at every computed point |

**Independent-replication status.** The checks are single-implementation but double-method wherever a second decision procedure exists: the criterion against an exact packing dynamic programme, the code enumeration against brute-force subset sums, the `(5,3)` general-vector optimum against the proved value `D_2(C_3^5) = 17`. Double implementation by one author is **not** independent replication and is not counted as such here.

**Availability.** All constructions, witnesses, search programs and verification scripts supporting this paper are archived in the public repository accompanying it.

**Outstanding prerequisites.** Two remain, and neither can be cleared from the authoring host.

**(i) Prior-art verification.** A literature search has been run and one reference — Marchan, Ordaz, Santos and Schmid — has been read in full, because it was supplied directly; the remainder have not, because the host permits search but blocks page fetching for every scholarly domain attempted. Reading that reference **removed** rather than confirmed a risk: its elementary-`p`-group results are for the *fully weighted* constant `D_{A,m}` with `A = {1, …, exp(G)−1}`, which coincides with the classical `D_m` only at `p = 2`, and its explicit values cover rank at most two together with `C_3^3`. Its cap-set and linear-code bridge is to the weighted problem. The overlap with this paper is therefore empty, and it is cited above as nearest-by-method.

What remains unverified is everything else: whether Theorem W or Theorem C is already known, whether the star-free bound of Theorem Y is recorded, and whether `D_2(C_3^4)` or `D_2(C_3^5)` appears in the literature. **No priority claim should be read into this draft** until a person with library access has checked them. The claim in §6.3 that these are the first exact rank-four and rank-five values is stated on that footing and is not verified.

**(ii) Independent mathematical review.** None of the proofs above has been read by a mathematician. The uniform results of §3–§5 are short and self-contained, which lowers but does not remove the risk; the two exact values of §6 depend on searches whose correctness rests on the reductions stated there, and those reductions are exactly what a reviewer should attack first.

---

## References

Identified by literature search. With one exception, noted below, **none has been read**: the authoring host permits search but blocks page fetching for scholarly domains, so attributions are unverified against the primary text (§11).

1. J. E. Olson, *A combinatorial problem on finite abelian groups*, J. Number Theory (1969). — `D(C_p^r) = r(p−1)+1`, the only external input used throughout.
2. M. Freeze, W. A. Schmid, *Remarks on a generalization of the Davenport constant*, Discrete Math. **310** (2010) 3373–3389; arXiv:0905.4248. — `(D_k(G))_k` is eventually an arithmetic progression with difference `exp(G)`; used in §4.4 to say that the `k`-direction carries no new content.
3. P. Erdős, R. Rado, *Intersection theorems for systems of sets*, J. London Math. Soc. **35** (1960) 85–90. — the sunflower lemma, used in §5.3.
4. A. J. W. Hilton, E. C. Milner, *Some intersection theorems for systems of finite sets*, Quart. J. Math. Oxford **18** (1967) 369–384. — the star-free regime named in §3.3.
5. L. E. Marchan, O. Ordaz, I. Santos, W. A. Schmid, *Multi-wise and constrained fully weighted Davenport constants and interactions with coding theory*, J. Combin. Theory Ser. A **135** (2015) 237–267; arXiv:1407.1966. — **read in full** (v2, 21 May 2015). Nearest by method: it studies multi-wise Davenport constants for elementary `p`-groups through linear codes and cap sets. Its elementary-`p`-group results are for the fully weighted constant, which agrees with the classical one only at `p = 2`, so the overlap with this paper is empty; see §11.
