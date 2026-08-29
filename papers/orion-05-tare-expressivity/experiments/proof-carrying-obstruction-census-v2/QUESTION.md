# ORION-05 proof-carrying obstruction census V2 — new instrument identity

Identity: `ORION05.PROOF_CARRYING_OBSTRUCTION_CENSUS.v2`.

The V1 5,005-instance census is preserved as `CANNOT_CHECK__CHECKER_DISAGREEMENT`: runner and independent checker disagree on all three planted controls, so agreement on the unlabelled census rows cannot grade the basis. This V2 does not reinterpret or repair those outcomes.

The new question is whether the prospectively frozen obstruction basis can be decided by **proof-carrying per-instance certificates** whose validity is checked independently of both the V1 runner and its V1 grading predicates.

Every positive membership/gap decision must carry an explicit witness/certificate; every negative decision that contributes to a universal basis theorem must carry either a checkable exhaustive residual certificate or a proof-producing solver certificate. Solver exit status or runner classification alone has no authority.
