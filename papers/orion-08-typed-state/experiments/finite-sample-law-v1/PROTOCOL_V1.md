# PROTOCOL V1 — finite-sample refinement law (ORION-08 successor)

Committed BEFORE any outcome under this protocol is produced. Companion
derivation: `DERIVATION_V1.md` (read first; it defines Û, Δ̂, the shrinkage
lemma, and the general-threshold form).

## Arms and quantities

Reproduce the v1 CC18 setting byte-for-byte in structure: same utility matrix,
same binning (3 quantile bins, train-only edges), same K_COARSE=2 /
K_EXTRA=2, same SPLIT_SEED=20260830, same 50% stratified split, same arms
(`coarse`, `refined_typed`, `infogain_refine`; `proxy_strong` is re-scored for
reference but is OUT of the law's scope — a gradient-boosted predictor is not
fibre-measurable and Û does not apply to it).

New quantity per arm: **Û(Π)** and **Δ̂ = Û(refined) − Û(coarse)**, both
train-only. Sensitivity variant: Jeffreys prior (k+½)/(n+1) — same formulas.

## Phase R — CC18 retrodiction (5 scored v1 datasets)

Datasets: credit-g, diabetes, spambase, qsar-biodeg, wdbc (the v1 scored set;
banknote and blood-transfusion were skipped by the v1 filter and stay out).
Re-derive the fibre tables with the frozen seed and verify reproduction by
cross-checking the scored arms against `RESULTS_V1.json` (max |Δarm| < 1e-9).

**R-gate (pass on all 5):** sign(Δ̂_typed) = sign(recorded held-out typed Δ)
with recorded signs credit-g −, diabetes −, spambase +, qsar-biodeg 0,
wdbc −. Predicted-zero vs observed-zero: agreement; predicted-zero vs
observed-nonzero: DISAGREEMENT, reported as such.

## Phase D — Defects4J retrodiction (conditional on data)

Requires `~/d4j_data.json` (laptop). If absent, emit
`D4J_SKIPPED_DATA_UNAVAILABLE` — never conflate unavailable with checked.
Using the v1 D4J binding and split, compute Û per project and test:

**D-gate:** Δ̂ < 0 on Cli (the genuine unexplained failure) AND Δ̂ > 0 on Gson
(its nearest neighbour on every axis the addendum measured), with the other 10
projects' predicted signs matching `OUT_OF_SAMPLE_V1.json` transfer direction
(Csv expected Δ̂ ≈ 0).

## Phase P — prospective cohort (the registration)

**Selection rule (fixed now, before any outcome):** from OpenML, fetch CC18
member datasets in ascending data_id, EXCLUDING the 7 ids v1 declared
(31, 37, 44, 1462, 1464, 1494, 1510); keep those with exactly 2 classes, ≥ 5
numeric features after dtype filtering, and n ≥ 300; take the **first 12** that
score without error. No other filter, no hand-removal. The thresholds are
structural (v1's feature need is 5; a 50% split needs ≥ 300 rows to populate
fibres), chosen before any outcome.

**Prediction-before-outcome is structural:** Û uses train-half fibre tables
only; the runner computes and logs every prediction before the held-out half
is scored, in one atomic pass with no branching on outcomes.

**P-gate (cohort verdict):**
- `LAW_RETRODICTS_AND_PROSPECTS`: R-gate passes, ≥ 10 of 12 prospective sign
  agreements (ties: predicted-zero vs |observed| < 1e-9 counts agree; vs
  larger observed counts disagree), both predicted strata populated
  (≥ 2 predicted Δ̂ > 0 and ≥ 2 predicted Δ̂ < 0 among the 12), and no
  contradiction of the strong kind (Δ̂ > +0.005 with observed Δ < 0).
- `LAW_RETRODICTS_ONLY`: R-gate passes, prospective below that bar.
- `LAW_FAILS`: R-gate fails (the law is refuted by the already-recorded
  outcomes — report immediately, no prospective rescue).

Secondary (reported, not gating): Spearman rank correlation of Δ̂ vs observed
typed Δ across all scored datasets; Jeffreys sensitivity on every sign claim.

## Discipline

- One script, one pass, stdout log + JSON receipt (schema
  `ORION08.FINITE_SAMPLE_LAW.v1`), SHA256 of protocol+derivation in the
  receipt. Exit codes: 0 retro+prospective pass, 1 retrodiction refuted,
  2 prospective fail, 3 no contrast / data unavailable (distinct states).
- No parameter is fitted at any point. The only constants are the frozen v1
  ones and the uniform/Jeffreys priors named in the derivation.
- Frozen Tier-B surfaces are untouched; this dir is additive. If the law
  passes, the claim ("a rule predicting when transfer succeeds") is earned in
  an additive successor ledger — never by editing CLAIM_LEDGER_V4.md.
