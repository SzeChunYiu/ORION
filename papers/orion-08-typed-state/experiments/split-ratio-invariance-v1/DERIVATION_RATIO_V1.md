# DERIVATION — split-ratio invariance V1

Companion: `PROTOCOL_RATIO_V1.md` (committed before any outcome). Parent:
`../finite-sample-law-v3/` (terminal `LAW_V3_CALIBRATED`).

## The prediction, derived from the registered mechanism

V3's mechanism model has exactly one independence claim: rows are iid, so the
E-half's fibre counts are independent of the actions selected on the disjoint
S-half. The calibrated predictive is the standard conjugate posterior for a
*fixed* policy under that independence.

Nothing in that argument uses the 50/50 split V3 happened to register. Fix an
E-fraction e ∈ (0,1) and split the train rows into S (1−e) and E (e):

- **Independence is preserved for every e.** S-selection still conditions on
  rows disjoint from the E-counts; the predictive remains an unconditional
  posterior for a (different) fixed policy. Coverage of the 80% central
  interval and confident-set sign correctness are therefore predicted to hold
  at every e on the cohort — the *law*, not the balance, is doing the work.
- **Width is predicted to scale with E-uncertainty.** The Beta-Binomial
  per-fibre posterior variance ~ p(1−p)/(n_s+3) and the multinomial
  allocation both tighten as E grows, so σ̂(e) decreases in e pointwise
  (registered as diagnostic D4, not a gate: per-dataset action maps also
  change with S, so strict pointwise monotonicity is expected on a large
  majority, not universally).
- **The falsifier is real, not structural.** At e ≠ 0.5 the S-share changes,
  so the selected action map changes, so the observed Δ and the zero-stratum
  realization can change (G4 stays a live falsifier). If one-sided z-misses
  (V2's winner's-curse signature) or confident-set sign violations appear at
  any e, then disjointness alone is NOT the operative condition — the 50/50
  calibration would be balance-specific and the V3 attribution incomplete.

## Why {0.25, 0.75} and not a finer grid

The two directions stress the two halves of the mechanism separately:
e = 0.25 shrinks the posterior's conditioning set (support shrinks — the
D5/6332 support-drift read is stressed hardest here); e = 0.75 shrinks the
selection set (actions chosen from little data — the "fixed policy" is
coarser). Two ratios + the 0.50 anchor give both directions at cohort-wide
gate power; a finer grid multiplies compute without adding a qualitatively
new failure mode, and every added ratio is another look at the same 16
answers (multiplicity the cohort cannot afford at n = 16).

## What this study does NOT test

- No new data: the CC18 registry is exhausted (V2 amendment A1); cohort
  transfer is therefore untestable by scan and deliberately not claimed.
- No re-coupled control: V2 at 50/50 already supplies the coupled estimator's
  miss pattern; re-running it at other ratios would re-litigate V2's verdict.
- No unseen-mass model: the predictive still allocates all test mass to
  E-occupied fibres (DERIVATION_V3 "deliberately NOT modeled"); D5 reports
  the separator's dose-response instead of fitting it away.

## Gate arithmetic (frozen from V3, restated)

- G1: |Δ̂| > 2σ̂ ⟹ sign agreement; one violation fails the ratio.
- G2: inside-count ~ Binomial(n, 0.8), two-sided exact test at α = 0.05,
  achieved n = 16 per ratio (per-ratio tests, not pooled: each ratio is an
  independent instantiation of the same prediction; pooling would hide a
  single-ratio failure).
- G4: V1-zero datasets (V2 rows' `predicted_zero_v1`) must observe Δ = 0
  exactly (3 datasets at 0.50; the stratum membership is V1's, frozen).
- R4a tolerance 1e-12 (not 0.0) — float JSON round-trip parity; V3's own
  cross-checks used the same convention via < 1e-12 / exact-where-printed.
- R4b tolerance 3·MC-SE, the V3 registered bound.

## New named constants (all registered before the run)

E_FRACS = {0.25, 0.75} (0.50 = anchor), R4A_TOL = 1e-12, D4 threshold = 2/3
of the all-nonzero stratum. Everything else is frozen from V3/V2/V1,
including MC seed 20260903 (used verbatim at every ratio — the ratio sweep
must not perturb the MC stream relative to the anchor).
