# Candidate answer — SEARCH.ROUTE_STOP.v0

**Target dimensions:** TRANSITION_MODEL, MATHEMATICS, OUTPUTS, INVARIANTS.
**Incumbent evidence:** RAKL `publication/papers/paper-01-epistemic-mechanics/sections/04b_open_world_stopping.tex` @ `bd4ce50f`.
**Motivation:** `development/BOOTSTRAP_READINESS.md` names *route-level vs task-level stopping* as an open reopen-fiber: ORION formalizes task-level stopping (bounded saturation) more strongly than route-level stopping. This cell is where the gap closes.

## Proposed step-specific contract

**Mathematics — value-of-information stopping tied to the decision, not the stream.** The route-continuation decision is a value-of-information problem (Fletcher-lineage screening work in the incumbent), not a fixed recall target: continue a route while the expected change to *decision coordinates* (claims, proofs, evidence roots, contradictions, novelty boundaries, assumptions, unresolved fibers, discovery routes) from further items exceeds the route's marginal cost; otherwise stop, reformulate, or switch.

**Outputs (typed, none of which claims task saturation).**

```text
ROUTE_CONTINUE          — expected decision-coordinate change still material
ROUTE_REFORMULATE       — stream flat but query/vocabulary implicated (route residual)
ROUTE_SWITCH            — this route flat; other registered route families remain open
ROUTE_EXHAUSTED         — source family itself exhausted or inaccessible (coverage fact)
ROUTE_BUDGET_STOP       — stopped by resource floor: emits CANNOT_CHECK, not flatness
```

**Invariants.**
- Route-level stop is **never** evidence of task-level saturation; only the SATURATE.\* cells may aggregate route verdicts, and only over heterogeneous route families.
- An absent result on a route is not a negative fact (open-world boundary: unobserved ≠ false).
- Stopping is tied to the epistemic decision the route serves, never to raw counts of documents/edges processed (incumbent's explicit lesson).
- A flat route with an unchallenged vocabulary is `ROUTE_REFORMULATE`, not `ROUTE_SWITCH`: nearby-query flatness is not route coverage.

**Transition model.** Input: route id, recent per-item decision-coordinate deltas, remaining route budget, vocabulary-challenge status. Deterministic given a declared marginal-value estimator; the estimator itself is a registered, replaceable component (V0 may be a simple windowed rule — last N items produced zero decision-coordinate change AND vocabulary challenged → not `ROUTE_CONTINUE`).

## Known-answer test candidates

1. Route yields duplicates only for N items, vocabulary challenged → `ROUTE_SWITCH`.
2. Same flat stream, vocabulary never challenged → `ROUTE_REFORMULATE`.
3. Budget floor hit with materials still arriving → `ROUTE_BUDGET_STOP` + CANNOT_CHECK, and the task-level saturation assessment must remain OPEN.
4. Hostile: an implementation that marks the task saturated because all currently-registered routes stopped, without heterogeneity audit → refuted at the SATURATE boundary.

## Not licensed

The marginal-value estimator's live quality (does it stop too early on real literature?) is an empirical open coordinate; V0 fixes the decision semantics and the typed outputs only.
