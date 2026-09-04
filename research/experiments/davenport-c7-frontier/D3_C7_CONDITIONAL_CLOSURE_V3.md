# `D_3(C_7^3) = 36`, conditional on one statement — V3

Status: **conditional theorem.** Every input is proved inside this packet except one, which is named precisely below. Machine-checked; the machinery is validated against a real object that must survive it. Priority CANNOT_CHECK.
Tools: `tools/spectra_complement_v3.py`, `tools/unconditional_v3.py`, `tools/selfcontained_v3.py`, `tools/replace_donors_v3.py`, `tools/control_complement_v3.py`.

## 1. Statement

> **Theorem.** Assume `(Z)`: *every zero-sum sequence of length 28 over `C_7^3` with zero-sum packing number 2 has an atom of length `≤ 12`.* Then `D_3(C_7^3) = 36`.

`(Z)` is exactly the specialisation of Zhang's `s_{≤12}(C_7^3) = 26` used by `ATOM_LENGTH_CORRIDOR_V1.md`. It is the **only** donor input left in the chain; everything else — including `D_2(C_7^3) = 29` and the short-zero-sum bounds that the corridor argument took from Zhao's Lemma 4.4 — is proved in this packet.

## 2. The chain

1. `D(C_7^3) = 19` (Olson) and `D_2(C_7^3) = 29` (`D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md`, self-contained).
2. Every atom of an obstruction has length `≥ 8`; a length-37 zero-sum has a zero-sum of length `≤ 10`; a `z = 2` sequence of length 29 or 27 has an atom of length `≤ 10`. **All three follow from this packet's congruence systems** (`tools/replace_donors_v3.py`), replacing the corridor argument's uses of Zhao. A control confirms the method is not vacuous: "length `≤ 9`" is *not* derivable at length 37.
3. `(Z)` supplies the remaining case, `|C| = 28`. This packet's congruences give only "atom of length `≤ 14`" there — see §4.
4. Hence the shortest-atom factorization has one of six profiles (the corridor).
5. The zero-sum sub-multisets of an obstruction are exactly `∅`, `T`, atoms, complements of atoms (`ATOM_SPECTRUM_CONGRUENCE_V3.md`), giving 548 admissible atom-length sets, cut to **eight** by closure and corridor consistency.
6. Each of the eight dies against a **complement system**: for an atom `A`, `C = T A^{−1}` has `z(C) = 2`, its zero-sum multisets are `∅`, `C` and paired atoms whose lengths lie in the spectrum, and the counting identity on `C` is then infeasible. All eight are killed, several of them at more than one atom length.

Therefore no obstruction exists, and `D_3(C_7^3) = 36`. ∎

## 3. Validation

The complement machinery is exactly the kind that could "prove" anything if wrong, so it is run against a **real** object that must survive it: the packing-number-3 sequence `T_3(5)·(−σ)` over `C_5^3`, length 25, atom lengths `{5,7,8,9,10,11,12,13}`. Every one of its eight complement systems is **feasible** (`tools/control_complement_v3.py`). The framework does not kill objects that exist.

## 4. Exactly how much `(Z)` is doing

Without `(Z)`, this packet's own bound for `|C| = 28` is "an atom of length `≤ 14`" rather than `≤ 12`, which enlarges the corridor by the two profiles `(9,13,15)` and `(9,14,14)`. Re-running the whole chain with that enlarged corridor leaves **30 surviving spectra** (`tools/selfcontained_v3.py`), every one of which has minimum atom length 9 and contains 14. Dropping the corridor step entirely leaves 35 (`tools/unconditional_v3.py`).

So the gap is sharp and singular: `(Z)` excludes precisely the profiles `(9,13,15)` and `(9,14,14)`, and with them the last 30 spectra. Equivalently, it suffices to prove

> **`f_12(C_7^3) ≤ 27`** — every sequence of length 28 over `C_7^3` has a zero-sum subsequence of length `≤ 12`

(Zhang's value is 25, so this is weaker than what the literature claims). A direct search for a length-28 counterexample is running; its rank-3 restriction is legitimate because a rank-`≤2` sequence of length 28 lies in `C_7^2`, where `η = 19 ≤ 28` already forces a zero-sum of length `≤ 7`.

**Refinement.** The congruences do not prove `(Z)`, but they pin the counterexample down. A length-28 zero-sum whose only proper zero-sum lengths are `{13,14,15}` must satisfy

    N_13 ≡ 0,   N_14 ≡ 5   (mod 7),

the unique solution of the 10-equation system in those two unknowns. So such a `C` has at least five zero-sum subsequences of length 14, and either none of length 13 or at least seven. In the first case every atom of `C` has length exactly 14, so `C` is a length-28 zero-sum all of whose proper zero-sums have length 14 — a rigid object, and the natural target for the search.

## 5. Claim ceiling

This is a conditional theorem, not an unconditional one, and the condition is a donor statement this host cannot read. Should `(Z)` fail, the 30 spectra of §4 are the complete residue. No novelty is claimed for `(Z)` or for `D_3(C_7^3) = 36`; whether the argument or the value is new is unknown.
