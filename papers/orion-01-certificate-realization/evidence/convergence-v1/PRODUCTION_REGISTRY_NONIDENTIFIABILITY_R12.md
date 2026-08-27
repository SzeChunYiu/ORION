# AB R12 — production-registry non-identifiability from optimizer outputs

Date: 2026-08-26

Exact parent: `533a8e15dc20fd875eb442b573fd72eb9264b218`

Status: analytic explanation of the fail-closed R6M production-transfer result. Generic rewriting systems, transition-system conformance, black-box identification and software trace coverage are donor-owned. The AB-specific contribution is the exact distinction between an optimizer certificate and a production-terminal certificate under the paper's representation/move/resource contract.

## 1. The blocker exposed by the completed gate

The finite R6M realization gate executed 31,457,280 candidate evaluations and reproduced every DP/brute-force optimum, but returned

`FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED`

with sole issue

`PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE`.

That terminal is not an engineering inconvenience. It is forced by an information-theoretic distinction: a direct optimizer can establish an optimum over a declared feasible set without defining which semantics-preserving reductions are legal operations of the production system. Production terminality depends on that move relation, not only on optimum values.

## 2. Finite setup

Let `S` be a finite state space, `sigma:S->Omega` a semantics map and `r:S->N_{>=1}` a support/resource measure. For a semantic class `S_omega`, a direct optimizer reports

`OPT(omega)=min_{s in S_omega} r(s)`

and optionally one minimizing state.

A production move registry is a relation `M subseteq S x S`. In this tranche every registered move is required to preserve semantics and strictly reduce resource:

`(u,v) in M => sigma(u)=sigma(v)` and `r(v)<r(u)`.

A state is `M`-terminal when it has no outgoing registered move. Define the production terminal complexity of a semantic class by

`T_M(omega)=max{r(s): s in S_omega and s is M-terminal}`.

This is the certificate ceiling relevant to AB. It is different from `OPT(omega)`.

A registry is **complete relative to a declared production language** when it contains every move admitted by that language. Completeness is always relative to a language or implementation contract; calling an arbitrary relation complete by fiat does not establish that it models an external compiler.

## 3. Same optimizer, arbitrarily different terminal complexity

### Theorem AB-R12.1 — optimizer-output non-identifiability

For every integer `n>=2`, there are two finite, sound, terminating and extensionally complete declared registries on the same state space, semantics and resource function with identical direct-optimizer output but terminal complexities `n` and `1`.

### Construction and proof

Let

`S={s_1,...,s_n}`,

put all states in one semantic class, and set `r(s_i)=i`. The direct optimizer uniquely returns `s_1` with value one.

Let `M_empty` contain no moves. It is complete for the declared language with no production reductions. Every state is terminal, so `T_M_empty=n`.

Let

`M_chain={(s_i,s_{i-1}): 2<=i<=n}`.

It is complete for the declared predecessor-fusion language. Every move preserves the sole semantics and strictly decreases resource. Its unique terminal is `s_1`, so `T_M_chain=1`.

The feasible states, semantic map, resource function, optimum value and optimum witness are identical. Only the production language differs. ∎

### Corollary AB-R12.2

No function of direct optimizer input/output pairs, optimum values, or optimum witnesses alone can determine production terminal complexity or registry completeness.

The gap in Theorem AB-R12.1 is `n-1`, so the ambiguity is unbounded.

## 4. Finite execution traces do not prove completeness

Suppose a reviewer observes only a set of executed move-membership queries or transition traces. Any candidate transition not resolved by those observations can differ between two registries that agree on the entire transcript.

### Theorem AB-R12.3 — hidden-edge ambiguity

Let `E` be the set of all semantics-preserving, resource-decreasing candidate edges. Let a finite audit leave some edge `(u,v) in E` unresolved. If `u` is terminal in the audited partial registry and has resource larger than every other partial-registry terminal, then the two completions

- exclude `(u,v)`;
- include `(u,v)`

agree on every resolved query but have different terminal complexity.

### Proof

Excluding the edge leaves `u` terminal and realizes its resource as the maximum. Including it makes `u` nonterminal. All resolved memberships are unchanged. Under the stated strict-maximum premise, the terminal maximum decreases. ∎

Thus a collection of successful optimizer traces, even exhaustive over benchmark inputs, cannot certify a move registry unless it is also exhaustive over the admissible transition language or accompanied by a schema-completeness proof.

### Corollary AB-R12.4 — observed moves are only a lower inventory

A trace-derived registry certifies that the observed moves exist. It does not certify that unobserved legal moves do not exist. Using it for a terminal lower bound is fail-open unless completeness is separately established.

## 5. What a complete production certificate must contain

### Theorem AB-R12.5 — two sufficient completeness routes

For a finite production subject, registry completeness is established by either of the following content-bound routes.

### Extensional route

1. bind the finite production-state domain;
2. bind a decidable legal-move predicate;
3. enumerate every ordered state pair or every generator parameter tuple;
4. prove that the committed registry equals exactly the predicate-positive set;
5. verify semantics preservation and resource descent for every member.

### Schema route

1. bind the external implementation's complete operation interface or formal grammar;
2. prove that every legal operation instance belongs to one of finitely many registered schemas;
3. prove that each schema's parameter domain is exhaustively covered;
4. verify semantics preservation and resource descent symbolically or extensionally;
5. include a hostile omitted-schema mutation that changes terminality and is rejected.

Under either route, terminal complexity may then be computed from the complete transition relation.

### Proof

The extensional route establishes set equality directly. The schema route establishes both inclusions: every implementation operation is covered by a schema, and every registered schema instance is a legal operation. Soundness/descent then make terminal analysis well defined. ∎

Source digests, optimizer correctness and finite optimum enumeration are necessary bindings but are not substitutes for either route.

## 6. Source-bound R6M diagnosis

Pinned subject commit: `1e18787841d99d76a3c7661505838d2eca8780db`.

Load-bearing source:

- protocol blob `48214ac16ce956a109cbce39a25d59b77eb95b3a`;
- runner blob `ead51fc9d03e25acf3d65557cb0f08fd1eb98873`.

The runner is a direct optimizer. Its load-bearing architecture consists of:

- local option/cost tables;
- a 512-state XOR dynamic program;
- exact backtracking from an accepting parity state;
- direct Restore-factor accounting;
- witness reconstruction and verification.

It does not expose an extensional production transition relation, a successor iterator, a rewrite schema registry or a legal-move predicate over production states. The optimizer can prove the frozen minimum cost without answering whether one feasible production object rewrites to another.

This diagnosis is source-bound to the runner, not a claim that no larger external TARE/compiler implementation has rewrite operations. If such an implementation is the intended production subject, its actual operation interface and completeness argument must be imported and audited explicitly.

## 7. Consequences for the AB manuscript

Admissible statement:

> The finite R6M gate independently confirms the declared optimizer values but rejects production transfer because the bound direct-DP source does not declare a complete production move language. This rejection is mathematically necessary: optimizer input/output behavior does not identify production terminal complexity.

Forbidden statements:

- enumerating the optimizer's candidates declares every legal production move;
- an optimum witness is automatically a terminal lower-bound witness;
- source-code coverage or benchmark trace coverage establishes registry completeness;
- the 31,457,280-evaluation run establishes a production compiler gap.

The abstract XOR/finite-group separations remain valid for their declared complete fusion languages. They transfer to R6M or another compiler only after one of Theorem AB-R12.5's completeness routes succeeds.

## 8. Finite corroboration

`verify_registry_nonidentifiability_r12.py` enumerates every resource-decreasing registry on chains of sizes two through six: `33,866` registries in total. All have the same unique direct optimum. Their terminal complexities span the full range from one to `n`. The verifier also checks the empty/chain unbounded family and a one-hidden-edge trace ambiguity for every `n` through 32.

The analytic theorems carry the universal statements; enumeration is implementation corroboration only.

## 9. Prior-art and authority boundary

Generic transition systems, abstract rewriting, operational semantics, model extraction, conformance testing and black-box system identification are donor-owned. AB does not claim the generic fact that behavior may underdetermine an implementation.

The residual contribution is the theorem's use as a fail-closed certificate-ownership boundary: exact optimizer corroboration, proof-language terminality and production-registry completeness are three different authorities and cannot promote one another.

This tranche does not establish the missing R6M registry, a compiler speedup, physical resource value, novelty, external review or journal authority. It turns the previous rejection into a precise theorem and a content-bound next gate.
