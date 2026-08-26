# ORION-22 procedural path-allocation protocol V1

**Programme:** #977  
**Purpose:** test Resource-Location Metareasoning in a second domain qualitatively different from SAT: repeated shortest-path queries on fixed grids.

## Scientific object

For a fixed grid and goal, the same total computation may be placed in two loci:

- **STATE_FIRST:** construct a reusable reverse-distance/predecessor state once from the goal, then answer every start query from that state;
- **REASON_ONLY:** construct no reusable state and run a fresh BFS from each start to the goal.

The adaptive policy chooses the locus from a pre-outcome structural signal: number of queries sharing the same goal.

## Frozen allocation policy

`ADAPTIVE_LOCATION` chooses:

- `REASON_ONLY` when query count `< 4`;
- `STATE_FIRST` when query count `>= 4`.

This threshold is frozen before execution and is not tuned from protected work counts.

## Grids

All grids are `15 x 15`, 4-neighbour motion, unit edge cost. Case data freezes one of these prospectively defined obstacle patterns:

- `OPEN`: no blocked cells;
- `CENTER_GATE`: block `(7,y)` for all `y != 7`;
- `DOUBLE_GATE`: block `(5,y)` for all `y != 3` and `(10,y)` for all `y != 11`;
- `HORIZONTAL_GATE`: block `(x,8)` for all `x != 4`.

Start/goal coordinates are frozen in `p12_procedural_path_cases_v1.json` before runner/scorer implementation. Starts/goals are never blocked.

## Arms

1. `REASON_ONLY` — BFS independently per query.
2. `STATE_FIRST` — one complete reverse BFS from goal; answer queries by monotonically following decreasing exact distance.
3. `ADAPTIVE_LOCATION` — frozen threshold policy above.
4. `ORACLE_LOCATION` — diagnostic only; chooses lower realized expansion cost after both policies are evaluated. It grants no policy-selection authority.

## Resource vector

Record separately:

- `state_construction_expansions`;
- `query_search_expansions`;
- `materialized_distance_cells`;
- `path_output_edges`;
- `verification_edge_checks`;
- `total_expansions = state_construction_expansions + query_search_expansions`.

No preprocessing/search coordinate is free.

A scalar expansion budget of `500` is frozen only as a secondary matched-budget diagnostic. Vector/Pareto reporting remains primary.

## Exact verifier

For every returned path independently verify:

- starts/ends at requested nodes;
- every consecutive pair is a legal unblocked 4-neighbour edge;
- no blocked cell occurs;
- path length equals the exact shortest distance from an independent BFS.

An arm that exceeds the 500-expansion diagnostic budget is recorded as budget-exhausted even if an unrestricted run later finds paths.

## Case design

Freeze both non-beneficial and beneficial regimes:

- `Q=1` and `Q=2` cases place starts near enough to the goal that repeated local BFS is expected to be cheaper than full state construction;
- `Q=8` and `Q=12` cases distribute starts across the grid so reusable state construction is expected to amortize and may prevent budget exhaustion.

Every obstacle family appears in both low- and high-query regimes.

## Endpoints

- exact verified solve rate;
- total expansion vector by arm/case;
- state-construction vs query-search placement;
- budget exhaustion count;
- adaptive regret vs diagnostic oracle;
- correct regime selection rate;
- non-beneficial low-query controls;
- state memory / path verification cost;
- deterministic replay.

## Positive terminal

`P12_PROCEDURAL_PATH_ALLOCATION_V1_SUPPORTED` requires:

- every non-exhausted returned path independently verifies as shortest;
- adaptive chooses the oracle-optimal locus in at least `7/8` frozen cases;
- adaptive total expansion cost is strictly lower than both fixed policies in aggregate;
- at least one low-query case demonstrates STATE_FIRST unnecessary overhead;
- at least one high-query case demonstrates REASON_ONLY higher work or budget exhaustion;
- adaptive has no more budget exhaustions than either fixed policy;
- vector resource accounting is complete for every case;
- deterministic byte replay.

A positive supports cross-domain resource-location allocation (SAT + procedural path planning). It does not establish a universal allocator or open-weight LLM transfer.
