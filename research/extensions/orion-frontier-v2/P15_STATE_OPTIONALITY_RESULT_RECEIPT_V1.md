# P15 State Optionality Phase Diagram — Controlled Result Receipt V1

Terminal: `P15_STATE_OPTIONALITY_PHASE_DIAGRAM_ESTABLISHED`

Protocol: `P15_STATE_OPTIONALITY_PHASE_DIAGRAM_PROTOCOL_V1.md`
Theorem: `THEOREM_STATE_OPTIONALITY_COVERAGE_V1.md`

This result is a deterministic evaluation of the frozen workload equations, not a learned-model benchmark.

## Exact checks

- General expected-distinct sum and uniform closed form agree exactly at all frozen cells (max absolute difference `0`).
- At horizons <=0.10N, compile-and-cache has lower expected compile work and lower component memory than universal materialization for every frozen beta `0.25,0.50,0.75`.
- At horizons >=4N with beta=0.50, universal materialization has lower compile work while cache retains lower expected memory: neither policy dominates in both resources.

## Uniform universal/cache crossover

The first frozen horizon where universal bulk compile work becomes lower than expected cache compile work is identical across N=`128,512,2048`:

| beta | first frozen crossover horizon |
|---:|---:|
| 0.25 | 0.50N |
| 0.50 | 1.00N |
| 0.75 | 2.00N |

These are grid-level phase locations under the frozen workload, not continuous exact roots.

## Query concentration at K=N

Expected fraction of distinct requested components:

| N | uniform | Zipf 1.1 | Zipf 1.5 |
|---:|---:|---:|---:|
| 128 | 0.63356 | 0.36209 | 0.21786 |
| 512 | 0.63248 | 0.30321 | 0.14478 |
| 2048 | 0.63221 | 0.25735 | 0.09506 |

Thus highly concentrated query workloads preserve a much smaller cache footprint and postpone the regime where universal state materialization is attractive.

## Optionality / recoverability

For compiled-only state retaining r of N independent query components after the raw source disappears, immediate/recoverable future uniform single-query coverage is exactly `r/N`.

For `N=2048`:
- r=1: coverage `0.00048828125`;
- r=5: coverage `0.00244140625`;
- r=16: coverage `0.0078125`.

Retaining raw source plus compiled state preserves recoverable coverage `1.0` but requires recompilation for uncached future queries. Universal-ready state has immediate coverage `1.0` with no recompilation at N-component memory.

## Strongest bounded interpretation

> Current-task accessibility, future-task optionality, and recoverability are distinct state resources. Query-specific compilation can minimize current accessible state, but if the source disappears it creates predictable future-query option debt; retaining raw state buys recoverability at future compilation cost, while universal materialization buys immediate future coverage at memory/upfront-compute cost. The preferred policy changes with query horizon, workload concentration and batch compilation efficiency.

This is an exact controlled workload result, not a universal law for all agent-memory implementations.
