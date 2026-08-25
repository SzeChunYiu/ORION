# Composition–Transfer–Completion Calculus V1

**Status:** complete theory and finite executable reference semantics for a declared class.
**Parent:** ORION Discovery V1 / PR #1280 / issue #1282.

This calculus formalizes three candidate-source modes:

1. **donor composition** — assemble load-bearing fragments such as `a1 × b2 × c3`;
2. **structural transfer** — transport a theorem schema, invariant, mechanism, or procedure from another domain;
3. **residual completion** — retain useful known structure and generate the missing object, relation, invariant, operator, question, interface, or validation rule.

```text
status = THEORY_COMPLETE_FOR_DECLARED_FINITE_TYPED_CLASS
present_day_discovery_authority = NONE
external_novelty_authority = CANNOT_CHECK
paper_authority_delta = NONE
```

The calculus is additive to `GENERATIVE_REACH_AND_DISCOVERY_CREDIT_V1.md`. It decomposes the candidate before origin, hidden-consequence, donor, validity, novelty, and adoption gates are evaluated.

## 1. Expert veto roles

- **Formal semantics:** no composition or transfer theorem from surface similarity or component validity alone.
- **Mathematical discovery:** a timeout is not an outside-closure obstruction.
- **Algorithms/synthesis:** a supplied menu, macro, or cached composition is not primitive invention.
- **History of science:** a retrospective narrative does not establish private cognition or a universal discovery ontology.
- **Empirical/design science:** a textual analogy is not target-domain validation.
- **Novelty/authority:** disciplinary distance, surprise, or new wording is not novelty authority.

---

# Part I — Semantic provenance

## 2. Frozen regime and candidate graph

Use the Discovery V1 regime

\[
R=(Q,\Phi,L,I,V,A,C,H),
\]

where the coordinates represent question, formulation, method language, instrument/intervention, validation, authority, capability/resources, and negative history.

For target `t`, `Reach_B(R,t)` means that a valid artifact satisfying `t` is reachable under the frozen information, operations, and vector budget `B`. The old semantic closure is

\[
\operatorname{Cl}_{R,B}(L)/{\equiv_{R,B,r}},
\]

where equivalence is responsibility-relative. A new token is not a new semantic object if it behaves like an old construction at the claimed responsibility and resource class.

Represent candidate `e` by a finite typed graph/hypergraph

\[
G_e=(N_e,E_e),
\]

with nodes such as questions, objects, relations, constraints, operators, interfaces, and validation rules, and edges such as composition, inference, transport, intervention, measurement, construction, and validation. Edges are first-class because all component nodes may be known while the bridge/topology is the residual.

## 3. Provenance classes

For each node or edge equivalence class, assign one state in conservative priority order:

```text
LOCAL_CLOSURE
DONOR_MAPPED
GENERATED_RESIDUAL
UNRESOLVED
```

A generated idea later absorbed by prior work becomes `DONOR_MAPPED` for present-day novelty, while its origin record remains process evidence.

## SYN-T1 — Class-relative provenance partition

For a finite candidate graph and frozen decidable membership, equivalence, donor-map, and origin relations, every node and edge belongs to exactly one class.

**Proof.** Test local membership; on its complement test donor mapping; on the remaining complement test generated origin; classify the rest unresolved. The ordered tests are exhaustive and disjoint. ∎

The result is class-relative. New donors can reclassify a residual without rewriting the historical origin record.

---

# Part II — Mode A: donor composition

## 4. Donor fragments and typed products

A donor fragment records source domain, input/output types, premises, guarantees, native validation, resource vector, scope, and authority. A fragment can be a theorem schema, invariant, proof tactic, algorithmic module, representation, experimental procedure, measurement model, or negative result.

A composition edge

\[
\beta:d_{i_1}\otimes\cdots\otimes d_{i_k}\to y
\]

is legal only when types, assumptions, content, responsibility, epoch, validation, blockers, information access, and resources all match or have explicit bridges.

Component validity does not imply composition validity.

## 5. Donor-product closure

For donor set `D` and grammar `Γ`, define `ProdCl(D,Γ)` as the least fixed point containing donor fragments and closed under registered typed composition, transfer, and old-regime operations.

## SYN-T2 — Supplied product closure

If every fragment and construction edge lies in `ProdCl(D,Γ)`, the final candidate lies in it.

**Proof.** Induction over the finite construction trace. ∎

Therefore `a1 × b2 × c3` may solve a major problem while remaining donor composition rather than primitive invention.

## 6. Minimal products and interaction order

Let

\[
\mathcal S_t=\{S\subseteq D:t\in\operatorname{ProdCl}(S,\Gamma)\}.
\]

An inclusion-minimal successful set has no successful proper subset. Multiple incomparable sets are retained.

## SYN-T3 — Minimal successful set exists

A finite nonempty successful-subset family contains an inclusion-minimal element.

**Proof.** Any strict descending inclusion chain in a finite set terminates. ∎

Define interaction order

\[
k_t=\min_{S\in\min(\mathcal S_t)}|S|.
\]

## SYN-T4 — Load-bearing fragments

Every member of an inclusion-minimal successful set is load-bearing relative to that set; deleting it prevents target reach. This follows directly from minimality.

## 7. Bridge residuals

A candidate can have donor-owned nodes but a graph outside the product closure because of a new bridge, feedback edge, ordering, compatibility condition, higher-order interaction, coupled constraint, or validation rule.

## SYN-T5 — Node sufficiency is false

There are candidates with zero node residual and nonzero edge/topology residual.

**Witness.** Two known modules are connected by a generated feedback edge that changes fixed points and produces a hidden consequence. ∎

Allowed composition terminals include:

```text
DONOR_COMPOSITION_ONLY
DONOR_COMPOSITION_WITH_RESOURCE_ADVANTAGE
DONOR_COMPOSITION_WITH_NEW_TARGET_APPLICATION
BRIDGE_RESIDUAL_CANDIDATE
```

No terminal above self-authorizes novelty.

---

# Part III — Mode B: cross-domain structural transfer

## 8. Structural addresses

Surface similarity is neither necessary nor sufficient for useful transfer. Every problem and donor receives a typed structural address containing:

```text
roles
relation signatures and arities
invariants/conservation laws
obstruction/counterexample signatures
input/output interfaces
validation semantics
resource dependencies
responsibility and scope
```

A distant field is useful when structural distortion is low and target obligations can be discharged, not because citation or embedding distance is high.

## 9. Two transfer forms

ORION admits complementary donor forms:

1. **relational structure mapping** when roles and relations admit an object-level correspondence;
2. **axiomatic/theory interpretation** when a shared law or proof schema is more appropriate than object matching, as often occurs in object-rich mathematics.

“Analogy” without a correspondence object is a search hint only.

A transfer map records source/target roles, mapped relations or axioms, invariant and boundary preservation, premises, validation correspondence, resource correspondence, and a negative/reminted twin.

Define transfer debt as a vector over:

```text
missing relations
missing premises
missing boundary conditions
validation mismatch
resource/access mismatch
```

## SYN-T6 — Exact formal transfer soundness

Let `F` interpret source theory `T_S` in target theory `T_T` and preserve every inference rule used in a source derivation. If mapped premises hold and `T_S ⊢ φ`, then `T_T ⊢ F(φ)`.

**Proof.** Induct over the derivation. Premises map by assumption and each inference step maps to a valid target step. ∎

Interpretation theory is donor mathematics. ORION’s object is the search, debt ledger, falsifiers, and authority coupling.

## SYN-T7 — Partial transfer cannot promote

If any load-bearing transfer debt remains, the map cannot authorize the target conclusion. Two target worlds can agree on the mapped coordinates while differing on the missing one and require different conclusions. The maximum map-derived terminal is:

```text
PARTIAL_ANALOGY_WITH_TRANSFER_DEBT
```

unless a separate target-native proof or experiment validates the result.

## 10. Distortion and negative twins

Record the vector

\[
\delta(F)=(
\delta_{roles},
\delta_{relations},
\delta_{invariants},
\delta_{obstructions},
\delta_{interfaces},
\delta_{validation}).
\]

An exact map has the zero vector. Competing maps and routes form a Pareto frontier with vector resource cost and authority debt.

## SYN-T8 — Domain distance is not authority

Lexical, disciplinary, citation, and embedding distance cannot be sufficient premises for validity or novelty because they can be changed by renaming or corpus representation while preserving or destroying the load-bearing structure. ∎

Every serious transfer includes a negative twin: a surface-similar target with one changed load-bearing relation. A structure-grounded method must refuse or alter the transfer there.

Allowed transfer terminals:

```text
STRUCTURAL_HINT_ONLY
PARTIAL_ANALOGY_WITH_TRANSFER_DEBT
EXACT_FORMAL_INTERPRETATION
TARGET_DOMAIN_VALIDATED_TRANSFER
CROSS_DOMAIN_TRANSFERRED_MECHANISM
```

None implies novelty by itself.

---

# Part IV — Mode C: residual completion

## 11. Residual obligations

For partial model or method `P`, define

\[
O_{res}(P,t)=O(t)\setminus Discharged(P).
\]

The system gives first refusal to:

1. fixed-regime search;
2. known schema instantiation;
3. donor modular composition;
4. structural transfer;
5. residual completion.

This ordering is a scientific anti-overclaim rule, not a universal psychological chronology.

## 12. Completion edits

A completion `λ` may edit:

```text
QUESTION
REPRESENTATION / LATENT OBJECT
RELATION / INVARIANT / CONSTRAINT
METHOD / OPERATOR
INSTRUMENT / INTERVENTION
VALIDATION / MEASUREMENT
```

Authority-only edits cannot expand scientific reach.

A valid completion candidate requires:

- consistency;
- preservation or explicit reopening of old judgments;
- discharge of the claimed residual obligations;
- non-reducibility to old and donor-product closure;
- no target-oracle or hidden-answer access;
- a material hidden consequence;
- held-out transfer at the claimed scope;
- independent native validation.

## 13. Minimality

Let `(Λ,≼)` be a finite edit poset. A weaker edit may use fewer primitives, less information, fewer changed assumptions, a narrower semantic effect, or a narrower intervention.

## SYN-T9 — Minimal completion exists

If a finite edit poset contains any successful completion, its successful subposet has a minimal element.

**Proof.** Finite descending chains terminate. ∎

## 14. Residual family

A candidate may admit several donor decompositions:

\[
e\equiv d_1\oplus\lambda_1
\equiv d_2\oplus\lambda_2.
\]

The harness returns all inclusion-minimal residuals across admissible decompositions.

## SYN-T10 — Residual need not be unique

Let a candidate require semantic elements `a,b,c`. One donor explanation covers `a,b`, leaving `c`; another covers `a,c`, leaving `b`. The two one-element residuals are incomparable and both minimal. ∎

No arbitrary decomposition becomes novelty authority.

## 15. Conservative completion

For frozen old domain `X_0` and responsibilities `R_0`, completion is conservative when

\[
\forall r\in R_0,\forall x\in X_0,
\quad
T_r(P\oplus\lambda,x)=T_r(P,x),
\]

while enabling a new target responsibility or instance.

## SYN-T11 — Conservative-extension safety

The equality above rules out regression on the exact registered old class. It says nothing about unregistered responsibilities or future regime changes.

## 16. Theory-bearing completion

Stronger completion evidence includes:

- several independent residuals closed;
- compression or unification;
- new discriminating predictions;
- transfer to held-out parameters/families;
- low false-expansion on no-jump controls;
- counterexample survival;
- reusable proof or construction operators.

These remain a vector, not one breakthrough score.

Allowed completion terminals:

```text
SCHEMA_INSTANTIATION_ONLY
DONOR_COMPLETION_ONLY
GENERATED_RESIDUAL_UNVALIDATED
MINIMAL_COMPLETION_FINITE_CLASS
HIDDEN_CONSEQUENCE_BEARING_COMPLETION
TRANSFERRED_COMPLETION
EXTERNALLY_ADJUDICATED_NOVEL_COMPLETION
```

---

# Part V — Unified synthesis normal form

## 17. Candidate equation

A general candidate can be written schematically as

\[
e=
\operatorname{Compose}_{\Gamma}
(F_1(d_1),\ldots,F_k(d_k))
\oplus\lambda,
\]

where `d_i` are local or external donor fragments, `F_i` are identities or transfer maps, `Compose_Γ` is a registered or generated topology, and `λ` is the residual family.

Special cases:

```text
DONOR_COMPOSITION:
  all maps are identities or same-domain adaptations; residual empty

STRUCTURAL_TRANSFER:
  at least one cross-domain map; transfer debt closed; residual empty

RESIDUAL_COMPLETION:
  residual nonempty

HYBRID:
  composition, transfer, and residual completion coexist
```

## SYN-T12 — Hybrid provenance normal form

Relative to a fixed finite graph, equivalence, local closure, donor registry, and transfer family, every candidate factors into local, donor-mapped, generated-residual, and unresolved node/edge sets.

**Proof.** Apply SYN-T1 to every node and edge and take their disjoint unions. ∎

This is a provenance theorem, not a theory of private human thought.

## SYN-T13 — No-free-navigation theorem

A navigator starting only with old-closure and donor-product elements and using only closure-preserving search, ranking, composition, and transfer cannot output an outside-closure semantic residual.

**Proof.** Induction over the navigator trace. ∎

A true outside-closure target therefore requires either a residual generator or an expanded information/interface contract. The two must not be confused.

## SYN-T14 — Finite relative completeness

For finite donor, map, composition, and completion candidate spaces, a fair enumerator with complete native validation finds every successful candidate in the registered universe.

This is relative completeness only. It gives no tractability, open-world, or novelty guarantee.

---

# Part VI — Theorem-identifying experiment synthesis

## 18. Alternative separation

Let `Θ` be the registered claim/theory alternatives. Experiment `x` distinguishes pair set

\[
Sep(x)\subseteq {\Theta\choose 2}.
\]

A panel is identifying when its union covers every pair.

## SYN-T15 — Minimum identifying panel is set cover

For a finite experiment library, minimum-cardinality theorem-identifying experiment synthesis is exactly set cover over the alternative-pair universe.

**Proof.** Each experiment covers the alternatives it separates; full pair coverage is exactly signature injectivity. ∎

Experiment cost, safety, latency, and access can be handled as constraints or supplied prices, not hidden in an arbitrary score.

## 19. Proof–counterexample separator

For frontier mathematics, let `P` be verified positive/supporting instances and `N` counterexamples. A candidate predicate separates `(p,n)` when its values differ.

## SYN-T16 — Missing-lemma separator criterion

A predicate library can distinguish every positive from every negative exactly when the union of its pair-separation sets covers `P × N`. Minimum separating families reduce to set cover.

The output is a missing-lemma hypothesis, not a theorem until proved over the claimed class.

---

# Part VII — Discovery Event Normal Form

## 20. Existing morphology

The 51-episode atlas established a ten-coordinate public-artifact morphology:

```text
REPRESENTATION_CHANGE
NEW_OBJECT_OR_STATE_VARIABLE
ABSTRACTION_EQUIVALENCE_STRUCTURE
NEW_LAW_CONSTRAINT_OR_INVARIANT
BRIDGE_CORRESPONDENCE
NEW_OPERATOR_PROCEDURE
SYSTEM_COMPOSITION_ARCHITECTURE
INTERFACE_MEASUREMENT_REDESIGN
FUNCTION_AFFORDANCE_INVENTION
FIXED_REGIME_SEARCH_CONTROL
```

It explicitly does not claim historical cognitive causes, atomicity, novelty, or universal completeness. The three synthesis modes add the missing candidate-source axis.

## 21. Factorized event object

Record

\[
DENF(E)=(Trigger,SourceMode,EditLayer,ArtifactEffect,Validation,Scope,Authority).
\]

Detailed values and the historical crosswalk are in `DISCOVERY_EVENT_NORMAL_FORM_V1.md`.

## SYN-T17 — Registered coverage criterion

A corpus is covered at a declared resolution when every episode has at least one source-grounded tuple, every load-bearing difference affecting a benchmark decision is represented, and unknown interpretations remain explicit.

This is an empirical coverage criterion, not a universal theorem.

## SYN-T18 — Finite-atlas non-exhaustiveness

No finite historical corpus and finite number of no-material-change rounds proves that no future discovery requires a new coordinate or source mode.

**Proof.** A possible future episode can contain a new load-bearing public relation absent from the corpus. The finite observations cannot rule it out. ∎

The correct terminal is `COVERED_AT_REGISTERED_RESOLUTION`, never `ALL_HUMAN_DISCOVERY_PATTERNS_COMPLETE`.

---

# Part VIII — Donor ownership and ORION residual

Strong established parents include:

- Darden: schema instantiation, modular subassembly, and chaining;
- structure-mapping and axiomatic/theory interpretations for analogy;
- Fauconnier and Turner: conceptual integration/blending;
- C-K theory: concept/knowledge co-expansion;
- Boden/Wiggins: transformational creativity and search-space formalisms;
- abduction: hypothesis formation under anomaly or incomplete explanation;
- serendipity/exaptation: unexpected exposure, opportunity recognition, and repurposing.

ORION claims none of these generic operations. Its candidate residual is their exact coupling with:

```text
donor-product closure and interaction order
structural/axiomatic transfer debt
explicit semantic residual families
blocked-layer diagnosis
content-bound proposal origin
theorem-identifying experiments
chronology-safe historical/counterfactual/prospective triangulation
separate validity, novelty, and adoption authority
```

The residual remains a hypothesis until prospective execution and external novelty review.

---

# Part IX — Required receipts

## `DONOR_SYNTHESIS_RECEIPT.v1`

```text
target/responsibility
frozen local closure
donor identities and revisions
fragments and native guarantees
composition grammar and edges
all minimal successful donor sets
interaction order
open composition obligations
resource vector
hidden consequence
independent validity
claim ceiling
```

## `STRUCTURAL_TRANSFER_RECEIPT.v1`

```text
source/target domains
source theorem or mechanism
relational or axiomatic correspondence
roles, relations, axioms, invariants
boundaries and validation semantics
transfer-debt vector
negative twin
hidden target consequence
scope ceiling
```

## `COMPLETION_CERTIFICATE.v1`

```text
partial model and residual obligations
old donor-product obstruction
candidate residual family
proposal origin
minimality/subedit results
old-domain preservation or reopening
hidden consequences
held-out transfer
counterexamples
independent validity
external novelty/adoption
```

## `DISCOVERY_EVENT_NORMAL_FORM.v1`

```text
trigger
source mode
edited layers
artifact effects
validation
scope
source evidence
competing interpretations
unknown fields
```

---

# Part X — Hostile controls

The harness must include:

1. all donor components present but no valid bridge;
2. a target reachable by a smaller donor subset;
3. two incomparable minimal donor products;
4. known nodes with a generated interaction edge;
5. known nodes with a renamed old edge;
6. distant surface similarity with structural mismatch;
7. exact transfer under reminted vocabulary;
8. partial analogy with one missing boundary premise;
9. generated residual later absorbed by prior work;
10. two incomparable minimal residuals;
11. schema instantiation mislabeled primitive invention;
12. hidden-answer access;
13. fixed-regime search solving the target;
14. post-hoc candidate selection;
15. an experiment library unable to separate one alternative pair;
16. governance-only edit falsely credited with reach.

---

# Part XI — Completion boundary

## Theory/reference work complete

```text
three-mode semantics
hybrid provenance normal form
donor-product closure
minimal donor sets and interaction order
bridge residuals
relational/axiomatic transfer debt
finite minimal-completion theorem
residual-family non-uniqueness
DENF morphology crosswalk
minimum experiment-panel reduction
frontier-math separator reduction
finite executable reference semantics
hostile unit controls
```

## Computation/external work only

```text
large donor graph and product-closure search
cross-domain structural index
proposal-origin integration in generators
historical DENF reannotation
counterfactual twins
prospective frontier mathematics
independent formal reconstruction
external novelty/adoption
natural-science instrument execution
```

## Strongest honest terminal

```text
COMPOSITION_TRANSFER_COMPLETION_CALCULUS_COMPLETE_FOR_DECLARED_CLASS
EXECUTION_AND_EXTERNAL_DISCOVERY_AUTHORITY_PENDING
```

## References / donor boundary

- Darden, L. (2002), *Strategies for Discovering Mechanisms: Schema Instantiation, Modular Subassembly, Forward/Backward Chaining*.
- Gentner, D. (1983), *Structure-Mapping: A Theoretical Framework for Analogy*.
- Schlimm, D. (2022), *Two Ways of Analogy: Extending the Study of Analogies to Mathematical Domains*.
- Fauconnier, G. & Turner, M. (1998), *Conceptual Integration Networks*.
- Hatchuel, Weil, and subsequent C-K theory work.
- Wiggins, G. A. (2006), *A Preliminary Framework for Description, Analysis and Comparison of Creative Systems*.

These donors own their native ideas. ORION claims no priority over analogy, blending, C-K design, abduction, modular assembly, search-space transformation, or mechanism discovery.
