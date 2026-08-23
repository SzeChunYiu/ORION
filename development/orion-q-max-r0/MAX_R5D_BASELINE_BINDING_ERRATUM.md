# MAX-R5D baseline-binding erratum

Date: 2026-08-20
Branch: `shadow/orion-q-max-r0`
Authority: hostile verification correction; supersedes any interpretation of the first MAX-R5D development log as a scientific pass.

## Observed

The first `max_r5d_n2_controlled_multiwindow_development.py` GitHub Actions run printed:

- B0 R5B outer incumbent: `CNOT=12232`, `T=95318`, `direct=104`;
- reported B1: `CNOT=12683`, `T=98854`, `direct=0`;
- B3: `CNOT=11605`, `T=95454`, `direct=100`;
- reported `r5d_development_pass=true`.

## Failure

The reported B1 was not the absorbed R5C donor-composed baseline. It was pure adjacent pairing evaluated with controlled-cost edge semantics. R5C already chooses the minimum `(Lambda,T,CNOT)` matching inside each four-term coefficient-local quartet and therefore has `direct=104`, `T=95318` before its slack moves.

The R5D T gate was consequently checked against a weaker `T=98854` reference. B3's `T=95454` is 136 larger than the actual absorbed incumbent's `T=95318`.

Therefore the first MAX-R5D development `pass` is invalid and carries no promotion authority.

## Failure class

`DONOR_COMPOSED_BASELINE_BINDING_MISMATCH`

A stronger donor capability was present in the current incumbent but was silently replaced by a weaker local baseline for one non-compensatory coordinate.

## Correct response

- preserve the log as a negative verification event;
- do not claim the 5.1259% CNOT number as an admissible ORION improvement;
- bind every successor coordinate against the actual R5C quartet baseline;
- align enlarged matching windows to complete R5C quartets so baseline pairs are not split across window boundaries;
- re-freeze the enlarged-window protocol before reading the corrected outcome.

## General lesson

For multiobjective donor-composed research, a candidate must bind to a **single jointly realizable incumbent object**. Comparing one coordinate to B0, another to a weaker B1, and another to B2 can fabricate a Pareto improvement that no matched incumbent comparison supports.
