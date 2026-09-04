# A four-atom corridor for the `D_4(C_5^3) = 31` branch — V4

Status: **proved**, given `D_3(C_5^3) = 25` and Olson. Constrains the open question `D_4(C_5^3) ∈ {30,31}`.
Checker: `verify_d4_c5_corridor_v4.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Why this is worth doing

`D_4(C_5^3) ∈ {30,31}` is open, and it decides the conjectured line `D_k(C_n^3) = ((2k+5)n−5)/2` at `n = 5`: the value 31 would falsify it at `k = 4`. `X1K_D4_C5CUBED_PROTOCOL_V1.md` leaves it open and develops the `= 31` branch; ORION-04 studies exactly the same object — "a hypothetical total-zero sequence of length 31 with no nonempty zero-sum subsequence of length at most five" — and reports bounded computational evidence through support ten.

That branch had a minimum atom length (6) but **no upper structure**: nothing said how the 31 terms distribute across atoms. This record supplies it.

## 2. The enabling lemma, with no packing hypothesis

The pointed short-atom bound of `SHORT_ATOM_BOUND_UNIFORM_V4.md` was stated for `z(C) = 2`, where every proper zero-sum is an atom. That hypothesis is not needed.

> **Lemma.** Let `C` be zero-sum over `C_p^3` with `|C| = m`, and suppose every atom of `C` has length `≥ w+1`. Then the proper nonempty zero-sum subsequences of `C` all have length in `[w+1, m−w−1]`.

*Proof.* A proper nonempty zero-sum `B` contains an atom, so `|B| ≥ w+1`. Its complement `C B^{−1}` is zero-sum and nonempty, so it contains an atom too, giving `m − |B| ≥ w+1`. ∎

No packing number appears. So the window is two-sided for **any** `k`, and the pointed system

`Σ_{ℓ} (−1)^ℓ M_ℓ C(ℓ−1, d) + (−1)^m C(m−1, d) ≡ 0 (mod p)`,  `d ≤ m − D − 1`,

must be consistent; infeasibility forces an atom of length `≤ w`. This is what lets the same machine run on a `k = 4` problem.

## 3. The bounds at `p = 5`

`D = 13`. The least `w` making the system infeasible, for every length that arises:

| `m` | 31 | 30 | 29 | 28 | 27 | 26 | 25 | 24 | 23 | 22 | 21 | 20 | 19 | 18 | 17 | 16 | 15 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `w(m)` | 7 | 7 | 7 | 8 | 7 | 7 | 7 | 7 | 8 | 7 | 7 | 7 | 7 | 8 | 7 | 7 | 7 | 7 |

So **every** zero-sum sequence over `C_5^3` of length `m ∈ [14,31]` has an atom of length `≤ 8`, and of length `≤ 7` unless `m ≡ 4 (mod 5)`. Each entry is decided by Gaussian elimination over `F_5`, twelve of the eighteen are cross-checked by exhaustive search over all `5^{|S|}` assignments, and in every case `w−1` is feasible — so no entry is vacuous.

## 4. The corridor

Let `T` be a length-31 obstruction: zero-sum, no five pairwise disjoint blocks. Atoms have length in `[6,13]` (§1 of the checker: a zero-sum of length `≤ 5` would leave `≥ 26 = D_3 + 1`, and the deletion argument produces a fifth block).

Peel: let `A_1` be a shortest atom, `|A_1| = s`. By §3 applied to `T`, `s ≤ 7`. Apply §3 to `C_1 = T A_1^{−1}` to get an atom `A_2` with `s ≤ |A_2| ≤ w(|C_1|)`, then to `C_2 = C_1 A_2^{−1}` to get `A_3`. Finally `A_4 = C_2 A_3^{−1}` **must be an atom**: if it split, `A_1, A_2, A_3` plus two blocks of `A_4` would be five disjoint blocks. Hence `6 ≤ |A_4| ≤ 13`.

> **Theorem.** A length-31 obstruction over `C_5^3` factors into four atoms whose lengths are one of
>
> `(6,6,6,13)`, `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)`, `(7,7,7,10)`.

Five profiles, from a space of 31-term sequences. In particular `T` has **at least three atoms of length `≤ 8`**, and at least two of length `≤ 7`.

## 5. What this hands the open question

1. **A finite target.** The `= 31` branch is now five length profiles rather than an unstructured 31-term search. Each is a constrained completion problem: fix a short atom, extend.
2. **A maximal-atom entry point.** `(6,6,6,13)` is the only profile with an atom of length `D(C_5^3) = 13`, so the support classification of maximal atoms applies to it and to no other profile.
3. **A flat end.** `(6,7,8,10)` and `(7,7,7,10)` have all parts `≤ 10`; those are the profiles no maximal-atom method reaches, exactly as at `p = 7`.
4. **Compatibility with the existing evidence.** ORION-04's exact searches through support ten found no obstruction. The corridor is orthogonal to support and can be combined with it.

## 6. Controls

The bound is not merely asserted. On a real packing-number-3 object over `C_5^3` of length 25, all 57 zero-sum subsequences of length `≥ 14` were checked against the predicted `w(m)`: **zero violations**. And `w−1` is feasible at every length, so the table is tight for this method rather than an artefact of an over-constrained system.

## Claim ceiling

This constrains the `D_4(C_5^3) = 31` branch; it does **not** decide `D_4(C_5^3)`, and it does not exclude any of the five profiles. `D_3(C_5^3) = 25` is used as an input and is prior ORION-RG work (X1-F), not proved here. Whether the five profiles can be closed by the support methods already in the repository is untested.
