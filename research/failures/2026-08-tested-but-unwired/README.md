# Shipping tested modules that nothing calls

**Observed:** 2026-08-16, measured against my own session output.

## Original measurement

Production consumers, excluding the module itself, its tests, and `__init__`
re-exports:

```
knowledge/space.py           0        kernel/hard_gates.py     0 -> 1 (driver stop path, same day)
knowledge/research_loop.py   0        kernel/workorder.py      1
knowledge/ingest.py          0        kernel/report.py         1
knowledge/local.py           0        knowledge/evaluation.py  1
knowledge/rate.py            0
```

**Six of fifteen modules added this session had no caller in the production
path.** All fifteen had tests. All fifteen had merged green.

## Failure class

`TESTED_BUT_UNWIRED` — the same defect this repository documents in its
provenance source and which I cited repeatedly while committing instances of it:
`MetricDirection.NON_COMPENSATORY_GATE` as an enum nothing branched on,
`AuthorityTransport` with only a test consumer, `related_failure_episodes`
computed and never consulted, `evolution_archive.py` ported faithfully and never
called. The audit rule I applied to RAKL — *a name with no consumer is ABSENT* —
marks an isolated tested module ABSENT as capability.

## Root cause, one level down

A green suite was treated as the completion signal. It is not: a test proves a
module behaves as specified in isolation, and says nothing about whether any
path reaches it. The two failure modes look identical in CI and are opposite in
value.

The incentive compounds it. Adding a module with its own tests always merges
green, because it cannot break anything that does not call it. Wiring a module
into the driver risks breaking the suite. So the cheapest-looking step is always
the one that adds surface without adding capability, and repeating it produces
exactly this repository's characteristic defect.

## Guard

A module is not done when its tests pass. It is done when something on the
production path calls it, and a test exercises it *through* that path.

Concretely, before opening a new module: name the caller. If the caller does not
exist yet, build the caller first and let it fail for want of the module — the
same discipline as writing the failing test first, applied one level up.

For review: `grep -rl "from \.<module>" src/ | grep -v __init__ | grep -v <module>.py`
returning nothing is a blocking finding, not a style note.

## Resolution: Shadow production wiring

The remaining five knowledge modules are now reached through the proposal-only
Shadow Self-ORION research path rather than being inventory:

```
knowledge/space.py           0 -> 1  self_orion/knowledge_runtime.py
knowledge/research_loop.py   0 -> 1  self_orion/knowledge_runtime.py
knowledge/ingest.py          0 -> 1  knowledge/research_loop.py
knowledge/local.py           0 -> 1  knowledge/searchers.py
knowledge/rate.py            0 -> 1  knowledge/searchers.py
kernel/hard_gates.py         0 -> 1  runtime driver stop path
```

The wiring is functional rather than import-only:

- `ShadowSelfOrionResearchLoop` optionally invokes `ShadowKnowledgeRuntime` for
  an empirical frontier item.
- `ShadowKnowledgeRuntime` runs the multi-route research loop and traverses the
  structured `KnowledgeSpace`.
- the research loop sends every retrieved rendition through the generic durable
  ingestion edge, producing SOURCE/READ ledger receipts under a question frame;
- `LocalCorpusSearcher` uses the content-addressed local corpus index as a route
  backend;
- `ArxivRouteSearcher` uses the repository `RateGate` before transport and the
  same gate records the provider request/Retry-After state after transport.

`tests/unit/self_orion/test_shadow_knowledge_wiring.py` exercises that complete
path from Shadow work selection through local + arXiv route search, multi-route
packet construction, durable ingest/read receipts, structured-space traversal,
and proposal-only Self-ORION output. The test also asserts the live arXiv route
consumes the configured three-second provider spacing budget.

This resolution does **not** convert retrieval into scientific authority. The
Shadow result remains proposal-only, the normal runtime may return
`CANNOT_CHECK`, and retrieved/structured-space evidence cannot self-promote a
change. Live-provider performance and independent evaluator evidence remain
Phase-2 empirical gates rather than being inferred from this wiring test.
