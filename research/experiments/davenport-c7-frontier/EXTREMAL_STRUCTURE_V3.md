# Inverse structure of `D_k`-extremal sequences over `C_n^3` — V3

Status: **exact finite observations**. Corrected by `CORRECTION_MULTIPLICITY_CAP_V3.md`: the `k = 2` enumerations are complete, but for `k ≥ 3` every table below covers only the sequences with all multiplicities `≤ n−1`, because the enumeration cap is not justified there. Conjecture R as first stated is **refuted for `k ≥ 3`** by the family `T_k(n)`; it survives as Conjecture R′ for `k = 2`. Priority CANNOT_CHECK.
Branch: `claude/orion-research-frontier-3ck9yt`. Tools: `tools/enum_packing_v2.c`, `tools/canon_gl3.py`, `tools/cubelike_v3.py`, `tools/boxmax.c`.

A `D_k`-extremal sequence is one of length `D_k(C_n^3) − 1` with packing number `k−1`: the largest sequences that still fail to contain `k` disjoint zero-sum subsequences.

## 1. Refuted: extremal sequences are **not** cube-like

The binary cube gives the best known lower bounds for `D_2, D_3, D_4` (`DK_ARITHMETIC_CONJECTURE_V3.md`), which invites the guess that extremal sequences are essentially cube-supported. They are not. For each complete enumeration, `tools/cubelike_v3.py` tests whether the support contains a `GL(3,n)`-image of `Q` (an ordered independent triple `f_1,f_2,f_3` in the support whose four sums `f_1+f_2, f_1+f_3, f_2+f_3, f_1+f_2+f_3` are also in the support):

| family | sequences | support sizes | contain a cube image | support **is** a cube image |
|---|---|---|---|---|
| `n=3`, `D_2`-extremal (len 10) | 529 | 5, 6, 7 | 16 (3.0 %) | 16 |
| `n=3`, `D_3`-extremal (len 13) | 7 317 | 7, 8, 9 | 1 806 (24.7 %) | 99 |
| `n=3`, `D_4`-extremal (len 16) | 8 921 | 8, 9, 10 | 5 399 (60.5 %) | 0 |

So at `k = 2` **97 % of the extremal objects contain no cube at all**, and the cube-supported ones are a thin, atypical slice. Any programme that hoped to close `D_3` by classifying extremal sequences as cube-like is dead; this is recorded as a negative so it is not re-attempted. It also sharpens the reading of `CUBE_PACKING_PROFILE_V3.md`: the cube is extremal in *length* while being unrepresentative in *structure*.

## 2. Conjecture that survives: maximal multiplicity `n−1`

**Conjecture R′ (rigidity, `k = 2`).** Every `D_2`-extremal sequence over `C_n^3` (`n` odd) contains an element of multiplicity exactly `n−1`.

The `k ≥ 3` version is **false**: `T_3(3) = e_1^5 e_2^2 e_3^2 e_12^2 e_13 e_23` is `D_3(C_3^3)`-extremal with maximal multiplicity 5 (`GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md`). The `k ≥ 3` rows below are therefore evidence only about the capped subset, and are kept for that restricted reading.

Evidence (complete only for `k = 2`; the `k ≥ 3` rows are over sequences with multiplicities `≤ n−1`):

| family | sequences | max-multiplicity distribution |
|---|---|---|
| `n=3`, `k=2` (len 10) | 529 | all 2 = `n−1` |
| `n=3`, `k=3` (len 13) | 7 317 | all 2 |
| `n=3`, `k=4` (len 16) | 8 921 | all 2 |
| `n=5`, `k=2` (len 19) | 7 847 | all 4 = `n−1` |
| `n=5`, `k=3` (len 24) | 4 014 so far (enumeration running) | all 4 |
| `n=7`, `k=2` (len 28), class `m(e_1)=6` | 19 174 so far | all 6 = `n−1` by construction of the class |
| `n=7`, `k=2` (len 28), class `m(e_1)=5` | 0 found from 791 short-zero-sum-free leaves (running) | — |

An independent, complete check inside the cube: capping all multiplicities at `n−2` strictly lowers the cube capacity at every computed `n`,

| n | `c_1` with cap `n−1` | with cap `n−2` | `c_2` with cap `n−1` | with cap `n−2` |
|---|---|---|---|---|
| 5 | 19 | 18 | 24 | 21 |
| 7 | 28 | 27 | 35 | 33 |
| 9 | 37 | 36 | 46 | 45 |
| 11 | 46 | 45 | 57 | 56 |

so no cube-supported extremal sequence for `k = 2` or `k = 3` avoids multiplicity `n−1`. The loss shrinks with `n` (3, 2, 1, 1 at `k = 3`), so this is evidence, not a proof, and the `k = 3` margin should be watched at larger `n`.

**Why Conjecture R′ matters.** In `OBSTRUCTION_REDUCTION_LEMMAS_V2.md` Lemma 2.4(4), a length-36 obstruction over `C_7^3` with shortest block `u = 8` produces a length-28 sequence that is `D_2`-extremal after deleting any single element. Conjecture R′ would force a multiplicity-6 element into that object, normalising it to `e_1^6 · (rest)` and cutting the residual search by roughly the size of the multiplicity alphabet. It is the cheapest available lever on the frozen question.

## 3. Support-size profiles (complete enumerations)

`GL(3,n)`-orbit counts by support size:

- `n=3`, `k=2`: 43 orbits — support 5 (1), 6 (20), 7 (22).
- `n=3`, `k=3`: 161 orbits — support 7 (22), 8 (109), 9 (30).
- `n=3`, `k=4`: 69 orbits — support 8 (1, the profile `2^8`), 9 (44), 10 (24).
- `n=5`, `k=2`: 1 405 orbits — support 5 (2), 6 (136), 7 (582), 8 (543), 9 (133), 10 (9).
- `n=5`, `k=3`: partial, 4 014 raw sequences with supports 6 (2), 7 (335), 8 (1 854), 9 (1 414), 10 (205), 11 (8).

The minimum support size grows with `k` and the distribution shifts right, consistent with the fact that each `+1` in `k` costs one more support point in the extremal families (`DK_ARITHMETIC_CONJECTURE_V3.md`).

## 4. Maximal atoms are a different population

Over `C_5^3` there are 181 979 symmetry-reduced zero-sum-free sequences of length `D−1 = 12`; completing each by `−σ` gives a minimal zero-sum sequence of the maximal length `D(C_5^3) = 13`. Their maximal multiplicities are 4 in 136 949 cases, 3 in 44 277, and **2 in 753**. So maximal atoms need not contain an element of multiplicity `n−1`, while (Conjecture R′) `D_2`-extremal sequences appear to. The two inverse problems are genuinely different, and results about maximal atoms cannot be imported.

## Claim ceiling

§1 is about the `n = 3` enumerations only (complete for `k = 2`, capped for `k = 3, 4`); it does not assert anything for `n ≥ 5`. Conjecture R′ is a conjecture, restricted to `k = 2` where the enumeration is complete. Rows marked running/partial are execution status, not results.
