# Paper 02 — Open-World Scientific Knowledge Discovery

**Status:** ACTIVE RESEARCH / IMPLEMENTATION AHEAD OF MANUSCRIPT / EMPIRICAL SUPERIORITY NOT ESTABLISHED

## Scoped claim

ORION studies scientific-literature discovery as a separate capability from synthesis.  The candidate contribution is the combination of earned route independence, question-framed read memory, route-vs-task stopping, fail-closed coverage diagnostics and recall-first promotion against strong simple baselines.

## Nearest-work boundary

Scientific RAG, agentic literature search and capture-recapture are not claimed as novel.  The current comparison absorbs mechanisms from ResearchArena, AutoResearchBench, MetaSyn, OpenScholar and systematic-review/capture-recapture research.

See `research/paper-programme-v1/PAPER_02_OPEN_WORLD_DISCOVERY.md` and `NEAREST_WORK_ATLAS.md`.

## Required evidence before manuscript claims

- frozen ResearchArena/AutoResearchBench/MetaSyn-compatible evaluations where licensing/access permits;
- matched BM25/keyword and one-pass retrieval baselines;
- content-identity and route-independence hostile cases;
- route-stop versus task-stop errors measured separately;
- recall/lost-evidence results reported whenever the gold set is complete;
- unavailable routes/resource censoring remain OPEN/CANNOT_CHECK rather than closure.

Current retrieval/ledger/route-control/research-packet code is implementation evidence only; it does not establish that ORION discovers more literature than simpler systems.
