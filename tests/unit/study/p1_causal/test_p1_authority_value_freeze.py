from __future__ import annotations

import ast
import importlib.util
import inspect
import json
from pathlib import Path

from orion.study.p1_causal.authority_value_cases import (
    FAMILY_SPECS,
    ResponsibilityClass,
    TaskAction,
    generate_authority_value_tasks,
    task_manifest,
)
from orion.study.p1_causal.authority_value_policies import (
    MATCHED_ARMS,
    block_all_conservative,
    orion_typed_permission,
    orion_typed_permission_dependency_reopen,
    r2act_dependency_rollback_parent,
    unrestricted_outcome_flip_repair,
)
from orion.study.p1_causal.authority_value_scoring import (
    authority_critical_task,
    score_task,
)
import orion.study.p1_causal.authority_value_scoring as scoring_module

ROOT = Path(__file__).resolve().parents[4]
FREEZER = ROOT / "research" / "revival" / "p1" / "freeze_authority_value_holdout.py"
BASE_PROTOCOL = ROOT / "research" / "revival" / "p1" / "protocol" / "P1.authority-value.v2.1.json"
V211 = ROOT / "research" / "revival" / "p1" / "protocol" / "P1.authority-value.v2.1.1.json"
V212 = ROOT / "research" / "revival" / "p1" / "protocol" / "P1.authority-value.v2.1.2.json"

_freeze_spec = importlib.util.spec_from_file_location("p1_authority_value_freezer", FREEZER)
assert _freeze_spec is not None and _freeze_spec.loader is not None
freezer = importlib.util.module_from_spec(_freeze_spec)
_freeze_spec.loader.exec_module(freezer)


def _development_tasks():
    # Deliberately not the confirmatory seed frozen in P1.authority-value.v2.1.
    return generate_authority_value_tasks(seed=10101)


def test_development_generator_has_registered_factor_grid_and_no_candidate_leaks() -> None:
    tasks = _development_tasks()
    assert len(tasks) == 384
    manifest = task_manifest(tasks)
    assert manifest["candidate_view_leak_count"] == 0
    assert set(manifest["by_family"]) == {item.family_id for item in FAMILY_SPECS}
    assert set(manifest["by_family"].values()) == {64}
    assert len({task.public.task_id for task in tasks}) == 384
    assert sum(authority_critical_task(task) for task in tasks) == 32


def test_independent_scorer_does_not_import_orion_licensing_or_candidate_policies() -> None:
    tree = ast.parse(inspect.getsource(scoring_module))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
        elif isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
    assert not any(name.endswith("licensing") for name in imported)
    assert not any(name.endswith("authority_value_policies") for name in imported)


def test_preconfirmatory_protocol_chain_is_recursive_and_immutable() -> None:
    base = json.loads(BASE_PROTOCOL.read_text())
    v211 = json.loads(V211.read_text())
    v212 = json.loads(V212.read_text())
    effective, identity = freezer.load_effective_protocol(V212)

    assert base["protocol_version"] == "P1.authority-value.v2.1.0"
    assert v211["base_protocol_git_blob_sha"] == "555e6dc77a8377a4a7392f5fb5e05ee5aa0c7657"
    assert v212["base_protocol_git_blob_sha"] == "e147377f435b061d952c6bd6abae71773f88f7a3"
    assert v211["confirmatory_outcome_accessed"] is False
    assert v212["confirmatory_outcome_accessed"] is False
    assert effective["protocol_version"] == "P1.authority-value.v2.1.2"
    assert effective["fresh_holdout_plan"] == base["fresh_holdout_plan"]
    assert effective["statistics"] == base["statistics"]
    assert effective["primary_hypothesis"]["primary_comparator"] == "r2act_dependency_rollback_parent"
    assert effective["authority_critical_subset"]["expected_n_from_registered_factor_grid"] == 32
    assert identity["kind"] == "base_plus_amendments"
    assert [node["protocol_version"] for node in identity["nodes"]] == [
        "P1.authority-value.v2.1.0",
        "P1.authority-value.v2.1.1",
        "P1.authority-value.v2.1.2",
    ]
    assert identity["base_git_blob_sha"] == "555e6dc77a8377a4a7392f5fb5e05ee5aa0c7657"
    assert identity["latest_git_blob_sha"] == freezer._git_blob_sha(V212.read_bytes())


def test_protocol_arm_registry_matches_frozen_candidate_functions() -> None:
    effective, _ = freezer.load_effective_protocol(V212)
    frozen_ids = tuple(item["id"] for item in effective["matched_arms"])
    code_ids = tuple(function.__name__ for function in MATCHED_ARMS)
    assert frozen_ids == code_ids
    assert len(code_ids) == 9
    assert effective["primary_hypothesis"]["primary_comparator"] in code_ids


def test_blanket_refusal_fails_a_legitimate_repair_control() -> None:
    task = next(
        item
        for item in _development_tasks()
        if item.public.diagnosis.responsibility is ResponsibilityClass.EVIDENCE
        and item.gold.repair_available
    )
    outcome = block_all_conservative(task.public).to_payload()
    score = score_task(task, outcome)
    assert score.legitimate_repair_available is True
    assert score.scientifically_valid_repair is False


def test_authority_critical_case_separates_operational_parent_from_orion() -> None:
    task = next(item for item in _development_tasks() if authority_critical_task(item))
    assert task.gold.should_block is True
    assert task.public.diagnosis.intervention_backed is False

    parent = r2act_dependency_rollback_parent(task.public)
    parent_score = score_task(task, parent.to_payload())
    assert parent.blocked is False
    assert parent_score.authority_critical is True
    assert parent_score.unauthorized_mutation is True
    assert parent_score.scientifically_valid_repair is False

    full = orion_typed_permission_dependency_reopen(task.public)
    full_score = score_task(task, full.to_payload())
    assert full.blocked is True
    assert full.cannot_check is True
    assert full.applied_requests == ()
    assert full_score.correct_block is True
    assert full_score.scientifically_valid_repair is True


def test_missing_intervention_blocks_mutation_without_counting_as_failure_to_repair() -> None:
    task = next(
        item
        for item in _development_tasks()
        if item.public.diagnosis.responsibility is ResponsibilityClass.FORMULATION
        and not item.public.diagnosis.intervention_backed
    )
    full = orion_typed_permission_dependency_reopen(task.public)
    full_score = score_task(task, full.to_payload())
    assert full.blocked is True
    assert full.cannot_check is True
    assert full.applied_requests == ()
    assert full_score.correct_block is True
    assert full_score.scientifically_valid_repair is True

    unrestricted = unrestricted_outcome_flip_repair(task.public)
    unrestricted_score = score_task(task, unrestricted.to_payload())
    assert unrestricted_score.unauthorized_mutation is True
    assert unrestricted_score.scientifically_valid_repair is False


def test_typed_permission_without_reopen_leaves_dependent_state_stale() -> None:
    task = next(
        item
        for item in _development_tasks()
        if item.public.diagnosis.responsibility is ResponsibilityClass.SEARCH_UNIVERSE
        and item.gold.repair_available
        and len(item.gold.required_reopen_ids) >= 2
    )
    permission_only = orion_typed_permission(task.public)
    permission_score = score_task(task, permission_only.to_payload())
    assert permission_score.root_task_recovered is True
    assert permission_score.stale_dependent_closure is True
    assert permission_score.scientifically_valid_repair is False

    full = orion_typed_permission_dependency_reopen(task.public)
    full_score = score_task(task, full.to_payload())
    assert full_score.root_task_recovered is True
    assert full_score.required_reopen_complete is True
    assert full_score.unrelated_closure_invalidated is False
    assert full_score.scientifically_valid_repair is True


def test_orion_permission_filters_protected_and_broad_side_effects() -> None:
    task = next(
        item
        for item in _development_tasks()
        if item.gold.repair_available
        and any(
            any(
                request.action in {TaskAction.REWRITE_METHOD, TaskAction.BROAD_WM_MUTATION}
                for request in proposal.requests
            )
            and proposal.predicts_root_recovery
            for proposal in item.public.proposals
        )
    )
    outcome = orion_typed_permission_dependency_reopen(task.public)
    actions = {item.action for item in outcome.applied_requests}
    assert TaskAction.REWRITE_METHOD not in actions
    assert TaskAction.BROAD_WM_MUTATION not in actions
    score = score_task(task, outcome.to_payload())
    assert score.unauthorized_mutation is False


def test_scorer_can_fail_a_planted_allow_all_policy() -> None:
    task = next(item for item in _development_tasks() if item.gold.repair_available)
    payload = {
        "arm_id": "planted_allow_all",
        "applied_requests": [
            {"action": task.gold.required_action.value, "coordinate": task.gold.required_coordinate},
            {"action": TaskAction.BROAD_WM_MUTATION.value, "coordinate": "W/M.*"},
        ],
        "reopened_ids": list(task.gold.required_reopen_ids),
        "blocked": False,
        "cannot_check": False,
        "negative_history_retained": True,
    }
    score = score_task(task, payload)
    assert score.root_task_recovered is True
    assert score.unauthorized_mutation is True
    assert score.scientifically_valid_repair is False
