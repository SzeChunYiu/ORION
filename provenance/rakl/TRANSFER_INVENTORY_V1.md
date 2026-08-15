# RAKL → ORION transfer inventory V1

Frozen RAKL source: `70f5f7c4a6771ffd1158765b42ac9f8aee8a270f`.

This inventory distinguishes **knowledge/mechanic transfer** from literal file copying. RAKL remains a provenance source; ORION owns the reconstructed contracts and implementations.

## Quantitative summary

- Canonical RAKL method surfaces: **24 / 24 represented in the ORION transfer catalog**.
- Current ORION mechanic graph: **59 reachable cells**.
- Leaf/cross-cutting mechanics receiving direct or adjacent RAKL surface profiles: **49 / 59**.
- Root/top-level mechanics receiving explicit ORION composition contracts: **10 / 59**.
- Shadow step-specific structural questions targeted by this transfer: **472 = 59 × 8**.
- RAKL V3 implementation-overlay modules registered in `method_specs.py`: **21**.
  - **12** are already substantially subsumed/reconstructed by ORION and should not be copied wholesale.
  - **9** remain high-value selective transfer candidates for later empirical rounds.

These counts describe coverage of registered structures, not proof that RAKL or ORION has discovered every necessary mechanic.

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

## V3 overlay modules: high-value selective transfer candidates (9)

1. `gluing_learning.py` — learn which gluing/obstruction patterns transfer.
2. `experience_policy.py` — experience-conditioned routing policy.
3. `experience_benchmark.py` — matched evaluation of learned experience reuse.
4. `saturation_vector.py` — richer multi-coordinate saturation telemetry.
5. `problem_novelty.py` — distinguish new structure from renamed old structure.
6. `evolution_archive.py` — challenger/incumbent evolution chronology and negative history.
7. `driver_learning.py` — learn development-control policies after frozen-baseline evidence exists.
8. `summation_compatibility.py` — specialized compatibility falsifier for aggregations.
9. `quantifier_compatibility.py` — specialized compatibility falsifier for quantified claims.

These are **not** automatically imported in V1. Self-ORION should select them when a current empirical/failure fibre shows root-relevant need.

## Transfer authority rule

A transferred RAKL contract is prior design knowledge, not ORION scientific authority. V1 transfer may remove a **specification question** only when the target ORION mechanic receives explicit scoped observables/state/handoff/transition/math/failure/verification/dependency semantics. It must simultaneously retain fresh ORION conformance, ablation and empirical-open coordinates.

Literal source code should be ported only when its contract is still correct under the current ORION state model and when a known-answer/hostile regression can be frozen before integration.
