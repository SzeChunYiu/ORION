# ORION-22 procedural path-allocation result receipt V1

**Run:** GitHub Actions `32657074186`  
**Artifact:** `p12-procedural-path-allocation-v1`, artifact ID `9498183456`  
**Artifact ZIP SHA-256:** `a31f8da71b0bc766bbf3d69d9e16edfe294e24638719ec89ca0f3fb4b898a3ec`  
**Terminal:** `P12_PROCEDURAL_PATH_ALLOCATION_V1_SUPPORTED`  
**Replay:** `P12_PROCEDURAL_PATH_ALLOCATION_V1_BYTE_REPLAY_GREEN`

## Exact binding

- protocol SHA-256: `10ce1c86aa4f9e43ef53f8e545369974d602a23941ac5dacfa9e8c9d4bf04791`
- frozen cases SHA-256: `c00215a95301dcee575b0724cdb14c658eba887f7527c21832a87f399aed78a2`
- receipt SHA-256: `69047eabab92f72355bfb1930fc4dd4ce61b4050003187321d4534e56ff09b46`
- case count: `8`
- adaptive/oracle locus agreement: `1.0`

## Protected result

The frozen procedural domain contains repeated shortest-path queries over four graph-pattern families with low- and high-query-count regimes. Every reported path is checked against the exact shortest-path verifier.

Aggregate verified output is identical across the three arms (`46` verified paths each), while resource placement differs sharply:

| arm | total expansions | budget exhaustions | verified paths |
|---|---:|---:|---:|
| ADAPTIVE_LOCATION | 858 | 0 | 46 |
| REASON_ONLY | 7,024 | 4 | 46 |
| STATE_FIRST | 1,688 | 0 | 46 |

The frozen allocator uses only the pre-outcome query-count signal. It selects `REASON_ONLY` in every low-query case and `STATE_FIRST` in every high-query case. These selections match the post-outcome oracle in all `8/8` cases, with zero observed allocation regret.

The non-beneficial regime is explicit: for one- or two-query cases, state materialization costs roughly 197–225 expansions while direct query search costs only 2–5 expansions. In high-query cases, the same reusable state construction costs roughly 197–225 expansions while repeated search costs 1,190–2,273 expansions and can exceed the frozen budget.

## Scientific disposition

Together with the existing verifier-backed SAT result, ORION-22 now has two qualitatively distinct executable domains showing the same higher phenomenon: fixed total resources are not enough to characterize performance; **where** the computation is placed can change the verified quality-cost frontier, and a pre-outcome signal can select the useful locus.

This does not establish universal allocation optimality or an open-weight LLM result. It does materially strengthen the cross-domain Resource-Location Metareasoning claim beyond the original scalar controlled world.
