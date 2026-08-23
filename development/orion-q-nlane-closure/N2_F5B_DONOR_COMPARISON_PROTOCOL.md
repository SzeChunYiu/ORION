# ORION-Q N2-F5B — donor comparison for the F5 crossover-prediction residual (frozen protocol)

Date frozen: 2026-08-21 (before any F5B outcome artifact exists)
Parent programme: #633; lane issue: #675 (carried-forward F5 residual); immutable prior negative: #671
Prior artifacts (read-only inputs, not edited): `N2_F5_PROTOCOL.md`, `N2_STOP_RULE_ASSESSMENT.md`, `research/extensions/orion-q/nlanes/n2_f5_crossover_prediction.py`, `.../N2_F5_CROSSOVER_PREDICTION_RESULTS.json`
Branch: `claude/orion-harness-verification-b17qdj`
Status: **PROTOCOL FREEZE BEFORE OUTCOMES.** Runner: `research/extensions/orion-q/nlanes/n2_f5b_donor_comparison.py`. Gates prespecified; reported honestly whatever they yield.

## Purpose (from the stop-rule assessment, authoritative text)

The F5 residual (`N2_F5_CROSSOVER_PREDICTION_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY`) may not claim
standing value until a **Predict-and-Conquer-style model-selection donor** gets first right of refusal:
fit a library of parametric cost models per route, select by held-out score, predict the crossover from
the fitted forms. The assessment further flags that the original F5 world is **partly well-specified**
(the candidate's frozen feature library contains the true forms), so this protocol adds a
**misspecified world** (true forms NOT in the candidate's feature library and NOT in the donor's model
library) evaluated for candidate and donor alike, plus the functional-form-shift hostile control (H2)
carried over unchanged from F5.

## Worlds (frozen)

### World ORIG — exact reuse of F5 (imported, not re-derived)

Everything is imported from `n2_f5_crossover_prediction.py` (which is not edited): true cost models
`C_S = 1.0*L*lam*d + 25.0*L`, `C_R = 0.35*(lam*d)^2*(1 + 6.0/d)`; `SEED = 20260821`; TRAIN (196 pts),
PRIMARY held-out (96 pts), H1 far-extrapolation (18 pts, informational), and H2 broken-form hostile
world (PRIMARY grid, `C_R += 15.0*L*log2(d)*sqrt(lam)` per F5 Amendment A1, training unbroken, all
predictors frozen pre-H2).

### World MIS — misspecified world (new, frozen here)

True (hidden) route costs, constants frozen now:

- `C_S_mis(L, lam, d) = a1 * L^0.9 * (lam*d)^1.15 + a2 * L^0.9`, with `a1 = 1.0`, `a2 = 25.0`.
- `C_R_mis(L, lam, d) = a3 * (lam*d)^2.1 * (1 + a4 / d^0.7)`, with `a3 = 0.35`, `a4 = 6.0`.

Same TRAIN / PRIMARY grids as ORIG (grid values imported from the F5 module). Winner = argmin.
By construction neither route's true form lies in the candidate's frozen feature library nor in the
donor's model library below (non-integer exponents 0.9 / 1.15 / 2.1 / 0.7; both costs are two-term
sums, so the single power law does not contain them either): **both predictors are misspecified here.**

Design-time world check (performed before this freeze, involving NO predictor fit or evaluation, only
true-label counts, recorded for honesty): MIS TRAIN has S=46 / R=150 of 196; MIS PRIMARY has
S=18 / R=78 of 96. Both regimes are represented on both grids, so the world can actually discriminate
predictors — the same defect class that forced F5 Amendment A1 is excluded up front.

MIS has no H1/H2 arms: the misspecification itself is the stressor; H2 (form shift) is gated on ORIG
exactly as in F5.

## Candidate (unchanged from F5)

The F5 mechanism, reused verbatim: least-squares fit of `C_S` on frozen features `[L*lam*d, L]` and
`C_R` on `[(lam*d)^2, (lam*d)^2/d]` from training observations; predict argmin; typed `UNCERTAIN` when
relative margin `< eta = 0.02`. On ORIG the fit function is **imported from the F5 module** (`fit_orion`)
so the ORIG candidate arm is the F5 arm, not a reimplementation. On MIS the identical feature library
and eta are fit against MIS training observations (generic fit path, same lstsq, margin denominator
guarded as `max(|cs|, |cr|)` since fitted costs are no longer guaranteed positive off-library).

## Donor — Predict-and-Conquer-style parametric model selection (first right of refusal)

Frozen model library, per route (each closed-form least squares on training observations only):

| id | form |
|---|---|
| M1_true_s_form | `w1*L*lam*d + w2*L` |
| M2_true_r_form | `w1*(lam*d)^2 + w2*(lam*d)^2/d` |
| M3_affine | `w0 + w1*L + w2*lam + w3*d` |
| M4_bilinear | `w1*L*lam + w2*L*d + w3*lam*d + w4*L` |
| M5_powerlaw | `exp(w0) * L^w1 * lam^w2 * d^w3` (lstsq in log space) |
| M6_quad_mix | `w0 + w1*(lam*d)^2 + w2*L*lam*d + w3*L` |

Selection (frozen): deterministic validation split of TRAIN — in the frozen itertools.product order,
indices `i % 4 == 3` are validation (49 pts), the rest fit (147 pts). Each model is fit on the fit-split,
scored on the validation split by **relative RMSE** `sqrt(mean(((pred-true)/true)^2))`; a model whose
validation score is non-finite is disqualified. Per route, the minimum-score model wins (ties broken by
frozen library order M1..M6), then is **refit on the full 196-point training grid** and frozen. Winner
prediction = argmin of the two fitted route costs, with the **same** typed `UNCERTAIN` band `eta = 0.02`
(guarded margin denominator `max(|cs|, |cr|)`) and the same 1.0 / 0.0 / 0.5 scoring as the candidate.

Information parity: the donor sees exactly what the candidate sees — per-route exact training costs on
the frozen TRAIN grid, nothing held-out. Compute budget: the donor is deliberately allowed MORE fitting
budget (6 closed-form fits + selection per route vs the candidate's 1) — first right of refusal means
the donor is never resource-starved relative to the candidate. All fits happen once, before any
held-out or hostile grid is scored (prospective discipline enforced by program structure, as in F5).

Note the honesty hazard is asymmetric and acknowledged: on ORIG the donor's library contains the true
forms (M1, M2), so the donor is expected to be exact there — **donor absorption on ORIG is the likely
and honest outcome**, not a failure of the harness.

## Arms scored (per world)

`candidate_orion_analytic_typed`, `donor_model_selection`, and (context, imported/refit unchanged)
`b1_nearest_neighbor`, `b3_linear_classifier` from F5 (fit per world on that world's training labels),
plus `oracle` (true winner; true broken model on H2). Baselines are informational only in F5B — the
F5B question is candidate vs donor.

Crossover probes (informational, no gate): frozen probe path `L=128, lam=2.0`, bisect `d* in [4, 4096]`
for the true and each of the candidate's / donor's fitted forms on both worlds; report relative errors
(null if no sign change in range).

## Prespecified gates

| Gate | Statement | Threshold |
|---|---|---|
| F5B-G1 determinism | pipeline twice in-process, canonical JSON identical | exact equality |
| F5B-G2 F5 reproduction | candidate ORIG scores (PRIMARY, H1, H2) equal the values stored in `N2_F5_CROSSOVER_PREDICTION_RESULTS.json` | exact equality (same floats) |
| F5B-G3 donor sufficiency (ORIG) | donor ORIG PRIMARY score `>=` candidate ORIG PRIMARY score `- 1e-9` | tolerance 1e-9 (ties count as sufficient) |
| F5B-G4 misspecified comparison | verdict on MIS PRIMARY: `CANDIDATE_AHEAD` if candidate > donor + 0.02; `DONOR_AHEAD` if donor > candidate + 0.02; else `TIE` | margin 0.02 (same margin as F5-G2) |
| F5B-G5 oracle bound | no arm exceeds oracle on any world | `<= oracle + 1e-12` |
| F5B-G6 hostile bite (both) | candidate H2 `<=` its ORIG PRIMARY `- 0.01` AND donor H2 `<=` its ORIG PRIMARY `- 0.01` (the form-shift world must bite both frozen predictors, else the hostile control failed) | 0.01 each |

Validity set = {G1, G2, G5, G6}. If any validity gate fails, the run is not promotable.

## Terminal vocabulary (exhaustive, prespecified)

- `N2_F5B_CONTROL_FAILED__NOT_PROMOTABLE` — any validity gate (G1/G2/G5/G6) fails.
- `N2_F5B_DONOR_ABSORBED__EXACT_SYNTHETIC_ONLY` — G3 holds (donor sufficient on ORIG) **and** MIS
  verdict is `DONOR_AHEAD` or `TIE`. Disposition: the F5 residual is donor-absorbed and carries **no
  standing value beyond the donor**; the honest and likely outcome.
- `N2_F5B_RESIDUAL_SURVIVES_DONOR__EXACT_SYNTHETIC_ONLY` — G3 fails (candidate strictly ahead on ORIG)
  **and** MIS verdict is `CANDIDATE_AHEAD`.
- `N2_F5B_MIXED__CANDIDATE_AHEAD_ON_MISSPECIFIED_ONLY__EXACT_SYNTHETIC_ONLY` — G3 holds but MIS verdict
  is `CANDIDATE_AHEAD` (the world stated: candidate survives only on MIS).
- `N2_F5B_MIXED__CANDIDATE_AHEAD_ON_ORIGINAL_ONLY__EXACT_SYNTHETIC_ONLY` — G3 fails but MIS verdict is
  `DONOR_AHEAD` or `TIE` (the world stated: candidate survives only on ORIG).

## Determinism and receipt rules

Stdlib + numpy only; `SEED` imported from F5 (bookkeeping only — everything is grid-deterministic);
runner exits 0 regardless of gates; one stdout receipt line
`ORIONQ_N2_F5B_DONOR_COMPARISON=<canonical sorted json>`; pretty results to
`research/extensions/orion-q/nlanes/N2_F5B_DONOR_COMPARISON_RESULTS.json`; double invocation must be
byte-identical.

## Claim boundary

Exact-synthetic scope only: frozen synthetic cost surfaces and frozen grids in the #671 lineage. No
measured-implementation, hardware, novelty, or `LOWER_BOUND` authority. `DONOR_ABSORBED` is a valid,
honest terminal under ORION discipline — it retires the F5 residual's standing-value claim without
retiring F5's internal receipts. Whatever survives on MIS says nothing beyond this frozen world pair.
