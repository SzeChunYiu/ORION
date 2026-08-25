# Knowledge-Web Navigation, Proof Economy, ORION-Q Transfer, and Recursive Self-Application

## Status

```text
identity = ORION Discovery V2 knowledge-web successor
relationship_to_v1 = ADDITIVE; V1 theorem identities remain frozen
paper_authority_delta = NONE
present_day_discovery_authority = NONE
quantum_scientific_authority_transfer = FORBIDDEN
external_novelty_authority = CANNOT_CHECK
external_adoption_authority = CANNOT_CHECK
```

This document completes the theory and executable reference contracts that can
be established without prospective protected outcomes or external authority.
It does not claim that the registered discovery morphology is universal, that
ORION autonomously generates frontier breakthroughs, or that a same-programme
self-study authorizes its own adoption.

---

# 1. Why a second discovery layer is necessary

The knowledge available to a research programme is not a list.  It is a
changing, typed, partially observed graph containing questions, objects,
assumptions, representations, mechanisms, methods, experiments, instruments,
validators, evidence, donors, costs, failures, claims, and authority records.
A correct solution may require a conjunction such as:

```text
new object
× transferred invariant
× changed representation
× donor theorem
× target-native validator
× one discriminating experiment
× an authority bridge
```

Finding any one item is insufficient.  A single path through the graph can
look persuasive while omitting another load-bearing ingredient.  Conversely,
several alternative support families may exist, and destroying one family
need not destroy the target claim.

Earlier ORION work already supplies important parents:

- Discovery morphology studies how historical breakthroughs may be described
  without claiming access to private cognition or a universal atom basis.
- Recursive atom studies test proposed operators against strongest parents,
  no-atom controls, interaction effects, and stop rules.
- Discovery V1 separates proposal origin, bounded reach, theorem
  identifiability, model chronology, counterfactual twins, and prospective
  escrow.
- The dual-harness negative-resolution programme freezes atomic root cause,
  donor subtraction, one-ingredient successors, and no-solution stopping.
- ORION-EA treats the epistemic state and its representation language as
  mutable research objects.
- The synchronization contract states that papers, framework semantics, and
  harnesses are projections of one scientific object, not independent files.
- ORION-Q contributes exact obstruction finding, certified representation
  changes, finite-size saturation, resource-vector accounting, and
  donor-first refusal.

The residual is therefore narrower:

> Build an auditable calculus for locating complete support in a knowledge
> web, selecting the next information- or proof-bearing move, minimizing
> effort subject to hard scientific obligations, propagating semantic change,
> transferring exact structures across domains without transferring
> authority, and applying the process recursively to ORION itself.

---

# 2. Expert cell and veto roles

The theory is reviewed as if by a small, adversarial research group.

## 2.1 Formal discovery theorist

Owns typed nodes, edges, support families, closure, theorem statements,
countermodels, and the distinction between a graph path and conjunctive
scientific support.

Veto: no prose-only “all ingredients found” claim without a support-family
receipt.

## 2.2 Algorithms and complexity scientist

Owns navigation search, exact finite correspondence, Pareto proof planning,
set-cover/hitting-set reductions, resource caps, and termination.

Veto: no “least effort” claim produced by an undeclared scalar objective.

## 2.3 Cognitive scientist and historian of discovery

Owns problem finding, hypothesis/experiment/representation/paradigm search,
analogy, impasse and representational change, mechanism construction, and
historical episode limitations.

Veto: no universal human-discovery law inferred from a selected historical
atlas.

## 2.4 Experimental and causal scientist

Owns target-relevant information gain, intervention design, measurement
semantics, instrument feasibility, hidden consequences, and held-out
transfer.

Veto: more observations do not count as progress unless they refine a
responsibility-relevant ambiguity.

## 2.5 Quantum structures and resources scientist

Owns exact ORION-Q transfer: obstruction certificates, structural
correspondence, representation cost, circuit/resource burden, finite-size
saturation, and native quantum validators.

Veto: a method learned in quantum research may transfer; a quantum result or
quantum novelty claim may not.

## 2.6 Verification, authority, and synchronization scientist

Owns proposal/evaluator/adopter separation, successor identity, change-impact
receipts, paper/framework/harness synchronization, content binding, and
negative-history retention.

Veto: local hashes, same-owner CI, or internal agreement do not create
external scientific authority.

---

# 3. Six coupled search spaces

Human and machine scientific problem solving should not be modelled as one
flat candidate search.  The minimum useful decomposition is:

1. **Problem/question space** — which responsibility is worth posing, and
   whether the problem statement itself is defective or incomplete.
2. **Hypothesis/mechanism space** — candidate laws, explanations, models, and
   causal mechanisms.
3. **Representation/ontology space** — objects, variables, coordinates,
   equivalence relations, abstractions, and languages in which candidates can
   be expressed.
4. **Experiment/instrument space** — interventions, measurements,
   counterfactuals, apparatus, and experimental paradigms.
5. **Proof/evidence space** — counterexamples, constructions, reductions,
   exhaustive finite checks, formal proofs, transfer evidence, and external
   review.
6. **Authority/adoption space** — who may validate, interpret, publish, or
   adopt the result.

A move in one space changes the reachable moves in the others.  For example:

- a representation change can make a short proof available;
- a new instrument can make a previously non-identifiable mechanism testable;
- a counterexample can show that the theorem, not the implementation, must be
  narrowed;
- an external authority requirement can make an otherwise cheap local proof
  inadequate for the claimed terminal.

This six-space model strictly contains the familiar donor-composition,
cross-domain transfer, and partial-invention patterns, while retaining an
explicit `OPEN_MOVE_CLASS` when the useful move does not fit the current
morphology.

---

# 4. Typed knowledge web

Define a finite registered knowledge web

\[
G=(N,E,\mathcal S,\tau_N,\tau_E,\iota),
\]

where:

- `N` is a set of content-identified nodes;
- `E` is a set of typed directed edges;
- `S` is a family of alternative support hyperedges;
- `tau_N` assigns node kinds;
- `tau_E` assigns edge kinds;
- `iota` binds content identity, domain, scope, and version.

## 4.1 Node kinds

```text
QUESTION / OBJECT / REPRESENTATION / ASSUMPTION
HYPOTHESIS / MECHANISM / INVARIANT
METHOD / OPERATOR
EXPERIMENT / INSTRUMENT
VALIDATOR / EVIDENCE
DONOR / RESOURCE / AUTHORITY / FAILURE / CLAIM
THEORY / CODE / HARNESS / PAPER / MANIFEST / ISSUE
OPEN_MOVE_CLASS
```

`OPEN_MOVE_CLASS` is mandatory.  A fixed taxonomy is an experimental language,
not a proof that every future discovery is expressible within it.

## 4.2 Edge kinds

```text
DEPENDS_ON / DERIVES / REFINES / CORRESPONDS_TO
ANALOGOUS_TO / COMPOSES_WITH / CONTRADICTS / OBSTRUCTS
EXPLAINS / PREDICTS / DISTINGUISHES / VALIDATES
SUBSUMES / REOPENS / COSTS / AUTHORIZES / SYNCHRONIZES
```

Each edge records whether it is load-bearing and whether a change at the
source reopens the target.

## 4.3 Alternative support families

For target `t`, a support family is

\[
S_i(t)=(N_i,E_i).
\]

The target is supported by the registered web iff

\[
\exists i\;[N_i\subseteq N_{available}\land E_i\subseteq E_{available}].
\]

This is deliberately a hypergraph condition.  A single route from a premise
to a conclusion cannot represent a conjunction such as “native validity and
target sufficiency and authority.”

The support receipt must report, per family:

```text
present nodes
missing nodes
present edges
missing edges
complete / incomplete
best remaining gap
```

A family can be donor-subsumed, refuted, or unavailable without forcing the
same disposition on every other family.

---

# 5. Ingredient discovery and navigation

Navigation is not “retrieve many documents.”  It is the controlled selection
of a graph observation or graph rewrite that is expected to close a
load-bearing support gap.

## 5.1 Atomic navigation cycle

```text
1. Freeze target responsibility and terminal family.
2. Enumerate registered support families and alternatives.
3. Compute present and missing ingredients per family.
4. Classify each missing item:
   RETRIEVABLE / DERIVABLE / TRANSFERABLE / EXPERIMENTALLY_OBSERVABLE /
   INVENTION_REQUIRED / AUTHORITY_REQUIRED / UNRESOLVED.
5. Generate candidate moves in all six spaces.
6. Predict which exact support gaps each move can close.
7. Attach proposal origin, cost vector, and failure terminals.
8. Select an intervention or proof plan on the Pareto frontier.
9. Execute under a theorem-identifying harness.
10. Update the web, negative history, and change-impact receipt.
11. Stop, recurse on a residual, or open `OPEN_MOVE_CLASS`.
```

## 5.2 Navigation portfolio

No one navigation policy is universally adequate.  Register at least:

- **dependency closure** — find every load-bearing ancestor of a target;
- **support-family gap search** — find the nearest complete alternative
  support family;
- **counterexample-guided refinement** — refine only where an abstract route
  admits a spurious success or failure;
- **delta reduction** — minimize a failure-inducing or theorem-breaking
  ingredient set;
- **target-information acquisition** — choose an experiment that separates
  states requiring different terminals;
- **relational analogy search** — map higher-order relations, not surface
  attributes, and require a target-native validator;
- **representation-change search** — relax constraints or decompose chunks
  when the incumbent representation causes an impasse;
- **concept/knowledge co-expansion** — permit candidate concepts not yet true
  or false in current knowledge while separately expanding the knowledge
  needed to decide them;
- **unknown-morphology search** — return `OPEN_MOVE_CLASS` rather than forcing
  an ill-fitting registered operator.

## 5.3 Target-information condition

Let the current observable interface induce partition `Pi` over scientific
states and let target terminal map be `T`.  An acquisition `a` is
responsibility-informative only when the refined partition `Pi_a` separates
at least one pair previously joined by `Pi` but separated by `T`:

\[
\exists x,y:\;x\sim_{\Pi}y,\;T(x)\ne T(y),\;x\not\sim_{\Pi_a}y.
\]

Information gain relative to the wrong fixed hypothesis space is not enough;
the navigation system must also retain representation- and ontology-change
moves.

---

# 6. Proof economy — proving enough with the least justified effort

“Least effort” is responsibility-relative and vector-valued.  Define a proof
or evidence cost contract

\[
c=(c_{compute},c_{human},c_{experiment},c_{external},c_{elapsed},\ldots).
\]

Without an independently supplied preference or price vector, two adequate
plans may be Pareto-incomparable.  The framework may return the Pareto set; it
may not invent an exchange rate after seeing which plan makes ORION look
best.

## 6.1 Obligation-specific cheapest evidence

Use the logically weakest adequate evidence class:

| Responsibility | Least adequate evidence, when its premises hold |
|---|---|
| Refute a universal statement | One valid counterexample |
| Establish existence | One independently checked constructive witness |
| Establish a finite universal | Exhaustive enumeration of the exact class, or a proof |
| Establish necessity | Matched countermodels or a deletion/ablation theorem |
| Establish sufficiency | A construction plus verification of every premise |
| Establish equivalence | Two reductions/correspondence directions, or a biconditional proof |
| Establish minimality | Witness plus exclusion of every strictly smaller candidate |
| Isolate failure cause | Minimal failure-inducing difference under a stable failure predicate |
| Refine an abstraction | One real/spurious counterexample followed by the smallest separating refinement |
| Establish causal mechanism | Intervention under exclusion/transport assumptions |
| Establish transfer | Counterfactual twin or held-out target family with target-native validation |
| Establish novelty | Independent prior-art and donor-subtraction review |
| Establish adoption | External authorized disposition |

A cheaper evidence object that lacks the required authority is not adequate.
A more expensive object that merely repeats an already decisive witness is
not automatically stronger.

## 6.2 Exact proof-plan problem

Let obligations be `O={o_1,...,o_m}` and proof options be `P={p_1,...,p_n}`.
Each option has:

```text
method
scope
preconditions
discharged obligations
authority class
cost vector
```

A plan is adequate iff every obligation has at least one accepted discharge
with an accepted authority and every hard precondition is attained.  The
reference implementation enumerates exact adequate subsets for bounded `n`
and returns the Pareto-minimal plans.

This is a typed set-cover problem with hard method and authority constraints,
not a scalar “proof score.”

## 6.3 Fail-closed cases

```text
empty hard stratum                  -> NOT_EXERCISED
solver timeout without lower bound  -> CANNOT_CHECK
same-programme review for novelty   -> CANNOT_CHECK
one path for a conjunctive theorem  -> INCOMPLETE_SUPPORT
post-outcome change of objective    -> NEW_STUDY_IDENTITY
implicit resource scalarization     -> INVALID_COST_COMPARISON
```

---

# 7. What human problem decomposition contributes

The historical and cognitive literature suggests several durable but
non-universal principles that should be registered as testable navigation
operators rather than as folklore.

## 7.1 Problem finding precedes solution search

High-value work often begins by changing what is asked, identifying a latent
opportunity, or replacing a supplied problem with a more generative one.
Therefore ORION needs question-origin and question-value records, not merely a
solver for owner-supplied tasks.

## 7.2 Hypothesis and experiment search interact

Scientists alternate between candidate explanations and experiments; failed
hypothesis generation can be repaired by generalizing from experimental
results.  A planner that searches only hypotheses or only experiments is
structurally incomplete.

## 7.3 Representation and experimental paradigm are separate spaces

Discoveries often require new descriptive features and new procedures, not
merely a new parameter value in an old model.  Representation and instrument
moves must therefore remain first-class.

## 7.4 Analogy transfers relational systems

Cross-domain transfer should preserve relational structure and higher-order
systematicity.  Shared labels, visual resemblance, or matching keywords are
not enough.

## 7.5 Impasse may diagnose a representation, not a hard search

Constraint relaxation and chunk decomposition can reveal solutions excluded
by the initial encoding.  ORION must distinguish “search harder” from
“change what counts as a legal state or move.”

## 7.6 Mechanism discovery is staged

Construction, evaluation, and revision are distinct.  Useful strategies
include schema instantiation, modular subassembly, and forward/backward
chaining from known activities or target phenomena.

## 7.7 Complex problems are often nearly decomposable, not independent

Atomic work should exploit modules and stable intermediate objects while
retaining explicit cross-module interactions.  “Atomic” means separately
falsifiable and composable, not context-free.

## 7.8 Concepts and knowledge co-expand

Some useful candidates are not decidable within current knowledge.  A
concept-space expansion may require a paired knowledge-acquisition plan rather
than immediate acceptance or rejection.

## 7.9 Counterexamples and reductions compress work

One valid counterexample can end a universal claim.  Minimal failure
reduction and counterexample-guided refinement should be preferred over
blindly enlarging a campaign.

## 7.10 No fixed principle list is final

The discovery-morphology and recursive-atom programmes already show that
broad labels split, interact, become donor-subsumed, or remain
non-identifiable.  The framework therefore registers these principles as a
portfolio and retains an open-class terminal.

---

# 8. ORION-Q as an exact transfer and falsification domain

ORION-Q is useful in four sharply bounded ways.

## 8.1 Exact obstruction certificates

Quantum and adjacent combinatorial problems often expose exact finite
obstructions, symmetry classes, rank/support constraints, and saturation
phenomena.  These are ideal for testing whether the navigator can identify a
missing ingredient rather than merely allocate more search.

## 8.2 Representation versus implementation cost

A representation or stochastic relaxation may improve a proxy objective yet
lose after circuit realization, compilation, depth, noise, or sampling cost
is charged.  This directly tests vector proof/resource accounting and guards
against answer laundering through preprocessing.

## 8.3 Certified coarse-to-fine navigation

Symmetry quotienting, bounded-defect localization, finite-size saturation,
and exact-referee-first escalation provide reusable navigation patterns.
Their transfer requires a relational correspondence and a target-native
validator.

## 8.4 Hard anti-overclaim domain

Quantum terminology makes authority laundering easy: a quantum-inspired
method, a simulator result, a circuit construction, and a physical advantage
claim are different objects.  ORION-Q is therefore a useful hostile test of
typed claim boundaries.

## 8.5 Transfer contract

A transfer from source domain `D_s` to target domain `D_t` is only a
structural candidate when it carries:

```text
relational correspondence
strongest-parent / donor-first refusal
target-native validator
matched vector resource contract
explicit non-transfer of scientific authority
```

Surface analogy, absent target validation, or inherited quantum authority is
invalid.

---

# 9. Recursive ORION-on-ORION science

ORION itself is a scientific object.  A valid self-study freezes:

```text
incumbent ORION version R0
problem and target responsibilities
old closure and known alternatives
proposal-origin trace
candidate change delta
hidden consequences
positive / negative / CANNOT_CHECK terminals
independent evaluator
external adoption owner
rollback and negative-history policy
```

## 9.1 Constitutional separation

```text
proposal principal != evaluator principal
evaluator principal != adoption principal
proposal principal != adoption principal
```

A same-programme implementation can supply engineering evidence or a formal
counterexample.  It cannot certify the novelty, scientific value, or adoption
of its own framework change.

## 9.2 Self-study cycle

```text
1. Freeze R0 and its current theorem/harness/paper state.
2. Register a concrete ORION failure, tension, or opportunity.
3. Generate no-change, donor-product, local-patch, and regime-change alternatives.
4. Seal candidate origin and old-closure evidence.
5. Predict downstream semantic and synchronization consequences.
6. Execute a theorem-identifying study on held-out tasks.
7. Preserve false, null, harmful, and over-conservative outcomes.
8. Emit ChangeImpactReceipt.v1.
9. Create R1 as a successor identity; never rewrite R0's outcome-bearing history.
10. External owner adopts, rejects, or leaves unresolved.
```

## 9.3 Recursion stop rules

Stop or return `CANNOT_CHECK` when:

- the residual is donor-subsumed;
- the support family is non-identifiable under available observations;
- the candidate origin is unresolved;
- the hidden consequence leaked;
- improvement depends on an unpriced resource scalarization;
- the only remaining gate is external validity, novelty, or adoption;
- recursive subdivision produces no new falsifier or decision.

---

# 10. Change-impact and synchronization calculus

A semantic change and a paper claim change are not the same event.

## 10.1 Impact graph

Register reopen-on-change edges among:

```text
THEORY -> CODE -> HARNESS -> PAPER -> AUTHORITY -> MANIFEST
      \-> ISSUE / EXECUTION BACKLOG / NEGATIVE HISTORY
```

The impact closure of changed nodes is the least forward-closed set under
registered reopen edges.

## 10.2 Mandatory receipt

`ChangeImpactReceipt.v1` contains:

```text
changed node identities
impacted node identities and kinds
reopened obligations
claim delta
external authority receipt presence
required synchronization surfaces
claim-bearing paper update allowed / forbidden
```

## 10.3 Update law

- Theory/code/harness may receive an additive successor when their semantic
  object changes.
- Issues and backlogs should be updated immediately so the work is visible.
- Papers may receive a non-authorizing scope or future-work note when useful,
  subject to their content-binding rules.
- A claim-bearing manuscript, claim ledger, active authority, or result
  terminal changes only after an earned `CLAIM_DELTA` and its required
  authority receipt.
- Content manifests are regenerated only after the authoritative bytes are
  committed; regeneration must not erase unexplained drift.
- Historical outcome-bearing artifacts remain immutable.

Therefore the present V2 work updates the framework, reference harness,
execution backlog, and issue graph.  It does **not** rewrite existing ORION or
ORION-Q paper claims.

---

# 11. Theorem programme

## Knowledge-web theorems

- **KW-T1 — identity and endpoint well-formedness.** Duplicate identities or
  dangling edges invalidate the web.
- **KW-T2 — exact support-family criterion.** A target is supported iff at
  least one registered support hyperedge is complete.
- **KW-T3 — path insufficiency.** Reachability by one graph path does not imply
  completion of a conjunctive support family.
- **KW-T4 — load-bearing ancestor closure.** Reverse closure over
  load-bearing edges contains every registered upstream ingredient.
- **KW-T5 — change-impact least closure.** Impact propagation is the least
  forward-closed set under reopen-on-change edges.
- **KW-T6 — alternative-support preservation.** Breaking one family does not
  revoke a target while another complete family survives.

## Navigation theorems

- **NAV-T1 — coupled-space necessity.** Fixed hypothesis/experiment search is
  incomplete for cases requiring representation or paradigm change.
- **NAV-T2 — target-information criterion.** An acquisition with no
  target-relevant partition refinement cannot identify a previously
  ambiguous terminal.
- **NAV-T3 — relational-transfer condition.** Surface similarity does not
  establish cross-domain transfer; a relational correspondence plus target
  validation is required.
- **NAV-T4 — open-morphology necessity.** No fixed finite move vocabulary can
  be declared universally complete from bounded episodes.
- **NAV-T5 — navigation successor identity.** Changing the objective,
  support families, or protected observations after outcome access defines a
  new study.

## Proof-economy theorems

- **PE-T1 — no universal scalar cheapest plan.** Pareto-incomparable adequate
  plans admit no unique cheapest plan without external preferences.
- **PE-T2 — counterexample economy.** One valid counterexample is sufficient
  to refute a universal statement in its declared domain.
- **PE-T3 — finite-enumeration ceiling.** Exhaustion establishes only the
  exact finite class enumerated.
- **PE-T4 — typed adequate-plan criterion.** A plan is adequate iff every hard
  obligation is discharged by an accepted method and authority with attained
  preconditions.
- **PE-T5 — Pareto proof frontier.** The bounded reference algorithm returns
  exactly the non-dominated adequate subsets of supplied proof options.
- **PE-T6 — authority non-compensation.** Additional local computation cannot
  compensate for a missing external novelty or adoption authority.

## ORION-Q transfer theorems

- **QX-T1 — method/authority separation.** Structural navigation methods can
  transfer across domains; source scientific authority cannot.
- **QX-T2 — target-validator necessity.** A transfer without target-native
  validation remains a hypothesis.
- **QX-T3 — matched-resource necessity.** An apparent transfer advantage under
  uncharged representation or implementation cost is non-identifying.

## Recursive self-application theorems

- **SELF-T1 — no self-evaluation authority.** A proposer controlling the
  evaluator cannot establish protected scientific value.
- **SELF-T2 — no self-adoption authority.** A framework cannot authorize its
  own adoption merely by passing its own checks.
- **SELF-T3 — frozen-origin requirement.** An unsealed proposal origin cannot
  earn outside-closure credit.
- **SELF-T4 — successor identity.** A material framework change creates a new
  version; prior outcome-bearing records remain historical facts.

## Synchronization theorems

- **SYNC-T1 — typed impact propagation.** Reopen obligations are determined by
  registered semantic dependencies, not filename proximity.
- **SYNC-T2 — claim-bearing paper gate.** A claim-bearing paper update requires
  an earned nontrivial claim delta and the appropriate authority receipt.
- **SYNC-T3 — scope-note nonpromotion.** A future-work or scope note does not
  authorize a scientific claim rewrite.
- **SYNC-T4 — binding-order law.** Authoritative bytes precede derived digest
  and package bindings.

---

# 12. Frozen execution order

1. `DISC-WEB-01` — repository-wide typed knowledge-web inventory and support
   family pilot.
2. `DISC-PROOF-ECONOMY-01` — exact bounded proof-plan correspondence and
   hostile precondition tests.
3. `DISC-IMPACT-01` — change-impact audit across Discovery, OSTC, ORION-Q,
   framework, harnesses, papers, authorities, and manifests.
4. `DISC-Q-TRANSFER-01` — ORION-Q structural-transfer pilot with target-native
   non-quantum validators and matched resource accounting.
5. `DISC-SELF-01` — frozen ORION-on-ORION study with independent evaluator and
   external adoption owner.
6. `DISC-HUMAN-DECOMP-01` — chronology-safe historical pilot comparing the
   six-space model with dual-space, four-space, analogy, mechanism, insight,
   and C-K parents.
7. `DISC-OOD-MORPH-01` — counterfactual cases whose solution move is outside
   the registered morphology.
8. `DISC-WEB-FRONTIER-MATH-01` — prospective exact-domain discovery with
   knowledge-web and proof-economy receipts.
9. `DISC-NOV-02` — independent novelty and donor-subtraction review of the
   atomic residual.

No paper claim update precedes jobs 1–4 and an earned claim delta.  No
self-improvement or present-day discovery claim precedes jobs 5, 8, and 9.

---

# 13. Honest terminals

```text
KNOWLEDGE_WEB_REFERENCE_CORE_GREEN
SUPPORT_FAMILY_INCOMPLETE
DONOR_PRODUCT_SUFFICIENT
SURFACE_ANALOGY_ONLY
TARGET_VALIDATOR_MISSING
PROOF_PLAN_PARETO_SET_RETURNED
NO_UNIQUE_CHEAPEST_WITHOUT_PREFERENCES
PRECONDITION_EMPTY_NOT_EXERCISED
OPEN_MOVE_CLASS_REQUIRED
SELF_EVALUATION_INVALID
SELF_ADOPTION_INVALID
SELF_STUDY_CANNOT_CHECK
CLAIM_BEARING_PAPER_UPDATE_FORBIDDEN
EXTERNAL_NOVELTY_CANNOT_CHECK
TRIANGULATED_DISCOVERY_SUPPORTED
```

The strongest programme terminal remains prospective:

```text
ORION_KNOWLEDGE_WEB_NAVIGATION_AND_PROOF_ECONOMY_EXTERNALLY_VALIDATED
```

---

# 14. Current completion boundary

Completed in this tranche:

- typed web nodes, edges, support families, and exact support status;
- load-bearing ancestor and change-impact closure;
- vector proof costs, exact adequate-plan enumeration, Pareto filtering, and
  explicit-weight selection;
- hard-precondition enforcement;
- separated self-application contract;
- target-validated ORION-Q transfer contract;
- paper claim-update gating;
- hostile finite tests and machine-readable theorem/backlog ledgers;
- issue-graph synchronization.

Not completed by local theory/code alone:

- repository-wide knowledge-web population;
- naturalistic human-discovery inference;
- target-domain ORION-Q transfer results;
- protected ORION self-study;
- prospective frontier discovery;
- external validity, novelty, publication, or adoption.
