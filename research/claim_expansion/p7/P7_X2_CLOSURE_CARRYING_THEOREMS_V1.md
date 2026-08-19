# P7-X2 closure-carrying navigation theorem family V1

Date: 2026-08-19
Parent: #534
Status: FROZEN_BEFORE_ENUMERATION

## Registered donor transform families
1. `PLANNING_REFINEMENT`
2. `CEGAR_REFINEMENT`
3. `BIDIRECTIONAL_MIGRATION`
4. `WORLD_MODEL_REPLAN`
5. `TERMINAL_COMMITMENT`

Each donor transform has its own native preservation/validity predicate. P7 does not alter that predicate.

## Registered scientific closure coordinates
The bounded theorem instance transports five task-global closure coordinates:

1. `obligations_total` — every target scientific obligation has a mapped source/discharge or an explicit target-new obligation;
2. `obligations_unambiguous` — the transport does not force one of several admissible incompatible obligation mappings;
3. `frontier_resolved` — no material route/source/world frontier relevant to the target closure remains silently unbound;
4. `objective_semantics_preserved` — the task/question/objective meaning used to define closure is preserved or explicitly replaced with new closure obligations;
5. `closure_epoch_current` — the closure certificate is current for the transformed evidence/model/representation state.

These five fields are a registered formal instance, not a universal minimal ontology.

## Closure lift
For donor transform `T` with native-validity predicate `DonorPreserves(T)` and closure carrier `o`, define:

`ClosureCarries(T,o) := DonorPreserves(T) AND all(o)`.

## Frozen theorem obligations

### T1 — donor conservativity
Adding the closure carrier never changes the donor-native preservation/refinement/round-trip/commitment verdict.

### T2 — closure-lifting separation
For each donor transform family and each non-inert closure coordinate, there are two transforms with the same valid donor-visible behavior but different scientific-closure inheritance when only that coordinate differs.

### T3 — closure-product non-laundering
Even when planning preservation, CEGAR validation, round-trip consistency, replanning validity and terminal commitment all succeed, task-global scientific closure does not follow if any load-bearing closure coordinate remains false without an explicit bridge.

### T4 — exact closure refinement
If a transform fails because a nonempty set `S` of closure coordinates is unresolved/incorrect while donor preservation remains valid, repairing every member of `S` restores closure carrying; repairing any proper subset of `S` does not.

This formalizes a closure-level analogue of CEGAR: refine the exact closure defect rather than discard a valid donor transform.

### T5 — compositional closure transport
Two closure-carrying transforms `T1:A->B` and `T2:B->C` compose to a closure-carrying transform only when the target obligation contract produced by `T1` is exactly the source obligation contract consumed by `T2` (or a registered bridge witnesses their equivalence). Donor-visible composability alone is insufficient.

### T6 — ideal donor-product equivalence
A donor stack with the exact same closure coordinates, bridge rules and composition predicate is extensionally equivalent to P7. No inherent centralization advantage is claimed.

## Falsifiers
- If a donor transform already contains the exact scientific closure contract and transport rule, that embedding belongs on the equivalence side.
- If a closure coordinate is inert in a claimed domain, remove it from that domain-specific theorem instance.
- Absence of a closure witness alone does not prove target ambiguity; it yields `CANNOT_CHECK/REOPEN` unless incompatible admissible completions are established.

## Intended widening
The goal is a positive architecture theorem: **scientific closure can be carried across heterogeneous navigation mechanisms by composing mature donor preservation/refinement machinery with explicit obligation transport and targeted closure refinement.**
