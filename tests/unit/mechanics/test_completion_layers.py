from orion.mechanics.model import MechanicCell
from orion.mechanics.questioning import generate_mechanic_questions
from orion.mechanics.actions import apply_candidate_action_plan
from orion.mechanics.objectives import apply_candidate_objective
from orion.mechanics.optimization import apply_default_optimization_policy
from orion.mechanics.resources import ResourceKind, apply_default_resource_plan, default_resource_plan
from orion.mechanics.diagnosis import apply_default_diagnosis_plan, default_diagnosis_plan
from orion.mechanics.storage import StorageLayer, apply_default_storage_contract, default_storage_requirements
from orion.mechanics.provenance import ProvenanceKind, apply_default_provenance_contract, default_provenance_requirements
from orion.mechanics.engineering import EngineeringConcern, apply_default_engineering_contract, default_engineering_requirements


def _dims(cell):
    return {item.dimension.value for item in generate_mechanic_questions(cell)}


def test_control_completion_layers_close_only_their_structural_questions():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture", input_ids=("problem",), output_ids=("evidence",))
    cell = apply_candidate_action_plan(cell)
    assert "ACTIONS" not in _dims(cell)
    cell = apply_candidate_objective(cell)
    assert "OBJECTIVE" not in _dims(cell)
    cell = apply_default_optimization_policy(cell)
    assert "OPTIMIZATION" not in _dims(cell)
    cell = apply_default_resource_plan(cell)
    assert "RESOURCES" not in _dims(cell)
    cell = apply_default_diagnosis_plan(cell)
    assert "DIAGNOSIS" not in _dims(cell)
    cell = apply_default_storage_contract(cell)
    assert "STORAGE" not in _dims(cell)
    cell = apply_default_provenance_contract(cell)
    assert "PROVENANCE" not in _dims(cell)
    cell = apply_default_engineering_contract(cell)
    assert "ENGINEERING" not in _dims(cell)
    assert cell.empirical_open_coordinates


def test_resource_plan_includes_time_tokens_compute_tools_money_and_human_attention():
    plan = default_resource_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    kinds = {item.kind for item in plan.coordinates}
    assert {
        ResourceKind.WALL_TIME,
        ResourceKind.MODEL_TOKENS,
        ResourceKind.COMPUTE,
        ResourceKind.TOOL_CALLS,
        ResourceKind.MONETARY_COST,
        ResourceKind.HUMAN_ATTENTION,
    } <= kinds
    assert "CANNOT_CHECK_RESOURCE_BOUND" in plan.exhaustion_rule


def test_diagnosis_refuses_recurrence_as_cause():
    plan = default_diagnosis_plan(MechanicCell("DIAGNOSE.test", "Diagnose.", "fixture"))
    assert "do not by themselves prove causal responsibility" in plan.recurrence_rule
    assert "discriminator" in plan.discriminator_rule.lower()


def test_storage_layers_keep_negative_experience_and_separate_cache():
    requirements = default_storage_requirements(MechanicCell("CROSS.MEMORY.test", "Store.", "fixture"))
    by_layer = {item.layer: item for item in requirements}
    assert StorageLayer.EPISODE in by_layer
    assert "negative episodes" in by_layer[StorageLayer.EPISODE].eviction_semantics
    assert StorageLayer.INDEX_CACHE in by_layer
    assert "evict freely" in by_layer[StorageLayer.INDEX_CACHE].eviction_semantics


def test_provenance_separates_evidence_from_computation_and_governance():
    requirements = default_provenance_requirements(MechanicCell("ABSORB.test", "Absorb.", "fixture"))
    kinds = {item.kind for item in requirements}
    assert {ProvenanceKind.EVIDENTIAL, ProvenanceKind.COMPUTATIONAL, ProvenanceKind.GOVERNANCE, ProvenanceKind.EXPERIENCE} <= kinds
    computational = next(item for item in requirements if item.kind is ProvenanceKind.COMPUTATIONAL)
    assert "not scientific evidence" in computational.authority_semantics


def test_engineering_contract_covers_replay_side_effects_concurrency_recovery_and_fault_injection():
    requirements = default_engineering_requirements(MechanicCell("CROSS.EXECUTION.test", "Execute.", "fixture"))
    concerns = {item.concern for item in requirements}
    assert {
        EngineeringConcern.DETERMINISM_REPLAY,
        EngineeringConcern.IDEMPOTENCY_SIDE_EFFECTS,
        EngineeringConcern.CONCURRENCY,
        EngineeringConcern.RECOVERY_CHECKPOINT,
        EngineeringConcern.SCHEMA_VALIDATION,
        EngineeringConcern.SECURITY_PRIVILEGE,
        EngineeringConcern.TESTING_FAULT_INJECTION,
    } <= concerns
