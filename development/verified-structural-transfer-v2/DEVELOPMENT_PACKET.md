# Verified Structural Transfer V2 — productionization development packet

**Development question:** Can the locally falsified transfer prototypes from PR #131 be converted into deterministic, content-addressed, replayable ORION infrastructure and paper-scoped V2 study hooks without altering any already-frozen P1–P5 V1 protocol or laundering local engineering evidence into scientific authority?

**Base subject:** `ecdaa00acd4a92d226497d01705fecd5d38d26c8`.

**Tracking issues:** #136, #137, #138, #139, #140, #141.

## Atomic development fibres

1. Canonicalize `ProblemSignature`, `AlgorithmCell`, transfer evidence and decisions into deterministic JSON.
2. Content-address every registered signature/cell/evidence payload and detect digest mismatches before use.
3. Produce immutable transfer receipts that bind target, cell, evidence, decision, structural score and reason codes.
4. Build a deterministic solver portfolio that cannot promote `BLOCKED_ASSUMPTION`, `OBSTRUCTED` or `CANNOT_CHECK` candidates and can optionally require independent source domains.
5. Add file-backed registry/catalog loading without dynamic imports, code execution or implicit trust in catalog metadata.
6. P1 V2: wrap responsibility diagnosability in explicit action licensing receipts; non-diagnosable/low-confidence/conflicting states fail closed.
7. P2 V2: wrap the conservative allocator in replayable state/action receipts while preserving censored feedback and route/task authority separation.
8. P3 V2: add typed scientific coordinates and mapping receipts above the affine known-answer substrate; type mismatch, missing anchors and inconsistent cycles fail closed.
9. P4: add protected-custody evidence-plan receipts; the planner remains structurally incapable of returning an authority terminal.
10. P5 V2: add staged candidate receipts and append-only negative-history commitments; fail/harm dominates missing stages and terminal remains host recommendation only.
11. Add machine-readable V2 manifests for all five papers and explicitly bind them to V2/future-study status rather than frozen V1 execution.
12. Add schemas, CLI replay path and hostile tests; require exact-head full repository CI before merge.

## Incumbent mechanics and negative history recovered

- V1 transfer prototypes already passed 31 local hostile tests and found two implementation defects: P2 post-rejection state mutation and P5 missing-stage masking of later harm. V2 must preserve those repaired invariants and add provenance/replay guarantees rather than redesigning the algorithms.
- Current P1 work has advanced on `main`; P2, P4 and P5 also have active concurrent PRs. This lane must therefore avoid editing those owned study/manuscript/protocol surfaces and integrate through additive transfer V2 manifests/harnesses.
- ORION's publication protocols distinguish `DESIGN_FROZEN`, `EXECUTION_FROZEN`, outcome access and external authority. V2 artifacts are not allowed to mutate those states.
- `CANNOT_CHECK` is a valid terminal for insufficient evidence and must survive serialization, replay and aggregation.

## Saturation assessment

Knowledge saturation is inherited from the V1 far-domain audit for the mechanics themselves. The V2 question is implementation integrity rather than novelty: deterministic serialization, content addressing, replay, typed receipts, fail-closed aggregation and paper-bound future-study manifests are standard engineering concepts and are not claimed as research novelty.

Search-universe saturation is bounded by the repository's existing governance primitives: publication manifests, content hashes, protected custody, replay/reproduction, typed authority states and multi-agent branch protocol. No new external mechanism is required to implement the productionization safely.

Formulation saturation: the task is not "make the prototypes production code" in the broad sense. The bounded formulation is "make every decision inspectable, content-addressed and replayable while preserving the V1 semantic invariants and V1/V2 evidence boundary."

## Challenge to the saturation basis

This can be falsely complete if deterministic JSON is mistaken for provenance, if a receipt binds a mutable identifier rather than content, if registry order changes portfolio output, if unknown evidence is defaulted to false/zero, or if a paper V2 manifest silently imports a V1 result as evidence. Hostile tests therefore target identity, ordering, omission, duplicate-domain and authority-boundary failures rather than only happy-path arithmetic.

## Miss hypotheses

1. Duplicate identifiers with different content may create registry ambiguity unless digest equality is enforced.
2. Floating-point serialization or set iteration may make identical inputs produce different digests/receipts.
3. Evidence maps may contain extra keys that appear authoritative unless only declared assumptions/falsifiers are bound to the decision.
4. Portfolio construction may accidentally treat absence of evidence as a skipped candidate rather than an explicit `CANNOT_CHECK` receipt.
5. P1 action licensing may accidentally infer permission from the best label without a confidence/diagnosability gate.
6. P2 rejected/censored actions may mutate replay state or be conflated with zero reward.
7. P3 type mismatches may be hidden by numerically invertible transforms.
8. P4 plan selection may be mistaken for authority readiness if receipt vocabularies overlap.
9. P5 negative history may be overwritten by re-registering a candidate ID or may hide known later harm behind missing earlier stages.
10. A V2 manifest may accidentally point at a V1 protocol as if it were execution-authorizing.

## Frozen implementation hypothesis

> If all transfer candidates, evidence and decisions are content-addressed, serialized canonically and evaluated by fail-closed typed receipts, then the V1 mechanics can be integrated as deterministic ORION infrastructure without creating new authority or contaminating frozen publication V1 studies.

This is a local engineering hypothesis only.

## Frozen hostile tests

- canonical serialization is invariant to input mapping/set order;
- changing any bound field changes the content digest;
- duplicate IDs with different digests are rejected;
- missing evidence yields an explicit `CANNOT_CHECK` receipt, never silent omission or admissibility;
- structural score cannot override false assumptions or failed falsifiers;
- cross-confirmation counts distinct source domains only;
- portfolio output is deterministic under catalog permutation;
- tampered receipt digest or target/cell/evidence digest is rejected on replay;
- P1 blind probes do not license any mutation; evidence/execution cannot license formulation/search-universe actions;
- P2 censored observations do not update reward; unsafe rejected records leave state unchanged; replay reconstructs the same state;
- P3 type mismatch, missing anchors and corrupted cycles yield non-GLUE outcomes;
- P4 unprotected actions are ignored and no planner receipt can say `AUTHORIZED`;
- P5 any known fail/harm dominates missing stages; protected uncertainty blocks; archived negative history cannot be overwritten by conflicting content;
- every paper manifest declares `V2_FUTURE_STUDY`, `outcome_accessed=false`, and no execution authority.

## Reopen triggers

Reopen design rather than extending code if a receipt can be forged without a digest mismatch, order changes deterministic output, any V2 integration needs to edit a frozen V1 protocol to function, any helper can escalate publication/authority state, or full CI exposes interaction with a production path not covered by the additive boundary.
