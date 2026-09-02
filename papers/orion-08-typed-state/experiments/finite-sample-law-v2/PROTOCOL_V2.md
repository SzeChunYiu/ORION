# PROTOCOL V2 — distributional finite-sample law (ORION-08 successor)

Committed BEFORE any V2 outcome. Companion: `DERIVATION_V2.md` (model, gates,
falsifiers). V1 result: `finite-sample-law-v1/` (terminal `LAW_FAILS_RETRO`).

## Phases

**R2 (retro, 5 datasets):** credit-g, diabetes, spambase, qsar-biodeg, wdbc,
same frozen seed and setting; MC = 10,000 draws, seed 20260902; report P(Δ<0),
σ̂, 80% interval, P(typed beats infogain); cross-check observed arm utilities
against v1 RESULTS (max |Δarm| < 1e-9) and the MC mean of Δ against the
closed-form mean of the SAME R-fibre predictive,
(n_te/n_tr)·Σ_s q̂_s·(a_t−a_c)·(2(k_s+1)/(n_s+2)−1) (max |diff| < 3·MC-SE).
V1's parent-posterior Δ̂ is reported alongside but is a different functional
(conditional on the finer table vs marginal at the arm's own granularity) and
is NOT gated; it defines the predicted-zero stratum for G4.

**P2 (prospective, fresh 12):** continue V1's pre-registered ascending scan
**past openml-1480** (V1-P consumed through 1480). Same rule — CC18 member ids
ascending, excluding v1's 7 declared ids AND the 12 V1-P scored ids, binary
target, ≥ 5 numeric features, n ≥ 300 — first 12 that score. Predictions
computed and logged (train-only) before held-out scoring, one atomic pass.

**D2 (Defects4J, conditional):** requires `~/d4j_data.json`; else
`D4J_SKIPPED_DATA_UNAVAILABLE`. Computes the V2 quantities at the general
threshold on the V1 D4J binding.

## Gates (registered now)

- **G1 confident-set:** every dataset with |Δ̂| > 2σ̂ (retro + prospective
  pooled) has sign(Δ̂) = sign(observed Δ). One violation = `LAW_V2_FAILS_G1`.
- **G2 calibration:** count of the 17 pooled datasets whose observed Δ falls
  inside its 80% central predictive interval must pass a two-sided exact
  binomial test at α = 0.05 against p = 0.8 (failure = `LAW_V2_FAILS_G2`).
- **G3 D4J discriminator:** among the 12 projects, P(Δ<0) ranks Cli in the
  top 2 AND Gson below the cohort median (failure = `LAW_V2_FAILS_G3`;
  skip if data unavailable — reported, never conflated).
- **G4 zero-stratum:** every predicted-zero dataset's observed Δ (expected 0)
  lies inside its 80% interval.

Terminals: `LAW_V2_RETRO_AND_PROSPECTS` (G1+G2 pass, G3 passes or skipped,
G4 passes) / `LAW_V2_PARTIAL_<failed gates>` / `LAW_V2_FAILS_ALL`. Exit 0 only
on the first. Priors: uniform primary, Jeffreys sensitivity on every gate
(sign flips of any headline quantity under the sensitivity are reported as
`SENSITIVITY_BREAK` even if the primary passes).

## Discipline

One script, one pass, stdout + `RESULTS_V1.json` (schema
`ORION08.FINITE_SAMPLE_LAW.v2`), SHA256s of derivation+protocol in the
receipt. No fitted parameter; the only new constants are MC size (10k) and MC
seed, both named here. Frozen surfaces untouched; additive only. V1's
refutation is not re-litigated.

## Amendment A1 (2026-09-02, after aborted pass 1, BEFORE any verdict)

Pass 1 aborted with `V2_INCOMPLETE_NO_VERDICT` — no gate outcome was consumed.
Two facts it established, registered here before the clean rerun:

1. **MC posterior bug, fixed to the registered model.** The runner coded the
   uniform posterior as Beta(k+1, n−k+2) (mean (k+1)/(n+3)); the registered
   derivation (DERIVATION_V2.md §model) is Beta(k+1, n−k+1) (mean (k+1)/(n+2),
   V1's p̄). The R2 MC-vs-closed-form cross-check caught it (13/16 violations,
   up to ~50 MC-SE); the fix is exactly that one parameter. No gate input or
   threshold changed.
2. **Registry exhaustion.** The ascending scan past openml-1480 yields exactly
   11 qualifying scorers (40927 fails fetch and is 10-class regardless;
   40996/41027 are 10-class). Pooled cohort is structurally 16, not 17.
   G2 therefore runs its exact two-sided binomial test at the ACHIEVED n
   (16); the n=17 literal is replaced by "n = all scored datasets". All other
   gates unchanged.

Pass 1's receipts are retained as `RESULTS_V2_pass1_aborted.json`; the result
of record is the post-A1 single clean pass.
