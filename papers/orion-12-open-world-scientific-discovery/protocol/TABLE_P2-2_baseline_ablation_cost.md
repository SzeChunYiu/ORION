# Table P2-2: Baselines and ablations with cost metrics

<!-- GENERATED FILE - DO NOT EDIT BY HAND.
     Regenerate with:
       python3 papers/orion-12-open-world-scientific-discovery/scripts/render_table_p2_2.py
     Sources: evidence/offline_results/RESULTS_SUMMARY_V1.json
              protocol/OFFLINE_RUN_MANIFEST_V1.json -->

## Metadata

| Field | Value |
| --- | --- |
| Analysis authority | `TIER_B_committed` |
| Tasks (n) | 390 |
| Systems (total) | 14 |
| Result records | 16380 |
| Results SHA256 | `c6430a651810f8e7a794aa0c10917949…` |

## Resource limits (per-task budgets)

| Resource | Limit |
| --- | --- |
| Max model tokens | 120000 |
| Max route calls | 12 |
| Max tool calls | 48 |
| Max wall-clock seconds | 120.0 |

## Confirmatory baselines

| System | Recall | Premature closure | Duplicate processing | Routes used | Legitimate rereads | Pass | Cannot check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Protocol-driven systematic review | 0.666667 | 1.0 | 0.0 | 3.0 | 0.6 | 0.0 | 0.0 |
| Sparse+dense hybrid | 0.555556 | 1.0 | 0.0 | 2.0 | 1.6 | 0.0 | 0.0 |
| One-pass RAG | 0.555556 | 1.0 | 0.0 | 2.0 | 1.6 | 0.0 | 0.0 |
| BM25/keyword | 0.333333 | 1.0 | 0.0 | 1.0 | 0.6 | 0.0 | 0.0 |
| Dense-route comparator | 0.333333 | 1.0 | 0.0 | 1.0 | 1.6 | 0.0 | 0.0 |
| Agentic single route | 0.333333 | 1.0 | 0.0 | 1.0 | 0.6 | 0.0 | 0.0 |

## Full ORION

| System | Recall | Premature closure | Duplicate processing | Routes used | Legitimate rereads | Pass | Cannot check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ORION full | 0.979487 | 0.0 | 0.0 | 4.989744 | 1.533333 | 0.666667 | 0.182051 |

## Safety ablations

| System | Recall | Premature closure | Duplicate processing | Routes used | Legitimate rereads | Pass | Cannot check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ablation: no route-independence check | 0.444444 | 1.0 | 0.0 | 2.0 | 0.6 | 0.0 | 0.0 |
| Ablation: no question-conditioned read ledger | 0.979487 | 0.0 | 0.0 | 4.989744 | 1.0 | 0.666667 | 0.182051 |
| Ablation: route stop can close task | 0.333333 | 1.0 | 0.0 | 1.0 | 0.6 | 0.0 | 0.0 |
| Ablation: no unavailable-route open state | 0.979487 | 0.0 | 0.0 | 4.989744 | 1.533333 | 0.666667 | 0.0 |
| Ablation: coverage diagnostic controls stopping | 0.555556 | 1.0 | 0.0 | 2.0 | 1.6 | 0.0 | 0.0 |
| Ablation: no content-identity dedup | 0.939031 | 0.0 | 0.31453 | 4.969231 | 1.235897 | 0.369231 | 0.135897 |

## Exploratory comparator (non-confirmatory)

| System | Recall | Premature closure | Duplicate processing | Routes used | Legitimate rereads | Pass | Cannot check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Exploratory: adaptive multiroute | 0.774074 | 0.758974 | 0.0 | 4.0 | 1.6 | 0.0 | 0.2 |

## Interpretation

- Authority: `TIER_B_committed` — no inferential claims are made from this n=390 offline campaign.
- Strongest confirmatory baseline: `protocol_driven_systematic_review` with recall 0.666667.
- ORION full recall advantage: +0.31282 over strongest baseline.
- ORION full premature-closure advantage: -1.0 (negative = fewer premature closures).
- Cost metrics (routes used, legitimate rereads) are descriptive resource consumption from the frozen offline companion; wall-clock is intentionally fixed to zero, so these reflect algorithmic behavior, not empirical time.
