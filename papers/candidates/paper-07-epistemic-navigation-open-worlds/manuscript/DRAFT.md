# Epistemic Navigation in Open Worlds

**Working manuscript — candidate ORION-17 — 2026-08-17**

## Abstract

Search-oriented agents are commonly evaluated as if they navigate a fixed information space: the agent chooses queries, graph edges, documents or actions until a stopping rule fires. Scientific research is harder. The agent may discover that the original representation, decomposition, measurement scheme or search universe is itself inadequate, so the topology of the epistemic space changes during inquiry. This paper investigates a general theory of **epistemic navigation** for such settings. We distinguish locations, frontiers, routes, censored regions, open obligations, revisit states and stopping authority; separate structural route independence from observed overlap; and treat representation change as a topology-changing operation rather than another edge in a fixed graph. The candidate residual is an evolving-space navigation model with fail-closed stopping under unknown coverage. Novelty remains unestablished pending comparison with graph navigation, exploratory search, information foraging, POMDP-style information acquisition, open-world search agents and ORION-12's existing route-governance theory.

## 1. Introduction

Research agents increasingly browse the web, traverse citation networks, query databases, inspect knowledge graphs and execute scientific workflows. The natural mathematical metaphor is navigation.

Yet most navigation formalisms begin with a state space. Scientific inquiry sometimes changes that state space.

A researcher who realizes that a phenomenon must be described in another coordinate system, that the wrong parent discipline has been searched, or that an apparent single problem is actually two coupled subproblems has not merely chosen a better path. The set of relevant states, routes and reachable evidence has changed.

ORION-12 already addresses one part of this problem: route independence, route stopping versus task stopping, question-conditioned memory and open/censored search obligations. ORION-17 asks whether these ideas can be generalized beyond literature retrieval into a navigation theory over **evolving epistemic topology**.

## 2. Navigation state

We tentatively define a navigation state

`N = (x, F, R, O, C, V, B, T)`

where:

- `x` is current epistemic location/state;
- `F` is the active frontier of reachable or hypothesized next states;
- `R` is the set of known routes and route relations;
- `O` is the set of open obligations;
- `C` records censored, unavailable or unknown-coverage regions;
- `V` records visited/revisited states and evidence identity;
- `B` records budget/resource state;
- `T` records the current representation/topology definition.

This is deliberately broader than a retrieval index. A state could be a search region, diagnosis hypothesis, representation, experimental design or scientific workflow state.

## 3. Route identity and independence

A major problem is determining whether two routes are truly different.

Different query strings, APIs or graph labels do not establish independence. Conversely, overlapping content does not prove structural dependence.

ORION-17 therefore distinguishes:

- **structural route independence**: routes differ in source/mechanism/coverage assumptions;
- **observed overlap**: routes happen to return the same content in a run;
- **route refinement**: a route narrows or expands another route;
- **route equivalence**: routes are operationally interchangeable under a defined obligation set.

The exact formal relations remain to be defined in #336.

## 4. Stopping and unresolved coverage

Local exhaustion is not global completion.

We distinguish:

`ROUTE_STOP` — no further action is justified on one route under the frozen policy;

`TASK_STOP` — all closure obligations required for the task are satisfied;

`DEFER/REVISIT` — a route remains unresolved but is postponed under resource policy;

`CANNOT_CHECK` — decisive coverage/authority cannot be established;

`REFRAME` — the current topology is judged inadequate and a representation-changing operation is proposed.

The key authority claim under test is that utility, low expected gain or local exhaustion may justify resource allocation, but should not automatically certify scientific completeness when coverage is censored or unknown.

## 5. Topology-changing reframing

Let a fixed-space navigation policy choose actions within topology `T`.

A reframe operator instead maps

`rho: T -> T'`

and induces a transformation of locations, frontiers, obligations and route identity:

`Phi_rho(N_T) -> N_T'`.

The central technical difficulty is preservation. Some visited evidence and closed obligations remain valid under `T'`; others must be reopened because their interpretation depended on the old representation.

This links ORION-11's responsibility-conditioned reconstruction with ORION-12's route governance. ORION-17 is distinct only if the composition produces a general navigation property that is neither paper's existing contribution alone.

## 6. Related-work boundary

Graph and knowledge-graph navigation already provide iterative observe-and-navigate mechanisms. Exploratory search and information foraging study behavior under uncertain information needs and patch value. POMDP and active-information-acquisition methods treat information gathering as sequential decision making. Search-agent work evaluates web/deep-research agents and increasingly exposes evidence-coverage and when-to-stop failures. Planning work distinguishes planning from local stepwise reasoning and studies replanning after deviations.

Recent work also raises a broader scientific concern: AI research agents can concentrate exploration around existing literature rather than broadening the scientific search space. This motivates a navigation metric beyond final answer correctness.

ORION-17 cannot claim novelty for exploration, graph navigation or replanning. The hostile question is whether prior work already models **representation-changing navigation with explicit open/censored stopping obligations**.

## 7. Prospective benchmark

#338 defines a new benchmark family only if #337 leaves a residual.

The planned families are:

1. fixed graphs with hidden useful branches;
2. partial-observation graphs with unknown coverage;
3. censored/unavailable routes;
4. redundant routes with deceptive apparent diversity;
5. dead ends and revisit requirements;
6. topology-change cases where the original representation cannot reach the solution;
7. negative controls where topology change is unnecessary;
8. a non-retrieval transfer domain.

The topology-change ablation is mandatory. If a fixed-space ORION-12-style navigator performs equivalently, the ORION-17 residual is weakened or refuted.

## 8. Metrics

Candidate outcomes include root-task success, obligation coverage, frontier discovery, redundant exploration, false route-independence, premature task stopping, dead-end recovery, revisit value, unnecessary topology change, calibrated unresolved/CANNOT_CHECK behavior, and cost.

A navigation paper should also report **exploration breadth** and whether the system repeatedly elaborates the same local region despite nominal route diversity.

## 9. Limitations

Many scientific spaces cannot be objectively enumerated. Topology is partly representation-dependent. A benchmark with known hidden structure may reward behaviors that do not transfer to real science. Representation change can be overused to avoid difficult local work. ORION-17 also risks being merely ORION-11+ORION-12 composition; #343 can terminate the candidate on that basis.

## 10. Conclusion

The candidate thesis is that open-world research is not only a problem of choosing paths but of maintaining justified orientation in a space whose structure may itself be wrong. ORION-17 will survive only if an evolving-topology navigation model yields a distinct formal and empirical contribution beyond existing graph/search/planning work and ORION-12.
