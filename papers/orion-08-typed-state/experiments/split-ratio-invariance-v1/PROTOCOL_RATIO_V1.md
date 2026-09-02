# PROTOCOL — split-ratio invariance V1 (ORION-08 successor)

Committed BEFORE any outcome. One script (`run_split_ratio_invariance_v1.py`),
one pass, stdout + JSON receipt (schema `ORION08.SPLIT_RATIO_INVARIANCE.v1`) +
SHA256SUMS. The statistical machinery is the frozen V3 implementation, imported
(`papers/orion-08-typed-state/experiments/finite-sample-law-v3/
run_finite_sample_law_v3.py`: `load_openml`, `binned`, `policy_actions`,
`predictive_mc`, `closed_form_mean_delta`, `oracle_utility`,
`binom_two_sided[_08]`, `COHORT`, `v2_index`, and every frozen constant). No
statistical code is re-implemented; the driver only re-orchestrates those
primitives with a parametrized inner-split fraction.

## Registered question

The V3 law (terminal `LAW_V3_CALIBRATED`) states: when the fibre action map
is selected on training rows disjoint from the posterior's conditioning set,
the Beta-Binomial posterior-predictive of held-out refinement utility is
calibrated. The law's mechanism model (rows iid) implies a sharp, untested
prediction: **calibration is invariant to the S:E split fraction** — at any
fraction the E-counts remain independent of the S-selected actions, so
disjointness, not the 50/50 balance V3 happened to use, is the operative
condition. This study tests that prediction on the exact frozen cohort.

## Registered design

- **Cohort:** the exact V3 sixteen (hard ids, `COHORT` in the frozen module);
  identical outer split (`test_size=0.5`, stratify, seed 20260830) — test sets
  byte-identical to V2/V3.
- **Inner split grid (registered):** E-fraction ∈ {0.25, 0.50, 0.75}, same
  seed 20260830, stratify. **0.50 is the reproduction anchor** (must reproduce
  V3 exactly, see R4a); 0.25 and 0.75 are the new mass.
- **Estimator:** the frozen V3 pipeline verbatim (S-stage selections on the S
  half-share, E-only posterior with uniform prior primary + Jeffreys
  sensitivity, R-fibre lift with the DERIVATION_V3 §6 unseen-in-S fallback,
  per-test-row scale, MC 10,000 draws / chunk 2,000 / seed 20260903 at every
  ratio — the MC seed is NOT re-drawn per ratio).
- **No new fitted parameter.** The only new constants are the grid values and
  the tolerances named here.

## Cross-checks (gated, structural — abort before any verdict on failure)

- **R4a exact reproduction at 0.50:** per dataset, the recomputed
  uniform {mean_delta, std_delta, p_delta_neg, ci80 lo/hi}, jeffreys
  {mean_delta}, observed {typed_delta, oracle_utility}, n_R_fibres, and
  closed_form_mean_delta must match `RESULTS_V3.json` within 1e-12 each.
  n_compared must be 16. Failure → `V4_INCOMPLETE_REPRODUCTION_FAILED`
  (exit 3).
- **R4b MC vs closed form:** |MC mean − closed form| < 3·MC-SE on every
  dataset × every ratio (uniform prior). Failure → same abort terminal.

## Gates (per non-anchor ratio r ∈ {0.25, 0.75}; definitions identical to V3)

1. **G1 confident set:** every dataset with |Δ̂| > 2σ̂ has
   sign(Δ̂) = sign(observed Δ).
2. **G2 calibration:** count of observed Δ inside its 80% central interval
   passes the two-sided exact binomial vs p = 0.8 at α = 0.05, achieved n
   (16).
3. **G4 zero stratum:** every V1-predicted-zero dataset (V2 rows'
   `predicted_zero_v1`) observes Δ exactly 0 under r's S-selected actions —
   a real falsifier, since S-selection can differ from V3's at r ≠ 0.50.
4. **Sensitivity (Jeffreys):** headline Δ̂ sign flips reported per ratio;
   appends `__SENSITIVITY_BREAK`, non-vetoing.

## Terminals (frozen at registration)

- `LAW_V4_RATIO_INVARIANT[__SENSITIVITY_BREAK]` (exit 0): structural passes
  AND G1+G2+G4 pass at BOTH 0.25 and 0.75.
- `LAW_V4_RATIO_PARTIAL_<failed gates@ratios>` (exit 1) otherwise.
- `V4_INCOMPLETE_NO_VERDICT` (exit 3) if any ratio scores ≠ 16 datasets.

## Registered diagnostics (non-vetoing, always reported)

- **D1 z-balance per ratio:** two-sided sign test on z-residual signs
  (nonzero-sd datasets), p ≥ 0.05 read as "no one-sided optimism reappeared".
- **D4 width ordering:** among datasets with σ̂ > 0 at all three ratios,
  count those with σ̂(0.25) ≥ σ̂(0.50) ≥ σ̂(0.75); registered expectation ≥
  2/3 of that stratum (Beta-Binomial 1/√n_E scaling).
- **D5 separator dose-response:** openml-6332 inside80 status and
  E-occupied R-fibre count at each ratio — the support-drift read of V3's
  D3 (E-support shrinks with e_frac; persistent/worsening miss as E shrinks
  attributes the separator to support drift, not selection).

## Monitoring

- Coverage inside-count at 0.50 must equal V3's 12/16 (asserted; implied by
  R4a exactness).
- Per-ratio confident-set sizes reported (V3 had 4).

## Discipline

One pass, `timeout 3600`, RUN log at the registration SHA. No gate,
threshold, cohort, or model constant changes after registration. An aborted
or crashed pass is retained as a receipt (suffix `_aborted`) and never
silently retried without an amendment naming the defect. Frozen Tier-B
package, V1/V2/V3 and N4-* artifacts untouched; additive only. V3's verdict
is not re-litigated — this study tests a different (untested) prediction of
the same calibrated law.
