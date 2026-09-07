# A general lower bound for all `k`, and an `η`-induction that closes `C_3^3` completely — V3

Status: **proved** (hand proofs below; both are elementary and self-contained given `D(C_n^3) = 3n−2`). Machine-verified: `verify_tk_family_v3.py`. Novelty: **not claimed** — the `k = 2` case is donor-owned and the general statement follows from the donor step inequality `D_{k+1} ≥ D_k + exp(G)`; what is new *here* is only that the packet no longer depends on unreadable donor text for it. Priority CANNOT_CHECK.
Branch: `claude/orion-research-frontier-3ck9yt`.

## 1. The family `T_k(n)`

For odd `n ≥ 3` and `k ≥ 2` put, in the basis `e_1,e_2,e_3` with `e_12 = e_1+e_2`, `e_13 = e_1+e_3`, `e_23 = e_2+e_3`,

    T_k(n) = e_1^{(k−1)n−1} · e_2^{n−1} · e_3^{n−1} · e_12^{(n+1)/2} · e_13^{(n−1)/2} · e_23^{(n−1)/2}.

Its length is

    |T_k(n)| = ((k−1)n−1) + 2(n−1) + (n+1)/2 + (n−1) = ((2k+5)n − 7)/2.

**Theorem 1.** `pk(T_k(n)) = k−1` for every odd `n ≥ 3` and every `k ≥ 2`. Hence

    D_k(C_n^3) ≥ ((2k+5)n − 5)/2      for every odd n and every k ≥ 2.

*Proof.* Write `m` for the multiplicity vector and `c_j` for integer coordinate sums. Then

    c_1 = m_1 + m_12 + m_13 = ((k−1)n−1) + (n+1)/2 + (n−1)/2 = kn − 1,
    c_2 = m_2 + m_12 + m_23 = (n−1) + (n+1)/2 + (n−1)/2 = 2n − 1,
    c_3 = m_3 + m_13 + m_23 = (n−1) + (n−1)/2 + (n−1)/2 = 2n − 2.

**`pk ≥ k−1`.** The `k−2` blocks `e_1^n` use `(k−2)n` copies of `e_1`, and `e_1^{(n−1)/2} e_2^{(n−1)/2} e_12^{(n+1)/2}` is a further, disjoint zero-sum block (both coordinates sum to `n`); it needs `(n−1)/2` more copies of `e_1`, and `(k−2)n + (n−1)/2 ≤ (k−1)n − 1` holds for every `n ≥ 1`.

**`pk ≤ k−1`.** Every zero-sum block `b ≤ m` has each `c_j(b)` a multiple of `n`. Call `b` *unary* if `c_2(b) = c_3(b) = 0`; then `b_2 = b_12 = b_23 = 0` (coordinate 2) and `b_3 = b_13 = 0` (coordinate 3), so `b = e_1^{jn}` for some `j ≥ 1`. Now:

- *At most one block has `c_2 > 0`*, since `c_2 = 2n−1 < 2n` and each such block has `c_2 ≥ n`. Likewise *at most one block has `c_3 > 0`* (`c_3 = 2n−2 < 2n`). Hence **at most two blocks are non-unary**.
- *A non-unary block with `c_1 = 0` uses both `c_2` and `c_3`.* If `c_1(b) = 0` then `b_1 = b_12 = b_13 = 0`; if also `c_3(b) = 0` then `b_23 = 0` and `b = e_2^{b_2}` needs `b_2 = n > n−1 = m_2`, impossible; symmetrically for `c_2(b) = 0`. So a non-unary block avoiding `c_1` must occupy **both** `c_2` and `c_3`, and by the previous point there can be at most one non-unary block in total in that case.

Split by the number `t` of non-unary blocks.

*`t = 2`.* By the second point each of them has `c_1 ≥ n`, so they consume `≥ 2n` of `c_1 = kn − 1`, leaving `< (k−2)n` for unary blocks; as each unary block consumes a positive multiple of `n`, there are at most `k−3` of them, and the total is `≤ 2 + (k−3) = k−1`.

*`t = 1`.* If that block uses `c_1`, the same count leaves `< (k−1)n` for unary blocks, i.e. at most `k−2`, total `≤ k−1`. If it does not use `c_1`, unary blocks only consume copies of `e_1`, of which there are `m_1 = (k−1)n − 1 < (k−1)n`, so again at most `k−2`, total `≤ k−1`.

*`t = 0`.* All blocks are powers of `e_1`, at most `⌊m_1/n⌋ = k−2`.

In every case `pk ≤ k−1`. ∎

The proof uses only that `n` is odd (so `(n±1)/2 ∈ Z`); `n` need not be prime. Machine check: `verify_tk_family_v3.py` recomputes `pk(T_k(n))` exactly for `n ∈ {3,5,7}` and `k ≤ 6`.

`T_2(n)` is the family `S_2(n)` of `CUBE_FAMILY_LOWER_BOUNDS_V2.md`; `T_k` for `k ≥ 3` is **not** cube-supported in the earlier sense, because `m(e_1) = (k−1)n−1 ≥ n`. That single observation forces a correction to several earlier claims and is treated separately in `CORRECTION_MULTIPLICITY_CAP_V3.md`.

## 2. The `η`-induction

Recall `η(G)`: the least `ℓ` such that every sequence over `G` of length `ℓ` has a nonempty zero-sum subsequence of length **at most `exp(G)`**.

**Theorem 2.** Let `G` be a finite abelian group, `k ≥ 1`. If `D_k(G) + exp(G) ≥ η(G)` then

    D_{k+1}(G) ≤ D_k(G) + exp(G).

*Proof.* Let `|S| = D_k(G) + exp(G) ≥ η(G)`. Then `S` has a nonempty zero-sum `U` with `|U| ≤ exp(G)`, so `|S U^{−1}| ≥ D_k(G)` and `S U^{−1}` has `k` disjoint nonempty zero-sum subsequences; together with `U` that is `k+1`. ∎

Once the hypothesis holds it keeps holding (the left side only grows), so the sequence `(D_k)` becomes arithmetic with difference `exp(G)` from the first `k` at which `D_k(G) + exp(G) ≥ η(G)`. This is the elementary mechanism behind the eventual-arithmetic phenomenon; the content is *where* it switches on.

**Corollary 3 (the switch-on point for `C_n^3`).** Assume `η(C_n^3) = 8n−7` and the conjectured value `D_k(C_n^3) = ((2k+5)n−5)/2`. Then `D_k + n ≥ η` reads `(2k−9)n ≥ −9`, so the induction is available for every `k ≥ 5`, and already for `k ≥ 4` when `n ≤ 9`. Consequently:

- **`n = 7`:** if `D_4(C_7^3) = 43` and `η(C_7^3) = 49`, then `D_k(C_7^3) = ((2k+5)·7−5)/2` for **all** `k ≥ 4`. The frozen question `k = 3` is therefore an isolated case: `k = 2` is settled, and everything from `k = 4` upward reduces to a single value plus `η`.
- **`n = 5`:** `D_4(C_5^3) = 30` together with `η(C_5^3) = 33` would settle every `k ≥ 4`.

## 3. `C_3^3` is completely determined

**Theorem 4.** `D_k(C_3^3) = 3k + 5` for every `k ≥ 2`.

*Proof.* Lower bound: Theorem 1 with `n = 3` gives `D_k ≥ (9k+25−25+…)`, concretely `((2k+5)·3−5)/2 = 3k+5`.

Upper bound. `D_2 = 11` and `D_3 = 14` are the exhaustive frames of `EXHAUSTIVE_ANALOG_RESULTS_V2.md` (whose multiplicity cap is justified in `CORRECTION_MULTIPLICITY_CAP_V3.md` §2 for exactly these upper-bound frames). Next, `η(C_3^3) ≤ 17`: a sequence of length 17 either has an element of multiplicity `≥ 3`, giving a zero-sum of length `3 = exp`, or has all multiplicities `≤ 2`, and the frame `3 17 2 3 3` reports **no leaves at all** — every such sequence already contains a zero-sum subsequence of length `≤ 3`. Since `D_3 + 3 = 17 ≥ η(C_3^3)`, Theorem 2 gives `D_4 ≤ 17`, and inductively `D_{k+1} ≤ D_k + 3` for every `k ≥ 3`, i.e. `D_k ≤ 3k+5` for all `k ≥ 3`. ∎

In particular `D_5(C_3^3) = 20`, `D_6(C_3^3) = 23`, and so on: the whole sequence, from the packet's own computations, with no unreadable donor input. (The values are very likely classical; no priority is claimed.)

## Claim ceiling

Theorem 1 and Theorem 2 are proved for all the stated parameters. Corollary 3 is conditional on `η(C_n^3) = 8n−7` (verified here only for `n = 3`) and on the quoted `D_4` values, neither of which is established for `n = 5, 7`. Theorem 4 depends on the two `C_3^3` upper-bound frames and on the `η ≤ 17` frame, all of which are replayable by `run_exhaustive_analogs_v2.sh`.
