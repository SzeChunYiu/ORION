# Epistemic Navigation in Open Worlds

**Working manuscript — candidate P7 — 2026-08-17**

## Abstract

Search-oriented agents are often modeled as navigating a fixed information space: a state, graph, index or environment exists, and the agent chooses actions until a stopping rule fires. Scientific inquiry can violate that premise. A researcher may discover that the current ontology, decomposition, model class, search universe or optimization objective is itself inadequate. In that case the state space being navigated changes. This paper develops a candidate theory of **open-world epistemic atlas navigation**: inquiry proceeds within local representations or *charts*, while authorized reframes may change locations, relations, route identity, objectives and closure semantics. The framework absorbs rather than avoids fixed-graph navigation, POMDP information gathering, exploratory search, initial-orientation theory, goal-evolving scientific agents, self-evolving world models and ORION P2's route/stop mechanics. Its distinct research question is whether evidence and closed obligations can be transported safely across representation/objective change while unresolved or censored regions remain unable to authorize global completion. We state a stopping impossibility theorem under extension ambiguity, distinguish orientation from ordinary route optimization, prove a support-transport criterion for reframes, and specify fixed-chart, negative-control and non-retrieval transfer tests. P7 remains `CANNOT_CHECK` for distinct novelty until the atlas residual survives P1+P2 ownership and nearest-work saturation.

## 1. Introduction

The navigation metaphor is natural for research agents. They browse web pages, traverse citation graphs, inspect knowledge graphs, query databases, test hypotheses and move through experimental workflows. Yet almost every navigation model begins by fixing the space in which motion occurs.

Scientific inquiry sometimes changes that space.

A researcher may discover that the wrong parent discipline has been searched, that two nominally identical constructs use incompatible measurement schemes, that the optimization objective is a poor proxy, that a hidden variable changes what counts as a state, or that an initial question should be decomposed into several coupled questions. The change is not just a better edge choice. It can alter what states exist, which edges are meaningful, what is reachable, what counts as equivalent, which obligations remain valid and whether earlier evidence still closes the transformed task.

ORION P1 already owns responsibility-triggered representation/search-universe reconstruction. P2 already owns earned route independence, question-framed discovery, route-versus-task stopping and fail-closed open/censored coverage. P7 cannot claim either mechanism. It asks whether their interaction belongs to a broader navigation theory in which representations, world models and objectives form a family of charts connected by partial preservation maps.

## 2. From one topology to an epistemic atlas

Instead of one graph `T`, P7 uses an epistemic atlas

\[
\mathfrak A=(\{T_i\}_{i\in I},\mathcal M,\Xi).
\]

Each chart

\[
T_i=(V_i,E_i,\lambda_i,\Omega_i,\mathcal C_i)
\]

contains epistemic locations, reachability relations, semantic/evidence labels, task obligations/objectives and route/coverage contracts under one representation. The family `\mathcal M` contains partial maps between charts. `\Xi` records what must be preserved for locations, relations, evidence identities, obligations and closure certificates to transport.

The word *atlas* is intentionally broader than a graph topology. A chart may be a knowledge graph, symbolic belief space, ontology, scientific model class, experimental-design space, search universe or objective representation. P7 should not imply point-set topology unless such structure is explicitly introduced.

A navigation state is

\[
N=(\mathfrak A,i,x,F,R,O,C,V_h,B,H),
\]

tracking the active chart, current location/belief, frontier, routes, obligations, censored/unknown regions, visited evidence identities, budget and history.

## 3. Orientation before ordinary navigation

The literature already contains a direct challenge to the assumption that users or agents begin with a valid starting point. The Initial Exploration Problem (arXiv:2602.21066) identifies scope uncertainty, ontology opacity and query incapacity when encountering an unfamiliar knowledge graph.

P7 absorbs this as an **orientation obligation**. A navigator can know that it is inside an information system while lacking a sufficient representation of what can be asked, what the schema means, or which routes exist. In such a state, ordinary route utility may not yet be well-defined because the semantics of the candidate actions depend on unresolved orientation variables.

This is not claimed as a novel phenomenon. The atlas generalization asks how orientation interacts with later reframing, route identity and stopping authority.

## 4. Partial observability, admissible completions and stopping

Open-world stopping requires care. An earlier draft stated that absence of a closure certificate automatically yields observationally indistinguishable complete and incomplete worlds. That is too strong without an assumption on the admissible world class.

P7 now defines a finite history `h` to be **extension-ambiguous** for mandatory obligations `O` when there exist two admissible completions `W_0,W_1` such that:

1. both produce exactly the same observations along `h`;
2. all mandatory obligations are satisfied/discharged in `W_0`;
3. at least one mandatory obligation remains unsatisfied in `W_1`.

A closure certificate is an object whose semantics excludes every admissible completion containing an unsatisfied obligation in its scope.

### Stopping impossibility under extension ambiguity

If `h` is extension-ambiguous, no stopping rule depending only on `h` can soundly certify `TASK_STOP` for every admissible completion. The two completions are observationally identical but disagree on task completion, so the same history-only verdict must fail in at least one.

Under a richer open-world premise—namely, that whenever no closure constraint excludes an unseen relevant witness the model class admits both a completion with and without such a witness—absence of that closure constraint implies extension ambiguity.

This theorem does not imply infinite search. It distinguishes **resource stopping** from **scientific completion authority**.

## 5. Route stopping is not task stopping

P2 already owns the local/global distinction. P7 embeds it as a navigation invariant.

A route may be locally stopped because its expected marginal value is low, its budget is exhausted or its local coverage contract is satisfied. Global task stopping requires all mandatory obligations to be satisfied/discharged/covered. Therefore all executed routes can be locally exhausted while an unavailable, censored or unexecuted route retains an open obligation.

The same distinction matters after chart change. Reframing does not erase unresolved coverage. A new representation can open new routes while leaving old censored obligations unresolved, or it can invalidate a closure that depended on an old representation.

## 6. Structural route identity

Different queries, APIs or labels are not necessarily different routes. Conversely, overlapping results do not imply common failure structure.

P7 represents a route with interface/source family, transition/query mechanism, structural failure signature and coverage/censoring contract. Structural independence is defined relative to an obligation: two routes are independent only when they do not share an unaccounted critical failure cause capable of making both miss the same relevant witness.

Constructive counterexamples show both directions:

- two structurally independent routes can return identical observed output;
- two structurally dependent routes can return disjoint observed output.

This relation is P2-owned when applied to literature discovery. P7 uses it as one component of atlas navigation.

## 7. Representation and objective change

A reframe from chart `T` to `T'` is represented as

\[
\rho=(T,T',\phi_V,\phi_E,\phi_\Omega,\Pi),
\]

where the partial maps transport locations, relations and obligations/objectives, and `\Pi` contains preservation obligations for semantic relations, evidence identities and closure scopes.

This abstraction absorbs several current lines of work.

**SAGA (arXiv:2512.21782)** already evolves scientific objective functions in an outer loop while optimizing under the current objective in an inner loop. P7 therefore treats objective evolution as a donor mechanism, not a novelty claim.

**Self-Evolving World Models (arXiv:2606.30639)** already revise a deployment-time world model from prediction-observation mismatch. P7 distinguishes intra-chart model revision from inter-chart representation change: changing transition beliefs inside a fixed vocabulary is not automatically a topology change.

**Graph World Models (arXiv:2604.27895)** provide structured world representations and identify dynamic graph adaptation as an important direction. P7 must therefore go beyond “graphs can change.”

The candidate residual is the preservation problem: what earlier evidence and closure authority survive when representation or objective semantics change?

## 8. Support transport across reframes

For a closed obligation `o`, let `Supp_T(o)` contain the full support used by its certificate: locations, relations, semantic labels, route/coverage contracts, objective meaning and content-bound evidence identities.

A reframe preserves `o` only when every support element is mapped, every predicate/relation used in the certificate is semantics-preserved, the new obligation has the same relevant satisfaction meaning, evidence identity remains stable, and no new in-scope defeater is introduced.

### Safe transfer criterion

If all support conditions hold, the old certificate can be transported through the map. If a required support/objective relation is absent and no replacement proof is supplied, uniformly sound navigation must reopen the obligation or return `CANNOT_CHECK`.

A key consequence is that **evidence can transport while closure does not**. Changing the scientific objective can leave an observation perfectly valid while invalidating the claim that the task is complete under the new objective.

This is one of the central cross-donor interactions P7 will test.

## 9. Expressivity and its limits

There are trivial task families where a fixed chart has no path to a goal state but an admissible reframe creates a representation in which the goal is reachable. An atlas policy is therefore strictly more expressive on such families.

This is not, by itself, a publishable theorem. Replanning, abstraction change, representation learning and world-model revision already imply variants of it. P7's burden is to combine that expressivity with support transport, obligation reopening and fail-closed stopping in a way that matters empirically.

Negative controls are essential. If the original chart already contains a valid route to the solution, unnecessary reframing should be counted as error/cost rather than “more sophisticated reasoning.”

## 10. Donor assimilation

P7 treats the following as strong donors.

### Search-on-Graph
Search-on-Graph (arXiv:2510.08825) demonstrates iterative observe-then-navigate reasoning on knowledge graphs. It is a fixed-chart navigation baseline.

### Mind-ParaWorld
Mind-ParaWorld / MPW-Bench (arXiv:2603.04751) creates dynamic parallel worlds with atomic ground truth and shows that evidence collection/coverage, sufficiency judgments and when-to-stop remain difficult. P7 adopts this style of hidden-world falsification.

### Initial Exploration Problem
Initial orientation is a first-class failure mode, not free setup.

### POMDP/belief-space planning and information foraging
Partial observability, value-of-information and exploratory-search utility are mature. P7 uses them to govern resource allocation but does not equate them with scientific completion.

### Goal/world-model evolution
SAGA and self-evolving/graph world models demonstrate that objectives and models can change. P7 asks when such changes preserve or reopen earlier scientific closures.

### Scientific exploration breadth
AI Research Agents Narrow Scientific Exploration (arXiv:2605.27905) reports that AI-generated research ideas are more concentrated and closer to seed literature than human follow-on work across a large study. P7 therefore includes exploration concentration/breadth as an outcome, while avoiding the mistake of treating raw route count as useful breadth.

## 11. A widened candidate object

The current P7 object is an **open-world epistemic atlas**:

\[
\text{orientation}
+
\text{partial-observation navigation}
+
\text{structural route contracts}
+
\text{chart/world-model/objective evolution}
+
\text{support-preserving transport/reopening}
+
\text{explicit censored obligations}
+
\text{fail-closed task-stop authority}.
\]

The generalization is scientific only if interactions among these components create new theorem obligations or benchmark behavior beyond simple composition of prior methods.

## 12. Deterministic falsifiers

The first checker is committed at `papers/candidates/checkers/p7_finite_falsifiers_v1.py`. The current local run is 7/7 PASS over bounded fixtures covering:

1. observationally identical complete/incomplete extension pairs;
2. a counterexample showing certificate absence is not logically equivalent to ambiguity without a richness premise;
3. route-stop/task-stop separation;
4. fixed-chart unreachable versus reframed reachable goal;
5. evidence transport with goal-change closure reopening;
6. fail-closed stopping with mandatory-open obligations;
7. a negative control where reframing is unnecessary.

The checker supports the definitions; it does not establish unrestricted correctness.

## 13. Prospective benchmark

The benchmark programme is wider than retrieval.

Required families include hidden useful branches, unknown coverage, censored routes, deceptive route diversity, dead ends and revisitation, initial-orientation tasks, ontology/representation-changing tasks, objective-evolving scientific design, world-model revision without representation change, exploration-breadth traps, and negative controls where fixed-chart navigation is optimal.

At least one non-retrieval symbolic or scientific domain must have exact ground truth.

Strong baselines include SoG-style fixed-chart navigation, POMDP/information-gathering where appropriate, P2 route governance, goal/world-model revision donors, and a no-topology-change ablation.

Primary outcomes include task success, obligation coverage, premature-stop rate, route-independence error, dead-end recovery, evidence/closure transport error, unnecessary reframe rate, useful exploration breadth, calibrated `CANNOT_CHECK` and resource cost.

## 14. Exact boundary against P1–P5

The V1 ownership matrix marks route independence, route/task stopping and fail-closed coverage as P2; native representation/search-universe reconstruction remains P1. P7 therefore survives only if atlas-level support/objective transport plus non-retrieval transfer yields a distinct result beyond P1+P2.

This is a hard termination rule, not a rhetorical disclaimer.

## 15. Limitations

Many scientific state spaces cannot be objectively enumerated. The choice of chart is itself theory-laden. Preservation maps may require expert judgment. Benchmarks with known hidden structure may overreward behaviors that do not transfer to real inquiry. More expressive reframing can become a failure mode by continually changing the problem rather than solving it. Exploration breadth can be gamed by useless dispersion. Closure certificates can be unavailable even when practical stopping is rational.

P7 can also fail scientifically by being a clean formal synthesis with no distinct empirical or theorem-level value. In that case the atlas concepts should be merged into P1/P2 rather than promoted.

## 16. Conclusion

Open-world scientific navigation is not only path selection. It can require orientation in an unknown structure, movement under partial observability, and justified transfer when the representation or objective itself changes. P7 deliberately absorbs strong navigation, search, world-model and goal-evolution work, then asks a narrower but deeper question: **what survives epistemically when the map changes?** The answer remains a research target until donor-faithful embeddings, formal checking and cross-domain prospective benchmarks close.