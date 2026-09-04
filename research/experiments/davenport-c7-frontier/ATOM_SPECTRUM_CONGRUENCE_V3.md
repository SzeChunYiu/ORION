# The atom-length spectrum of a `D_3(C_7^3)` obstruction — V3

Status: **proved and machine-validated**, self-contained given Olson's `D(C_7^3)=19` and `D_2(C_7^3)=29` (the latter now proved in this packet, `D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md`). Priority CANNOT_CHECK.
Checker: `verify_atom_spectrum_v3.py`. Branch: `claude/orion-research-frontier-3ck9yt`.

## 1. What this adds

The ChatGPT lane's reduction is geometric and scalar: projective directions, arcs, conics, plane caps. Its stated ceiling (`PROGRESS_LEDGER_V1`) is a support-six barrier "requiring genuinely rank-three information next". The constraint below is exactly that — it comes from a Chevalley–Warning count in `F_7^3` and sees nothing geometric at all, only the multiset of atom lengths.

## 2. The zero-sum multisets of an obstruction

Let `T` be zero-sum over `G = C_7^3` with `|T| = 37` and `z(T) = 3` (`z` = zero-sum packing number; `z(T) ≥ 3` always, since deleting one term leaves length `36 ≥ D_2` and the remainder is a further block).

**Lemma 2.1.** The zero-sum sub-multisets of `T` are exactly `∅`, `T`, the atoms of `T`, and the complements of atoms.

*Proof.* For a proper nonempty zero-sum `U`, blocks inside `U` and inside `T U^{−1}` are disjoint in `T`, so `z(U) + z(T U^{−1}) ≤ 3` with both terms `≥ 1`. If `z(U) = 1` then `U` is an atom; if `z(U) = 2` then `z(T U^{−1}) = 1`, so `U` is the complement of an atom. ∎

**Lemma 2.2.** Atoms and complements-of-atoms overlap only in atoms `A` with `T A^{−1}` also an atom, which forces `|A|, |T A^{−1}| ∈ {18,19}`.

*Proof.* `|A| + |T A^{−1}| = 37` with both `≤ D = 19`. ∎

Every atom has length `≥ 8`: if a block `U` had `|U| ≤ 7` then `|T U^{−1}| ≥ 30 > D_2`, so any 29 of its terms already contain two disjoint blocks, leaving a nonempty zero-sum remainder — four blocks in all.

## 3. The congruence

Theorem 1 of `D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md` with `h = e_d` gives, for `0 ≤ d ≤ |T| − D = 18`,

    Σ_l (−1)^l N_l C(l,d) ≡ 0   (mod 7),

where `N_l` counts zero-sum **index subsets** of size `l`. A zero-sum sub-multiset `M` contributes `w(M) = Π_i C(m_i(T), m_i(M))`, and complementation preserves that weight, `w(T M^{−1}) = w(M)`. Writing

    W_l = Σ_{atoms A, |A| = l} w(A)  (mod 7),    X_l = the same sum over atoms whose complement is an atom,

Lemma 2.1 and `(−1)^{37−l} = −(−1)^l` turn the congruence into

> **(⋆)**  `Σ_{l=8}^{19} (−1)^l W_l [ C(l,d) − C(37−l,d) ] − Σ_{l∈{18,19}} (−1)^l X_l C(l,d) + [ C(0,d) − C(37,d) ] ≡ 0 (mod 7)`, for every `0 ≤ d ≤ 18`.

Nineteen equations in fourteen unknowns over `F_7`.

## 4. Forced atom lengths

The system `(⋆)` is consistent, so it does not by itself exclude an obstruction. But it is inconsistent as soon as certain pairs of `W_l` are set to zero, and `W_l = 0` whenever `T` has no atom of length `l`. Solving gives, with `s = W_18 + W_19`,

    W_8 = −2W_15,  W_9 = 4−s,  W_10 = 2s,  W_11 = 4s,  W_12 = 4s,
    W_13 = 2s,  W_14 = 1−s,  W_16 = 6−2s,  W_17 = 4s,   (W_15, W_18, W_19 free)

so `W_13 = 0` forces `s = 0` and then `W_14 = 1 ≠ 0`. Hence:

> **Theorem.** Every zero-sum `T` over `C_7^3` with `|T| = 37` and `z(T) = 3` has an atom of length **13 or 14**.

The full list of minimal length-sets that cannot all be absent is computed by the checker; it includes `{9,10}`, `{9,11}`, `{9,12}`, `{9,13}`, `{9,14}`, `{9,16}`, `{9,17}`, `{10,14}`, `{10,16}`, `{11,14}`, `{11,16}`, `{12,14}`, `{12,16}`, `{13,14}`, `{13,16}`, `{14,16}`, `{14,17}`, `{16,17}`, and three triples involving `{18,19}`.

## 5. Why 13 and 14 are the interesting ones

`ATOM_LENGTH_CORRIDOR_V1.md` shows that a factorization built from a **shortest** atom has one of six length triples — `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)` — and **none contains 13 or 14**. So the atom whose existence is forced above lies in no shortest-atom factorization. Its complement has length 24 or 23 and splits into two atoms, giving a second factorization of type `(13,u,24−u)` or `(14,u,23−u)`.

**Reduction.** If every atom of an obstruction were confined to the corridor lengths `{8,…,12,16,…,19}`, then `W_13 = W_14 = 0` and `(⋆)` would be inconsistent, so:

> Ruling out atoms of length 13 **and** of length 14 proves `D_3(C_7^3) = 36`.

That is a sharper and more finite target than the support ladder: two atom lengths, rather than a support parameter with no a priori bound.

## 6. A correction, recorded

I first read the corridor theorem as constraining **every** three-atom factorization, concluded `W_13 = W_14 = W_15 = 0` outright, and therefore that `D_3(C_7^3) = 36`. That was wrong. The proof in `ATOM_LENGTH_CORRIDOR_V1.md` selects a *shortest* atom `A` and classifies the factorization built from it; an atom of length 13 sitting in a factorization such as `(11,13,13)`, which contains no shortest atom, is not excluded by that argument. The claim is withdrawn; what survives is §4 (unconditional) and §5 (a reduction, not a proof).

## 7. Validation

`verify_atom_spectrum_v3.py` checks, in order:

1. the counting identity itself, by brute force over all `2^15` index subsets of random zero-sum sequences over `C_3^3`;
2. Lemma 2.1 on a **real** packing-number-3 object — `T = T_3(5)·(−σ)` over `C_5^3`, length 25 — where the predicted and actual families of zero-sum multisets agree exactly (144 = 144), and `(⋆)` holds for every `d ≤ 12` with the true weights;
3. the `p = 7` solution above, and that `{13,14}` is among the forced sets;
4. that no forced set at `p = 5` is violated by the real object.

## Claim ceiling

§4 is unconditional given `D(C_7^3) = 19` and `D_2(C_7^3) = 29`. §5's reduction quotes the corridor theorem, which is donor-conditional (Zhao Lemma 4.4, Zhang `s_{≤12} = 26`). Nothing here determines `D_3(C_7^3)`.
