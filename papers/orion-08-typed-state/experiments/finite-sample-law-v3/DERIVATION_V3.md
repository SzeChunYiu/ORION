# DERIVATION V3 — selection-corrected distributional law (ORION-08 successor)

Companion: `PROTOCOL_V3.md` (committed before any V3 outcome). Parent:
`../finite-sample-law-v2/` (terminal `LAW_V2_PARTIAL_G1_G2`).

## Mechanism being modeled

V2 attributed its one-sided optimism to the **winner's curse of fibre-action
selection**: each fibre action is argmax over the *same* train counts the
posterior conditions on. A conjugate posterior corrects sampling noise, not
selection — E[argmax posterior value] > argmax true value, with the bias
concentrated in the direction of the selected action, hence every interval
miss was LOW (11/13 negative z, sign p = 0.0112).

V3 removes the coupling by construction: **actions are selected on a disjoint
half S of the training rows; the posterior conditions only on the other half
E.** Under the model (rows iid), E-counts are independent of S-selected
actions, so the predictive is an *unconditional* posterior for the utility of
a fixed policy — the standard setting where conjugate posteriors are calibrated.
If V2's attribution is right, V3's intervals must cover; if V3 still misses
low, the attribution was incomplete and something else (e.g. fibre-support
drift) drives the optimism.

## Estimator

1. Identical outer split to V2 (`test_size=0.5`, `stratify`, seed 20260830)
   — the test sets are byte-identical; the per-dataset `oracle_utility` must
   reproduce V2's exactly (registered cross-check R3a).
2. Train rows are split once more into selection half **S** and estimation
   half **E** (`test_size=0.5`, `stratify`, same seed).
3. **All label-dependent selections move to S:** the infogain column
   (`mutual_info_classif` on S) and every arm's fibre actions
   (argmax over S counts per fibre of the coarse / typed / infogain
   partitions). Edges are label-free S-quantiles (same 3 bins).
4. **Posterior from E only:** on the common refinement R (union of typed and
   infogain columns) occupied by E rows, `p_s ~ Beta(k_s+1, n_s−k_s+1)`
   (uniform-prior conjugate; Jeffreys sensitivity as in V2), `q̂_s` = E-fibre
   mass, `N ~ Multinomial(n_te, q̂)`, `K_s | N_s ~ Binomial(N_s, p_s)`, all
   arms scored on the same draw.
5. **Scale convention (registered):** Û(a) = (1/n_te)·Σ_s a_s(2K_s−N_s) —
   per-test-row utility, directly the scale of the observed arm utilities
   (Σ U / n_te). V2 divided by n_tr; the two coincide in V2 only because
   n_te = n_tr there. The closed form becomes exactly
   **E[Δ] = Σ_s q̂_s(a_t−a_c)(2(k_s+1)/(n_s+2)−1)** (no n_te/n factor), and
   the registered R3b cross-check is |MC mean − closed form| < 3·MC-SE.
6. Observed Δ: S-selected actions applied to test rows binned with S-edges;
   arm codes unseen in S score action 0 (same fallback as V2).

## What is deliberately NOT modeled

Unseen-fibre test mass (V2's secondary mechanism; 6332 at 0.256): the
predictive still allocates all test mass to E-occupied fibres. openml-6332 is
therefore the registered mechanism separator — if it misses low again under
V3, support drift dominates it; if not, selection did. Reported either way.

## Registered predictions (diagnostics, non-vetoing)

- **D1 (z-balance):** among nonzero-sd datasets, the sign of z = (obs−mean)/σ̂
  is balanced: two-sided sign test p ≥ 0.05.
- **D2 (optimism removal):** per-dataset predictive mean under V3 ≤ V2's on a
  majority of the 13 datasets nonzero in both (registered threshold ≥ 8/13).
- **D3 (separator):** openml-6332's interval status under V3, read as above.

## Gates

- **G1 confident set** (unchanged): every dataset with |Δ̂| > 2σ̂ has
  sign(Δ̂) = sign(observed Δ).
- **G2 calibration** (unchanged rule, achieved n): two-sided exact binomial
  vs p = 0.8 at α = 0.05 on the pooled cohort (16 if the registry exhausts as
  in A1).
- **G4 zero stratum, selection-robust:** every dataset with V1 Δ̂ = 0
  (dhat_v1, full-train criterion) observes Δ = 0 under V3's S-selected
  actions. This is no longer structural — S-selection could differ — so it is
  a real falsifier of the claim that the zero stratum is selection-stable.
- **Sensitivity:** Jeffreys flips no headline sign (reported as break).

Terminals: `LAW_V3_CALIBRATED[__SENSITIVITY_BREAK]` (exit 0) /
`LAW_V3_PARTIAL_<failed>` (exit 1) / `V3_INCOMPLETE_NO_VERDICT` or
`V3_INCOMPLETE_REPRODUCTION_FAILED` (exit 3).

New named constants: MC seed 20260903 (V2's draws/chunk retained: 10,000 /
2,000). Everything else frozen from V1/V2.
