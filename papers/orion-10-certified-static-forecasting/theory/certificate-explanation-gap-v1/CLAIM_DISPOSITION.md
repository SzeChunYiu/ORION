# ORION10.CERTIFICATE_EXPLANATION_GAP.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Terminal:** `THEORY_PROVED__COUNTS_REPRODUCED`
**Scientific authority delta:** `NONE`
**New blocker raised:** none

---

## 1. What changed

One additive directory under
`papers/orion-10-certified-static-forecasting/theory/`. No manuscript, receipt or
ledger byte was modified.

## 2. What was established

**Theorem 1.** An exact `Psi`-only explanation exists iff `cost` is constant on
every `Psi`-fibre.

**Theorem 2 (the useful one).** If a `Psi`-fibre is cost-mixed, **no function of
`Psi` is exact — of any expression size, in any language over `Psi`.**

**Theorem 3.** An exact certificate can coexist with no exact `Psi`-explanation
exactly when the certificate separates a cost-discriminating pair that `Psi`
merges. That is ORION-10's situation stated formally.

## 3. The practical consequence

The candidate note proposes freezing *"allowed primitive predicates, operators,
interaction order, expression-size budget."*

Theorem 2 says three of those four cannot affect any exactness verdict. **Only
the primitive predicates matter**, because only they determine the fibres. A
grammar freeze that spends its rigour on a size budget is freezing the wrong
thing.

That narrows the productive next moves to exactly two: enlarge `Psi` with a
separating primitive, or prove a **vocabulary-level** lower bound by exhibiting
two instances with equal `Psi` and different exact cost for a `Psi` frozen in
advance. The second is what would convert *"improving but not yet an all-`n`
theorem"* into a permanent statement.

## 4. What the 64 witnesses actually proved

By Theorem 2 they are a proof that **`B'` is insufficient as a vocabulary** — not
that a longer or cleverer `B'`-formula was needed. Each subsequent enlargement
(phantom homes, the hybrid `B''`) is a vocabulary move, which is the only kind
Theorem 2 permits.

This **strengthens** what the refutation established. It does not soften it.

## 5. Independent verification

No ORION-10 or QG module imported. Theorems verified on freshly enumerated
structures over **21,501** `(Psi, cost)` configurations; the QG-7b receipt is
read as data and never executed. **3/3** negative controls fire.

All four manuscript counts reproduce exactly from the frozen receipt:

| quantity | manuscript | receipt |
|---|---|---|
| fourth-configuration witnesses | 64 | **64** |
| instances evaluated | 740 | **740** |
| rows closed by the hybrid family | 10,481 | **10,481** |
| fifth configurations | 0 | **0** |

The size-independence check is exhaustive **by construction**: the complete set
of `Psi`-measurable functions is the set of fibre-assignments, so enumerating
them covers every formula of every size in every language over `Psi`.

## 6. Adverse and null evidence

All preserved and none converted. `all_n_theorem_authority: false`,
`all_n_identity: UNPROVED_CANNOT_CHECK_FROM_CURRENT_PARENT_QUOTIENT`,
`btripleprime: UNFOUND_IN_FROZEN_PADDING_ABLATION`, the open comm-`s2` sector,
`novelty_authority: false` and `physical_quantum_advantage_claim: false` all
stand unchanged. **A `CANNOT_CHECK` is preserved as a `CANNOT_CHECK`.**

## 7. Donor boundary

**No novelty claimed.** Measurability with respect to a partition, and the fact
that a function of a statistic is constant on its level sets, are elementary and
donor-owned — the same information-sufficiency spine as ORION-09 and ORION-13.

## 8. Recommended action — referred, not taken

The §3 reading could inform how the next grammar freeze is written. No manuscript
edit is taken; per #1634 there is currently no sanctioned path for correcting a
manuscript bound by a paper-level `SHA256SUMS`.

## 9. Blocker status

`ORION-10 IS NOT BLOCKED BY THIS LANE.` The vocabulary-level lower bound is
optional successor science.
