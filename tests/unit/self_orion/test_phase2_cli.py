import hashlib
import json

import pytest

from orion.benchmarks.cli import main
from orion.self_orion.phase2_io import BINDING_SCHEMA


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def test_repository_phase2_preflight_stops_at_final_subject_binding(capsys):
    assert main(["phase2-preflight"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "BIND_FINAL_PHASE1_SUBJECT"
    assert payload["blockers"] == ["final_phase1_subject_revision_not_bound"]
    assert len(payload["frozen_task_ids"]) == 2
    assert len(payload["authority_attack_ids"]) == 10
    assert not payload["ready_to_execute_shadow_trial"]
    assert not payload["grants_phase2_closure"]
    assert not payload["grants_governed_self_orion"]


def test_fully_bound_phase2_preflight_emits_packet_fingerprint(tmp_path, capsys):
    binding = {
        "schema": BINDING_SCHEMA,
        "protocol_id": "phase2-shadow-closure-v1",
        "subject_revision_hash": _digest("final-phase1-main"),
        "provider_manifest_hash": _digest("provider-manifest"),
        "evaluator_artifact_hash": _digest("external-evaluator"),
        "evaluation_epoch_id": "phase2:epoch:001",
        "baseline_id": "simple-llm-retrieval-baseline-v1",
        "resource_budget_units": 100.0,
        # Attempts to inject tasks/attacks are ignored: those remain frozen in code.
        "tasks": [{"task_id": "posthoc-task"}],
        "authority_attack_ids": ["posthoc-attack"],
    }
    path = tmp_path / "phase2-binding.json"
    path.write_text(json.dumps(binding))

    assert main(["phase2-preflight", "--binding", str(path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "READY_TO_EXECUTE_SHADOW_TRIAL"
    assert payload["ready_to_execute_shadow_trial"]
    assert len(payload["live_trial_packet_fingerprint"]) == 64
    assert "posthoc-task" not in payload["frozen_task_ids"]
    assert "posthoc-attack" not in payload["authority_attack_ids"]
    assert not payload["grants_phase2_closure"]


def test_phase2_binding_rejects_string_resource_budget(tmp_path):
    binding = {
        "schema": BINDING_SCHEMA,
        "protocol_id": "phase2-shadow-closure-v1",
        "subject_revision_hash": _digest("subject"),
        "provider_manifest_hash": _digest("provider"),
        "evaluator_artifact_hash": _digest("evaluator"),
        "evaluation_epoch_id": "phase2:epoch:001",
        "baseline_id": "baseline-v1",
        "resource_budget_units": "100",
    }
    path = tmp_path / "phase2-binding.json"
    path.write_text(json.dumps(binding))
    with pytest.raises(ValueError, match="resource_budget_units must be a JSON number"):
        main(["phase2-preflight", "--binding", str(path)])


def test_phase2_binding_rejects_unknown_schema(tmp_path):
    binding = {
        "schema": "Phase2ClosureBinding.v0",
        "protocol_id": "phase2-shadow-closure-v1",
        "subject_revision_hash": _digest("subject"),
        "provider_manifest_hash": _digest("provider"),
        "evaluator_artifact_hash": _digest("evaluator"),
        "evaluation_epoch_id": "phase2:epoch:001",
        "baseline_id": "baseline-v1",
        "resource_budget_units": 100,
    }
    path = tmp_path / "phase2-binding.json"
    path.write_text(json.dumps(binding))
    with pytest.raises(ValueError, match="phase2 binding schema"):
        main(["phase2-preflight", "--binding", str(path)])
