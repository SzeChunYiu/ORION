from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "research" / "publication" / "result_lifecycle.py"


def _load():
    spec = importlib.util.spec_from_file_location("result_lifecycle_under_test", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _record(module, record_id: str, **changes):
    result = changes.pop("result", {"estimate": 0.0})
    row = {
        "schema_version": module.SCHEMA_VERSION,
        "paper_id": "P1",
        "claim_id": "P1.H1.V1",
        "claim_scope": "registered bounded V1 frame",
        "study_id": "V1",
        "record_id": record_id,
        "lifecycle_status": "HISTORICAL",
        "record_kind": "SCIENTIFIC_RESULT",
        "claim_authority": "PRIMARY",
        "disposition": "ADVERSE",
        "estimand_id": "paired-root-success",
        "population_id": "p1-v1-frame",
        "outcome_id": "protected-root-success",
        "decision_rule_id": "v1-h1-rule",
        "measurement_id": "P1.H1.V1.primary",
        "protocol_digest": "sha256:" + "1" * 64,
        "dataset_digest": "sha256:" + "2" * 64,
        "comparator_set_digest": "sha256:" + "3" * 64,
        "visibility_contract_digest": "sha256:" + "4" * 64,
        "cluster_id": "aggregate",
        "cluster_members": ["c1"],
        "edge_type": None,
        "parent_record_id": None,
        "is_projection": False,
        "design_validity": "VALID",
        "gate_role": "CLAIM_DECISION",
        "terminal": "NOT_SUPPORTED",
        "result": result,
        "result_digest": module.digest_result(result),
    }
    row.update(changes)
    if "result" in changes and "result_digest" not in changes:
        row["result_digest"] = module.digest_result(row["result"])
    return row


def test_successor_does_not_erase_historical_adverse_parent():
    module = _load()
    old = _record(module, "old")
    new = _record(
        module,
        "new",
        claim_id="P1.H1.R7",
        study_id="R7",
        lifecycle_status="ACTIVE",
        disposition="PENDING",
        estimand_id="wide-cluster-success",
        population_id="r7-wide-frame",
        decision_rule_id="r7-wide-rule",
        protocol_digest="sha256:" + "5" * 64,
        comparator_set_digest="sha256:" + "6" * 64,
        edge_type="SUCCESSOR_OF",
        parent_record_id="old",
        result={"status": "PENDING"},
    )
    view = module.publication_view([old, new])
    assert [row["record_id"] for row in view["active_leaves"]] == ["new"]
    assert [row["record_id"] for row in view["historical_adverse_ancestors"]] == ["old"]


def test_only_true_same_study_supersession_retires_an_active_parent():
    module = _load()
    parent = _record(module, "a", lifecycle_status="ACTIVE")
    child = _record(
        module,
        "b",
        lifecycle_status="ACTIVE",
        edge_type="SUPERSEDES",
        parent_record_id="a",
        result={"estimate": 0.1},
    )
    assert [row["record_id"] for row in module.active_leaves([parent, child])] == ["b"]

    invalid = dict(child, estimand_id="different-estimand")
    with pytest.raises(module.LifecycleError, match="SUPERSEDES"):
        module.validate_graph([parent, invalid])


def test_projection_and_directory_location_cannot_inflate_paper_counts():
    module = _load()
    canonical = _record(
        module,
        "p4-canonical",
        paper_id="P4",
        claim_id="P4.H3.V2",
        measurement_id="P4.H3.correct-cannot-check-rate",
        claim_authority="DIAGNOSTIC",
        record_kind="DIAGNOSTIC_RESULT",
        gate_role="DIAGNOSTIC",
    )
    projected = dict(
        canonical,
        record_id="copy-under-p3-directory",
        edge_type="PROJECTS",
        parent_record_id="p4-canonical",
        is_projection=True,
    )
    groups = module.diagnostic_measurements([canonical, projected])
    assert list(groups) == [("P4", "P4.H3.correct-cannot-check-rate")]
    assert groups[("P4", "P4.H3.correct-cannot-check-rate")] == ["p4-canonical"]


def test_duplicate_measurement_content_is_deduplicated_but_conflict_fails():
    module = _load()
    a = _record(module, "a", claim_authority="DIAGNOSTIC", record_kind="DIAGNOSTIC_RESULT", gate_role="DIAGNOSTIC")
    b = dict(a, record_id="b")
    groups = module.diagnostic_measurements([a, b])
    assert list(groups.values()) == [["a", "b"]]
    changed = dict(b, result={"estimate": 1.0})
    changed["result_digest"] = module.digest_result(changed["result"])
    with pytest.raises(module.LifecycleError, match="conflicting result content"):
        module.diagnostic_measurements([a, changed])


def test_digest_tampering_and_ambiguous_claims_fail_closed():
    module = _load()
    tampered = _record(module, "bad")
    tampered["result"]["estimate"] = 1.0
    with pytest.raises(module.LifecycleError, match="result_digest"):
        module.validate_record(tampered)

    bare = _record(module, "bare", claim_id="P1.H1")
    with pytest.raises(module.LifecycleError, match="claim_id"):
        module.validate_record(bare)


def test_expected_negative_controls_and_non_results_are_not_diagnostics():
    module = _load()
    control = _record(
        module,
        "control",
        claim_authority="NEGATIVE_CONTROL",
        gate_role="EXPECTED_NEGATIVE_CONTROL",
    )
    manifest = _record(
        module,
        "manifest",
        claim_authority="SCHEMA",
        record_kind="MANIFEST",
        gate_role="DIAGNOSTIC",
    )
    assert module.diagnostic_measurements([control, manifest]) == {}

