# ORION-08 finite-sample law — findings V1

**Terminal: `LAW_FAILS_RETRO`** (registered R-gate, one contradiction), with
three structural facts that survive the failure and define the successor.
Protocol `PROTOCOL_V1.md` was committed (ea3d47146) before any outcome.

## Phase R — retrodiction against the recorded CC18 outcomes

Arms reproduce `real-transfer-cc18-v1/RESULTS_V1.json` to 0.00e+00 on all 5
datasets, so the disagreement below is the law's, not a rerun artifact.

| dataset | Δ̂ (uniform) | predicted | recorded | agrees | Δ̂ (Jeffreys) |
|---|---|---|---|---|---|
| credit-g | +0.01150 | + | **−** | **no** | +0.01313 |
| diabetes | −0.06669 | − | − | yes | −0.03358 |
| spambase | +0.09457 | + | + | yes | +0.09467 |
| qsar-biodeg | 0.00000 | 0 | 0 | yes | 0.00000 |
| wdbc | −0.00558 | − | − | yes | −0.00161 |

4/5. **credit-g refutes the sign law**: its recorded failure is not small-fibre
shrinkage — the shrinkage-corrected gain stays positive (+0.0115 uniform,
+0.0131 Jeffreys, prior-robust). The miss is prior-robust and belongs to the
predictive *variance*, not the mean.

## Phase P — prospective cohort (rule pre-registered: first 12 CC18 ids
ascending, excluding v1's 7, binary, ≥5 numeric features, n ≥ 300)

12/12 scored (15, 29, 38, 151, 1049, 1050, 1053, 1063, 1067, 1068, 1461,
1480). 10/12 sign agreements; 6 predicted-positive, 6 predicted-zero,
0 predicted-negative; 1 strong contradiction (openml-1049: Δ̂ +0.0055,
observed −0.0069).

### What survives

1. **Predicted-zero is 7/7.** Every dataset the shrinkage law says carries no
   surviving value (qsar-biodeg retro + 38, 1050, 1053, 1067, 1461, 1068
   prospective) observed an exactly-zero refinement delta. The qsar mechanism
   (all value erased by n/(n+2) shrinkage) generalized to six new datasets
   without a miss.
2. **Confident signs are 5/5.** Every |Δ̂| ≥ 0.04 (diabetes −0.067, spambase
   +0.095, 29 +0.084, 151 +0.148, 1480 +0.043) agreed with the observed sign.
3. **All 4 sign misses live in the low-|Δ̂| band** (|Δ̂| ≤ 0.0115, observed
   |Δ| ≤ 0.011). The sign functional is wrong exactly where the held-out draw
   has irreducible noise comparable to the effect: the posterior predictive
   straddles zero, and a single test half is one draw from it.

## Diagnosis (failure attribution, one stage)

The v1 law extracted only the mean of the posterior predictive
(E[Δ] = Δ̂). The refutation is a statement about that functional's sign, not
about the predictive model: no per-fibre shrinkage, under any prior, can put
credit-g's mean negative while its fibres keep MLE-positive value. What the
predictive model DOES contain and v1 did not use is the full distribution of
the held-out Δ (per-fibre Beta-Bernoulli draws on the test half). The successor
tests exactly that, pre-registered: per-dataset P(Δ < 0), a confident-set gate
(|Δ̂| > 2σ̂ must be 100% sign-correct on retro + a fresh 12), and predictive
calibration of the 80% intervals across all scored datasets.

## Phase D — Defects4J

`D4J_SKIPPED_DATA_UNAVAILABLE` — `~/d4j_data.json` lives on the laptop host,
unreachable during this run. Not checked is not passed; the D4J
Cli-vs-Gson discriminating prediction is carried into the successor protocol
unchanged (it is untouched by this failure: Δ̂_D4J uses the same per-fibre
formula at the general threshold).

## Amendments

- One typo (`rows, scored = [], [], True`) crashed the first prospective pass
  after phase R printed; no outcome had been emitted and no gate input
  changed. Fixed and rerun from scratch; both receipts (stdout log above,
  `RESULTS_V1.json`) come from the fixed single pass.
- Arm-winner agreement (secondary, 8/12) is reported and not gated, as
  registered.

## What this licenses

Nothing in the frozen Tier-B package changes. The successor ledger may record:
the mean-sign form of the finite-sample law is REFUTED on the recorded
outcomes (credit-g, prior-robust); the zero-stratum prediction is 7/7; the
magnitude-sign structure is 5/5 above |Δ̂| ≥ 0.04 with all misses below
0.0115. The distributional successor is registered before its own outcomes in
`finite-sample-law-v2/` (new directory, same discipline).
