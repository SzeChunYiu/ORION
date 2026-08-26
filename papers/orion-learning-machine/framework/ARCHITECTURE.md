# Learning Machine architecture V1

## State separation

The research core maintains four logically separate learned objects:

\[
L=(\mathcal M, B, \Gamma, H),
\]

where `M` is the mechanic library, `B` is empirical competence/unknown evidence, `Γ` is the empirical transition-contract map, and `H` is retained experience history. Planning and residual analysis consume these objects but do not rewrite their scientific meaning.

### Mechanic identity

A local `MechanicSpec` contains a stable ID, family, description, cost, source provenance, prerequisites, donor-protected traits and an optional semantic compatibility key. P6 is expected to supply the eventual richer typed mechanic contract. Until then, same-ID canonicalization is fail-closed.

### Competence

For mechanic `m` and observable feature vector `x`, the local model estimates success probability only inside an admitted evidence neighborhood. Outside that neighborhood it returns `UNKNOWN`. This separates epistemic support from a low probability of success.

### Transition contracts

For real transition observations `(state context, mechanic, effect)`, the inducer estimates effect frequencies and modal effect with explicit support, donors and source IDs. The object is called an **empirical** contract because its authority is intentionally weaker than a formal P6 semantic contract.

### Composition

`ExplicitPlanner` searches over named mechanics and emits a recoverable `SolverPlan`. It uses competence estimates and costs but cannot execute the plan. Optional state identity enables loop pruning without pretending arbitrary Python object equality is semantic state identity.

### Execution authority

`LearningMachine.execute_plan` invokes an external authorizer before every mechanic. A high competence prediction never becomes permission. The authorizer interface is the future P8 integration point.

### History and invention

All admitted experience can be hash-chained in `ExperienceLedger`. Residual recurrence is computed over explicit failure/UNKNOWN signatures. Passing the recurrence gate means only “worth proposing a candidate mechanic”; it does not authorize library admission or self-modification.

## P10 result identity

P10 freezes a mathematical task by content and source revision. An attempt binds the statement hash, solver identity, solution bytes, resource-use record and provenance. A verifier receipt binds both the frozen statement hash and exact attempt hash. Any mismatch fails closed. Verifier trust/independence is external to this package.
