# ORION-02 — prospective finite-fibre certifiability on OpenML-CC18

**Committed before any dataset is fetched.**

## Identity, and what this is not

This is a **new prospective identity**. It is **not** a revival attempt on the
FiberGuard empirical programme and **does not consume a slot** in
`ORION02_REVIVAL_ATTEMPT_LEDGER_V1.jsonl`. The two counted adverse attempts —
`R23` (`C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE`) and `R24`
(`C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`) — stand exactly as recorded, and
nothing here rescues, reopens or reinterprets them. Their corpora (PMLB, ASlib,
CSP-MZN) are not touched.

#1701 asks for a prospective test of the theorem across heterogeneous real
datasets using E2 OpenML-CC18. That is what this is.

## The theorem being tested

ORION-02's finite-fibre result concerns **certifiability**: a representation
partitions instances into fibres, and a certificate issued per fibre is *valid*
when the truth falls inside it at the guaranteed rate. Refining a representation
can only help when a fibre's certificate is doing work the finer one would not.

Operationally, for a representation `R` and calibration split:

- the certificate for a fibre is the set of labels observed in that fibre on
  calibration data;
- **coverage** is the fraction of held-out instances whose true label lies in
  their fibre's certificate;
- **width** is the mean certificate size, in labels — a certificate naming every
  label is valid and useless, so coverage without width means nothing;
- a fibre unseen in calibration falls back to the full label set, and those
  fallbacks are counted and reported rather than hidden.

## Datasets and strata, frozen before outcomes

Task IDs are frozen here, chosen from OpenML-CC18 **by metadata alone** — number
of classes and number of features — and not by any accuracy or coverage number.
Four application/task strata:

| stratum | criterion | frozen dataset ids |
|---|---|---|
| `binary_small` | 2 classes, < 25 features | 31, 37, 44 |
| `binary_wide` | 2 classes, >= 25 features | 1462, 1471, 1494 |
| `multiclass_small` | > 2 classes, < 25 features | 11, 54, 187 |
| `multiclass_wide` | > 2 classes, >= 25 features | 14, 16, 18 |

Split: 50/50 calibration/held-out, seed `20260830`, stratified by label.

## Bindings and arms

- `coarse` — every instance in one fibre. The certificate is the whole calibration
  label set.
- `theorem_minimal` — the theorem's own criterion: refine only where a fibre's
  calibration labels are not constant. Implemented as an equal-frequency binning of
  the single feature with the highest mutual information with the label, into
  `K = 4` bins, computed on calibration data alone.
- `distance_proxy` — 4 fibres from k-means on standardised features, using no label
  information. The natural cheap substitute.
- `learned` — 4 leaves of a depth-2 decision tree fitted on calibration data.
- `oracle` — one fibre per true label. Coverage 1.0 at width 1 by construction, and
  unavailable in practice; it bounds what any representation could achieve.

`K = 4` throughout so the arms are compared at equal fibre budget. A method that
wins by having more fibres has not won.

## Endpoints

**Primary: certifiability under a valid bound.** The predeclared gate is
**coverage >= 0.90** on held-out data. An arm that misses it is invalid regardless
of width, and its width is not reported as an achievement.

Secondary: mean certificate width, predictive loss (0/1 error of the fibre's
majority label), and acquisition cost (fibres used, features touched).

## Required contrast

At least one stratum must be **theorem-predicted tie/no-value** — where
`theorem_minimal` does not improve on `coarse` — and at least one must be
predicted value. Otherwise the terminal is `CANNOT_CHECK_NO_CONTRAST`. Prediction
is computed from calibration data alone, before held-out coverage is measured.

## Terminals

- `CERTIFIABILITY_DISCRIMINATOR_SUPPORTED` — the bound holds for
  `theorem_minimal` on every stratum, its width is no worse than `distance_proxy`,
  and the predicted tie/value split matches what is observed.
- `CERTIFIABILITY_DISCRIMINATOR_NOT_SUPPORTED` — any of those fails. **Failure is
  terminal**, as #1701 requires: it is recorded with the stratum and not rescued by
  re-binning, re-splitting or changing `K`.
- `CANNOT_CHECK_NO_CONTRAST` / `CANNOT_CHECK_DATA_UNAVAILABLE`.

A pass supports the theorem on fresh heterogeneous data. It does not revive R23 or
R24 and does not make FiberGuard's certificate valid; that record is closed and
adverse.
