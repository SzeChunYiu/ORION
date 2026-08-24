#!/usr/bin/env python3
"""Self-contained non-pytest validator for the P5 C2 V11 packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
IDENTITY = "C2_LAWFUL_NATIVE_BYTE_SUCCESSOR__ORION_V11"
CLASS_IDS = [
    "session",
    "source_mount",
    "pre_action_certificate",
    "public_evaluator",
    "write_reset_policy",
    "route_adapter",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(name: str) -> dict[str, Any]:
    value = json.loads((HERE / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{name} must contain a JSON object")
    return value


def check_ref(base: Path, ref: dict[str, Any]) -> None:
    path = base / ref["path"]
    assert path.is_file(), path
    assert path.stat().st_size == ref["size_bytes"], path
    assert sha256(path) == ref["sha256"], path


def main() -> int:
    freeze = load("P5_C2_V11_EXECUTION_FREEZE.json")
    gate = load("P5_C2_V11_SIX_CLASS_GATE_RECEIPT.json")
    result = load("P5_C2_V11_RESULT.json")
    ledger = load("P5_C2_V11_RECURSIVE_NEGATIVE_LEDGER.json")
    manifest = load("ARTIFACT_MANIFEST_V11.json")
    session = load("session/P5_C2_V11_SESSION_MANIFEST.json")
    boundary = load("P5_C2_V11_CERTIFICATE_AUTHORITY_BOUNDARY.json")
    runtime = load("P5_C2_V11_JDK_RUNTIME_LOCK.json")
    upstream = load("P5_C2_V11_UPSTREAM_SEARCH_RECEIPT.json")

    assert freeze["successor_identity"] == IDENTITY
    assert freeze["released_moss_identity_claimed"] is False
    assert freeze["released_moss_state_changed"] is False
    assert freeze["candidate_execution_authorized"] is False
    assert freeze["evaluator_execution_authorized"] is False
    assert [row["id"] for row in freeze["required_byte_classes"]] == CLASS_IDS
    for ref in freeze["packet_artifacts"].values():
        check_ref(HERE, ref)
    for ref in freeze["external_inputs"].values():
        check_ref(REPO_ROOT, ref)

    assert gate["status"] == "PASS"
    assert gate["successor_identity"] == IDENTITY
    assert gate["released_moss_identity_claimed"] is False
    assert gate["required_class_count"] == 6
    assert gate["passed_class_count"] == 6
    assert [row["class_id"] for row in gate["class_receipts"]] == CLASS_IDS
    assert all(row["passed"] for row in gate["class_receipts"])
    assert gate["candidate_tree_before_sha256"] == gate["candidate_tree_after_sha256"]
    assert gate["mutable_target_before_sha256"] == gate["mutable_target_after_sha256"]
    assert gate["attempt_destruction_verified"] is True
    assert gate["forbidden_recursive_key_hits"] == 0
    assert gate["forbidden_attempt_path_hits"] == 0
    assert gate["executed"] == {
        "benchmark": False,
        "coding_agent": False,
        "model": False,
        "moss": False,
        "protected_data": False,
        "protected_scorer": False,
        "public_evaluator": False,
        "repository_ci": False,
        "route_gate": True,
        "test_framework": False,
    }

    assert result["status"] == "BOUND_ONE_FIELD_FOR_DISTINCT_SUCCESSOR"
    assert result["field_instances_closed"] == 1
    assert result["successor_count_basis"]["predecessor_bound"] == 7
    assert result["successor_count_basis"]["predecessor_blocking"] == 14
    assert result["successor_count_basis"]["successor_bound"] == 8
    assert result["successor_count_basis"]["successor_blocking"] == 13
    assert result["released_moss_preserved"]["bound"] == 7
    assert result["released_moss_preserved"]["blocking"] == 14
    assert result["panel_and_claim_boundaries"]["ready_arms"] == "0/6"
    for key in ("H1", "H2", "H3", "H4", "performance", "superiority"):
        assert result["panel_and_claim_boundaries"][key] == "CANNOT_CHECK"
    assert result["manuscript_or_claim_ledger_edited"] is False

    assert ledger["resolved_in_v11"] == ["runtime.task_environment"]
    assert ledger["remaining_successor_blocker_count"] == 13
    remaining = [row for row in ledger["entries"] if "field" in row]
    assert len(remaining) == 13
    assert len({row["field"] for row in remaining}) == 13
    assert all(row["next_discriminator"] for row in ledger["entries"])

    assert session["complete_chunk_enumeration"] is True
    assert session["candidate_outcome_selected"] is False
    assert session["outcome_or_feedback_bytes_present"] is False
    assert session["case_selection_boundary"] == "INHERITED_POST_OUTCOME_PUBLIC_DEVELOPMENT_CASE__NOT_CONFIRMATORY"
    assert boundary["natural_case_fibre_proof"] == "NOT_SUPPLIED"
    assert boundary["revision_authority"] == "NOT_SUPPLIED"
    assert runtime["path_fallback_allowed"] is False
    assert runtime["network_required"] is False
    assert runtime["evaluator_executed_by_v11_route_gate"] is False
    assert upstream["observations"]["public_release_count"] == 0
    assert upstream["observations"]["maintainer_companion_found"] is False
    assert upstream["observations"]["exact_runner_code_search_count"] == 0
    for ref in upstream["raw_snapshots"]:
        check_ref(HERE, ref)

    manifest_paths = {row["path"] for row in manifest["artifacts"]}
    assert manifest["artifact_count"] == len(manifest["artifacts"])
    assert len(manifest_paths) == manifest["artifact_count"]
    for ref in manifest["artifacts"]:
        check_ref(HERE, ref)
    actual_manifest_paths = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file()
        and path.name not in {"ARTIFACT_MANIFEST_V11.json", "SHA256SUMS"}
        and "__pycache__" not in path.parts
    }
    assert manifest_paths == actual_manifest_paths

    declared_sums = {}
    for line in (HERE / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, path = line.split("  ", 1)
        declared_sums[path] = digest
    actual_sum_paths = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts
    }
    assert set(declared_sums) == actual_sum_paths
    for relative, digest in declared_sums.items():
        assert sha256(HERE / relative) == digest, relative

    adapter_text = (HERE / "p5_c2_v11_route_adapter.py").read_text(encoding="utf-8")
    assert "import subprocess" not in adapter_text
    assert "C2_LAWFUL_NATIVE_BYTE_SUCCESSOR__ORION_V11" in adapter_text
    print("P5_C2_V11_PACKET_VALID__SIX_OF_SIX_CLASSES_PASS__ONE_SUCCESSOR_FIELD_BOUND__RELEASED_MOSS_UNCHANGED__NO_OUTCOME_EXECUTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
