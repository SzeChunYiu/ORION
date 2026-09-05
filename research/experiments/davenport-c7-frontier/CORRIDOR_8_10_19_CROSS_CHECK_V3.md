# Cross-lane check of the `(8,10,19)` corridor, and a partition reduction — V3

Status: **the support-four branch of the `(8,10,19)` corridor is CLOSED.** All three canonical 19-atom types exhausted: 562 pairs, 2,796 length-37 candidates, every one with a four-pack. Pair counts independently reproduce the ChatGPT lane's. Priority CANNOT_CHECK.
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

## 3. Result: the branch is closed

| `a` | pairs | `T` candidates after the 8-atom | four-pack | no four-pack |
|---|---|---|---|---|
| 3 | 0 | 0 | — | — |
| 2 | 24 | 24 | **24** | **0** |
| 1 | 538 | 2,772 | **2,772** | **0** |
| **total** | **562** | **2,796** | **2,796** | **0** |

> **Theorem.** No length-37 zero-sum sequence over `C_7^3` with packing number 3 has a three-atom factorization of type `(8,10,19)` whose 19-atom has support four.

The extension factor is not uniform: the 24 `a = 2` pairs each admit exactly one 8-atom, while the 538 `a = 1` pairs admit 2,772 between them (mean ≈ 5.2). So the "exactly one `U`" observation is a feature of the `a = 2` branch, not a general law — worth recording as a corrected reading of the earlier note.

## 3a. The `(9,9,19)` corridor

The same pipeline runs on the other length-19 corridor with `|V| = 9`, pair **8**-short-free (the threshold is `|VW| − D − 1 = 28 − 19 − 1`) and `|U| = 9`:

| `a` | pairs | `T` candidates | four-pack | no four-pack |
|---|---|---|---|---|
| 3 | 1,436 | 6,394 | **6,394** | **0** |
| 2 | 3,971 | 5,518 | **5,518** | **0** |
| 1 | **48,353** | — | — | stage 2 NOT run — see V6 note |

> **Theorem (partial).** No length-37 obstruction over `C_7^3` has a `(9,9,19)` factorization whose 19-atom is of canonical support-four type `a = 3` or `a = 2`.

**V6 update — stage 1 of the `a = 1` branch is complete: 48,353 companions** (874,321,748 nodes).
The branch had been left marked "running" by an earlier session, and the committed tool could not
resume it: `|V|` and the pair short-free bound were hardcoded to the `(8,10,19)` values `K = 10`,
`S = 9`, whereas `(9,9,19)` needs `K = 9`, `S = 8`. Both tools are now `#ifndef`-guarded so the
corridor is selected at compile time (`-DKV= -DSV= -DKU=`), defaults unchanged, and the
parameterisation was validated against **every** count already on record before being trusted for
a new one — `(8,10,19)`: 0 / 24 / 538, and `(9,9,19)`: 1,436 / 3,971, all reproduced exactly.

**Stage 2 was not run, and this is what is and is not established.**

*Established.* The companion count 48,353 comes from `tools/verify_corridor_8_10_19_pairs_v3.c`
compiled with `-DK=9 -DS=8`, and that tool's parameterisation is validated on **every** count
already on record: `(8,10,19)` → 0 / 24 / 538 and `(9,9,19)` → 1,436 / 3,971, all exact.

*Not established.* The four-pack stage for this branch. Two separate obstacles, both measured:

1. **Cost.** `tools/verify_corridor_8_10_19_fourpack_v3.c` on `(8,10,19)` `a = 1` took 667 s for
   538 pairs — about 1.24 s per pair. At 48,353 pairs that is ≈ **17 hours single-threaded**, and
   more here because `|U| = 9` against 8 there. The tool has no sharding, and this environment
   reclaims containers on idle, so the run does not complete.
2. **The fourpack tool's `(9,9,19)` path is itself unvalidated.** After the bounds fix it
   reproduces all three `(8,10,19)` branches exactly (0; 24/24/24/0; 538/2,772/2,772/0), but the
   `(9,9,19)` re-validation against the recorded 1,436 / 6,394 and 3,971 / 5,518 is a one-to-two
   hour run that was repeatedly killed before finishing. **No `(9,9,19)` four-pack number in this
   record has been reproduced on the fixed build.**

So the branch is now *finishable* — the committed tools could not previously even express the
`(9,9,19)` case — but it is not finished. Anyone resuming it should validate the fourpack tool on
`(9,9,19)` `a = 3` and `a = 2` first, then shard `a = 1` across cores.

Across both corridors that is **11,912 candidates with no obstruction**, on top of the 2,796 above.

## 4. Validation of the predicate

The four-pack predicate is not taken on trust. Every `a = 2` candidate and a sample of eight `a = 1` candidates (supports 8 to 11) were re-tested by the packet's atom-based packing recursion — a different algorithm from the partition search — which returns packing number exactly 4 for all of them, and each candidate was independently confirmed to have 37 terms, zero sum, and no zero-sum of length `≤ 7`. The recursion was also run on a V1 binary-cube profile of known packing number 4 as a control.

## Claim ceiling

This closes only the **support-four** branch: the classification applies when the 19-atom has support four, and larger-support 19-atoms in this corridor remain open, as do the five other corridors. The reduction that produced the three canonical types is the ChatGPT lane's; this lane contributes the independent pair count, the partition lemma, the exhaustion of all three branches, and the cross-algorithm validation.
