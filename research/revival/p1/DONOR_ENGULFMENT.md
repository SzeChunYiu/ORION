# P1 donor engulfment architecture

**Status:** framework doctrine and executable-substrate map, 2026-08-18.  
**Machine-readable authority:** `P1_DONOR_ENGULFMENT_V1.json`.  
**Coverage authority:** `P1_DONOR_ASSIMILATION_COVERAGE_V1.json` + Round B/C receipts.

## Rule

ORION does not respond to nearest work by deleting the overlapping mechanism from the system. It responds by **learning it, crediting it, and absorbing its strongest reusable structure**.

For Paper 1:

- `ADOPT` means the donor mechanism becomes incumbent ORION substrate when it improves the research process.
- `ADAPT` means the donor structure is retained but translated into ORION's typed scientific-state contract.
- `COMPOSE` means the donor structure becomes a parent component in a larger mechanism; its atom remains donor-owned.
- `DEFER` means the mechanism is learned and kept as an explicit reopen trigger, but is not forced into the active system without task-isomorphic evidence.
- `REJECT` preserves negative history and supplies no scientific or architectural authority.

**Engulfment is not appropriation.** Provenance travels with the component. A donor-owned atom does not become ORION novelty merely because ORION executes it internally.

## Executable absorbed layers

### 1. Inquiry/revision state

Absorbs the strongest structures from Iris, AGM belief revision, ATMS/TMS context handling, Kosmos-style structured state, and AREX-style retained context.

ORION substrate:
- explicit scoped claims rather than hidden conversational memory;
- support/refutation pointers;
- `add / update / invalidate` transitions;
- qualified or invalidated status;
- evidence acquisition kept distinct from solution/formulation mutation.

Runtime: `InquiryRevisionState`, `ClaimRecord`.

### 2. Causal diagnosis and active inquiry

Absorbs REFLECT's diagnosis-specific controlled replay and attribution update; CAR's intervention/do-operation framing; Who&When/MAST failure-attribution discipline; OAT-style suspicion priors; MedAction/value-of-information probe selection; ARTS-style execution-vs-hypothesis diagnosis.

ORION substrate:
- competing cause hypotheses;
- cheapest separating probe selection;
- intervention outcome as causal evidence;
- priors/rankings may direct attention but never grant mutation authority.

Runtime: `InterventionEvidence`, `DiagnosticProbe`, `choose_information_probe`.

### 3. Admissible recovery

Absorbs R2Act and DARC's strongest post-diagnosis lesson: correct diagnosis does not imply a valid recovery action. Recovery must be chosen from an incident/task-specific admissible action/target space.

ORION substrate:
- diagnosis-conditioned action admission;
- invalid action/target rejection before execution;
- selective recovery interface rather than uniformly broader prompting/context.

Runtime: `RecoveryAction`, `admit_recovery_action`.

### 4. Dependency and truth maintenance

Absorbs EviGraph downstream regeneration, EA-Graph staleness, Doyle/de Kleer truth maintenance, systems-engineering change-impact analysis, STARTS/incremental-build transitive invalidation, and SCION dependency-aware planning.

ORION substrate:
- changed coordinates identify directly affected closures;
- transitive dependency closure identifies stale descendants;
- unrelated verified state is preserved;
- rollback/reopening is a reusable substrate, not a Paper-1 novelty atom.

Runtime: `DependencyNode`, `dependency_impact_closure`.

### 5. Verification obligations

Absorbs requirements-verification-matrix discipline: a missing verification relation is itself a defect.

ORION substrate:
- every claim/mechanic relation must have a verification cell;
- empty cells mechanically emit obligations rather than disappearing into prose TODOs.

Runtime: `VerificationObligation`, `missing_verification_obligations`.

### 6. Certificate-bound execution

Absorbs the proposal/admission/execution split exemplified by Sovereign Assurance/Execution Boundary work: non-deterministic reasoning should not itself be the mutation actuator.

ORION substrate:
- an upstream process earns a certificate;
- runtime enforcement checks exact action, scope, epoch/revocation and state binding;
- live-state drift, scope mismatch or expiry fails closed;
- enforcement never manufactures authority.

Runtime: `MutationCertificate`, `ExecutionRequest`, `enforce_certificate`.

## Orchestration/evaluation layers also engulfed

AREX recursive audit/follow-up, AI Scientist-v2 tree exploration, AI Co-Scientist role specialization, Agent Laboratory stage/cost accounting, Agent-MD selective escalation, SciAgentArena stepwise verification, and Who&When-style controlled attribution benchmarking are integrated as orchestration/evaluation doctrine. They are not standalone P1 novelty.

## What remains for Paper 1 after engulfment

The current candidate residual is deliberately **not** generic attribution, active diagnosis, recovery selection, scoped invalidation, a permission table, or a runtime certificate broker. Those are now incumbent framework parts.

The powered P1 V2.2 successor tests one narrower scientific mechanism:

> Before a high-level scientific `K/W/M` mutation is admitted, require counterfactual evidence that the mutation is **necessary rather than merely locally successful**: registered lower-level alternatives fail, the candidate mutation restores the target, protected sibling/invariant checks survive, and its observed dependency impact matches the bound reopen set.

The confirmatory study must compare against the engulfed framework, including active diagnosis and diagnosis-to-action + dependency parents. If the residual does not add value once those donor structures are present, the Paper-1 claim must narrow again.

## Fixed-point rule

Nearest-work saturation is reached only when two consecutive hostile searches add no structure that changes:

1. the active ORION framework,
2. the strongest comparator,
3. the causal mechanism under test, or
4. the surviving novelty statement.

A new useful donor found later is **food**: integrate it, rerun the affected discriminator, and shrink ORION's novelty if necessary.
