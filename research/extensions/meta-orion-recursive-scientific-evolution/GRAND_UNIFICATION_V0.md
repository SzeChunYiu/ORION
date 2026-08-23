# ORION Grand Unification V0 — Lineage, Projection, and Justified Reach

**Status:** programme-level synthesis / research hypothesis. Not a claimed new mathematical theory and not a numbered paper identity.

**Programme:** #625

**Nearest-work rule:** causal states, predictive-state representations, sufficient statistics, bisimulation, CEGAR, truth maintenance, event sourcing, dynamic assurance, proof-carrying verification/authorization, ontology evolution and belief revision own the corresponding mathematical/system ingredients. ORION's scientific question is the protected composition under autonomous scientific-framework evolution.

---

## 1. Central correction: there is no reason to expect one final scientific state tuple

A fixed tuple such as

```text
Omega = (R,K,I,V,A,C,T,U,...)
```

can be useful at a registered resolution, but open-ended scientific evolution makes a stronger permanent claim unjustified.

A state representation is sufficient only relative to the future distinctions it must support.

If future scientific questions, methods, observation interfaces, representations, obligations or authority rules can change, a distinction that is irrelevant today may become load-bearing tomorrow.

Therefore the grand framework should not seek one eternal list of coordinates.

It should maintain two different objects with different responsibilities.

---

## 2. The dual scientific state

### 2.1 Reconstructive scientific lineage

Let

```text
L_t
```

be an append-only or equivalently reconstructive lineage containing the source-bound scientific history required to recover prior distinctions:

- observations/evidence and identities;
- scientific claims and their justifications;
- representations/semantic views;
- methods/operators and versions;
- dependencies/defeaters;
- obligations and their discharge routes;
- negative/failure knowledge and causal scope;
- objective/question versions;
- authority/policy/evaluator versions;
- framework revisions and correspondence maps;
- explicit UNKNOWN/unresolved history.

`L_t` need not be one literal log file. The requirement is reconstructability: a future scientific transition must not depend on distinctions that were irreversibly erased without an explicit bounded justification.

### 2.2 Working scientific projection

Let

```text
Z_t = phi_t(L_t)
```

be a compact, operational scientific state used for current reasoning.

`Z_t` should expose exactly the distinctions needed for the registered family of scientific operations and protected decisions, not copy all lineage by default.

This yields the design objective:

```text
retain lineage for future recoverability
compress projection for current scientific efficiency
```

This is a scientific instance of established event-sourcing / predictive-state / sufficient-statistic ideas, not a novelty claim for the ingredients.

---

## 3. Protected future-science equivalence

For protected constitution `kappa`, resource bound `B`, and a registered family of admissible future scientific/framework transitions `U`, define a history equivalence conceptually by

```text
h ~_(kappa,B,U) h'
```

iff every admissible future transition sequence in `U` produces the same protected scientific consequences from `h` and `h'`.

The consequences include at least:

- scientific standing of inherited claims;
- admissible evidence routes;
- hard obligation discharge/reopening;
- negative-knowledge applicability;
- authority/adoption status;
- UNKNOWN/CANNOT_CHECK outcomes;
- justified reachable scientific contracts under `B`.

A working projection `phi` is **future-science sufficient** for `(kappa,B,U)` only if

```text
phi(h) = phi(h')  =>  h ~_(kappa,B,U) h'.
```

The #629 delayed-pair benchmark constructs explicit counterexamples to a projection that keeps only current answer and standing.

---

## 4. Minimal scientific state is relative, not absolute

For a fixed registered transition/query family `U`, the quotient of histories by future-science equivalence gives the conceptual minimal state partition needed for that family.

This is analogous to minimal sufficient statistics, causal states and bisimulation quotients. ORION does not claim first ownership of that mathematics.

The scientifically important consequence is operational:

> a claim that a scientific-state representation is sufficient must name the future contract family for which sufficiency is asserted.

No bare `STATE_COMPLETE` terminal is meaningful without a registered scope.

---

## 5. Monotone refinement under an expanding future

Suppose the admissible scientific-transition family expands:

```text
U_0 subseteq U_1.
```

Then any two histories distinguishable under `U_0` remain distinguishable under `U_1`; new future operations may additionally split histories previously equivalent.

Conceptually:

```text
~_(U_1) refines ~_(U_0).
```

This is an elementary consequence of quantifying equivalence over a larger future family, not a new theorem claim.

It has a major ORION implication:

> method/operator/framework invention can make the old scientific-state abstraction insufficient even when every old task remains solved.

This is the exact phenomenon behind the successor-conditioned D3/D4 programme.

---

## 6. Open-ended sufficiency limit

Consider any lossy working projection `phi` for which two reconstructively distinct histories satisfy

```text
phi(h) = phi(h').
```

If the future scientific framework is allowed to introduce an admissible transition whose protected consequence depends on the discarded distinction between `h` and `h'`, then `phi` is not sufficient for that expanded future family.

Therefore a **fixed lossy projection cannot be guaranteed sufficient for unrestricted open-ended framework evolution** unless the system has an independent reason that all discarded distinctions are irrelevant to every admissible future scientific transition.

This is a design limitation derived from standard sufficiency logic, not a claim of a new impossibility theorem.

ORION's response should be neither:

```text
store only the current summary forever
```

nor

```text
reason from the entire raw history on every step.
```

It should preserve reconstructive lineage and refine/cache task-relative projections as the future operation family changes.

---

## 7. Counterexample-guided scientific-state refinement

When protected evaluation exposes histories that the current projection merged but whose scientific consequences differ, the system has an abstraction counterexample.

Adopt the established CEGAR doctrine:

```text
coarse projection
-> protected counterexample
-> identify missing distinguishing predicate/coordinate
-> refine projection
-> replay affected scientific standing
-> fresh protected test
```

The ORION-specific research question is not CEGAR itself. It is whether the counterexample, refinement and replay can be defined over **scientific standing** across heterogeneous evidence, obligations, failures and authority while the scientific framework itself evolves.

A refinement proposal cannot authorize its own scientific adoption.

---

## 8. Justified Reach as the common performance object

Retain the programme-level object

```text
JReach_B(F, Z, C | kappa)
```

for contracts scientifically reachable under framework `F`, working state `Z`, resource bound `B`, target contracts `C`, and protected constitution `kappa`.

The lineage/projection distinction now sharpens this object:

```text
Z = phi_U(L).
```

A framework change can improve justified reach in two separate ways:

1. **operator/framework expansion** — new valid scientific transitions become possible;
2. **state refinement** — previously conflated histories become distinguishable, preventing invalid actions or enabling valid ones.

The two effects must not be conflated experimentally.

---

## 9. Scientific evolution is a coupled dynamics

The full ORION research process becomes a coupled evolution of three mutable objects under one protected authority boundary:

```text
L_t     reconstructive scientific lineage
phi_t   working scientific projection
F_t     scientific framework / mechanic / inquiry system
```

with protected constitution

```text
kappa_t
```

outside ordinary self-promotion.

A generation can therefore contain:

```text
(L_t, phi_t, F_t)
  -> observe protected discrepancy/failure/opportunity
  -> diagnose responsible layer
  -> search/absorb strongest donor
  -> propose local repair OR operator/framework change
  -> if state abstraction is insufficient, refine phi_t
  -> append evidence/change to L_(t+1)
  -> migrate scientific standing explicitly
  -> external kappa gate
  -> fresh scientific evaluation
  -> freeze accepted successor
```

A proposed change to `kappa` requires a separate externally governed generation; it cannot be certified by the actor benefiting from the new rule.

---

## 10. Projection of the ORION research programme

This is a synthesis map, not a numbering rewrite.

### P1 — recursive reconstruction

Owns discovery that the active problem/formulation/search state is inadequate and that a higher-level reframe must be licensed by lower-level exclusion and preservation obligations.

In the unified view: P1 changes `F` and/or the active projection `phi` when the current scientific coordinates are insufficient.

### P2 — open-world discovery

Owns route/search expansion and nontrivial stopping in an open world.

In the unified view: P2 explores `JReach` under the current `F` and proposes new observations/routes that may expand lineage `L` or expose projection insufficiency.

### P3 — global knowledge portrait

Owns source-local projections, scientific meaning, correspondence, GLUE and obstruction.

In the unified view: P3 supplies semantic maps needed to interpret and transport lineage/projected state across representations.

### P4 — verified scientific discovery

Owns content-bound evidence and independent checking.

In the unified view: P4 constrains which lineage events and standing derivations can enter protected scientific state.

### P5 — Self-ORION

Owns persistent failure/issue history, causal discrimination, isolated self-change, fresh transfer and no self-promotion.

In the unified view: P5 governs accepted transitions of `F` and `phi` and retention of negative lineage.

### P6 — formal epistemic mechanics

Owns typed local scientific transitions, footprints, preconditions/effects/preservation at its supported scope; the broad universal-calculus claim is struck.

In the unified view: P6 provides the local transition contracts used inside `F`.

### P7 — epistemic navigation / transport

Owns movement, representation change and preservation/reopening across open-world charts.

In the unified view: P7 supplies transport laws between projections and representations.

### P8 — epistemic authority

Owns non-compensatory authority and anti-laundering.

In the unified view: P8 supplies the protected decision boundary between proposal, evidence, standing and adoption.

### P9 — structured epistemic learning

Current bounded P9 shows that load-bearing structural coordinates can change identifiability/transfer and that richer learning is unnecessary when explicit inference already closes the residual.

In the unified view: a P9 successor may learn useful approximations to `phi_U`, applicability/effect predictions, and candidate missing distinctions—but learned confidence remains non-authoritative.

### P10 — revision-bound formal evaluation evidence

Current P10 shows concretely that content identity, native checker acceptance, semantic faithfulness and scientific authority are distinct.

In the unified view: P10 supplies a bounded example of why reconstructive lineage and protected standing cannot be collapsed to a verifier bit.

### Meta-ORION / ORION-RSE

Owns the prospective empirical question of whether `F`, `phi` and their improvement process can recursively evolve while scientific lineage/standing remain valid and future successor generation improves under `kappa`.

---

## 11. The recursive scientific-improvement criterion

One-generation performance is insufficient.

Use the D0–D4 protocol:

```text
D0 -> F0 proposes F1
D1 -> external acceptance of F1
D2 -> untouched current-generation scientific value
D3 -> new future transformation/scientific environments
D4 -> protected successor/F2 standing and scientific value
```

Require separately:

```text
DirectImprove(F1,F0)
MetaImprove(F1,F0)
StandingIntegrity(F0->F1->F2)
```

A system that improves D2 but corrupts D4 standing is not recursively scientifically improved.

---

## 12. Ultimate ORION objective

The strongest defensible programme statement is now:

> **ORION studies science as the controlled evolution of a reconstructive knowledge lineage, a task-relative scientific state projection, and a revisable framework of inquiry—while keeping the authority to declare scientific progress externally protected.**

Or operationally:

```text
preserve what may matter later
compress what is sufficient now
refine when protected counterexamples prove it is not
invent new scientific operations only after narrower parents fail
never let the inventor define its own success
```

This is the current grand-unified architecture.

Its publishable frontier is not the architecture prose. It is the protected empirical question:

> Can this lineage-projection-framework coevolution achieve better resource-bounded future scientific standing and multi-generation successor quality than full-history replay, dynamic assurance, epistemic-state replication, fixed compact state, CEGAR-based refinement and the complete donor meta-product under matched powers?

That is the no-man's-land experiment ORION-RSE must now earn.