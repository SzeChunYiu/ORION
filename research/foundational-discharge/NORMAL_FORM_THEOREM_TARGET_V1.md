# Scientific Status Transition Normal-Form Theorem Target V1

**Date:** 2026-08-20  
**Status:** `PROSPECTIVE_FORMAL_TARGET__NOT_A_PROVED_THEOREM`  
**Parents:** `PROTOCOL_V1.md`, `NEAREST_PRIOR_ART_AND_RESIDUAL_V1.md`

## Motivation

The Scientific Status Transition Factorization conjecture is not scientifically interesting if `AdmissibleStatusChange` is merely *defined* to be the conjunction of the desired gates. The programme needs a non-tautological result derived from a more primitive operational semantics.

The stronger target is therefore a **normal-form theorem for scientific status transitions**.

## Primitive workflow semantics

Assume a workflow language whose primitive events include:

- creation/observation of scientific artifacts;
- donor-native validation events;
- retrieval/acquisition and question-conditioned processing;
- scientific inference applications;
- identity/mapping operations;
- formulation/revision proposals;
- promotion/release operations;
- representation/navigation transforms;
- revalidation after scientific change;
- authorization/delegation/coercion events;
- blocker introduction/refutation;
- support-family creation/revocation;
- epoch/version transitions.

A workflow trace records exact object identity, content, scope, epoch, provenance and event chronology. The semantics assigns a scientific-status transition only from these primitive events and registered rules; it does not define admissibility by naming the desired factorization.

## Candidate normal form

For every accepted transition changing the scientific standing of target object `o`, seek a certificate

`Pi_o = (pi_V, pi_S, pi_E, pi_B)`

where:

- `pi_V` is a **native-validity witness** for every local artifact used by the transition;
- `pi_S` is a **target-sufficiency witness** showing that the information exposed to the registered rule distinguishes the target decision at the required resolution;
- `pi_E` is a **target-bound discharge witness**: an admissible inference/identity/closure/promotion/revalidation/transport/authority bridge connecting the valid inputs to the exact target type, content, scope and epoch;
- `pi_B` is a **blocker/support witness** showing that every load-bearing blocker is refuted and at least one required complete support family remains valid.

## T-NF — normal-form completeness

For a nontrivial registered workflow class `C`:

> Every semantically admissible status transition has an equivalent certificate in the four-part normal form above.

This direction must be proved by normalization over the primitive workflow semantics, not by definition.

## T-S — certificate soundness

> Any well-typed normal-form certificate whose four witnesses validate against the registered target semantics authorizes the corresponding status transition.

Together T-NF and T-S establish a two-way correspondence between operationally admitted transitions and independently checkable scientific-discharge certificates.

## T-I — factor independence / non-substitutability

For each load-bearing factor `X in {V,S,E,B}`, construct a matched pair of traces identical on the other three factors but differing on `X`, with different scientific-status outcomes.

This is stronger than one ablation table: it requires explicit separating countermodels showing that no amount of success on the other factors can substitute for the missing factor within the theorem class.

Existing ORION results suggest candidate instances:

- P4 supplies non-compensatory promotion separations;
- P6/P7 supply full-repair sufficiency plus strict-subset necessity;
- P8 supplies type/bridge/blocker/support separations and paired widening countermodels;
- P1/P2/P3 supply empirical target-authority separations.

These are motivation and bounded instances, not a proof of T-I for the general workflow class.

## T-R — representation invariance

Define an equivalence `~_o` over workflow representations that preserves every primitive fact relevant to `Pi_o` while permitting arbitrary implementation organization.

> If `A ~_o A'`, then both representations admit exactly the same normal-form certificate validity and hence the same target scientific-status transition.

This is the programme-level theorem suggested by repeated ideal-product ties. It must be proved from the normal form rather than separately asserted for each architecture.

## T-C — compositionality

For transitions `o_0 -> o_1` and `o_1 -> o_2`, normal-form certificates compose only if the target contract produced by the first is admissible as a source contract for the second or an explicit registered bridge proves the required equivalence/transport.

The composed certificate must preserve:

- content/scope/epoch consistency;
- authority non-widening except through an explicit bridge;
- unresolved blockers;
- support-family provenance and revocation;
- native validity of donor-local artifacts.

P7 and P8 provide bounded composition instances; the theorem target is a generic composition rule for the workflow class.

## T-M — minimal-certificate research target

Do **not** initially claim global mathematical minimality of the four factors. Instead require:

1. T-I separating countermodels for each factor;
2. strict-subset witness families in at least two independent scientific-transition classes;
3. proof that any proposed factor removal makes T-S or T-NF false in the registered class.

Only then may the four-part normal form be described as minimal for that class.

## Prospective predictions generated by the theorem target

The theorem should predict before outcome access that:

1. an information-equivalent architecture will tie ORION on target decisions;
2. a richer representation will add no decision value if it preserves exactly the same normal-form witnesses;
3. local correctness plus target information sufficiency will still fail if the discharge witness is absent;
4. target authorization plus locally valid inputs will still fail if the interface is non-identifying and therefore lacks a sufficiency witness;
5. status after material change will be restored by re-establishing the affected certificate witnesses without invalidating unrelated native-valid artifacts;
6. a matched target-widening composition will fail exactly at the bridge witness while all donor-native judgments remain valid.

## Prospective falsifiers

The normal-form target fails or must be enlarged if:

- an admissible transition in the primitive semantics has no four-part certificate;
- a valid four-part certificate authorizes a transition the primitive semantics rejects;
- two representation-equivalent systems disagree on the target transition;
- one factor is removable without changing any admissible transition in the target class;
- a legitimate novel scientific inference requires a form of authority that cannot be represented as a registered target-bound bridge;
- a real scientific domain needs an additional load-bearing factor not reducible to the four witnesses.

## Why this could be foundational if it survives

A successful theorem would provide a common proof object for scientific-status changes that are currently governed separately by retrieval logic, identity resolution, verification, workflow closure, certification, provenance, and authorization. The scientific contribution would not be any one of those donor mechanisms. It would be the demonstrated claim that heterogeneous autonomous-science transitions share one normal form, together with exact conditions for soundness, completeness, representation invariance and composition.

That would be a genuinely stronger result than a suite of benchmarks or a rhetorical unification. It would still require prospective empirical confirmation that the formal object predicts real scientific failure modes rather than merely fitting existing ORION cases.

**Current terminal:** `SCIENTIFIC_STATUS_NORMAL_FORM__PROSPECTIVE_THEOREM_TARGET__UNPROVED`.
