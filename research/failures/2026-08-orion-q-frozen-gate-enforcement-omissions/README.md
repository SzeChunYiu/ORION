# ORION-Q MAX — frozen hostile/scientific gate enforcement omissions

## Observed

Hostile review found two independent fail-open enforcement defects in the MAX branch:

1. `max_r4b_tare_split_majorization.py` implemented only random strictly-positive exhaustive cases, while the already-frozen R4B protocol also required zeros, equal/repeated magnitudes, one-dominant cases, coefficient-identity remints, and a rule that brute force must never beat the sorted split before theorem promotion. The script emitted the positive theorem terminal unconditionally.
2. `.github/workflows/orion-q-max-r4d.yml` checked only that an `ORIONQ_MAX_R4D_RESULT=` line existed. It did not require the receipt's frozen `r4d_protocol_pass` field to be `true`.

## Failure

Neither defect changes the frozen scientific thresholds or comparators. They are enforcement omissions: a future counterexample/failing confirmation could have been reported while CI or the terminal still looked positive.

## Failure class

`FROZEN_GATE_ENFORCEMENT -> REQUIRED_HOSTILE_CASES_NOT_EXECUTED`

and

`FROZEN_GATE_ENFORCEMENT -> RECEIPT_PRESENCE_CONFUSED_WITH_SCIENTIFIC_PASS`

## Correct response

- execute every hostile coefficient family named by the frozen R4B protocol;
- condition the positive R4B terminal on zero hostile/random brute-force violations and exit nonzero otherwise;
- parse the R4D JSON receipt in CI and fail unless `r4d_protocol_pass is true`;
- retain all existing R4B/R4D scientific thresholds unchanged;
- replay the unchanged experiments after these enforcement repairs.

## Authority

`GATE_ENFORCEMENT_ERRATUM_ONLY__NO_R6_OR_NOVELTY_AUTHORITY`
