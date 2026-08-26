# Phase 4 Constitutional Boundary

## Status

**PREPARATORY PROTOCOL** — Not active until Issue #209 closes and Issue #210 authorizes programme operation.

## Purpose

Define the immutable constitutional boundary that no candidate/LLM process may mutate, regardless of programme phase or cycle.

## Constitutional Rules

### CB-01: Protected Evaluator Immutability

**Rule**: Candidate/LLM processes cannot mutate protected evaluators.

**Scope**:
- Evaluator source code and configuration
- Metric definitions and computation
- Test/benchmark held-out sets
- Evaluation verdict logic

**Protection mechanisms**:
1. Evaluator custody resides outside candidate write authority
2. All evaluator changes require explicit host promotion
3. Evaluator telemetry includes patch/access logging
4. Hostile battery validates evaluator integrity

**Violations**:
- Candidate modifies evaluator/metric code → `BLOCK`
- Candidate reads held-out labels → `BLOCK`
- Candidate weakens tests to improve scores → `BLOCK`

### CB-02: Missing Evidence Semantics

**Rule**: Missing evidence remains `OPEN`/`CANNOT_CHECK`; programme pressure cannot force positive conclusions.

**Scope**:
- Unresolved claim attribution
- Missing source references
- Unavailable external validation
- Insufficient protected evaluation

**Protection mechanisms**:
1. `OPEN` and `CANNOT_CHECK` are valid terminal states
2. No implicit downgrade to soft confidence scores
3. Evidence gaps block promotion, not just scoring
4. Programme deadlines do not override evidence requirements

**Violations**:
- Converting `CANNOT_CHECK` to probabilistic score → `BLOCK`
- Averaging missing-evidence cases into success rate → `BLOCK`

### CB-03: Negative History Immutability

**Rule**: Null, harmful and rejected research directions remain immutable negative history.

**Scope**:
- Rejected method variants
- Failed interventions
- Harmful transferred changes
- Recognized failure classes

**Protection mechanisms**:
1. Append-only negative history storage
2. No deletion or modification of historical records
3. Negative history conditions future routing/guards
4. Hostile attempts to launder history are detected

**Violations**:
- Deleting harmful variant from history → `BLOCK`
- Rebranding failed method as new → `BLOCK`
- Ignoring negative history in promotion decision → `BLOCK`

### CB-04: State Change Traceability

**Rule**: Every programme-level state change is content/lineage/version bound and replayable.

**Scope**:
- Programme configuration changes
- Knowledge-layer updates
- Evaluation epoch transitions
- Policy/governance modifications

**Protection mechanisms**:
1. Content-addressed state artifacts
2. Immutable lineage tracking
3. Exact version binding for all dependencies
4. Replay scripts for every state transition

**Violations**:
- Unrecorded state mutation → `BLOCK`
- Missing dependency version → `BLOCK`
- Non-reproducible state transition → `BLOCK`

## Machine-Readable Specification

```yaml
constitutional_boundary:
  version: "0.1.0-preparatory"
  status: "awaiting_issue_209_closure"

  protected_paths:
    - evaluators/
    - held_outs/
    - authority_policy/
    - phase_rules/
    - programme_termination_criteria/

  immutable_states:
    - OPEN
    - CANNOT_CHECK
    - BLOCK

  negative_history_rules:
    storage: "append_only"
    deletion: "forbidden"
    modification: "forbidden"
    retrieval: "always_required"

  state_change_requirements:
    - content_addressing
    - lineage_tracking
    - version_binding
    - reproducibility_script
```

## Validation Tests

```python
# Pre-commit checks for constitutional violations
def test_evaluator_immutability():
    """Candidate cannot modify protected evaluators."""
    pass

def test_missing_evidence_semantics():
    """Missing evidence cannot be converted to positive scores."""
    pass

def test_negative_history_immutability():
    """Negative history cannot be deleted or modified."""
    pass

def test_state_change_traceability():
    """All state changes must be content/lineage/version bound."""
    pass
```

## Activation Condition

This protocol becomes active when:
1. Issue #209 closes with `PHASE_3_GOVERNED_SELF_ORION_CLOSED`
2. Issue #210 authorizes self-sustaining research programme operation
3. All constitutional rules are implemented in code
4. Hostile battery validates protection mechanisms

## References

- Issue #209: Phase 3 closure dependency
- Issue #210: Phase 4 closure (this protocol)
- Issue #208: Programme parent
- PAPER_05_SELF_ORION.md: Self-ORION research object
