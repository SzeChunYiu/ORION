# ORION-10 — reproducing the forecast/certificate chain

## 1. Baseline closed-form forecaster and prospective evidence

Replay `QG5_CERTIFIED_FORECAST_RESULTS.json` and `QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`. Preserve the QG-5 fresh-panel counterexample exactly: one `n=3` row has `C_DP=10` while the frozen three-family formula predicts 11. QG-3's 102/102 staged confirmations remain valid finite/prospective evidence but do not override this later counterexample.

## 2. Theorem-backed repair

Replay `QG5B_EXACT_FORECASTER_RESULTS.json`. Verify:

- `F2(t)=C_Dxx(t)` is computed over the full frozen support-`<=2` family without an unrestricted DP call;
- R6S is the certificate basis for `C_DP=C_Dxx` for every `n` under the unit objective;
- F2 has zero error on the 9,547 compared instances;
- the original QG-5 refuting instance is now cost 10 under F2;
- enlarged borrow `B'` classifies that instance as borrow and closes the finite QG-5b panels.

## 3. Explanation stress test

Replay QG-7 without changing `B'`. The hostile H-panel must reproduce 64 rows with `C_Dxx < min(C_Dplus,f_Bprime)`, all gap -1, including the weight-two-Tag plus phantom-borrow hybrid. Confirm `C_DP=C_Dxx` still holds on the same rows.

Then replay QG-7b and QG-7c. QG-7b's `B''` covers the verified hybrid corpus; QG-7c leaves the pinned `comm-s2` proof sector open. These lanes update the explanation certificate, not F2 cost exactness.

## 4. Chemistry/library status

Rows with committed exact-referee receipts may be labeled verified. Rows without a committed referee remain predictions with verification authority `NONE`. High-`n` chemistry F2 values obtained by an exact containment pinch must not be described as direct exhaustive `D++` sweeps.

## Integrity rule

A compact explanation failure is not an F2 cost failure. Conversely, theorem-backed cost exactness does not authorize an exact regime label unless the explanation/classification certificate independently closes.