# `D_4(C_5^3) = 30` — the last profile falls, the `p = 5` line closes — V6

Status: **proved**, given `D_3(C_5^3) = 25`. Decides a question left open as `D_4(C_5^3) ∈ {30,31}` by ORION-04 and by `X1K_D4_C5CUBED_PROTOCOL_V1.md`.
Tools: `tools/sweep_atoms_by_length_c5_v6.c`, `tools/sweep_atoms_turbo_c5_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Statement

> **Theorem T.** `D_4(C_5^3) = 30`.

## 2. The chain

**(a) Lower bound.** `T_4(5) = e_1^{14} e_2^4 e_3^4 e_{12}^3 e_{13}^2 e_{23}^2` has length 29 and `z = 3` (`GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md` Theorem 1, `verify_tk_family_v3.py`). So `D_4(C_5^3) ≥ 30`.

**(b) Suppose `D_4 > 30`.** Then some `S` of length 30 has `z(S) ≤ 3`. Put `T = S·(−σ(S))`: zero-sum, `|T| = 31`, and `z(T) ≤ z(S)+1 ≤ 4`.

**(c) `T` has no zero-sum of length `≤ 5`.** If `U ⊆ T` were one, `|T U^{−1}| ≥ 26 = D_3 + 1`; delete an element `x`, find three disjoint blocks among the remaining `≥ 25 = D_3`, and `U`, those three, and the rest (containing `x`) are five disjoint blocks — contradicting `z(T) ≤ 4`. *This is the only place `D_3(C_5^3) = 25` is used.*

**(d) Four-atom corridor.** Peeling a shortest atom and then two more by the short-atom law — with the fourth part forced to be an atom, since a split would give five blocks — leaves exactly five length profiles (`D4_C5_FOUR_ATOM_CORRIDOR_V4.md`):

`(6,6,6,13)`, `(6,6,7,12)`, `(6,7,7,11)`, `(6,7,8,10)`, `(7,7,7,10)`.

**(e) Every profile's largest part lies in `{10,11,12,13}`.** So `T` contains an atom of one of those four lengths.

**(f) It cannot.** Complete `GL(3,5)`-orbit sweeps at each length find **no** zero-sum 5-short-free length-31 sequence containing such an atom:

| `L` | pairs | distinct atoms | orbits | sweep nodes | **completions** |
|---|---|---|---|---|---|
| 13 | 6,315,607 | 998,182 | 3,325 | 284,529,220 | **0** |
| 12 | 36,202,974 | 5,603,363 | 17,141 | 1,406,175,228 | **0** |
| 11 | 89,338,594 | 13,851,427 | 39,760 | 3,674,071,087 | **0** |
| 10 | 94,515,860 | 15,289,814 | 44,111 | 5,923,695,859 | **0** |

Contradiction. So no such `S` exists, `D_4(C_5^3) ≤ 30`, and with (a) equality holds. ∎

## 3. Why the sweeps are exhaustive

An atom of length `L` is a zero-sum-free sequence of length `L−1` plus its completion. For `L ≥ 10`, `L−1 > D(C_5^2) − 1 = 8`, so the atom cannot lie in a plane: it spans rank three, contains an independent triple, and `GL(3,5)` carries that triple to `e_1,e_2,e_3`. Enumerating atoms containing `e_1,e_2,e_3` is therefore complete up to `GL(3,5)`, and canonical forms (lex-min over ordered independent triples from the support) group them into orbits exactly — two atoms sharing a canonical form are images of one another. Testing one representative per orbit suffices because "extends to a zero-sum 5-short-free length-31 sequence" is `GL`-invariant.

Orbit counts (3,325 / 17,141 / 39,760 / 44,111) are all far below the representative-array cap, so the guard of `D4_LENGTH_SWEEP_STATUS_V6.md` §2 is satisfied at every length.

## 4. Cross-checks

Every sweep was run by **two independent builds** differing in the deduplication step and in the mask-translation routine:

- orbit counts agree at `L = 10` (44,111) and `L = 11` (39,760);
- the `L = 11` sweeps agree on the node count **exactly**: 3,674,071,087;
- the `L = 10` sweeps agree on the node count **exactly**: 5,923,695,859 (626 s vs 3,999 s);
- the faster build was validated on the settled `L = 12` case first, reproducing 17,141 orbits and 1,406,175,228 nodes;
- the rotation-based mask translation was validated against the naive 125-iteration loop on 50,000 random inputs, 0 mismatches.

## 5. Consequence for the whole `p = 5` line

ORION-04 records: *"If `D_4(C_5^3) = 30`, then the lower line is exact for every `k ≥ 2`."* With Theorem T that hypothesis is discharged, giving

> `D_k(C_5^3) = 5k + 10` for every `k ≥ 2`,

i.e. the conjectured line `D_k(C_n^3) = ((2k+5)n−5)/2` holds at `n = 5` for all `k`. The step from Theorem T to this is the induction in that record and in Freeze–Schmid, which is **not** re-proved here.

## Claim ceiling

Theorem T is proved **given `D_3(C_5^3) = 25`**, which is prior ORION-RG work (X1-F), not established here. Steps (a)–(e) are this packet's; step (f) is exhaustive within the frame of §3. The `p = 5` line consequence in §5 depends additionally on the donor induction. No claim is made about `D_4(C_n^3)` for `n ≠ 5`, and none about priority — the external prior-art pass remains outstanding.
