# ORION-02 — the frontier is not fundamental; it is a selector problem

**Protocol identity:** `ORION02.SELECTOR_LIMITED_CERTIFICATION.v1`
**Status:** `DIAGNOSTIC_ON_COMMITTED_DATA` · `scientific_authority_delta = NONE`
**Supersedes the reading in:** `VALIDITY_UTILITY_FRONTIER_V1.md`

No new run. Every number below is recomputed from the committed R24 held-out records in
`rounds/r24-arm-conditional-fibres-revival/failed-executions/3550275/run_a.result.json`.

**Extraction validated first:** recomputing from `folds[*].test[primary_arm]` reproduces
the committed `violations_strict = 20` and `violations_tau = 11` exactly. The analysis
below runs on the same 44 held-out decisions.

## 1. The registered gate is arithmetically infeasible

With `tau = 0.02` and registered gate `alpha = 0.10`, on the realised held-out excess:

- `P(excess > tau) = 11/44 = 0.25`
- split-conformal bound required for validity at `alpha = 0.10` is **0.061381 = 3.07x tau**

| alpha | required bound | vs tau |
|---|---|---|
| 0.30 | 0.017178 | 0.86x — useful |
| 0.25 | 0.031508 | 1.58x |
| 0.20 | 0.034720 | 1.74x |
| 0.15 | 0.057887 | 2.89x |
| **0.10** | **0.061381** | **3.07x** |
| 0.05 | 0.065566 | 3.28x |

Because a quarter of held-out instances exceed `tau`, **any** bound at or below `tau`
must violate on at least 25 %, and **any** bound valid at 10 % must be about three times
`tau`. This is a property of the realised excess distribution, not of the certificate
construction — so it is not repaired by a different certificate. It generalises the
`tau`-ceiling finding from "this construction fails" to "no construction satisfies both
requirements at these parameters on this corpus."

## 2. But an interior point does exist

Abstain on the 25 % of instances with the highest realised excess and certify the rest:

| abstain | retained | violations at tau | conformal bound at alpha=0.10 | |
|---|---|---|---|---|
| 20 % | 35 | 2 | 0.017333 | 0.87x tau |
| **25 %** | **33** | **0** | **0.016837** | **0.84x tau** |
| 30 % | 31 | 0 | 0.014220 | 0.71x tau |

At 25 % abstention the certificate is **valid and useful simultaneously** — zero
violations with a bound below `tau`. The frontier in
`VALIDITY_UTILITY_FRONTIER_V1.md` is therefore **not fundamental**. A feasible operating
point exists; four rounds simply never reached it.

## 3. Why the rounds never reached it

That table is an **oracle**: it abstains using realised excess, which is unavailable at
decision time. Repeating it with the quantity actually available — the model's own
predicted `bound` — does not work at all:

| abstain | retained | violation rate at tau | conformal bound at alpha=0.10 |
|---|---|---|---|
| 0 % | 44 | 0.250 | 0.061381 |
| 20 % | 35 | 0.286 | 0.061532 |
| 25 % | 33 | 0.303 | 0.061532 |
| 50 % | 22 | 0.364 | 0.061532 |

Abstaining makes the retained violation rate **worse**, and the bound does not move.

The reason is measurable:

```
corr(model_bound, realised_excess) = -0.1442
permutation two-sided p = 0.3528  (20,000 shuffles)
Spearman rho            = -0.1921
```

**The model's predicted bound carries no usable signal about realised excess.** It is
not anti-informative — at n = 44 the correlation is not distinguishable from zero. It is
simply uninformative, and every abstention rule built on it is therefore a random
subset.

**This is the binding constraint, and no round ever measured it.** R18, R22, R23 and R24
all measured certificate validity while the quantity that determines whether validity is
attainable — selector quality — went unmeasured.

## 4. What the successor must hit

Degrading the oracle selector with Gaussian noise gives the requirement directly:

| selector corr with realised excess | retained | violations at tau | bound at alpha=0.10 |
|---|---|---|---|
| 1.000 | 33 | 0 | 0.84x tau |
| 0.980 | 33 | 0 | 0.84x tau |
| 0.924 | 33 | 1 | 0.84x tau |
| 0.845 | 33 | 2 | 0.86x tau |
| 0.759 | 33 | 3 | **1.67x tau** — no longer useful |

The certificate stays valid and useful down to a selector correlation of roughly **0.85**,
and degrades sharply below it. Current selector: **-0.14**.

So the target is a number, not an adjective: **build a predictor of realised excess with
correlation of about 0.85 or better, then apply split-conformal to the retained 75 %.**

## 5. The model this replaces

| | old | new |
|---|---|---|
| certificate | max over eligibility-gated pool | split-conformal over the retained set |
| eligibility | `excess <= tau + TOL` (forces `bound <= tau`) | none — the gate caused the ceiling |
| coverage | certify everything | selective, with explicit abstention |
| measured quantity | certificate validity | **selector correlation with realised excess** |
| success target | `violations <= 0.10` at `bound <= tau` | `corr >= ~0.85`; validity then follows |

`ORION02.SELECTIVE_FIBRE_RISK.v1` already preregisters disjoint train/calibration/test
custody and an explicit abstain floor, which is the right shape. This adds the **primary
endpoint** it should carry: selector correlation, with 0.85 as the preregistered target
and -0.14 as the current baseline to beat.

## 6. Limits

- n = 44, one corpus (PMLB), one committed classifier assignment. The 0.85 threshold is
  a simulation on this excess distribution, not a general constant.
- The oracle row is an **upper bound on any selector**, not an achievable guarantee. It
  shows a feasible point exists; it does not show a learnable rule reaches it.
- `corr = -0.14` at p = 0.35 means "no evidence of signal", not "proven zero signal". A
  larger corpus could reveal weak signal.
- Split-conformal validity assumes exchangeability of calibration and test excesses.
  These come from disjoint fold roles, which supports but does not prove it.
- Nothing here rehabilitates the R22-R24 terminals. They remain
  `CERTIFICATE_INVALID`. What changes is the diagnosis of why, and what to measure next.
