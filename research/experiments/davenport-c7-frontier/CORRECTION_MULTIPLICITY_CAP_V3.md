# Correction: the multiplicity cap in the enumeration frames — V3

Status: **self-audit; corrects claims made earlier in this packet**. Retained in full per the lane's negative-retention rule.
Trigger: the family `T_k(n)` of `GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md` has `m(e_1) = (k−1)n−1 ≥ n` for `k ≥ 3`, i.e. it is a `D_k`-extremal sequence whose largest multiplicity **exceeds `n−1`**. Every enumeration frame in this packet caps multiplicities at `n−1`. That cap needs a justification per frame, and it does not hold everywhere.

## 1. The cap and when it is legitimate

A frame `(n, L, cap = n−1, s, kmax)` enumerates sequences of length `L` with multiplicities `≤ n−1`, no zero-sum subsequence of length `≤ s`, and asks for `pk ≤ kmax`. Dropping a multiplicity `m(v) ≥ n` loses nothing **iff** no sequence of length `L` with `pk ≤ kmax` can contain `v^n`. If `v^n | S` then `v^n` is a zero-sum block and `S v^{−n}` must satisfy `pk ≤ kmax − 1`, so the cap is justified exactly when

    L − n > D_{kmax}(C_n^3) − 1,   i.e.   L ≥ D_{kmax}(C_n^3) + n.

## 2. Frames that survive unchanged (all upper-bound frames)

| frame | `L` | `kmax` | needs `L − n > D_kmax − 1` | verdict |
|---|---|---|---|---|
| `3 11 2 4 1` (`D_2(C_3^3) ≤ 11`) | 11 | 1 | `8 > D_1−1 = 6` | **valid** |
| `3 14 2 3 2` (`D_3 ≤ 14`) | 14 | 2 | `11 > D_2−1 = 10` | **valid** |
| `3 17 2 3 3` (`D_4 ≤ 17`) | 17 | 3 | `14 > D_3−1 = 13` | **valid** |
| `5 20 4 7 1` (`D_2(C_5^3) ≤ 20`) | 20 | 1 | `15 > 12` | **valid** |
| `5 25 4 5 2` (`D_3(C_5^3) ≤ 25`) | 25 | 2 | `20 > D_2−1 = 19` | **valid** |
| `3 17 2 3 3` read as `η(C_3^3) ≤ 17` | 17 | — | an element of multiplicity `≥ 3` *is itself* a zero-sum of length `3 = exp` | **valid** |

**Every exact value claimed in this packet stands**: `D_2(C_3^3) = 11`, `D_3(C_3^3) = 14`, `D_4(C_3^3) = 17`, `D_2(C_5^3) = 20`, `D_3(C_5^3) = 25`, and `η(C_3^3) ≤ 17`. Likewise `SPECTRUM_CONGRUENCE_THEOREM_V2.md`, `CUBE_PACKING_PROFILE_V3.md` (which is a statement *about the cube box*, where the cap is part of the definition) and `OBSTRUCTION_REDUCTION_LEMMAS_V2.md` Lemma 2.1 (which *proves* the cap for its own case, `L = 37`, `kmax = 3`, `37 − 7 = 30 > D_3 − 1 = 29`) are unaffected.

## 3. Claims that must be restated (all witness frames with `k ≥ 3`)

For a witness frame `L = D_k − 1` the test reads `D_k − 1 − n > D_{k−1} − 1`, i.e. `D_k > D_{k−1} + n` — precisely the inequality that **fails**, since `D_k = D_{k−1} + n`. So for `k ≥ 3` the cap is illegitimate and the frames enumerate a proper subset. For `k = 2` the test reads `D_2 − 1 − n > D − 1`, i.e. `(9n−5)/2 > 4n−2`, true for every `n ≥ 3`: **the `k = 2` classifications are complete.**

Restatements:

- `EXHAUSTIVE_ANALOG_RESULTS_V2.md`: the counts "7 317 → 161 orbits" (`n=3`, `k=3`), "8 921 → 69 orbits" (`n=3`, `k=4`) and the partial `n=5`, `k=3` run classify **`D_k`-extremal sequences with all multiplicities `≤ n−1`**, not all of them. The lower bounds `D_3 ≥ 14`, `D_4 ≥ 17` they witness are unaffected. The `k = 2` counts (43 orbits at `n=3`, 1 405 at `n=5`) are complete classifications.
- `EXTREMAL_STRUCTURE_V3.md` §1 (cube-likeness percentages): computed over the capped families; the `k = 2` row is a complete-enumeration fact, the `k = 3, 4` rows are statements about the capped subset.
- `EXTREMAL_STRUCTURE_V3.md` §2, **Conjecture R is refuted for `k ≥ 3`**: `T_3(3) = e_1^5 e_2^2 e_3^2 e_12^2 e_13 e_23` is `D_3(C_3^3)`-extremal (length 13, `pk = 2`) with maximal multiplicity 5, not `n−1 = 2`. The conjecture survives only in the form below.
- `PROGRESS_LEDGER_V2.md` row C7-EXH-3 and `PROGRESS_LEDGER_V3.md` row C7-INV-2: same correction.

## 4. What survives of the rigidity conjecture

**Conjecture R′ (`k = 2` only).** Every `D_2`-extremal sequence over `C_n^3` contains an element of multiplicity exactly `n−1`.

The `k = 2` enumerations are complete (§3), so this is supported by all 529 sequences at `n = 3` and all 7 847 at `n = 5`, and by the capped-cube capacities of `EXTREMAL_STRUCTURE_V3.md` §2. It is exactly the form needed by `OBSTRUCTION_REDUCTION_LEMMAS_V2.md` Lemma 2.4(4), whose `u = 8` case concerns a `D_2`-extremal object — so the lever survives the correction intact.

The `n = 7`, `L = 28`, `k = 2` classification frames (classes `m(e_1) = 6` and `m(e_1) = 5`) are also legitimate: `28 − 7 = 21 > D_1 − 1 = 18`.

## 5. Lesson

A symmetry- or structure-based restriction that is sound for one `(L, k)` is not sound for the whole family; the admissible cap depends on the very quantity being computed (`D_{k−1}` versus `D_k`), so it must be re-derived per frame rather than inherited. The generic failure mode is that a restriction which is *forced* at the boundary case becomes merely *typical* one step in. Frames whose conclusion is "found = 0" degrade safely under an over-tight restriction only when the restriction is proved; frames whose conclusion is a classification never do.
