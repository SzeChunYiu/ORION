# P7 additive bridge — navigation in open method space

**Status:** additive successor text for #420/#422. The current P7 manuscript/formal core/contract suite remain historical authority and are not rewritten.

## MethodChart.v1

P7 consumes P6 signature/fibre identities as navigation nodes; it does not redefine or certify fibre membership. `MethodChart.v1` is a bounded local view containing known signatures/fibres, typed transform edges, route/source-family lineage, an explicit unknown boundary, explicit noncoverage and reopen triggers. Every chart carries `can_claim_global_exhaustion=false` and `can_authorize_invention=false`.

Navigation events cover local neighbors, fibre realizations, structural-analogy routes, generalization/specialization, composition routes, representation changes and invention escalation. Each event binds its chart, source/target, evidence, provenance and rationale; it grants neither transfer nor novelty authority.

## Stop hierarchy

P7 separates four terminals mechanically:

1. route stop — one acquisition route ended;
2. chart stop — the current bounded neighborhood has no more justified moves;
3. known-library stop — currently represented fibres/routes are exhausted under the frozen policy;
4. task stop — allowed only with external scientific authority.

The first three leave `task_terminal=OPEN` and `global_method_space_open=true`. Thus local exhaustion never becomes “no useful method exists.” Known-library exhaustion may make an invention challenger eligible, but it never proves invention is necessary.

## Representation change, reopening and revisit control

A representation-change edge that requires reconstruction is blocked when reconstruction fails and remains unresolved when reconstruction evidence is missing. A new signature or route increments the chart epoch and content identity, invalidating stale local closure. Repeated visits to the same target with identical evidence are suppressed; new evidence may reopen the move.

## Bounded discriminator

`P7.MethodSpaceBench.v1` freezes ten synthetic contracts covering route/chart/library stops, an externally authorized task stop, harmful and beneficial reframes, premature and policy-complete invention escalation, chart reopening and repeated-reframe suppression. All ten frozen contract outcomes pass. The terminal is deliberately `P7_METHOD_SPACE_NAVIGATION_NARROWED`: the suite establishes the stop/reopen/escalation semantics, not real-world retrieval efficiency or superiority to strong semantic, planning or POMDP baselines.

## P9/P10 boundary

P9 may score or prioritize chart transitions but model probability cannot alter chart evidence or authority. P10 may receive an `INVENTION_ESCALATION` proposal only after the declared known-route policy is exhausted; that proposal does not claim global nonexistence and cannot self-authorize a new method. P4/P8 remain the authority path.
