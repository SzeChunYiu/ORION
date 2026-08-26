# P14D blinded external-validation acquisition protocol v1

This is a frozen acquisition contract, not an external-validation result.
Nothing authored in this repository can satisfy an external-custody field merely
by naming itself independent.

Execution is admissible only after all of the following content-bound artifacts
exist:

1. at least three realistic domain packet sets owned outside the evaluated
   implementation lane;
2. a common resource/budget manifest applied to every workflow;
3. a blinded assignment manifest hiding workflow identity from adjudicators;
4. an adjudicator roster and custody attestation owned outside ORION authorship;
5. a frozen rubric for maximum admissible claim, donor overlap, negative-evidence
   retention, `CANNOT_CHECK`, false promotion and valid discovery;
6. per-packet independent adjudications plus agreement/disagreement records;
7. a protected output register and replay receipt.

The intake validator must reject missing files, empty packet registers,
self-authored custody, unblinded labels, unequal resources, result-bearing
previews and malformed or stale digests.  Until every field passes, the only
admissible terminal is `P14D_EXTERNAL_ACQUISITION_BLOCKED`; P14C remains the
active bounded result.

