# The positional code dictionary, and what the extremal problem actually is

**Status: proved and machine-checked.** Checker: `verify_code_dictionary_v7.py` (7 asserted
steps, self-contained, no compiled tool). Every statement below holds for all `(p, r)`.

**This is positioning work, not a breakthrough.** §1 is almost certainly folklore — it is the
obvious dictionary, and the prior-art pass (`EXTERNAL_PRIOR_ART_V5.md` §V7) shows the literature
on `D_k` for elementary `p`-groups already speaks in exactly this language. It is recorded here
because the packet had been speaking a *different* one, and the translation is what lets these
results be compared against the coding-theoretic route rather than merely coexist with it.
§3 is elementary but was not previously recorded anywhere in the packet.

---

## 1. Theorem C (the dictionary)

Let `S = (g_1, …, g_n)` be a sequence over `C_p^r` and let `M ∈ F_p^{r×n}` be the matrix whose
`i`-th **column** is `g_i`. Let `C = ker M ⊆ F_p^n`, a linear code of length `n` and codimension
at most `r`.

Write `𝔅(S)` for the set of supports of the nonzero **binary** vectors of `C`, that is of the
`x ∈ C` with every coordinate in `{0, 1}`.

> **(a)** The nonempty zero-sum subsequences of `S` — the *blocks* — are exactly the nonzero
> binary codewords of `C`, matched by support.
>
> **(b)** Two blocks are disjoint as subsequences precisely when their supports are disjoint, so
> `z(S)` is the maximum number of pairwise disjoint members of `𝔅(S)`.
>
> **(c)** Consequently, for every `k ≥ 1`,
>
> `D_k(C_p^r) = 1 + max{ n : some M ∈ F_p^{r×n} has no k pairwise disjoint binary codewords }`.

**Proof.** A subsequence of `S` is a choice of a set `T` of *positions* (repeated group elements
occupy distinct positions and are chosen independently), so it is the 0/1 indicator vector `x_T`.
Its sum is `Σ_{i∈T} g_i = M x_T`. Hence `T` is a nonempty zero-sum subsequence iff `x_T ≠ 0` and
`M x_T = 0`, i.e. iff `x_T` is a nonzero binary codeword. That is (a); (b) is immediate since
disjointness of subsequences *is* disjointness of position sets; (c) is the definition of `D_k`
read through (a) and (b). ∎

**Why "positional" matters.** The packet's earlier formalisms
(`PACKING_DEFECT_CORE_FORMALISM_V1.md`, `GENERAL_CP3_MULTIWISE_MASTER_REDUCTION_V1.md`) index by
*multiplicity vectors over distinct group elements*, which makes the relevant kernel vectors
**box-constrained** — entries in `[0, m_g]` — and the whole apparatus is about conformal
decomposition in an affine semigroup. Indexing by *positions* instead makes them strictly **0/1**.
The cost is that repeated elements are no longer collapsed; the gain is that the objects become an
ordinary set system and the whole vocabulary of extremal set theory applies directly. §3 is what
that buys.

**Verified.** Step 1 computes `𝔅(S)` twice — once by brute-force subset sums, once by Gaussian
elimination over `F_p` followed by enumeration of the code — on 60 random sequences, 0
disagreements. Step 2 confirms `z(S)` agrees along both paths on 96 sequences.

**Where cap sets enter.** A binary codeword of weight `w` is a zero-sum subsequence of length `w`.
For `p = 3` a weight-3 binary codeword on distinct columns is three points summing to zero, so a
sequence of distinct elements with no weight-3 binary codeword is exactly a cap set in `AG(r,3)`.
This is the bridge the literature uses, and it is why cap-set bounds appear in this subject at all.

---

## 2. Lemma A: under `z(S) ≤ 1` the blocks form an antichain

> If `z(S) ≤ 1` then no block properly contains another; equivalently every block is an atom.

**Proof.** If `A ⊊ B` are blocks then `B \ A` is nonempty and `sum(B\A) = sum(B) − sum(A) = 0`, so
`B \ A` is a block disjoint from `A`, giving `z(S) ≥ 2`. ∎

**Corollary C1.** `z(S) ≤ 1` **iff** the atoms of `S` pairwise intersect.

*(⇒ is Lemma A plus the definition. ⇐: two disjoint blocks would contain two disjoint atoms.)*

So the object of study is not "an intersecting family" loosely — it is an **intersecting
antichain** of subsets of `[n]`, arising as the binary supports of an `F_p` code of codimension
`≤ r`. Verified in steps 3 and 4 (84 sequences with `z ≤ 1`, no violations, 246 controls with
`z ≥ 2`; the biconditional agrees on all 305 sequences that had a block).

---

## 3. Theorem Y: above `D`, the family is star-free

> Let `S` be **any** sequence over `C_p^r` of length `n` with at least one block. If some position
> lies in **every** block of `S`, then `n ≤ D(C_p^r) = r(p−1) + 1`.

Note there is no `z(S) ≤ 1` hypothesis — this is a statement about arbitrary sequences.

**Proof.** Suppose position `i` lies in every block, and let `S'` be `S` with that one term
deleted, `|S'| = n − 1`. A nonempty zero-sum subsequence of `S'` would be a block of `S` avoiding
`i`, so `S'` is zero-sum free and `n − 1 ≤ D(C_p^r) − 1 = r(p−1)` by Olson. ∎

> **Corollary Y1 (star-free).** If `z(S) ≤ 1` and `n ≥ D(C_p^r) + 1 = r(p−1) + 2`, the atoms of
> `S` have **empty** common intersection.

**Sharp.** `n = D` is attained: take `T = ∏_i e_i^{p−1}` (zero-sum free, length `r(p−1)`) and
append `g = −sum(T)`. The only block is all of `S`, so every position lies in every block, and
`n = r(p−1) + 1 = D` exactly. Verified in step 6 at `C_3^3`, `C_3^5`, `C_5^3`, `C_7^2`.

**Why this is the point.** An intersecting family with a common element is a *star*, and stars are
the trivial extremal examples in set theory — they are also the only ones a naive construction
finds. Theorem Y says the entire star construction is worth exactly `D(C_p^r)` and not one term
more. Every sequence witnessing `D_2 > D + 1` must therefore have atoms that pairwise meet with
**no** element common to all of them: the Hilton–Milner regime, where intersecting families stop
being easy. That is a structural explanation for something the packet had only observed
empirically — that `D_2` lower-bound constructions are awkward, and that neither natural uniform
family shape works (`WITNESS_CRITERION_V6.md` §8).

Verified in step 5: of 3,074 random sequences possessing a block, 734 had a position lying in
every block, and none of those had `n > r(p−1) + 1`.

---

## 4. The extremal problem, restated

Collecting §1–§3, `D_2(C_p^r) − 1` is the largest `n` for which there is a matrix
`M ∈ F_p^{r×n}` such that the binary supports of `ker M` form a family that is

1. **intersecting** (Corollary C1),
2. an **antichain** (Lemma A),
3. **star-free** once `n ≥ r(p−1) + 2` (Corollary Y1),
4. with every member of size `≤ r(p−1) + 1` (Olson: atoms are short), and
5. with every member of size `≥ n − r(p−1)` (the complement lemma: deleting a block must leave a
   zero-sum-free sequence).

Constraints 4 and 5 give the trivial upper bound `n ≤ 2r(p−1) + 1`, i.e. `D_2 ≤ 2D(C_p^r)`. That
bound is weak — for `C_3^5` it gives `D_2 ≤ 22` against the true value 17 — and closing that gap
uniformly is exactly open problem #2 in `README.md`. What §4 contributes is that the gap is now a
question about a **named class of set systems** rather than about sequences.

---

## 5. The `C_3^5` witness through the dictionary

The length-16 witness `S = e₁²e₂²e₃²e₄²e₅² · ∏_{2≤i<j≤5}(e₁+eᵢ+eⱼ)` that gives `D_2(C_3^5) ≥ 17`
reads as follows (step 7, all asserted):

| quantity | value |
|---|---|
| blocks | **289** |
| of which atoms | **289** — every block is an atom, as Lemma A requires |
| `z(S)` | 1 |
| atom sizes | exactly `{6, 7, 8, 9, 10, 11}` |
| constraint 5 floor `n − r(p−1)` | **6** — attained |
| constraint 4 ceiling `r(p−1)+1` | **11** — attained |
| pairwise intersecting | yes |
| common core | **empty**, as Corollary Y1 requires at `n = 16 ≥ 12` |

Both size constraints are tight *in the same example*, and the sizes fill the admissible interval
with no gaps. A construction that saturates every elementary constraint simultaneously is the
expected shape of an extremal object, and it is a reason to believe 16 is not beatable by a small
perturbation — which the 2.73-billion-node sweep then confirmed outright
(`D2_C3_5_DECIDED_V6.md`).

---

## 6. Relation to Theorem W, and to the coding literature

**To Theorem W.** `WITNESS_CRITERION_V6.md` works inside the structured family
`S = ∏ᵢ eᵢ^{p−1} · ∏_A v_A^{m_A}` and proves that blocks there are indexed by the multiplicity
vector `b` of the `v`-part alone, the `e`-part being forced to `aᵢ = ⟨−(Mb)ᵢ⟩`. In the language of
§1 that is the statement that, for this particular `M`, the binary codewords of `ker M` are
parameterised by `b`, and the no-carry condition is disjointness of supports. Theorem W is
therefore a *computation of `𝔅(S)` for a specific matrix family*, and Corollary 1 there ("admissible
supports are intersecting") is Corollary C1 restricted to that family. The dictionary does not
reprove Theorem W and does not weaken it; it says what kind of object Theorem W computes.

**To the literature.** `EXTERNAL_PRIOR_ART_V5.md` §V7 identifies `arXiv:1407.1966`
(Marchan–Ordaz–Santos–Schmid, JCTA 2015) as the real prior-art gate: they treat the `m`-wise
Davenport constant for elementary `p`-groups by linking it to linear codes and cap sets. §1 is
almost certainly a special case of the setup they work in. Recording it here does two things:

- it makes the packet's results *statable in their terms*, which is what a referee will want; and
- it makes the comparison concrete. Their route bounds `D_k` through code parameters —
  minimum distance, cap-set size. Constraints 4 and 5 above are exactly such parameter bounds, and
  together they give only `D_2 ≤ 2D`. The five improved lower bounds in this packet come from
  constraint 3's regime — star-free intersecting families — which is a *combinatorial* property of
  the support system, not a weight-spectrum property of the code. That is a reason to expect the
  two lines of work to be complementary rather than in collision, but it is **not** evidence, and
  it does not close the gate. The paper must still be read.

---

## 7. Claim ceiling

§1 is folklore in all likelihood and is claimed as translation, not as a result. §2 and §3 are
elementary, have two-line proofs, and are recorded because they were absent from this packet, not
because they are asserted to be absent from the literature — that has not been checked and cannot
be checked from this host. §4 is a restatement, not a theorem. §5 is a computation. §6 contains a
*conjecture about how two methods relate*, explicitly flagged as unverified.

Nothing here has been read by a mathematician.
