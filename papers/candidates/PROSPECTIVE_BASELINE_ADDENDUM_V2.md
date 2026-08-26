# ORION-16–ORION-18 prospective baseline addendum V2

**Date:** 2026-08-17  
**Relationship:** additive to each paper's `PROSPECTIVE_EVALUATION_V1.md`.  
**Status:** baseline requirements only; `NO_RESULT`.

The second breadth pass found mature parent fields that make several earlier baselines too weak. These additions are mandatory before a broad candidate-paper claim.

## ORION-16 baseline additions

### B5 — self-adjusting / incremental change-propagation baseline
Represent the computation or workflow with an explicit dynamic dependence graph and propagate changes only through affected computation, preserving reusable unaffected work.

**Purpose:** prevent ORION-16 from winning merely because it has dependency-aware incremental repair.

**Required comparison families:**
- dependency-only mutation/recompute;
- independent-support preservation;
- repeated local changes with reusable prior computation.

**ORION-16 can only add value if:** a case requires a distinct epistemic terminal or constraint—e.g. unauthorized commit, unresolved hard obligation, certification reopening, content/provenance condition, or chronology-sensitive audit—that the faithful incremental-computation baseline is not designed to decide.

## ORION-17 baseline additions

### B5 — schema/specification-preserving transformation
A transformation baseline that preserves the frozen semantic/specification properties defined by the source/target schema model.

### B6 — bidirectional/lens-style transformation
A source/view or chart/chart relation with explicit update laws or bidirectional propagation.

### B7 — provenance-assisted schema evolution
A transformation/reconstruction baseline that retains sufficient provenance to reconstruct prior state/results under schema change.

### B8 — conceptual/signature or ontology-revision baseline
A donor representation where the vocabulary/signature/interpretation changes explicitly rather than only values in a fixed schema.

**Purpose:** prevent ORION-17 from winning merely because it can map old states into a changed representation.

**ORION-17 can only add value if:** the frozen case separates:

1. successful representation/data/evidence transport, from
2. successful **scientific obligation/closure transport**.

The key matched pair should preserve the same content-bound evidence in both cases while changing whether the old closure remains authorized under the target objective/ontology.

## ORION-18 baseline additions

### B7 — proof-carrying / linear authorization
Authorization is granted only when a valid formal proof/credential exists under the frozen policy.

### B8 — stateful/temporal authorization
Authorization decisions depend on explicit current state/time and reject stale request-time approval when relevant state has changed.

### B9 — authorization-policy type discipline
A typed implementation/policy-conformance baseline that rejects uses inconsistent with logical policy types/dependencies.

### B10 — logical attestation
Machine-checkable attributable statements about runtime/program properties serve as credentials for authorization.

### B11 — policy-composition logic
An explicit grant/deny/conflict/unspecified or comparable multi-valued policy composition baseline.

### B12 — non-interference / information-flow typing
A typed-flow baseline prevents judgments/information from crossing forbidden domain boundaries.

### B13 — policy-state serializable concurrent governance
A stateful-agent baseline in which the committed effect must be authorized against the policy state immediately preceding commit, preventing stale authorization under concurrency.

**Purpose:** prevent ORION-18 from winning merely because judgments are typed, proof-bearing, stateful, epoch-bound or prohibited from arbitrary cross-domain flow.

**ORION-18 can only add value if:** the target action's hard **scientific epistemic obligation semantics** matter. A valid source judgment must fail to discharge a target obligation even when ordinary policy-flow/state freshness is correct; an explicit ORION-18 coercion may succeed only when it proves the target obligation is actually discharged without semantic weakening.

## Cross-paper matched discriminator

A useful common benchmark pattern is a three-layer matched case:

### Layer 1 — computational preservation
The update can be propagated incrementally and the current data/state is consistent.

### Layer 2 — evidence preservation
The old evidence/data object remains content-valid in the transformed representation.

### Layer 3 — epistemic authority preservation
The transformed evidence either does or does not discharge the target scientific obligation required for closure/merge/assert/promotion.

A strong ORION result should show that the parent baseline correctly handles its own layer while a higher-layer decision still differs. If no such case exists after faithful encoding, the candidate generalization contracts.

## Result discipline

These baselines are prospective requirements. They do not authorize a result until:

- exact implementations/adapters are version-bound;
- native donor behavior is reproduced on donor fixtures;
- hidden ORION labels are frozen before candidate runs;
- matched negative/positive controls are retained;
- adapter impossibility is recorded as `CANNOT_CHECK` rather than replaced with a weak substitute.