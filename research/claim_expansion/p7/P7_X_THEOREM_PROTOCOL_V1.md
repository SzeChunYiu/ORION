# P7-X theorem protocol V1

Date: 2026-08-19
Parent: #534
Status: `THEOREMS_FROZEN_BEFORE_FINITE_ENUMERATION`

## Donor subtraction
P7-X does not claim novelty for search/planning, route stopping, world/task completion versus terminal reporting, abstraction/refinement, bisimulation/sound abstraction, replanning, representation mapping/lenses, world-model revision, workflow migration, or generic closure-gap terminology.

Fresh pressure strengthens that subtraction: VIGIL independently scores world completion versus terminal commitment; current sound-abstraction work preserves/refines planning and goals under bisimulation/refinement mappings; bidirectional/lens work owns representation consistency and round-trip laws; current open-world agent work owns generic closure-gap/misclosure language.

## Bounded transformation embeddings
1. `RETRIEVAL_ROUTE_CHANGE`
2. `PLANNING_ABSTRACTION_REFINEMENT`
3. `SEMANTIC_REPRESENTATION_MAPPING`
4. `WORLD_MODEL_MEASUREMENT_UPDATE`

These are semantic contract embeddings, not claims to implement every donor system.

## State coordinates
Donor-visible transformation state:
- `transform_valid`
- `information_preserved`
- `goal_preserved`
- `local_route_stopped`

Scientific closure coordinates:
- `closure_obligations_transported`
- `objective_same`
- `ambiguity_resolved`
- `no_unresolved_material_route`

`DonorPreserved_D(s)` iff `transform_valid AND information_preserved AND goal_preserved`.

`ScientificTaskClosed_D(s)` iff donor preservation holds AND all four scientific closure coordinates are true.

Local route stop is a separate judgment and never enters donor preservation or scientific task closure by itself.

## Frozen theorem family
### T1 — information/evidence/goal preservation does not reflect closure
If one scientific closure coordinate is non-inert, there exist states with identical donor-visible transformation state and equal donor-preservation verdicts but different scientific task-closure verdicts.

### T2 — local/global stopping separation
`local_route_stopped=true` does not imply scientific task closure. In particular, a material unresolved route can coexist with local stop and otherwise valid/preserved state.

### T3 — complete closure transport sufficiency
If donor preservation holds and all four closure coordinates are true, task closure transports/persists under the bounded contract.

### T4 — ambiguous/incomplete transport fails closed
If `ambiguity_resolved=false`, scientific task closure is false even when information and goal are preserved. The authorized terminal is `REOPEN_OR_CANNOT_CHECK`, not forced task closure.

### T5 — objective-change non-transport
If `objective_same=false`, old task closure does not automatically transport even when state/evidence/goal are otherwise preserved.

### T6 — ideal-product equivalence
A donor product carrying the exact P7-X closure coordinates and closure predicate is extensionally equivalent. No inherent expressivity or centralization advantage is permitted.

## Finite-model obligations
Enumerate every Boolean state for each of the four transformation embeddings (256 states per embedding; 1,024 evaluations total). Require:
- T1 witness for each of the four closure coordinates in every embedding;
- T2 witness with local stop + unresolved material route for every embedding;
- T3 exact sufficiency on every state with donor preservation and all closure coordinates true;
- T4 ambiguity countermodels;
- T5 objective-change countermodels;
- T6 zero ideal-product mismatches;
- no-alarm clean transport cases.

## Claim ladder
A1: explicit scientific closure-obligation transport layer over donor navigation/representation mechanisms.
A2: bounded principle that information/evidence/goal preservation is weaker than scientific closure preservation.
A3: common closure-transport semantics across the four bounded transformation embeddings.

No deployed-agent superiority, universal closure ontology, or claim that every donor abstraction/mapping loses closure is authorized.
