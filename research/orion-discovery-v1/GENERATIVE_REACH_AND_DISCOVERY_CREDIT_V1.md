# Generative Reach and Discovery Credit V1

**Status:** prospective theory and protocol.  
**Purpose:** distinguish genuine scientific expansion from selection, search, renaming, macro formation, hidden-answer construction, or retrospective novelty narration.  
**Authority:** no present-day discovery or novelty claim.

## 1. Scientific regime

For a target domain and responsibility, define a bounded scientific regime

\[
R=(Q,\Phi,L,I,V,A,C,H),
\]

where:

- `Q` — current question and objective language;
- `Φ` — formulation, representation, ontology, and accessible state;
- `L` — registered method/operator language;
- `I` — observation, intervention, instrument, simulator, and prototype interface;
- `V` — validation and measurement semantics;
- `A` — authority and adoption boundary;
- `C` — capability/resource contract;
- `H` — retained failures, nulls, counterexamples, donor absorption, and negative history.

For a target contract `t`, let

\[
Reach_B(R,t)
\]

mean that a valid artifact satisfying `t` can be generated under frozen resource vector `B`, legal operations, and admitted information.

The notation is responsibility-relative. A representation may make prediction reachable while leaving intervention, proof, diagnosis, or repair unreachable.

## 2. Discovery edit types

A proposal changes one or more typed coordinates:

\[
e=(\Delta Q,\Delta\Phi,\Delta L,\Delta I,\Delta V,\Delta A).
\]

Interpretation:

- `ΔQ`: question, conjecture, objective, or unit-of-analysis edit;
- `ΔΦ`: formulation, representation, latent object, coordinate, invariant, or ontology edit;
- `ΔL`: method, proof rule, algorithm, operator, or composition grammar edit;
- `ΔI`: measurement, instrument, intervention, simulator, prototype, or data-acquisition edit;
- `ΔV`: validation, loss, evidence, error, or experimental-design edit;
- `ΔA`: delegation, custody, promotion, or adoption edit.

Only the first five may expand scientific reach. `ΔA` may authorize use of an earned result but cannot create the result or its novelty.

## 3. Proposal-origin record

Every candidate must carry a content-bound origin trace:

```text
ProposalOrigin.v1 =
  proposal_id
  frozen_regime_id
  frozen_operator_grammar_id
  visible_source_ids
  visible_failure_and_tension_ids
  generator_identity
  generation_trace
  supplied_candidate_ids
  newly_constructed_primitive_ids
  correspondence_map
  hidden_fields_attestation
  target_oracle_access
  candidate_reducibility_state
  execution_and_validation_requests
  digest
```

The origin trace records what was supplied and what was generated. It does not grant validity or novelty.

## 4. GRT-T1 — supplied-menu closure theorem

Let `G` be a supplied candidate set and let a controller select, rank, combine, or repeat candidates using operations already in the frozen closure `Cl_R`.

If

\[
G\subseteq Cl_R(L),
\]

and every controller operation preserves `Cl_R(L)`, then

\[
Output(controller,G)\subseteq Cl_R(L).
\]

### Proof

`Cl_R(L)` contains `G` and is closed under every legal controller operation. Induction over the finite controller trace keeps every intermediate and final candidate inside the closure. ∎

### Consequence

Choosing a human-supplied missing method from a menu is difficult search, not outside-closure method invention. Discovery credit may attach to efficient search or selection, but not to semantic expansion.

## 5. GRT-T2 — macro versus semantic expansion

A candidate primitive `e` is a **macro** when its behavior is extensionally equivalent to an old-language construction under the frozen semantics and resource contract:

\[
\exists p\in Cl_R(L)
\quad
p\equiv_{R,B} e.
\]

It is a **semantic expansion candidate** when

\[
e\notin Cl_R(L)/{\equiv_{R,B}}.
\]

A new name, serialization, prompt, wrapper, cached composition, or compressed library entry is not a semantic expansion if an old construction has the same admitted behavior and resource class.

Resource-bounded equivalence must be stated explicitly. A conservative representation change may preserve unbounded expressibility while materially changing bounded reach.

## 6. GRT-T3 — obstruction–extension theorem

For target contract `t`, a certified expansion instance requires:

\[
t\notin Reach_B(R),
\]

\[
e\notin Cl_{R,B}(L)/{\equiv},
\]

and

\[
t\in Reach_{B'}(R\oplus e)
\]

under a declared correspondence between `B` and `B'`.

The first clause is an **old-regime obstruction**, the second is **non-reducibility**, and the third is **new reach**.

None alone suffices:

- obstruction without new reach is failure;
- new reach without obstruction may be ordinary search;
- outside-grammar syntax without semantic reach is decoration;
- new reach obtained from hidden information is access widening.

## 7. GRT-T4 — minimum expansion

Let `E` be a registered partially ordered family of edits, where `e'≺e` means `e'` is strictly weaker by primitive set, information access, or semantic effect.

An edit `e` is minimum for target `t` when:

\[
t\in Reach(R\oplus e)
\]

and

\[
\forall e'\prec e,
\quad
t\notin Reach(R\oplus e').
\]

Minimum expansion is class-relative. A new donor or weaker edit may later refute it, in which case the old receipt remains valid only for the earlier registered family.

## 8. GRT-T5 — no-answer-laundering theorem

Let the protected target be `T(x)`. A proposal construction is inadmissible when its new state or primitive contains, queries, or computes `T(x)` through an interface unavailable to the old regime while the experiment is described as a representation or method change.

Formally, if an edit constructor `C` has access to a protected oracle `O_T` and the compared baseline does not, then

\[
Reach(R\oplus C(O_T))
\not\Rightarrow
\text{representation or method expansion under matched information}.
\]

The result is an access expansion. It may still be useful, but it belongs to a different scientific claim.

Every candidate origin record must state:

```text
target_oracle_access = NONE / DECLARED / CANNOT_CHECK
hidden_fields_attestation
candidate-visible evaluator fields
```

## 9. GRT-T6 — hidden-consequence requirement

A proposal generated from development evidence earns scientific value only through consequences not used to construct or select it.

Let `D` be the development consequence set and `H` a protected hidden set. Require:

\[
H\cap D=\varnothing
\]

at the registered independent unit and

\[
Performance(e,H)
\]

to be evaluated by an independent native verifier or scientific adjudicator.

Reproducing the development target proves consistency with the construction, not general discovery value.

## 10. GRT-T7 — transfer requirement

A candidate mechanism is reusable only if its effect survives at least one material change not encoded by renaming alone, such as:

- problem instance family;
- domain;
- model/provider;
- representation vocabulary;
- scale;
- objective or responsibility;
- simulator/experimental host;
- source window;
- theorem parameter.

The transfer contract must state which coordinates are required to remain the same and which change.

A candidate may earn:

```text
INSTANCE_VALUE
FAMILY_VALUE
DOMAIN_VALUE
CROSS_DOMAIN_VALUE
```

Only the highest actually tested rung is authorized.

## 11. GRT-T8 — donor first-refusal theorem

Let `D_1,…,D_k` be donor-complete systems receiving matched information, tools, method primitives, and resources. If a donor produces an equivalent candidate/result under the frozen contract, ORION has no architectural discovery residual on that instance.

The correct terminal is one of:

```text
DONOR_EQUIVALENT
DONOR_SUBSUMES
ORION_RESOURCE_ADVANTAGE_ONLY
ORION_ROBUSTNESS_ADVANTAGE_ONLY
RESIDUAL_MECHANISM_SURVIVES
```

A donor tie is a predicted and scientifically valuable result. Hiding ties converts a semantic theory into branding.

## 12. GRT-T9 — discovery-credit factorization

Define a discovery-credit certificate

\[
\mathcal D=(O,N,R,H,T,D,V,A),
\]

with:

- `O`: content-bound proposal origin;
- `N`: old-regime non-reach/obstruction;
- `R`: candidate non-reducibility;
- `H`: hidden consequence success;
- `T`: held-out transfer;
- `D`: donor subtraction;
- `V`: independent validity;
- `A`: external novelty/adoption authority.

A strongest present-day discovery claim requires all factors:

\[
DiscoveryCredit(e,t)
\iff
O\land N\land R\land H\land T\land D\land V\land A.
\]

This is an authority contract, not a definition of creativity. Weaker factor combinations authorize weaker terminals:

| Factors closed | Maximum terminal |
|---|---|
| `O` only | `PROPOSAL_RECORDED` |
| `O+N+R` | `OUTSIDE_REGISTERED_CLOSURE_CANDIDATE` |
| `O+N+R+H` | `PROTECTED_INSTANCE_EXPANSION` |
| `+T` | `TRANSFERRED_EXPANSION` |
| `+D+V` | `VALIDATED_RESIDUAL` |
| `+A` | `EXTERNALLY_ADJUDICATED_NOVEL_DISCOVERY` |

Missing factors remain visible; they are not averaged.

## 13. GRT-T10 — proposal and adoption separation

A candidate may generate evidence in favor of itself, but that evidence does not grant adoption authority when the candidate controls the evaluator, protected data, thresholds, negative history, or merge path.

Therefore:

\[
ProposalAuthority(e)
\not\Rightarrow
AdoptionAuthority(e).
\]

Adoption requires a protected bridge with evaluator identity, fresh evidence, negative-history integrity, and external or otherwise unforgeable approval.

This preserves OSTC-T19/T21 and P5/P14 boundaries inside the discovery engine.

## 14. GRT-T11 — novelty is not derivable from internal search alone

A finite literature search can establish the sources it found and the residual after their absorption. It cannot prove that no inaccessible or undiscovered prior work exists.

Thus internal novelty state is at most:

```text
RESIDUAL_SURVIVED_REGISTERED_SEARCH
NOVELTY_NARROWED
ALREADY_SOLVED
CANNOT_CHECK
```

`EXTERNALLY_ADJUDICATED_NOVEL_DISCOVERY` requires an authority outside the proposing programme and remains defeasible under later prior work.

## 15. Discovery engine architecture

A complete ORION discovery cycle should execute:

```text
1. reconstruct scientific state and responsibilities
2. generate plural material tensions, including opportunity without anomaly
3. diagnose first blocked layer:
   information / formulation / method / instrument / resource / validation / admission
4. prove or bound the obstruction
5. generate candidate edits at that layer
6. attach proposal-origin records
7. remove macros, renamings, hidden-answer and access-widening candidates
8. construct theorem-identifying discriminators
9. execute development, hidden, transfer and hostile controls
10. absorb donor mechanisms
11. submit validity, novelty and adoption to separate authorities
12. retain every false, harmful, tied, and unresolved candidate
```

## 16. Generative frontier metric

For frozen regime `R`, define the empirically observed **generative frontier** as the set of proposal equivalence classes the system can produce without target-oracle access under budget `B`:

\[
GF_B(R)=\{[e]_{\equiv}:e\text{ has a valid origin trace under }B\}.
\]

This is a capability object, not novelty. Scientific evaluation asks:

- does `GF_B(R)` include edits outside the old closure?
- do those edits pass hidden consequences?
- which edit types are absent?
- does increased compute expand useful classes or only produce paraphrases?
- how much of the frontier is donor-equivalent?

## 17. Strong falsifiers

A discovery engine fails its strongest claim when:

- the hidden operator appears in the supplied menu;
- a prompt names the historical solution;
- a representation computes the answer;
- the result disappears under symbol or entity reminting;
- a donor with the same primitives finds the same edit;
- the edit solves only the originating instance;
- the old closure was not actually exhausted or bounded;
- an evaluator rewards ORION vocabulary rather than consequences;
- the system generates unlimited candidates and selects after seeing hidden outcomes;
- novelty is asserted from confidence or citation distance;
- the candidate can self-approve.

## 18. Immediate ORION targets

The highest-value initial targets are evaluator-rich domains:

1. finite mathematics and combinatorics;
2. proof and tactic languages;
3. program synthesis and verified algorithms;
4. state abstraction and compiler regimes;
5. symbolic physical-law worlds;
6. chemistry/materials simulators only after exact action and validity contracts exist.

The target is not to maximize the number of generated ideas. It is to maximize the number of independently valid, non-reducible, hidden-consequence-bearing edits per charged scientific resource while keeping false invention low.

## 19. Prior-art boundary

Program synthesis, evolutionary search, library learning, conceptual expansion, analogy, question generation, design theory, scientific agents, and automated experiment design are donor fields.

The candidate ORION residual is the exact coupling of:

- blocked-layer diagnosis;
- obstruction certification;
- proposal-origin lineage;
- theorem-identifying harness design;
- typed scientific admission;
- chronology-safe historical/counterfactual/prospective triangulation;
- separate validity, novelty, and adoption authority.

That residual remains a hypothesis until the execution programme and #287 external novelty review close.