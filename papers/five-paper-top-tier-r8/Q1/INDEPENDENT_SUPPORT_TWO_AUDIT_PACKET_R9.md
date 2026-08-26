# ORION-Q1 R9 Independent Support-Two Audit Packet

## 1. Purpose

This packet separates four questions that must not be collapsed:

1. Is the frozen support-two theorem mathematically correct on its declared compiler and objective?
2. Does a structurally independent finite encoding fail to find a support-three optimum on the bounded declared domain?
3. What exact production object does one unit of theorem support count?
4. Is the result correctly positioned against current primary literature by an independent quantum-compilation reviewer?

A positive answer to one question does not answer the others. In particular, a bounded exhaustive PASS does not prove the all-size theorem, and an all-size theorem does not automatically imply a T-count, T-depth, qubit, or wall-clock improvement.

## 2. Expert cell and independence

### Q1-A — algebraic reconstruction specialist

Background: Pauli algebra, finite abelian normal forms, exact circuit identities, and proof auditing.

The specialist receives definitions and the claim ledger before receiving the manuscript proof. They must first reconstruct the argument independently, then compare proof dependency graphs.

### Q1-B — finite adversarial-search specialist

Background: SAT/SMT/ILP, exact synthesis, symmetry reduction, and proof-producing exhaustive search.

The implementation must not import the registered solver, canonicalizer, witness generator, or support-two checker. Shared test data are permitted only through a neutral documented interchange format.

### Q1-C — production-resource specialist

Background: fault-tolerant quantum resource estimation, circuit compilation, ancilla and feed-forward models, architecture constraints, and search-complexity accounting.

This lane owns the map from theorem support to production resources. It may terminate `NO_FAITHFUL_MAP` without disputing the theorem.

### Q1-D — independent quantum reviewer

The reviewer audits theorem scope, physical assumptions, nearest work, resource interpretation, and the proportionality of the headline. The reviewer must not be the author of Q1-A, Q1-B, or Q1-C.

## 3. Source binding before execution

No review starts from a mutable file name alone. The executor must freeze:

- repository and branch;
- commit SHA;
- manuscript path and blob SHA;
- theorem-definition path and blob SHA;
- claim-ledger path and blob SHA;
- registered implementation tree SHA, if any;
- registered result and manifest SHA-256 digests; and
- the exact objective and feasibility predicates copied into the receipt.

`discover_q1_support_two_sources_r9.py` produces candidate bindings but does not select the authoritative theorem. Q1-A and the portfolio owner must agree on one binding before scientific execution.

## 4. Frozen claim decomposition

The audit must rewrite the headline as atomic statements with explicit quantifiers. At minimum:

- the instance family;
- the feasible-state grammar;
- the shared-Tag or shared-auxiliary assumptions;
- the exact semantic invariant;
- the objective and its comparison order;
- the support functional;
- the existence statement for a support-at-most-two optimum;
- any lower witness showing support one is insufficient;
- excluded moves, architectures, or cost models; and
- whether the theorem is existential, constructive, algorithmic, or complexity-theoretic.

The phrase “support two” is forbidden in the final review without naming its owner, scope, and counted object.

## 5. Lane Q1-A — proof reconstruction protocol

1. Reconstruct the theorem from frozen definitions without reading the registered proof.
2. Record every lemma as a node in a dependency DAG.
3. For every step, record the algebraic identity, feasibility premise, semantic invariant, and objective premise used.
4. Attack supports zero, one, two, and three separately.
5. Attack degenerate generators, duplicate coordinates, vanishing coefficients, shared-auxiliary aliases, and objective ties.
6. After reconstruction, compare the independent DAG with the registered proof.
7. Preserve the first disagreement rather than silently aligning notation.

Allowed terminals:

- `PROOF_RECONSTRUCTED_EQUIVALENT`;
- `PROOF_RECONSTRUCTED_STRONGER_SCOPE`;
- `PROOF_RECONSTRUCTED_WEAKER_SCOPE`;
- `COUNTEREXAMPLE`;
- `SCOPE_MISMATCH`;
- `DEFINITION_AMBIGUITY`;
- `CANNOT_CHECK`.

Required receipts include the independent proof, dependency DAG, counterexample search notes, comparison table, reviewer identity/procedure, and content digests.

## 6. Lane Q1-B — structurally independent finite attack

### 6.1 Required encoding

The attack must encode the frozen production grammar directly. It may use SAT, SMT, MILP, CP-SAT, exhaustive canonical generation, or two independent methods. It must not encode the theorem as an assumption.

For each finite instance, compute:

- the exact optimum objective;
- the minimum support among all optima;
- at least one optimum witness;
- the result of an independent semantic evaluator; and
- the orbit/canonicalization receipt.

### 6.2 Required controls

The suite must include:

- known support-two positive witnesses;
- instances where support one is sufficient;
- matching lower witnesses where every optimum needs support two, when such witnesses are claimed;
- intentionally broken shared-Tag assumptions;
- intentionally omitted production moves;
- objective-tie cases;
- relabeling and coordinate-permutation metamorphic tests;
- a negative control whose correct terminal is a support-three counterexample outside the frozen scope; and
- timeout/resource-exhaustion preservation.

### 6.3 Required terminals

- `NO_SUPPORT3_COUNTEREXAMPLE_IN_DECLARED_FINITE_DOMAIN`;
- `SUPPORT3_COUNTEREXAMPLE`;
- `ENCODING_DISAGREEMENT`;
- `SEMANTIC_EVALUATOR_DISAGREEMENT`;
- `SYMMETRY_LEAKAGE`;
- `RESOURCE_EXHAUSTED`;
- `CANNOT_CHECK`.

A bounded no-counterexample result is corroborative only.

## 7. Lane Q1-C — production-resource map

For every abstract support unit, the map must complete the following fields:

- `abstract_object`;
- `production_object`;
- `counting_map`;
- `map_direction` — equality, upper bound, lower bound, or heuristic proxy;
- `additional_moves`;
- `ancilla_model`;
- `measurement_and_feed_forward_model`;
- `connectivity_model`;
- `parallelism_model`;
- `error_correction_model`;
- `resource_metric` — for example T count, T depth, non-Clifford layer count, qubits, magic states, search support, or candidate count;
- `conversion_theorem`;
- `failure_cases`;
- `measured_benchmark`;
- `uncertainty_or_interval`; and
- `authority_ceiling`.

The lane must distinguish:

1. theorem-owned support;
2. exact production consequence under additional premises;
3. architecture-specific search consequence;
4. empirical benchmark observation; and
5. speculation.

Allowed terminals:

- `FAITHFUL_RESOURCE_MAP`;
- `PARTIAL_RESOURCE_MAP`;
- `NO_FAITHFUL_MAP`;
- `PRODUCTION_COUNTEREXAMPLE`;
- `CANNOT_CHECK`.

`NO_FAITHFUL_MAP` is not a theorem failure. It blocks production-resource headlines.

## 8. Lane Q1-D — literature and independent review

The reviewer must search current primary sources for the nearest results in:

- exact Clifford+T or TARE synthesis;
- Pauli gadget and phase-polynomial optimization;
- ancilla-assisted and measurement-assisted identities;
- support sparsification and normal forms;
- finite-group or matroid formulations used in quantum compilation;
- lower bounds for T count, T depth, or non-Clifford support; and
- compiler benchmark methodology.

For each nearest work, record the exact theorem overlap, stronger/weaker assumptions, production model, objective, and what residual claim remains.

Allowed review terminals:

- `CLEAR_FOR_SUBMISSION`;
- `REVISION_REQUIRED`;
- `REJECT_THEOREM`;
- `REJECT_PRODUCTION_INTERPRETATION`;
- `NOVELTY_NOT_ESTABLISHED`;
- `CANNOT_CHECK`.

## 9. Journal-grade promotion gate

Q1 is not journal-submission grade until all are present:

1. a content-bound source packet;
2. independent proof reconstruction or a resolved disagreement;
3. a structurally independent finite attack with positive and negative controls;
4. a complete claim ledger;
5. a faithful or explicitly partial production-resource map;
6. a current primary-source novelty matrix;
7. an independent quantum review;
8. source, result, environment, symmetry, and negative-control manifests; and
9. a final headline whose authority does not exceed the weakest lane.

The final terminal is one of:

- `Q1_JOURNAL_GRADE_SCOPE_CLEAR`;
- `Q1_THEOREM_CLEAR__PRODUCTION_MAP_PARTIAL`;
- `Q1_REVISION_REQUIRED`;
- `Q1_COUNTEREXAMPLE_OPEN`;
- `Q1_NOVELTY_OPEN`;
- `Q1_CANNOT_CHECK`.

CI success, internal review, and manuscript polish cannot directly produce the first terminal.
