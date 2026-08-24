# P7 formal core V2 — closed theory

**Candidate paper:** Epistemic Navigation in Open Worlds  
**Theory terminal:** `CLOSED_V2`  
**Novelty / external-evidence terminal:** `CANNOT_CHECK`  
**Date:** 2026-08-18

This V2 closes the logical gaps identified in V1 and hostile review. The theory is complete as a mathematical object; it does not claim that representation change, abstraction, open-world search, or scientific exploration are themselves new.

## 1. Charts, atlases and navigation state

### Definition 1 — epistemic chart

An epistemic chart is

\[
T=(S,A,\delta,Y,h,\Omega,\mathcal C),
\]

where:

- `S` is a latent state set;
- `A` is an action/navigation set;
- `\delta` is the latent transition relation or kernel;
- `Y` is the retained raw observation/evidence alphabet available to the inquiry;
- `h:Y\to V` is the active representation map producing chart locations/observations `V`;
- `\Omega` is the typed obligation/objective family interpreted in the chart;
- `\mathcal C` records route, coverage and censoring constraints.

The explicit latent/raw/representation split is used only when needed. In a purely symbolic graph chart it may collapse to the usual graph representation.

### Definition 2 — epistemic atlas

An epistemic atlas is

\[
\mathfrak A=(\{T_i\}_{i\in I},\mathcal R,\Xi),
\]

where `\mathcal R` is a set of partial chart/objective transformations and `\Xi` is the family of preservation contracts controlling transport of evidence, support, obligations and closure certificates.

### Definition 3 — navigation state

\[
N=(\mathfrak A,i,b,F,R,O,C,V_h,B,H),
\]

where `i` is the active chart, `b` is the current location/belief state, `F` is frontier, `R` registered routes, `O` active mandatory obligations, `C` censored/unavailable/unknown-coverage state, `V_h` visited evidence/location history, `B` resources, and `H` action/reframe history.

## 2. Histories and admissible completions

### Definition 4 — observational equivalence

World/atlas instances `W_0,W_1` are observationally equivalent at finite history `h`, written

\[
W_0\equiv_h W_1,
\]

iff every observation, route response, exposed cost, action result, active-chart fact and declared coverage fact visible along `h` is identical.

### Definition 5 — admissible completion

An admissible completion of `h` is a world/atlas instance preserving all facts in `h` and all frozen structural/coverage constraints while allowing any unobserved state, route, defeater or obligation condition not excluded by those constraints.

### Definition 6 — extension ambiguity

History `h` is extension-ambiguous for mandatory obligation family `O` iff there exist admissible completions `W_0,W_1` such that

1. `W_0\equiv_h W_1`;
2. every obligation in `O` is discharged in `W_0`;
3. at least one obligation in `O` remains open in `W_1`.

### Theorem 1 — open-world stopping impossibility

If `h` is extension-ambiguous for `O`, no stopping rule that depends only on `h` can soundly output `TASK_STOP` for every admissible completion of `h`.

#### Proof

The rule receives identical input on `W_0,W_1`, hence returns the same decision. `TASK_STOP` is false in `W_1`; any other decision does not certify completion in `W_0`. Therefore history alone cannot distinguish the completion truth value. `\square`

### Important converse boundary

Absence of an explicit closure certificate does not logically imply extension ambiguity. A model class may contain only one complete admissible world, or completeness may follow from a constraint not represented by the chosen certificate object.

### Definition 7 — extension-rich world class

A world class is extension-rich at `h` for obligation `o` iff, whenever the exposed constraints do not exclude an unseen witness relevant to `o`, both a completion without such a witness and an observationally equivalent completion with one are admissible.

### Corollary 1.1

In an extension-rich class, absence of a constraint excluding an unseen mandatory witness implies extension ambiguity, so Theorem 1 applies.

This explicit richness premise repairs the over-strong negative direction of V1.

## 3. Route stop, task stop and `CANNOT_CHECK`

### Definition 8 — terminal vocabulary

- `ROUTE_STOP(r)`: the frozen local route policy licenses suspending route `r`.
- `TASK_STOP`: every mandatory obligation is discharged or covered by a valid completeness certificate.
- `CONTINUE`: at least one mandatory obligation is open and an admissible next action remains.
- `CANNOT_CHECK`: at least one mandatory obligation is unresolved and the required information/action is unavailable under the current resource/access state.

### Proposition 2 — local route stop does not imply global task stop

\[
\bigwedge_{r\in R_{executed}}ROUTE\_STOP(r)
\not\Rightarrow TASK\_STOP
\]

without a premise establishing that executed routes cover every mandatory obligation.

#### Proof by construction

Take one exhausted executed route and a second unexecuted or censored route that alone can reach an open mandatory witness. The first route is correctly stopped while the task is incomplete. `\square`

P2 already owns this local/global stopping distinction in ORION; P7 embeds it as an invariant across chart change.

### Definition 8.1 — route identity, equivalence and refinement

A route identity binds the chart and active objective, the initial mandatory
obligation set, and the normalized action/observation/evidence trace. Observed
content overlap alone never determines route identity.

Two routes are structurally equivalent only through a protected bijection that
preserves adjacency/action availability, evidence identity, obligation labels
and terminal semantics. A route `r'` refines `r` when a declared projection
from `r'` to `r` preserves every old relation/obligation while `r'` may expose
additional distinctions. A route is genuinely new relative to an archive only
when no archived route is structurally equivalent and no declared
refinement/projection reduces it to an archived route with the same reachable
obligations and terminal semantics.

### Definition 8.2 — recovery transitions

- `DEFER_REVISIT(r,o,t)` stores the exact open obligation and a protected
  revisit trigger; it is neither route nor task completion.
- `BACKTRACK(r,v)` returns to a recorded frontier only when the failed suffix
  has a dead-end, loop or violated-premise witness and an admissible alternative
  remains.
- `FORCED_REFRAME` is licensed only when the current chart has no authorized
  action capable of resolving an active mandatory obligation and a candidate
  chart makes a relevant distinction expressible; closure is transported only
  by the contracts below and otherwise reopens.

A dead end has no admissible successor. A loop repeats the normalized
chart/location/objective/open-obligation state without new support. A deceptive
local optimum is not declared from low marginal gain alone: it requires an
independent witness that another reachable route can improve an unresolved
mandatory obligation. These are recovery predicates, not new navigation
algorithms.

## 4. Representation-only refinement under fixed latent information

The V1 strictness witness added a newly represented goal state. That established only that a larger model can solve more tasks. V2 freezes the latent world, dynamics, goals and raw sensing and changes only the representation applied to retained information.

### Definition 9 — chart refinement on fixed latent information

Let a latent problem be

\[
L=(S,A,\delta,Y,r,G),
\]

where raw sensing `r:S\to Y` and goal semantics `G` are fixed. A chart is an observation/representation map `h:Y\to V`. A refinement `h'` of `h` may distinguish raw signals that `h` aliases but may not introduce a new latent state, action, transition, goal fact or sensor value.

A chart-restricted stationary policy has form `\pi:V\to A`.

### Theorem 3 — strict solvability gain from representation refinement

There exists a fixed latent problem `L` and two charts `h,h'` over the same raw signal such that no deterministic stationary policy over `h` succeeds from all admissible starts, while a deterministic stationary policy over `h'` does.

#### Proof by finite construction

Let `S={s_0,s_1}`, `A={a_0,a_1}`. Success from `s_0` requires `a_0`; success from `s_1` requires `a_1`. Let the retained raw signals be `r(s_0)=(u,0)` and `r(s_1)=(u,1)`. The coarse chart maps both raw signals to `u`; every deterministic stationary policy must therefore choose the same action in both starts and fails one. The refined chart maps the two retained raw signals to distinct locations, so the policy choosing `a_0` on `(u,0)` and `a_1` on `(u,1)` succeeds on both. No latent state, transition, goal or raw observation has changed. `\square`

### Proposition 3.1 — reframe is not monotone

The reverse coarsening from `h'` to `h` strictly reduces worst-case solvability in the same construction. Therefore representation change cannot be assumed beneficial merely because it changes topology.

This negative control is mandatory in P7 evaluation.

## 5. Reframes and transport contracts

### Definition 10 — reframe

A reframe is

\[
\rho=(T,T',\phi_V,\phi_E,\phi_\Omega,\Pi),
\]

where location/relation/obligation maps may be partial and `\Pi` contains explicit preservation facts.

An admissible reframe must be authorized by the relevant responsibility/authority rule, retain content-bound evidence identity, and reopen or mark `CANNOT_CHECK` every prior closure whose support/obligation semantics are not transported.

## 6. Evidence preservation is weaker than closure preservation

### Definition 11 — evidence transport

Evidence item `e` transports when its content identity, provenance and proposition/measurement semantics remain valid in the target chart.

### Definition 12 — obligation transport

Obligation `o` transports to `o'` when the transformation preserves the satisfaction relation relevant to the old certificate:

\[
Sat_T(e,o)\Longleftrightarrow Sat_{T'}(\phi(e),o')
\]

for every support item and defeater within the certificate's declared scope.

### Theorem 4 — evidence-preservation/closure-separation

There exist chart/objective transformations preserving an evidence item exactly while invalidating the closure judgment previously supported by it.

#### Proof by construction

Let evidence `e` be the unchanged measurement `x=5`. Let old obligation `o` require `x>3`, so `Sat(e,o)` holds. Let the transformed objective `o'` require `x>7`. Evidence identity, provenance and measured value remain unchanged, but `Sat(e,o')` is false. Hence evidence transport does not imply closure transport. `\square`

### Corollary 4.1

Objective evolution can reuse evidence without inheriting the old completion judgment.

This is the central bridge to goal-evolving scientific systems.

## 7. Complete support transport

For a certificate `z` closing obligation `o`, let `Supp_T(z,o)` contain every state/relation/semantic predicate/evidence identity/coverage premise/defeater-exclusion premise used by its derivation.

### Definition 13 — complete transport witness

A witness `\Pi(z,o,\rho)` is complete iff it establishes:

1. all support nodes and relations used by `z` are mapped;
2. every predicate/measurement/referent used by `z` is semantics-preserved;
3. `o` maps to `o'` with the same relevant satisfaction relation;
4. evidence identity/provenance remains content-bound;
5. coverage/completeness premises used by `z` remain valid;
6. no new in-scope defeater is admitted without being resolved.

### Theorem 5 — positive closure transport

If `\Pi(z,o,\rho)` is complete and valid, `z` has a transported certificate `z'` for `o'` in `T'`.

#### Proof

Transport the derivation of `z` step by step through the mapped support objects. Conditions 1–5 preserve every positive premise and inference relation; condition 6 preserves the absence-of-defeater premise within the declared scope. Therefore the target derivation remains valid. `\square`

### Definition 14 — target ambiguity after incomplete transport

An incomplete witness is target-ambiguous iff there exist two target completions consistent with every established mapping fact, one preserving the old certificate derivation and one invalidating it.

### Theorem 6 — fail-closed negative transport

If the transport witness for a previously closed obligation is incomplete and target-ambiguous, every uniformly sound navigator must reopen the obligation or return `CANNOT_CHECK`; retaining closure is unsound.

#### Proof

The two target completions are indistinguishable given the established transport facts but disagree on certificate validity. Any policy retaining closure on that information is wrong in the invalidating completion. `\square`

### Boundary

If the witness is incomplete but the admissible target class is not ambiguous, the theory does **not** infer semantic failure. The correct epistemic terminal is `CANNOT_CHECK` unless another proof establishes preservation or failure. This closes the V1 logical gap.

## 8. Fail-closed task stopping through reframes

### Definition 15 — mandatory-open

An obligation is mandatory-open iff it is neither discharged nor covered by a current valid closure certificate.

### Theorem 7 — reframe-safe task-stop invariant

In any trace enforcing

\[
TASK\_STOP\Rightarrow\neg\exists o\;MandatoryOpen(o),
\]

none of route exhaustion, low utility, budget depletion, repeated observations, successful evidence transport, or a chart reframe can alone derive `TASK_STOP`.

#### Proof

None of the listed events, by itself, changes the discharge/closure status of every mandatory-open obligation. The implication therefore remains blocking until an authorized obligation-state transition occurs. `\square`

If resources end while an obligation remains open, the appropriate terminal is `CANNOT_CHECK`, not scientific completeness.

## 9. Orientation as a typed obligation

### Definition 16 — orientation obligation

An orientation obligation requires enough scope, ontology or action-interface information to make ordinary route/query actions semantically interpretable in the current chart.

### Proposition 8

There exist navigation problems where no route utility is well-defined before an orientation variable is resolved because the action labels themselves do not yet have stable semantics. A scope-revelation step can therefore be epistemically prior to route optimization.

This embeds the Initial Exploration Problem; P7 does not claim orientation as new.

## 10. Fixed-chart and planning-abstraction special cases

### Proposition 9 — fixed-chart navigation

Disable atlas transformations and objective changes. P7 reduces to ordinary navigation over one chart with the same route/action/observation semantics. Graph search and POMDP/belief-space policies can therefore be represented as special cases when their assumptions are supplied.

### Proposition 10 — sound planning abstraction as a transport witness

If a planning abstraction map is sound/complete for the properties used by a P7 obligation and its certificate, those established preservation facts can instantiate the corresponding fields of `\Pi`. P7 does not replace planning abstraction theory; it consumes its preservation result when deciding scientific closure transport.

### Proposition 11 — schema/lens preservation as a transport witness

A schema transformation or bidirectional mapping that proves preservation of a data/semantic property may instantiate the relevant semantic component of `\Pi`, but cannot by itself establish unrelated scientific coverage, objective or authority premises.

These propositions state the assimilation boundary rather than a subsumption claim.

## 11. Breadth and exploration

Let `Region(h)` be the set of semantically distinct relevant regions reached by a history and `Red(h)` a redundancy measure. Exploration breadth is observable but not intrinsically good:

- low breadth can miss relevant regions;
- high breadth can waste resources without advancing mandatory obligations.

Therefore P7 treats breadth as a diagnostic coordinate, not a scalar objective that can override closure or resource invariants.

## 12. Executable support

`formal/check_theory_closure_v2.py` deterministically checks:

- the extension-ambiguity stopping witness;
- a counterexample to `no certificate => ambiguity` without richness;
- fixed-latent, fixed-sensing representation-refinement strictness;
- harmful coarsening;
- evidence-preserved/closure-broken objective change;
- all 64 combinations of the six support-transport coordinates, each paired with each of the 15 admissible target completion classes, so Definition 14 target-ambiguity is decided per case rather than supplied — 960 cases;
- distinct `ROUTE_STOP`, `TASK_STOP`, `CONTINUE`, `CANNOT_CHECK` terminals;
- fixed-chart identity special case.

The checker is standard-library only and is mathematical support, not a benchmark result about deployed agents.

## 13. Prior-work ownership and final residual

The following are donor or internally owned, not P7 inventions:

- ordinary graph exploration/search and knowledge-graph navigation;
- exploratory search/information foraging;
- POMDP and belief-space information gathering;
- planning abstraction, homomorphism and representation-language change;
- schema evolution, ontology mapping and lens/bidirectional transformation preservation;
- objective/goal evolution;
- world-model revision and dynamic graph representations;
- orientation/initial exploration;
- P2 route independence and route/task stopping;
- generic scientific-search breadth metrics.

The completed P7 theoretical object is:

\[
\boxed{
\text{open-world epistemic atlas}
+
\text{fixed-information representation refinement}
+
\text{evidence/closure transport separation}
+
\text{ambiguity-conditioned reopening}
+
\text{fail-closed scientific stopping}
}
\]

Its strongest internal result is not “graphs can change.” It is that representation/objective changes require a typed preservation account because the same evidence can remain valid while reachability, obligation meaning and scientific closure change independently.

## 14. Final theory terminal

There are no remaining mathematical `THEOREM TARGET` placeholders in V2.

- `P7_THEORY = CLOSED_V2`
- `P7_NOVELTY = CANNOT_CHECK_UNTIL_LITERATURE_CLOSURE`
- `P7_EXTERNAL_AGENT_PERFORMANCE = OPEN_IF_CLAIMED`

A later empirical failure does not make the theory incomplete; it changes the empirical claim or publication disposition.

## Addendum (2026-08-24): the exact containment replacement

`P7.CONTAIN.EXACT_BRIDGE_RULE.V1` replaces the intermediate-contract test
`Match(a, b) := a = b OR Bridge(a, b)` in the coordinate transport axiom with
exact containment `Contains(a, b) := forall o. Demands(b, o) -> Demands(a, o)`,
everything else in the calculus unchanged. Discharged by solver refutation and
by closed-world witnesses (`src/orion/study/p7/exact_containment.py`):

- `REFLEXIVITY_OF_CONTAINMENT`, `TRANSITIVITY_OF_CONTAINMENT`
- `EXACT_RULE_IS_SOUND`, `EXACT_RULE_IS_NOT_DROPPABLE`
- `EXACT_RULE_SUBSUMES_THE_BRIDGE_RULE`,
  `CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH`
- `LEFT_IDENTITY_UNDER_EXACT_RULE`, `RIGHT_IDENTITY_UNDER_EXACT_RULE`,
  `IDENTITY_STRICT_UNDER_EXACT_RULE`
- `ASSOCIATIVITY_OBSERVABLE_UNDER_EXACT_RULE`,
  `ASSOCIATIVITY_STRICT_UNDER_EXACT_RULE`
- `EXACT_CALCULUS_IS_SATISFIABLE` (the vacuity guard: the axiom set has a
  model, so the PROVED lines are not free facts from a contradiction)

The incompleteness theorem about the *old* rule is not retracted; it is the
reason the replacement exists. `P7_THEORY = CLOSED_V2` plus this addendum.
