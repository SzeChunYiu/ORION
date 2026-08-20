# ORION-Q MAX-R1 cross-domain research-operator arbitration protocol

Date: 2026-08-20
Parent: #679
Development packet: `development/orion-q-max-r0/DEVELOPMENT_PACKET.md`
Status: frozen before result-bearing generation.

## Question

Can a single typed ORION quantum-research state identify the correct **research operator** across heterogeneous quantum domains when a same-information weaker representation loses the semantic binding between observations and roles?

This tests W1/W2 structural generality. It does not test P10 method invention.

## Frozen action vocabulary

- `SEARCH_MORE`
- `VERIFY_MORE`
- `REOPEN_METHOD`
- `CHANGE_REPRESENTATION`
- `CHANGE_INTERFACE`
- `GROW_LANGUAGE`
- `CANNOT_CHECK`

## Domains

- synthesis/program search;
- algorithm/interface/QSVT-style design;
- QEC code–circuit–decoder co-design;
- formal theorem/conjecture reasoning.

Domain identity is evaluator metadata only and is excluded from generic model-visible views.

## Common semantic coordinates

`QuantumResearchDecisionState.v1` contains only bounded categorical/binary facts:

- `search_exhausted`;
- `evidence_sufficient`;
- `verifier_available`;
- `verifier_budget_available`;
- `previous_failure`;
- `failure_required_same_representation`;
- `failure_required_same_access`;
- `representation_changed`;
- `access_changed`;
- `representation_obstruction_witness`;
- `interface_obstruction_witness`;
- `language_obstruction_witness`;
- `alternate_representation_available`;
- `interface_constructible`.

No operator/gate/paper/task-family names enter the state.

## Gold decision rule

Order is frozen:

1. insufficient evidence + usable verifier budget -> `VERIFY_MORE`;
2. insufficient evidence without admissible verification -> `CANNOT_CHECK`;
3. scoped prior failure whose required-same coordinate changed -> `REOPEN_METHOD`;
4. search not exhausted and no certified obstruction -> `SEARCH_MORE`;
5. certified representation obstruction + alternate representation -> `CHANGE_REPRESENTATION`;
6. certified interface obstruction + constructible interface -> `CHANGE_INTERFACE`;
7. certified language obstruction -> `GROW_LANGUAGE`;
8. otherwise -> `CANNOT_CHECK`.

Obstruction labels are evaluator facts derived from exact synthetic witnesses, not human-readable family names.

## Information views

### V0 `SURFACE`
Opaque problem token only.

### V1 `UNTYPED_BAG`
All model-visible Boolean/categorical values from the typed state are present, but role names and binding are removed. The bag is deterministically canonicalized as a multiset.

This is the key same-information control: information quantity is retained; semantic coordinate binding is removed.

### V2 `RAW_HISTORY`
Adds whether a prior failure exists, but not the failure's `required_same` bindings or which coordinate changed.

### V3 `TYPED_STATE`
Full typed coordinates above, but no evaluator gold/domain identity.

### V4 `TYPED_STATE_PLUS_SCOPED_FAILURE`
V3 plus explicit `required_same` bindings on the failure receipt. This is the strongest P9 view.

## Hostile-pair requirement

For every action class where mathematically possible, construct pairs/groups such that:

- V0 collides;
- V1 collides;
- V2 collides for failure-sensitive cases;
- gold action differs;
- V4 separates.

At least one pair must distinguish:
- stale vs still-applicable failure;
- representation vs interface obstruction;
- search-more vs grow-language;
- verify-more vs cannot-check.

## Exact information ceilings

Before fitting any learner, compute the maximum deterministic classification accuracy for each view as the majority label within identical view fingerprints.

If V1 or V2 has ceiling 1.0, the benchmark fails to establish a typed-state information residual and must be redesigned before model fitting.

## Baselines

- majority/frequency;
- V1 exact deterministic ceiling;
- V2 exact deterministic ceiling;
- simple decision rule on V3 without scoped failure bindings;
- exact frozen rule on V4;
- optional learned classical model only after ceilings are computed.

No LLM is needed for the core non-vacuity result.

## Cross-domain transfer

The exact rule is domain-neutral. Generated identities and carrier-specific tokens are reminted by domain. The primary generality claim requires the same typed rule/coordinate semantics to evaluate all four domains without domain-specific branches.

## Primary endpoints

1. exact deterministic ceiling gap: `ceiling(V4) - ceiling(V1)`;
2. exact deterministic ceiling gap: `ceiling(V4) - ceiling(V2)`;
3. false escalation rate;
4. correct `CANNOT_CHECK` rate;
5. per-domain action accuracy under the same rule;
6. remint/order invariance.

## Falsifiers

- untyped bag reaches 1.0 ceiling;
- domain identity leaks gold;
- a unique specialist/tool availability pattern identifies the action;
- V4 includes evaluator obstruction class directly instead of evidence coordinates;
- role names encode the answer lexically;
- generated pairs differ in information quantity rather than binding;
- the exact rule requires domain-specific conditionals;
- hidden future outcome enters any view.

## Permitted terminal

Positive:

`MAX_R1_TYPED_RESEARCH_OPERATOR_ARBITRATION_SUPPORTED__EXACT_SYNTHETIC`

Only if V4 has exact ceiling 1.0, weaker same-information views have a strictly lower ceiling, all four domains use one rule, and hostile remint/order tests pass.

Negative terminals:

- `MAX_R1_UNTYPED_INFORMATION_SUFFICIENT`;
- `MAX_R1_DOMAIN_LOCAL_ONLY`;
- `MAX_R1_INFORMATION_LATTICE_INVALID`;
- `CANNOT_CHECK`.

No P10, real quantum algorithm, or novelty claim is authorized by this experiment.