# ORION-Q N2-F5 — Held-out prospective crossover prediction (frozen protocol)

Date frozen: 2026-08-21 (before any outcome artifact exists)
Parent programme: #633; lane issue: #675 (successor family 5); immutable prior negative: #671
Branch: `claude/orion-harness-verification-b17qdj`
Status: **PROTOCOL FREEZE BEFORE OUTCOMES.** Runner: `research/extensions/orion-q/nlanes/n2_f5_crossover_prediction.py`. Gates prespecified; reported honestly whatever they yield.

## Registered design being executed (from #675, authoritative text)

> **Held-out crossover prediction:** freeze parameter/operator families and predict regime switches prospectively.

## Exact-synthetic world (frozen)

True (hidden) route cost models, constants frozen here before any fit or outcome:

- `C_S(L, lam, d) = c1 * L * lam * d + c2 * L`, with `c1 = 1.0`, `c2 = 25.0`.
- `C_R(L, lam, d) = c3 * (lam*d)^2 * (1 + c4/d)`, with `c3 = 0.35`, `c4 = 6.0`.

Winner = argmin. `SEED = 20260821` (used only for tie-free jitter-free bookkeeping; grids are deterministic).

- **Training regimes** (196 points, exact cost observations for both routes): `L in {8,12,16,24,32,48,64} x lam in {1.0,1.5,2.2,3.3} x d in {4,6,8,12,16,24,32}`.
- **PRIMARY held-out** (96 points, labels hidden until scoring, disjoint extrapolative grid): `L in {80,120,160,240,320,480} x lam in {1.2,1.8,2.7,4.0} x d in {48,64,96,128}`.
- **H1 far extrapolation** (18 points): `L in {640,1280,2560} x lam in {1.5,3.0} x d in {192,384,768}`.
- **H2 broken-form world** (hostile, 96 points, same grid as PRIMARY): held-out truth gains an extra term on route R only, `C_R += c5 * L * log2(d) * sqrt(lam)`, `c5 = 15.0`. Training observations remain unbroken; every frozen predictor is applied unchanged. This world exists to verify the frozen predictor's authority does **not** extend across a functional-form shift.

> **Amendment A1 (2026-08-21, after first run):** the originally frozen `c5 = 0.8` was a defective hostile control — it flipped exactly 1 of 96 H2 labels, and that single point fell inside the mechanism's `UNCERTAIN` band, so the "broken world" left every confident prediction intact (first-run F5-G5 false, first-run terminal `N2_F5_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED`; first-run PRIMARY numbers: ORION 0.9948, best baseline 0.9271 — G2 already passing). A1 raises `c5` to 15.0 (flips 54/96 labels), making H2 an actual regime shift. Training, PRIMARY, H1, the mechanism, baselines, scoring and all gate thresholds are unchanged; G2 is computed on PRIMARY and is untouched by `c5`.

All predictors are fit on training only, then frozen before touching any held-out point (prospective discipline enforced by program structure: fit function is called once, before held-out grids are generated).

## Candidate ORION mechanism

Mechanism-derived analytic crossover predictor: least-squares fit (numpy lstsq) of `C_S` on frozen feature library `[L*lam*d, L]` and `C_R` on `[(lam*d)^2, (lam*d)^2/d]` from training observations; predict `argmin` of fitted costs; typed `UNCERTAIN` answer when relative fitted margin `|C_S - C_R| / max(C_S, C_R) < eta = 0.02`.

## Strongest non-ORION baselines (first right of refusal)

- `B1_nearest_neighbor`: 1-NN in `(log L, log lam, log d)`, predicts nearest training point's observed winner.
- `B2_training_majority`: constant prediction of the training-majority route.
- `B3_linear_classifier`: least-squares linear separator on `[1, log L, log lam, log d]` against labels `+-1`, predicts by sign. (The stripped two-route proxy of #671 is exactly linear in logs, so this is the strongest closed-form parent.)
- `ORACLE`: true model (true broken model on H2); accuracy 1.0 by construction; upper bound.

Scoring (frozen): per point — correct 1.0, wrong 0.0, `UNCERTAIN` 0.5 regardless of truth. Confident-only accuracy also reported (informational).

## Prespecified gates

| Gate | Statement | Threshold |
|---|---|---|
| F5-G1 | Determinism: pipeline twice in-process, canonical JSON identical | exact equality |
| F5-G2 | Residual: ORION PRIMARY score `>=` every baseline's PRIMARY score `+ 0.02` | absolute margin 0.02 |
| F5-G3 | Crossover location: frozen probe path `L=128, lam=2.0`, bisect `d* in [4,1024]` where `C_S = C_R` for true and fitted models; relative error | `<= 0.02` |
| F5-G4 | Oracle bound: no arm score exceeds oracle score on any world | `<= oracle + 1e-12` |
| F5-G5 | Hostile bite: ORION score on H2 `<=` ORION PRIMARY score `- 0.01` (the broken-form world must actually degrade the frozen predictor; if it fails to bite, the hostile control failed and the run is not promotable) | 0.01 |

Terminal vocabulary: `N2_F5_CROSSOVER_PREDICTION_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY`; `N2_F5_CROSSOVER_PREDICTION_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY` (honest negative, valid); `N2_F5_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED` (any of G1, G3, G4, G5 fails).

## Determinism and receipt rules

Stdlib + numpy only; fixed seed; one stdout receipt line `ORIONQ_N2_F5_CROSSOVER_PREDICTION=<canonical sorted json>`; pretty results to `research/extensions/orion-q/nlanes/N2_F5_CROSSOVER_PREDICTION_RESULTS.json`; exit 0 regardless of gates.

## Claim boundary

Exact-synthetic scope only. The cost surfaces are frozen synthetic proxies in the lineage of #671's stripped two-route model, not measured QSVT implementations. A positive residual says only that, within this frozen world family, the analytic-form predictor extrapolates regime switches where the frozen baselines do not; H2 explicitly bounds that authority at functional-form shifts. No `LOWER_BOUND` claim; no real-hardware or novelty claim (Predict-and-Conquer-style selection is donor-owned per #675).
