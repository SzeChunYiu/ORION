# Paper Card — STALE

**Source mode:** primary arXiv record/abstract.  
**Context mode:** targeted current-donor check.  
**Checked:** 2026-08-21.

## 01. Bibliographic position
Hanxiang Chao, Yihan Bai, Rui Sheng, Tianle Li, Yushi Sun. **STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?** arXiv:2605.06527 (2026).

## 02. Research question
Can LLM agents detect when stored memories have become invalid because later observations implicitly conflict with them, and can they propagate that update into downstream behavior?

## 03. Background route
Long-term agent memory benchmarks commonly emphasize retrieval of stored facts. STALE targets dynamic state revision, particularly implicit conflicts that do not explicitly negate the old memory.

## 04. Prior-work / field context
Agent memory, personalization and long-context systems are the parent space. STALE directly introduces a benchmark for memory invalidation/revision behavior.

## 05. Pain point
Retrieving new evidence is not the same as recognizing that an old belief is stale or refusing downstream prompts that presuppose the outdated state.

## 06. Core insight
Evaluate stale-memory handling along three axes: state resolution, premise resistance and implicit policy adaptation; add structured consolidation/propagation as an initial repair direction.

## 07. Method / module logic
The abstract reports 400 expert-validated conflict scenarios, 1,200 queries across three probing dimensions, over 100 topics, with contexts up to 150K tokens. CUPMem is introduced as a prototype strengthening write-time revision and propagation-aware search.

## 08. Essential formulas
Not needed/assessable from source-limited record.

## 09. Experiment-to-claim evidence
Systematic evaluation of frontier LLMs and specialized memory frameworks; the best evaluated model reaches 55.2% overall accuracy in the reported benchmark, indicating substantial stale-state failures.

## 10. Main conclusions
Dynamic memory validity and downstream state adaptation are distinct from static retrieval; explicit state adjudication/consolidation is a promising approach.

## 11. Conclusion boundaries
STALE owns broad novelty territory for **detecting/revising stale agent memory and testing downstream consequences**. Q4's N4-B may not be positioned as introducing stale-memory detection itself.

## 12. Author-stated limitations
Not fully assessable from abstract record; full paper required before detailed benchmark comparison.

## 13. Critical analysis
Q4 survives by changing the object. N4-B asks whether a **failure receipt bound to the context coordinates that justified it** should reopen after a later representation/access change, under matched-information exact-synthetic controls. That is narrower than general memory staleness and should be presented as a scoped-dependency mechanism rather than an agent-memory benchmark.

## 14. Learned knowledge
“Stale” should not be used loosely in Q4. The manuscript should distinguish:
- old information contradicted by later evidence (STALE-style memory invalidation);
- a previously valid failure receipt whose **scope assumptions** have changed (Q4 N4-B).

## 15. Knowledge connections
Truth maintenance; dependency-directed invalidation; ContextNest version governance; Q4 scoped reopening; P13 responsibility-carrying state.

## 16. Testable research ideas
- Compare explicit receipt-scope reopening against STALE-like semantic conflict detectors in environments where both can fire.
- Test approximate learned scope certificates rather than exact synthetic scope labels.

## ORION claim effect
**Removed from Q4 novelty:** generic stale-memory detection/revision.  
**Q4 retained residual:** exact matched-information evidence that dependency/scope-bound failure receipts can avoid both stale reuse and unnecessary reopening in the frozen world.
