# ORION09.REGIME_SEPARATOR_COMPLEXITY.v1 — THEORY

**Paper:** ORION-09 — Compilation Regime Geometry
**Successor id:** `ORION09.REGIME_SEPARATOR_COMPLEXITY.v1`
**Candidate source:** PR #1617, Priority A, `ORION09.REGIME_INFORMATION_COMPLEXITY.v1`
**Authored:** 2026-08-28
**Status:** `THEORY_PROVED__COMPUTED_ON_FROZEN_DOMAIN__ONE_MANUSCRIPT_INCOMPLETENESS_FOUND`
**Scientific authority delta:** `NONE` for recorded terminals; **one submission blocker raised** (§8, incompleteness not falsity)
**Packet layout source:** issue #1608
**Frozen paper bytes modified:** NONE

---

## 1. Why this successor exists

The R2 negative-revival addendum records that stage-1 determination under the L3
vocabulary is *near-injective* — `1109` cells over `1146` instances, `1072`
singletons — and therefore concludes, correctly and cautiously, that the floor-0
conversion proves **vocabulary existence** and

> does NOT establish a compact or low-dimensional law.

That disclosure is a pre-frozen gate and it is honest. It is also **purely
qualitative**. Nobody had computed how much of the floor-0 result was forced by
the cell structure alone, nor how few features actually suffice.

This packet computes both, exactly, on the frozen domain. The answers change the
scientific reading in both directions: they make the positive result much
stronger than recorded, and they contradict the manuscript's headline negative.

The candidate note in #1617 asks to "independently recompute the `43/1146`
minority-mass floor" and to "retain a nonzero lower bound if no frozen extension
purifies fibres". **Both premises are superseded by evidence committed on
2026-08-28**: a frozen extension already purified the fibres. §7 records this.

---

## 2. Setting

A finite domain of `N` instances, each with a binary label `Y` (donor-exactness)
and a feature map `phi` into a finite set. `phi` induces **fibres** (cells)
`F_z = {i : phi(i) = z}`, with class counts `n_z^0, n_z^1`.

```
E*(phi) = (1/N) * sum_z min(n_z^0, n_z^1)
```

### Theorem A (fibre floor is exactly the best achievable error)

Any deterministic classifier that reads only `phi` must emit one label per fibre.
Choosing the majority label in each fibre errs `min(n_z^0, n_z^1)` times there,
and any other choice errs at least that often. Hence `E*(phi)` is exactly the
minimum empirical error over all `phi`-measurable classifiers, attained by
per-fibre majority vote. ∎

This is generic information-sufficiency mathematics and is **donor-owned**.

### Theorem B (compression bound — what the cell structure forces on its own)

If `phi` realizes `c` distinct cells on `N` instances then

```
E*(phi) <= (N - c) / N.
```

**Proof.** A cell of size `m` has `min(n^0, n^1) <= floor(m/2) <= m - 1`. Summing
over cells, `sum_z min(n_z^0, n_z^1) <= sum_z (|F_z| - 1) = N - c`. ∎

Theorem B is the precise form of the memorization worry. A map that is close to
injective has `c` close to `N`, so its floor is confined to a narrow band near
zero **before any label is examined**. Reporting `E* = 0` for such a map is then
weak evidence, because little else was possible.

### Definition (separator complexity)

For a frozen feature library `Phi = {phi_1, ..., phi_K}` and subset `S`, write
`phi_S` for the projection. Define

```
k*(Phi) = min { |S| : E*(phi_S) = 0 }.
```

`k*` is the honest measure of "is there a compact law?" that `E* = 0` alone
cannot supply.

### Theorem C (hitting-set characterization)

`E*(phi_S) = 0` holds iff every opposite-label pair `(x, x')` is separated by some
coordinate in `S`. Writing the discernibility set

```
D(x, x') = { j : phi_j(x) != phi_j(x') },
```

`E*(phi_S) = 0` iff `S ∩ D(x, x') != empty` for every opposite-label pair. Hence

```
k*(Phi) = minimum hitting set over { D(x,x') : Y(x) != Y(x') }.
```

**Proof.** `E*(phi_S) = 0` iff no cell of `phi_S` is mixed, iff no opposite-label
pair shares a cell, iff every such pair differs on some coordinate of `S`. ∎

This equivalence is **donor-owned** rough-set / discernibility-matrix theory. It
is the same object as ORION-14's minimal promotion reduct and ORION-13's minimal
semantic separator; see the cross-paper spine in #1617.

### Structure-free null

Given the *realized* cell structure and the *realized* class balance, the exact
probability that a uniformly random relabelling also attains floor 0 is computed
in closed form: floor 0 requires every cell to be label-homogeneous, so with
non-singleton cell sizes `s_1..s_m` and `n_+` positives among `N`,

```
P = [ sum over subsets A of {1..m} of C(N_single, n_+ - sum_{i in A} s_i) ] / C(N, n_+)
```

where `N_single` is the number of singleton cells. Exact integer arithmetic.
This separates *"the labels really are aligned with the feature partition"* from
*"the cells were small enough that any labelling would have been pure."*

---

## 3. Results on the frozen domain

All numbers below are computed by `independent_checker/`, from a feature matrix
regenerated from the committed, hash-verified modules. Nothing is read from the
receipt except for comparison.

### 3.1 Independent replay of the receipt — PASS

Every stage-1 statistic in
`R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json` was reproduced exactly:
`1146` instances, `127` features, `1109` cells, `1072` singletons, `0` mixed
cells, floor `0`, compression `0.967714`, and the per-`n` domain counts
`6 / 60 / 1080` with `5 / 28 / 189` donor-exact. Zero mismatches.

### 3.2 Pipeline validated against three independently recorded floors

The extraction was checked against numbers recorded in the receipt but **not**
used to build it:

| vocabulary | receipt | recomputed | match |
|---|---|---|---|
| V1 (13 features) | `N2_V1_floor = 43` | floor `43`, 243 cells, 12 mixed | yes |
| V2 (33 features) | `N2_V2_floor = 1` | floor `1`, 1043 cells, 1 mixed | yes |
| L2 = V1 + donor-path (66) | `N2_L2_floor = 5`, "3 mixed cells" | floor `5`, 654 cells, **3 mixed** | yes |

Three independent agreements, including the mixed-cell count. The pipeline is
validated on real frozen data, not on a fixture.

### 3.3 What the cell structure forced (Theorem B)

The realized L3 structure is `1072` singletons and `37` cells of size `2`
(maximum cell size `2`). So `N - c = 37` and

```
E*(L3) was confined to [0, 37/1146] = [0, 0.0323]  before any label was read.
```

The memorization worry is therefore real but **bounded**: floor 0 could differ
from the a-priori-forced band by at most `3.23%`.

### 3.4 The floor-0 result is not a near-injectivity artifact

Exact structure-free null for the full L3 map:

```
P(floor = 0 | random relabelling, same cells, same class balance) = 7.057e-07
```

cross-checked by `20000` permutations, `0` hits. So the labels genuinely align
with the feature partition; the conversion is **not** explained by small cells.

### 3.5 Separator complexity: `k* = 4`, proved

```
opposite-label pairs                     205128
distinct minimal discernibility sets      43762
covering subsets of size 1                    0   (all 127 tested)
covering subsets of size 2                    0   (all 8001 tested)
covering subsets of size 3                    0   (all 333375 tested)
witness of size 4                   {15, 30, 39, 42}
```

Exhaustive refutation of every subset of size `<= 3` gives `k* >= 4`; the verified
witness gives `k* <= 4`. Therefore **`k* = 4` exactly**.

The 4-feature projection has `523` cells on `1146` instances — compression
`0.456`, nowhere near injective. By Theorem B its floor could have been as large
as `623/1146 = 0.544`, and it is `0`. Its structure-free null is

```
P(floor = 0 | random relabelling) = 1.442e-120.
```

**A compact four-feature law determines donor-exactness on the complete
`n <= 3` StabPrep domain.** This is exactly the "compact or low-dimensional law"
the R2 addendum declined to claim. The addendum's caution was appropriate for
what had been computed; it is now superseded in the favourable direction by exact
computation on the same frozen data.

### 3.6 Block attribution — the new sign-aware block was not necessary

L3 is composed of three committed blocks: V2 `[0,33)`, donor-path `[33,86)`, and
the new sign-aware STATE block `[86,127)` added by the R2 revival.

| vocabulary | features | cells | mixed | floor |
|---|---|---|---|---|
| V2 | 33 | 1043 | 1 | 1 |
| donor-path | 53 | 654 | 3 | 5 |
| STATE (new) | 41 | 461 | 29 | 43 |
| **V2 + donor-path** | **86** | **1106** | **0** | **0** |
| V2 + STATE | 74 | 1088 | 0 | 0 |
| donor-path + STATE | 94 | 888 | 0 | 0 |
| all L3 | 127 | 1109 | 0 | 0 |

**Any two of the three blocks already attain floor 0.** In particular
`V2 + donor-path` — both committed *before* the revival — attains floor 0 with no
sign-aware feature at all, and the minimal witness `{15, 30, 39, 42}` contains
**zero** STATE-block coordinates (two from V2, two from donor-path).

The addendum's pair-level witness is not contradicted: the STATE block does
separate the specific V2-surviving mixed pair. What is **not** established is the
stronger reading that sign-awareness is *the* operative mechanism for the
conversion. The conversion did not require the new block.

This is recorded as an adverse finding against the mechanism attribution. It does
**not** overturn the recorded verdict: `floor(L3) == 0` is true, and
`POSITIVE_CONVERSION` under the pre-frozen criterion H-A stands.

### 3.7 The n = 4 negative is untouched

Stage 2 remains `NOT_IMPROVED`: in-panel floor `0` but `32/120` CV errors, equal
to the parent cell-lookup baseline, shuffle-null mean `32.41`, empirical
`p = 0.51`. The compact `n <= 3` law does **not** transfer out of sample.

Nothing in this packet improves, reinterprets or softens that. The correct
combined statement is:

> a compact four-feature law determines donor-exactness on `n <= 3`, and it does
> not transfer to unseen `n = 4` states.

---

## 4. Strongest falsifiers

1. **Against `k* = 4`:** any subset of size `<= 3` attaining floor 0. Refuted
   exhaustively — all `333375` triples, all `8001` pairs, all `127` singletons
   tested.
2. **Against the compact-law reading:** the four features could be a domain
   artifact. The honest limit is that `k*` is computed on `n <= 3` only, and §3.7
   shows the vocabulary does not transfer to `n = 4`. No cross-`n` claim is made.
3. **Against the block-attribution finding:** if `V2 + donor-path` failed to
   attain floor 0, the necessity of the STATE block would stand. It attains
   floor 0, verified directly and by two independent routes.
4. **Against the structure-free null:** if the null probability were high, floor 0
   would be a cell-size artifact. It is `7.06e-07` for L3 and `1.44e-120` for the
   4-feature map.

---

## 5. Independent verification

Three checkers, each usable on its own:

- `extract_frozen_matrix.py` — verifies module SHA-256 against the receipt, then
  regenerates the matrix and recomputes every stage-1 statistic; the receipt is
  compared, not trusted.
- `separator_complexity.py` — Theorem B bound, exact structure-free null with
  permutation cross-check, and `k*` by branch and bound.
- `verify_minimality.py` — **independent** exhaustive refutation of all subsets of
  size `<= 3` by bitset covering, direct witness re-projection, and the block
  attribution table. Shares no search logic with the branch and bound.

`CANNOT_CHECK` has its own exit code `3` in every checker and is never reported as
a pass.

---

## 6. Donor boundary

Theorem A (per-fibre majority optimality), Theorem C (sufficiency as a hitting-set
/ discernibility-matrix problem) and the reduct formulation are **donor-owned**
rough-set and information-sufficiency mathematics. Theorem B is an elementary
counting bound and is very likely also classical. **No novelty is claimed for any
of them.**

The ORION-specific content is the exact instantiation on the frozen StabPrep
domain: `k* = 4` with its witness, the block-attribution table, and the two
structure-free nulls.

---

## 7. Supersession of the #1617 ORION-09 premise

The candidate note asks to recompute a `43/1146` "irreducible vocabulary floor"
and to "retain a nonzero lower bound if no frozen extension purifies fibres."

Both are superseded. `43/1146` is the **V1** floor, reproduced here exactly, but a
frozen extension *did* purify the fibres on 2026-08-28: floor `0` under L3, and in
fact under any two of its three blocks. The correct successor question is not the
size of an irreducible floor but the **separator complexity** of the enlarged
vocabulary, which is `4`.

The note's own strongest falsifier anticipated this: *"if an independent
reconstruction makes all StabPrep fibres pure, the current irreducible-vocabulary-
floor interpretation is wrong."* That falsifier has fired.

---

## 8. Submission blocker raised against the ORION-09 manuscript

`manuscript/main.tex` line 16 (abstract) currently states:

> "no predicate in the frozen natural feature vocabulary exactly separates
> donor-exactness, and mixed feature cells impose an irreducible 43/1146 error
> floor regardless of predicate budget. Thus the transferable object is the
> mapping discipline, not a universal low-order boundary law."

`manuscript/main.tex` contains **zero** occurrences of `R2`, `L3` or `revival`.
The committed R2 evidence sitting in `evidence/` of this same paper is not
integrated anywhere in the manuscript.

**The defect is omission, not falsity.** Every sentence quoted above is true as
written:

- the V1 floor is `43/1146` and is irreducible within V1 — reproduced exactly in
  §3.2;
- *"regardless of predicate budget"* sits inside the scope set by *"in the frozen
  natural feature vocabulary"*, and within V1 it is correct: by Theorem A no
  predicate of any complexity over V1 features can beat the V1 fibre floor;
- *"not a universal low-order boundary law"* is **also true**, and §3.7 of this
  packet independently supports it — the four-feature law is domain-local and
  fails at `n = 4`.

The defect is that the abstract presents a **superseded scoped result as the
paper's StabPrep finding**, while evidence committed in this paper's own
`evidence/` directory — a prospectively frozen revival that drove the floor to
`0` — appears nowhere in the manuscript. A reader finishes the abstract believing
the vocabulary question closed negatively. It is not: under an enlarged, frozen
vocabulary the floor is `0`, and exactly four features suffice on `n <= 3`.

That is material incompleteness rather than a false statement, and it is enough
to block submission under #1609 §A (*headline quantitative statements are
generated from immutable result artifacts*) and §D (*Abstract, Results and
Conclusion map to a claim/evidence matrix*). #1609's ORION-09 checklist already
requires *"integrate the R2 negative-revival outcomes without overstating the
near-injective L3 vocabulary"*; that integration has not happened.

The rescope is therefore an **addition and re-scoping**, not a retraction. The
paper's negative conclusion survives in a sharper, better-supported form.

**ORION-09 must not be submitted until the abstract is rescoped.** The rescope is
a manuscript edit and therefore belongs in a separate PR with its own authority
record; it is **not** taken here. `CLAIM_DISPOSITION.md` §6 carries proposed
replacement wording.

---

## 9. Authority boundary

`scientific_authority_delta = NONE` for every recorded ORION-09 terminal, verdict,
receipt and ledger row.

- `H_A_N2 = POSITIVE_CONVERSION` and `H_B_N4_residual = NOT_IMPROVED` are
  unchanged.
- The `n = 4` negative, the shuffle-null `p = 0.51`, and the `NOT_R6` authority
  ceiling are unchanged.
- No frozen receipt, protocol or evidence byte is modified.
- `submission_prx/` is not read, written or depended upon.
- The blocker in §8 is a **referral**, not an edit.
