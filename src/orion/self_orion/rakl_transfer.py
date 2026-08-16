from __future__ import annotations

from dataclasses import dataclass, replace

from orion.mechanics.decomposition import RAKL_SURFACE_TO_CHILDREN
from orion.mechanics.model import HandoffField, MechanicCell, MechanicDimension

RAKL_SOURCE_COMMIT = "70f5f7c4a6771ffd1158765b42ac9f8aee8a270f"
RAKL_METHOD_SPEC_PATH = "src/rakl/method_specs.py"

STEP_SPECIFIC_DIMENSIONS = (
    MechanicDimension.VERIFICATION,
    MechanicDimension.FAILURE,
    MechanicDimension.OBSERVABILITY,
    MechanicDimension.HANDOFF,
    MechanicDimension.STATE,
    MechanicDimension.TRANSITION_MODEL,
    MechanicDimension.MATHEMATICS,
    MechanicDimension.DEPENDENCIES,
)


@dataclass(frozen=True)
class RaklSurfaceProfile:
    surface: str
    observables: tuple[str, ...]
    state: tuple[str, ...]
    transition: tuple[str, ...]
    mathematics: tuple[str, ...]
    failures: tuple[str, ...]
    verification_refs: tuple[str, ...]
    external_dependencies: tuple[str, ...]


@dataclass(frozen=True)
class RaklTransferReceipt:
    mechanic_id: str
    source_surfaces: tuple[str, ...]
    source_commit: str
    source_paths: tuple[str, ...]
    dimensions_closed: tuple[str, ...]
    confidence: str
    boundary: str


# Compact, ORION-facing reconstruction of the mature RAKL method contracts.
# These are design/implementation provenance. They do not import RAKL authority.
RAKL_SURFACE_PROFILES: dict[str, RaklSurfaceProfile] = {
    "decomposition": RaklSurfaceProfile(
        "decomposition",
        ("open_residual_count", "child_fibre_count", "dependency_cycle_count", "root_obligation_coverage"),
        ("active_problem", "active_residual", "decomposition_graph", "budget"),
        ("problem_and_residual -> acyclic decision-relevant child fibres + lineage",),
        ("f=(o_f,q_f,gamma_f,r_f,parent(f))", "rho(r,K_t) subseteq F_{t+1}"),
        ("missing_required_child", "dependency_cycle", "false_atomization", "resource_bound"),
        ("tests/test_core.py", "tests/test_tree.py", "tests/test_missing_operator.py"),
        ("problem-contract", "residual-ledger", "resource-budget"),
    ),
    "routing": RaklSurfaceProfile(
        "routing",
        ("candidate_route_count", "admissible_route_count", "selected_route", "route_cost", "blocking_reason"),
        ("active_fibre", "residual_class", "operator_catalog", "availability_and_cost"),
        ("admissible operators + residual -> selected route or BLOCKED/CANNOT_CHECK",),
        ("a*=argmax U(a|K_t) over admissible actions subject to blocking invariants",),
        ("no_admissible_route", "wrong_route_family", "hidden_authority_escalation", "resource_bound"),
        ("tests/test_assimilation.py", "tests/test_search_controller.py", "tests/test_challenge_learning.py"),
        ("operator-registry", "availability-ledger", "cost-model"),
    ),
    "search_query_generation": RaklSurfaceProfile(
        "search_query_generation",
        ("query_candidate_count", "selected_query", "query_route_kind", "expected_gain_or_separation", "query_cost"),
        ("active_fibre", "active_residual", "source_universe", "query_budget"),
        ("residual + route + budget -> query candidates -> selected evidence-acquisition query",),
        ("q*=argmax expected decision-relevant gain(q)/Cost(q) when calibrated; otherwise set-valued obstruction elimination",),
        ("query_not_residual_relevant", "query_fixation", "unsupported_expected_gain", "budget_exhausted"),
        ("tests/test_search_controller.py", "tests/test_tree.py"),
        ("route-contract", "retrieval-provider", "query-budget"),
    ),
    "source_selection_reliability": RaklSurfaceProfile(
        "source_selection_reliability",
        ("candidate_source_count", "qualified_source_count", "source_identity", "lineage_overlap", "support_scope"),
        ("candidate_sources", "claim_or_qoi", "source_metadata", "lineage_graph"),
        ("candidate sources -> identity/lineage qualification -> scoped qualified set + warnings",),
        ("EffectiveEvidence != CitationCount", "shared lineage does not add independent evidence mass"),
        ("source_identity_collision", "lineage_dependence_missed", "support_scope_mismatch", "source_unavailable"),
        ("tests/test_retrieval_benchmark.py", "tests/test_claim_evidence.py", "tests/test_evidence_lineage.py"),
        ("source-registry", "lineage-graph", "claim-scope"),
    ),
    "claim_extraction": RaklSurfaceProfile(
        "claim_extraction",
        ("source_selector", "claim_atom_count", "unresolved_scope_count", "evidence_binding_count"),
        ("source_snapshot", "selector", "claim_context", "extraction_state"),
        ("exact source material + context -> atomic scoped claim candidates + exact evidence links",),
        ("claim authority <= evidence selector and source projection scope",),
        ("selector_not_exact", "scope_loss", "negation_or_modality_loss", "unsupported_claim_atom"),
        ("tests/test_claim_evidence.py",),
        ("source-snapshot", "scientific-language-analysis", "evidence-selector"),
    ),
    "ontology_terminology_normalization": RaklSurfaceProfile(
        "ontology_terminology_normalization",
        ("term_count", "identity_hypothesis_count", "alias_count", "obstruction_count", "unresolved_reference_count"),
        ("local_terms", "contexts", "identity_ledger", "equivalence_evidence"),
        ("local terms + contextual identity evidence -> normalized concepts/aliases or explicit obstruction",),
        ("Normalize(x_i,gamma_i)->z only under a typed identity/equivalence witness",),
        ("false_entity_merge", "false_alias", "context_coordinate_loss", "unresolved_identity_hidden"),
        ("tests/test_core.py", "tests/test_meta_registry.py", "tests/test_generator_transport.py"),
        ("identity-ledger", "context-model", "equivalence-witness"),
    ),
    "mathematical_context_translation": RaklSurfaceProfile(
        "mathematical_context_translation",
        ("source_chart", "target_chart", "transform_id", "assumption_count", "uncertainty_transform_status", "obstruction_count"),
        ("source_chart", "target_chart", "typed_transition", "measurement_model", "uncertainty_model"),
        ("source coordinates + licensed transition -> translated target view or obstruction certificate",),
        ("T_ij^{tau,sigma}:phi_i(U_i cap U_j)->phi_j(U_i cap U_j)", "mu_y=A mu_x+b; Sigma_y=A Sigma_x A^T when assumptions license it"),
        ("noncomposable_transform", "unit_or_scale_mismatch", "uncertainty_transform_invalid", "hidden_assumption"),
        ("tests/test_atlas_gluing.py", "tests/test_bridge_composition.py", "tests/test_measurement.py", "tests/test_metrology.py"),
        ("chart-registry", "measurement-model", "uncertainty-model"),
    ),
    "equivalence_similarity": RaklSurfaceProfile(
        "equivalence_similarity",
        ("relation_type", "probe_count", "preserved_structure", "nonpreserved_structure", "distinguishing_probe_count"),
        ("source_object", "target_object", "relation_witness", "probe_family", "scope"),
        ("source/target + witness/probes -> typed scoped relation report + non-preservation ledger",),
        ("W_{A->B}^{tau,q}=(phi,P+,P-,Gamma,Delta,E)", "equivalence is probe-family and scope indexed"),
        ("relation_overclaim", "probe_family_too_weak", "scope_transport_invalid", "nonpreservation_hidden"),
        ("tests/test_similarity.py", "tests/test_measurement.py", "tests/test_generator_transport.py"),
        ("relation-registry", "probe-family", "scope-context"),
    ),
    "contextual_theory_gluing": RaklSurfaceProfile(
        "contextual_theory_gluing",
        ("chart_count", "overlap_count", "compatible_overlap_count", "cycle_obstruction_count", "global_status"),
        ("atlas_charts", "overlap_transitions", "alignment_witnesses", "cycle_witnesses"),
        ("compatible local sections + licensed overlaps -> global section; otherwise plural atlas/obstruction",),
        ("Contradict_l=Overlap and Align_l and not Compatible_l", "global glue requires compatible overlaps and licensed cycle composition"),
        ("forced_gluing", "cycle_inconsistency", "missing_overlap_witness", "pluralism_erased"),
        ("tests/test_atlas_gluing.py",),
        ("atlas", "transition-registry", "compatibility-checker"),
    ),
    "contradiction_diagnosis": RaklSurfaceProfile(
        "contradiction_diagnosis",
        ("candidate_disagreement_count", "aligned_overlap_count", "contradiction_count", "context_difference_count", "undercut_count"),
        ("claims_or_charts", "contexts", "identity_alignment", "evidence", "transitions"),
        ("disagreement -> align identity/context -> classify contradiction/context difference/undercut/obstruction",),
        ("Contradict_l=Overlap and Align_l and not Compatible_l",),
        ("false_contradiction", "missed_contradiction", "identity_mismatch", "context_difference_misclassified"),
        ("tests/test_core.py", "tests/test_atlas_gluing.py", "tests/test_claim_evidence.py"),
        ("identity-alignment", "context-model", "compatibility-checker"),
    ),
    "gap_discovery": RaklSurfaceProfile(
        "gap_discovery",
        ("survivor_count", "open_residual_count", "candidate_cut_size", "missing_operator_candidate_count"),
        ("target_qoi", "survivors", "obstructions", "residual_history", "operator_basis"),
        ("target + survivors/obstructions -> minimal decision-changing unresolved coordinate set",),
        ("cut(K,target)=minimal unresolved coordinate set whose resolution can change target status",),
        ("false_gap", "missed_gap", "irrelevant_cut", "method_gap_confused_with_data_gap"),
        ("tests/test_metacognition.py", "tests/test_missing_operator.py", "tests/test_challenge_learning.py"),
        ("target-contract", "residual-ledger", "operator-basis"),
    ),
    "experiment_query_selection": RaklSurfaceProfile(
        "experiment_query_selection",
        ("candidate_action_count", "survivor_count", "separation_score", "expected_information_value", "selected_cost"),
        ("surviving_hypotheses", "target_qoi", "candidate_actions", "costs", "calibrated_or_set_model"),
        ("survivors + candidate observations -> discriminator maximizing licensed separation per cost",),
        ("u(a|K) combines target information, survivor separation and novelty gain per cost only when probability semantics are licensed",),
        ("nonseparating_probe", "fabricated_probability", "cost_overrun", "selection_proxy_failure"),
        ("tests/test_tree.py", "tests/test_formal_oracles.py", "tests/test_math_oracles.py"),
        ("hypothesis-set", "candidate-action-registry", "cost-model"),
    ),
    "synthesis": RaklSurfaceProfile(
        "synthesis",
        ("verified_chart_count", "obstruction_count", "identified_set_width", "qualified_conclusion_count", "open_residual_count"),
        ("verified_charts", "survivors", "obstructions", "identified_sets", "authority_certificates"),
        ("verified local knowledge -> scoped global formalism/plural atlas/identified set + residual ledger",),
        ("Synthesize(K,Q) returns global formalism, plural atlas, or identified/bounded set",),
        ("unsupported_synthesis", "uncertainty_erasure", "plural_view_erasure", "residual_omission"),
        ("tests/test_mechanism_compiler.py", "tests/test_atlas_gluing.py", "tests/test_bridge_composition.py"),
        ("verified-knowledge", "atlas", "authority-certificates"),
    ),
    "memory": RaklSurfaceProfile(
        "memory",
        ("canonical_record_count", "retrieved_item_count", "mandatory_context_coverage", "token_cost", "negative_history_hits"),
        ("canonical_records", "source_pins", "operation_request", "working_context_budget"),
        ("canonical archive + operation request -> reconstructable bounded working view with lineage",),
        ("storage_growth does_not_imply prompt_growth", "C*=argmax U(C|o) subject to mandatory context and token budget"),
        ("mandatory_context_dropped", "negative_history_lost", "stale_view", "unreconstructable_summary"),
        ("tests/test_memory.py", "tests/test_multires_memory.py", "tests/test_context_compiler.py"),
        ("canonical-store", "context-compiler", "source-pins"),
    ),
    "review": RaklSurfaceProfile(
        "review",
        ("review_finding_count", "blocking_finding_count", "process_independence", "lineage_independence", "cannot_check_count"),
        ("candidate", "falsifiers", "reviewer_context", "evidence_lineage"),
        ("frozen candidate + independent review context -> findings + independence qualification",),
        ("IndependentCredit=ProcessIndependent and LineageIndependent",),
        ("self_review_counted_independent", "shared_lineage_counted_independent", "blocking_issue_missed", "review_scope_drift"),
        ("tests/test_hard_gates.py", "tests/test_parent_evaluator.py", "tests/test_promotion_attestation.py"),
        ("frozen-candidate", "reviewer-context", "lineage-graph"),
    ),
    "benchmarking": RaklSurfaceProfile(
        "benchmarking",
        ("subject_hash", "evaluator_hash", "split_id", "resource_match", "metric_vector", "blocking_verdict"),
        ("frozen_benchmark", "subject", "candidate_output", "evaluator", "chronology"),
        ("frozen subject/evaluator/thresholds + candidate -> metric vector + blocking verdict + receipt",),
        ("evaluation target/evaluator/thresholds freeze before candidate execution",),
        ("benchmark_leakage", "evaluator_drift", "resource_mismatch", "construct_invalid_score"),
        ("tests/test_evaluator.py", "tests/test_retrieval_benchmark.py", "tests/test_invention_benchmark.py", "tests/test_publication_gate.py"),
        ("benchmark-packet", "protected-evaluator", "resource-ledger"),
    ),
    "authority_promotion": RaklSurfaceProfile(
        "authority_promotion",
        ("candidate_hash", "certificate_count", "blocking_gate_count", "authority_delta", "evaluator_identity"),
        ("candidate", "evidence_certificates", "required_checks", "subject_identity", "evaluator_identity"),
        ("candidate + protected certificates -> scoped coordinate-wise authority update or block",),
        ("authority coordinates update only under compatible scope; protected class-B promotion requires all blockers and registered meta-QoI improvement",),
        ("self_promotion", "cross_axis_escalation", "subject_binding_mismatch", "evaluator_binding_mismatch"),
        ("tests/test_promotion.py", "tests/test_promotion_attestation.py", "tests/test_subject_identity.py", "tests/test_evidence_lineage.py"),
        ("protected-verifier", "certificate-store", "subject-registry"),
    ),
    "saturation_stopping": RaklSurfaceProfile(
        "saturation_stopping",
        ("semantic_growth", "route_coverage", "lineage_diversity", "open_residual_count", "flat_rounds", "closure_status"),
        ("canonical_semantic_sets", "route_coverage", "review_independence", "residuals", "frozen_basis"),
        ("growth/coverage/residual history -> continue, bounded-flat, reopen, or CANNOT_CHECK",),
        ("Delta_t^f=C_t^f\\C_{t-1}^f", "flat also requires no new contradiction/discriminator/data requirement/residual"),
        ("false_saturation", "resource_exhaustion_as_closure", "lineage_double_count", "material_residual_ignored"),
        ("tests/test_saturation.py", "tests/test_identity_saturation.py", "tests/test_meta_registry.py"),
        ("frozen-saturation-basis", "route-ledger", "residual-ledger"),
    ),
    "prompting_context_policy": RaklSurfaceProfile(
        "prompting_context_policy",
        ("mandatory_atom_count", "selected_atom_count", "token_count", "budget", "erasure_count"),
        ("operation", "candidate_context_items", "mandatory_atoms", "token_budget"),
        ("candidate context + mandatory set + budget -> smallest sufficient working manifest or CANNOT_COMPILE",),
        ("C*=argmax U(C|o) subject to M(o) subseteq C and Tokens(C)<=B",),
        ("silent_truncation", "mandatory_atom_missing", "tokenizer_miscalibration", "irrelevant_context_bloat"),
        ("tests/test_context_compiler.py", "tests/test_token_budget.py"),
        ("canonical-memory", "tokenizer", "operation-contract"),
    ),
    "capability_shaping": RaklSurfaceProfile(
        "capability_shaping",
        ("baseline_score", "challenger_score", "matched_resource_delta", "failure_pattern_count", "attribution_status"),
        ("capability_trial", "operator_candidate", "matched_baseline", "failure_patterns"),
        ("matched capability trial -> attribution + candidate operator verdict/learning action",),
        ("gain decomposes into model-utilization, external-resource, specialist-complementation and whole-system coordinates",),
        ("unmatched_baseline", "compensator_confused_with_truth", "attribution_ambiguity", "meta_overfit"),
        ("tests/test_capability.py", "tests/test_challenge_learning.py", "tests/test_metacognition.py", "tests/test_missing_operator.py"),
        ("matched-baseline", "capability-evaluator", "failure-history"),
    ),
    "software_architecture_execution": RaklSurfaceProfile(
        "software_architecture_execution",
        ("invocation_id", "event_count", "receipt_hash", "side_effect_state", "replay_status", "resource_usage"),
        ("task_packet", "runner_contract", "generation_config", "environment", "project_store", "event_chain"),
        ("canonical execution spec -> content-addressed invocation -> immutable event chain -> receipt/recovery outcome",),
        ("invocation_id=SHA256(canonical(spec))", "event_n binds SHA256(event_{n-1})"),
        ("identity_drift", "unsafe_retry", "ambiguous_side_effect", "receipt_chain_break", "environment_drift"),
        ("tests/test_project_runtime.py", "tests/test_execution.py", "tests/test_release_manifest.py", "tests/test_reference_profile.py", "tests/test_artifact_attestation.py"),
        ("runtime", "project-store", "environment-manifest", "side-effect-guard"),
    ),
    "research_portfolio_tree": RaklSurfaceProfile(
        "research_portfolio_tree",
        ("open_fibre_count", "allocation_by_branch", "expected_separation", "cost_by_branch", "revisit_trigger_count"),
        ("open_fibres", "decision_value", "separation_value", "costs", "portfolio_constraints"),
        ("open fibres + constraints -> non-greedy exploit/diversify/moonshot/meta agenda",),
        ("Portfolio={exploit,diversify,moonshot,meta} under validity and budget constraints",),
        ("single_branch_fixation", "budget_starvation", "root_irrelevant_branch", "revisit_trigger_missing"),
        ("tests/test_tree.py", "tests/test_search_controller.py"),
        ("fibre-registry", "resource-budget", "root-objective"),
    ),
    "objective_evolution": RaklSurfaceProfile(
        "objective_evolution",
        ("current_objective_id", "proposal_count", "protected_invariant_status", "meta_qoi_delta", "promotion_status"),
        ("current_objective", "feedback", "meta_qois", "protected_criteria", "negative_history"),
        ("feedback + protected criteria -> proposal-only objective update/block under meta-QoI evidence",),
        ("objective update admissible only if protected invariants stay fixed and target/meta-QoI evidence supports it",),
        ("goodhart_proxy_shift", "protected_criterion_changed", "objective_self_approval", "negative_history_erased"),
        ("tests/test_evolution.py", "tests/test_meta.py", "tests/test_challenge_learning.py"),
        ("protected-objective-registry", "meta-evaluator", "negative-history"),
    ),
    "generator_transport": RaklSurfaceProfile(
        "generator_transport",
        ("source_generator", "target_generator", "lift_id", "relation_strength", "target_trial_status", "weakest_certificate"),
        ("source_generator", "target_generator", "lift", "relation_witness", "scope", "target_trial"),
        ("source structural generator + explicit lift/witness -> target transport proposal -> target validation/refutation",),
        ("transport authority <= weakest licensed lift/relation/measurement/target certificate", "multi-hop requires composable handoffs and regime intersection"),
        ("invalid_lift", "scope_intersection_empty", "target_trial_failure", "relation_overclaim"),
        ("tests/test_generator_transport.py", "tests/test_similarity.py", "tests/test_bridge_composition.py"),
        ("generator-registry", "relation-witness", "target-validation"),
    ),
}


# ORION mechanics that were not in the original 24-surface map still have mature
# RAKL parents/adjacent mechanics. The mapping is deliberately many-to-many.
SPECIAL_SURFACE_MAP: dict[str, tuple[str, ...]] = {
    "FRAME.CONTEXT.v0": ("ontology_terminology_normalization", "mathematical_context_translation"),
    "FRAME.AUTHORITY_TARGET.v0": ("authority_promotion", "benchmarking"),
    "FRAME.RESOURCES.v0": ("software_architecture_execution", "prompting_context_policy", "research_portfolio_tree"),
    "SEARCH.RETRIEVE.v0": ("source_selection_reliability", "software_architecture_execution"),
    "SEARCH.ROUTE_STOP.v0": ("routing", "saturation_stopping"),
    "RECONSTRUCT.SEARCH_UNIVERSE.v0": ("gap_discovery", "routing", "saturation_stopping"),
    "DETECT.FAILURE.v0": ("contradiction_diagnosis", "capability_shaping"),
    "REFRAME.REPRESENTATION.v0": ("ontology_terminology_normalization", "capability_shaping"),
    "REOPEN.DEPENDENCY.v0": ("decomposition", "software_architecture_execution"),
    "REOPEN.CLOSURE.v0": ("saturation_stopping", "decomposition"),
    "SATURATE.FORMULATION_FLATNESS.v0": ("gap_discovery", "saturation_stopping", "objective_evolution"),
    "SATURATE.OMISSION_CHALLENGE.v0": ("gap_discovery", "saturation_stopping", "routing"),
    "CROSS.EXPERIENCE.v0": ("memory", "capability_shaping", "authority_promotion"),
}


def _reverse_surface_map() -> dict[str, tuple[str, ...]]:
    rows: dict[str, list[str]] = {}
    for surface, mechanic_ids in RAKL_SURFACE_TO_CHILDREN.items():
        for mechanic_id in mechanic_ids:
            rows.setdefault(mechanic_id, []).append(surface)
    for mechanic_id, surfaces in SPECIAL_SURFACE_MAP.items():
        rows.setdefault(mechanic_id, []).extend(surfaces)
    return {key: tuple(dict.fromkeys(values)) for key, values in rows.items()}


MECHANIC_TO_RAKL_SURFACES = _reverse_surface_map()


def _slug(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace(":", "_")


def _surface_handoff_fields(mechanic_id: str, surfaces: tuple[str, ...]) -> tuple[HandoffField, ...]:
    fields: list[HandoffField] = []
    for surface in surfaces:
        profile = RAKL_SURFACE_PROFILES[surface]
        for observable in profile.observables[:3]:
            fields.append(
                HandoffField(
                    field_id=f"{mechanic_id}:{surface}:{_slug(observable)}",
                    description=f"Step-specific {surface} output/observable: {observable}.",
                    schema_ref=f"orion://mechanic/{mechanic_id}/handoff/{_slug(observable)}",
                    required=True,
                )
            )
    fields.extend(
        (
            HandoffField(f"{mechanic_id}:evidence_bindings", "Exact evidence/content bindings used by this mechanic.", "orion://schema/evidence-bindings", True),
            HandoffField(f"{mechanic_id}:uncertainty", "Typed uncertainty/identified-set/cannot-check state for downstream consumers.", "orion://schema/uncertainty", True),
            HandoffField(f"{mechanic_id}:provenance", "Transformation, execution and source provenance for this mechanic result.", "orion://schema/provenance", True),
        )
    )
    seen: set[str] = set()
    return tuple(item for item in fields if not (item.field_id in seen or seen.add(item.field_id)))


def _apply_leaf_transfer(cell: MechanicCell, surfaces: tuple[str, ...]) -> MechanicCell:
    profiles = tuple(RAKL_SURFACE_PROFILES[surface] for surface in surfaces)
    source_paths = tuple(
        dict.fromkeys(
            path
            for profile in profiles
            for path in profile.verification_refs
        )
    )
    provenance_contracts = tuple(
        dict.fromkeys(
            cell.provenance_contracts
            + tuple(
                f"design-transfer:RAKL@{RAKL_SOURCE_COMMIT}:{RAKL_METHOD_SPEC_PATH}:{surface}"
                for surface in surfaces
            )
        )
    )
    verification = tuple(
        dict.fromkeys(
            tuple(f"rakl-transfer:{surface}:conformance:{path}" for surface in surfaces for path in RAKL_SURFACE_PROFILES[surface].verification_refs)
            + (f"orion:{cell.mechanic_id}:known-answer-conformance", f"orion:{cell.mechanic_id}:hostile-failure-path", f"orion:{cell.mechanic_id}:fresh-transfer-before-performance-promotion")
        )
    )
    failures = tuple(
        dict.fromkeys(
            tuple(f"{cell.mechanic_id}:{failure}" for profile in profiles for failure in profile.failures)
            + (f"{cell.mechanic_id}:scope_or_subject_binding_mismatch",)
        )
    )
    falsifiers = tuple(
        dict.fromkeys(
            tuple(f"{cell.mechanic_id}:fails:{path}" for path in source_paths)
            + (f"{cell.mechanic_id}:known_answer_output_wrong", f"{cell.mechanic_id}:declared_scope_not_preserved")
        )
    )
    observables = tuple(dict.fromkeys(item for profile in profiles for item in profile.observables))
    state = tuple(dict.fromkeys(item for profile in profiles for item in profile.state))
    transition = tuple(
        dict.fromkeys(
            (f"mechanic={cell.mechanic_id}; purpose={cell.purpose}",)
            + tuple(item for profile in profiles for item in profile.transition)
        )
    )
    mathematics = tuple(dict.fromkeys(item for profile in profiles for item in profile.mathematics))
    external_dependencies = tuple(
        dict.fromkeys(
            ("external:ORION_RUNTIME",)
            + tuple(f"contract:{cell.mechanic_id}:{_slug(item)}" for profile in profiles for item in profile.external_dependencies)
        )
    )
    provisional = tuple(item for item in cell.provisional_dimensions if item not in STEP_SPECIFIC_DIMENSIONS)
    empirical = tuple(
        dict.fromkeys(
            cell.empirical_open_coordinates
            + (
                f"fresh ORION conformance of the transferred RAKL contract for {cell.mechanic_id}",
                "transfer-ablation against the untransferred Shadow baseline",
            )
        )
    )
    return replace(
        cell,
        handoff_fields=_surface_handoff_fields(cell.mechanic_id, surfaces),
        state_ids=state,
        observable_ids=observables,
        transition_semantics=transition,
        mathematical_semantics=mathematics,
        failure_signatures=failures,
        falsifiers=falsifiers,
        verification_contracts=verification,
        external_dependency_contract_ids=external_dependencies,
        provenance_contracts=provenance_contracts,
        provisional_dimensions=provisional,
        empirical_open_coordinates=empirical,
    )


def _apply_composition_transfer(cell: MechanicCell) -> MechanicCell:
    child_ids = cell.child_mechanic_ids
    handoff = (
        HandoffField(f"{cell.mechanic_id}:operator_receipt", "Typed operator/root receipt including status and exact state delta.", f"orion://mechanic/{cell.mechanic_id}/receipt", True),
        HandoffField(f"{cell.mechanic_id}:residuals", "Material residuals and reopen obligations emitted by the composed mechanic.", "orion://schema/residual-set", True),
        HandoffField(f"{cell.mechanic_id}:evidence_bindings", "Content-bound evidence identities used by child mechanics.", "orion://schema/evidence-bindings", True),
        HandoffField(f"{cell.mechanic_id}:provenance", "Ordered child receipt and state-transition lineage.", "orion://schema/provenance", True),
    )
    state = ("K_t", "W_t", "M_t", "epoch", f"active:{cell.mechanic_id}", "child_receipt_ledger")
    observables = ("child_status_vector", "state_epoch", "material_residual_count", "authority_delta", "resource_spend", "cannot_check_count")
    transition = (
        f"{cell.mechanic_id} composes the declared child transitions under dependency order and blocking invariants.",
        "A child BLOCKED/CANNOT_CHECK/failure is preserved in the parent receipt; success cannot be synthesized by dropping failed children.",
        "Material child residuals update K/W/M only through declared state transitions and trigger scoped reopening.",
    )
    mathematics = (
        "T_parent is relational composition of child transition relations over the declared dependency partial order.",
        "When child relations are set-valued/partially identified, parent composition remains set-valued; no uniqueness or probability is invented.",
    )
    verification = (
        f"orion:{cell.mechanic_id}:all-registered-child-contracts-explicit",
        f"orion:{cell.mechanic_id}:dependency-order-and-handoff-conformance",
        f"orion:{cell.mechanic_id}:known-answer-end-to-end-trace",
        f"orion:{cell.mechanic_id}:hostile-child-failure-propagation",
    )
    failures = (
        f"{cell.mechanic_id}:child_failure_suppressed",
        f"{cell.mechanic_id}:handoff_contract_violation",
        f"{cell.mechanic_id}:invalid_transition_order",
        f"{cell.mechanic_id}:state_or_authority_escalation",
        f"{cell.mechanic_id}:resource_bound",
    )
    falsifiers = (
        f"{cell.mechanic_id}:parent_success_with_blocking_child_failure",
        f"{cell.mechanic_id}:replay_trace_differs_under_bound_deterministic_inputs",
        f"{cell.mechanic_id}:downstream_state_missing_declared_child_delta",
    )
    dependencies = tuple(
        dict.fromkeys(
            cell.external_dependency_contract_ids
            + ("external:ORION_RUNTIME", "contract:protected-authority-boundary", "contract:experience-ledger")
        )
    )
    provisional = tuple(item for item in cell.provisional_dimensions if item not in STEP_SPECIFIC_DIMENSIONS)
    return replace(
        cell,
        handoff_fields=handoff,
        state_ids=state,
        observable_ids=observables,
        transition_semantics=transition,
        mathematical_semantics=mathematics,
        failure_signatures=failures,
        falsifiers=falsifiers,
        verification_contracts=verification,
        external_dependency_contract_ids=dependencies,
        provenance_contracts=tuple(dict.fromkeys(cell.provenance_contracts + (f"composition-contract:{cell.mechanic_id}:children={','.join(child_ids)}",))),
        provisional_dimensions=provisional,
        empirical_open_coordinates=tuple(dict.fromkeys(cell.empirical_open_coordinates + (f"fresh end-to-end performance/transfer of composed mechanic {cell.mechanic_id}",))),
    )


def apply_rakl_transfer_profiles(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    """Answer the eight Shadow provisional dimensions from scoped RAKL/ORION knowledge.

    Leaf/cross-cutting mechanics receive explicit source-surface profiles. Top-level
    operators/root receive an explicit composition contract. The operation closes
    specification questions only; empirical-open coordinates remain and no scientific
    or method-promotion authority is created.
    """

    output: list[MechanicCell] = []
    for cell in cells:
        surfaces = MECHANIC_TO_RAKL_SURFACES.get(cell.mechanic_id)
        if surfaces:
            output.append(_apply_leaf_transfer(cell, surfaces))
        elif cell.child_mechanic_ids:
            output.append(_apply_composition_transfer(cell))
        else:
            output.append(cell)
    return tuple(output)


def rakl_transfer_receipts(cells: tuple[MechanicCell, ...]) -> tuple[RaklTransferReceipt, ...]:
    receipts: list[RaklTransferReceipt] = []
    for cell in cells:
        surfaces = MECHANIC_TO_RAKL_SURFACES.get(cell.mechanic_id)
        if surfaces:
            source_paths = tuple(
                dict.fromkeys(
                    (RAKL_METHOD_SPEC_PATH,)
                    + tuple(path for surface in surfaces for path in RAKL_SURFACE_PROFILES[surface].verification_refs)
                )
            )
            confidence = "DIRECT_OR_ADJACENT_RAKL_CONTRACT_TRANSFER"
        elif cell.child_mechanic_ids:
            surfaces = ()
            source_paths = ("ORION:child-mechanic-composition",)
            confidence = "ORION_COMPOSITION_DERIVATION"
        else:
            continue
        receipts.append(
            RaklTransferReceipt(
                mechanic_id=cell.mechanic_id,
                source_surfaces=surfaces,
                source_commit=RAKL_SOURCE_COMMIT,
                source_paths=source_paths,
                dimensions_closed=tuple(item.value for item in STEP_SPECIFIC_DIMENSIONS),
                confidence=confidence,
                boundary="specification transfer only; fresh ORION validation and all empirical-open coordinates remain required",
            )
        )
    return tuple(receipts)


def transfer_coverage(cells: tuple[MechanicCell, ...]) -> tuple[int, int, int]:
    receipts = rakl_transfer_receipts(cells)
    direct = sum(bool(item.source_surfaces) for item in receipts)
    composed = len(receipts) - direct
    return len(receipts), direct, composed
