# P15 State Optionality / Compile-Cache-Materialize Phase Diagram — Protocol V1

Status: PROSPECTIVE / FROZEN BEFORE P15 RESULT GENERATION
Frozen: 2026-08-20

## Question

Given a state that may face a sequence of future queries, when should a system:
- compile only the current query-specific state;
- cache components as they are requested;
- retain raw state and recompile on demand; or
- materialize a universal query-ready state in advance?

The question is not whether caching or specialization exists. The object is a representation-resource phase diagram with accessibility, recoverability and optionality accounted separately.

## Controlled workload model

There are N independent query components. Each future query asks for one component.

Frozen N values: `128, 512, 2048`.

Query horizons K are expressed relative to N:
`0.05N, 0.10N, 0.25N, 0.50N, 1N, 2N, 4N, 8N`, rounded to at least one query.

Frozen query distributions:
1. `UNIFORM`;
2. `ZIPF_1_1`: p_i proportional to i^-1.1;
3. `ZIPF_1_5`: p_i proportional to i^-1.5.

For independent queries with probabilities p_i, expected distinct requested components after K queries are

`D(K)=sum_i [1-(1-p_i)^K]`.

For uniform p_i=1/N this reduces exactly to

`D(K)=N[1-(1-1/N)^K]`.

## Policies

### E0 — `EPHEMERAL_COMPILE`
Raw/source state is available for every query. Compile the requested component each time and discard it afterward.
- expected compile work: K isolated-component units;
- materialized component memory: 1;
- first-query/miss fraction: 1.

### E1 — `COMPILE_AND_CACHE`
Compile a component on first request, then retain it.
- expected compile work: D(K);
- expected component memory: D(K);
- expected first-occurrence/miss fraction: D(K)/K.

### E2 — `UNIVERSAL_MATERIALIZE`
Materialize all N components before queries.
- memory: N;
- future miss fraction: 0;
- compile work: beta*N, where beta represents prespecified batch/shared-computation efficiency relative to isolated compilation.

Frozen beta values: `0.25, 0.50, 0.75`.

Beta is a controlled systems parameter, not an empirical claim about a particular implementation.

### O0 — `COMPILED_ONLY_SOURCE_GONE`
After a current r-component task is compiled, the raw source disappears. Future exact query coverage is only the retained component set.

Frozen r values: `1, 5, 16` where r<=N.

### O1 — `RAW_PLUS_COMPILED`
Retain raw source plus current compiled state. Future query coverage is 1 if the compiler remains valid, but every previously unseen query may incur compilation work.

### O2 — `UNIVERSAL_READY`
Retain universal query-ready state. Future immediate query coverage is 1 with no recompilation, at N-component memory.

## Metrics

For E0/E1/E2:
- expected compile work;
- expected materialized component count;
- expected miss fraction;
- Pareto dominance in `(compile_work, component_memory)`;
- crossover horizon where universal compile work first becomes lower than expected cache compile work for each beta.

For O0/O1/O2:
- immediate future-query coverage;
- recoverable future-query coverage;
- retained component/raw-state burden;
- recompilation requirement.

## Protected expected findings / gates

The result terminal `P15_STATE_OPTIONALITY_PHASE_DIAGRAM_ESTABLISHED` requires all mathematically checkable gates:

1. uniform D(K) computed both by the closed form and general sum agree within `1e-12`;
2. at low horizon K<=0.10N, cache has both lower compile work and lower component memory than universal materialization for beta>=0.25;
3. at high horizon K>=4N, for beta=0.50 universal has lower compile work than cache while cache retains lower expected memory, producing a genuine Pareto tradeoff rather than one policy universally dominating;
4. the universal/cache compile-work crossover occurs earlier for beta=0.25 than beta=0.50, and earlier for beta=0.50 than beta=0.75;
5. at K=N, expected distinct fraction under ZIPF_1_5 is smaller than under ZIPF_1_1, which is smaller than under UNIFORM, demonstrating workload concentration shifts the phase boundary;
6. O0 immediate future coverage equals r/N exactly for every frozen r,N pair;
7. O1 and O2 both have recoverable coverage 1, while only O2 has immediate no-recompile coverage 1;
8. deterministic output byte-identical across two executions.

No thresholds may be changed after result generation.

## Claim boundary

A positive controlled result supports a systems design law for this explicit query-workload model, not a universal theorem about all memory architectures. Query distributions, compiler costs, shared computation and storage hardware can change the optimum.

The intended real-system escalation is to estimate analogous resource points for LLM agent context and Lean proof-state workloads with exact token/tool/verifier accounting.
