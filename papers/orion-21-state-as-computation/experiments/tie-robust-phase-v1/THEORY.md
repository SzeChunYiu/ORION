# Tie-robust phase boundaries — theory

**Protocol identity:** `ORION21.TIE_ROBUST_PHASE.v1`
**Status:** `PREREGISTERED__OUTCOMES_NOT_READ`
**Authority:** none. This document states a criterion and a prediction; it grants no
law, width, mechanism, superiority, manuscript-freeze or submission authority.

## 1. The object

A screening rule ranks a feature bank by absolute integer correlation with the label
stream and keeps the top `r` features as a support. When the `r`-th and `(r+1)`-th
absolute correlations are **equal**, the rule does not name a support: it names a
**set** of supports. Write

    S(x)  =  { s : s is consistent with the declared ordering, including every
                   admissible resolution of boundary equalities }

`S(x)` is a singleton exactly when the top-`r` rank gap is separable. Otherwise
`|S(x)| > 1` and every downstream quantity computed "from the support" is set-valued.

## 2. The criterion

Let `M(s, x)` be the exact downstream metric under support `s`, and let `τ` be a
preregistered threshold. A threshold conclusion at `x` is **tie-robust** iff

    max_{s ∈ S(x)} M(s, x) < τ        or        min_{s ∈ S(x)} M(s, x) ≥ τ .

If `min M < τ ≤ max M`, the conclusion straddles the threshold and **no
implementation-specific tie ordering establishes it** — unless the secondary ordering
is itself part of the prospectively frozen scientific object.

The criterion is near-definitional once `S(x)` is made explicit. The scientific work is
(i) making set-valued support semantics part of the registered measurement object, and
(ii) characterising when equality classes occur and whether they bind.

## 3. Why this bites for NR07

NR07's registered primary quantity is a threshold crossing:

    n_cross(p)  =  smallest ladder train size whose 7-seed mean screening accuracy
                   reaches τ = 0.95

So `n_cross` is not merely measured with error — it is *defined* by which side of `τ`
a mean falls on. Set-valuedness of `M` therefore propagates into set-valuedness of the
quantity the width law predicts:

    n_cross_hi  =  smallest n such that  min-over-worlds 7-seed mean ≥ τ
    n_cross_lo  =  smallest n such that  max-over-worlds 7-seed mean ≥ τ

with `n_cross_lo ≤ n_cross_hi`, and equality exactly when the crossing is tie-robust.

`DIAGNOSIS.md` establishes from the authoritative bytes that ties are pervasive
(479/1050 = 45.6 % of ladder points have a non-separable rank gap) and that **all 10**
ladder cells have their crossing sitting on tied points. It does **not** establish that
`n_cross` is set-valued, because the ladder readings record only the realised selection.
That is what this experiment measures.

## 4. Prediction and the two hypotheses

- **H_LOCAL** — `n_cross_lo = n_cross_hi` at every cell. Tie exposure is incidental; the
  C1/C2/C3 verdict is well-defined and the registered study can adjudicate its hypothesis.
- **H_SYSTEMIC** — `n_cross_lo < n_cross_hi` at one or more cells. `n_cross` is an
  interval, and the width-law verdict must be evaluated over the admissible set.

These are mutually exclusive and jointly exhaustive given a successful reconstruction.
Neither is favoured by the design. H_LOCAL would *rescue* the registered study; H_SYSTEMIC
would show it cannot adjudicate its own hypothesis under its frozen protocol.

## 5. Relation to the quarantined repair

The quarantined `V1_1` move widened the exact-replay tolerance from 1e-12 to 1e-3. The
observed replay delta was 1/20480 = 4.88e-05, so the widened gate passes. But tolerance
acts on the *replay comparison*, not on the *support selection*, and therefore cannot
remove set-valuedness. No tolerance value repairs an under-specified measurement object.
This experiment fixes the object instead, by binding a deterministic secondary key and by
reporting the admissible range rather than a point.

## 6. Donor credit

Set-valued / non-unique-argmax semantics, tie-breaking in selection rules, and partial
identification of a parameter defined by a threshold crossing are all established ideas
and are donor-owned. Nothing here claims them as novel. The contribution claimed, if the
experiment supports it, is narrow: that this specific registered quantity is partially
identified under its own frozen protocol, and by how much.
