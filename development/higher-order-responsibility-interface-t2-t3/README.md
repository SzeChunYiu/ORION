# Higher-order responsibility + interface mechanics — T2/T3 development packet

Status: **IMPLEMENTATION HYPOTHESIS FROZEN / NO SCIENTIFIC RESULT**

Base subject: `acc1d8830ecab42a5650a8e8a250310248b14482`

Owners / research inputs: #452, #455, #459, #463. Structural donor process: #454. Verification/novelty remain #283/#287.

## Development question

After tranche T1 established a non-authorizing minimal-revision calculus, implement the smallest additional substrate needed to answer two questions without freezing the still-provisional RLC/MDA taxonomy:

1. Can ORION represent **competing revision-responsibility hypotheses** and remain plural or unresolved until discriminating observations actually separate them?
2. Can ORION represent **interface adequacy** (observation/measurement/representation/feedback checks) as a fail-closed prerequisite so a model/method/objective rewrite is not selected while a narrower interface defect is still established or unresolved?

The framework integration must be read-only/non-authorizing: it may select a candidate mechanic for later testing; it may not adopt, promote, merge, certify novelty, or claim scientific validity.

## Atomic fibres

### T2-A — responsibility hypotheses
- content-bound hypothesis identity;
- claim-relative expected discriminator outcomes;
- exact support/defeater evidence identities;
- no fixed global revision-class enum;
- no confidence threshold capable of granting write authority.

### T2-B — responsibility assessment
- contradictory observed outcome defeats a hypothesis;
- one fully tested survivor -> `IDENTIFIED`;
- multiple fully tested survivors -> `AMBIGUOUS`;
- missing required discriminator observations -> `UNRESOLVED`;
- zero survivors -> `NO_SURVIVING`;
- every report is explicitly non-authorizing.

### T3-A — interface checks
- generic check scope strings rather than a frozen ontology;
- required checks carry `PASS / FAIL / UNRESOLVED`;
- any required fail -> `REPAIR_REQUIRED`;
- no fail + any required unresolved -> `UNRESOLVED`;
- all required pass -> `ADEQUATE`;
- an optional/advisory pass cannot compensate a failed/unresolved required check.

### T3-B — Self-ORION revision gate
- consumes T2 responsibility, T3 interface adequacy, and T1 mechanics/assessments;
- unresolved/ambiguous/no-survivor responsibility never selects a material revision;
- interface `REPAIR_REQUIRED` restricts candidate selection to explicitly registered interface-repair mechanics whose writes stay inside the declared interface coordinate set;
- interface `UNRESOLVED` blocks broader selection;
- only after interface `ADEQUATE` may the gate filter candidates through an identified responsibility binding and call T1 minimal-revision selection;
- returned candidate is a recommendation for later replay/fresh/protected evaluation only;
- `grants_adoption_authority = False`, `grants_promotion_authority = False`.

## Saturation assessment

The surrounding literature already establishes the ingredients separately: diagnostic/model criticism, POMDP/state sufficiency and representation diagnostics, Bayesian/causal discrimination, belief revision, process/effect systems, M-open model expansion, rational metareasoning, and protected authority. RLC 2026/MDA pressure adds direct reasons not to conflate observation failure with model failure. None of this packet claims those ingredients as ORION novelty.

The implementation deliberately avoids formalizing a universal state tuple or final list of scientific failure classes. It provides only the generic relations required by the current countermodels. If #452/#454 saturation finds a stronger existing formalism, these objects may become adapters or be removed.

## Challenge to the saturation basis

Possible reasons this packet is still too broad or wrong:

- responsibility may require probabilistic/credal state rather than discrete survivors;
- exact outcome signatures may be too brittle for real scientific evidence;
- interface adequacy may be task-relative and not reducible to independent checks;
- a representation change may sometimes be simultaneously an interface and model change, defeating a clean layer boundary;
- intervention choice may need to be co-optimized with responsibility rather than supplied externally;
- standard diagnostic decision theory may already subsume the whole gate;
- the T1 footprint preorder may be only a necessary engineering order, not a semantic scientific order.

These are reopen triggers, not reasons to fabricate a richer implementation now.

## Competing implementation hypotheses

### H-I1 — generic discrete substrate (selected for this tranche)
Use exact, content-bound discriminator predictions and generic interface-check scopes. Keep ambiguity/unresolved explicit. This is small, deterministic, and countermodel-friendly.

### H-I2 — probabilistic responsibility posterior
Represent probabilities over revision classes. Rejected for T2/T3 because it would force likelihood/calibration semantics before the literature and benchmark are frozen.

### H-I3 — hard-coded revision taxonomy
Encode EVIDENCE / MODEL_CLASS / REPRESENTATION / OBJECTIVE / METHOD etc. directly. Rejected: the taxonomy is a research hypothesis under #452, not implementation authority.

### H-I4 — modify P5 invention gate directly
Rejected for this tranche. P5 V1/V2 evidence and current invention-readiness semantics remain stable. A separate non-authorizing V3 adapter is safer and falsifiable.

## Frozen implementation hypothesis

Implement three additive modules:

1. `orion.transfer.v2.epistemic_responsibility`;
2. `orion.transfer.v2.interface_adequacy`;
3. `orion.self_orion.revision_gate`.

The Self-ORION module may import the formal transfer layer. The transfer layer must not import Self-ORION or any provider/LLM implementation.

## RED hostile tests required before GREEN implementation

Responsibility:
- identical observed symptom with two indistinguishable hypotheses remains `AMBIGUOUS`;
- a discriminator that contradicts one hypothesis identifies the other;
- a required discriminator not yet observed remains `UNRESOLVED`;
- contradictory evidence defeating every hypothesis yields `NO_SURVIVING`, not arbitrary repair;
- duplicate hypothesis IDs or cross-claim mixtures are rejected;
- report cannot self-authorize.

Interface:
- required observation failure -> `REPAIR_REQUIRED`;
- all required checks pass -> `ADEQUATE`;
- unresolved required check -> `UNRESOLVED`;
- advisory PASS cannot compensate a required FAIL;
- report does not grant broader-revision or scientific authority.

Revision gate:
- failed interface + broad model mechanic + narrow interface mechanic -> only narrow interface mechanic can be selected;
- failed interface with no admissible interface mechanic -> no broad fallback;
- unresolved interface -> no material revision;
- ambiguous responsibility -> no material revision;
- adequate interface + identified responsibility -> T1 minimal selection may nominate a candidate;
- incomplete responsibility-to-mechanic binding fails closed;
- gate cannot grant adoption/promotion/merge authority.

## Paper boundary

This tranche may update P5's claim-boundary prose and claim ledger only to state that a **non-authorizing V3 formal/framework substrate exists**. H1-H4 remain `CANNOT_CHECK`; 21/24 attribution remains descriptive-only. Frozen P1/P4/P6 V2.1 packages and the active P3 publication lane are not edited. Other papers receive additive successor handoff prose only.

## Reopen triggers

- #452 freezes a materially different responsibility model;
- #454 finds prior work that subsumes the selected substrate;
- countermodels require probability/credal or causal-graph semantics;
- interface checks cannot be composed without losing task-relative sufficiency;
- T1 minimality produces a wrong-layer selection in a new hostile case;
- P5 V3 prospective study refutes the utility of responsibility/interface gating;
- any implementation path can self-authorize or mutate protected evaluator/authority state.

## Claim ceiling

A green implementation establishes only deterministic formal/framework behavior on registered countermodels. It does **not** establish Self-ORION improvement, correct scientific diagnosis, publication novelty, model-general validity, or paper readiness.
