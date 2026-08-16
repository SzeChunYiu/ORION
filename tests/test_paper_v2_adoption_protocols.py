from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.study.v2_adoption import V2ProtocolError, canonical_sha256, evaluate_incremental_decision, load_protocols, validate_protocol, verify_digest_registry

ROOT = Path(__file__).resolve().parents[1]
PROGRAMME = ROOT / "research" / "paper-programme-v2"
PROTOCOL_DIR = PROGRAMME / "protocols"


def _protocol(paper: str) -> dict:
    return json.loads((PROTOCOL_DIR / f"{paper}_V2.json").read_text(encoding="utf-8"))


def test_all_five_v2_protocols_are_design_frozen_and_incremental():
    protocols = load_protocols(PROTOCOL_DIR)
    assert [p["paper_id"] for p in protocols] == ["P1", "P2", "P3", "P4", "P5"]
    assert all(p["protocol_status"] == "DESIGN_FROZEN" for p in protocols)
    assert all(p["outcome_accessed"] is False for p in protocols)
    assert all(p["v1_protocol_mutated"] is False for p in protocols)
    assert all(p["local_evidence_authority"] == "LOCAL_ENGINEERING_ONLY" for p in protocols)


def test_digest_registry_binds_exact_designs():
    protocols = load_protocols(PROTOCOL_DIR)
    registry = json.loads((PROGRAMME / "PROTOCOL_DIGESTS_V1.json").read_text(encoding="utf-8"))
    verify_digest_registry(protocols, registry)


def test_adoption_decisions_match_protocols():
    decisions = json.loads((PROGRAMME / "ADOPTION_DECISIONS_V1.json").read_text(encoding="utf-8"))
    by_paper = {item["paper_id"]: item for item in decisions["decisions"]}
    assert set(by_paper) == {"P1", "P2", "P3", "P4", "P5"}
    assert by_paper["P1"]["decision"] == "ADOPT"
    assert by_paper["P2"]["decision"] == "ADAPT"
    assert by_paper["P3"]["decision"] == "ADOPT"
    assert by_paper["P4"]["decision"] == "ADAPT"
    assert by_paper["P5"]["decision"] == "ADOPT"
    for paper, decision in by_paper.items():
        protocol = _protocol(paper)
        assert protocol["adoption_decision"] == decision["decision"]
        assert protocol["mechanism_id"] == decision["mechanism_id"]
        assert protocol["protocol_id"] == decision["protocol_id"]


def test_transfer_manifest_mechanism_ids_match():
    for paper in ("P1", "P2", "P3", "P4", "P5"):
        protocol = _protocol(paper)
        manifest = json.loads((ROOT / "research" / "verified-structural-transfer-v2" / "manifests" / f"ORION-{paper}.json").read_text(encoding="utf-8"))
        assert protocol["mechanism_id"] == manifest["mechanism_id"]
        assert manifest["outcome_accessed"] is False
        assert manifest["execution_authority"] == "NONE"
        assert manifest["v1_protocol_mutated"] is False


def test_known_answer_fixture_exercises_pass_and_guard_failures():
    fixture = json.loads((PROGRAMME / "fixtures" / "INCREMENTAL_DECISION_KNOWN_ANSWER_V1.json").read_text(encoding="utf-8"))
    assert fixture["authority"] == "LOCAL_ENGINEERING_ONLY"
    assert len(fixture["cases"]) == 10
    statuses = {paper: set() for paper in ("P1", "P2", "P3", "P4", "P5")}
    for case in fixture["cases"]:
        result = evaluate_incremental_decision(_protocol(case["paper_id"]), case["v1"], case["v2"])
        assert result["status"] == case["expected"]
        statuses[case["paper_id"]].add(result["status"])
    assert all(value == {"PASS", "FAIL"} for value in statuses.values())


def test_missing_metric_is_cannot_check_not_failure_or_success():
    protocol = _protocol("P1")
    result = evaluate_incremental_decision(protocol, {"unnecessary_or_unauthorized_epistemic_mutation_rate": 0.12}, {"unnecessary_or_unauthorized_epistemic_mutation_rate": 0.08})
    assert result["status"] == "CANNOT_CHECK"
    assert "root_task_success" in result["reason"]


def test_p4_planner_cannot_gain_authority():
    assert _protocol("P4")["authority_cap"] == "PLANNER_CAN_NEVER_AUTHORIZE"


def test_p5_terminal_is_host_only():
    assert _protocol("P5")["promotion_terminal"] == "RECOMMEND_HOST_PROMOTION_ONLY"


def test_v1_mutation_is_rejected():
    mutated = copy.deepcopy(_protocol("P1"))
    mutated["v1_protocol_mutated"] = True
    with pytest.raises(V2ProtocolError):
        validate_protocol(mutated)


def test_outcome_access_before_execution_freeze_is_rejected():
    mutated = copy.deepcopy(_protocol("P3"))
    mutated["outcome_accessed"] = True
    with pytest.raises(V2ProtocolError):
        validate_protocol(mutated)


def test_design_freeze_cannot_pretend_execution_is_bound():
    mutated = copy.deepcopy(_protocol("P2"))
    mutated["execution_bindings"] = {"subject_revision":"abc","dataset_revisions":["data"],"model_provider_revisions":["model"],"baseline_config_hashes":["baseline"],"evaluator_hash":"eval","split_hashes":["split"],"evaluation_epoch":"epoch"}
    with pytest.raises(V2ProtocolError):
        validate_protocol(mutated)


def test_digest_changes_when_design_changes():
    protocol = _protocol("P5")
    mutated = copy.deepcopy(protocol)
    mutated["ablations"] = list(mutated["ablations"]) + ["new_posthoc_ablation"]
    assert canonical_sha256(mutated) != canonical_sha256(protocol)


def test_protocol_schema_is_parseable_and_names_incremental_contract():
    schema = json.loads((PROGRAMME / "V2_INCREMENTAL_PROTOCOL_SCHEMA_V1.json").read_text(encoding="utf-8"))
    assert schema["$id"] == "orion.paper-v2-incremental-protocol.v1"
    assert "incremental_decision" in schema["required"]
    assert schema["properties"]["protocol_status"]["const"] == "DESIGN_FROZEN"
    assert schema["properties"]["outcome_accessed"]["const"] is False
