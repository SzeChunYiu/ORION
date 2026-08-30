# ORION-08 on OpenML-CC18 — the theorem transfers, the method does not

**Terminal:** `THEOREM_PREDICTS_REAL_TRANSFER` (E2 leg only).

Two findings, and the second is adverse.

## 1. The exact statement holds on real decision families

Theorem 2 says refinement decreases regret **strictly, exactly when** it splits an
action-impure fibre. On five CC18 datasets, with the prediction computed from the
training split before any evaluation score:

| dataset | predicted | observed (in-sample) | holds |
|---|---|---|---|
| credit-g | strict decrease | strict decrease | ✅ |
| diabetes | strict decrease | strict decrease | ✅ |
| spambase | strict decrease | strict decrease | ✅ |
| wdbc | strict decrease | strict decrease | ✅ |
| **qsar-biodeg** | **no decrease** | **none, delta exactly 0.000** | ✅ |

**0 contradictions**, and both strata populated, which the protocol required in
advance precisely so a one-sided result could not pass as confirmation.
`qsar-biodeg` is the load-bearing case: it is the one where the criterion said
"no value", and a refinement that helped anyway would have refuted the "exactly
when". It did not help, by exactly zero.

## 2. The typed binding is not a good method out of sample

Fraction of the oracle-achievable gap captured on held-out data, where the typed
binding competes against a generic mutual-information refinement and a
gradient-boosted proxy:

| dataset | typed | infogain | proxy |
|---|---|---|---|
| credit-g | −0.033 | +0.000 | −0.040 |
| diabetes | **−0.183** | +0.000 | −0.029 |
| spambase | +0.214 | **+0.472** | **+0.875** |
| qsar-biodeg | +0.000 | +0.183 | **+0.489** |
| wdbc | **−0.273** | **+0.432** | **+0.773** |

The typed binding is **negative on three of five** and is beaten by the generic
info-gain refinement on three and by the proxy on three. On `wdbc` it captures
−0.273 of the gap while a standard heuristic captures +0.432.

These are not in tension. Theorem 2 is a statement about the distribution the
fibres are defined on, and it is exactly right there. Out of sample a refinement
has more fibres and fewer rows in each, so it pays estimation error the theorem
never claimed to govern. **Being exactly true is not the same as being useful**,
and the arms that could expose the difference were in the protocol from the start
for this reason.

## Two design errors, corrected before this was reported

Both were caught by the results looking wrong, and both would have produced a
false headline.

**Scoring the theorem out of sample.** The first run measured `observed strict
decrease` on held-out data and reported `credit-g` as contradicting Theorem 2.
That was a measurement error, not a refutation: the theorem is about the
empirical distribution the fibres are defined on. Scored in-sample, `credit-g`
agrees. Had the first design been reported it would have claimed a refutation of
an exact theorem on the strength of overfitting.

**A mass threshold on the prediction but not the measurement.** The purity test
initially skipped fibres with fewer than 10 rows while the regret measurement
counted every row, so small impure fibres could produce a decrease the predictor
had never looked at. That manufactured a contradiction on `diabetes`. "Positive
mass" on an empirical distribution means at least one row; with the threshold at
1, `diabetes` agrees. The prediction and the measurement now cover the same
fibres.

## Scope

E2 leg only. This says nothing about E3 Defects4J, which the successor also names
and which remains unrun. ORION-08's terminal stays
`INTERNAL_REVIEW_PASS__EXACT_SYNTHETIC_MECHANISM_CLAIM`: the mechanism claim now
has real-domain predictive support on one leg, and the practical superiority
claim that would justify more has evidence pointing the other way.
