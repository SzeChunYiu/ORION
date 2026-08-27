# AB R12 — source-bound registry non-identifiability result

Exact theorem parent: `533a8e15dc20fd875eb442b573fd72eb9264b218`

Source/theorem/workflow head: `4caf9076cf4d5eeb7eaacaeec38890b5d2cc4922`

Workflow run/job: `33019293566` / `98345369363`

Artifact SHA-256: `705c5dfffc799b61056bbfb295382b2049f9936bed1028bda0410b80ee8100b4`

Result SHA-256: `d4f14be666dceb2da71bfac01a25fd32c6fd7bc947734db1d0f945bc10487cf0`

Terminal:

`AB_REGISTRY_NONIDENTIFIABILITY_R12_PASS`

## Exact result

The verifier exhausts every semantics-preserving, resource-decreasing registry on the complete descending-edge state spaces of sizes two through six:

- total registries: `33,866`;
- size-six registries: `32,768`;
- identical direct optimizer signature for every registry;
- terminal complexity spans every value from one through `n` for every `n=2,...,6`.

For the analytic empty-versus-chain family through `n=32`, the optimizer value remains one while the terminal-complexity ambiguity reaches 31. A single unresolved edge from state `n` to state one changes terminal complexity from `n` to `n-1` for every tested `n`.

## Source-bound R6M result

The workflow binds the exact R6M protocol and runner blobs at source commit `1e18787841d99d76a3c7661505838d2eca8780db` and verifies the load-bearing direct-optimizer structure:

- local option/cost tables;
- a 512-state XOR dynamic program;
- exact DP backtracking;
- direct Restore accounting;
- witness reconstruction.

The bound source exposes no move-registry function, legal-move predicate, successor iterator or rewrite-schema interface. It can establish the frozen optimum without defining production terminality.

This is not evidence that no larger external compiler has rewrites. It proves that the executed R6M source used by the failed transfer gate does not itself supply the complete move language required to convert optimizer corroboration into a production-terminal claim.

## Scientific disposition

The earlier terminal

`FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED__PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE`

is upheld and sharpened. The rejection cannot be repaired by relabeling enumerated candidates or observed optimizer traces as moves. A future transfer must bind either:

1. an extensional legal-move predicate and exact complete enumeration; or
2. a complete external operation grammar plus a schema/parameter coverage proof and hostile omitted-schema control.

Until then:

- R6M optimizer values: internally corroborated;
- abstract AB fusion/interaction theorems: valid in their declared languages;
- R6M production terminal complexity: not established;
- compiler/resource application: not established.

## Authority

The universal non-identifiability theorem is analytic; the finite run is implementation/source-binding corroboration. Generic rewriting and black-box identification are donor-owned. No production transfer, compiler performance, physical-resource, novelty, external-review or journal authority follows.
