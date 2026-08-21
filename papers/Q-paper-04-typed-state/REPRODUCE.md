# Q4 — reproducing the six-family mechanism study

## Primary receipts

Under `research/extensions/orion-q/nlanes/` verify:

- `N4_A_UNKNOWN_VOI_RESULTS.json`
- `N4_B_STALE_RECEIPT_REOPENING_RESULTS.json`
- `N4_C_INTERVAL_PARETO_RESULTS.json`
- `N4_D_LAUNDERING_DETECTION_RESULTS.json`
- `N4_E_ACTIVE_EXPERIMENTS_RESULTS.json`
- `N4_F3_REMINT_TRANSPORT_RESULTS.json`

The corresponding protocols under `development/orion-q-nlane-closure/` must predate their result-bearing runs.

## Reproduction order

1. verify protocol hashes/seeds and terminal vocabulary;
2. re-run each deterministic world/arm generator;
3. compare the canonical receipt line and result JSON to the committed artifact;
4. independently recompute the headline comparator metric and the hostile-control validity gate;
5. confirm every non-oracle arm receives the same serialized visible state inside that family;
6. verify the negative families N1-C and N2-F5B separately rather than pooling them with the six positives.

The replay ledger covers the core N-lane receipts; N4-F3 should be checked under the same byte/canonical-equality rule.

## Non-equivalences to preserve

- `LLM_PROXY_HEURISTIC` is a deterministic heuristic and must not be relabeled as a real-LLM benchmark.
- N4-D's seeded hashes are construction identifiers, not cryptographic security.
- N4-C scalarized regret is not Pareto-front hypervolume.
- an oracle comparator is a reference bound, not an admissible deployable baseline.
- N1-C supports typed failure state while explicitly closing the allocation-policy claim against ideal VOI.
- N2-F5B is donor-absorbed on the original world.

A replay that changes a hostile world after observing a shortcut's performance is invalid.