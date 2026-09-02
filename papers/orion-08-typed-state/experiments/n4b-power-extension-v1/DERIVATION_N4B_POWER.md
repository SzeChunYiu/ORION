# DERIVATION — N4-B power extension V1 (ORION-08 successor)

Companion: `PROTOCOL_N4B_POWER.md` (committed before any outcome). Parent:
`papers/orion-08-typed-state/PUBLICATION_PAIRED_ANALYSIS_V1.json` (frozen
secondary analysis) and the manuscript limitation it leaves open: the two
N4-B `scoped_vs_never` contrasts are the surviving rows whose mean intervals
contain zero — their registered disposition (the mean) stays **undetermined**
at the frozen n.

## What is being determined

| contrast | frozen mean | frozen 95% CI | status |
|---|---|---|---|
| STALE_MATTERS scoped vs never | +0.774 | [−0.664, +2.254] | undetermined |
| REOPEN_WASTEFUL scoped vs never | +0.060 | [−0.540, +0.634] | undetermined |

Nothing about the frozen protocol changes: same module
(`research/extensions/orion-q/nlanes/n4_b_stale_receipt_reopening.py`),
same seed (20260821), same arms (`ORION_SCOPED_REOPEN` treatment,
`NEVER_REOPEN` comparator), same metric (`mean_round_utility`), same paired
estimand (per-episode difference, mean over episodes). The extension only
**continues the frozen RNG stream**: the frozen layout is generated first
(STALE_MATTERS 1..200 then REOPEN_WASTEFUL 1..200 — stream draws 1..400,
byte-identical to the frozen analysis by determinism of `random.Random`),
then each regime's block is extended in `REGIMES` order on the same stream
(STALE 201..2000 = draws 401..2200, REOPEN 201..2000 = draws 2201..4000),
so **both frozen 200-blocks are prefixes** of the extension and episodes
201..2000 are the new, pre-outcome-registered mass. No re-seeding, no
stratification, no selection. (A1-N4B: the originally registered
block-of-2000 layout could only ever reproduce the first regime's prefix —
P1 caught it; see the protocol amendment.)

## Power arithmetic (from the frozen intervals only)

Per-pair sd estimated from the frozen CI half-widths (÷1.96·, ×√200):

- STALE_MATTERS: sd ≈ 10.5 → se(n=2000) ≈ 0.235 → Bonferroni-97.5% CI
  half-width ≈ 0.53. Frozen mean +0.774 → predicted interval ≈ [+0.25,
  +1.30] → excludes zero (z ≈ 3.3, power ≈ 96% if the frozen point estimate
  holds).
- REOPEN_WASTEFUL: sd ≈ 4.2 → se ≈ 0.095 → half-width ≈ 0.21. Frozen mean
  +0.060 → predicted interval ≈ [−0.15, +0.27] → contains zero but sits far
  inside any practical bound.

## Registered practical-equivalence bound

δ = 1.0 mean-round-utility, chosen from the frozen data alone: it is
≈ 1/7 of the smallest N4-B effect the manuscript already carries as resolved
(scoped vs unscoped, STALE_MATTERS, +6.97) and ~1/15 of the REOPEN_WASTEFUL
one (+15.05); anything below one round-utility cannot move the manuscript's
qualitative claim that scoped reopening recovers essentially all of the
unscoped loss while never paying for it. `BOUNDED_NULL` requires the
corrected CI ⊂ (−δ, +δ).

## Registered predictions (non-vetoing, always reported)

- P-STALE resolves `RESOLVED_POSITIVE` (excludes zero, favors scoped).
- P-WASTE resolves `BOUNDED_NULL` (contains zero, inside ±1.0).
- Continuity: scoped_vs_unscoped point estimates in both regimes stay
  within ±10% of the frozen values (monitoring only, not a target).
- Split-half (first 1000 vs second 1000 per regime): both halves' point
  estimates on the same side of zero as the full-sample value (no stream
  drift is expected — the generator is regime-stationary by construction).

## Terminals

Per target: `RESOLVED_POSITIVE` / `RESOLVED_NEGATIVE` (Bonferroni-97.5% CI
excludes 0) / `BOUNDED_NULL` (CI ⊂ (−δ, +δ)) / `UNRESOLVED` (neither).
Study: `N4B_POWER_DETERMINED_BOTH` (both targets resolved or bounded) /
`N4B_POWER_PARTIAL_<which>` / `N4B_POWER_PREFIX_FAIL` (cross-check P1
fails → no verdict, exit 3). Frozen artifacts untouched; this experiment is
additive under `experiments/n4b-power-extension-v1/`.
