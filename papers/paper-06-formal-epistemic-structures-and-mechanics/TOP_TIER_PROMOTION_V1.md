# P6 top-tier promotion V1 — Epistemic Transition Systems

**Programme:** #977  
**Existing controlled authority:** `THEORY_FINISHED_V2_1` / peer-review package remains valid.  
**Top-tier state:** `EXTERNAL_PROMOTION_PENDING`

## Maximum claim to earn

> **Epistemic Transition Systems (ETS):** correctness-preserving state change is insufficient for scientific admissibility. Across heterogeneous state-changing systems, a transition must additionally preserve or explicitly reopen typed evidence meaning, outstanding obligations and commit authority; these requirements compose under explicit transport conditions and are not recoverable from a computation/dependency-only erasure in general.

This is deliberately above dependency repair, truth maintenance, effect systems, belief revision and incremental computation. Those mechanisms are donors.

## Donor-complete baseline

Build the strongest integrated comparator from:

- dependency/support tracking and selective recomputation;
- truth-maintenance / multiple-support semantics;
- effect/permission constraints;
- provenance and evidence binding;
- generic authorization / policy enforcement;
- existing ORION P1/P4/P8 interfaces only as frozen upstream donors, without re-owning their claims.

The baseline must receive the same state, transition and evidence information as P6.

## Upward theorem programme

### T6.1 — Transition factorization

Define a state transition as a product of at least:

`(computational support, evidence meaning, scientific obligation, authority/commit)`.

Prove sufficient conditions under which preservation at a higher coordinate implies required lower-coordinate preservation/revalidation, and exhibit non-implications in the reverse direction.

### T6.2 — Composition under transport

For transitions `A -> B -> C`, characterize when admissibility certificates compose and when intermediate evidence/obligation transport forces reopening.

A transitive theorem must name epoch/context assumptions explicitly; stale certificates may not compose by default.

### T6.3 — Erasure non-full-abstraction generalization

Generalize the existing typed-erasure separation from the current P6 model to the strongest donor-complete transition interface used in the external study. The theorem target is not "all computation is insufficient"; it is an explicit pair of scientifically distinct states/transitions collapsed by the donor-only observable interface.

## Protected external study

Freeze at least three transition families before protected execution:

1. **formal/software:** proof/build/workflow dependency repair after upstream changes;
2. **agent memory/tool state:** persistent state updated after source/evidence invalidation;
3. **scientific evidence state:** analysis/claim state changed after measurement, source or evaluator revision.

For each family construct:

- clean transition;
- computationally valid but scientifically inadmissible transition;
- independent-support case where unnecessary reopening is harmful;
- stale-epoch/context case;
- hidden-read/hidden-dependency attack;
- authority laundering case.

### Primary endpoints

- unsafe admissible-transition false positive rate;
- unnecessary-reopen false positive rate;
- correct obligation persistence;
- correct independent-support preservation;
- correct `CANNOT_CHECK` under missing transport evidence;
- transition/revalidation cost.

P6 must beat the donor-complete product on scientific-admissibility errors without degenerating to always-reopen.

## Strongest hostile attacks

- donor product extended with every P6-visible coordinate except P6 terminology;
- all P6 gains vanish once the donor baseline gets equivalent evidence information;
- P6 simply duplicates P8 authorization;
- P6 simply rephrases P1 selective reopening;
- hidden state gives P6 privileged dependency/evidence information;
- a safe donor transition is blocked because P6 over-conservatively requires full recomputation;
- certificate composition silently ignores epoch/context drift.

## Independent authority

At least one of:

- machine-check the central transition/composition theorem in a proof assistant; or
- obtain a second independent executable checker implementing the formal semantics and reproducing every protected classification.

External study adjudication must be generated from frozen transition facts, not from labels emitted by P6 itself.

## Top-tier promotion gate

`P6_TOP_TIER_SUBMISSION_READY` requires:

- [ ] T6.1 closure;
- [ ] T6.2 closure;
- [ ] generalized erasure witness against donor-complete observable interface;
- [ ] three protected transition families executed;
- [ ] donor-complete comparator implemented fairly;
- [ ] P6 reduces unsafe scientific-admissibility decisions without always-reopen collapse;
- [ ] independent theorem/checker authority;
- [ ] cross-paper non-overlap review against P1/P4/P7/P8;
- [ ] fresh nearest-work saturation immediately before submission;
- [ ] exact reproduction/package binding.

If the donor-complete product becomes extensionally equivalent to P6, record the equivalence as the result; do not manufacture residual novelty.
