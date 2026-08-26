# P2 additive manuscript bridge — structure-conditioned discovery routes

**Status:** additive extension for #406/#407. The already peer-review-ready narrowed P2 manuscript and its current submission PDF remain immutable historical authority. This file is the canonical insertion text for a successor manuscript/version; it does **not** broaden the current P2 headline.

## Structure-conditioned discovery routes

Open-world scientific discovery is not always well served by topical similarity. A failed method can expose a structural need that is more informative than the target field's vocabulary: preserve an invariant while changing representation; avoid a known failure mode; decompose a global obligation into local obligations; or recover a solution after solving a relaxed/dual problem. P2 therefore admits a route whose query is derived from a versioned structural object rather than from topic terms alone.

A `StructuralDiscoveryRoute.v1` binds the originating structural-need digest, derivation kind, backend identity, query-derivation identity, capture identity and exact derived terms. The structural derivation kinds are `METHOD_SIGNATURE`, `FAILURE_SIGNATURE` and `REPRESENTATION_ANALOGY`. They coexist with ordinary topical, citation and entity routes; the label "structural" is not itself evidence that the route is independent or useful.

The route has a deliberately low authority ceiling. It may surface **candidate donors only**. P3 owns source-local method projection/alignment, P6 owns formal structural reduction/equivalence, P4 owns validity/transfer evidence, P8 owns typed authority, and novelty remains external to candidate acquisition. Accordingly a P2 structural-route receipt carries `can_certify_transfer=false`, `can_claim_novelty=false`, and `can_close_task=false`.

### Earned independence still applies

A different structural label does not create another evidential route. For the bounded extension, two structural routes count as earned-independent only when backend, query-derivation and capture identities are all distinct. This is intentionally stricter than counting tool names or route labels. A method-signature query and a failure-signature query sent through the same derivation and capture path remain one dependent acquisition lane for closure accounting.

### False analogy is an explicit failure state

Semantic distance is not creativity evidence. Before a returned donor is even treated as a structural candidate, the bounded checker compares declared assumptions, protected invariants, effects and reconstruction obligations. A candidate that looks structurally attractive but drops a load-bearing assumption is an `OBSTRUCTION`; missing provenance or reconstruction is acquisition-local `UNKNOWN`. A clean match remains only `CANDIDATE`, because P2 cannot certify that the donor-to-target mapping is valid. `UNKNOWN` is deliberately below the scientific-authority layer: if such a candidate is later offered for a scientific claim, P4/P8 determine the corresponding fail-closed authority state rather than P2 minting a second authority terminal.

### Route stop remains local

Exhausting, censoring or losing a structural route does not prove that no useful method exists. `EXHAUSTED`, `UNAVAILABLE`, `CENSORED` and `BUDGET_STOP` structural-route receipts all leave the task terminal `OPEN`. The route may be revisited after a new representation, source family or upstream structural object appears.

## Worked examples

**Legitimate semantically distant route.** A combinatorial-optimization target repeatedly falls into local minima. A failure-signature route derived from `local_minimum + retain_feasible_state + escape_local_minimum` can surface a statistical-mechanics donor. The route is interesting because its transformation contract matches; its distance in vocabulary is irrelevant.

**False analogy.** A graph-shaped donor can still be blocked when its precondition is `signed_pairwise_costs` while the target reduction requires `nonnegative_pairwise_costs`. Similar topology is insufficient because the assumption changes the admissible transformation.

## Bounded historical discriminator

The extension freezes `structural_extension/HISTORICAL_PANEL_V1.json`, a four-case curated historical candidate universe with primary-source lineage and same-topic/assumption/random decoys. It contains Metropolis→simulated annealing, network flow→graph-cut segmentation, Sinkhorn matrix scaling→regularized optimal transport computation, and citation-influence→web-link ranking as a structural-precursor case (the latter is explicitly **not** asserted as exclusive causal lineage).

The deterministic pilot compares token-overlap retrieval with the typed structural scorer under the same four-candidate budget. The frozen summary is `HISTORICAL_PILOT_SUMMARY_V1.json`. Its terminal is deliberately `P2_STRUCTURAL_DISCOVERY_NARROWED`: this curated panel is a non-vacuity discriminator, not evidence of open-web superiority. Dense embedding, citation-expansion and LLM-query baselines remain a reopen condition for any broader empirical claim.

## Nonclaims

This extension does not claim that:

- structurally similar methods are formally equivalent;
- a surfaced donor transfers correctly to a target;
- semantic distance implies novelty or creativity;
- the curated historical pilot predicts open-web retrieval performance;
- P9 has learned the structural space;
- P10 can invent methods;
- route or known-library exhaustion proves global absence.

The current P2 publication claim remains exactly the bounded fail-closed discovery/closure claim recorded in `JOURNAL_READINESS.md`.
