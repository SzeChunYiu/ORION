#!/usr/bin/env python3
"""Self-contained non-pytest validator for the P5 C2 V12 packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
IDENTITY = "C2_SOURCE_NATIVE_VISIBLE_CORE_SUCCESSOR__ORION_V12"
FIELDS = ["inputs.candidate_visible_case_bytes", "rights.task_and_benchmark_content"]
CORE_SHA = "09a2eb17394d7b84c11641b468d14446af955c4c3272557810d861a275c72da7"
TREE_SHA = "4fbe1517b1bf3c549986272fe16fead6a8e4eb6f3cfa47f09c3a92bf94162abc"


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
    freeze = load("P5_C2_V12_EXECUTION_FREEZE.json")
    basis = load("P5_C2_V12_EXPLICIT_ACCEPTANCE_BASIS.json")
    lineage = load("P5_C2_V12_SOURCE_RIGHTS_LINEAGE_MANIFEST.json")
    receipt = load("P5_C2_V12_SOURCE_LINEAGE_ROUTE_RECEIPT.json")
    result = load("P5_C2_V12_RESULT.json")
    ledger = load("P5_C2_V12_RECURSIVE_NEGATIVE_LEDGER.json")
    manifest = load("ARTIFACT_MANIFEST_V12.json")

    assert freeze["successor_identity"] == IDENTITY
    assert freeze["released_moss_identity_claimed"] is False
    assert freeze["aggregation_with_v11_authorized"] is False
    assert freeze["field_targets"] == FIELDS
    assert freeze["expected_candidate_visible_core_sha256"] == CORE_SHA
    assert freeze["expected_source_tree_manifest_sha256"] == TREE_SHA
    assert freeze["candidate_execution_authorized"] is False
    assert freeze["outcome_execution_authorized"] is False
    assert len(freeze["required_component_paths"]) == 6
    for ref in freeze["packet_artifacts"].values():
        check_ref(HERE, ref)
    for ref in freeze["external_inputs"].values():
        check_ref(REPO_ROOT, ref)

    assert basis["permitted_field_closures"] == FIELDS
    assert basis["count_basis"]["before"] == {"bound": 7, "blocking": 14}
    assert basis["count_basis"]["after_source_core_only"] == {"bound": 9, "blocking": 12}
    assert basis["forbidden_aggregation"]["runtime_task_environment_inherited"] is False
    assert basis["forbidden_aggregation"]["aggregation_with_v11_authorized"] is False
    assert basis["released_moss_preserved"]["bound"] == 7
    assert basis["released_moss_preserved"]["blocking"] == 14

    assert lineage["candidate_visible_component_count"] == 6
    assert lineage["candidate_visible_bytes"] == 703610
    assert lineage["candidate_visible_core_sha256"] == CORE_SHA
    assert lineage["source_lineage"]["canonical_tree_manifest_sha256"] == TREE_SHA
    assert lineage["source_lineage"]["regular_file_count"] == 302
    assert lineage["selection_and_outcome_boundary"]["selection_is_post_outcome"] is True
    assert lineage["selection_and_outcome_boundary"]["known_public_fix_bytes_in_candidate_core"] is False

    assert receipt["status"] == "PASS"
    assert receipt["successor_identity"] == IDENTITY
    assert receipt["required_component_count"] == 6
    assert receipt["mounted_component_count"] == 6
    assert receipt["candidate_visible_bytes"] == 703610
    assert receipt["candidate_visible_core_sha256"] == CORE_SHA
    assert receipt["source_tree_manifest_sha256"] == TREE_SHA
    assert receipt["source_tree_regular_files"] == 302
    assert receipt["all_mounted_bytes_read_only"] is True
    assert receipt["attempt_destruction_verified"] is True
    assert receipt["forbidden_recursive_key_hits"] == 0
    assert receipt["forbidden_attempt_path_hits"] == 0
    assert receipt["field_acceptance"] == {
        "inputs.candidate_visible_case_bytes": "PASS",
        "rights.task_and_benchmark_content": "PASS_FOR_LISTED_SHARED_CORE_ONLY",
    }
    assert receipt["identity_boundaries"] == {
        "aggregation_with_v11_authorized": False,
        "released_moss_identity_claimed": False,
        "v11_runtime_task_environment_inherited": False,
    }
    assert receipt["executed"] == {
        "benchmark": False,
        "coding_agent": False,
        "evaluator": False,
        "model": False,
        "moss": False,
        "protected_data": False,
        "repository_ci": False,
        "route_gate": True,
        "scorer": False,
        "test_framework": False,
    }

    assert result["successor_identity"] == IDENTITY
    assert result["status"] == "BOUND_TWO_SOURCE_NATIVE_FIELDS_FOR_DISTINCT_SUCCESSOR"
    assert result["field_instances_closed"] == 2
    assert result["closed_fields"] == FIELDS
    assert result["count_basis"]["after_v12_source_core_only"] == {"bound": 9, "blocking": 12}
    assert result["identity_frontier"]["released_moss"]["bound"] == 7
    assert result["identity_frontier"]["released_moss"]["blocking"] == 14
    assert result["identity_frontier"]["v11_distinct_runtime_successor"]["bound"] == 8
    assert result["identity_frontier"]["v11_distinct_runtime_successor"]["blocking"] == 13
    assert result["identity_frontier"]["v11_distinct_runtime_successor"]["inherited"] is False
    assert result["identity_frontier"]["aggregation_authorized"] is False
    assert result["v12_runtime_task_environment"] == "BLOCKING__V11_CLOSURE_NOT_INHERITED"
    assert result["panel_and_claim_boundaries"]["ready_arms"] == "0/6"
    for key in ("H1", "H2", "H3", "H4", "performance", "superiority"):
        assert result["panel_and_claim_boundaries"][key] == "CANNOT_CHECK"
    assert result["manuscript_or_claim_ledger_edited"] is False

    assert ledger["resolved_in_v12"] == FIELDS
    assert ledger["remaining_successor_blocker_count"] == 12
    remaining = [row for row in ledger["entries"] if "field" in row]
    assert len(remaining) == 12
    assert len({row["field"] for row in remaining}) == 12
    assert "runtime.task_environment" in {row["field"] for row in remaining}
    assert all(row["next_discriminator"] for row in ledger["entries"])

    manifest_paths = {row["path"] for row in manifest["artifacts"]}
    assert manifest["artifact_count"] == len(manifest["artifacts"])
    assert len(manifest_paths) == manifest["artifact_count"]
    for ref in manifest["artifacts"]:
        check_ref(HERE, ref)
    actual_manifest_paths = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file()
        and path.name not in {"ARTIFACT_MANIFEST_V12.json", "SHA256SUMS"}
        and "__pycache__" not in path.parts
    }
    assert manifest_paths == actual_manifest_paths

    declared = {}
    for line in (HERE / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        declared[relative] = digest
    actual_sum_paths = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts
    }
    assert set(declared) == actual_sum_paths
    for relative, digest in declared.items():
        assert sha256(HERE / relative) == digest, relative

    adapter = (HERE / "p5_c2_v12_source_lineage_route.py").read_text(encoding="utf-8")
    assert "import subprocess" not in adapter
    assert IDENTITY in adapter
    print("P5_C2_V12_PACKET_VALID__SIX_OF_SIX_SOURCE_COMPONENTS_PASS__TWO_FIELDS_BOUND__V11_NOT_AGGREGATED__RELEASED_MOSS_UNCHANGED__NO_OUTCOME_EXECUTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
