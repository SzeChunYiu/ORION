# ORION-08 selection-corrected law — findings V3

**Terminal: `LAW_V3_CALIBRATED`** (exit 0). Every registered gate passes;
both mechanism diagnostics hold. Protocol `PROTOCOL_V3.md` + amendment A1-V3
(pre-outcome crash fix: apply the registered unseen-fibre fallback in the
R-lift) committed before this outcome. One clean pass, 16-dataset pooled V2
cohort, 10k-draw MC (seed 20260903).

## The law that survives

**When the fibre action map is selected on training rows disjoint from the
posterior's conditioning set, the Beta-Binomial posterior-predictive of
held-out refinement utility is calibrated.**

| gate | outcome |
|---|---|
| R3a test-set reproduction | exact (max \|diff\| = 0.0, 16 datasets) |
| R3b MC vs closed form | clean (max 4.2e-04 ≈ MC-SE) |
| G1 confident set | **4/4 correct** (spambase +, 1489 +, 40983 +, 40994 −) |
| G2 calibration | **12/16 inside 80% CI** (expected 12.8; exact binomial p = 0.54) |
| G4 zero stratum | **selection-robust 3/3** → 12/12 cumulative across V1–V3 |
| Jeffreys sensitivity | no headline sign flips |

## Per-dataset (uniform prior; Δ = typed − coarse, per-test-row scale)

| dataset | mean | sd | P(Δ<0) | conf | obs |
|---|---|---|---|---|---|
| credit-g | −0.0217 | 0.0214 | 0.837 | no | − |
| diabetes | −0.0142 | 0.0275 | 0.678 | no | − |
| spambase | +0.0987 | 0.0177 | 0.000 | **yes** | + |
| qsar-biodeg | 0 | 0 | — | — | 0 |
| wdbc | +0.0001 | 0.0084 | 0.408 | no | − |
| openml-1485 | −0.0155 | 0.0237 | 0.742 | no | + |
| openml-1486 | +0.0018 | 0.0011 | 0.048 | no | + |
| openml-1487 | 0 | 0 | — | — | 0 |
| openml-1489 | +0.0570 | 0.0145 | 0.000 | **yes** | + |
| openml-1590 | +0.0018 | 0.0025 | 0.235 | no | − |
| openml-4134 | +0.0280 | 0.0169 | 0.046 | no | + |
| openml-6332 | −0.0267 | 0.0480 | 0.701 | no | − |
| openml-23517 | −0.0009 | 0.0042 | 0.587 | no | + |
| openml-40701 | 0 | 0 | — | — | 0 |
| openml-40983 | +0.0126 | 0.0046 | 0.003 | **yes** | + |
| openml-40994 | −0.0750 | 0.0348 | 0.982 | **yes** | − |

## The mechanism exhibit

Six V2→V3 mean sign flips, **every one + → −**, and four of them land on the
observed sign (credit-g, diabetes, 6332, 40994 — including V2's sole G1
violation 6332 and V2's worst calibrated dataset 40994). This is the
selection correction operating, not interval widening:

- **D1 (z-balance): 7/13 negative residuals, sign test p = 1.0** — V2's
  11/13 one-sided optimism (p = 0.0112) is *gone*. Width alone could not do
  this.
- **D2 (optimism removed): 11/13 datasets have mean_V3 ≤ mean_V2** —
  registered threshold ≥ 8.
- **D3 (separator): openml-6332 still misses its 80% interval** (now from a
  correctly-signed, unconfident predictive). The registered reading: for the
  cohort's most fragmented table (unseen-fibre mass 0.256), support drift
  dominates selection — consistent with V2's attribution that both
  mechanisms act, selection necessary for the pattern, unseen mass the
  amplifier at the extremes.

## Honest cost accounting

Selection correction is not free: with actions from half the train data the
predictive widens and the confident set shrinks (4 here vs 5 in V2 — but
V2's fifth member, 6332, was its one wrong call). 12/16 coverage under wider
intervals is the expected 12.8 exactly; the evidence that calibration was
*restored* rather than *masked* is D1's sign balance plus the six downward
flips.

## Arc (successor ledger)

V1 mean-sign law REFUTED (credit-g; prior-robust) → V2 distributional law
REFUTED (`LAW_V2_PARTIAL_G1_G2`; one-sided optimism attributed to
winner's-curse selection + unseen-fibre mass) → **V3 selection-corrected law
CALIBRATED** — the attributed mechanism, removed by construction, converts
the refutation into a positive law. Zero stratum 12/12 cumulative. Frozen
Tier-B package untouched; all three studies additive under
`experiments/finite-sample-law-{v1,v2,v3}/`.

## Phase D2 — Defects4J

Still `D4J_SKIPPED_DATA_UNAVAILABLE` (host lacks the data; laptop-billy
offline). Not checked is not passed; carried forward.
