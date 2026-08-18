# Higher-order epistemic mechanics T4–T6 — development packet

Status: **IMPLEMENTATION HYPOTHESIS FROZEN / NO SCIENTIFIC RESULT**

Base subject: `8d166ab6dbcb96612c5e709ed640870143aa4f5f`

Owners: #458 (computation), #462 (social evidence), #463 (formal successor). Uncertainty containment is tracked through #452/#455/#459/#463. Structural donor/novelty/verification authority remains #454/#287/#283.

## Development question

Implement the smallest non-authorizing formal substrate for three structures that survived the RLC/MDA harvest after T1–T3:

1. **Epistemic computation allocation:** what internal/inquiry action should be spent next when actions have costs, expected decision value, hard obligations, and authority requirements?
2. **Uncertainty containment:** when a model/interface is valid only on a bounded context set, can ORION restrict admissible action/claim scope without pretending the model has been repaired or proven correct?
3. **Social evidence dependence:** when multiple agents/reports share upstream evidence or strategic uncertainty, can ORION refuse to count them as independent corroboration and preserve hidden-contribution uncertainty?

These are formal/framework contracts only. They do not authorize scientific claims, self-adoption, or paper-level novelty.

## Atomic fibres

### T4-A — computation action
Content-bound claim-relative action with:
- caller-declared action kind (retrieve, diagnose, experiment, plan, LLM, wait, verify, escalate, etc. are examples, not a frozen enum);
- expected decision/information value;
- declared cost;
- hard applicability requirements;
- hard obligations the action can discharge;
- required external authority domains;
- no self-authorization.

### T4-B — computation assessment and selection
- violated requirement or missing required authority -> `BLOCKED`;
- unresolved requirement -> `UNRESOLVED`;
- otherwise `ELIGIBLE`;
- active hard obligations are non-compensatory: eligible actions capable of discharging them take precedence over non-obligation actions even when their scalar net value is lower or negative;
- among obligation-serving actions, maximize number of active hard obligations discharged, then bounded net value `expected_value - cost`;
- without active hard obligations, select positive-net eligible action(s), tie-preserving;
- if every eligible nonmandatory action has non-positive net value -> `LOCAL_COMPUTATION_STOP`;
- unresolved action that could discharge an otherwise uncovered hard obligation keeps selection `UNRESOLVED` rather than allowing a substitute;
- scalar value never grants downstream scientific/revision authority.

### T5-A — validity envelope
Content-bound versioned envelope over caller-declared context IDs with states:
- `SUPPORTED` — current evidence permits action/claim use under the bounded envelope;
- `INVALID` — current evidence blocks use in that context;
- `UNRESOLVED` — evidence is insufficient.

The envelope may be superseded by a new content-bound version linked to its parent digest. Old envelopes remain immutable.

### T5-B — containment assessment
- supported context -> `IN_SCOPE`;
- invalid context -> `BLOCKED`;
- unresolved/missing context -> `UNRESOLVED`;
- containment changes admissible scope only; it does not rewrite model/frame/objective state;
- `establishes_model_correctness = False` and `grants_scientific_authority = False`.

### T6-A — social evidence record
Content-bound report with:
- report/agent/claim identities;
- direct-observation IDs;
- upstream-source/provenance IDs;
- truthfulness/reliability evidence state `SATISFIED / VIOLATED / UNRESOLVED`;
- no inference that different process/model/agent IDs imply independence.

### T6-B — bounded independence
For one claim:
- violated truthfulness -> `UNRELIABLE`;
- unresolved truthfulness or missing provenance basis -> `UNRESOLVED`;
- shared direct observation or upstream source -> `CORRELATED`;
- only disjoint registered provenance under satisfied truthfulness -> `INDEPENDENT`;
- repeated correlated reports do not multiply independent evidence authority.

### T6-C — hidden contribution / credit state
Represent registered possible contributors with `OBSERVED / ABSENT / UNRESOLVED`.
- one observed and all others absent -> `EXCLUSIVE_SUPPORTED` (bounded causal-credit state only);
- multiple observed -> `SHARED`;
- any unresolved plausible contributor -> `UNRESOLVED`;
- no observed -> `NONE_OBSERVED`;
- no credit report authorizes scientific truth or publication credit.

## Saturation assessment

The ingredients are prior art: rational metareasoning/value of computation; constrained decision-making; safe/model-validity regions; conformal/predictive safety; robust control; Bayesian networks/provenance; social learning; epistemic logic; mechanism design; strategic communication; multi-agent credit assignment. The possible ORION residual is only the bounded cross-coordinate **scientific-admissibility composition**, and even that remains unclaimed until #287 and prospective discrimination.

## Challenge to saturation

Potential reasons this implementation is wrong or too broad:
- one-step value-of-computation is insufficient for sequential information gathering;
- net value may require distributions/risk rather than one expected scalar;
- obligations may have deadlines/dependencies rather than simple active membership;
- validity regions may be continuous/probabilistic rather than discrete context IDs;
- context membership itself may be uncertain;
- independence may require a full causal/probabilistic graph rather than shared-ID overlap;
- truthfulness cannot generally be represented as a three-state exogenous input;
- hidden contribution may be non-identifiable even with registered actors;
- existing parent formalisms may subsume these objects entirely.

These are explicit reopen triggers. Do not implement richer semantics before countermodels require them.

## Competing implementation hypotheses

### H1 — small deterministic bounded contracts (selected)
Use content-bound finite objects and fail-closed tri-state evidence. Suitable for countermodels and native framework embedding.

### H2 — probabilistic/POMDP/credal unified controller
Rejected for this tranche: would prematurely choose likelihoods, risk semantics, horizon and calibration.

### H3 — hard-coded action/social/context taxonomies
Rejected: action kinds, contexts and social roles remain caller-declared until the research issues stabilize them.

### H4 — wire directly into autonomous Self-ORION loop
Rejected for T4–T6. Formal objects land first; cross-mechanic runtime composition belongs to T7 after countermodels and CI.

## RED hostile tests required before GREEN implementation

### T4
- mandatory protected verification selected even with negative net value over a high positive-value optional LLM/planning action;
- an optional action cannot compensate an uncovered hard obligation;
- unresolved action that might discharge an otherwise uncovered hard obligation -> `UNRESOLVED`;
- equal eligible optima remain `MULTIPLE_OPTIMA`;
- all nonmandatory eligible net values <= 0 -> `LOCAL_COMPUTATION_STOP`;
- missing authority blocks action;
- computation selection report cannot grant scientific/revision/adoption authority.

### T5
- supported context -> in-scope;
- invalid context -> blocked;
- unresolved and unknown context -> unresolved;
- containment cannot establish model correctness;
- successor envelope links parent digest and does not mutate parent;
- contradictory duplicate context entries rejected.

### T6
- different agent IDs with same upstream source -> correlated;
- different agents with disjoint registered observations/sources + satisfied truthfulness -> bounded independent;
- missing provenance or unresolved truthfulness -> unresolved;
- violated truthfulness -> unreliable;
- one observed contributor + another unresolved plausible contributor -> credit unresolved;
- two observed contributors -> shared;
- one observed + all other registered contributors absent -> bounded exclusive-supported;
- social evidence/credit reports cannot self-authorize claims.

## Paper boundary

P5 working manuscript may be updated only to say these successor formal mechanics exist and remain non-authorizing; H1–H4 stay `CANNOT_CHECK`. P6 receives additive successor theory/manuscript material. P1/P2/P3/P4/P7/P8 ready/frozen publication packages are not edited. P3 active PRs are read-only. Cross-paper consequences go to a programme handoff.

## Reopen triggers

- #454 identifies an existing formalism that subsumes a new object;
- T4 one-step selector fails a finite sequential countermodel;
- containment scope cannot be represented without model mutation;
- social provenance overlap is insufficient to characterize dependence;
- T7 composition exposes circular authority or inconsistent ordering;
- prospective #455 shows these mechanics add no value or cause harmful underthinking/overcontainment;
- any path makes expected value, containment, social consensus, or formal selection into scientific authority.

## Claim ceiling

A green T4–T6 tranche establishes only deterministic formal behavior on frozen finite countermodels and safe framework data structures. No scientific efficacy, novelty, generality, social truth, autonomous authority, or publication readiness is authorized.
