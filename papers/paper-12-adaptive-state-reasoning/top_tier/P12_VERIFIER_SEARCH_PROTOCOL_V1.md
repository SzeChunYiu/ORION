# P12 verifier-backed resource-location protocol V1

**Programme:** #977  
**State:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** replicate resource-location metareasoning in an exact verifier-backed formal search setting.

## Task

Solve frozen Boolean CNF satisfiability instances. A candidate solution is accepted only if an independent clause verifier confirms every clause. `UNSAT` is accepted only after exhaustive search of the residual variable space or propagation derives contradiction.

The task family is defined in `sat_resource_location_cases_v1.json`; the runner may not add/remove formulas after execution begins.

## Shared work unit

Both state construction and downstream reasoning are charged in the same primitive unit: **one literal truth evaluation** inside a clause.

Metadata reads such as clause length/unit-clause count are reported separately and cannot consume hidden truth values.

Every policy has a hard budget of `2000` literal evaluations per instance. Exceeding the budget returns `BUDGET_EXHAUSTED`, not partial credit.

## State-construction action

`PROPAGATE` performs deterministic unit propagation to fixed point:

- scan clauses under the current partial assignment;
- detect satisfied clauses, contradictions and unit literals;
- assign forced unit literals;
- repeat until fixed point or contradiction;
- charge every literal evaluation.

The resulting partial assignment/residual formula is the compiled state. Propagation never reads the hidden satisfying assignment; it uses only clause semantics.

## Reasoning/search action

`SEARCH` enumerates remaining Boolean variables in deterministic lexicographic order, checking each full assignment with the same literal-evaluation accounting. It stops on the first independently verified satisfying assignment or after exhausting all residual assignments.

## Frozen policies

### REASON_ONLY

No state construction. Spend the entire budget on `SEARCH` over the original formula.

### PROPAGATE_FIRST

Run `PROPAGATE` to fixed point, then use remaining budget for `SEARCH` over residual variables.

### ADAPTIVE_LOCATION

Pre-outcome signal: count unit clauses from clause lengths only.

- if `unit_clause_count >= 4`, run `PROPAGATE` then search;
- otherwise run `SEARCH` directly.

Threshold `4` is frozen before outcomes.

### ORACLE_LOCATION

Diagnostic ceiling only: retrospectively choose the lower-work successful result between `REASON_ONLY` and `PROPAGATE_FIRST`. It cannot serve as a candidate policy or tune the threshold.

## Frozen formula families

The task specification contains:

- `UNIT_HEAVY_SAT`: 8 positive unit assignments plus a non-unit tail constraint. Raw lexicographic search must encounter many incompatible assignments; propagation should compress the state.
- `UNIT_MIXED_SAT`: 4–6 positive units plus non-unit residual constraints.
- `UNIT_CONTRADICTION`: at least four unit clauses including a direct contradiction; propagation can prove UNSAT without enumerating the full space.
- `LOW_UNIT_EASY_SAT`: no unit clauses and an early satisfying assignment; propagation scanning is expected to be unnecessary overhead.

The mixture is part of the hypothesis. Failure on any family remains visible.

## Primary outcomes

Per instance/policy report:

- terminal `SAT`, `UNSAT`, or `BUDGET_EXHAUSTED`;
- verifier-correctness;
- literal evaluations in propagation;
- literal evaluations in search;
- total literal evaluations;
- number of variables fixed by compilation;
- number of search assignments tried.

Aggregate by family first.

## Frozen positive gate

`P12_VERIFIER_RESOURCE_LOCATION_V1_SUPPORTED` requires:

1. every reported SAT assignment independently verifies;
2. every reported UNSAT is established by contradiction or exhaustive residual search;
3. `ADAPTIVE_LOCATION` solve rate >= both non-oracle comparators;
4. `ADAPTIVE_LOCATION` mean work over solved cases is < `PROPAGATE_FIRST` mean work and < `REASON_ONLY` mean work **or** it strictly solves more instances than a comparator at the same budget while not using more mean work than the other;
5. adaptive regret relative to `ORACLE_LOCATION` is reported, not hidden;
6. threshold remains exactly 4 and cases remain frozen;
7. byte replay passes.

## Hostile checks

- propagation/search use different work units;
- unit signal evaluates clause truth rather than structure only;
- hidden solution leaks into propagation/order;
- unsat claimed after timeout/budget exhaustion;
- oracle result used to tune threshold;
- cases selected after outcomes;
- solution validity inferred from solver self-report without independent clause verification.

## Authority boundary

A positive closes a verifier-backed formal/search replication of resource-location metareasoning. It does not satisfy the still-preferred open-weight LLM/procedural replication or universal cross-domain allocator transfer.
