# P11C Multi-Query Union Compilation Protocol V1

Status: **FROZEN BEFORE OUTCOME**  
Date: 2026-08-20  
Parent atom: `F0.P11.MULTIQUERY`

## Question

When one state must service a *batch* of queries, how does the union/rank of query-relevant latent coordinates control the break-even point between per-query compilation and universal state materialization?

This is not a claim that multi-query optimization or materialized views are new. Knowledge compilation, database view selection, caching, and partial evaluation are mandatory parents.

## Controlled family

- latent world `x in {-1,+1}^20`;
- latent component bank: all size-3 parity coordinates, `N = C(20,3) = 1140`;
- each query selects `r=5` distinct parity components and asks for the majority sign of those five;
- final label is **not** itself an exposed feature;
- query batches `B in {1,4,16,32}`;
- within the primary disjoint regime, component sets of distinct queries are disjoint, so the compiled union dimension is exactly `5B`;
- secondary overlap regime uses a prospectively fixed shared-core construction and is descriptive only.

## Arms

1. `PER_QUERY_5D` — compile only the five components required by the active query; lower-bound/oracle interface.
2. `BATCH_UNION` — compile the union of components needed by all queries in the batch; the same state is reused by all query-specific downstream learners.
3. `UNIVERSAL_1140D` — materialize all parity components.
4. `RAW_20D` — original raw signs, linear learner negative control.

The downstream learner is identical L2 logistic regression for every query/arm. Query-specific models are allowed because the object under study is the shared state interface, not a universal decoder.

## Fresh execution

- master seed: `914401`;
- independent batch seed per B derived from the master seed;
- 16 query batches per B;
- train sizes: `64,128,256,512,1024,2048`;
- test cases per batch: `8192`;
- no hyperparameter tuning on protected outcomes.

## Protected checks

- no exposed coordinate equals or negates a final majority label on all protected cases;
- union cardinality equals exact set union of query components;
- `PER_QUERY_5D` must be >=0.99 at all train sizes;
- `BATCH_UNION` must be >=0.95 by 2048 for every B;
- raw linear at 2048 must remain <=0.65;
- for B in {16,32}, batch-union state dimension must be < universal dimension and its 0.95 sample threshold must be no worse than universal;
- canonical replay excludes wall-clock timing and must be byte-identical across two fresh processes.

## Interpretation

A positive result establishes only a controlled **query-set rank/union frontier**: state size can scale with the set of responsibilities actually required rather than the entire universal query family. It does not establish novelty of multi-query optimization, a universal cache policy, or LLM/Lean benefit.
