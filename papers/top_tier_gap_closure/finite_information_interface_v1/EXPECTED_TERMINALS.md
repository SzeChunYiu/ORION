# Expected terminals — finite-information interface V1

## Green

`FINITE_INFORMATION_INTERFACE_V1_THEOREMS_REPRODUCED`

Emitted only after every registered exact-enumeration class passes, the recomputed counters match `RESULT.json`, and zero mismatches are observed.

## Red

`FINITE_INFORMATION_INTERFACE_V1_COUNTEREXAMPLE_OR_IMPLEMENTATION_DRIFT`

Emitted on the first theorem mismatch, malformed result, counter drift, or failed protocol invariant.

## Interpretation

Green means that an independent bounded brute-force implementation failed to falsify the closed-form finite theorem spine on the registered universe. The unrestricted result rests on the proofs in `THEORY.md`. Green does not establish novelty, practical importance, external transfer, or any paper promotion.