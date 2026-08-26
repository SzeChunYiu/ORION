# Donor boundary and responsibility-relative sufficiency

Statistical sufficiency, state abstraction, bisimulation, predictive-state representations and causal abstractions already establish that different tasks can require different retained distinctions. Selective prediction and uncertainty gating use confidence to abstain. Provenance/evidence tracing binds artifacts to origin. Proof-carrying systems attach verifiable certificates. Memory-staleness work asks when stored information is no longer valid. ORION-23 claims none of these primitives.

The residual is **responsibility-scoped certified reuse with explicit reopen semantics and exact responsibility-support conditions**. Empirical safety–cost superiority remains unestablished because P13A's published harm endpoint was self-scored and had no reachable opportunities.

Let raw world `X` induce correct output `g_rho(X)` for responsibility `rho`, and let compact representation be `Z=T(X)`.

## Exact responsibility sufficiency

`Z` is sufficient for responsibility `rho` over world set `Omega` if there exists `h_rho` such that `g_rho(x)=h_rho(T(x))` for every `x` in `Omega`. Equivalently, every equivalence class induced by `T` must be homogeneous under `g_rho`.

## Responsibility-shift witness

A pair `(x,x')` witnesses insufficiency after `rho_L -> rho_H` when `T(x)=T(x')`, the lower-responsibility outputs agree, and the higher-responsibility outputs differ. No learner is needed to establish such a witness; it is a property of the abstraction and responsibility.

For empirical systems, operational sufficiency debt is the verified higher-responsibility performance gap between richer and compact state, conditional on a prospectively frozen lower-responsibility equivalence/noninferiority requirement. It is a benchmark quantity, not a universal information measure.
