# PROTOCOL V3 — selection-corrected distributional law (ORION-08 successor)

Committed BEFORE any V3 outcome. Companions: `DERIVATION_V3.md` (model,
gates, predictions), parent result `../finite-sample-law-v2/RESULTS_V2.json`
(terminal `LAW_V2_PARTIAL_G1_G2`).

## Phases

**R3 (retro 5 + prospective 11, one pooled cohort):** the exact V2 cohort —
5 retro (credit-g, diabetes, spambase, qsar-biodeg, wdbc) + the 11 P2
openml-{1485,1486,1487,1489,1590,4134,6332,23517,40701,40983,40994} (hard-id
list, not a re-scan — the registry scan is settled by A1). One atomic pass:
for each dataset, S/E split, S-selections, E-posterior, 10,000-draw
posterior-predictive MC (seed 20260903, chunk 2,000), held-out scoring.

## Cross-checks (registered, gated)

- **R3a test-set reproduction:** per-dataset `oracle_utility` equals V2's
  exactly (same outer split seed) — max |diff| < 1e-12.
- **R3b MC vs closed form:** |MC mean of Δ − Σ_s q̂_s(a_t−a_c)(2(k_s+1)/(n_s+2)−1)|
  < 3·MC-SE on every dataset.

## Gates

- **G1 confident set:** |Δ̂| > 2σ̂ ⟹ sign(Δ̂) = sign(observed). One violation
  fails.
- **G2 calibration:** #(observed inside its 80% central interval) vs
  two-sided exact binomial, p = 0.8, α = 0.05, at the achieved n (16).
- **G4 zero stratum (selection-robust):** V1-Δ̂-zero datasets observe Δ = 0
  under V3.
- **Sensitivity (Jeffreys):** sign flips of headline Δ̂ reported as
  `SENSITIVITY_BREAK`; non-vetoing.

## Registered diagnostics (non-vetoing, always reported)

- **D1 z-balance:** two-sided sign test on z-residual signs (nonzero-sd
  datasets) must show p ≥ 0.05 for the attribution to hold.
- **D2 optimism removal:** #{datasets: mean_V3 ≤ mean_V2 (uniform, nonzero
  both)} ≥ 8 of 13.
- **D3 separator:** openml-6332 interval status under V3 (support-drift vs
  selection attribution).

## Discipline

One script (`run_finite_sample_law_v3.py`), one pass, stdout + JSON receipt
(schema `ORION08.FINITE_SAMPLE_LAW.v3`) + SHA256SUMS over derivation,
protocol, findings, results, runner. No fitted parameter. New constants:
MC seed 20260903; the /n_te scale convention (V2-equivalent at n_te = n_tr,
see DERIVATION_V3 §5). Frozen Tier-B package and V1/V2 artifacts untouched;
additive only. V2's verdict is not re-litigated — V3 tests a different
law (selection-corrected), registered here before its outcome.
