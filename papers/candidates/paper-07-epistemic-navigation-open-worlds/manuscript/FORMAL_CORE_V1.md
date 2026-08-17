# P7 formal core V1

**Candidate paper:** Epistemic Navigation in Open Worlds  
**Authority:** mathematical working object; novelty not yet authorized  
**Date:** 2026-08-17  
**Donor policy:** absorb graph navigation, partial-observability, orientation, goal evolution and world-model revision as special cases.

## 1. Epistemic charts and atlases

### Definition 1 (epistemic chart)
An **epistemic chart** is a tuple

\[
T=(V,E,\lambda,\Omega,\mathcal C),
\]

where:

- `V` is a set of epistemic locations/states under one representation;
- `E\subseteq V\times V` is a directed reachability relation;
- `\lambda` assigns typed semantic labels, representations and evidence identities to locations/edges;
- `\Omega` is a set of task obligations/objectives whose satisfaction conditions are expressed in the chart;
- `\mathcal C` records route/coverage/censoring contracts known in that chart.

The word *chart* is deliberate. A chart may be a graph, hypergraph, transition system, belief-state abstraction, ontology, objective representation, or another structure with a reachability/obligation semantics. P7 does not assume a topological-space structure unless introduced explicitly.

### Definition 2 (epistemic atlas)
An **epistemic atlas** is

\[
\mathfrak A=(\{T_i\}_{i\in I},\mathcal M,\Xi),
\]

where `T_i` are charts, `\mathcal M` is a family of partial chart/objective transformation maps, and `\Xi` records conditions under which locations, relations, evidence identities, obligations and closure certificates transport between charts.

An atlas represents the possibility that inquiry changes not only the current node but the representation defining nodes, edges, routes, objectives or admissible questions.

### Definition 3 (route)
A route is

\[
r=(I_r,\delta_r,\sigma_r,\kappa_r),
\]

where `I_r` is an interface/source family, `\delta_r` its transition/query mechanism, `\sigma_r` a structural assumption/failure signature, and `\kappa_r` its known coverage/censoring contract.

Different names, query strings or APIs do not establish distinct structural routes.

### Definition 4 (navigation state)
A navigation state is

\[
N=(\mathfrak A,i,x,F,R,O,C,V_h,B,H),
\]

where:

- `i` is the active chart;
- `x` is the current epistemic location or belief over locations;
- `F` is the active frontier;
- `R` is the registered route set;
- `O\subseteq\Omega_i` is the active obligation set;
- `C` records censored, unavailable and unknown-coverage regions/routes;
- `V_h` records visited locations and evidence identities;
- `B` is remaining resource state;
- `H` is observation/action/reframe history.

## 2. Observation histories and admissible completions

### Definition 5 (observational equivalence)
Let `h` be a finite history produced by a navigator. Two world/atlas instances `W_1,W_2` are observationally equivalent at `h`, written

\[
W_1\equiv_h W_2,
\]

when every observation, route response, cost, transition and chart information exposed along `h` is identical.

### Definition 6 (admissible completion)
An admissible completion of history `h` is any world/atlas instance that preserves every observation in `h` and satisfies all currently valid structural/coverage constraints, while possibly containing unobserved locations, edges, routes, labels, objectives or defeaters not excluded by those constraints.

### Definition 7 (extension ambiguity)
A history `h` is **extension-ambiguous** for mandatory obligation family `O` when there exist two admissible completions `W_0,W_1` such that:

1. `W_0\equiv_h W_1`;
2. every mandatory obligation in `O` is satisfied/discharged in `W_0`;
3. at least one mandatory obligation in `O` is unsatisfied in `W_1`.

This is the exact premise needed by the stopping impossibility result.

### Definition 8 (closure certificate)
A closure certificate for `O` is an externally or mechanically checkable object `z` whose semantics excludes every admissible completion containing an unsatisfied obligation in `O`.

Examples may include a complete finite manifest, exhaustive content-bound index with coverage proof, or theorem proving that every relevant state lies in the enumerated region.

Low expected utility, repeated empty responses, budget exhaustion and local route saturation are not closure certificates by themselves.

### Important logical boundary
Absence of a closure certificate does **not by itself** imply extension ambiguity in every possible world class. A model class may be complete for other reasons not represented as a certificate. P7 therefore states the impossibility theorem on extension ambiguity directly and treats certificate absence as a practical sufficient route only under an explicit richness premise.

## 3. Impossibility of unlicensed open-world stopping

Let a stopping rule `\pi` map finite histories to

\[
\{\mathsf{continue},\mathsf{route\_stop},\mathsf{task\_stop},\mathsf{defer},\mathsf{cannot\_check},\mathsf{reframe}\}.
\]

### Theorem 1 (stopping impossibility under extension ambiguity)
If history `h` is extension-ambiguous for mandatory obligations `O`, then no stopping rule depending only on `h` can soundly output `\mathsf{task\_stop}` for every admissible completion of `h`.

#### Proof
By extension ambiguity there exist observationally equivalent completions `W_0,W_1` with different task-completion truth values. A history-only rule receives the same `h` in both worlds and therefore produces the same output. If it returns `task_stop`, the judgment is false in `W_1`; if it does not, it does not certify completion in `W_0`. Hence no history-only rule can soundly certify completion for both. `\square`

### Corollary 1.1 (rich-open-world construction)
Suppose a world class has the property that whenever no valid closure constraint excludes an unseen relevant witness, one may construct both (i) a completion with no such witness and (ii) an observationally equivalent completion containing one. Then absence of such a closure constraint implies extension ambiguity and Theorem 1 applies.

### Corollary 1.2 (utility is not completion authority)
Expected marginal utility may be equally low in both observationally equivalent completions. Utility can therefore govern resource allocation without resolving the completion truth value.

### Interpretation
The theorem does not require research to continue forever. It identifies the extra epistemic object needed to convert resource stopping into scientific completion: a valid closure/discharge condition for the mandatory obligations.

## 4. Route stopping versus task stopping

### Definition 9 (route-stop judgment)
A route `r` may receive `route_stop` when its frozen local policy establishes that no further action on `r` is currently justified under its budget/coverage contract.

### Definition 10 (task-stop judgment)
A task may receive `task_stop` only when every mandatory obligation is satisfied, validly discharged, or covered by a closure certificate whose scope includes the obligation.

### Proposition 2 (route stop does not imply task stop)
There exists a navigation state in which every executed route has locally stopped while an unexecuted, unavailable or censored route retains an open mandatory obligation. Therefore

\[
\bigwedge_{r\in R_{executed}}\mathsf{route\_stop}(r)
\not\Rightarrow
\mathsf{task\_stop}
\]

without an additional coverage premise.

This local/global distinction is P2-owned in ORION. P7 embeds it; it does not relabel it.

## 5. Orientation and initial exploration

### Definition 11 (orientation obligation)
An orientation obligation is an obligation to establish enough scope/ontology/route information to make subsequent navigation actions interpretable under the active chart.

A navigator may therefore begin with `x` partially undefined: it can know that it is inside an information system while lacking a valid starting concept, route vocabulary, or estimate of what can be asked.

This adopts the Initial Exploration Problem's scope uncertainty, ontology opacity and query incapacity as first-class navigation state rather than treating initial query formulation as free.

### Proposition 3 (orientation can precede ordinary route optimization)
There exist tasks in which no route utility estimate is well-defined under the current chart because route/action semantics depend on unresolved orientation variables. A scope-revelation action can therefore be epistemically prior to ordinary route ranking.

This is an embedding target, not a novelty claim.

## 6. Route independence and observed overlap

### Definition 12 (structural independence relative to obligation)
Routes `r_1,r_2` are structurally independent relative to obligation `o` only when their registered critical failure/coverage assumptions do not share an unaccounted common cause sufficient to make both miss the same relevant witness. The exact relation may be implemented by disjoint critical-assumption sets, a causal model, or a stronger contract.

Observed result sets are `Y_1,Y_2`.

### Proposition 4 (equal output does not imply structural dependence)
There exist structurally independent routes with `Y_1=Y_2`.

### Proposition 5 (disjoint output does not imply structural independence)
There exist structurally dependent routes with `Y_1\cap Y_2=\varnothing`.

### Consequence
Content overlap is a behavior metric, not an authority proof for route independence.

Again, the route-governance core is P2-owned; P7 needs atlas/reframe transfer to remain distinct.

## 7. Chart-changing reframes

### Definition 13 (reframe morphism)
A reframe is

\[
\rho=(T,T',\phi_V,\phi_E,\phi_\Omega,\Pi),
\]

where:

- `T` is the old chart and `T'` the proposed chart;
- `\phi_V:V\rightharpoonup V'` is a partial location map;
- `\phi_E:E\rightharpoonup E'` is a partial relation map;
- `\phi_\Omega:\Omega\rightharpoonup\Omega'` is a partial obligation/objective map;
- `\Pi` is a set of preservation obligations/proofs specifying which labels, evidence identities, semantic relations, closure scopes and objective meanings survive.

A reframe can therefore change representation, ontology, world model, search universe or objective structure. It is not merely another transition inside `T`.

### Definition 14 (admissible reframe)
A reframe is admissible when:

1. the representation/objective mutation is authorized by the relevant responsibility/authority contract;
2. every retained evidence identity remains content-bound;
3. every transported closure has complete support preserved by the map;
4. obligations that are unmapped, semantically changed or unsupported reopen or become `CANNOT_CHECK`;
5. negative history relevant to recurrence/governance is retained.

### Theorem 6 (strict expressivity of chart-changing navigation)
There exists a family of tasks for which every policy restricted to an initial chart `T` fails, while an atlas policy with one admissible reframe to `T'` succeeds.

#### Proof
Choose `T` such that the reachability closure of start state `s` contains no state satisfying goal predicate `g`. Any fixed-chart policy remains inside that closure. Let an admissible reframe map the preserved context into `T'`, in which a newly represented goal state `v_g` satisfying `g` is reachable. The atlas policy applies the reframe and follows the new route. `\square`

### Limitation
This theorem is intentionally weak as a novelty result; representation change, replanning, world-model revision and goal evolution are established. P7 requires the stronger coupling of chart/objective change with evidence transport, reopening and stopping authority.

## 8. Support transport and reopening across reframes

For a closed obligation `o`, let `\operatorname{Supp}_T(o)` be the complete support substructure used by its certificate: supporting locations, relations, labels, route/coverage contracts, objective semantics and evidence identities.

### Definition 15 (support-preserving reframe for an obligation)
A reframe `\rho` preserves `o` when:

1. all support locations/relations are mapped;
2. every predicate/relation used by the certificate is semantics-preserved;
3. the mapped obligation/objective has the same relevant satisfaction meaning;
4. evidence identities remain content-bound;
5. no new in-scope defeater is introduced inside the certificate's declared completeness scope.

### Theorem 7 (safe transfer criterion)
If `\rho` preserves `o`, the old certificate transports to `T'`. If any required preservation condition is absent and no replacement proof is supplied, uniformly sound navigation must reopen `o` or assign `CANNOT_CHECK`.

#### Proof
For the first direction, transport the original derivation through the semantics-preserving maps. For the second, if a required support/objective relation is unmapped or unproved, construct two target charts consistent with the available map: one preserving the derivation and one falsifying the missing element. Retaining closure would be unsound in the latter. `\square`

### Corollary 7.1 (goal evolution is not automatic evidence inheritance)
Changing an objective can preserve prior evidence while invalidating the closure meaning of a prior result. An objective-evolving system must therefore distinguish evidence transport from obligation/goal transport.

This is a direct assimilation target for SAGA-style goal evolution.

## 9. World-model revision and atlas evolution

World-model revision systems can be represented as chart updates or chart transitions depending on whether the state vocabulary remains fixed.

- If predictions/transition parameters change while state/objective semantics remain fixed, P7 treats this as **intra-chart model revision**.
- If the representation introduces/removes state distinctions, route identities, ontology relations or objectives, P7 treats it as **inter-chart atlas evolution**.

This distinction allows self-evolving world models and dynamic graph world models to be absorbed without calling every model update a topology change.

## 10. Fail-closed stopping invariant

### Definition 16 (mandatory-open obligation)
An obligation is mandatory-open when it is not satisfied/discharged and no valid closure certificate covers it.

### Theorem 8 (fail-closed task-stop invariant)
In any navigation trace preserving

\[
\mathsf{task\_stop}\Rightarrow \text{no mandatory-open obligation},
\]

route exhaustion, low utility, budget depletion, repeated observations or a chart reframe cannot by themselves derive `task_stop`.

#### Proof
None of these events by itself changes a mandatory-open obligation into a satisfied/discharged/covered state. The invariant therefore continues to block task stop until the obligation state changes through an authorized rule. `\square`

## 11. Donor-faithful embeddings

P7 now treats the following as explicit donor targets:

- **Search-on-Graph (arXiv:2510.08825):** fixed-chart observe-then-navigate graph traversal;
- **Mind-ParaWorld (arXiv:2603.04751):** atomic hidden-world evaluation of evidence coverage, sufficiency and stopping;
- **Initial Exploration Problem (arXiv:2602.21066):** scope uncertainty, ontology opacity and query incapacity;
- **POMDP/belief-space information gathering:** partial observability and value-of-information planning;
- **SAGA (arXiv:2512.21782):** autonomous objective evolution with inner-loop optimization;
- **Self-Evolving World Models (arXiv:2606.30639):** test-time world-model revision and selective foresight;
- **Graph World Models (arXiv:2604.27895):** structured world representations and dynamic graph adaptation;
- **AI Research Agents Narrow Scientific Exploration (arXiv:2605.27905):** empirical scientific-search concentration/breadth pressure;
- **P2:** route independence, route/task stopping, question-conditioned discovery and open/censored obligations.

### Theorem target 9 (conservative donor embedding)
When P7 atlas transformations are disabled and the donor-specific assumptions hold, the P7 representation should reproduce the donor's native navigation/stop/update judgments rather than invent extra behavior.

## 12. Widened P7 residual under test

The candidate object is now an **open-world epistemic atlas**, not merely a dynamic graph:

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

The generalization is useful only if these axes interact in ways not settled by juxtaposing their parent literatures.

## 13. Deterministic checking obligations

The associated finite checker must generate bounded atlas instances and verify:

1. extension-ambiguous complete/incomplete world pairs for Theorem 1;
2. a counterexample showing certificate absence alone is not logically equivalent to ambiguity without a richness premise;
3. route-stop/task-stop counterexamples;
4. equal-output independent-route and disjoint-output dependent-route constructions;
5. an unreachable fixed chart and reachable reframed chart;
6. transfer versus reopening under complete/incomplete preservation maps;
7. goal/objective change that retains evidence but reopens closure;
8. no task stop in the presence of mandatory-open obligations;
9. negative controls where an unnecessary reframe is penalized;
10. donor-native fixed-chart fixtures remain unchanged under conservative embeddings.

No LLM API is required.

## 14. Benchmark width required by #338/#353

Minimum benchmark families now include:

- hidden-branch fixed graphs;
- unknown/censored route coverage;
- initial-orientation/scope-revelation tasks;
- deceptive local optima and revisitation;
- topology/ontology-changing tasks;
- objective-evolving scientific design tasks;
- world-model revision tasks where representation does **not** change, to test the intra/inter-chart distinction;
- exploration-breadth cases where local elaboration is tempting but broader chart/route discovery matters;
- negative controls where fixed-chart navigation is optimal;
- at least one non-retrieval symbolic/scientific domain with exact ground truth.

Strongest relevant donor baselines are mandatory.

## 15. Nearest-work pressure and nonclaims

This core does **not** claim novelty for:

- graph/KG navigation;
- POMDP/belief-space planning;
- information foraging/exploratory search;
- search-agent stopping or evidence sufficiency;
- initial orientation problems;
- replanning/world-model revision;
- dynamic graph adaptation;
- autonomous goal/objective evolution;
- open-world indistinguishability arguments in general;
- P2's route/task stopping mechanics.

The widened candidate residual is the donor-faithful composition of these ideas around representation/objective change, support transport/reopening and non-escalating closure authority. If #337/#352/#343 reduce this to P1+P2 or established planning/search theory with no new theorem/transfer discriminator, P7 should merge rather than survive by terminology.

## 16. What this formal core establishes now

The core establishes elementary impossibility, separation, expressivity and transfer results under the definitions above, and repairs an over-strong premise from the earlier stopping theorem. It does **not** establish:

- novelty;
- that real scientific state spaces admit faithful charts/maps;
- that route-independence contracts are practically identifiable;
- that atlas-changing navigation improves real research;
- that the generalization is distinct from P1+P2;
- peer-review readiness.

Current novelty/promotion terminal remains `CANNOT_CHECK`.