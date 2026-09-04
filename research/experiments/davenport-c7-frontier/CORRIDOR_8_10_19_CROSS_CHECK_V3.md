# Cross-lane check of the `(8,10,19)` corridor, and a partition reduction — V3

Status: **independent confirmation of the ChatGPT lane's pair counts; the `a = 2` branch closed here with two different algorithms; the `a = 1` branch in progress.** Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`, verifying `shadow/davenport-c7-frontier-20260903` at `5c0f1b53` (support-four maximal atom classification).
Tools: `tools/verify_corridor_8_10_19_pairs_v3.c`, `tools/verify_corridor_8_10_19_fourpack_v3.c`.

## 1. What was checked

`SUPPORT4_MAXIMAL_ATOM_WEIGHTS_V1.md` classifies support-four maximal atoms over `C_p^3` as `(p−1,p−1,a,p−a)`, giving three canonical 19-atoms at `p = 7`. In the `(8,10,19)` corridor a hypothetical length-37 obstruction is `T = U_8 · V_10 · W_19`, and the pair `V·W` must be **9-short-free**: a zero-sum `A ⊆ V·W` with `8 ≤ |A| ≤ 9` would leave `V·W·A^{−1}` of length `≥ 20 > D`, hence containing a block `B`, and `U, A, B` plus the nonempty remainder would be four disjoint blocks.

Independently reimplemented from that predicate — enumerating `V` in nondecreasing index order while maintaining subsums by size and pruning against `F[i] = ⋃_{j ≤ 9−i} (−σ_j(W))` — the companion counts are

| `a` | canonical `W` | companions `V` |
|---|---|---|
| 3 | `e_1^3 e_2^4 e_3^6 (3,4,6)^6` | **0** |
| 2 | `e_1^2 e_2^5 e_3^6 (2,5,6)^6` | **24** |
| 1 | `e_1^1 e_2^6 e_3^6 (1,6,6)^6` | **538** |

**These reproduce the ChatGPT lane's 0 / 24 / 538 exactly**, from a separately written program.

## 2. A partition reduction that shrinks stage 2

The four-pack test on the extended candidates does not need a packing search.

**Lemma.** Let `T` be zero-sum over `C_7^3` with `|T| = 37` and no zero-sum subsequence of length `≤ 7`. If `T` has four pairwise disjoint blocks, they **partition** `T`, and their length profile is one of

    (8,8,8,13)  (8,8,9,12)  (8,8,10,11)  (8,9,9,11)  (8,9,10,10)  (9,9,9,10).

*Proof.* Each block has length `≥ 8`, so four of them use at least 32 terms and the unused part `C` has `|C| ≤ 5`. Since `σ(T) = 0` and each block is zero-sum, `σ(C) = 0`; a nonempty zero-sum of length `≤ 5` contradicts 7-short-freeness. So `C = ∅`, the four lengths sum to 37, each is `≥ 8`, and each is `≤ 37 − 24 = 13`. ∎

This turns stage 2 from "find four disjoint blocks" into "partition into four blocks", with six admissible profiles — a strictly smaller search, and the one implemented here.

## 3. Results so far

| `a` | pairs | `T` candidates after the 8-atom | four-pack | no four-pack |
|---|---|---|---|---|
| 3 | 0 | 0 | — | — |
| 2 | 24 | 24 | **24** | **0** |
| 1 | 538 | running | running | none so far |

A structural observation from the `a = 2` branch: **each `(W,V)` pair extends to exactly one 8-atom `U`**. 24 pairs give 24 candidates, not more.

## 4. Validation of the predicate

The four-pack predicate is not taken on trust. Every `a = 2` candidate was re-tested by the packet's atom-based packing recursion — a different algorithm from the partition search — which returns packing number exactly 4 for all of them, and each candidate was independently confirmed to have 37 terms, zero sum, and no zero-sum of length `≤ 7`. The recursion was also run on a V1 binary-cube profile of known packing number 4 as a control.

## Claim ceiling

This is verification of another lane's reduction plus one lemma, not a new corridor closure by this lane. The `(8,10,19)` corridor is not closed until the `a = 1` branch completes. Five other corridors remain.
