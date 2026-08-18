# Issue #417 completion receipt

**Terminal sought:** `P6_METHOD_FIBRE_FORMALISM_MERGED`  
**Scope:** #417 only. The broader empirical discriminator #419 remains a separate bounded/narrowed study.  
**Frozen-package rule:** the content-bound P6 V2.1 candidate is not modified; successor material lives under `research/extensions/p6-method-fibres/`.

## Formal objects

- [x] Reconcile coordinate names with P1 rather than duplicate ownership — `P6.P1MethodRealizationAdapter.v1` is version-gated to `P1.MethodRealization.v1@issue-404` and binds the upstream digest.
- [x] Mandatory/optional/claim-relative coordinates stated — executable `P1_ADAPTER_PROFILE` plus manuscript table.
- [x] Unknowns explicit — upstream unknown fields remain bound in the adapter; existing P6 preserved-coordinate UNKNOWN remains `UNRESOLVED`.
- [x] Preserved coordinates — `StructuralReduction.v1`.
- [x] Erased coordinates — `StructuralReduction.v1` with exact erasure justification.
- [x] Transformations/normalizations — `P6.StructuralReductionProcedure.v1`.
- [x] Preservation obligations — base reduction + procedure receipt.
- [x] Unresolved coordinates — base reduction + adapter context partition.
- [x] Erasure admissibility — exact justifications required for every erased base/context coordinate.
- [x] Signature reduction identity/version — `StructuralSignature.v1` + `P6.StructuralSignatureContract.v1`.
- [x] Preserved structural coordinates — content-bound in base signature.
- [x] Provenance to contributing realizations — signature contract.
- [x] Load-bearing assumptions/invariants — signature contract binds reduction load-bearing coordinates.
- [x] Effect/reconstruction obligations — signature contract.
- [x] Uncertainty/obstruction — `SUPPORTED/UNRESOLVED/OBSTRUCTION` retained.
- [x] Evidence-bound fibre membership — existing membership evidence/receipt.
- [x] Incompatible assumptions block/UNRESOLVED — existing hostile tests/bench.
- [x] One panel insufficient — `ONE_PANEL_EFFECT_COINCIDENCE_INSUFFICIENT`.
- [x] Lineage recoverable — `P6.FibreLineageIndex.v1` maps member digest to upstream adapter receipt.

## Higher-order method operators

- [x] Sequential composition — existing `CompositionContract`.
- [x] Conditional composition — existing `CompositionContract`.
- [x] Parallel/independent composition — existing collision checks.
- [x] Specialization — existing directional relation + new preorder witness.
- [x] Generalization — existing directional relation + new preorder witness.
- [x] Compatible-realization substitution — `P6.CompatibleRealizationSubstitution.v1`.
- [x] Representation lift/project — existing lift + new project semantics.
- [x] Explicit preorder — `P6.StructuralPreorderWitness.v1`, tested for reflexive/transitive supported examples and explicitly non-membership-authorizing.
- [x] Same-fibre vs new-signature composition — `classify_fibre_composition` returns `STAYS_IN_FIBRE`, `NEW_SIGNATURE_REQUIRED`, `BLOCKED`, or `UNRESOLVED`.

## Manuscript bridge

Evidence: `METHOD_FIBRES_MANUSCRIPT_BRIDGE_V1.md`.

- [x] `Concrete realizations and structural reduction`.
- [x] `Claim-relative method fibres`.
- [x] `Faithful substitution and composition`.
- [x] `Generalization, specialization and representation change`.
- [x] Worked cross-domain illustration — numerical bisection ↔ monotone threshold calibration, explicitly illustrative rather than empirical generality evidence.
- [x] False fibre — same midpoint/discard-half surface loop with erased monotonicity/bracketing invariant.
- [x] Explicit P9 boundary — learned similarity cannot define fibre membership or authority.

## Core propositions / executable countermodels

- [x] Surface equivalence insufficient.
- [x] One finite panel insufficient.
- [x] Load-bearing erasure can be unsound.
- [x] Faithful substitution requires explicit preservation conditions.
- [x] Composition closure conditional.
- [x] Generalization/specialization directional, not equivalence.
- [x] Missing evidence remains `UNRESOLVED`; downstream scientific authority may remain `CANNOT_CHECK`.

Primary bounded evidence remains `MethodFibreBench.v1`: 12/12 expected outcomes, including false-fibre and clean no-alarm cases. The broader #419 terminal remains intentionally `P6_METHOD_FIBRE_FORMALISM_NARROWED` until its separate external/comparator/correspondence programme is executed.

## Ownership / nonclaims

- [x] No claim P3 accurately extracts arbitrary-paper structures.
- [x] No claim P2 retrieves useful distant donors.
- [x] No claim P9 latent geometry recovers formal fibres.
- [x] No claim P10 invents fibres/methods.
- [x] No generic graph/category/action-model/refinement mechanism is relabeled ORION novelty.

These boundaries are stated in the manuscript bridge and reinforced by non-authorizing fields in the new receipts.

## Verification paths

- `src/orion/transfer/v2/p6_method_fibres.py` — merged core from #436.
- `src/orion/transfer/v2/p6_method_fibre_completion.py` — #417 completion contracts.
- `tests/test_p6_method_fibre_extension.py` — original core hostile tests.
- `tests/test_p6_issue417_completion.py` — completion hostile/positive tests.
- `research/extensions/p6-method-fibres/METHOD_FIBRE_BENCH_V1.json` — frozen 12-case panel.
- `research/extensions/p6-method-fibres/METHOD_FIBRE_BENCH_SUMMARY_V1.json` — frozen bounded result.
- `research/extensions/p6-method-fibres/METHOD_FIBRES_MANUSCRIPT_BRIDGE_V1.md` — successor manuscript text.

Close #417 only after exact-head repository CI and P6–P8 candidate CI are green and the completion PR is merged to `main`.
