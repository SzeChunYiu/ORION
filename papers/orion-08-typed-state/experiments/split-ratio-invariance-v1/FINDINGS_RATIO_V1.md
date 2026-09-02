# ORION-08 — split-ratio invariance V1: findings

**Terminal: `LAW_V4_RATIO_INVARIANT`** (exit 0, first pass, no amendment
needed). Protocol + derivation + driver committed and pushed (620784cb8)
before the outcome run, which executed at exactly that SHA. One clean pass,
16-dataset frozen V3 cohort, registered grid E-fraction ∈ {0.25, 0.50
(anchor), 0.75}, frozen MC (10k draws, seed 20260903, at every ratio).

## Result — the law's untested prediction held

The calibrated V3 law implies calibration is invariant to the S:E split
fraction (disjointness, not the 50/50 balance, is the operative condition).
Every registered gate passes at BOTH non-anchor ratios:

| gate | e = 0.25 | e = 0.75 |
|---|---|---|
| G1 confident set | 0 violations (2 confident) | 0 violations (5 confident) |
| G2 calibration (80% CI) | 14/16 inside, p = 0.754 | 11/16 inside, p = 0.342 |
| G4 zero stratum (live falsifier) | 3/3 exactly 0 | 3/3 exactly 0 |
| Jeffreys sensitivity | no sign breaks | no sign breaks |
| D1 z-balance (non-vetoing) | 8/13 neg, p = 0.581 | 8/13 neg, p = 0.581 |

Structural cross-checks: **R4a anchor reproduction exact** (max |diff| =
0.0 across all 16 datasets' registered scalars — the parametrized
orchestration is a faithful generalization of the frozen V3 module, gate
confirmed rather than assumed); R4b MC-vs-closed-form clean at every
dataset × ratio; anchor coverage 12/16 = V3's exactly.

**Reading:** V2's winner's-curse signature (one-sided z, 11/13) does not
reappear at any fraction — shrinking either half leaves the predictive
calibrated. The zero stratum (qsar-biodeg, 1487, 40701) observes exactly 0
under all three S-selection sizes even though the selected action maps
differ off-anchor — selection-robustness confirmed at both extremes, G4's
live falsifier standing.

## Registered diagnostics — one failed, reported (non-vetoing)

- **D4 width ordering: FAILED (6/13 monotone, threshold 9).** The
  pointwise prediction σ̂(0.25) ≥ σ̂(0.50) ≥ σ̂(0.75) does not hold on a
  majority. One-stage attribution: the prediction assumed a FIXED fibre
  table across e; in fact the E-occupied table itself changes with e
  (e.g. wdbc 13→18→28 R-fibres; diabetes 48→66→133). Per-fibre posterior
  variance is driven by counts-per-fibre (n_E/F), and F grows with e —
  support growth opposes 1/√n_E scaling, so width is table-mediated, not
  n_E-only. The failure is confined to the secondary width prediction; the
  primary registered prediction (calibration invariance) is untouched.
- **D5 separator (openml-6332) dose-response: mixed.** inside80 = true at
  e = 0.25 (51 R-fibres, σ̂ = 0.059), false at 0.50 (83, 0.048) and 0.75
  (111, 0.045). The miss returns exactly as E-support grows and the
  predictive tightens — more E data sharpens the predictive around the
  E-supported distribution while test mass keeps landing on unseen fibres.
  Consistent with V3's attribution that support drift, not selection, owns
  this separator; the coarse-support cover is interval width, not mechanism
  repair.

## Discipline record

Single clean pass at the registration SHA; no gate, threshold, cohort, seed,
or model constant changed after registration. Smoke-tested truncated
(3 datasets, `--smoke`, no receipt) before the registration commit. Frozen
Tier-B package, V1/V2/V3, and N4-* artifacts untouched; this study is
additive under `experiments/split-ratio-invariance-v1/`. V3's verdict is not
re-litigated — this study tested a different (previously untested)
prediction of the same calibrated law, and that prediction held.

## Arc (successor ledger)

V1 mean-sign law REFUTED → V2 distributional law REFUTED (one-sided
optimism attributed to winner's-curse selection + unseen-fibre mass) → V3
selection-corrected law CALIBRATED (at 50/50) → **V4 split-ratio
invariant: the calibration survives both directions of S:E stress
(posterior-starved e = 0.25 and selection-starved e = 0.75), D1 stays
balanced, zero stratum selection-robust at every fraction.**

## Next open residual queued

The width law (D4): a table-aware σ̂ model predicting when support growth
overrides 1/√n_E — would need a pre-registered derivation (counts-per-fibre
scaling), NOT a fit. The 6332 support-drift mechanism (D5) remains the
cohort's one uncovered dataset at e ≥ 0.5; modeling unseen-fibre mass is
deliberately out of scope (no parameter-free form is registered).
