# Dependency invalidation and reopening (Step 2)

Code: `src/orion/programme/dependency.py`. Schemas
`orion.programme.dependency-edge.v1`, `orion.programme.reopen-event.v1`,
`orion.programme.reopen-ledger.v1`.

## The mechanism already existed in miniature

`orion.core.closure.ClosureCertificate` carries `dependency_coordinates` and an
`invalidate(reason)` that returns a **new** frozen certificate via
`dataclasses.replace`. Reopening therefore cannot rewrite the prior certificate,
because it never touches it. Historical reproducibility is a structural property
of that design, not a discipline anyone has to remember. This module makes it
explicit, types the trigger, and writes the reopening down.

## Coordinates

Addressing reuses what the engine already reads: the roots `K`/`W`/`M` from
`orion.registry.CORE_STATE_COORDINATES`, plus the formulation prefixes
`QUESTION`, `FRAME`, `METHOD`, `EVALUATOR` that
`orion.core.history.IterationRecord.formulation_flat` already matches on. A
reopen event and an iteration record can therefore be joined with no translation
table. A record that names no coordinate is rejected: nothing could ever
invalidate it, which makes it indistinguishable from an unversioned assertion.

## Edges run in every direction

`DependencyEdge` names a dependent record, a supporting record, the coordinates
it watches, and the `InvalidationTrigger` values it accepts. Co-evolution is the
point, so all six inter-layer directions are expressible:

- new object evidence → search-universe closure is no longer sound
  (`NEW_OBJECT_EVIDENCE`, `CONTRADICTING_OBJECT_CLAIM`)
- new object evidence → a method's applicability boundary is violated
  (`METHOD_APPLICABILITY_VIOLATED`)
- a new domain, route or representation → object claims verified under the old
  universe reopen (`NEW_DOMAIN_DISCOVERED`, `NEW_ROUTE_DISCOVERED`,
  `NEW_REPRESENTATION_DISCOVERED`, `BLIND_SPOT_FOUND`)
- a method or evaluator revision → remeasurement of object claims
  (`METHOD_REVISION`, `EVALUATOR_REVISION`)
- a source version change → every claim bound to the old version
  (`SOURCE_VERSION_CHANGED`)
- external authority → anything (`EXTERNAL_AUTHORITY_DIRECTIVE`)

An edge fires only when the trigger is one it accepts *and* a changed coordinate
falls inside a subtree it watches.

## Reopening adds; it never removes

`ReopenEvent` records the trigger, the origin, the changed coordinates, the
reason, the epoch, the digests it supersedes and the digests that succeed them.
Two rules are enforced by `validate_reopen_event`:

1. Superseded and successor digests must be **disjoint**. Overlap would mean a
   record is its own successor — an in-place edit dressed as a reopening.
2. A supersession with **no successor** is rejected. That is deletion, not
   reopening, and `HC-HIDDEN-DELETION` treats it as laundering.

`apply_reopen` returns a new certificate tuple. The inputs are untouched, and a
test asserts the prior certificate's digest is byte-identical afterwards.

## The ledger

`build_reopen_ledger` produces an append-only transcript with the same shape as
`orion.study.p5.negative_history_chain`: a genesis digest over
`(programme_id, protocol_digest)`, one link per event binding its predecessor
hash, a final chain hash, and a sealed document digest.

Determinism is not authority. `verify_reopen_ledger` requires an
`expected_document_hash` supplied by an external host; a transcript that only
verifies against itself proves nothing about who froze it. Reordering, editing or
dropping an event all produce errors.

## What this does not do

It does not decide *whether* to reopen. That is a programme-governance question
(Step 3), and it depends on evidence that does not exist yet. This layer only
guarantees that when a reopening happens it is typed, auditable, and lossless.
