# ORION-Q MAX-R4E-B0 — prospective held-out QG-32 action forecast protocol

Date: 2026-08-22
Issue: #914
Parent skill result: MAX-R4E-A #908 / committed authority-indexed router result
Held-out target: QG-32 #911
Execution branch: `codex/orion-q-max-r4eb0-heldout-qg32-20260822`
Status: **FROZEN BEFORE ANY ACCEPTED QG-32 RESULT RECEIPT EXISTS.**

## Purpose

Test whether the QG-derived ORION-Q authority-indexed research-control skill transfers prospectively to a new TARE query whose protected numerical outcome is hidden at forecast time.

This is a T1 same-domain transfer test only.

## Frozen forecast object

The forecast is **action-class only**. It contains no numerical prediction for:
- joint class count;
- unresolved pair count;
- minimum probe cardinality;
- selected probe indices;
- solver result.

Forecast actions:

1. `DO_NOT_USE_BULK45_ALONE`
2. `DO_NOT_USE_SPECTRUM54_ALONE`
3. `DO_NOT_TREAT_JOINT_BULK_SPECTRUM_AS_ALREADY_SUFFICIENT`
4. `LOCALIZE_VERIFICATION_TO_UNRESOLVED_JOINT_CLASSES`
5. `ACQUIRE_INDEXED_PROBES_ONLY_FOR_REMAINING_PAIR_SEPARATION`
6. If exact minimum cardinality is independently verified, authorize only `JOINT_SUMMARY_PLUS_MINIMUM_FIXED_PROBES -> INDEXED_LOCAL_RESPONSE_IDENTITY`.
7. If only a certified separating upper bound is verified, authorize only that upper-bound route and retain richer indexed state as fallback.
8. Preserve all QG-32 stronger authority negatives.

## Post-outcome inputs

The adjudicator may read only:
- the immutable MAX-R4E-A committed result receipt;
- this frozen protocol;
- the immutable committed QG-32 result receipt after QG-32 closes its own production/generic/native/replay/tamper harness;
- QG-32's own native/generic authority flags as copied into that receipt.

The adjudicator must not infer authority from PR prose, workflow success alone, or a production-only result.

## Decision map

### BORNE_OUT_EXACT_MINIMUM
Requires all:
- QG-32 parent/production/generic/native all accept;
- a separating fixed probe set exists;
- exact minimum cardinality is independently closed (`no_smaller=true` or equivalent committed authority);
- the target authority is only indexed local-response identity above joint summaries;
- all stronger QG-32 claims remain false.

### BORNE_OUT_UPPER_BOUND_ONLY
Requires:
- QG-32 has a verified separating set;
- exact minimum is not independently closed;
- QG-32 correctly withholds minimum authority;
- stronger claims remain false.

### REFUTED_JOINT_ALREADY_SUFFICIENT
Only if the committed QG-32 result says no probes are needed above joint summaries. Because QG-31 already contains a same-bulk+same-spectrum+different-indexed witness, this outcome also requires parent-binding review and cannot be treated as ordinary scientific refutation.

### REFUTED_PROBE_LOCALIZATION_INVALID
Only if QG-32's exact semantics show that restricting separation constraints to pairs inside the same joint class does not preserve the target indexed-identity query.

Otherwise `CANNOT_CHECK`.

## Positive transfer terminal

`MAX_R4EB0_QG_DERIVED_AUTHORITY_SKILL_TRANSFERS_PROSPECTIVELY_TO_HELD_OUT_TARE_QUERY`

requires either `BORNE_OUT_EXACT_MINIMUM` or `BORNE_OUT_UPPER_BOUND_ONLY`, plus:
- forecast contains no numerical target guess;
- false-authority count = 0;
- hidden-outcome dependency count = 0;
- information-layer action correct;
- all stronger authority remains false.

## Metrics

Report:
- adjudication class;
- exact/upper-bound branch;
- false-authority count;
- hidden-outcome dependency count;
- forecast-number-present flag (must be false);
- whether unresolved-pair localization is validated;
- if a certified probe set is smaller than 384: `indexed_probe_coordinates_avoided = 384 - |P|`, explicitly scoped to the fixed indexed-response query after joint summaries;
- if no smaller certified set exists, report zero avoided coordinates rather than negative value.

## Hard authority boundary

Even positive keeps false:
- `MAX_R4E_QG_SKILLS_COMPILER_GENERAL`
- `MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE`
- `MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER`
- `AUTONOMOUS_SKILL_SELECTION_AUTHORITY`
- `GENERAL_QUANTUM_SCIENCE_IMPROVEMENT`
- novelty / physical quantum advantage.

The next positive rung must use a materially different compiler family whose target outcome is frozen after this forecast.