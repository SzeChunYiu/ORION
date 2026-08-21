# Epistemic Navigation in Open Worlds

**Paper VII candidate — theory-complete manuscript**  
**Version:** 2026-08-18 / V2 closure  
**Scientific scope:** formal open-world navigation theory with deterministic finite witnesses  
**Programme rule:** engulf strong donor mechanisms before narrowing claims  
**No first-of-kind claim is made.**

## Abstract

Scientific inquiry is often described as search, but ordinary search presumes a representation in which states, actions, goals, and stopping conditions are already meaningful. Open-ended research can violate that premise: a system may begin without a stable ontology, discover new routes or censored regions, change the representation in which the problem is posed, or revise the objective whose satisfaction defines completion. Existing work already studies graph navigation, exploratory search, POMDP planning, planning abstraction, schema transformation, evolving world models, goal evolution, and search-agent stopping. Rather than avoiding these structures, we absorb them as donor mechanisms inside a larger **epistemic atlas** and ask what additional laws are required when scientific evidence and closure authority must survive representation or objective change.

We formalize inquiry as navigation in a family of charts linked by partial representation/objective transformations and explicit preservation contracts. We prove an open-world stopping impossibility theorem under observational extension ambiguity, while separating that condition from the mere absence of a closure certificate. We give a fixed-latent, fixed-sensing construction in which refining only the representation strictly increases worst-case solvability, alongside a harmful-coarsening negative control. We prove that evidence preservation is strictly weaker than closure preservation: an unchanged, valid observation may cease to satisfy a transformed obligation. Complete support-transport witnesses license closure transfer; incomplete and target-ambiguous transport requires reopening, while incomplete but non-ambiguous transport yields `CANNOT_CHECK` unless another proof resolves the question. Route stopping, task stopping, continuation and inability to check remain distinct terminals throughout.

A standard-library finite checker exercises stopping countermodels, representation-only refinement, harmful reframing, evidence-versus-closure separation, all 64 combinations of six support-transport conditions, and stopping-terminal distinctions. A donor-complete programme additionally compares the atlas semantics to fixed-graph search, belief-space planning, planning abstractions, schema/lens preservation, goal evolution and world-model revision, and requires comparison against an ideal product of those donors rather than weak single-module baselines. The contribution is therefore not “adaptive search” or “changing graphs,” but a preservation semantics connecting representation/objective evolution to evidence reuse, reopening, censoring, and scientific stopping.

## 1. Introduction

A scientific search agent does not always know the search space it is searching. It may not know which domains contain relevant evidence, which ontology expresses the decisive distinction, whether two apparent routes are genuinely independent, or whether the current objective is the right proxy for the scientific goal. In such settings, “search” is not merely movement through a fixed graph.

Consider four cases.

- A literature search exhausts its current database interface but cannot establish that a censored archive contains no relevant work.
- A model receives a new representation that separates two situations previously aliased together; a policy impossible under the old representation becomes possible without any new raw observation.
- A scientific objective is revised. Previously collected evidence remains authentic and useful, but the old evidence no longer satisfies the new completion criterion.
- A world model changes its transition estimates while keeping the same state vocabulary; this is a model update, not necessarily a new epistemic topology.

These cases are often conflated as generic “adaptive search.” They involve different preservation questions. This paper introduces an epistemic-atlas formalism whose central object is not the ability to reframe, but the **transport contract** that says what survives a reframe.

### 1.1 Engulf-before-narrowing policy

The paper deliberately imports the strongest relevant structures from adjacent fields. Fixed-graph navigation is a chart-restricted special case. POMDP belief-state machinery can supply the within-chart state and value-of-information policy. Planning abstractions and homomorphisms can provide certified reachability or plan-preservation facts. Schema/lens/ontology mappings can supply semantic-preservation facts. Goal-evolving agents provide objective transformations. Self-evolving world models provide model updates and retained memory. None is treated as a weak strawman.

The ORION question is what **composes across them**. If a donor product with correct interfaces reproduces the same decisions, the contribution is an integration/preservation interface rather than superior expressivity. If an ORION-specific law yields a difference, that law must be isolated prospectively and tested against the donor-product super-baseline.

### 1.2 Contributions

**C1 — open-world stopping theorem with explicit premise.** We formalize observational extension ambiguity and prove that a history-only stopping rule cannot soundly certify task completion across observationally identical complete and incomplete admissible worlds. We explicitly reject the invalid converse that “no closure certificate” always implies ambiguity.

**C2 — fixed-information representation-refinement theorem.** We show that a representation refinement can strictly increase solvability while latent state, dynamics, goals, actions and retained raw sensing remain fixed. A matched coarsening demonstrates that reframing can also harm solvability.

**C3 — evidence/closure separation.** We prove that evidence can remain content-valid and semantically unchanged while a transformed scientific obligation is no longer discharged.

**C4 — complete support-transport criterion.** We define the preservation witness needed to carry closure across a chart/objective change. Complete witnesses transport closure; incomplete target-ambiguous witnesses require reopening; incomplete non-ambiguous cases remain `CANNOT_CHECK` until resolved.

**C5 — fail-closed stopping across representation change.** We preserve the distinction among `ROUTE_STOP`, `TASK_STOP`, `CONTINUE`, and `CANNOT_CHECK` across reframes, censored routes and resource exhaustion.

**C6 — donor-complete envelope.** We specify conservative embeddings for graph navigation, POMDPs, planning abstraction, schema/lens mappings, goal evolution and world-model revision, and require the strongest comparison to be their integrated product.

### 1.3 Non-contributions

We do not claim novelty for graph search, exploratory search, POMDP planning, learned or symbolic abstraction, schema evolution, bidirectional transformation, objective evolution, world-model revision, initial orientation, route diversification, or the P2 route-versus-task stopping result. The contribution is the scientific preservation layer at their interfaces.

## 2. Related work as donor structures

### 2.1 Fixed graph navigation

Search-on-Graph performs iterative observe-then-navigate reasoning over a knowledge graph rather than requiring a complete path plan in advance. This is a strong fixed-chart donor: the current graph schema is inspected at each step and navigation adapts locally. In P7, this behavior is recovered when atlas transformations are disabled.

The unresolved issue appears when the representation itself changes. A route result obtained under the old chart can remain valid evidence while its relation to the active scientific obligation changes.

### 2.2 Partial observability and belief-space planning

POMDP and information-gathering methods supply a principled account of uncertain state, belief update, action cost and value of information. P7 adopts this within-chart machinery where appropriate. It does not replace it.

The additional boundary is scientific completion: low expected information gain, low utility or resource exhaustion may rationally stop further action without establishing that every mandatory scientific obligation is satisfied.

### 2.3 Planning abstraction and representation change

Planning research has long shown that representation and abstraction affect solvability, search complexity and solution preservation. The canonical preservation result is ordered monotonicity [Knoblock 1994], which “guarantees that the structure of an abstract solution is not changed in the process of refining it”. Sound/complete abstraction or plan-preserving maps can therefore provide strong transport witnesses for reachability-related obligations.

This inheritance is not one-directional, and stating it as though it were would misrepresent the field. Abstraction is not free: hierarchies without a refinement guarantee can make search *exponentially worse*, and any scheme that transports an obligation across a representation change inherits that risk rather than escaping it. The nearest sources for both halves, including the downward refinement property and the negative result, are recorded under  with their retrieval status; only  has been verified against its primary source so far, and only it is cited here.

P7 does not claim the existence or value of abstraction. It asks what else must be preserved when the object being transported is a scientific closure certificate rather than only a plan property.

### 2.4 Schema evolution, lenses and ontology mappings

Schema transformation and bidirectional/lens formalisms provide mappings with round-trip or information-preservation laws. Ontology mappings can preserve semantic correspondences under explicit assumptions. These are natural donors for P7's `Rep` transformation layer.

However, data/semantic preservation is not automatically scientific closure preservation. A transformed objective can impose a different threshold or coverage condition even when the underlying evidence is identical.

### 2.5 Goal evolution

SAGA explicitly changes scientific objective functions in an outer loop while optimizing under the current objective in an inner loop. This is direct evidence that objective evolution should be treated as a first-class operation rather than an edge inside a fixed search graph.

P7 imports the operation and adds an epistemic constraint: objective change creates a new obligation-transport question. Prior evidence may remain reusable without inheriting the prior `DONE` judgment.

### 2.6 Evolving world models

Self-Evolving World Models revise deployment-time predictive context from action-transition experience and prediction-observation mismatch. This supplies a strong donor for intra-chart model revision. P7 distinguishes such parameter/model updates from inter-chart changes that alter state distinctions, route identity, ontology, or obligation semantics.

### 2.7 Search coverage and stopping

Open-world and parallel-world benchmarks expose failures in evidence coverage, sufficiency judgment and stopping. ORION Paper II already owns route independence, route-versus-task stopping, and fail-closed treatment of unresolved/censored coverage. P7 conservatively embeds those judgments and studies whether they remain sound after representation or objective change.

## 3. Formal setting

An epistemic chart is

\[
T=(S,A,\delta,Y,h,\Omega,\mathcal C),
\]

with latent states `S`, actions `A`, transition model `\delta`, retained raw observations/evidence alphabet `Y`, active representation `h:Y\to V`, obligations/objectives `\Omega`, and route/coverage/censoring constraints `\mathcal C`.

An atlas is

\[
\mathfrak A=(\{T_i\}_{i\in I},\mathcal R,\Xi),
\]

where `\mathcal R` is a set of partial chart/objective transformations and `\Xi` contains preservation contracts.

The split between raw signal and representation is important: it lets us distinguish **new sensing** from **new use of information already retained**.

## 4. Open-world stopping

A finite history does not generally identify the full world. Two admissible completions may agree on every observation so far while disagreeing on whether an unseen mandatory witness exists.

### Definition — extension ambiguity

History `h` is extension-ambiguous for mandatory obligations `O` when there exist admissible completions `W_0,W_1` with identical exposed history, every obligation discharged in `W_0`, and at least one mandatory obligation open in `W_1`.

### Theorem 1 — stopping impossibility

No rule depending only on `h` can soundly return `TASK_STOP` for every admissible completion when `h` is extension-ambiguous.

The proof is by indistinguishability: the rule must return the same result in both worlds but task completion differs.

### Boundary: absence of certificate is not ambiguity

A missing explicit closure certificate is not, by itself, a theorem that the world class contains both a complete and incomplete extension. P7 therefore introduces an **extension-richness** premise when deriving ambiguity from the absence of an excluding constraint.

This distinction matters in finite closed worlds: a system may know the universe is complete through a frozen manifest even if no object happens to be labeled “closure certificate.”

## 5. Route stop is not task stop

A route may be correctly exhausted while another route is censored, unavailable or unexecuted. Thus

\[
\bigwedge_r ROUTE\_STOP(r)\not\Rightarrow TASK\_STOP
\]

without a coverage premise.

P7 carries four terminals:

- `ROUTE_STOP`: local route policy says stop this route;
- `TASK_STOP`: all mandatory obligations are discharged or covered by valid completeness evidence;
- `CONTINUE`: an open mandatory obligation and admissible next action remain;
- `CANNOT_CHECK`: a mandatory obligation remains unresolved but required access/resource/evidence is unavailable.

This vocabulary prevents budget exhaustion from being silently converted into scientific completeness.

## 6. Strictness from representation refinement, not added information

A weak “topology change helps” result can be manufactured by adding a new goal state or new sensor. We instead freeze the latent problem.

Let

\[
L=(S,A,\delta,Y,r,G)
\]

with fixed states, actions, dynamics, raw sensing and goal semantics. A chart is only a representation `h:Y\to V`.

### Theorem 2 — fixed-information representation refinement can increase solvability

There exists `L` and charts `h,h'` over the same retained raw signals such that no deterministic stationary policy over `h` succeeds from every admissible start while one over `h'` does.

Construction: two starts require opposite actions. Their raw signals differ in a retained bit, but the coarse chart discards the bit and aliases them. The refined chart exposes the already-retained bit. No new state, action, transition, goal or sensor value is introduced.

### Negative control — coarsening can hurt

The reverse transformation destroys the distinction and strictly reduces worst-case solvability. Therefore “reframe” is not a monotonic-progress operator.

## 7. Evidence transport is not closure transport

Suppose evidence `e` remains exactly the same observation under a transformed objective.

### Theorem 3 — evidence/closure separation

There exist obligations `o,o'` and unchanged evidence `e` such that

\[
Sat(e,o)=true
\quad\text{but}\quad
Sat(e,o')=false.
\]

A minimal example uses evidence `x=5`, an old criterion `x>3`, and a new criterion `x>7`. The evidence remains valid; only the satisfaction semantics changed.

This theorem is central to engulfing goal-evolving systems: an objective generator may legitimately change the goal while the research memory remains valid. P7 adds the rule that the old completion authority does not follow automatically.

## 8. Support transport across chart change

For a closure certificate `z` of obligation `o`, define its complete support set to include every state/relation/semantic predicate/evidence identity/coverage premise/defeater-exclusion premise used in its derivation.

A complete transport witness establishes:

1. support nodes/relations map;
2. predicates, measurements and referents used by the certificate preserve meaning;
3. the obligation maps with the same relevant satisfaction semantics;
4. evidence identity and provenance remain content-bound;
5. coverage/completeness premises remain valid;
6. no unresolved new in-scope defeater appears.

### Theorem 4 — positive closure transport

A valid complete witness transports the certificate to the new chart.

### Theorem 5 — ambiguity-conditioned negative transport

If the witness is incomplete **and** the unresolved part admits two target completions consistent with all established facts—one preserving the certificate and one invalidating it—uniformly retaining closure is unsound. The navigator must reopen or return `CANNOT_CHECK`.

If transport is incomplete but the target model class is not ambiguous, P7 does not invent a counterexample. It returns `CANNOT_CHECK` unless another proof establishes preservation or failure.

## 9. Donor-complete embeddings

### 9.1 Search-on-Graph special case

Disable atlas transformations. Chart locations are graph entities, actions are graph hops/queries, and local observation exposes actual outgoing relations. P7 adds no extra behavior when its additional transport dimensions are inert.

### 9.2 POMDP special case

Let chart state be a belief distribution and action selection be a value-of-information policy. P7 accepts the donor's local action ranking. The only additional condition concerns scientific terminal authority when mandatory obligations remain open.

### 9.3 Planning-abstraction special case

A donor proof that an abstraction preserves a reachability or plan property instantiates the corresponding part of P7's preservation witness. P7 does not re-prove the donor's abstraction theorem.

### 9.4 Lens/schema special case

Round-trip or semantic-preservation laws instantiate the data/semantic portion of the witness. They do not, by themselves, satisfy unrelated scientific coverage or objective premises.

### 9.5 Goal-evolution special case

A new objective is accepted as a legitimate atlas transformation. Evidence is retained when content/provenance remains valid; closure is recomputed under the new satisfaction relation.

### 9.6 World-model special case

Prediction-model updates with a fixed vocabulary are intra-chart updates. A change that introduces/removes distinctions or redefines action/goal semantics is inter-chart and requires transport analysis.

## 10. Donor-product super-baseline

The strongest competitor is the integrated product of fixed-graph/POMDP navigation, abstraction mappings, schema transformations, objective evolution, world-model revision, provenance tracking and P2 stopping rules with correct adapters.

If this product implements the same transport semantics, P7 should **tie it** on behavioral decisions. That does not invalidate the theory; it means the contribution is a common scientific contract rather than extra expressive power.

A claim that ORION outperforms the product requires a prospective difference such as fewer inconsistent preservation judgments, lower proof duplication, smaller audit traces, better revocation/reopening precision, or a specific missing cross-module law. The programme will not declare superiority merely because ORION names all components in one tuple.

## 11. Deterministic theory support

The standard-library V2 checker verifies:

- an extension-ambiguous complete/incomplete pair;
- a closed-world counterexample to “no certificate implies ambiguity”;
- representation-only strict solvability under fixed latent information;
- harmful coarsening;
- unchanged evidence with changed closure truth;
- all 64 combinations of six transport-preservation dimensions;
- distinct route/task/continue/cannot-check terminals;
- fixed-chart identity embedding.

All authored checks pass. These are theorem-boundary tests, not empirical claims about deployed agents.

The programme-wide donor-envelope checker further freezes cross-structure cases involving representation + obligation, goal + provenance, censoring + resource stop, and other combinations. It also includes an ideal donor-product super-baseline, which is expected to tie the envelope when the interfaces are semantically identical.

## 12. Discussion

### 12.1 Why an atlas rather than a dynamic graph

A dynamic graph still invites one to treat every change as graph mutation. The atlas separates at least three operations:

1. movement inside a representation;
2. model update under fixed representation semantics;
3. representation/objective change requiring transport of prior epistemic state.

This distinction prevents a new world-model parameter estimate from triggering unnecessary closure invalidation, while also preventing a genuinely changed scientific objective from inheriting stale completion authority.

### 12.2 Preservation ladder

P7 occupies the middle of a wider ORION preservation ladder:

- computation/support may be preserved;
- evidence meaning may be preserved;
- target obligation discharge may fail to preserve;
- even discharged obligation may not imply commit authority in another domain.

Paper VI formalizes the computation/certification boundary; Paper VIII formalizes the obligation/authority boundary.

### 12.3 Falsifiers

P7 should be narrowed or merged if:

- every useful reframe can be represented without loss as an ordinary fixed-state transition and no transport judgment changes;
- the strongest donor product already provides the same complete evidence/closure preservation semantics and P7 adds no simpler proof, broader integration or measurable engineering benefit;
- harmful-reframe controls show that the proposed gating mechanism cannot distinguish beneficial from destructive representation changes;
- empirical open-world evaluations show no improvement on any protected measure while increasing cost or refusal.

## 13. Limitations

The representation-refinement theorem is an existence result under a deterministic stationary policy class; it is not a statement that every model class benefits from refinement. A history-dependent policy with access to retained raw state may simulate some refinements, so the policy/input interface must be declared explicitly.

The transport theorem assumes the soundness of its preservation witnesses. Constructing such witnesses automatically can itself be difficult and may require domain-specific proof tools.

Extension ambiguity depends on the admissible completion class. The theory does not license perpetual search merely because uncertainty exists; resource stopping remains valid as a resource decision and becomes `CANNOT_CHECK` when mandatory completion cannot be established.

Finally, this manuscript closes the theory, not the literature or empirical superiority question. The donor fields are broad and active; novelty and comparative performance require the programme's separate saturation and protected-evaluation gates.

## 14. Conclusion

Open-ended scientific navigation is not adequately characterized by “take another edge” once the representation or objective that defines edges and success can change. By engulfing fixed-graph navigation, belief-space planning, planning abstraction, schema transformation, goal evolution and world-model revision as donor structures, we isolate the shared missing scientific question: **what prior epistemic authority survives the transformation?**

The epistemic-atlas formalism answers this with explicit preservation contracts. It separates extension ambiguity from certificate absence, demonstrates representation-only solvability gains and harms under fixed information, proves that evidence preservation is weaker than closure preservation, and makes support transport and fail-closed stopping explicit.

**Theory terminal:** `CLOSED_V2`.

## References

1. Jia Ao Sun et al. **Search-on-Graph: Iterative Informed Navigation for Large Language Model Reasoning on Knowledge Graphs.** arXiv:2510.08825, 2025.
2. Yuanqi Du et al. **Accelerating Scientific Discovery with Autonomous Goal-evolving Agents.** arXiv:2512.21782, 2025.
3. Xuan Zhang et al. **Self-Evolving World Models for LLM Agent Planning.** arXiv:2606.30639, 2026.
4. Alexander Newell and Herbert Simon. Classical problem-space/search formulations; modern planning/POMDP literature provides the fixed-representation and partial-observability parents used here.
5. Planning abstraction and homomorphism literature on sound/complete abstraction and plan preservation is treated as a donor family rather than a single ownership claim.
6. Bidirectional transformation/lens and schema-evolution literature supplies data/semantic preservation structures used as transport witnesses.
7. ORION Paper II. **Open-World Scientific Discovery.** Internal programme owner of route independence and route/task stopping semantics.

## Artifact map

- Closed formal theory: `FORMAL_CORE_V2.md`
- Deterministic theorem checker: `../formal/check_theory_closure_v2.py`
- Donor-complete programme: `../../DONOR_COMPLETE_ORION_ENVELOPE_V1.md`
- Earlier exploratory draft: `DRAFT.md`
- Claim authority: `../CLAIM_LEDGER_V2.md`
- Reproduction: `../REPRODUCE.md`
