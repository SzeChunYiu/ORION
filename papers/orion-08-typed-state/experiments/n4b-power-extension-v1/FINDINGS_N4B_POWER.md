# ORION-08 — N4-B power extension V1: findings

**Terminal: `N4B_POWER_DETERMINED_BOTH`** (exit 0). Both contrasts the
manuscript's limitations section left **undetermined** are now determined —
as **bounded nulls**, not as the directions the frozen point estimates
suggested. Protocol + A1-N4B amendment committed before this outcome;
pass-1 receipt (P1 abort) retained. n = 2000 per regime (frozen 200 =
byte-identical prefix of each block, P1 exact 0.0 both regimes).

## Result

| contrast | frozen (n=200) | extension (n=2000) | 97.5% CI | verdict |
|---|---|---|---|---|
| STALE_MATTERS scoped − never | +0.774 [−0.66, +2.25] | **−0.097** | [−0.673, +0.447] | **BOUNDED_NULL** |
| REOPEN_WASTEFUL scoped − never | +0.060 [−0.54, +0.63] | **+0.019** | [−0.181, +0.220] | **BOUNDED_NULL** |

Bonferroni family m = 2 → per-comparison two-sided 97.5% bootstrap CIs
(5000 draws). Practical-equivalence bound δ = 1.0 registered pre-outcome.

**Reading:** with ten times the mass, neither scoped-vs-never contrast
excludes zero — instead both are confined to |effect| < 1 round-utility
(and in the wasteful regime to ±0.22). Combined with the continuity rows
(scoped beats unscoped by +6.50 / +14.37, both within 10% of the frozen
values, direction-consistent), the manuscript's qualitative claim upgrades
from "direction consistent but undetermined on the mean" to a quantitative
one: **scoped reopening recovers essentially all of the unscoped loss at a
bounded, sub-δ cost relative to never reopening — in both regimes, in
particular in the regime where reopening is mostly waste.** The one-sided
win structure survives (STALE 60.5% wins vs 23.8% losses; REOPEN 13.4% vs
4.9%) but the mean is the registered estimand and the mean is ≈ 0.

## Registered predictions — two of four failed (reported, non-vetoing)

- **P-STALE (RESOLVED_POSITIVE): FAILED.** The frozen +0.774 was
  small-sample noise; at n = 2000 the mean sits at −0.097. The naive "add
  power, resolve the sign" reading is refuted by the data.
- **P-WASTE (BOUNDED_NULL): held** (CI [−0.18, +0.22] ⊂ (−1, 1)).
- **Continuity (scoped_vs_unscoped within ±10%): held** both regimes.
- **Split-half same-side: FAILED in both regimes** (STALE +0.33/−0.52,
  REOPEN −0.04/+0.08 — halves straddle zero). Under a true ≈0 effect with
  per-half se ≈ 0.33 (STALE), straddling is the expected behavior — the
  failure is the null verdict speaking, not stream drift (the generator is
  regime-stationary; the frozen prefixes reproduce exactly).

## Discipline record

Pass 1 aborted at the registered P1 gate (REOPEN prefix off by 0.2279 —
the originally registered stream layout could not reproduce any prefix but
the first regime's). Amendment A1-N4B (frozen layout first, then extend
each block in order) fixed the layout pre-verdict; no gate, threshold, δ,
family, seed, or target changed. Receipts: `RESULTS_pass1_aborted.json`,
`RUN_pass1_aborted.log`. Frozen protocol, module, and
`PUBLICATION_PAIRED_ANALYSIS_V1.json` untouched; this study is additive.

## What this changes in the manuscript's limitation

"Targeted verification … and decision-coupled acquisition … are the
surviving contrasts whose intervals lie closest to zero" — for the N4-B
half of that sentence, the two zero-containing rows are no longer
undetermined: they are bounded nulls at n = 2000 (this experiment). The
manuscript text itself is frozen; this finding is the additive successor
record a future revision cites.
