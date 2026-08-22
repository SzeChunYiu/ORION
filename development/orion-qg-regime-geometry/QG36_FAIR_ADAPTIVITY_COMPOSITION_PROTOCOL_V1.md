# ORION-QG QG-36 — fair fixed-vs-adaptive post-summary composition

Date: 2026-08-22
Issue: SzeChunYiu/ORION#933
Earned adaptive parent: QG-34 #924.
Prospective fixed parent: QG-35 #932.

## Status

**PROSPECTIVE EXECUTABLE COMPOSITION FREEZE. FROZEN BEFORE ANY ACCEPTED QG-35 RESULT.**

QG-36 performs no compiler-state search. It may read only immutable committed parent receipts from QG-34 and QG-35.

The comparison gives both policy classes identical side information: the exact initial joint bulk+spectrum summary class is known before any indexed probe is selected.

## Frozen parent binding

QG-34 must provide:
- terminal `QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED`;
- `both_accept=true`;
- `EXACT_ADAPTIVE_MINIMAX_AUTHORITY=true`;
- 92 exact `class_depths` values in the canonical QG-32 joint-class order;
- `worst_case_depth = max(class_depths)`;
- QG-32 parent file hash.

QG-35 must provide:
- terminal `QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED`;
- `both_accept=true`;
- `EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY=true`;
- 92 exact `class_minima` values in the same canonical QG-32 joint-class order;
- `worst_case_class_conditioned_fixed_minimum = max(class_minima)`;
- the same QG-32 parent file hash.

Class-order binding is fail-closed by identical QG-32 parent hash, identical universe `(715 orbits, 384 probes, 92 joint classes)`, and the explicit receipt statement that both arrays use QG-32 generic `make_groups` canonical order. QG-36 does not re-open raw compiler states.

## Frozen decision table

Let `D_i` be QG-34 class depth and `F_i` QG-35 class-conditioned fixed minimum.

Mandatory invariant:
`D_i <= F_i` for every `i=0..91`.

If any `D_i > F_i`:
`QG36_PARENT_INCONSISTENCY__ADAPTIVE_WORSE_THAN_OPTIMAL_FIXED`.
No scientific promotion is allowed.

Let `D_* = max_i D_i` and `F_* = max_i F_i`.

If either parent is not exact/bound:
`QG36_CANNOT_CHECK`.

If `D_* == F_*`:
`QG36_NO_STRICT_POSTSUMMARY_ADAPTIVITY_ADVANTAGE__EXACT_TIE`.

If `D_* < F_*`:
`QG36_TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT`.

The logically impossible branch `D_*>F_*` is covered by the pointwise inconsistency rule and must fail closed.

No `F_*` value is predicted in this protocol.

## Production composition

Read only the two committed parent JSON receipts. Recompute:
- parent authority checks;
- array lengths/ranges;
- maxima from arrays;
- pointwise inequality count and first violation if any;
- strict/tie decision from the frozen table;
- indices where `D_i < F_i`, `D_i == F_i`, and any invalid `D_i > F_i`.

## Independent generic verification

Independently re-read the two immutable receipts and recompute all 92 comparisons using a separate implementation/order. Require exact agreement with the production composition object.

## Native ORION-Q authority

Only the strict terminal may set:
`TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT=true`.

The tie terminal must set it false while still authorizing the exact equality of worst-case observation counts.

The inconsistency or cannot-check terminal sets all comparison authority false.

## Hard boundaries

Always false:
- compiler optimization-cost advantage;
- hardware/measurement minimum;
- full finite-n identification optimum;
- generic adaptive-testing novelty;
- autonomous skill-selection authority;
- physical quantum advantage.

## Workflow

Before QG-35 target receipt exists, CI performs freeze-only checks and exits successfully without adjudication.
After only the immutable QG-35 receipt is bound, the unchanged workflow executes production/generic/native composition, deterministic replay, and a self-consistent parent-array/max tamper rejection.