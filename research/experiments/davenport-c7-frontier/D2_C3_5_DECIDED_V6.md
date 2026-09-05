# `D_2(C_3^5) = 17` — decided by exhaustive search — V6

Status: **proved**, given Olson's `D(C_3^5) = 11` and this packet's `D_2(C_3^4) = 14`.
Determines a value the packet previously bracketed as `D_2(C_3^5) ∈ [16, 20]`, and which
`D2_ALL_RANKS_V3.md` bounded only as `≥ 16`.
Tools: `tools/enum_rank_generic_v3.c` (sweep), `tools/pk1_check_v6.c` (witness).
Checker: `verify_witness_criterion_v6.py` step 6 covers the lower-bound witness.

## 1. Statement

> **Theorem.** `D_2(C_3^5) = 17`. Equivalently, the longest sequence over `C_3^5` with no two
> disjoint nonempty zero-sum subsequences has length 16.

## 2. Lower bound: an explicit witness

From the witness-coordinate criterion (`WITNESS_CRITERION_V6.md`), the optimal family at `r = 5`
is the six triples through coordinate 1, giving

    S = e_1^2 e_2^2 e_3^2 e_4^2 e_5^2 · ∏_{2 ≤ i < j ≤ 5} (e_1 + e_i + e_j),      |S| = 16.

`z(S) = 1` was confirmed by the exact packing DP of `tools/pk1_check_v6.c`, an algorithm
independent of the criterion. Hence `D_2(C_3^5) ≥ 17`. Note all six triples contain coordinate 1,
whose load is therefore `6 = 2p` — twice the cap of `D2_ALL_RANKS_V3.md` Theorem 2, which is why
that record could only reach 16.

## 3. Upper bound: the sweep

Suppose `S` over `C_3^5` has `|S| = 17` and `z(S) ≤ 1`.

1. **Every block is long.** If `A ⊆ S` is a nonempty zero-sum then `S·A^{-1}` is zero-sum-free
   (else two disjoint blocks), so `|S| − |A| ≤ D(C_3^5) − 1 = 10`, giving `|A| ≥ 7`. So `S` has
   **no zero-sum subsequence of length `≤ 6`**.
2. **`S` spans.** Otherwise `S` lies in a subgroup `≅ C_3^s` with `s ≤ 4`, and
   `|S| = 17 ≥ D_2(C_3^4) = 14` forces `z(S) ≥ 2`.
3. **Normal form.** By 2, `S` contains a basis, which `GL(5,3)` maps to `e_1,…,e_5`; the remaining
   12 terms are enumerated in nondecreasing index order.

An exhaustive depth-first search over that normal form, pruning on the length-`≤ 6` condition of
step 1, was run to completion:

| | shards | nodes | leaves | witnesses |
|---|---|---|---|---|
| 16-way, classes `{0,2,4,8,12}` | 5 | 419,118,356 | 0 | 0 |
| 64-way, the other 11 classes | 44 | 2,311,473,279 | 0 | 0 |
| **total** | **49** | **2,730,591,635** | **0** | **0** |

Coverage is exact: a 16-way shard `i` takes first-free-element `g ≡ i (mod 16)`, a 64-way
sub-shard `j` takes `g ≡ j (mod 64)` and so lies inside class `j mod 16`, and the four `j ≡ i`
partition class `i`. All 16 residue classes are accounted for.

**Zero leaves** — no length-17 sequence even survives the short-zero-sum prune, let alone has
`z ≤ 1`. So no such `S` exists, the longest `z ≤ 1` sequence has length 16, and `D_2(C_3^5) = 17`. ∎

## 4. Consequences

- `D_k(C_3^5) = 17 + 3(k−2)` for `k ≥ 2` would follow if the upper bound propagated; what is
  established here is `D_k(C_3^5) ≥ 17 + 3(k−2)`, by the Freeze–Schmid arithmetic-progression
  argument (see `WITNESS_CRITERION_V6.md` §9a).
- It is a fourth exact `D_2(C_3^r)` value: `8, 11, 14, 17` at `r = 2,3,4,5`. Those match `3r+2` —
  but see §6 of the criterion record: `M*(7,3) = 7` **refutes** `3r+2` as a general law on the
  construction side, so the agreement at `r ≤ 5` is not evidence for `r ≥ 6`.

## 5. Reproduction

    gcc -O2 -o enumr tools/enum_rank_generic_v3.c
    for j in 0..63: ./enumr 3 5 17 6 --shard $j 64        # ~2.7e9 nodes total

Each shard prints `leaves=0 found=0`. The run is far too long for CI (hours of core time), so it
is recorded here rather than wired in, exactly as the `D_4(C_5^3)` sweep is; the cheap half — the
length-16 witness — is verified in CI by `verify_witness_criterion_v6.py` step 6.

## Claim ceiling

Machine-assisted. Depends on Olson's `D(C_3^5) = 11` (classical) and this packet's
`D_2(C_3^4) = 14` (exhaustive, CI-verified). The sweep used the enumerator at `N = 243`, inside
every buffer bound in that tool. Not reviewed by a mathematician; novelty CANNOT_CHECK.
