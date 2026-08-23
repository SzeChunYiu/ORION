# P12 unchanged-allocator cross-domain transfer protocol V1

**Programme:** #977
**Purpose:** close the open P12 transfer gate — one frozen allocator, defined with no domain-specific parameter, applied unchanged across three qualitatively distinct exact domains — and bind the unified I/A/C/M resource-vector ontology to the same study so P9 and P12 accounting compose.

## Scientific object

The 2025–26 adaptive test-time-compute lane allocates within the reason/inference locus. None of its allocators can transfer across construction/reasoning loci because they possess no second locus. The discriminating evidence for P12's upward claim is therefore not another within-domain win: it is **one unchanged allocation rule exhibiting bounded (target: zero) regret against a per-case hindsight oracle in every domain, while each single-locus restriction policy (the donor family) is strictly suboptimal somewhere**.

## Frozen allocator (identical bytes in every domain)

`P12_TRANSFER_ALLOCATOR_V1` uses exactly three pre-outcome signals and no others:

1. `q_i` — pending query multiplicity of reusable structure `i` (a count, dimensionless);
2. `c_i` — declared construction cost of structure `i` in frozen abstract units (declared in the case file before any execution; a structural property, not an outcome);
3. `B` — frozen abstract secondary budget, `500` units.

Rule:

- a structure is *materializable* if `q_i >= tau` with `tau = 4`;
- among materializable structures, materialize in decreasing `q_i` while cumulative declared cost `<= B` (ties by frozen case order);
- queries on a materialized structure are served from the state locus (`STATE`); all other queries are served by fresh per-query computation (`REASON`).

`tau`, `B`, the rule and the signal set are frozen before execution and are byte-identical across all three domains. The allocator performs no per-domain tuning, fitting or calibration.

## Arms

1. `P12_TRANSFER_ALLOCATOR_V1` — the unchanged rule above.
2. `REASON_ONLY` — never materializes; the reason-locus restriction (donor family locus).
3. `STATE_ALWAYS` — materializes every structure with `c_i <= B`, ignoring `q_i`; the construction-locus restriction.
4. `ORACLE_LOCATION` — diagnostic only; per case, selects the locus assignment minimizing realized charged operations in hindsight (exhaustive over structures, budget-respecting). Grants no policy-selection authority.

## Domains

All three are exact, deterministic and stdlib-only. Every arm must produce identical verified outputs; only placement of work differs.

- **SAT-propagation domain.** Structures are frozen 3-CNF formulas. A query is the unit-propagation closure of a frozen literal set. `REASON` runs naive fixpoint propagation per query (operation = clause examination). `STATE` materializes a watch index in one pass over clauses (declared cost = clause count) and serves closures from it. Independent verification: from-scratch exhaustive rescanning fixpoint computation of the closure.
- **Path domain.** Structures are goals on frozen grids (15x15, 4-neighbour, unit cost; the four obstacle families of the procedural study). A query is a shortest path from a start to the goal. `REASON` runs a fresh BFS per query. `STATE` materializes the reverse-distance state from the goal (declared cost = 225 cell expansions) and answers by descent. Independent verification: bidirectional BFS distance plus per-edge legality.
- **Knapsack domain.** Structures are frozen item sets (`n <= 16`, integer weights/values). A query is an exact optimum for a frozen capacity. `REASON` fills a per-query DP table (operation = cell fill). `STATE` materializes the DP table for the declared maximal capacity once (declared cost = `n * C_max` fills) and answers by row lookup. Independent verification: exhaustive `2^n` enumeration of the exact optimum.

Case files freeze every formula, grid, item set, literal set, start/goal pair, capacity, declared cost and query multiplicity before any runner exists. Beneficial (`q >= 4`) and non-beneficial (`q < 4`) regimes are present in every domain. At least one case per domain contains multiple competing structures so the budgeted greedy ordering is exercised.

## Unified resource vector

Every arm-case cell emits the P9 ledger field names so P9/P12 accounting compose:

`R = (I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit, R_registered)`

- `I_sem`: semantic information coordinates exposed to the arm (clause-literal occurrences / grid edges / item bits);
- `A_dim`: representation dimension of the materialized or delivered state;
- `A_transform`: construction/transform touches (watch-index passes, reverse-BFS expansions, DP-table fills);
- `M_state`: learned model-state coordinates — identically zero; no P12 locus is learned;
- `C_fit`: fit touches — identically zero (no learned access mechanism);
- `C_infer`: per-query serving work (indexed propagation examinations, query BFS expansions, row lookups);
- `C_explicit`: independent verification operations, reported separately and never hidden;
- `R_registered`: the frozen abstract charged unit the allocator protocol registers (clause examinations / BFS expansions / DP cell fills per domain convention, declared here, before execution).

Vectors are primary; the scalar budget `B` is a secondary diagnostic only. No universal scalar exchange rate across domains is claimed.

## Frozen endpoints

The study terminal `P12_TRANSFER_ALLOCATION_V1_SUPPORTED` requires all of:

- **G1 exactness:** every query output in every arm equals the independent verifier's output in all three domains.
- **G2 zero transfer regret:** `P12_TRANSFER_ALLOCATOR_V1` realized charged operations equal the hindsight oracle's in every case (regret `0` per case).
- **G3 restrictions fail somewhere:** `REASON_ONLY` has strictly positive regret in at least one case in every domain, and `STATE_ALWAYS` has strictly positive regret in at least one case in at least two domains.
- **G4 accounting completeness:** all eight vector fields present for every arm-case cell; `M_state` and `C_fit` identically zero and explicitly reported.
- **G5 determinism:** byte-identical replay.
- **G6 allocator identity:** the emitted allocator parameters (`tau`, `B`, rule tokens) are asserted equal across domains inside the run.

If any gate fails, the terminal records the failure honestly; no post-hoc protocol edit may convert it.

## Non-claims

This study does not establish universal allocation optimality, does not cover open-weight LLM workloads (the refresh names that as a further strengthening cell, not a blocker for this gate), and does not convert heterogeneous resource coordinates into one scalar. `ORACLE_LOCATION` remains diagnostic.

## Artifacts

- protocol: `P12_TRANSFER_ALLOCATION_PROTOCOL_V1.md` (this file)
- frozen cases: `p12_transfer_cases_v1.json`
- runner: `run_transfer_allocation_v1.py`
- independent verifier: `check_transfer_allocation_independent_v1.py`
- workflow: `.github/workflows/p12-transfer-allocation-v1.yml`
- receipt (post-success only): `P12_TRANSFER_ALLOCATION_RESULT_RECEIPT_V1.md`
