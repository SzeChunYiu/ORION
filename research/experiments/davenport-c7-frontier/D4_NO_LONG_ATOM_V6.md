# No `D_4(C_5^3)` obstruction contains an atom of length 12 or 13 — three of five profiles eliminated — V6

Status: **proved by complete `GL(3,5)`-orbit sweeps at `L = 13` and `L = 12`.** Three of the five corridor profiles are now eliminated. `L = 11` is running.
Checker: `tools/sweep_atoms_by_length_c5_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Statement

> **Theorem R.** No zero-sum 5-short-free sequence of length 31 over `C_5^3` contains an atom of length 12 or of length 13.
>
> **Corollary.** The corridor profiles `(6,6,6,13)`, `(7,7,7,10)` and `(6,6,7,12)` are eliminated. `D_4(C_5^3) = 31` therefore requires `(6,7,7,11)` or `(6,7,8,10)`.

`(6,6,6,13)` and `(6,6,7,12)` carry a long atom by construction; `(7,7,7,10)` carries a 13-atom by Theorem O.

## 2. The sweeps

Both are complete enumerations of `GL(3,5)`-orbits followed by an exhaustive extension search to length 31 from each representative.

| `L` | `(prefix, completion)` pairs | orbits | canonicalisation | sweep | nodes | **completions** |
|---|---|---|---|---|---|---|
| 13 | 6,315,607 | 3,325 | 557 s | 199 s | 284,529,220 | **0** |
| 12 | 36,202,974 | 17,141 | 2,978 s | 949 s | 1,406,175,228 | **0** |

The rank argument holds at both lengths: an atom of length `L` has a zero-sum-free part of length `L−1`, and `L−1 > D(C_5^2) − 1 = 8` for `L ≥ 10`, so it spans rank three and the `e_1,e_2,e_3` normalisation is complete up to `GL(3,5)`.

**Guard satisfied.** `D4_LENGTH_SWEEP_STATUS_V6.md` §2 requires the orbit count to stay under the representative-array cap or the sweep is not exhaustive. 3,325 and 17,141 are both far under 400,000, so both runs are complete. (The cap has since been raised to 4,000,000 for the shorter lengths.)

**Counting note.** The pair counts are not atom counts — see the correction in `D4_NO_MAXIMAL_ATOM_V6.md` §2: each atom is produced once per element whose removal leaves a zero-sum-free sequence. Only the orbit counts matter for exhaustiveness, and those deduplicate exactly.

## 3. Where `D_4(C_5^3)` stands

| profile | status |
|---|---|
| `(6,6,6,13)` | **eliminated** (Theorem Q / R) |
| `(7,7,7,10)` | **eliminated** (Theorem O + R) |
| `(6,6,7,12)` | **eliminated** (Theorem R) |
| `(6,7,7,11)` | open — longest part 11, sweep running |
| `(6,7,8,10)` | open — longest part 10 |

Two profiles remain. If the `L = 11` sweep also returns zero, `(6,7,7,11)` falls and only `(6,7,8,10)` is left; an `L = 10` sweep would then **decide `D_4(C_5^3)`** outright.

Cost is climbing steeply: 89,338,594 pairs at `L = 11` against 36 million at `L = 12`, with a correspondingly larger orbit set and a 20-slot rather than 19-slot extension. The `L = 10` sweep will be larger again and is unmeasured.

## Claim ceiling

Theorem R is exhaustive within the stated frame and rests only on the completeness of the orbit enumeration. It does not decide `D_4(C_5^3)`, and says nothing about the two surviving profiles. The `L = 11` and `L = 10` sweeps are unrun or incomplete; no result is claimed for them.
