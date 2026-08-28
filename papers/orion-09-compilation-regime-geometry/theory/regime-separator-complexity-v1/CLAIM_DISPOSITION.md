# ORION09.REGIME_SEPARATOR_COMPLEXITY.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Terminal:** `THEORY_PROVED__COMPUTED_ON_FROZEN_DOMAIN`
**Scientific authority delta for recorded ORION-09 terminals:** `NONE`
**New blocker raised:** `MANUSCRIPT_INCOMPLETENESS__SUBMISSION_BLOCKED` (§6)

---

## 1. What changed

One additive directory:

```
papers/orion-09-compilation-regime-geometry/theory/regime-separator-complexity-v1/
```

No receipt, protocol, addendum, ledger, manuscript or `submission_prx/` byte was
modified. The feature matrix used here is **regenerated** from committed modules
whose SHA-256 is verified against the frozen receipt before import; a hash
mismatch aborts with `CANNOT_CHECK` rather than proceeding.

## 2. Independent replay — PASS

Every stage-1 statistic in the frozen R2 receipt reproduced exactly from
regenerated data: `1146` instances, `127` features, `1109` cells, `1072`
singletons, `0` mixed cells, floor `0`, compression `0.967714`, per-`n` counts
`6/60/1080` with `5/28/189` donor-exact. **Zero mismatches.**

This discharges the #1609 ORION-09 line *"independent replay of selected QG
receipts"* for the R2/N2 receipt.

The extraction pipeline was additionally validated against three floors recorded
in the receipt but not used to build it — V1 → `43`, V2 → `1`, L2 → `5` with `3`
mixed cells — all matching. A separator-complexity number from an unvalidated
extraction would be worthless, so this validation is a precondition, not a bonus.

## 3. What was established

### 3.1 The memorization concern is real, bounded, and resolved

The R2 addendum's near-injectivity disclosure is correct and was a pre-frozen
gate. It was qualitative. It is now quantitative:

- **Theorem B** (`E* <= (N-c)/N`) shows the realized cell structure confined the
  floor to `[0, 37/1146] = [0, 0.0323]` before any label was read.
- The exact **structure-free null** — probability that a random relabelling with
  the same cells and class balance also attains floor 0 — is `7.057e-07`, with
  `0/20000` permutation hits.

So floor 0 is **not** a small-cell artifact. The labels genuinely align with the
feature partition.

### 3.2 A compact four-feature law exists — `k* = 4`, proved

`k*`, the minimum number of frozen features whose projection still attains floor
0, is **exactly 4**:

- **`k* >= 4`** by exhaustive refutation — all `127` singletons, all `8001`
  pairs and all `333375` triples fail to separate every opposite-label pair.
- **`k* <= 4`** by a directly verified witness `{15, 30, 39, 42}`, re-projected
  over all `1146` instances: `523` cells, `0` mixed, floor `0`.

The witness map has compression `0.456` — **nowhere near injective**. By Theorem B
its floor could have been as large as `623/1146 = 0.544`; it is `0`. Its
structure-free null is `1.442e-120`.

This is precisely the *"compact or low-dimensional law"* the R2 addendum declined
to claim. The addendum's caution was right for what had been computed; exact
computation on the same frozen data now supersedes it **in the favourable
direction**.

### 3.3 Adverse: the mechanism attribution is not supported

Any **two** of L3's three blocks attain floor 0. In particular
`V2 + donor-path` — both committed *before* the revival — attains floor 0 with
**no sign-aware feature at all**, and the minimal witness contains **zero**
STATE-block coordinates.

The addendum's pair-level witness is not contradicted: the STATE block does
separate the specific V2-surviving mixed pair. What is not established is the
stronger reading that sign-awareness is *the* operative mechanism. **The
conversion did not require the new block.**

This is preserved as an adverse finding. It does **not** overturn `floor(L3)=0`
or the `H_A_N2 = POSITIVE_CONVERSION` verdict, both of which stand.

## 4. Adverse and null evidence — all preserved

The `n = 4` negative is untouched and is reported with every positive statement,
never separately: `H_B_N4_residual = NOT_IMPROVED`, `32/120` CV errors equal to
the parent cell-lookup baseline, shuffle-null mean `32.41`, empirical `p = 0.51`.
The QG-23 V2 lattice parent still beats L3 out of sample (`3/120` vs `32/120`) and
that is not explained away.

The correct combined statement, used everywhere in this packet:

> A compact four-feature law determines donor-exactness on the frozen `n <= 3`
> domain, and it does not transfer to unseen `n = 4` states.

The `NOT_R6` authority ceiling and the no-physical-advantage constraint are
unchanged. No `CANNOT_CHECK` was converted to a pass.

## 5. Supersession of the #1617 premise

The candidate note asks to recompute a `43/1146` *irreducible* floor and to
retain a nonzero lower bound if no frozen extension purifies the fibres. A frozen
extension **did** purify them, on 2026-08-28. `43/1146` is the V1 floor —
reproduced exactly — not a property of the current vocabulary.

The note's own strongest falsifier anticipated exactly this and has fired. The
live successor question is separator complexity, and the answer is `4`.

## 6. Submission blocker — referred, not taken

`manuscript/main.tex` (abstract) states:

> "no predicate in the frozen natural feature vocabulary exactly separates
> donor-exactness, and mixed feature cells impose an irreducible 43/1146 error
> floor **regardless of predicate budget**. Thus the transferable object is the
> mapping discipline, **not a universal low-order boundary law**."

The manuscript contains **zero** occurrences of `R2`, `L3` or `revival`. Evidence
committed in this paper's own `evidence/` directory is not integrated anywhere.

**The defect is omission, not falsity.** Every quoted sentence is true as written:

| element | verdict |
|---|---|
| V1 floor is `43/1146`, irreducible within V1 | **true**, reproduced exactly |
| "regardless of predicate budget" | **true as scoped** — by Theorem A no predicate over V1 beats the V1 floor |
| "not a universal low-order boundary law" | **true** — and §4 of this packet independently supports it |
| a low-order law is domain-local, not universal across `n` | **supported** by §4 |

What is wrong is that the abstract presents a **superseded scoped result as the
paper's StabPrep finding** while the prospectively frozen revival sitting in this
paper's own `evidence/` directory appears nowhere in the manuscript. A reader
finishes the abstract believing the vocabulary question is closed negatively. It
is not: under an enlarged frozen vocabulary the floor is `0` and four features
suffice on `n <= 3`.

That is material incompleteness, not a false claim, and it blocks submission
under #1609 §A (headline statements generated from immutable result artifacts)
and §D (abstract maps to a claim/evidence matrix).

**ORION-09 must not be submitted until the abstract is rescoped.** The rescope is
an **addition and re-scoping, not a retraction** — the paper's negative
conclusion survives in a sharper form. Proposed replacement for the two
sentences:

> "A third-family StabPrep transfer preserves the trade-mapping programme and
> sharpens the cross-family motif question. In the originally frozen natural
> feature vocabulary no predicate separates donor-exactness and mixed cells impose
> a `43/1146` floor; under a prospectively frozen enlarged vocabulary the floor is
> `0`, and exactly four features suffice on the complete `n <= 3` domain. That
> low-order law does not transfer to unseen `n = 4` states, where the enlarged
> vocabulary matches a shuffle null. The transferable object is therefore the
> mapping discipline together with a domain-local boundary law, not a universal
> one."

This edit is **not taken here**: it changes claim authority in the abstract and
belongs in its own PR with its own review, per #1608's rule that no frozen paper
byte is modified merely to run successor science.

## 7. Donor boundary and novelty

**No novelty is claimed** for Theorems A, B or C. Per-fibre majority optimality,
the discernibility/hitting-set characterization of sufficiency, and the reduct
formulation are donor-owned rough-set and information-sufficiency mathematics;
the counting bound in Theorem B is elementary and very likely classical.

The ORION-specific content is the exact instantiation on the frozen StabPrep
domain: `k* = 4` with its witness, the block-attribution table, and the two
structure-free nulls.

## 8. Blocker status for the paper

`ORION-09 IS BLOCKED` — but by §6, an abstract rescope, **not** by this successor
theory. The theory itself creates no new experimental prerequisite and generates
no successor study. Per #1608's portfolio rule, optional successor science must
not hold a coherent bounded paper open; here the hold comes from a stale claim in
the paper's own abstract, which is a Wave-1 correctness item under #1609.
