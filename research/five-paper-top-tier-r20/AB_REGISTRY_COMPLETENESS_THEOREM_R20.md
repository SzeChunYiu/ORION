# AB R20 — registry completeness is the exact production-transfer boundary

Date: 2026-08-27

Status: analytic theorem package explaining the preserved R6M production-gate rejection. Generic rewriting, confluence, zero-sum theory, graph independence, and equality saturation are donor-owned.

## Setup

Let `S` be a finite declared state space, `sigma:S->Omega` its semantics, `w:S->R_+` the registered support/objective, and `M` a set of admissible directed moves. Every move `s->t` must preserve `sigma` and strictly decrease the registered termination measure. A state is `M`-terminal when no move in `M` applies. Define

`kappa(M)=max{w(s):s is M-terminal}`

on the declared feasible subject.

A proof language may use a weak registry `M_weak`; a production implementation owns another registry `M_prod`. A weak terminal lower witness is production-owned only when the representation and objective transfer and the witness is irreducible under the complete production registry.

## Theorem AB-R20.1 — registry-extension monotonicity

If `M subseteq M'`, then every `M'`-terminal state is `M`-terminal and

`kappa(M') <= kappa(M)`.

### Proof

Any move available in `M` remains available in `M'`. Therefore a state with no `M'` successor has no `M` successor. The `M'` terminal set is a subset of the `M` terminal set, so its maximum registered support cannot be larger.

## Theorem AB-R20.2 — incomplete registries cannot certify production lower bounds

Suppose a claimed production lower bound is justified only by a declared registry `M`, while extensional completeness for the intended production implementation is not established. Then terminality under `M` alone is insufficient to transfer the lower bound. More sharply, for every nonminimal `M`-terminal witness `s`, there exists a semantics-preserving terminating registry extension `M'` containing `M` in which `s` is reducible.

### Proof

Choose any feasible state `t` with `sigma(t)=sigma(s)` and strictly smaller termination measure, when such a state is admitted by the intended representation. Add the move `s->t`. It preserves semantics, decreases the measure, and makes `s` nonterminal. Repeating this construction for every nonminimal terminal can collapse the terminal ceiling to the intrinsic minimum. Thus the observed behavior of `M` does not distinguish a complete registry from a semantics-preserving extension that invalidates the lower witness.

If no smaller same-semantics state exists, that impossibility is itself the intrinsic lower-bound proof and must be established from the complete production state space, not inferred from missing moves.

## Corollary AB-R20.3 — exact transfer criterion

A weak certificate ceiling transfers as an exact production ceiling only after all of the following are content-bound:

1. a feasible representation map preserving semantics and registered support;
2. objective nonincrease and strict termination for every production move;
3. exact lifting of every weak move used by the upper-bound proof;
4. an extensional completeness argument for the production move registry;
5. a production preimage of a maximum weak terminal;
6. irreducibility of that witness under every production move;
7. interaction/confluence obligations required by the claimed normal-form semantics.

Failure of item 4 is not a minor reproducibility omission. By Theorem AB-R20.2 it destroys lower-bound authority.

## Theorem AB-R20.4 — interaction tax after completeness

Assume the production registry is complete and each realized component contributes one terminal certificate unit. If every minimal reducing cross-component move has support two, let `H` be the graph whose vertices are component units and whose edges are exactly the reducing pairs. Then the maximum surviving terminal budget is

`alpha(H)`,

and the loss from naive additivity is

`|V(H)|-alpha(H)=tau(H)`.

### Proof

A set of component units survives jointly exactly when it contains no registered reducing pair, hence exactly when it is an independent set. Maximizing surviving units gives `alpha(H)`. The complementary minimum deletion set is a vertex cover, giving the second identity.

If minimal reducing moves have higher arity, the same statement holds with the hypergraph independence number and complementary transversal number.

## Registered adverse application result

The finite R6M `n=2` production-realization gate evaluated 31,457,280 candidates and independently reproduced every bounded DP/brute result. Its terminal is

`FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED`

with sole issue

`PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE`.

The rejection is mathematically informative. It is the exact failure predicted by Theorem AB-R20.2: the available optimizer enumerates feasible configurations and objective values but does not expose an extensional semantics-preserving rewrite registry whose omitted moves can be audited. The result therefore supports the finite grammar computation but not a production compiler lower bound.

## Strongest defensible story

AB may claim:

> Certificate ceilings are monotone under registry extension, and no proof-language lower bound transfers to production without extensional move completeness. Once completeness is established, cross-move interactions impose an exact graph or hypergraph tax on additive certificate budgets.

AB may not claim:

- that the R6M optimizer is a complete production rewrite engine;
- a Pauli/compiler lower bound from the rejected gate;
- runtime, memory, circuit, or hardware benefit;
- novelty for Davenport constants, associative fusion, equality saturation, graph independence, or vertex cover;
- external or journal authority from finite same-owner verification.

## Remaining application gate

A production experiment must bind an executable rewrite-registry source, enumerate or prove complete every semantics-preserving reducing move on the smallest complete domains, include an omitted-move hostile control, and compare native search with certificate-aware search under matched semantics. Until then `production_transfer=false` is load-bearing evidence, not an editorial limitation.
