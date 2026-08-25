# P2 harness probe read a retired evaluator projection

**Observed:** 2026-08-25 while reproducing the merged research-harness
engineering-conformance job.

## Failure

`paper_programme_conformance()` reported P2 as non-operational because its P2
probe read `evaluation.stop_audits` and expected route/task records carrying a
`scope` field.  The live P2 complete-gold evaluator now projects route evidence
as `evaluation.route_stop_audits` and task-closure evidence as the explicit
`closure_declared`, `premature_closure`, `authority_flags`, and oracle residual
fields.  The P2 evaluator executed and preserved the adverse premature-closure
outcome, but the programme probe raised `KeyError: 'stop_audits'` before it
could assess that evidence.

## Failure class

`STALE_HARNESS_PROJECTION_INTERFACE`

A cross-paper conformance probe was bound to a retired serialization shape
instead of the current public evaluator projection.  A valid adverse result was
therefore misreported as an unavailable mechanic.

## Correct response

1. Preserve the current P2 evaluator output and its adverse
   `premature_closure` terminal; do not retune the study.
2. Add a focused regression test that executes the live P2 programme probe.
3. Bind the route-stop check to `route_stop_audits`, including the current
   `false_positive` and `cannot_check` fields.
4. Bind the task-stop check to the current explicit task-closure fields and the
   exact task/system residual in the evaluator oracle.
5. Keep the P1-P15 conformance terminal open if either the positive or
   fail-closed probe is false.

## General lesson candidate

Cross-module conformance probes need contract tests against the exact exported
projection they consume.  When an evaluator schema changes, a probe must not
translate a missing legacy field into scientific failure or erase an adverse
outcome.  Interface conformance, scientific outcome, and publication authority
remain separate judgments.
