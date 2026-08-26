# Table ORION-12-S1 — Complete-gold route-stop oracle replay

**Authority:** `TIER_B_committed`; 390 frozen tasks. Deterministic repeat seeds were checked for identical route/stop traces and collapsed within task before counting denominators. The authority is an achieved precision tier, not a promoted primary claim.

| System | Route-stop events | FP | FP rate | Routes reaching oracle exhaustion | FN | FN rate | Attempts after exhaustion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ORION full | 1950 | 13 | 0.0067 | 1878 | 0 | 0.0000 | 377 |
| Protocol-driven SLR | 1170 | 0 | 0.0000 | 1170 | 0 | 0.0000 | 0 |
| BM25 / keyword | 390 | 0 | 0.0000 | 390 | 0 | 0.0000 | 0 |
| Dense retrieval | 390 | 0 | 0.0000 | 390 | 0 | 0.0000 | 0 |
| Sparse+dense hybrid | 780 | 0 | 0.0000 | 780 | 0 | 0.0000 | 0 |
| One-pass RAG | 780 | 0 | 0.0000 | 780 | 0 | 0.0000 | 0 |
| Agentic single route | 390 | 0 | 0.0000 | 390 | 0 | 0.0000 | 0 |
| Adaptive multiroute (exploratory) | 1560 | 13 | 0.0083 | 1547 | 0 | 0.0000 | 377 |
| No route-independence check | 780 | 0 | 0.0000 | 780 | 0 | 0.0000 | 0 |
| No question-conditioned read ledger | 1950 | 13 | 0.0067 | 1878 | 0 | 0.0000 | 377 |
| Route stop can close task | 390 | 0 | 0.0000 | 390 | 0 | 0.0000 | 0 |
| No unavailable-route open state | 1950 | 13 | 0.0067 | 1878 | 0 | 0.0000 | 377 |
| Coverage diagnostic controls stopping | 780 | 0 | 0.0000 | 780 | 0 | 0.0000 | 0 |
| No content-identity dedup | 1950 | 13 | 0.0067 | 1788 | 0 | 0.0000 | 377 |

## Interpretation

O1 defines a route-stop false positive as a declared route stop while at least one previously unfound gold identity remains reachable on that route and at least one route-call budget unit remains. It defines a route-stop false negative as **more than one** attempt after the gold-defined oracle exhaustion point; one confirming attempt is explicitly allowed.

Full ORION records 13 O1 route-stop FP in 1950 route-stop events (0.0067) and 0 FN over 1878 routes that reach oracle exhaustion. On the `RESTRICTED` route, 13 stops are false positives, 377 task-routes reach oracle exhaustion, and 377 post-exhaustion attempts are retained.

A route-level FP does **not** automatically become a task-level false closure: O4 keeps unresolved unavailable-route evidence open, and full ORION may return `CANNOT_CHECK` instead of asserting task completeness. This is the intended separation between route stopping and task stopping.

Source record digest: `c6430a651810f8e7a794aa0c1091794963c43389a1e5080c02c2807a2fc2c574`  
Source rich-artifact hash-list digest: `d851f168faaf50969198180ecc61a6ac361c72556ceeb992f011af307dd00c37`
