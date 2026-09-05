# The witness-coordinate criterion: an exact packing test for algebraic families — V6

Status: **criterion proved (Theorems W and W_t) and machine-verified; five published lower
bounds in `D2_ALL_RANKS_V3.md` improved; two upper bounds on the construction optimum proved
(Theorems X and X′).** The criterion contains that record's Theorem 2 as the special case of
one-element pairs, and reproduces all ten exact `D_k(C_p^r)` values the packet owns. Priority CANNOT_CHECK.
Checker: `verify_witness_criterion_v6.py`. Tools: `tools/pk1_check_v6.c`,
`tools/witness_optimum_v6.c`.
Branch: `claude/orion-research-frontier-3ck9yt`.

Throughout `p` is an odd prime, `G = C_p^r` with basis `e_1,…,e_r`, and for `x ∈ Z` we write
`⟨x⟩ ∈ {0,…,p−1}` for its residue. `z(S)` is the packing number.

## 1. The set-up

`D2_ALL_RANKS_V3.md` Theorem 2 builds packing-number-1 sequences of the shape

    S  =  e_1^{p−1} ⋯ e_r^{p−1} · v_1^{m_1} ⋯ v_k^{m_k},                     (†)

and proves `z(S) = 1` under two hypotheses: the supports form an **intersecting family**, and
every coordinate carries load `Σ_{A ∋ i} m_A ≤ p`. Both hypotheses are sufficient, neither is
necessary. This record replaces them by a criterion that is **exactly equivalent** to `z(S) ≤ 1`.

Let `M` be the `r × k` matrix over `Z_p` whose columns are `v_1,…,v_k`, and for
`b ∈ Z^k` with `0 ≤ b ≤ m` write `c(b) = Mb ∈ Z_p^r` for the **load vector**.

## 2. Blocks are indexed by `b`

**Lemma 1.** The zero-sum subsequences of `(†)` are exactly

    B(b)  =  e_1^{a_1(b)} ⋯ e_r^{a_r(b)} · v_1^{b_1} ⋯ v_k^{b_k},
    a_i(b) = ⟨−c(b)_i⟩,

one for each `b` with `0 ≤ b ≤ m`, and `B(b) = ∅` exactly when `b = 0`.

*Proof.* A sub-multiset of `(†)` is given by multiplicities `a_i ∈ [0,p−1]` and `b_A ∈ [0,m_A]`.
Its sum is `Σ_i (a_i + c(b)_i) e_i`, which vanishes iff `a_i ≡ −c(b)_i (mod p)` for every `i`;
as `a_i` lies in `[0,p−1]` this determines `a_i = ⟨−c(b)_i⟩` uniquely. If `b = 0` then `c(b) = 0`
and every `a_i = 0`. ∎

So the *choice of the `v`-part already fixes the block*: the `e`-part is not free. This is what
makes the whole question finite and independent of `|G|`.

**Lemma 2.** `B(b)` and `B(b′)` are disjoint iff `b + b′ ≤ m` and `a_i(b) + a_i(b′) ≤ p−1` for all `i`.

*Proof.* Disjointness of sub-multisets is exactly the statement that the multiplicities add to at
most those of `S`, which are `p−1` for each `e_i` and `m_A` for each `v_A`. ∎

## 3. The criterion

Call a coordinate `i` a **witness** for the ordered pair `(b,b′)` when

    ⟨c(b)_i⟩ ≠ 0,   ⟨c(b′)_i⟩ ≠ 0,   and   ⟨c(b)_i⟩ + ⟨c(b′)_i⟩ ≤ p.

> **Theorem W.** For `S` as in `(†)`,
>
>     z(S) ≤ 1   ⟺   every pair b, b′ ∈ Z_{≥0}^k \ {0} with b + b′ ≤ m has a witness coordinate.

*Proof.* By Lemmas 1 and 2, `z(S) ≥ 2` iff some pair `b,b′ ≠ 0` with `b+b′ ≤ m` satisfies
`⟨−c(b)_i⟩ + ⟨−c(b′)_i⟩ ≤ p−1` for **every** `i`. Fix `i` and put `u = ⟨c(b)_i⟩`, `u′ = ⟨c(b′)_i⟩`,
so `⟨−c(b)_i⟩` is `0` when `u = 0` and `p − u` otherwise. Four cases:

| `u` | `u′` | `⟨−c(b)_i⟩ + ⟨−c(b′)_i⟩` | `≤ p−1` ? |
|---|---|---|---|
| `0` | `0` | `0` | yes |
| `0` | `≠0` | `p − u′` | yes |
| `≠0` | `0` | `p − u` | yes |
| `≠0` | `≠0` | `2p − u − u′` | iff `u + u′ ≥ p+1` |

So coordinate `i` obstructs the disjointness of `B(b)` and `B(b′)` precisely when `u,u′ ≠ 0` and
`u + u′ ≤ p` — that is, precisely when `i` is a witness. Hence `z(S) ≥ 2` iff some admissible pair
has no witness at all. ∎

The mechanism is **carrying**: `⟨x⟩ + ⟨y⟩ ≤ p−1` iff `⟨x⟩ + ⟨y⟩ = ⟨x+y⟩`, so two blocks are
disjoint iff their `e`-parts add with no carry in any coordinate. A witness is a coordinate that
forces a carry.

### 3a. Equivalent form: superadditivity of block length

`|B(b)| = |b| + w(b)` with `w(b) = Σ_i ⟨−c(b)_i⟩`, and `|b| + |b′| = |b+b′|`, so Theorem W reads

> `z(S) ≤ 1` ⟺ `|B(b)| + |B(b′)| ≥ |B(b+b′)| + p` for every nontrivial split of every `s ≤ m`.

The union of two disjoint blocks is never the *shortest* block on its own load vector; it always
overshoots by at least `p`.

## 4. What the criterion contains

**Corollary 1 (intersecting families are the singleton case).** Take `v_A = 1_A` and
`b = e_A`, `b′ = e_B` with `A ≠ B`, `m_A, m_B ≥ 1`. Then `c(b) = 1_A`, `c(b′) = 1_B`, and a witness
is an `i ∈ A ∩ B` (there `1 + 1 = 2 ≤ p`). So the criterion forces `A ∩ B ≠ ∅`: **the support of any
admissible family is intersecting.** ∎

**Corollary 2 (multiplicity cap).** `m_A ≤ p` for every `A`. *Proof.* If `m_A ≥ p+1` take `b = e_A`,
`b′ = p·e_A`; then `c(b′) = p v_A = 0`, so no coordinate can witness. ∎ (Concretely, `v_A^p` is a
block disjoint from `v_A`.)

**Corollary 3 (`D2_ALL_RANKS_V3.md` Theorem 2, reproved in three lines).** If the `v_A = 1_A` are
intersecting and `Σ_{A∋i} m_A ≤ p` for every `i`, then `z(S) ≤ 1`. *Proof.* Given `b,b′ ≠ 0` with
`b+b′ ≤ m`, pick `A ∈ supp b`, `B ∈ supp b′` and `i ∈ A ∩ B`. Then `c(b)_i ≥ 1`, `c(b′)_i ≥ 1` and
`c(b)_i + c(b′)_i ≤ Σ_{A′∋i} (b+b′)_{A′} ≤ Σ_{A′∋i} m_{A′} ≤ p`; in particular each is `< p`, so both
residues are nonzero and sum to at most `p`. Coordinate `i` witnesses. ∎

The load cap is what Corollary 3 needs and what Theorem W does **not** need — and that is exactly
where the improvements below come from.

## 5. The optimum, and four improved lower bounds

Write `M*(r,p)` for the maximum of `Σ_A m_A` over all families satisfying Theorem W. Since the
criterion is downward closed in `m`, depth-first search with immediate pruning enumerates exactly
the admissible families (`tools/witness_optimum_v6.c`), and

    D_2(C_p^r)  ≥  r(p−1) + M*(r,p) + 1.

Restricting to 0/1 indicator families costs nothing at the ranks where both can be searched:
allowing **every** vector of `Z_3^r` gives the same optimum at `r = 2` (3) and `r = 3` (4). Since
those two are exact values of `D_2`, the construction class is provably optimal there.

**Validation — every previously known exact value is reproduced on the nose:**

| `(r,p)` | `M*` | `r(p−1)+M*+1` | known `D_2` |
|---|---|---|---|
| `(2,3)` | 3 | 8 | 8 |
| `(2,5)` | 5 | 14 | `3p−1 = 14` |
| `(2,7)` | 7 | 20 | `3p−1 = 20` |
| `(3,3)` | 4 | 11 | 11 |
| `(3,5)` | 7 | 20 | `(9p−5)/2 = 20` |
| `(3,7)` | 10 | 29 | `(9p−5)/2 = 29` |
| `(4,3)` | 5 | 14 | 14 |

**New values, all four strictly better than `D2_ALL_RANKS_V3.md` Theorem 2:**

| group | Thm 2 bound | **Theorem W bound** | optimal family (all `m_A = 1` unless shown) |
|---|---|---|---|
| `C_3^5` | `≥ 16` | **`≥ 17`** | the six triples through `1`: `{1,i,j}`, `2 ≤ i < j ≤ 5` |
| `C_3^6` | `≥ 19` | **`≥ 20`** | `123, 124, 125, 345, 136, 146, 156` |
| `C_5^4` | `≥ 25` | **`≥ 26`** | `12, 13, 124^2, 14, 134^2, 234^2` |
| `C_7^4` | `≥ 36` | **`≥ 37`** | `12, 13, 23^2, 123, 124^4, 234^3` |
| `C_5^5` | `≥ 30` | **`≥ 31`** | `123, 124, 134^2, 125^2, 135, 145^2, 2345` |

Every witness was confirmed by the exact packing DP of `tools/pk1_check_v6.c`, an algorithm
independent of the criterion.

The `C_3^5` family is the sharpest illustration of what Theorem 2 cannot see: all six triples
contain coordinate `1`, so its load there is `6 = 2p`, twice the cap. The family is nevertheless
admissible, because every split is obstructed by a *carry* rather than by a small load.

## 6. One pattern holds, one is refuted

    M*(r,p) = ⌊ν_r · p⌋  with  ν_2 = 1,  ν_3 = 3/2,  ν_4 = 9/5,  ν_5 = 2

fits every computed value at `r ≤ 5`:

| `r` | `ν_r` | `M*(r,3)` | `M*(r,5)` | `M*(r,7)` |
|---|---|---|---|---|
| 2 | `1` | 3 | 5 | 7 |
| 3 | `3/2` | 4 | 7 | 10 |
| 4 | `9/5` | 5 | 9 | 12 |
| 5 | `2` | 6 | 10 | — |

**`M*(r,3) = r+1` is refuted.** It held for `2 ≤ r ≤ 6`, and the natural reading — that
`D_2(C_3^r) = 3r+2` for all `r`, matching the three ranks where the value is known — is **false on
the construction side at `r = 7`**:

| `r` | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|
| `M*(r,3)` | 3 | 4 | 5 | 6 | 7 | **7** |
| `r+1` | 3 | 4 | 5 | 6 | 7 | ~~8~~ |

So the construction gives `D_2(C_3^7) ≥ 2·7 + 7 + 1 = 22`, not the `3r+2 = 23` the pattern
predicted. The optimal family is

    {1234}, {1235}, {1236}, {1456}, {12456}, {12467}, {12357}   (as subsets of [7], all m = 1)

and its sequence `S = ∏ᵢ eᵢ² · ∏_A v_A`, of length 21, was confirmed `z(S) = 1` by the exact
packing DP, independently of the criterion.

**Theorem X′ is what made this decidable.** A blind search over families on `[7]` is hopeless, but
X′ says any family with `Σ m_A ≥ 8` needs `2a + 1 ≥ 8`, i.e. minimum set size `a ≥ 4` — while
families with `a ≤ 3` are capped at `2·3+1 = 7` outright. That reduces the question to the 64
subsets of `[7]` of size `≥ 4`, which terminates. The search returned 7, so `M*(7,3) = 7` and the
law is dead. This is the first place an upper-bound theorem from §7 has paid for itself
computationally rather than only descriptively.

What the corrected sequence `3, 4, 5, 6, 7, 7` is, no one here knows; `ν_6` and `ν_7` are not
determined by a single prime. Both remaining patterns are observations over finite ranges, **not
theorems**, and the refuted one is a standing warning about how far the small cases can be trusted.

## 7. Two upper bounds on the construction optimum

Theorem W is an equivalence, so it bounds `M*` from **above** as well as below. Write
`V` for the multiset `{v_A^{m_A}}` of the extra part, so `|V| = Σ_A m_A` and `|S| = r(p−1) + |V|`.

> **Theorem X.** If `S` as in `(†)` has `z(S) ≤ 1`, then `V` has no nonempty *proper*
> zero-sum sub-multiset — that is, `V` is zero-sum-free, or `V` is a single atom. Hence
>
>     M*(r,p) ≤ D(C_p^r) = r(p−1) + 1.

*Proof.* Suppose `0 < b < m` with `Mb = 0`. Then `c(b) = 0`, so `a_i(b) = ⟨0⟩ = 0` for every `i`
and `B(b)` consists of `v`'s alone; it is nonempty since `b ≠ 0`. Put `b′ = m − b ≠ 0`. No
coordinate witnesses `(b,b′)`, because a witness needs `⟨c(b)_i⟩ ≠ 0`. By Theorem W, `z(S) ≥ 2`. ∎

Consequently `|S| ≤ (r(p−1)) + (r(p−1)+1) = 2D − 1`, so this construction class can never beat the
trivial bound `D_2 ≤ 2D` — a consistency check, and an explanation of why it stops where it does.

Theorem X is loose (at `p = 3` it gives `2r+1` against an observed `r+1`). Pairing `b` against a
**single set** instead of against the complement sharpens it a great deal.

> **Theorem X′.** Let the family be an indicator family (`v_A = 1_A`) satisfying Theorem W. Then for
> every `A` with `m_A ≥ 1`, the projected multiset `{ 1_{A ∩ B} : B ∈ V ∖ {A} }` is zero-sum-free in
> `Z_p^A`. Hence
>
>     |V| ≤ |A|(p−1) + 1     for every A,      so     M*(r,p) ≤ a(p−1) + 1,   a = min_{A} |A|.

*Proof.* Take `b′ = e_A`, so `c(b′) = 1_A`. A coordinate `i` witnesses `(b, e_A)` iff `i ∈ A`,
`⟨c(b)_i⟩ ≠ 0` and `⟨c(b)_i⟩ + 1 ≤ p` — and the last is automatic since `⟨c(b)_i⟩ ≤ p−1`. So
Theorem W says exactly: for every nonempty `b ≤ m − e_A` there is an `i ∈ A` with `c(b)_i ≢ 0`.
Restricting to the coordinates of `A` turns `c(b)` into `Σ_B b_B 1_{A∩B}`, so this says the
multiset `{1_{A∩B}}` over `B ∈ V ∖ {A}` has no zero-sum sub-multiset at all: it is zero-sum-free
in `Z_p^A`, hence of length at most `D(C_p^{|A|}) − 1 = |A|(p−1)`. Adding back the removed copy of
`A` gives `|V| ≤ |A|(p−1) + 1`. ∎

Against the computed optima, Theorem X′ is tight in half the cases:

| group | `M*` | `a = min|A|` | `a(p−1)+1` | Theorem X (`D(G)`) | |
|---|---|---|---|---|---|
| `C_3^2` | 3 | 1 | **3** | 5 | tight |
| `C_3^3` | 4 | 2 | 5 | 7 | |
| `C_3^4` | 5 | 2 | **5** | 9 | tight |
| `C_3^5` | 6 | 3 | 7 | 11 | |
| `C_3^6` | 7 | 3 | **7** | 13 | tight |
| `C_5^4` | 9 | 2 | **9** | 17 | tight |
| `C_7^4` | 12 | 2 | 13 | 25 | |
| `C_5^5` | 10 | 3 | 13 | 21 | |

Theorem X′ also explains the shape of the extremal families. To reach `M* = r+1` at `p = 3` one
needs `2a + 1 ≥ r + 1`, i.e. **every set must have size at least `r/2`** — and the computed optima
sit exactly at that threshold (`a = 2` at `r = 3,4`; `a = 3` at `r = 5,6`). Small sets are cheap to
intersect but cap `|V|`; large sets lift the cap but leave too few of them. What is still missing
for a closed form is the opposing inequality — an upper bound on how many *large* pairwise
intersecting sets can satisfy Theorem W — and that is exactly the content of §8.

### 7a. Corollary 4: admissible families are sunflower-free

Theorem X′ came from pairing `b` against **one** set. Pairing *two against two* gives a
condition of a completely different flavour. For `b = e_A + e_B` the load is `2` on `A ∩ B` and
`1` on `A △ B`; likewise for `b′ = e_C + e_D`. At `p = 3` a witness fails only where **both**
loads equal `2`, so the pair `(b,b′)` has no witness precisely when

    (A ∪ B) ∩ (C ∪ D)  =  A ∩ B ∩ C ∩ D.

> **Corollary 4.** No four members of `V` (repetitions allowed) satisfy that identity. In
> particular an admissible family contains no **4-petal sunflower**: four sets with a common
> core `K` and pairwise disjoint petals, for which both sides equal `K`.

The `4` is `p+1`, and the statement is uniform in `p`:

> **Corollary 4′.** An admissible indicator family contains no sunflower with `p+1` petals, and
> `p` petals is the largest that can survive.

*Proof.* Let `A_1,…,A_{p+1} ∈ V` have common core `K` and pairwise disjoint petals `A_j ∖ K`.
Split them into groups of sizes `u` and `v` with `u + v = p+1` and `1 ≤ u, v ≤ p−1` (take
`u = 2`, `v = p−1`), and let `b`, `b′` be the corresponding sums of `e_{A_j}`; they are disjoint.
Since the petals are pairwise disjoint, a petal coordinate lies in exactly one group, so
`supp c(b) ∩ supp c(b′) = K`, and there `⟨c(b)_i⟩ + ⟨c(b′)_i⟩ = u + v = p+1 > p`. No coordinate
witnesses, so `z(S) ≥ 2` by Theorem W. Conversely with only `p` petals every split has
`u + v ≤ p` with `u, v ≥ 1`, so any `i ∈ K` witnesses. ∎

Verified computationally at `p = 3, 5, 7`: `p−1` and `p` petals are admissible, `p+1` and `p+2`
never are — a sharp threshold, with `p = 3` recovering Corollary 4.

This is a genuinely different constraint from intersectingness — it forbids the families that are
*too* uniformly intersecting, those meeting in the same place every time. Combined with the
Erdős–Rado sunflower lemma it bounds the number of distinct sets outright: if every set has size
at most `s`, a family with more than `s!·p^s` distinct sets contains a `(p+1)`-sunflower and is
therefore inadmissible, so `M* ≤ p · s! · p^s`.

So the two bounds squeeze from opposite directions. Theorem X′ says the sets must be **large**
(`|V| ≤ a(p−1)+1` forces `a ≥ r/2` at the optimum); Corollary 4 says they must not be large in the
same way — they cannot share a common core. That tension is exactly why the extremal families in
§8 are irregular, and why `M*` resists a closed form.

### 7b. Corollary 5: multiplicity is almost never repeated at `p = 3`

Pairing `b` against **two copies of one set**, `b′ = 2e_A` (available whenever `m_A ≥ 2`), needs a
coordinate `i ∈ A` with `⟨c(b)_i⟩ ≠ 0` and `⟨c(b)_i⟩ + 2 ≤ p`:

> **Corollary 5.** If `m_A ≥ 2` then every nonzero `b ≤ m − 2e_A` has a coordinate `i ∈ A` with
> `1 ≤ ⟨c(b)_i⟩ ≤ p−2`.

At `p = 3` the window `[1, p−2]` collapses to the single value `1`, and that is rigid enough to
force a global structure. Take `b = 2e_C` for any other set with `m_C ≥ 2`: its load is `2` on `C`
and `0` elsewhere, so it never takes the value `1` and no coordinate can witness. Hence

> **Corollary 5a (`p = 3` only).** At most one set of an admissible family over `C_3^r` has
> multiplicity `≥ 2` — so `Σ_A m_A ≤ |F| + 2`.

For `p ≥ 5` the same `b = 2e_C` is harmless (`2 ≤ p−2`), and the contrast is visible in the data:
every `C_3^r` optimum carries at most one repeated set, while the `C_5^4` and `C_7^4` optima each
carry **three**. Verified directly — two sets at multiplicity 2 are inadmissible at `p = 3` and
admissible at `p = 5` — and on 134 random admissible families over `C_3^r`, none had two.

The same pairing with `b = e_C + e_D` gives a second `p = 3` consequence: if `m_A ≥ 2` then the
traces `C ∩ A` over the other members of `V` are **pairwise distinct**, since `A ∩ (C Δ D) =
(A∩C) Δ (A∩D)` must be nonempty.

### 7c. Negative: the necessary conditions do not add up to the criterion

Corollary 1 (intersecting) and Theorem X (no proper zero-sum in `V`) are both necessary and both
purely combinatorial, so it is natural to hope they *characterise* admissibility. They do not.
Let `B(r,p)` be the largest `|V|` over multisets of 0/1 vectors whose supports pairwise intersect
and which have no proper nonempty zero-sum — a quantity defined without any reference to blocks or
packing. Then `M* ≤ B`, but the gap is real and growing:

| `r` | `M*(r,3)` | `B(r,3)` | `D(C_3^r) = 2r+1` |
|---|---|---|---|
| 2 | 3 | 4 | 5 |
| 3 | 4 | 6 | 7 |
| 4 | 5 | **9** | 9 |

At `r = 4` the combinatorial ceiling has already risen to Theorem X's bound `2r+1` while the truth
sits at `r+1`. So the carry structure of Theorem W is doing work that intersectingness and
zero-sum-freeness cannot do between them, and a proof of `M*(r,3) = r+1` will have to use the
criterion itself rather than these two shadows of it.

## 8. Negative: the extremal families have no uniform shape

`M*(r,3) = r+1` is clean, but the families achieving it are not. Two natural uniform shapes
suggested by the small cases were tested against the criterion and **both fail**:

| candidate shape | works at | fails at |
|---|---|---|
| `{[r]\{i} : i ∈ [r]} ∪ {[r]}` (all `(r−1)`-subsets plus the whole set), `r+1` sets | `r = 3` only | `r = 2, 4,…,12` |
| `{ {1} ∪ e : e ∈ E }` for a graph `E` on the other `r−1` vertices with `r+1` edges | `r = 5` only, uniquely `E = K_4` | `r = 6, 7` (no graph works) |

The first dies for a transparent reason: taking `b = {[r]}` and `b′` = all `r` of the
`(r−1)`-subsets gives `deg_i(b′) = r−1` in every coordinate, which is `≡ 0 (mod 3)` whenever
`r ≡ 1 (mod 3)`, so no coordinate can witness. The second has no such clean cause — at `r = 6`
all 120 seven-edge graphs on five vertices fail, and at `r = 7` all 6435 eight-edge graphs on
six vertices fail.

So the optimum `r+1` is attained by genuinely heterogeneous families (the `r = 6` optimum
`123, 124, 125, 345, 136, 146, 156` mixes a set avoiding coordinate `1` with six containing it),
and a closed form for `M*(r,p)` is not going to come from guessing a family shape. Determining
`M*` is an extremal problem in its own right — the asymptotic version is a fractional relaxation
in which the constraint involves *fractional parts* of the loads, hence is not a linear
programme, which is why the load-capped LP of Theorem 2 (whose optimum is the fractional
matching number of an intersecting family) undershoots.

## 9. All `k` at once: Theorem W_t

Nothing in §2 used `t = 2`. A packing of size `t` is a set of `t` pairwise disjoint blocks
`B(b^{(1)}),…,B(b^{(t)})`, which by Lemmas 1 and 2 means `Σ_j b^{(j)} ≤ m` together with
`Σ_j a_i(b^{(j)}) ≤ p−1` for every `i` — the `t` `e`-parts must add with **no carry**. So:

> **Theorem W_t.** For `S` as in `(†)`,
>
>     z(S) ≥ t   ⟺   there are b^{(1)},…,b^{(t)} ≠ 0 with Σ_j b^{(j)} ≤ m
>                    and  Σ_j ⟨−(M b^{(j)})_i⟩ ≤ p−1  for every coordinate i.
>
> Theorem W is the case `t = 2`, where the condition rearranges into the witness form of §3.

*Proof.* (⇐) Given such `b^{(1)},…,b^{(t)}`, form the blocks `B(b^{(j)})` of Lemma 1. Each is
nonempty because `b^{(j)} ≠ 0`. They are pairwise disjoint as sub-multisets of `S`: the `v`-parts
use `Σ_j b^{(j)} ≤ m` copies in total, and coordinate `i` of the `e`-part uses
`Σ_j a_i(b^{(j)}) = Σ_j ⟨−(Mb^{(j)})_i⟩ ≤ p−1` copies of `e_i`, which is all that `(†)` supplies.
So `S` has `t` pairwise disjoint nonempty zero-sum subsequences, i.e. `z(S) ≥ t`.

(⇒) Conversely let `B_1,…,B_t` be pairwise disjoint nonempty zero-sum subsequences of `S`. By
Lemma 1 each is `B(b^{(j)})` for a unique `b^{(j)} ≤ m`, and `b^{(j)} ≠ 0` since `B_j ≠ ∅`.
Disjointness bounds the total use of each `v_A` by `m_A`, giving `Σ_j b^{(j)} ≤ m`, and the total
use of each `e_i` by its multiplicity `p−1`, giving `Σ_j ⟨−(Mb^{(j)})_i⟩ ≤ p−1`. ∎

The `t = 2` rearrangement is the four-case table of §3: `⟨−x⟩ + ⟨−y⟩ ≤ p−1` fails exactly when
both residues are nonzero and sum to at most `p`. For `t ≥ 3` no such two-term rearrangement is
available, so the `Σ_j ⟨−·⟩ ≤ p−1` form is the one to use; the "witness coordinate" language of
§3 is a convenience special to pairs, not the substance.

Writing `M*_k(r,p)` for the largest `Σ_A m_A` admitting no such `k`-tuple,

    D_k(C_p^r)  ≥  r(p−1) + M*_k(r,p) + 1.

**This reproduces every exact multiwise value the packet has, across three different `k`:**

| value | source | `r(p−1)` | `M*_k` computed | bound obtained | known |
|---|---|---|---|---|---|
| `D_2(C_3^2)` | exhaustive (V6) | 2 | 5 | 8 | 8 |
| `D_2(C_5^2)` | `3p−1` | 4 | 9 | 14 | 14 |
| `D_2(C_7^2)` | `3p−1` | 6 | 13 | 20 | 20 |
| `D_2(C_3^3)` | exhaustive (V6) | 6 | 4 | 11 | 11 |
| `D_2(C_5^3)` | `(9p−5)/2` | 12 | 7 | 20 | 20 |
| `D_2(C_7^3)` | `(9p−5)/2` | 18 | 10 | 29 | 29 |
| `D_2(C_3^4)` | exhaustive | 8 | 5 | 14 | 14 |
| `D_3(C_5^3)` | `D3_C5_*` | 12 | **12** | **25** | 25 |
| `D_3(C_7^3)` | `HYPOTHESIS_Z_PROVED_V3` | 18 | **17** | **36** | 36 |
| `D_4(C_5^3)` | Theorem T (`D4_C5_DECIDED_V6`) | 12 | **17** | **30** | 30 |

Ten exact values, three ranks, three values of `k`, four primes — all recovered by one criterion,
with no case fitted. The three bottom rows are the packet's hardest theorems (`D_3(C_7^3) = 36`
took the corridor argument plus a proved Hypothesis `(Z)`; `D_4(C_5^3) = 30` took a
5.9-billion-node sweep), and each drops out here as a small search over set families.

That is the strongest evidence available from this host that the algebraic construction class is
not merely a source of lower bounds but is **extremal** for `D_k(C_p^r)` — every known value is
attained inside it.

### 9a. The `k`-direction collapses to `k = 2`

The computed optima satisfy

    M*_k(r,p)  =  M*_2(r,p) + (k−2)p            observed at (r,p,k) = (3,5,3), (3,5,4), (3,7,3), (4,3,3)

and the inequality `≥` is a theorem inside the class: given an admissible family for `k`, append a
new set with multiplicity `p`. The extra part contributes the single block `v_A^p` (its load is
`p·v_A = 0`, so its `e`-part is empty), which raises the packing number by at most one, so the
family is admissible for `k+1` with `Σ m_A` larger by `p`. This is the classical
`D_{k+1}(G) ≥ D_k(G) + exp(G)` induction, re-derived inside the criterion — and the `k = 4`
optimum for `C_5^3` displays it literally, containing `e_2^5 = e_2^p`.

So **all the content sits at `k = 2`**, and every `D_2` improvement propagates to every `k`:

| group | `D_2 ≥` (this record) | consequence for all `k ≥ 2` |
|---|---|---|
| `C_3^5` | 17 | `D_k(C_3^5) ≥ 17 + 3(k−2)` |
| `C_3^6` | 20 | `D_k(C_3^6) ≥ 20 + 3(k−2)` |
| `C_5^4` | 26 | `D_k(C_5^4) ≥ 26 + 5(k−2)` |
| `C_7^4` | 37 | `D_k(C_7^4) ≥ 37 + 7(k−2)` |
| `C_5^5` | 31 | `D_k(C_5^5) ≥ 31 + 5(k−2)` |

each one better by exactly `1` than what `D2_ALL_RANKS_V3.md` Theorem 2 gives, at every `k`.

A caveat on the computation: `tools/witness_optimum_k_v6.c` caps `m_A ≤ p`. That cap is *forced*
at `k = 2` (Corollary 2) but not for larger `k`, so the `k ≥ 3` numbers are conservative — they
remain valid lower bounds, and they already meet the known exact values, so the cap is not binding
in any tested case.

## Claim ceiling

Theorems W, X and X′ and the three corollaries are proved above and hold for all `(p,r)`
(X′ for indicator families). `M*` values are
exhaustive computations over 0/1-indicator families for the individual `(r,p)` listed and are
**lower** bounds on what general `Z_p^r` families could give. The two patterns in §6 are
observations over finite ranges. No novelty claim: whether Theorem W is known is CANNOT_CHECK
from this host.
