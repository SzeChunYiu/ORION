#!/usr/bin/env python3
"""Read-only, non-pytest validator for the P5 C2 V13 packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
IDENTITY = "C2_RIGHTS_CLEARED_SCRATCH_IMAGE_SUCCESSOR__ORION_V13"
FIELD = "rights.container_and_generated_artifacts"
EXPECTED_STDOUT = b"ORION V13 container pass\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(name: str) -> dict[str, Any]:
    value = json.loads((HERE / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{name} must contain one JSON object")
    return value


def check_ref(base: Path, item: dict[str, Any]) -> None:
    path = base / item["path"]
    assert path.is_file(), path
    assert path.stat().st_size == item["size_bytes"], path
    assert sha256(path) == item["sha256"], path


def main() -> int:
    protocol = load("P5_C2_V13_FROZEN_PROTOCOL.json")
    freeze = load("P5_C2_V13_EXECUTION_FREEZE.json")
    context = load("BUILD_CONTEXT_MANIFEST_V13.json")
    probe = load("PROBE_GENERATION_RECEIPT_V13.json")
    authority = load("P5_C2_V13_GENERATED_ARTIFACT_AUTHORITY.json")
    rights = load("P5_C2_V13_IMAGE_CONTENT_RIGHTS_MAP.json")
    licenses = load("LICENSE_BUNDLE_MANIFEST_V13.json")
    layer = load("ROOTFS_LAYER_MANIFEST_V13.json")
    sbom = load("IMAGE_SBOM_V13.spdx.json")
    descriptor = load("IMAGE_DESCRIPTOR_V13.json")
    runtime = load("RUNTIME_RECEIPT_V13.json")
    archive = load("IMAGE_ARCHIVE_RECEIPT_V13.json")
    disposal = load("DISPOSAL_RECEIPT_V13.json")
    gate = load("P5_C2_V13_RIGHTS_IMAGE_GATE_RECEIPT.json")
    result = load("P5_C2_V13_RESULT.json")
    ledger = load("P5_C2_V13_RECURSIVE_NEGATIVE_LEDGER.json")
    validation = load("VALIDATION_RECEIPT_V13.json")
    manifest = load("ARTIFACT_MANIFEST_V13.json")

    assert protocol["successor_identity"] == IDENTITY
    assert protocol["target_field"] == FIELD
    assert protocol["identity_boundary"] == {
        "aggregation_with_v11_or_v12_authorized": False,
        "count_basis_after_only_if_gate_passes": {"blocking": 13, "bound": 8},
        "count_basis_before": {"blocking": 14, "bound": 7},
        "distinct_from_released_moss": True,
        "distinct_from_v11": True,
        "distinct_from_v12": True,
    }
    assert protocol["build_contract"]["base_image"] == "scratch"
    assert protocol["build_contract"]["platform"] == "linux/arm64"
    assert protocol["build_contract"]["network"] == "none"
    assert protocol["runtime_contract"]["expected_stdout_hex"] == EXPECTED_STDOUT.hex()
    assert protocol["runtime_contract"]["expected_diff_entries"] == 0
    assert "pytest or repository CI" in protocol["executions_forbidden"]
    for item in protocol["frozen_code"].values():
        check_ref(HERE, item)
    for item in protocol["frozen_packet_inputs"].values():
        check_ref(HERE, item)
    for item in protocol["external_inputs"].values():
        check_ref(REPO, item)

    assert freeze["frozen_before_docker_server_start"] is True
    assert freeze["docker_server_pre_freeze_returncode"] != 0
    assert freeze["candidate_or_outcome_execution_authorized"] is False
    assert freeze["pytest_or_repository_ci_authorized"] is False
    check_ref(HERE, freeze["protocol"])
    check_ref(HERE, freeze["build_context_manifest"])

    for item in context["build_context_files"]:
        check_ref(HERE, item)
    frozen_root = context["rootfs_regular_files"]
    assert context["rootfs_regular_file_count"] == 9
    assert context["rootfs_symlink_count"] == 0
    assert context["base_image"] == "scratch"
    assert context["network_required_to_build"] is False
    check_ref(HERE, probe["generator"])
    check_ref(HERE, probe["binary"])
    assert probe["elf_machine"] == "AArch64"
    assert probe["dynamic_dependencies"] == []
    assert probe["expected_stdout_hex"] == EXPECTED_STDOUT.hex()

    assert authority["authority_status"] == "EXPLICIT_FOR_NEWLY_AUTHORED_V13_ARTIFACTS_ONLY"
    assert authority["retention_authorized"] is True
    assert authority["disclosure_authorized"] is True
    assert authority["publication_authorized"] is True
    assert authority["redistribution_authorized"] is True
    assert authority["generated_session_and_evolution_state_authorized"] is True
    assert authority["license_spdx"] == "CC0-1.0"
    assert authority["legal_advice"] is False

    rights_paths = {row["path"] for row in rights["entries"]}
    assert rights["status"] == "COMPLETE_FOR_EVERY_REGULAR_FILE_OR_SYMLINK_EXPECTED_IN_SCRATCH_ROOTFS"
    assert rights["base_image"] == "scratch"
    assert rights["regular_file_count"] == 9
    assert rights["symlink_count"] == 0
    assert rights["all_entries_retention_disclosure_publication_addressed"] is True
    assert rights_paths == set(frozen_root)
    assert {row["license_concluded"] for row in rights["entries"]} == {"Apache-2.0", "CC0-1.0"}
    assert licenses["complete_for_expected_rootfs"] is True
    for item in licenses["licenses"].values():
        check_ref(HERE, item)

    actual = layer["regular_file_or_symlink_inventory"]
    assert layer["exactly_equals_frozen_rootfs_manifest"] is True
    assert layer["regular_file_count"] == 9
    assert layer["symlink_count"] == 0
    assert set(actual) == set(frozen_root) == rights_paths
    for path in actual:
        assert actual[path]["type"] == frozen_root[path]["type"]
        assert actual[path]["sha256"] == frozen_root[path]["sha256"]
        assert actual[path]["size_bytes"] == frozen_root[path]["size_bytes"]
        assert actual[path]["mode"] == frozen_root[path]["mode"]

    assert sbom["spdxVersion"] == "SPDX-2.3"
    assert sbom["dataLicense"] == "CC0-1.0"
    assert len(sbom["packages"]) == 1
    assert sbom["packages"][0]["filesAnalyzed"] is True
    sbom_paths = {row["fileName"].removeprefix(".") for row in sbom["files"]}
    assert sbom_paths == set(actual)
    assert len(sbom["files"]) == 9
    for row in sbom["files"]:
        path = row["fileName"].removeprefix(".")
        assert row["licenseConcluded"] == next(item["license_concluded"] for item in rights["entries"] if item["path"] == path)
        checks = {item["algorithm"]: item["checksumValue"] for item in row.get("checksums", [])}
        assert checks["SHA256"] == actual[path]["sha256"]
        assert checks["SHA1"] == actual[path]["sha1"]

    assert descriptor["base_image"] == "scratch"
    assert descriptor["parent"] == ""
    assert descriptor["os"] == "linux"
    assert descriptor["architecture"] == "arm64"
    assert descriptor["entrypoint"] == ["/orion/probe"]
    assert len(descriptor["docker_save_layer_members"]) == 1
    assert descriptor["layer_archive_sha256"] == layer["layer_archive_sha256"]
    assert descriptor["layer_archive_size_bytes"] == layer["layer_archive_size_bytes"]

    assert runtime["runtime_pass"] is True
    assert runtime["start_returncode"] == 0
    assert runtime["container_exit_code"] == 0
    assert runtime["stdout_exact_expected"] is True
    assert runtime["stderr_empty"] is True
    assert runtime["diff"]["entry_count"] == 0
    assert runtime["security"] == {
        "cap_drop_all": True,
        "network_none": True,
        "no_new_privileges": True,
        "read_only_rootfs": True,
    }
    assert runtime["network_requests"] == 0
    assert runtime["protected_or_outcome_data_accessed"] is False
    assert (HERE / runtime["stdout"]["path"]).read_bytes() == EXPECTED_STDOUT
    assert (HERE / runtime["stderr"]["path"]).read_bytes() == b""
    for key in ("stdout", "stderr"):
        check_ref(HERE, runtime[key])
    for key in ("stdout", "stderr"):
        check_ref(HERE, runtime["diff"][key])

    check_ref(HERE, archive["archive"])
    assert archive["image_id"] == descriptor["image_id"]
    assert archive["config_digest"] == descriptor["config_digest"]
    assert archive["archive_retention_disclosure_publication_authorized"] is True
    assert disposal["daemon_container_and_tag_absence_verified"] is True
    assert disposal["container_remove_returncode"] == 0
    assert disposal["image_remove_returncode"] == 0
    assert disposal["post_disposal_container_inspect_returncode"] != 0
    assert disposal["post_disposal_image_inspect_returncode"] != 0
    check_ref(HERE, disposal["retained_archive"])

    assert gate["status"] == "PASS"
    assert gate["checks_passed"] == gate["checks_total"]
    assert all(row["pass"] for row in gate["checks"])
    assert gate["executed"] == {
        "benchmark": False,
        "c4": False,
        "coding_agent": False,
        "docker_probe_runtime": True,
        "docker_scratch_image_build": True,
        "evaluator": False,
        "model": False,
        "moss": False,
        "protected_data": False,
        "pytest": False,
        "repository_ci": False,
        "scorer": False,
    }

    assert result["successor_identity"] == IDENTITY
    assert result["status"] == "BOUND_ONE_FIELD_FOR_DISTINCT_SUCCESSOR"
    assert result["field_target"] == FIELD
    assert result["field_instances_closed"] == 1
    assert result["successor_count_basis"] == {
        "authority": "OWNER_SPECIFIED_C2_V4_TWENTY_ONE_FIELD_BASIS",
        "only_state_transition": FIELD + ": UNBOUND -> BOUND",
        "predecessor_blocking": 14,
        "predecessor_bound": 7,
        "successor_blocking": 13,
        "successor_bound": 8,
    }
    assert result["identity_frontier"]["aggregation_with_v11_or_v12_authorized"] is False
    assert result["identity_frontier"]["v11_distinct_runtime_successor_inherited"] is False
    assert result["identity_frontier"]["v12_distinct_source_core_successor_inherited"] is False
    assert result["identity_frontier"]["released_moss"] == {"blocking": 14, "bound": 7, "commit": "5453f1feebad44c199f5887f852fc5bc7fb7d4da", "unchanged": True}
    assert result["panel_and_claim_boundaries"]["ready_arms"] == "0/6"
    for key in ("H1", "H2", "H3", "H4", "performance", "superiority"):
        assert result["panel_and_claim_boundaries"][key] == "CANNOT_CHECK"
    assert result["manuscript_or_claim_ledger_edited"] is False
    assert result["no_pytest_or_repository_ci"] is True

    assert ledger["resolved_in_v13"] == [FIELD]
    assert ledger["remaining_successor_blocker_count"] == 13
    assert len(ledger["entries"]) == 13
    assert len({row["field"] for row in ledger["entries"]}) == 13
    assert FIELD not in {row["field"] for row in ledger["entries"]}
    assert all(row["next_discriminator"] for row in ledger["entries"])
    assert ledger["aggregation_with_v11_or_v12_authorized"] is False
    assert ledger["released_moss_unchanged"] is True
    assert validation["field_closed"] is True
    assert validation["pytest_or_repository_ci_run"] is False

    manifest_paths = {row["path"] for row in manifest["artifacts"]}
    assert manifest["artifact_count"] == len(manifest["artifacts"])
    assert len(manifest_paths) == manifest["artifact_count"]
    for item in manifest["artifacts"]:
        check_ref(HERE, item)
    actual_manifest_paths = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and path.name not in {"ARTIFACT_MANIFEST_V13.json", "SHA256SUMS"} and "__pycache__" not in path.parts
    }
    assert manifest_paths == actual_manifest_paths

    declared: dict[str, str] = {}
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

    print("P5_C2_V13_PACKET_VALID__COMPLETE_SCRATCH_IMAGE_SBOM_LICENSE_AND_GENERATED_AUTHORITY_BOUND__EIGHT_OF_TWENTY_ONE_DISTINCT_SUCCESSOR__V11_V12_NOT_AGGREGATED__RELEASED_MOSS_UNCHANGED__NO_PYTEST_CI_OR_OUTCOME_EXECUTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
