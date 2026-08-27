# P2 structural-discovery extension — development packet

Parent issues: #406, #407. Coordinator: #403. Publication parent: #99.

## Pre-existing design authority

Issues #406/#407 were frozen before this implementation session and supplied the goal, schema coordinates, hostile cases, benchmark families, claim ceiling and allowed terminals. This packet records the implementation mapping; it does not retroactively promote any outcome.

## Subject / branch

- base: `main@451ed1da903d9b5eda67c60dadb280e4cea20a17`
- lane: `shadow/p2-structure-extension-2026-08-18`
- additive only: current peer-review-ready P2 manuscript/result package is not rewritten.

## Scientific object

`StructuralDiscoveryRoute.v1` is a content-bound candidate-acquisition receipt generated from a versioned `StructuralNeed`. It binds structural source, derivation kind, backend, query-derivation and capture identities. It has no transfer, novelty or task-closure authority.

## RED / hostile families

- route kind changed while backend/query/capture stay the same -> no earned independence;
- same surface/graph shape with incompatible assumption -> `OBSTRUCTION`;
- missing reconstruction or provenance -> acquisition-local `UNKNOWN`, with scientific authority still `NONE` until downstream P4/P8 evaluation;
- semantically distant but structurally unrelated donor -> `OBSTRUCTION`;
- unavailable/censored/exhausted structural route -> task remains `OPEN`;
- source structural digest changed after route freeze -> receipt verification fails;
- clean different-domain structural match -> `CANDIDATE` only, never scientific authority.

## Bounded empirical discriminator

`HISTORICAL_PANEL_V1.json` freezes four curated candidate universes with pre-transfer donor sources and later transfer/realization sources. The panel is adversarial: topical decoys share target vocabulary, while the intended donor is often lexically distant. The deterministic scorer compares token overlap with typed structural compatibility at the same candidate budget.

The only admissible terminal from this pilot is `P2_STRUCTURAL_DISCOVERY_NARROWED`. A broader `SUPPORTED` terminal requires a new prospectively frozen external retrieval campaign with strong embedding, citation-expansion and LLM-query baselines.

## Authority / nonclaims

- P2 surfaces candidates only.
- P3/P6 own structural mapping/equivalence.
- P4/P8 own scientific authority.
- acquisition-local `UNKNOWN` is not a scientific authority terminal.
- novelty remains externally adjudicated.
- the current P2 publication terminal and external-superiority `CANNOT_CHECK` boundary remain unchanged.

## Verification target

Run at minimum:

```bash
pytest -q tests/test_p2_structure_extension.py tests/test_p2_structural_pilot.py tests/test_p2_structure_claim_boundary.py
python papers/paper-02-open-world-scientific-discovery/scripts/run_structural_discovery_pilot.py --check
```

Then run repository CI on the PR head. No issue closes from prose or a local green alone.
