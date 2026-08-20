# ORION-RSE formal verification closure V1

**Date:** 2026-08-20  
**Executable owner:** `formal_verification_core.py`  
**CI owner:** `tests/unit/research/test_formal_verification_core.py`  
**Status before exact-head CI:** `CANDIDATE_CLOSURE_PENDING_CI`.

This document closes the formal/mechanic interpretation of the RSE wave. It deliberately distinguishes finite/executable results from definitions, protocol axioms and donor-owned formalisms.

## 1. Executable propositions

### RSE.T1 — task correctness is not scientific-standing correctness

Registered exact RSSI worlds separate final task answer from standing migration. Always-preserve, always-reopen and answer-only controls fail. The first donor union closes the simple pilot; on the transport/fresh-authority interaction pilot a naive donor union keeps task answers correct while migrating standing incorrectly, whereas a coordinated justification/authority composition closes the case.

**Disposition:** `EXECUTABLE_COUNTERMODEL_VERIFIED` once CI binds the executable report.

**Novelty boundary:** no claim that ORION invented semantic transport, assurance cases or proof-carrying authority. The interaction is a benchmark/control property.

### RSE.T2 — finite successor-state non-identifiability

For each registered DPAIR-1..3 pair:

```text
candidate_input(left) = candidate_input(right)
future_transition(left) = future_transition(right)
protected_future_standing(left) != protected_future_standing(right)
```

Therefore any deterministic current-summary-only policy must emit the same prediction for both variants and can be correct on at most one of the two. The exact per-pair ceiling is `1/2`. The registered current-summary policy reaches exactly `1/2`; full history and the compact typed-lineage control reach `1.0`.

**Disposition:** `FINITE_INFORMATION_CEILING_VERIFIED`.

**Novelty boundary:** the mathematics is ordinary information/sufficiency/bisimulation structure. ORION contributes the scientific-standing future-transition countermodel family, not a new general sufficiency theorem.

### RSE.T3 — delayed epistemic debt

On the D4 extension, present-generation task answers are correct for every variant. A lossy current-summary state still yields `1/2` successor-action accuracy and produces all three registered failure modes:

- invalid commit when evidence should be revalidated;
- missed reopened route when an old negative cause has been removed;
- stale-authority action where external reauthorization is required.

Full history and compact typed lineage remain exact.

**Disposition:** `CAUSAL_DELAYED_DEBT_COUNTERMODEL_VERIFIED`.

**Novelty boundary:** “delayed epistemic debt” is descriptive shorthand for this exact synthetic result, not a claimed new universal scientific phenomenon.

### RSE.T4 — counterexample-guided projection evolution

The registered CEGAR application shows:

```text
F0: 0 registered lineage coordinate families
 -> protected DPAIR-1..3 counterexamples
F1: 3 coordinate families; 1.0 disjoint holdout on DPAIR-1..3
 -> unseen obligation-provenance family: 0.5
 -> protected counterexample
F2: 4 coordinate families; 1.0 disjoint old+new holdout
```

Full reconstructive lineage remains `1.0` throughout.

**Disposition:** `CEGAR_APPLICATION_VERIFIED`.

**Novelty boundary:** CEGAR, abstraction refinement and task-relative sufficient state are donor-owned. No ORION refinement-algorithm theorem is claimed.

### RSE.T5 — generic justification donor subsumption

The strongest registered subtraction replaces bespoke coordinate enumeration with a fixed, family-agnostic justification condition language:

```text
ALWAYS_VALID
INVALIDATE_ON_EVENT
INVALIDATE_WHEN_EVENT_TARGET
VALID_ONLY_FOR_EVENT_TARGET
```

The obligation-provenance family reuses `INVALIDATE_ON_EVENT`; the condition interpreter is not widened after seeing that family. On disjoint all-family holdout the donor is exact while the frozen three-coordinate F1 projection is `1/2` on the unseen obligation family.

**Required terminal:** `GENERIC_JUSTIFICATION_DONOR_SUFFICIENT`.

**Scientific consequence:** strike any RSE/P9/P1 claim that the bespoke F1->F2 coordinate expansion is a superior scientific-state representation on DPAIR-1..4.

## 2. Definitions and design rules that are not theorems

### RSE.D1 — `JReach_B(F,x,C|kappa)`

**Status:** `DEFINITION_ONLY`.

It is an organizing definition for scientifically justified reach under declared resources and protected constitution. This wave does not prove a universal theorem about its existence, optimality or uniqueness.

### RSE.D2 — mutable framework versus protected constitution

**Status:** `DESIGN_AXIOM_PLUS_EXISTING_P4_P8_AUTHORITY`.

Separating proposal/self-change capability from validation/authority is a programme constraint supported by P4/P8 and broad prior work. It is not a new standalone RSE theorem.

### RSE.D3 — reconstructive lineage plus task-relative working projection

**Status:** `DONOR_COMPOSITION_PRINCIPLE`.

Event sourcing, truth-maintenance/justification systems, predictive-state theory and abstraction refinement own the ingredients. RSE uses the composition to specify future experiments.

### RSE.D4 — non-compensatory scientific dominance

**Status:** `PROTOCOL_RULE_ONLY`.

A successor is not accepted merely for a higher scalar task score when authority, integrity, preservation or protected-evaluation obligations regress. This is ORION evaluation doctrine, not a theorem of rational agency.

### RSE.D5 — one permanently sufficient compact scientific state

**Status:** `STRUCK_UNPROVED_UNIVERSAL`.

The programme explicitly does not claim that a fixed compact state is sufficient for every future open-ended scientific transformation. Sufficiency remains relative to a declared future query/transformation family and resource model.

## 3. Study dispositions

### #627 — donor saturation

The recorded changed-vocabulary search reached two consecutive no-material-change rounds after repeated claim subtraction.

**Closure terminal:** `INTERACTION_ONLY_RESIDUAL_FROZEN` / donor saturation closed for this registered wave.

This is a saturation result, not external novelty authority.

### #628 — exact RSSI interaction benchmark

The exact benchmark is non-vacuous and catches naive union/answer-only failure. However the stronger coordinated justification/authority composition closes the interaction pilot. The subsequent generic justification donor further removes bespoke state-schema novelty.

**Closure terminal:** `DONOR_COMPOSITION_SUFFICIENT`.

Retain the benchmark as a hostile regression suite.

### #629 — successor-conditioned state sufficiency

The exact pair theorem, D4 delayed-action extension and CEGAR projection cycle all verify their registered properties. Full history is a fidelity ceiling, compact typed lineage closes DPAIR-1..3, and the fixed generic justification donor closes DPAIR-1..4 without bespoke schema growth. No frozen cost comparison establishes an efficiency advantage over the donor/full-history state.

**Closure terminal:** `FULL_HISTORY_OR_DONOR_STATE_SUFFICIENT`.

The result is useful subtraction: it identifies what information a future scientific state must preserve on these families, while refusing to claim a new state formalism.

### #625 — parent Constitutional Recursive Scientific Evolution programme

The wave produced a disciplined framework synthesis, exact countermodels and reusable falsifiers, but did not establish an ORION-specific recursive-evolution advantage over the strongest donor composition. The strongest registered state representation is donor-sufficient, and no external F0->F1->F2 scientific campaign exists.

**Closure terminal:** `DONOR_COMPOSITION_SUFFICIENT`.

This closes the current RSE research wave honestly. It does not prohibit reopening on a genuinely new interaction family that defeats the frozen donor meta-product under a prospectively registered protocol.

## 4. Paper synchronization

The exact implications and nonclaims are synchronized through:

- `papers/RSE_VERIFIED_SUCCESSOR_HANDOFF_V1.md`;
- `research/paper-programme-v1/RSE_P1_P10_HANDOFF_2026-08-20.md`;
- paper-local `RSE_SUCCESSOR_BOUNDARY_V1.md` files for P1–P5 and the current P9/P10 packages.

No existing headline empirical result is widened. P5 external governed self-improvement remains `CANNOT_CHECK`; P9 remains bounded structured learning; P10 remains the bounded Lean/Mathlib technical note.

## 5. Final exact-head gate

Close/merge only when all are true on the final PR head:

1. repository `ci` is `success`;
2. `tests/unit/research/test_formal_verification_core.py` is collected by the normal `tests/` configuration;
3. the executable closure terminal is `RSE_FORMAL_MECHANICS_VERIFIED_WITH_DONOR_SUBSUMPTION`;
4. no paper synchronization edit changes an existing claim ledger or protected numerical result;
5. PR remains mergeable against the exact current `main` base.

Until that exact-head gate is observed, this file is a candidate closure packet rather than repository authority.
