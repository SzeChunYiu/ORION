# A second corridor: the factorization through the forced 13/14-atom — V3

Status: **derived**, from `ATOM_SPECTRUM_CONGRUENCE_V3.md` (unconditional) together with the *proof* of `ATOM_LENGTH_CORRIDOR_V1.md` (donor-conditional). Checker: `verify_second_corridor_v3.py`. Priority CANNOT_CHECK.

## 1. The gap this fills

`ATOM_LENGTH_CORRIDOR_V1.md` classifies the three-atom factorization built from a **shortest** atom: six profiles, `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`. The atom-spectrum congruence forces an atom `B` with `|B| ∈ {13,14}`, and **no corridor triple contains 13 or 14**, so `B` lies in no shortest-atom factorization. The factorization through `B` was therefore unclassified. This record classifies it.

## 2. Derivation

`C = T B^{−1}` has length `37 − |B| ∈ {23,24} > D = 19`, so `z(C) = 2` and `C = U·V` with `U, V` atoms. Every atom has length in `[8,19]`, giving the candidate profiles below. Let `s` be the global minimum atom length of `T`; the corridor proof gives `s ∈ {8,9,10}`, and any three-atom factorization **containing an atom of length `s`** must be a corridor triple.

A profile containing the value 8 forces `s = 8` (8 is the global minimum), so such a profile must be a corridor triple — excluding `(8,13,16)` and `(8,14,15)` outright. The same test applied for each admissible `s` gives:

| `|B|` | profile | verdict |
|---|---|---|
| 13 | `(8,13,16)` | **excluded** |
| 13 | `(9,13,15)` | survives, forces `s = 8` |
| 13 | `(10,13,14)` | survives, `s ∈ {8,9}` |
| 13 | `(11,13,13)` | survives, `s ∈ {8,9,10}` |
| 13 | `(12,12,13)` | survives, `s ∈ {8,9,10}` |
| 14 | `(8,14,15)` | **excluded** |
| 14 | `(9,14,14)` | survives, forces `s = 8` |
| 14 | `(10,13,14)` | survives, `s ∈ {8,9}` |
| 14 | `(11,12,14)` | survives, `s ∈ {8,9,10}` |

> **Second corridor.** Every length-37 obstruction over `C_7^3` admits a three-atom factorization with one of the six profiles
>
> `(9,13,15)`, `(9,14,14)`, `(10,13,14)`, `(11,12,14)`, `(11,13,13)`, `(12,12,13)`,
>
> in addition to its shortest-atom factorization from the first corridor.

## 3. Two levers this hands the geometric programme

1. **The `s = 8` cases pair with an already-closed branch.** `(9,13,15)` and `(9,14,14)` force `s = 8`, so `T` also has an atom of length 8 and hence a first-corridor factorization `(8,10,19)` — whose support-four branch is closed (`CORRIDOR_8_10_19_CROSS_CHECK_V3.md`). Those two profiles therefore survive only alongside an `(8,10,19)` factorization whose 19-atom has support `≥ 5`.
2. **The profiles are flatter.** Unlike the first corridor, no profile here has a maximal (19) atom, and three of the six have no atom above 14. The support-four maximal-atom classification does not apply, but the multiplicity budget is tighter: `(11,13,13)` and `(12,12,13)` have all parts in `[11,13]`, so no part is close to `D`.

Closing all six profiles proves `D_3(C_7^3) = 36`, since an obstruction must exhibit one of them.

## Claim ceiling

The forcing of a 13- or 14-atom is unconditional. The exclusions here quote the corridor proof, which is donor-conditional (Zhao Lemma 4.4, Zhang `s_{≤12} = 26`); if that proof's scope is actually *every* three-atom factorization rather than the shortest-atom one, then 13- and 14-atoms are impossible outright and `D_3(C_7^3) = 36` follows without this record. That ambiguity is flagged on PR #2198.
