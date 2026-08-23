# EpistemicState.v0 / EpistemicDelta.v0

**Status:** provisional exact-study contract; frozen for EA-1A only.  
**Nonclaim:** this is not a universal ontology of knowledge or cognition.

The purpose of V0 is to make the first ORION-EA discriminator executable without importing the whole ORION framework into a neural architecture. The schema is deliberately smaller than #957's opening tuple.

## 1. Minimal state

```text
EpistemicState.v0 = {
  state_id,
  representation,
  nodes,
  edges,
  failure_scopes,
  obligation_scopes,
  lineage
}
```

### Representation

```text
Representation.v0 = {
  representation_id,
  semantic_key,
  parent_id?,
  correspondence_id?
}
```

`representation_id` is an occurrence/version identity. `semantic_key` denotes the evaluator-defined semantic regime for V0.

A new identity with the **same** semantic key is a remint, not a material regime change. A changed semantic key is a material change for the V0 tests. This distinction is evaluator-defined in exact worlds and must not be guessed from natural-language names.

### Node

```text
EpistemicNode.v0 = {
  node_id,
  kind,
  status,
  payload_token
}
```

Kinds:

```text
EVIDENCE
CLAIM
METHOD
FAILURE
OBLIGATION
```

Statuses:

```text
ACTIVE
RETRACTED
BLOCKED
UNKNOWN
STALE
```

`payload_token` is opaque/reminted model-visible content. Gold labels, family id and evaluator semantics are never encoded in it.

### Edge

```text
EpistemicEdge.v0 = {
  edge_id,
  source_id,
  target_id,
  kind
}
```

V0 edge kinds:

- `SUPPORTS`: a target with multiple independent support edges remains supported while at least one active support remains.
- `REQUIRES`: a hard dependency; retraction of a required prerequisite retracts the target, while an `UNKNOWN` prerequisite makes the target `UNKNOWN`.
- `DEFEATS`: an active defeater blocks a method or retracts a claim.

These semantics are benchmark mechanics, not proposed universal epistemic logic.

### Failure scope

```text
FailureScope.v0 = {
  failure_id,
  required_semantic_key,
  reopen_on_semantic_change
}
```

An active failure may defeat/block a method. If the active representation changes semantically and the failure is scoped to the old semantic key with `reopen_on_semantic_change=true`, the failure becomes `STALE`; its defeated method may reopen if no other active blocker remains.

A representation **remint** with the same semantic key does not stale the failure.

### Obligation scope

```text
ObligationScope.v0 = {
  obligation_id,
  required_semantic_key,
  transportable
}
```

On a material semantic representation change:

- a transportable obligation remains active;
- a non-transportable old-regime obligation becomes `UNKNOWN` until revalidated;
- claims/methods with hard dependency on that obligation become `UNKNOWN`.

This creates an exact fail-closed representation/obligation test without pretending to solve general proof transport.

## 2. Intervention object

```text
EpistemicIntervention.v0 =
  RETRACT(node_id)
  ACTIVATE(node_id)
  MARK_UNKNOWN(node_id)
  CHANGE_REPRESENTATION(new_representation)
```

Interventions are evaluator-controlled. The learned model does not choose the protected intervention in EA-1A; it must infer the correct minimal state delta *after* the intervention is exposed through the permitted observation contract.

Later studies may learn inquiry/intervention choice, but that is deliberately separated from state-update correctness.

## 3. Delta object

```text
EpistemicDelta.v0 = {
  operations: [DeltaOp...]
}
```

V0 operations:

```text
SET_STATUS(node_id, ACTIVE|RETRACTED|BLOCKED|UNKNOWN|STALE)
SET_REPRESENTATION(representation_id)
```

The delta is **minimal**: operations are emitted only for coordinates whose state changes. Preservation is evaluated against all omitted state coordinates.

The learned output is a proposal. The exact kernel verifies/executes it and independently computes gold in benchmark generation.

## 4. Exact propagation rules

After the evaluator intervention, repeatedly apply the following deterministic rules until a fixed point.

### Defeat

For active target `t`:

```text
if exists ACTIVE source s with DEFEATS(s,t):
    CLAIM(t)  -> RETRACTED
    METHOD(t) -> BLOCKED
```

### Hard requirement

For every `REQUIRES(s,t)`:

```text
if status(s) in {RETRACTED, BLOCKED}:
    t -> RETRACTED
elif status(s) == UNKNOWN and no stronger terminal already applies:
    t -> UNKNOWN
```

### Alternative support

If `t` has one or more incoming `SUPPORTS` edges:

```text
if any support source is ACTIVE:
    t -> ACTIVE
elif any support source is UNKNOWN:
    t -> UNKNOWN
else:
    t -> RETRACTED
```

This permits an independently supported claim to survive deletion of one source.

### Reopening after defeater staleness

A METHOD blocked only by a failure node may return to `ACTIVE` when all active defeating failure nodes cease to be active.

This is a V0 test mechanic, not automatic scientific permission to execute the method.

## 5. Representation-change rules

For `CHANGE_REPRESENTATION(R_old -> R_new)`:

```text
material_change = R_old.semantic_key != R_new.semantic_key
```

If false:

- only representation occurrence/version changes;
- scoped failures remain active;
- old obligations remain at their previous state;
- no semantic reopening is licensed.

If true:

- qualifying old-regime failure records become `STALE`;
- nontransportable old-regime obligations become `UNKNOWN`;
- the fixed-point dependency rules then run;
- any method freed from all active defeaters may reopen to `ACTIVE`;
- dependent claims may become `UNKNOWN` rather than falsely remaining certified.

## 6. Invariants

Every EA-1A exact world must satisfy:

1. unique node/edge identities;
2. every edge endpoint exists;
3. failure/obligation scope references a node of the correct kind;
4. evaluator family/gold identities are excluded from model-visible payloads;
5. a representation remint cannot change semantic gold except the occurrence/version field;
6. a material representation change cannot silently preserve a nontransportable old-regime obligation;
7. independent active support prevents unnecessary descendant retraction;
8. exact kernel result is deterministic;
9. applying the kernel-produced delta reconstructs the exact post-state;
10. no model output can create authority/novelty/adoption status.

## 7. Why V0 is intentionally small

V0 does **not** yet model:

- probabilistic confidence;
- graded support;
- causal interventions on the external world;
- social evidence;
- full ORION P4/P8 authority;
- arbitrary method preconditions/effects;
- higher-order representation correspondence proofs;
- learned new node/edge types;
- Jump/concept invention.

Those would confound the first question: can a learned model propose correct minimal typed changes to an evolving epistemic state beyond donor-complete state/memory controls?

A V1 schema is permitted only if EA-1A exposes a residual that cannot be expressed cleanly with V0.
