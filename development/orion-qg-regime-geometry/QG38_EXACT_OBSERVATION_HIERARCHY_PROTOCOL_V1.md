# QG-38 Exact Observation-Cost Hierarchy Protocol v1

Issue: SzeChunYiu/ORION#942

## Scope

This lane performs a receipt-only composition of already-earned exact ORION-QG authorities under one shared indexed local-response semantics. It does not rerun or alter QG-34, QG-35, QG-36, or QG-32c science.

The three quantities are deliberately different decision models:

- `D_star`: worst-case number of probes when the joint bulk+spectrum summary class is known and the next probe may adapt to earlier probe outcomes.
- `F_star`: worst-case minimum size of a nonadaptive probe set when the joint bulk+spectrum summary class is known and the set may be chosen separately for that class.
- `U_star`: minimum size of one nonadaptive probe set selected universally, before knowing which of the 92 summary classes / 715 indexed identities is present, with the same summary information available at evaluation.

The scientific question is whether the exact parent authorities imply a strict hierarchy `D_star < F_star < U_star`.

## Parent requirements

QG-38 may issue an exact terminal only when all of the following are true:

1. The QG-36 fair-comparison parent has `both_accept=true`, `EXACT_FAIR_FIXED_VS_ADAPTIVE_COMPARISON_AUTHORITY=true`, zero pointwise adaptive>fixed violations, and exact integer `D_star`, `F_star`.
2. The QG-32c independent MITM replication has `both_accept=true`, `MINIMUM_FIXED_PROBE_CARDINALITY_AUTHORITY=true`, `EXISTS_SEPARATOR_AT_MOST_4=false`, and exact integer `MINIMUM_FIXED_PROBE_CARDINALITY`.
3. The QG-36 and QG-32c parents bind the identical QG-32 semantic parent SHA-256.
4. Both parents bind the same universe: 715 indexed local-Clifford orbit identities, 384 indexed probes, 92 joint bulk+spectrum summary classes.
5. Parent receipts and projections are provenance-bound to their successful workflow run / artifact IDs and self-digest valid where a result digest is present.
6. All quantities are nonnegative integers and their semantic labels match this protocol.

Any failure is `QG38_CANNOT_CHECK_PARENT_OR_SEMANTIC_BINDING`.

## Frozen decision table

After parent validation, let `(D,F,U)=(D_star,F_star,U_star)`.

- If `D < F < U`: `QG38_EXACT_STRICT_OBSERVATION_COST_HIERARCHY_MACHINE_CHECKED`.
- Else if `D == F == U`: `QG38_EXACT_THREE_WAY_TIE_MACHINE_CHECKED`.
- Else if `D <= F <= U`: `QG38_EXACT_NONSTRICT_MONOTONE_HIERARCHY_MACHINE_CHECKED`.
- Else: `QG38_PARENT_INCONSISTENCY_OR_NONMONOTONE_MODEL_ORDERING`.

The terminal is determined mechanically. The numeric ordering was known before this receipt-composition protocol and therefore earns no prospective/blinded novelty credit.

## Derived quantities allowed

For an exact terminal the lane may report:

- `adaptive_to_conditioned_fixed_gap = F-D`;
- `conditioned_fixed_to_universal_fixed_gap = U-F`;
- `adaptive_to_universal_gap = U-D`;
- exact rational ratios `F/D`, `U/F`, `U/D` when denominators are nonzero;
- the QG-36 count of summary classes with strict adaptive improvement.

These are observation-complexity statements only.

## Required independent checks

A generic receipt verifier and a native responsibility verifier must independently:

- recompute the expected terminal from parent values;
- verify the shared QG-32 parent hash and 715/384/92 universe;
- verify all reported gaps/ratios;
- enforce the semantic labels of `D`, `F`, `U`;
- reject a self-consistent tamper to either parent value, parent hash, or universe;
- agree on the exact terminal before `both_accept=true`.

The composed artifact must replay byte-identically from the same parent projections.

## Hard claim ceiling

All of these fields MUST remain false:

- `HARDWARE_MEASUREMENT_MINIMUM`
- `MINIMUM_FULL_FINITE_OPTIMUM_PROBES`
- `COMPILER_OPTIMIZATION_COST_ADVANTAGE`
- `COMPILER_RUNTIME_ADVANTAGE`
- `GENERIC_ACTIVE_LEARNING_NOVELTY`
- `AUTONOMOUS_SKILL_SELECTION_AUTHORITY`
- `physical_quantum_advantage_claim`
- `novelty_authority`

QG-38 is not a hardware lower bound, not a compiler-runtime benchmark, and not a general theorem about arbitrary adaptive testing.
