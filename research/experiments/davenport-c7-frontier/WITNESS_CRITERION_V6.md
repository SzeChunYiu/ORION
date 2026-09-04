# The witness-coordinate criterion: an exact packing test for algebraic families — V6

Status: **criterion proved (Theorem W) and machine-verified; four published lower bounds in
`D2_ALL_RANKS_V3.md` improved.** The criterion contains that record's Theorem 2 as the
special case of one-element pairs. Priority CANNOT_CHECK.
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

## 6. Two patterns

    M*(r,3) = r + 1      for 2 ≤ r ≤ 6,     hence   D_2(C_3^r) ≥ 3r + 2
    M*(r,p) = ⌊ν_r · p⌋  with  ν_2 = 1,  ν_3 = 3/2,  ν_4 = 9/5,  ν_5 = 2

`D_2(C_3^r) = 3r+2` holds at every rank where the value is known (`r = 2, 3, 4`: values `8, 11, 14`),
so it is the natural conjecture; `r = 5` is being decided by exhaustive search separately. The
second pattern fits every computed value at `r ≤ 5`:

| `r` | `ν_r` | `M*(r,3)` | `M*(r,5)` | `M*(r,7)` |
|---|---|---|---|---|
| 2 | `1` | 3 | 5 | 7 |
| 3 | `3/2` | 4 | 7 | 10 |
| 4 | `9/5` | 5 | 9 | 12 |
| 5 | `2` | 6 | 10 | — |

At `r = 6` only `M*(6,3) = 7` is computed, which forces `ν_6 ∈ [7/3, 8/3)` if the shape persists —
a jump that does **not** continue the decreasing increments `1 → 3/2 → 9/5 → 2`, so either `ν_6`
breaks the pattern or `M*` is not exactly `⌊ν_r p⌋` at every rank. Both patterns are observed
regularities over the ranges shown, **not theorems**.

## Claim ceiling

Theorem W and its three corollaries are proved above and hold for all `(p,r)`. `M*` values are
exhaustive computations over 0/1-indicator families for the individual `(r,p)` listed and are
**lower** bounds on what general `Z_p^r` families could give. The two patterns in §6 are
observations over finite ranges. No novelty claim: whether Theorem W is known is CANNOT_CHECK
from this host.
