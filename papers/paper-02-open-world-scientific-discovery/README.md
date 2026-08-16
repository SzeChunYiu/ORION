# Paper 02 — Open-World Scientific Knowledge Discovery

**Stable ID:** ORION-P2  
**Status:** STRUCTURED WORKING MANUSCRIPT / LOCAL FALSIFIER V1 PASSED / EXTERNAL RECALL CLAIM `CANNOT_CHECK`

## Scoped claim

ORION studies scientific-literature discovery as a separate capability from synthesis. The candidate contribution is the combination of earned route independence, question-framed read memory, route-vs-task stopping, fail-closed coverage diagnostics and recall-first promotion against strong simple baselines.

## Nearest-work boundary

Scientific RAG, agentic literature search, systematic-review automation and capture-recapture are not claimed as novel. The comparison now explicitly includes ResearchArena, AutoResearchBench, SAGE, MetaSyn, AgentSLR, OpenScholar and systematic-review/capture-recapture research.

See `research/paper-programme-v1/PAPER_02_OPEN_WORLD_DISCOVERY.md`, `NEAREST_WORK_ATLAS.md`, `JOURNAL_READINESS_AUDIT_2026-08-16.md`, and this directory's `JOURNAL_READINESS.md`.

## Falsifier V1

A complete-gold local retrieval world plus hostile route/coverage cases exercise the promotion contract. The suite requires a same-call lexical baseline, refuses independence for shared backends, refuses bounded unseen-population claims under zero overlap, deduplicates route re-encounters by content, rejects single-target pseudo-recall and keeps coverage diagnostics non-authoritative.

Evidence: `evidence/FALSIFIER_V1.md` and `research/paper-programme-v1/FLAGSHIP_FALSIFIER_RESULTS_V1.md`.

## External evidence still required

- frozen AutoResearchBench Wide/Deep, SAGE and MetaSyn-compatible evaluations where licensing/access permits;
- matched BM25/keyword, dense, hybrid and agentic retrieval baselines;
- frozen provider/search trajectories plus an offline controlled-index companion;
- route-stop versus task-stop errors measured separately;
- recall/lost-evidence results only where the gold denominator is legitimate;
- search-time contamination accounting for public benchmarks;
- unavailable routes/resource censoring remain `OPEN/CANNOT_CHECK` rather than closure.

Current retrieval/ledger/route-control/research-packet code and the local falsifier establish implementation semantics only; they do not establish that ORION discovers more literature than simpler systems.

## Manuscript

`manuscript/main.tex` is now the canonical structured Paper-II working manuscript. Its Results section deliberately remains external-evidence open rather than inventing benchmark outcomes.
