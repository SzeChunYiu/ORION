# P1-X Protocol V1 Amendment 003 — terminal determinism, responsibility coverage, exact scale

Date: 2026-08-19  
Parent: #529 / PR #540  
Protected cases generated before this amendment: **NO**  
Protected outcomes accessed before this amendment: **NO**

## Trigger

Hostile review found three pre-outcome specification defects:

1. `REQUEST_DISCRIMINATOR` and `UNRESOLVED` were not operationally distinguished, empty-candidate behavior did not map to the frozen terminal enum, and unique narrow repair did not explicitly map to `REPAIR_LOCAL`.
2. The development generator's `MODEL_EXPERIMENT_DESIGN` family collapsed measurement and representation responsibility and therefore did not exercise the four responsibility families required by the protocol.
3. The protocol checker accepted any integer factorization with product 400 rather than freezing the declared `5 x 8 x 10` protected design.

## Repair

- The protocol now defines a deterministic terminal function.
- Candidate-visible `discriminator_status` is frozen as `NOT_NEEDED / AVAILABLE / UNAVAILABLE`.
- Incomparable minima map to `REQUEST_DISCRIMINATOR` only when an in-budget discriminator is available; otherwise they map to `UNRESOLVED`.
- Unique admitted non-high-level revisions map to `REPAIR_LOCAL`; unique admitted high-level revisions map to `REVISE_HIGH_LEVEL`; insufficient-evidence empty sets map to `CANNOT_CHECK`; no-anomaly cases map to `NO_CHANGE`.
- The model/experiment development family now includes `PARAMETER_REVISION`, `EXPERIMENT_MEASUREMENT_REVISION`, `MODEL_CLASS_EXPANSION`, and `REPRESENTATION_REGIME_REVISION` as distinct responsibilities.
- The validator now requires protected scale exactly `(5, 8, 10, 400)`.
- Hostile tests cover all three repairs.

## Unchanged scientific commitments

This amendment does **not** change:

- five domain families;
- eight archetypes;
- 200-development / 400-protected counts;
- B1/B2/B3/P1-X arm identities;
- ESRD definition;
- `+0.10` primary practical margin;
- non-regression margins;
- ideal-product equivalence boundary;
- result or novelty authority (`CANNOT_CHECK`).

Terminal: `PRE_OUTCOME_PROTOCOL_REPAIR__NO_RESULT_AUTHORITY`.
