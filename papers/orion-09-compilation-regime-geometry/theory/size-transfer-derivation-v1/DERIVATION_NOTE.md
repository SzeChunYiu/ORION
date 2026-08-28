# ORION-09 size-transfer — label-free derivation material

**Status:** `DERIVATION_ONLY__PROMOTION_BUDGET_NOT_SPENT`
**Governing issue:** #1649 Tier B
**Blueprint:** ORION Wave-1 Top-Tier Closure Blueprint 2026-08-28, §4.18–4.22
**Scientific authority delta:** `NONE`

---

## 1. What this is, and what it deliberately is not

This is **not** ORION-09's one promotion attempt under #1649. That budget is
**unspent**, and this note exists to keep it that way while preserving work that
would otherwise have to be recomputed.

The blueprint is explicit on two points that together rule out the attempt I was
preparing:

- **§4.18:** *"another normalization or post-hoc feature fit is not a valid
  promotion path."*
- **§4.22:** *"Because n=4 has already been observed, it cannot prospectively
  validate a theorem discovered from it. Use n=4 only for derivation and
  adversarial proof checking."*

I had begun a capacity-ratio predictor — a statistic over the four witness
features' value ranges. On the blueprint's reading that is a feature-level fit,
not the structural invariant §4.19–4.20 asks for (canonical interaction
hypergraph, local obstruction signatures `O_t`, disjoint-union stability, gluing
completeness). Spending the one attempt on it would have burned the budget on the
wrong object.

So the measurements below are filed as **derivation material**, which is exactly
the use §4.22 permits for `n=4`.

## 2. The measurements are label-free

`compute_label_free_capacity.py` enumerates the `n=3` and `n=4` domains and
computes the four witness features `{15, 30, 39, 42}` for every instance. It
**never reads the donor-exactness label**. The referee's distance map is used only
to enumerate states.

That matters for custody: nothing here consumes the `n=4` outcome, so the
prospective position for a future `n=5` test is untouched.

| n | instances | witness value ranges | capacity product | realized cells | capacity ratio | compression |
|---|---|---|---|---|---|---|
| 3 | 1,080 | 15 · 28 · 16 · 5 | 33,600 | 523 | 31.11 | 0.484 |
| 4 | 36,720 | 20 · 47 · 33 · 5 | 155,100 | 4,817 | **4.22** | **0.131** |

## 3. What the numbers say, stated at their real strength

The four-feature map **collapses sharply** with size. At `n=3` it spreads 1,080
instances over 523 cells (≈2.1 per cell); at `n=4` it spreads 36,720 over 4,817
(≈7.6 per cell). Capacity ratio falls `31.1 → 4.2`.

By `ORION09.REGIME_SEPARATOR_COMPLEXITY.v1`'s compression bound (PR #1627), the
**maximum attainable floor** rises correspondingly:

```
n=3:  (1080 - 523)/1080   = 0.516
n=4:  (36720 - 4817)/36720 = 0.869
```

So the structural room for mixed fibres at `n=4` is far larger than at `n=3`.

**This is a plausibility argument, not a theorem, and not a promotion.** It says
the witness map has much more opportunity to fail at `n=4`; it does not say it
does fail, and it supplies no invariant that predicts *which* instances collide.
The blueprint's `O_t` obstruction basis would; a capacity ratio would not.

## 4. Adverse evidence that stays load-bearing

The blueprint's §4.18 record is preserved verbatim in force: **the `n=4` forecast
failed**, the later n-dependence study found extensive features caused support
failure, its frozen normalization produced no useful competence region, and **no
`n=5` component was ever executed**. Nothing here softens any of that.

`ORION09.REGIME_SEPARATOR_COMPLEXITY.v1`'s own findings also stand unchanged:
`k* = 4` on `n<=3`, the sign-aware mechanism attribution falsified, and the `n=4`
panel at chance (32/120 errors, shuffle `p = 0.51`).

## 5. What a real attempt would require

Per §4.19–4.22, and recorded here so the next attempt starts from the right
object rather than this one:

1. define the canonical interaction hypergraph and `O_t` signatures;
2. prove — or refute — local witness property, disjoint-union stability and
   gluing completeness;
3. freeze `t`, the obstruction basis, the boundary signature and the predictions;
4. freeze a deterministic `n=5` challenge set covering every predicted stratum,
   **before** any `n=5` exact labels;
5. prohibit feature or threshold changes after labels;
6. use an exact referee and an independent prediction checker.

Only step 4 onward consumes prospective custody. Steps 1–3 can use the `n<=4`
corpus freely, which is what §4.22 means by *derivation*.

## 6. Authority

`scientific_authority_delta = NONE`. No claim, terminal, receipt or manuscript is
modified. **ORION-09's #1649 promotion budget remains unspent**, and this note is
explicitly not an attempt at it.
