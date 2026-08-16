# RAKL → ORION donor atlas V2

**Status:** ACTIVE / REPOSITORY-WIDE DONOR SATURATION OPEN

Frozen donor revision: `SzeChunYiu/RAKL@70f5f7c4a6771ffd1158765b42ac9f8aee8a270f`.

This atlas corrects the scope of `TRANSFER_INVENTORY_V1.md`. V1 exhaustively covered the **registered 24 method surfaces and 21 V3 overlays**. It did **not** prove that every useful model, mechanic, benchmark, negative result, engineering contract or executed failure in the RAKL repository had been dispositioned.

## Donor-first rule

Before clean-generation invention, ORION must prefer, in order:

1. `EXACT_REUSE` — same contract/assumptions survive; port code + tests with provenance.
2. `RECONSTRUCTED` — semantic mechanic survives but ORION state/interfaces differ.
3. `TESTS_RESULTS_REUSED` — implementation is obsolete or too coupled, but the falsifier/negative result is still reusable.
4. `DEFER_WITH_TRIGGER` — useful donor, but activation would be premature; retain a concrete trigger.
5. `REJECT_WITH_REASON` — donor does not survive target-specific comparison.
6. `OPEN_EQUIVALENCE_AUDIT` — not yet safe to invent around this area.

`OPEN_EQUIVALENCE_AUDIT` is not a terminal disposition and keeps issue #7 open.

## Public scientific/research families

| RAKL donor family | Representative donor | Current ORION disposition | Evidence / next action |
|---|---|---|---|
| method assimilation | `method_assimilation.py` | RECONSTRUCTED | ORION knowledge assimilation + donor-before-invention gate; audit exact method-candidate fields before further invention |
| Atlas gluing | `atlas_gluing.py` | OPEN_EQUIVALENCE_AUDIT | ORION has portrait/GLUE machinery, but exact overlap/cycle/obstruction report equivalence has not yet been proved |
| backward multi-seed / meet-in-the-middle | `backward_multiseed.py` | OPEN_EQUIVALENCE_AUDIT | High priority: search-from-obligations and meet witnesses are absent as a clearly equivalent ORION contract |
| bridge composition | `bridge_composition.py` | OPEN_EQUIVALENCE_AUDIT | Compare against ORION representation-map composition before any new bridge-search mechanic |
| capability shaping | `capability.py` | RECONSTRUCTED | ORION capability/method change remains governed; retain RAKL tests/results as donor evidence |
| challenge/failure learning | `challenge_learning.py`, `failure_learning.py` | RECONSTRUCTED | `TaskEpisode`, failure patterns, `DevelopmentIssue`, `EvolutionArchive`; negative-history semantics retained |
| claim↔evidence binding | `claim_evidence.py` | RECONSTRUCTED | ORION content/evidence bindings + authority gates; continue importing hostile substitutions rather than parallel schemas |
| epistemic context compiler | `context_compiler.py` | **EXACT_REUSE** | `orion.knowledge.context_compiler`; RAKL regressions including H30 carried over |
| formalism/mechanism/verification packets | `formalism.py`, mechanism/verification modules | OPEN_EQUIVALENCE_AUDIT | Map to ORION mechanic/formal readiness/verification objects; do not duplicate packet grammars first |
| generator transport | `generator_transport.py` | **EXACT_REUSE** | `orion.knowledge.generator_transport`; RAKL LIFT/RELATE/PROJECT tests carried over |
| identity / source identity / identity saturation | identity modules | RECONSTRUCTED + TESTS_RESULTS_REUSED | ORION source identity/read ledger; RAKL empty-lineage refusal directly repaired ORION false saturation |
| invention / positive goals / Pareto selection | invention modules | RECONSTRUCTED | ORION invention gate now additionally requires pinned RAKL donor audit |
| measurement-aware relations | `measurement.py` | **EXACT_REUSE** | `orion.knowledge.measurement`; RAKL M01–M18 / MU01–MU05-style regressions carried over |
| multiresolution memory | memory modules | OPEN_EQUIVALENCE_AUDIT | Compare exact rehydration/erasure/view semantics against ORION memory/context surfaces |
| promotion | promotion modules | RECONSTRUCTED | ORION scientific/method authority remains separately protected |
| promotion attestation | promotion-attestation modules | OPEN_EQUIVALENCE_AUDIT | Candidate for direct reuse/reconstruction into external host/evaluator custody |
| retrieval benchmark / factorized ground truth | retrieval benchmark modules | OPEN_EQUIVALENCE_AUDIT | High priority for Paper II and live trial; reuse factorized failure attribution rather than inventing a new benchmark ontology |
| route-family health / continuity | `route_family_health.py` | OPEN_EQUIVALENCE_AUDIT | ORION `route_control` is only route-local; RAKL longitudinal non-compensatory health, continuity and root-preservation logic is richer |
| typed similarity / analogy witnesses | `similarity.py` | **EXACT_REUSE** | `orion.knowledge.similarity`; corpus/retrieval/recognition/transfer failure localization retained |
| subject / execution identity attestation | subject identity modules | OPEN_EQUIVALENCE_AUDIT | Compare to ORION evidence/readiness lineage before adding any new attestation object |
| 24 canonical method surfaces | `method_specs.py` | RECONSTRUCTED | Existing V1 transfer profiles + evidence-bound answer loop |
| 21 V3 overlays | V3 modules registered in `method_specs.py` | PARTIAL TERMINAL | V1: 12 subsumed, 4 reconstructed, 5 trigger-deferred; still valid subset of V2 |

## Engineering donor programme

RAKL's engineering closure programme is a donor **result set**, not merely code. Its E0–E8 implementation ladder and E1–E20 fibres include executed hostile findings that should be imported as regression obligations whenever ORION implements the corresponding runtime surface.

| Donor wave/family | Current ORION disposition | Required reuse |
|---|---|---|
| E0 freeze/parity fixtures | TESTS_RESULTS_REUSED | Preserve exact-state fixture discipline for protected migrations |
| E1 additive state contracts | OPEN_EQUIVALENCE_AUDIT | Compare RAKL `ProjectSnapshot` / `EpistemicStatus` projection with ORION state before inventing another durable state model |
| E2 repository protocols/reference backend | OPEN_EQUIVALENCE_AUDIT | Reuse `BlobStore`, `SnapshotRepository`, `SemanticRepository`, `MetrologyRepository`, `TransitionRepository` contracts if ORION adds production persistence |
| E3 production persistence | DEFER_WITH_TRIGGER | Trigger: ORION moves beyond local/reference storage; inherit CAS/sequence/parity hostile tests |
| E4 epistemic-control integration | RECONSTRUCTED + TESTS_RESULTS_REUSED | ORION kernel hard gates/saturation; keep stale-certificate, missing-route, residual-reopen regressions |
| E5 durable workflow engine | OPEN_EQUIVALENCE_AUDIT | Reuse idempotency/retry-safe/heartbeat/exact-snapshot/`RECOVERY_REQUIRED` semantics before new workflow infrastructure |
| E6 service API / read-only observatory | DEFER_WITH_TRIGGER | Trigger: network service/UI; UI must render, never calculate, epistemic state |
| E7 operations/security/provenance | DEFER_WITH_TRIGGER | Trigger: production deployment; reuse build attestation, backup/restore, doctor/telemetry hostile cases |
| E8 fresh hostile production assurance | TESTS_RESULTS_REUSED | Preserve typed terminal vocabulary and clean-deployment/frozen-release assurance rule |
| E1–E20 hostile defects | TESTS_RESULTS_REUSED | Carry over applicable negatives: payload-hash binding, Atlas CAS, sequence rewind, FD leak, canonical encoding, empty-doctor OK, CANNOT_CHECK masking FAIL, resource ratchet, replay-before-staleness, coverage≠reachability, HTTP idempotency/staleness race, dead idempotency key, telemetry outage, silent schema repair, ghost index atom, context-ready-with-nothing |

## Exact-reuse tranche V2.1

The following donor mechanics are now copied in semantic substance under ORION ownership **with explicit RAKL provenance and regression transfer**:

- `src/rakl/context_compiler.py` → `src/orion/knowledge/context_compiler.py`
- `src/rakl/similarity.py` → `src/orion/knowledge/similarity.py`
- `src/rakl/measurement.py` → `src/orion/knowledge/measurement.py`
- `src/rakl/generator_transport.py` → `src/orion/knowledge/generator_transport.py`

Their tests are carried into `tests/unit/knowledge/` rather than replaced by new ORION fixtures.

## Governance change

`RaklDonorAudit.v1` now makes donor search a prerequisite of `InventionReadinessGate.v2`.

Required donor routes for a target-specific invention decision:

- public API;
- source tree;
- tests;
- research results;
- engineering substrate.

A missing/unfinished audit blocks invention. A donor disposition of `EXACT_REUSE` or `RECONSTRUCTED` pre-empts clean-generation invention and routes work to reuse instead. The gate grants no invention or promotion authority itself.

## Priority remaining donor audits

1. route-family health / root-coordinate preservation / continuity;
2. backward multi-seed and its hidden-path benchmark;
3. retrieval benchmark / factorized ground truth;
4. Atlas gluing + bridge composition;
5. multiresolution memory;
6. promotion + subject/execution attestation;
7. durable engineering repository/workflow interfaces;
8. all remaining public exports and research result families not yet listed with a terminal disposition.

## Closure rule

This atlas is **not saturated**. Issue #7 remains open until a fresh walk of the frozen RAKL public API/source/tests/research/engineering surfaces yields no relevant donor without a terminal disposition and all high-value `OPEN_EQUIVALENCE_AUDIT` rows have either been reused/reconstructed or rejected/deferred with evidence.
