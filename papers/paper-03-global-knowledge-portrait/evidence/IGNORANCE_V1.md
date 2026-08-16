# Typed scientific ignorance V1

This evidence packet belongs to Paper III's source-projection/knowledge-portrait boundary and to the general ORION search/reframing controller.

## Representation

`IgnoranceProjection.v1` records one source-local statement that knowledge is missing, incomplete, disputed, anomalous, blocked or proposed as future work. It preserves the source span, original taxonomy label and implied knowledge goal.

Constitutional boundary: a source-local ignorance statement is **not** proof of a globally real/current gap. `asserts_global_gap` is fixed false; every derived action plan requires independent confirmation and creates no scientific authority.

## Frozen action discriminator

`src/orion/benchmarks/ignorance.py` contains exact cases for:

- incomplete evidence -> `SEARCH_EVIDENCE`;
- competing explanations -> `DESIGN_DISCRIMINATOR`;
- anomalous observation -> `REPLICATE_OR_EXPERIMENT`;
- research/instrument barrier -> `REPAIR_RESEARCH_BARRIER`;
- future-work proposal -> `RETAIN_FUTURE_WORK_CANDIDATE` + freshness route.

A generic missing-gap controller always selects evidence search and therefore fails most of the frozen cases. The typed controller must reach 1.0 action accuracy and strictly exceed that baseline.

Independent sources making the same ignorance statement remain separate source projections; only an exact duplicate from the same source/span/context is deduplicated.

## Empirical-open coordinates

- text-to-ignorance extraction precision/recall;
- usefulness of the action taxonomy on fresh research tasks;
- whether additional source taxonomy classes materially change next actions;
- whether richer ignorance typing improves search/reframe/experiment outcomes relative to generic residuals;
- false activation rate when source future-work statements are already resolved by newer evidence.
