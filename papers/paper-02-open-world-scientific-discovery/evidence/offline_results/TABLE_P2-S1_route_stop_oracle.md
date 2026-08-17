# Table P2-S1 — Complete-gold route-stop oracle replay

**Authority:** `DESCRIPTIVE_ONLY`; 20 frozen tasks. Deterministic repeat seeds were checked for identical route/stop traces and collapsed within task before counting denominators.

| System | Route-stop events | FP | FP rate | Routes reaching oracle exhaustion | FN | FN rate | Attempts after exhaustion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ORION full | 100 | 1 | 0.0100 | 99 | 0 | 0.0000 | 19 |
| Protocol-driven SLR | 60 | 0 | 0.0000 | 60 | 0 | 0.0000 | 0 |
| BM25 / keyword | 20 | 0 | 0.0000 | 20 | 0 | 0.0000 | 0 |
| Dense retrieval | 20 | 0 | 0.0000 | 20 | 0 | 0.0000 | 0 |
| Sparse+dense hybrid | 40 | 0 | 0.0000 | 40 | 0 | 0.0000 | 0 |
| One-pass RAG | 40 | 0 | 0.0000 | 40 | 0 | 0.0000 | 0 |
| Agentic single route | 20 | 0 | 0.0000 | 20 | 0 | 0.0000 | 0 |
| Adaptive multiroute (exploratory) | 80 | 1 | 0.0125 | 79 | 0 | 0.0000 | 19 |
| No route-independence check | 40 | 0 | 0.0000 | 40 | 0 | 0.0000 | 0 |
| No question-conditioned read ledger | 100 | 1 | 0.0100 | 99 | 0 | 0.0000 | 19 |
| Route stop can close task | 20 | 0 | 0.0000 | 20 | 0 | 0.0000 | 0 |
| No unavailable-route open state | 100 | 1 | 0.0100 | 99 | 0 | 0.0000 | 19 |
| Coverage diagnostic controls stopping | 40 | 0 | 0.0000 | 40 | 0 | 0.0000 | 0 |
| No content-identity dedup | 100 | 1 | 0.0100 | 94 | 0 | 0.0000 | 19 |

## Interpretation

O1 defines a route-stop false positive as a declared route stop while at least one previously unfound gold identity remains reachable on that route and at least one route-call budget unit remains. It defines a route-stop false negative as **more than one** attempt after the gold-defined oracle exhaustion point; one confirming attempt is explicitly allowed.

Full ORION records 1 O1 route-stop FP in 100 route-stop events (0.0100) and 0 FN over 99 routes that reach oracle exhaustion. The single FP is the frozen unavailable `RESTRICTED` case. That route has 19 exhaustible task-routes and 19 total post-exhaustion attempts: exactly one allowed confirming attempt on each of the 19 non-censored tasks, so none is an FN.

The route-level FP does **not** become a task-level false closure: O4 opens an unresolved obligation for the unavailable restricted route, and full ORION returns `CANNOT_CHECK` instead of asserting task completeness. This is the intended separation between route stopping and task stopping.

Source record digest: `611808dc80846d5057c84c12af7ff8ec3fa88ef15a6ede91807e590f4edb6f1f`  
Source rich-artifact hash-list digest: `2da59dc21e6473e4a81eb93910501a67bed008dbc3e29c26116041b68dfbb325`
