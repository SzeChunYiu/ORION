# Paper I research object — Recursive Epistemic Reconstruction

## Candidate claim after nearest-work challenge

ORION is not novel merely because it runs an iterative scientific workflow.  The scoped candidate is:

> A research process whose **object knowledge `K`, model of the relevant knowledge/search universe `W`, and research method `M` are explicit mutable state**, and where typed residuals can mechanically change the question, representation, decomposition, search policy or method; dependent closure is then reopened and research must be repeated.  The same mechanic-cell audit recursively applies to the research process itself.

## Atoms

1. research-state representation;
2. decomposition / mechanic-cell representation;
3. search/action selection;
4. assimilation and state update;
5. mismatch/residual detection;
6. responsibility attribution;
7. formulation/method revision;
8. dependency-directed reopening;
9. cost-aware metareasoning;
10. bounded stopping without completeness claims.

## Nearest work and mechanisms absorbed

### AI Scientist-v2 — arXiv:2504.08066
Mechanisms: progressive agentic tree search, experiment-manager agent, autonomous hypothesis/experiment/analysis/manuscript cycle, iterative reviewer feedback.

**Absorb:** branch/tree exploration; experiment manager; explicit experiment artifacts; iterative feedback.

**Not a surviving ORION novelty:** end-to-end automated science, iterative hypotheses or tree search.

**Residual:** AI Scientist-v2 searches within an agent/task formulation; ORION's candidate delta is an explicit typed operation that can revise the formulation/search universe/method and stale dependent closure.

### Google AI Co-Scientist — Gottweis et al., *Towards an AI co-scientist*, arXiv:2502.18864 (2025)
Mechanisms: specialized Generation/Reflection/Ranking/Evolution/Proximity/Meta-review agents, supervisor resource allocation, test-time compute scaling, tournaments and evolution of hypotheses.

**Absorb:** role-specialized hypothesis generation/challenge; parallel candidates; resource allocation; explicit proximity/nearest-work operation; test-time scaling when value justifies cost.

**Do not absorb as authority:** self-Elo/tournament score is proposal-ranking evidence, not independent scientific verification.

### Kosmos — arXiv:2511.02824
Mechanisms: long-horizon cycles of literature search, hypothesis generation and data analysis coordinated through a structured world model; traceable citations.

**Absorb:** persistent structured world model; long-horizon coordination; literature/data parallelism; statement-level traceability.

**Residual:** ORION must model not only discovered facts but also the current relevance universe and method state, plus typed reopen semantics.

### Agent Laboratory — arXiv:2501.04227
Mechanisms: staged literature-review/experiment/writing pipeline, human feedback checkpoints, cost measurement.

**Absorb:** stage receipts, explicit human intervention points, matched cost accounting.

### NASA Systems Engineering Handbook / NASA-HDBK-1009A
Mechanisms: recursive and iterative decomposition, requirements traceability, explicit interfaces/state/timing, verification matrices and validation plans.

**Absorb:** every mechanic owns traceable requirements/observables/interfaces and a verification method; child mechanics must transport obligations to/from parents.

**Residual:** systems engineering provides development recursion, but not ORION's epistemic authority/search/knowledge-reconstruction semantics.

### Rational metareasoning / value of computation — arXiv:2410.05563 and decision-focused active learning
Mechanisms: extra reasoning/search has opportunity cost; choose computation by expected downstream value rather than uniform depth.

**Absorb:** metareasoning budget; decision-relevant information value; stop/switch/escalate based on expected change to the root decision, not token count.

## ORION state already implementing the claim

Current main includes typed mechanic cells, deterministic missing-coordinate questions, K/W/M state, residual/reframe/reopen operators, failure episodes, work-order generation, typed knowledge assimilation and source/mapping lineage.

## Surviving candidate deltas

- `P1.D1.KWM_RECONSTRUCTION`: knowledge, relevance/search-universe model and method are co-evolving state, not hidden agent context.
- `P1.D2.TYPED_FORMULATION_REVISION`: discoveries/failures can target question, representation, decomposition, interface, measurement, search policy or method separately.
- `P1.D3.SCOPED_REOPENING`: a material reframe invalidates only dependent closure and forces renewed search under the changed formulation.
- `P1.D4.MECHANIC_SELF_AUDIT`: the research workflow is itself recursively decomposed into inspectable mechanic cells whose missing dimensions generate work orders mechanically.

These are **candidate differences**, not established novelty.

## Falsifiers / benchmarks

### Hidden-representation-shift worlds
Construct tasks where the answer is unreachable unless the solver discovers that the initial representation/search universe is inadequate. Compare:
- static ReAct/tree-search agent;
- AI-Scientist-like staged workflow;
- ORION without W/M revision;
- full ORION.

Metrics:
- correct missing-coordinate/domain discovery;
- correct responsibility level;
- unnecessary-reframe rate;
- dependent-closure invalidation precision/recall;
- root success under matched compute;
- authority violations;
- cost to resolution.

### Failure replay
Use the historical NLP/parent-discipline omission with names hidden. A valid result must discover an unseen parent field/functionally relevant representation without having the label preloaded.

### Negative benchmark
Cases where missing evidence—not formulation—is the only problem. Full ORION should acquire evidence, not rewrite `W` or `M`.

## Paper claim boundary

Paper I must **not** claim:
- first autonomous scientist;
- first iterative scientific agent;
- first agent tree search;
- first structured world model;
- first recursive engineering process.

It may test the narrower hypothesis that **typed recursive epistemic reconstruction and scoped reopening outperform static-workflow reasoning when the problem representation/search universe itself must change**.
