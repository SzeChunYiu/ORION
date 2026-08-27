# Q1 R20 — sharp support theorem without resource inflation

Date: 2026-08-27

Status: analytic theorem and resource-authority boundary.

## Exact scoped theorem

In the frozen three-block shared-Tag TARE-M2 grammar, every exact optimum admits frame support at most two. A clean proof uses parity-neutral local deletion and a Restore-cost bound: any feasible frame of support at least three has a proper deletion preserving nonidentity, partner anticommutation, shared-Tag parity, assignment, central branch, and the other blocks, while the Restore increase is no larger than the frame refund. Repeating the exchange terminates at support at most two without increasing the objective.

A two-qubit witness has unrestricted optimum 5 and support-at-most-one optimum 6, with support zero infeasible. Therefore the frozen threshold is exactly

`kappa_R6M=2`.

## Structural consequences

For the fixed six-frame grammar:

- each support-two anticommuting block pair occupies at most three qubits;
- all six frames admit an optimum on a common auxiliary frame core of at most nine qubits;
- the shared Tag can be projected to that core without changing label equations or increasing the frozen objective;
- a compatible Tag has support at most six for any fixed feasible frames;
- the exact ordered support-at-most-two anticommuting-pair count is

  `P(n)=6n+54n(n-1)^2`;

- target-only preprocessing followed by direct exact checking has a theorem-certified `P(n)^3=O(n^9)` candidate bound with constant candidate-local work.

These are representation/search theorems. They are not runtime or hardware-resource claims.

## Independence ceiling

The analytic proof has same-program clean-room reconstruction and finite hostile controls. A bounded `n=3` search over one deterministic digest-selected subject finds no support-three optimum, but its source contract historically included the registered proof blob. It remains bounded corroboration, not proof-independent external replay.

A proof-clean successor must use only neutral grammar definitions and a prospectively frozen target selector. It may not read the registered proof, proof-named source files, solver, canonicalizer, witness generator, or result receipts before its own encoding is committed.

## Exact resource map

Under one explicit all-to-all parity-ladder/single-control template, the frozen objective has a conditional interpretation in logical two-qubit Clifford counts. The three-block family has exactly nine arbitrary-angle rotations under that template.

This does not determine:

- T count or T depth;
- approximation precision or rotation-synthesis cost;
- logical/physical qubit count;
- routing or architecture overhead;
- error-correction factories or spacetime;
- wall time or production search benefit.

## Preserved adverse benchmark

The primary QG-21 chemistry control remains donor-exact on 90/90 rows. Only a sensitivity arm improves 18/90 rows by two logical two-qubit Clifford gates. This is an adverse/no-gain primary result, not evidence of compiler advantage.

Current holistic Pauli compilers use global binary-symplectic transformations and report large gate/depth reductions on public Hamiltonian suites. Q1 must therefore compare against a current global compiler under matched semantics, architecture, routing, synthesis precision, and resource accounting. The nine-qubit/core theorem cannot substitute for that experiment.

## Strongest defensible claim

> A frozen shared-Tag TARE-M2 grammar has a sharp support-two exact normal form, a system-size-independent nine-qubit auxiliary frame core, and a polynomial direct-checker bound.

Q1 may not claim production compiler advantage, circuit-resource savings, fault-tolerant improvement, hardware benefit, or external novelty authority without the matched benchmark and proof-clean independent review.
