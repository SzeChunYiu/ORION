# ORION-Q MAX-R6 native post-interface method-language gate

Date: 2026-08-20
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: frozen before interface-envelope outcome generation.
Authority ceiling: native responsibility/revision attribution only; not R6.

## Purpose

Native N0 selected donor closure. Native N1 is frozen to select `REV:CHANGE_INTERFACE` if its registered donor-closure observations identify interface responsibility. MAX_R6_INTERFACE_CLOSURE_PROTOCOL then tests an optimistic FOQCS lower envelope.

This packet freezes the next native discriminator **before** that interface outcome is generated. It prevents the operator from deciding after seeing the result whether method-language growth should be allowed.

## Candidate visibility

The native state and harness must not contain or import:

- ADT3;
- an anchored/dependent TARE construction;
- `R2=R0R1` as a candidate relation;
- R5J outcomes;
- any operator-authored auxiliary-frame recommendation;
- stretched-N2 coefficient contents.

## Registered observations

Native N2 may receive only these semantic observations, after their evidence exists:

- `R5H_CURRENT_ALPHABET_EXACT` in `{YES,NO}`;
- `GENERAL_M_DONOR_OUTCOME` in `{NONDOMINATING_OR_CLOSED,DOMINATES_OR_INCONCLUSIVE}`;
- `FOQCS_INTERFACE_ENVELOPE` in `{OPTIMISTIC_BOUND_REGISTERED,UNRESOLVED}`;
- `FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR` in `{YES,NO,UNRESOLVED}`;
- `CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4` in `{NONE_OVER_DIRECT_CLIQUE_DONOR,NONZERO,UNRESOLVED}`.

No implementation-level quantum candidate is a discriminator.

## Frozen responsibility hypotheses

### `RESP:CURRENT_SEARCH_INCOMPLETE`

Predicts `R5H_CURRENT_ALPHABET_EXACT = NO`.

### `RESP:DONOR_CLOSURE_INCOMPLETE`

Predicts at least one of:

- `GENERAL_M_DONOR_OUTCOME = DOMINATES_OR_INCONCLUSIVE`;
- `FOQCS_INTERFACE_ENVELOPE = UNRESOLVED`.

### `RESP:INTERFACE_INADEQUATE`

Predicts:

- current search exact;
- general-m donor nondominating/closed;
- FOQCS optimistic envelope registered;
- `FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR = YES` or `UNRESOLVED`.

This hypothesis survives whenever an interface-only route could still deliver a strict non-compensatory successor.

### `RESP:METHOD_LANGUAGE_INADEQUATE`

Predicts all of:

- `R5H_CURRENT_ALPHABET_EXACT = YES`;
- `GENERAL_M_DONOR_OUTCOME = NONDOMINATING_OR_CLOSED`;
- `FOQCS_INTERFACE_ENVELOPE = OPTIMISTIC_BOUND_REGISTERED`;
- `FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR = NO`;
- `CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4 = NONE_OVER_DIRECT_CLIQUE_DONOR`.

Interpretation: search, known donors, and an unrealistically favourable interface have been absorbed/closed for strict all-coordinate superiority, while the current registered method language contributes no H4 point beyond the donor-composed incumbent.

## Responsibility -> revision binding

Use the same generic mechanics as N0/N1:

- `RESP:CURRENT_SEARCH_INCOMPLETE` -> `REV:SEARCH_CURRENT_ALPHABET`;
- `RESP:DONOR_CLOSURE_INCOMPLETE` -> `REV:ABSORB_DONOR`;
- `RESP:INTERFACE_INADEQUATE` -> `REV:CHANGE_INTERFACE`;
- `RESP:METHOD_LANGUAGE_INADEQUATE` -> `REV:GROW_METHOD_LANGUAGE`.

## Expected fail-closed behavior

- Missing interface-envelope evidence keeps responsibility unresolved.
- A dominating or unresolved optimistic interface blocks method-language growth.
- Only the full registered method-language observation pattern may identify `RESP:METHOD_LANGUAGE_INADEQUATE`.
- The production revision gate must select `REV:GROW_METHOD_LANGUAGE`; the P9/no-P10 shadow receives the same evidence but has no such revision mechanic and therefore cannot select it.

## Consequence of a native method-language selection

A `REV:GROW_METHOD_LANGUAGE` output does not authorize a quantum construction. It only permits a separately frozen isolated optimizer to expand a generic quantum representation grammar.

That optimizer must be candidate-blind. It may operate over generic algebraic objects such as block partitions, Pauli/symplectic auxiliary variables, control labels, correction/restore variables and resource coordinates, but its grammar/protocol may not name or encode an operator-authored target construction.

## Fresh R6 subject

The stretched-N2 public discriminator remains unopened until:

1. native N2 is executed;
2. if language growth is selected, the generic optimizer protocol is frozen and its output generated without candidate leakage;
3. donor comparison and R6 gates are frozen.
