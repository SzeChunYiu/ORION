# ORION mechanics completion program

The mechanics-of-mechanics substrate turns ORION development into an observable recursive program rather than a feature checklist.

`observe_mechanics_program(expanded_workflow_cells())` reports at least:

- number of mechanic cells currently reachable from the root workflow;
- number ready for benchmarking versus still open;
- total unresolved mechanic questions;
- unresolved-question counts by dimension;
- unknown child references;
- unknown execution-dependency references;
- containment cycles and execution-dependency cycles detected separately.

The current provisional decomposition contains 59 reachable cells and 1,181 open typed questions after the protected-verification specification wave. This number is a workload observation, not a target to maximize. Universal envelopes remain marked provisional and do not remove step-specific questions. A question disappears only when the cell gains a scoped non-provisional contract/evidence field or an explicit justified waiver.

## V0 research scheduling

`plan_program_questions` is deliberately simple and deterministic:

1. preserve the local non-compensatory question priority;
2. inspect the highest-priority open coordinate across many mechanics before descending deeply into one cell;
3. convert selected questions into provider-neutral search tasks;
4. let evidence update the mechanic cell;
5. re-audit and repeat.

The current global wave returns to step-specific failure semantics across the breadth of the workflow. Universal failure/observability/handoff/state/transition/mathematics envelopes provide reusable scaffolding but remain explicitly provisional. This is a fixed auditable bootstrap policy, not a claim that breadth-first scheduling is optimal. A learned/metareasoning scheduler must demonstrate better root-relevant progress under frozen evaluation before promotion.
