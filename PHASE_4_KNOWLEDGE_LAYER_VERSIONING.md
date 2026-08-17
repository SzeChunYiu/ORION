# Phase 4 Knowledge Layer Versioning

## Status

**PREPARATORY PROTOCOL** — Not active until Issue #209 closes and Issue #210 authorizes programme operation.

## Overview

Phase 4 maintains three co-evolving knowledge layers:

1. **Object Knowledge (K)**: Claims, evidence, referents, and their relationships
2. **Search-Universe Knowledge (W)**: Sources, domains, routes, and coverage obligations
3. **Method Knowledge (M)**: Algorithms, protocols, and their applicability boundaries

These layers co-evolve under dependency-directed invalidation: changes in one layer can trigger reopening of dependent knowledge states.

## Layer 1: Object Knowledge (K)

### Schema

```yaml
ObjectKnowledge:
  version: string                    # Semantic version
  created_at: datetime
  epoch: string                      # Evaluation epoch identifier

  # Core identities
  objects:
    - id: string                     # Content-addressed identifier
      type: enum[claim, evidence, referent, measurement]
      content_hash: string
      source_version: string
      provenance:
        origin: enum[generated, retrieved, measured, derived]
        lineages: list[string]       # Dependency chain
      authority_state: enum[VERIFIED, SUPPORTED, CONTRADICTED, OPEN, CANNOT_CHECK]

  # Relationships
  relationships:
    - from_object_id: string
      to_object_id: string
      type: enum[supports, contradicts, cites, measures, depends_on]
      confidence: float | null

  # Contradictions and plural views
  contradictions:
    - object_id: string
      conflicting_objects: list[string]
      resolution_status: enum[unresolved, resolved_rejected, resolved_accepted, stable_plural]
      resolution_evidence: list[string]

  # Uncertainty representation
  uncertainty:
    - object_id: string
      uncertainty_type: enum[evidence_missing, attribution_unclear, measurement_error, model_limitation]
      magnitude: enum[low, medium, high]
      blocking_promotion: boolean

  # Dependencies
  dependencies:
    - object_id: string
      depends_on:
        - type: enum[method, measurement, search_universe_assumption]
          target_id: string
          criticality: enum[required, supporting, incidental]
```

### Versioning Rules

1. **Content addressing**: Object IDs derive from cryptographic hash of content
2. **Source version binding**: Every claim binds to exact source version
3. **Provenance tracking**: Full lineage from origin to current state
4. **Append-only updates**: New evidence appends; history never mutates
5. **Contradiction visibility**: Contradictions are first-class, not hidden

### Invalidation Triggers

- New evidence invalidates claim authority status
- Source version change reopens all dependent claims
- Contradiction discovery triggers reassessment
- Measurement error discovery invalidates dependent conclusions

## Layer 2: Search-Universe Knowledge (W)

### Schema

```yaml
SearchUniverseKnowledge:
  version: string
  created_at: datetime
  epoch: string

  # Search universe state
  universe_state:
    explicit_version: string            # W state identifier
    last_updated: datetime
    coverage_audit_date: date

  # Source coverage
  source_families:
    - family_id: string
      domains: list[string]
      routes: list[string]
      coverage_obligation: enum[mandatory, preferred, optional]
      coverage_status: enum[satisfied, partial, blind_spot, unavailable]
      saturation_test_date: date | null

  # Blind spots and gaps
  blind_spots:
    - domain: string
      gap_type: enum[no_sources, stale_index, access_denied, censorship_unknown]
      severity: enum[critical, high, medium, low]
      discovery_date: date
      mitigation: string | null

  # Censorship and unavailability
  censored_unavailable:
    - route: string
      status: enum[censored, unavailable, deprecated, blocked]
      last_verified: date
      fallback_routes: list[string]

  # Reopen rules
  reopen_conditions:
    - trigger: enum[new_domain_discovered, new_route_available, censorship_lifted, index_freshened]
      affected_objects: list[string]      # Objects to reopen
      required_actions: list[string]

  # Closure declaration
  closure_state:
    is_closed: boolean
    closure_basis: list[string]           # Evidence supporting closure
    outstanding_gaps: list[string]
    reopen_triggers: list[string]
```

### Versioning Rules

1. **Explicit W versioning**: Every search state has a version identifier
2. **Coverage obligations**: Mandatory domains must be satisfied before closure
3. **Blind-spot registration**: All gaps are visible, not hidden
4. **Censorship typing**: Distinguish censorship from unavailability
5. **Reopen triggers**: Clear conditions for reopening closed universes

### Invalidation Triggers

- New domain/route discovery reopens source-family coverage
- Blind-spot discovery triggers saturation reassessment
- Censorship status change reopens dependent claims
- Index refresh invalidates stale-universe-based conclusions

## Layer 3: Method Knowledge (M)

### Schema

```yaml
MethodKnowledge:
  version: string
  created_at: datetime
  epoch: string

  # Method definitions
  methods:
    - id: string                         # Content-addressed method ID
      name: string
      type: enum[algorithm, protocol, heuristic, model]
      implementation:
        commit_hash: string
        entry_point: string
        dependencies: list[string]       # Exact version pins
      applicability:
        domains: list[string]
        assumptions: list[string]
        boundary_conditions: list[string]
        known_failures: list[string]

  # Causal support
  causal_support:
    - method_id: string
      failure_hypothesis: string
      discriminator: string              # Test that separates this cause
      supporting_evidence: list[string]
      refuting_evidence: list[string]
      confidence: enum[established, plausible, speculative, rejected]

  # Replay and fresh transfer
  transfer_evidence:
    - method_id: string
      replay_success: boolean
      fresh_transfer_success: boolean
      transfer_domain: string
      regression_magnitude: float | null

  # Negative history
  negative_history:
    - method_id: string
      failure_class: string
      discovery_date: date
      harmful_outcomes: list[string]
      blocking_conditions: list[string]

  # Known failure classes
  failure_classes:
    - class_id: string
      description: string
      detection_method: string
      affected_methods: list[string]
      recurrence_prevention: string
```

### Versioning Rules

1. **Exact implementation identity**: Commit hash + entry point + dependency pins
2. **Assumption boundary**: Explicit applicability and boundary conditions
3. **Causal linking**: Failures trace to specific hypotheses with discriminators
4. **Transfer separation**: Replay success ≠ fresh transfer success
5. **Negative preservation**: Harmful variants remain addressable

### Invalidation Triggers

- New failure discovery invalidates method applicability claims
- Boundary violation discovery narrows applicability
- Transfer regression discovery blocks promotion
- New failure class triggers method reassessment

## Co-Evolution Invalidation Rules

### Object → Search-Universe

```yaml
invalidation_rules:
  - trigger: "new_object_evidence"
    target: "search_universe_coverage"
    condition: "evidence from previously unknown domain/route"
    action: "reopen source_family coverage status"
```

### Object → Method

```yaml
  - trigger: "new_object_failure_pattern"
    target: "method_applicability"
    condition: "method fails on new object subclass"
    action: "narrow method boundary or mark failure"
```

### Search-Universe → Object

```yaml
  - trigger: "search_universe_reopened"
    target: "dependent_object_claims"
    condition: "W version change affects claim source basis"
    action: "reopen claim authority status"
```

### Search-Universe → Method

```yaml
  - trigger: "search_universe_expanded"
    target: "method_comparison"
    condition: "new sources enable fresh baseline comparison"
    action: "reopen method competitive evaluation"
```

### Method → Object

```yaml
  - trigger: "method_promoted"
    target: "method_dependent_claims"
    condition: "new method changes measurement/verification capability"
    action: "remeasure affected objects"
```

### Method → Search-Universe

```yaml
  - trigger: "method_boundary_change"
    target: "search_universe_coverage_obligations"
    condition: "method can now access new domains"
    action: "update coverage requirements"
```

## Dependency Graph Structure

```yaml
dependency_graph:
  nodes:
    - id: string
      type: enum[object, search_universe, method]
      version: string
      invalidation_hooks: list[string]

  edges:
    - from: string
      to: string
      relation_type: enum[invalidates, reopens, requires, narrows]
      condition: string

  traversal_rules:
    - "invalidation propagates downstream"
    - "reopening is typed and auditable"
    - "historical states remain reproducible"
```

## Machine-Readable Protocol Format

```yaml
knowledge_layers:
  protocol_version: "0.1.0-preparatory"
  activation_condition: "awaiting_issue_209_closure"

  object_knowledge:
    schema_path: "schemas/object_knowledge.yaml"
    versioning_strategy: "content_addressed_append_only"
    invalidation_triggers:
      - "new_evidence"
      - "source_version_change"
      - "contradiction_discovery"

  search_universe_knowledge:
    schema_path: "schemas/search_universe_knowledge.yaml"
    versioning_strategy: "explicit_W_versioning"
    invalidation_triggers:
      - "new_domain_discovery"
      - "blind_spot_discovery"
      - "censorship_status_change"

  method_knowledge:
    schema_path: "schemas/method_knowledge.yaml"
    versioning_strategy: "exact_implementation_identity"
    invalidation_triggers:
      - "new_failure_discovery"
      - "boundary_violation"
      - "transfer_regression"

  co_evolution_rules:
    invalidation_graph: "directed_acyclic"
    propagation: "downstream_only"
    audit_trail: "required_for_all_transitions"
```

## Activation Condition

This protocol becomes active when:
1. Issue #209 closes with `PHASE_3_GOVERNED_SELF_ORION_CLOSED`
2. Issue #210 authorizes self-sustaining research programme operation
3. All three knowledge-layer schemas are implemented
4. Dependency graph and invalidation propagation are functional

## References

- Issue #209: Phase 3 closure dependency
- Issue #210: Phase 4 closure (this protocol)
- PAPER_04_VERIFIED_DISCOVERY.md: Verified Scientific Discovery
- PAPER_05_SELF_ORION.md: Self-ORION research object
