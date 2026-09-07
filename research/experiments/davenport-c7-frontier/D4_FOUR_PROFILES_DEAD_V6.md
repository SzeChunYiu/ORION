# No `D_4(C_5^3)` obstruction has an atom of length 11, 12 or 13 — four of five profiles eliminated — V6

Status: **proved by complete `GL(3,5)`-orbit sweeps at `L = 13, 12, 11`**, each cross-checked by two independent implementations. One profile remains; its sweep (`L = 10`) is running.
Tools: `tools/sweep_atoms_by_length_c5_v6.c`, `tools/sweep_atoms_turbo_c5_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Statement

> **Theorem S.** No zero-sum 5-short-free sequence of length 31 over `C_5^3` contains an atom of length 11, 12 or 13.
>
> **Corollary.** Of the five corridor profiles, `(6,6,6,13)`, `(6,6,7,12)`, `(6,7,7,11)` and `(7,7,7,10)` are eliminated. `D_4(C_5^3) = 31` requires the single profile `(6,7,8,10)`.

`(7,7,7,10)` falls because Theorem O forces it to carry a 13-atom.

## 2. The sweeps

| `L` | pairs | distinct atoms | orbits | canon | sweep | nodes | **completions** |
|---|---|---|---|---|---|---|---|
| 13 | 6,315,607 | 998,182 | 3,325 | 557 s | 199 s | 284,529,220 | **0** |
| 12 | 36,202,974 | 5,603,363 | 17,141 | 517 s | 165 s | 1,406,175,228 | **0** |
| 11 | 89,338,594 | 13,851,427 | 39,760 | 1,159 s | 396 s | 3,674,071,087 | **0** |
| 10 | 94,515,860 | 15,289,814 | 44,111 | 1,144 s | running | — | — |

Every orbit count is far below the representative cap, so the guard of `D4_LENGTH_SWEEP_STATUS_V6.md` §2 is satisfied and each completed sweep is exhaustive.

**Cross-checks.** Orbit counts at `L = 10` and `L = 11` were produced independently by the plain and the deduplicating build (44,111 and 39,760 from both). The `L = 11` sweep was run by two builds and returned *identical* node counts, 3,674,071,087, and zero completions. The turbo build was validated on the settled `L = 12` case before use, reproducing 17,141 orbits and the same 1,406,175,228 nodes.

## 3. Two optimisations, and what they were worth

The first sweeps were correct but wasteful. Two changes, both validated against settled cases:

1. **Deduplicate atom multisets before canonicalising.** The enumeration emits `(prefix, completion)` pairs, so each atom arrives about 6.3 times; canonicalising every copy wasted that factor. Measured: `L = 11` canonicalisation 7,328 s → 1,159 s.
2. **Replace the mask translation.** Translating a subsum-set by `+v` was a 125-iteration loop. With bit index `25x + 5y + z` it is three nested cyclic rotations — about nine word operations. Validated separately against the naive loop on 50,000 random cases (0 mismatches). Measured: `L = 12` sweep 949 s → 165 s.

Together roughly `6×` on canonicalisation and `5.8×` on the sweep. What had been projected at 114 hours for `L = 13` alone became minutes per length.

## 4. What remains

Only `(6,7,8,10)`. Its longest part is 10, and the `L = 10` sweep over all 44,111 orbits is in progress. **If it returns zero, `D_4(C_5^3) = 30` is decided**, which fixes `D_k(C_5^3) = 5k+10` for every `k ≥ 2` and settles the conjectured line at `p = 5`.

## Claim ceiling

Theorem S is exhaustive within the stated frame, resting only on completeness of the orbit enumeration (an atom of length `L ≥ 10` has a zero-sum-free part of length `L−1 > D(C_5^2)−1 = 8`, so it spans rank three and the `e_1,e_2,e_3` normalisation is complete up to `GL(3,5)`). It does **not** decide `D_4(C_5^3)`; the `L = 10` sweep is unfinished and no result is claimed for it.
