# 01 — Recursive Epistemic Reconstruction Engine

This subtree defines the central ORION state-transition machine.

\[
\boxed{\text{FRAME}\to\text{SEARCH}\to\text{ABSORB}\to\text{RECONSTRUCT}\to\text{DETECT}\to\text{DIAGNOSE}\to\text{REFRAME}\to\text{REOPEN}\to\text{RECURSE}}
\]

## Operator contracts

Each operator must eventually specify:

```text
identity
purpose
typed inputs / outputs
state read/write coordinates
preconditions / postconditions
authority it may and may not create
admissibility conditions
invariants
failure and CANNOT_CHECK semantics
reopen conditions
composition rules
resource semantics
known-answer benchmark
hostile benchmark
fresh-transfer benchmark
implementation reference
empirical-open coordinates
```

## Operators

### FRAME
Construct the active object, question, context, target authority, resources and blocking invariants. Framing remains provisional and challengeable.

### SEARCH
Expand computational access through heterogeneous query/source/domain routes. Search results are candidates, never authority.

### ABSORB
Interpret retrieved material as contextual projections; perform extraction, identity resolution, mapping, verification and typed assimilation.

### RECONSTRUCT
Update the global portrait and the model of what knowledge might be relevant. Learning may therefore change both `K_t` and `W_t`.

### DETECT
Emit typed residuals: missing evidence, contradiction, context gap, representation failure, search-coverage failure, measurement/evaluator failure, method gap, etc.

### DIAGNOSE
Separate competing responsibility hypotheses before modification. An unresolved responsibility set blocks high-impact reframing.

### REFRAME
Apply the smallest justified typed change to question, representation, decomposition, interface, search/routing policy, measurement, evaluator or method.

### REOPEN
Stale every dependent closure/saturation certificate while preserving unaffected verified knowledge and all negative history.

### RECURSE
Continue from the reconstructed state, opening child fibers or ancestor challenges as residuals require.

### BOUNDED SATURATION
Stop only when knowledge growth and formulation growth are flat under registered heterogeneous challenges, all material residuals are resolved/typed/blocked, and resource-bound uncertainty is reported as CANNOT_CHECK rather than rounded to closure.
