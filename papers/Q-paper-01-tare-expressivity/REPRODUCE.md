# Q1 — reproducing the claim spine

The manuscript is receipt-first. A reviewer should verify the strongest claims in this order.

## 1. All-n support-two theorem

Run the generator/verifier associated with:

- `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`
- its frozen protocol under `development/orion-q-max-r0/`.

The required terminal is the machine-checked all-`n` support-two result for the frozen R6M unit support-count objective. The theorem is the source of `C_DP = C_D++`; finite benchmark agreement is only a consistency check.

## 2. Refutation ladder

Replay, without changing any frozen family definition:

- R6N — Tag-anchor splitting;
- R6O/R6P — central frame-for-Tag borrow and support-two closure;
- QG-5/QG-5b — out-of-support phantom borrow and theorem-backed exact forecaster;
- QG-7 — weight-two-Tag plus phantom-borrow hybrid;
- QG-7b — `B''` closure on 10,481 verified instances;
- QG-7c — classification proof chain with the pinned `comm-s2` sector left lemma-open.

A valid replay must preserve the counterexamples. A later family repair may cover a witness, but it must not erase the earlier refutation.

## 3. Chemistry/prospective rows

Verify H4 and equilibrium-N2 rows from the R6M/R6O/R6P receipts. Verify the Benzene prospective staging from `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`; the prediction digest must precede the exact referee computation.

## 4. Applied grounding

Reproduce the R4B coefficient-majorization checks and the blob-locked R4D H2O compiler result. These support only their stated cost coordinates.

## Integrity rules

- never substitute `CANNOT_CHECK` with failure or success;
- do not re-run the protected stretched-N2 subject;
- chemistry `D++` values obtained by exact containment pinch must not be described as a direct high-`n` sweep;
- timing fields are not correctness evidence;
- a closed-form classifier failure does not contradict the R6S support-two theorem.

The exact commands are the generating scripts named beside each receipt. The submission snapshot should add a checksum list over the cited receipt/protocol files.