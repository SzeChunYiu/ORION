# P7 candidate — Epistemic Navigation in Open Worlds

**Status:** PROPOSED / `CANNOT_CHECK` for distinct publishable novelty.

**Parent:** #332. Theory #336. Literature #337. Evaluation #338. Anti-overlap #343.

## Research question

Can open-world scientific reasoning be modeled as navigation over an epistemic space whose topology can itself change when the system reframes the problem, rather than as search over a fixed graph or retrieval index?

## Candidate contribution

P7 tentatively models navigation state using:

- current epistemic location/state;
- frontier and open obligations;
- route identity and route relation;
- structural independence vs observed overlap;
- censored/unavailable regions;
- revisit/defer state;
- local route-stop vs global task-stop authority;
- resource state;
- representation-change operations that may alter reachability, frontier and route equivalence.

The main hypothesis is that fixed-space search is insufficient when scientific progress can require changing the representation or search universe itself.

## Ownership boundary

P2 owns open-world scientific discovery, route independence, question-conditioned memory, route/task stopping and recall-first promotion. P7 survives only if it demonstrates a more general navigation object that transfers beyond retrieval and adds a distinct mechanism—especially **topology-changing reframing**—rather than simply renaming P2 route governance.

### Explicit nonclaims

P7 does not claim novelty for graph search, knowledge-graph navigation, information foraging, POMDP exploration, query diversification, retrieval planning, replanning, or stopping criteria individually.

## First nearest-work pressure

The initial literature pass surfaced Search-on-Graph, Mind-ParaWorld/MPW-Bench, the Initial Exploration Problem in knowledge graphs, and evidence that current AI research agents can narrow rather than broaden scientific exploration. P2 already contains a large nearest-work base in open-world retrieval and stopping.

The hostile novelty question is:

> Does prior work already treat an agent's search/navigation topology as revisable under representation change while preserving explicit censored/open obligations and separate stopping authority?

Until #337 closes that route, novelty remains `CANNOT_CHECK`.

## Planned evidence

#338 requires a benchmark spanning fixed graphs, censored coverage, deceptive local optima, dead ends, and representation-changing cases, plus at least one non-retrieval transfer domain. A direct topology-change ablation is mandatory.

## Working manuscript

See `manuscript/DRAFT.md`.
