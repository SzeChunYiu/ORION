# RAKL → ORION transfer inventory V1

Frozen RAKL source: `70f5f7c4a6771ffd1158765b42ac9f8aee8a270f`.

This inventory distinguishes **knowledge/mechanic transfer** from literal file copying. RAKL remains a provenance source; ORION owns the reconstructed contracts and implementations.

## Quantitative summary

- Canonical RAKL method surfaces: **24 / 24 represented in the ORION transfer catalog**.
- Current ORION mechanic graph: **59 reachable cells**.
- Leaf/cross-cutting mechanics receiving direct or adjacent RAKL surface profiles: **49 / 59**.
- Root/top-level mechanics receiving explicit ORION composition contracts: **10 / 59**.
- Current step-specific structural frontier answered at the specification layer: **826 = 59 × 14 evidence-bound AnswerRecords**.
- The 14 dimensions are verification, failure, observability, handoff, state, transition model, mathematics, dependencies, metrics, uncertainty, invariants, parent discipline, search coverage, and saturation.
- CI on reconciliation commit `e0a18fa5505fc27af79d1aed250cca122b9b018f` confirms **826 open → 0 open**, with one attributable answer per closed question and zero answer/audit residuals (GitHub Actions run `31911583880`).
- RAKL V3 implementation-overlay modules registered in `method_specs.py`: **21**.
  - **12** were already substantially subsumed/reconstructed by ORION and should not be copied wholesale.
  - **4** additional high-value overlays are reconstructed in this round: `experience_policy`, `saturation_vector`, `problem_novelty`, and `evolution_archive`.
  - **5** remain deliberately selective/open: `gluing_learning`, `experience_benchmark`, `driver_learning`, `summation_compatibility`, and `quantifier_compatibility`.
- Functional V3 overlay absorption/reconstruction after this round: **16 / 21**.

These counts describe coverage of registered structures, not proof that RAKL or ORION has discovered every necessary mechanic or that the transferred mechanics perform well on fresh live research.

## Canonical 24-surface transfer

| RAKL surface | ORION destinations | V1 transfer |
|---|---|---|
| decomposition | `FRAME.DECOMPOSE`, `REFRAME.DECOMPOSITION` | contract/profile |
| routing | `SEARCH.ROUTE`, `REFRAME.SEARCH_POLICY` | contract/profile |
| search_query_generation | `SEARCH.QUERY` | contract/profile |
| source_selection_reliability | `SEARCH.SOURCE`, `ABSORB.EVIDENCE_BIND` | contract/profile |
| claim_extraction | `ABSORB.SCIENTIFIC_LANGUAGE`, `ABSORB.CLAIM` | contract/profile; NLP performance remains open |
| ontology_terminology_normalization | `ABSORB.REFERENCE_IDENTITY`, `ABSORB.CONTEXT` | contract/profile |
| mathematical_context_translation | `ABSORB.REPRESENTATION_MAP` | contract/profile |
| equivalence_similarity | `ABSORB.REPRESENTATION_MAP`, `RECONSTRUCT.ATLAS_UPDATE` | contract/profile |
| contextual_theory_gluing | `RECONSTRUCT.GLUE` | contract/profile |
| contradiction_diagnosis | `DETECT.CONTRADICTION`, `DIAGNOSE.HYPOTHESES` | contract/profile |
| gap_discovery | `DETECT.GAP`, `DETECT.COVERAGE` | contract/profile |
| experiment_query_selection | `CROSS.EXPERIMENT_SELECTION`, `DIAGNOSE.DISCRIMINATOR` | contract/profile |
| synthesis | `RECONSTRUCT.PORTRAIT` | contract/profile |
| memory | `CROSS.MEMORY`, `DIAGNOSE.EXPERIENCE_RETRIEVAL` | contract/profile |
| review | `CROSS.REVIEW`, `DIAGNOSE.ATTRIBUTION` | contract/profile |
| benchmarking | `CROSS.BENCHMARK` | contract/profile |
| authority_promotion | `CROSS.AUTHORITY` | contract/profile; protected verifier remains external |
| saturation_stopping | `SATURATE.KNOWLEDGE_FLATNESS`, `SATURATE.ROUTE_COVERAGE`, `SATURATE.STOP` | contract/profile |
| prompting_context_policy | `CROSS.CONTEXT_POLICY` | contract/profile |
| capability_shaping | `REFRAME.METHOD`, `DIAGNOSE.ATTRIBUTION` | contract/profile |
| software_architecture_execution | `CROSS.EXECUTION` | contract/profile |
| research_portfolio_tree | `FRAME.DECOMPOSE`, `REOPEN.FIBRE` | contract/profile |
| objective_evolution | `FRAME.QUESTION`, `REFRAME.OBJECTIVE` | contract/profile |
| generator_transport | `CROSS.EXECUTION`, `REFRAME.METHOD` | contract/profile |

Thirteen ORION leaf/cross-cutting mechanics that do not have a one-to-one historical surface receive **adjacent many-to-many profiles**, for example `SEARCH.RETRIEVE` from source-reliability + execution, `SATURATE.OMISSION_CHALLENGE` from gap + stopping + routing, and `CROSS.EXPERIENCE` from memory + capability + authority.

## Evidence-bound answer transfer

The earlier direct-transfer prototype was falsified when concurrent Codex work strengthened `MechanicCell.v1` to keep fourteen generic dimensions provisional. V1 therefore routes all structural closure through ORION's answer-loop rather than directly removing provisional flags.

For every currently open mechanic/dimension pair, the transfer emits an `AnswerRecord` that contains either typed content or an explicit waiver, plus provenance. Content answers cite the frozen RAKL method contract/test paths or an explicit ORION composition derivation. The answer engine checks target mechanic, evidence presence, structured payload type, conflicts/supersession, and then removes only the corresponding provisional dimension. `audit_answer_application` verifies that the number of questions closed cannot exceed the number of answers applied.

The successful V1 result is therefore **826 evidence-bound applications for 826 closed questions**, not a bulk-clear operation.

## V3 overlay modules: already subsumed / reconstruct rather than copy (12)

1. `v3_authority.py` → ORION protected experience/authority/guards.
2. `experience_substrate.py` → ORION immutable `TaskEpisode.v1` and experience ledger.
3. `experience_learning.py` → ORION failure-pattern/replay/fresh-transfer promotion gates.
4. `experience_memory.py` → ORION experience-store/provider boundary.
5. `failure_learning.py` → ORION failure learning + development driver/fibres.
6. `problem_fibre.py` → ORION `DevelopmentFibre` reconstruction in this round.
7. `unified_substrate.py` → ORION K/W/M + provenance/experience layers.
8. `v3_runtime.py` → `OrionRuntime` and provider-neutral composition root.
9. `v3_scientific_authority.py` → ORION authority/non-escalation semantics.
10. `v3.py` → no parallel facade needed; ORION package is canonical.
11. `shadow_artifact_hash.py` → existing content/evidence/receipt hashes.
12. `pre_scratch_fibre_freeze.py` → frozen trial/packet identity is reconstructed in the Self-ORION live-trial harness.

## V3 overlays reconstructed in this round (4)

1. `experience_policy.py` → `orion.self_orion.experience_policy`: failure/success history changes scheduling priority only; it never creates method/scientific authority.
2. `saturation_vector.py` → `orion.self_orion.saturation_vector`: independent multi-axis development flatness; resource exhaustion cannot be called saturation.
3. `problem_novelty.py` → `orion.self_orion.novelty`: distinguishes stored/compositional/transfer reuse from representation/operator/ontology novelty.
4. `evolution_archive.py` → `orion.self_orion.evolution_archive`: append-only challenger/trial history; assured variants can only yield a host-promotion recommendation.

The RAKL `experience_policy` invention-readiness rule is additionally reconstructed as `orion.self_orion.invention_gate`, so repeated failure cannot directly trigger operator invention.

## V3 overlay modules deliberately still open/selective (5)

1. `gluing_learning.py` — defer until contextual gluing produces enough real success/obstruction episodes to learn a useful policy without premature specialization.
2. `experience_benchmark.py` — the generic matched-resource live-trial harness exists, but an experience-reuse-specific benchmark still requires frozen live episodes and a no-experience baseline.
3. `driver_learning.py` — deliberately **not activated** until the fixed auditable Self-ORION controller has enough frozen development episodes to beat under protected evaluation.
4. `summation_compatibility.py` — specialized aggregation falsifier; import when a live residual requires it.
5. `quantifier_compatibility.py` — specialized quantified-claim falsifier; import when a live residual requires it.

## Self-driving boundary added in this round

ORION now has a Shadow self-driving composition:

`RAKL/local absorption → evidence-bound answer application → empirical work ranking → DevelopmentFibre → ORION research → evidence gate → coding proposal provider → content-addressed patch artifact → isolated sandbox → protected fresh assurance → append-only evolution history → host-promotion recommendation`.

The coding worker may be an LLM/Codex/other provider. ORION owns the control loop. No component in this chain has a merge primitive or self-promotion authority. The implementation exposes a factory that composes the existing research runtime, proposal-only coding LLM, artifact store, host sandbox executor, and protected evaluator into `ShadowSelfDrivingController`.

## Transfer authority rule

A transferred RAKL contract is prior design knowledge, not ORION scientific authority. V1 transfer may remove a **specification question** only through an evidence-bound answer application. Every target mechanic retains fresh ORION conformance, ablation, live-performance, and protected-assurance coordinates.

Literal source code should be ported only when its contract is still correct under the current ORION state model and when a known-answer/hostile regression can be frozen before integration.
