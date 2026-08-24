#!/usr/bin/env python3
"""Network-free validator for the official public-base LUNARC smoke packet."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from cleanup_gate_v1 import batch_cleanup_passed, driver_cleanup_passed


ROOT = Path(__file__).resolve().parent
PREDECESSOR = ROOT.parent / "p1-scienceagentbench-lunarc-runtime-v1-2026-08-24"
EXPECTED_DOCKERFILE_SHA256 = (
    "08045fc892652a6835adb808ee6db4dc5715ae64f65878eb0d0140e7d8c29a15"
)
EXPECTED_SOURCE_SHA256 = (
    "b0122b82a64165389a134216dffda8d6e9d3ff8bfc3ebb3795a00d54f2194b25"
)
EXPECTED_SOURCE_COMMIT = "c26e151ed601ba109dc4d35e057ff8e73fec469d"
EXPECTED_SOURCE_BLOB = "d0e11f6a2beb89080a242eb77a9f211dabf74069"
EXPECTED_TERMINAL = (
    "P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_SMOKE_PASS__"
    "EXACT_PINNED_DOCKERFILE_BOUND__IMAGE_AND_NODE_LOCAL_LAYERS_REMOVED__"
    "ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
)
EXPECTED_PACKAGES = {
    "code_bert_score": "0.4.1",
    "httpx": "0.27.2",
    "matplotlib": "3.7.5",
    "numpy": "1.26.4",
    "openai": "1.54.4",
    "pandas": "2.3.3",
    "pipreqs": "0.5.0",
    "rdkit": "2023.9.5",
    "scikit-learn": "1.7.2",
    "scipy": "1.13.1",
    "tensorflow": "2.17.0",
    "tf_keras": "2.17.0",
    "torch": "2.3.0",
    "transformers": "4.46.3",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_sums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, separator, name = line.partition("  ")
        assert separator and re.fullmatch(r"[0-9a-f]{64}", digest) and name
        result[name] = digest
    return result


def main() -> int:
    source = load(ROOT / "SOURCE_BINDING_V1.json")
    integration = load(ROOT / "INTEGRATION_BINDING_V1.json")
    dockerfile = ROOT / "OFFICIAL_BASE_DOCKERFILE_V1"
    receipt = load(ROOT / "SLURM_OFFICIAL_BASE_RECEIPT_V1.json")

    assert source["upstream"]["commit"] == EXPECTED_SOURCE_COMMIT
    assert source["upstream"]["git_blob_sha1"] == EXPECTED_SOURCE_BLOB
    assert source["source_file"]["sha256"] == EXPECTED_SOURCE_SHA256
    assert source["rendered_base_dockerfile"]["bytes"] == 1251
    assert source["rendered_base_dockerfile"]["sha256"] == EXPECTED_DOCKERFILE_SHA256
    assert dockerfile.stat().st_size == 1251
    assert sha256(dockerfile) == EXPECTED_DOCKERFILE_SHA256
    assert integration["audit_start_base_commit"] == (
        "adf76040815e71218776793e2f1a7d1afdb6e9d2"
    )
    assert integration["packet_integration_base_commit"] == (
        "0dc9e07badae039743a6966dd9198586a497d72f"
    )
    assert integration["successful_execution_binding"]["source_binding_sha256"] == sha256(
        ROOT / "SOURCE_BINDING_V1.json"
    )
    assert integration["successful_execution_binding"]["receipt_sha256"] == sha256(
        ROOT / "SLURM_OFFICIAL_BASE_RECEIPT_V1.json"
    )
    assert integration["successful_execution_binding"]["failure_atlas_sha256"] == sha256(
        ROOT / "FAILURE_ATLAS_V1.json"
    )
    assert integration["successful_execution_binding"]["cleanup_gate_sha256"] == sha256(
        ROOT / "cleanup_gate_v1.py"
    )
    assert integration["concurrent_merged_archive_lane"][
        "archive_or_entry_body_opened_by_this_lane"
    ] is False

    assert receipt["schema"] == "orion.p1.sab.lunarc.official-public-base-smoke.v1"
    assert receipt["status"] == "PASS"
    assert receipt["terminal"] == EXPECTED_TERMINAL
    assert receipt["error"] is None
    assert receipt["host"]["slurm_job_id"] == "3533961"
    assert receipt["host"]["hostname"] == "cn045"
    assert receipt["host"]["tmpdir"] == "/local/slurmtmp.3533961"

    binding = receipt["source_binding"]
    assert binding["commit"] == EXPECTED_SOURCE_COMMIT
    assert binding["git_blob_sha1"] == EXPECTED_SOURCE_BLOB
    assert binding["source_file_sha256"] == EXPECTED_SOURCE_SHA256
    assert binding["source_receipt_sha256"] == sha256(ROOT / "SOURCE_BINDING_V1.json")
    assert binding["rendered_dockerfile_bytes"] == 1251
    assert binding["rendered_dockerfile_sha256"] == EXPECTED_DOCKERFILE_SHA256

    sdk = receipt["docker_sdk"]
    assert sdk["package_version"] == "7.1.0"
    assert sdk["ping"] is True
    assert sdk["docker_host_scheme"] == "unix"
    assert sdk["server_version"]["Version"] == "5.8.2"
    assert sdk["server_version"]["ApiVersion"] == "1.44"

    resolved = receipt["resolved_identities"]
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", resolved["ubuntu_22_04_image_id"])
    assert len(resolved["ubuntu_22_04_repo_digests"]) == 2
    for digest in resolved["ubuntu_22_04_repo_digests"]:
        assert re.fullmatch(r"docker\.io/library/ubuntu@sha256:[0-9a-f]{64}", digest)
    built = resolved["built_image"]
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", built["id"])
    assert built["architecture"] == "amd64" and built["os"] == "linux"
    assert built["size_bytes"] == 10_625_816_107
    assert built["config_contains_credential_name"] is False
    assert built["repo_digests"] and built["repo_tags"]

    inspection = receipt["bounded_inspection"]
    assert inspection["package_probe"]["python"] == "3.10.20"
    assert inspection["package_probe"]["distributions"] == EXPECTED_PACKAGES
    assert inspection["conda_version"] == "conda 26.7.1"
    assert inspection["nonroot_identity"] == (
        "uid=1000(nonroot) gid=1000(nonroot) groups=1000(nonroot)"
    )

    adapter = receipt["rootless_runtime_adapter"]
    assert adapter["dockerfile_bytes_modified"] is False
    assert adapter["docker_sdk_context_owner_normalization_sha256"] == sha256(
        ROOT / "docker_sdk_owner_normalization_v1.py"
    )
    assert sha256(ROOT / "docker_sdk_owner_normalization_v1.py") == sha256(
        PREDECESSOR / "docker_sdk_owner_normalization_v1.py"
    )
    assert adapter["apt_sandbox_config_sha256"] == sha256(
        ROOT / "apt_rootless_sandbox_v1.conf"
    )
    assert adapter["singlemap_identity_normalization_source_sha256"] == sha256(
        ROOT / "singlemap_identity_normalization_v1.c"
    )
    assert adapter["singlemap_owner_command_sha256"] == sha256(
        ROOT / "singlemap_owner_command_v1.pl"
    )
    assert adapter["singlemap_adduser_sha256"] == sha256(
        ROOT / "singlemap_adduser_v1.sh"
    )
    assert adapter["singlemap_adapter_probe"]["exit_code"] == 0
    assert "owner=0:0" in adapter["singlemap_adapter_probe"]["bounded_output"]
    assert adapter["singlemap_adapter_probe_container_removed"] is True
    assert adapter["singlemap_owner_commands_are_noop"] is True
    assert adapter["singlemap_adduser_exact_arguments_fail_closed"] is True

    build_log = receipt["build_log"]
    assert build_log["normalized_json_event_count"] == 22_232
    assert build_log["normalized_json_bytes"] == 672_301
    assert build_log["normalized_json_sha256"] == (
        "5bc54b20e286379b87a214c7c7dab6b87014cce965eea324c6e13e8845de589e"
    )
    assert build_log["raw_log_retained_in_repository"] is False

    cleanup = receipt["cleanup"]
    for key in (
        "container_removed",
        "built_image_removed",
        "resolved_base_image_removed",
        "node_local_job_root_removed",
        "runtime_socket_root_removed",
    ):
        assert cleanup[key] is True, key
    assert cleanup["remaining_image_ids"] == []
    assert cleanup["cleanup_errors"] == []
    assert cleanup["node_local_job_root_removal_pending"] is False
    assert cleanup["node_local_graphroot"].startswith(receipt["host"]["tmpdir"] + "/")

    clean_driver = {
        "adapter_probe_container_removed": True,
        "container_removed": True,
        "built_image_removed": True,
        "base_image_removed": True,
        "remaining_image_ids": [],
        "cleanup_errors": [],
    }
    assert driver_cleanup_passed(**clean_driver) is True
    for key in (
        "adapter_probe_container_removed",
        "container_removed",
        "built_image_removed",
        "base_image_removed",
    ):
        hostile = dict(clean_driver)
        hostile[key] = False
        assert driver_cleanup_passed(**hostile) is False
    hostile = dict(clean_driver)
    hostile["remaining_image_ids"] = ["sha256:" + "0" * 64]
    assert driver_cleanup_passed(**hostile) is False
    hostile = dict(clean_driver)
    hostile["cleanup_errors"] = [
        {"operation": "residual_image_sweep", "type": "InjectedError", "message": "x"}
    ]
    assert driver_cleanup_passed(**hostile) is False

    assert batch_cleanup_passed(
        receipt, driver_rc=0, job_root_removed=True, socket_root_removed=True
    ) is True
    hostile_receipt = json.loads(json.dumps(receipt))
    hostile_receipt["error"] = {"type": "InjectedError", "message": "x"}
    assert batch_cleanup_passed(
        hostile_receipt, driver_rc=0, job_root_removed=True, socket_root_removed=True
    ) is False
    hostile_receipt = json.loads(json.dumps(receipt))
    hostile_receipt["cleanup"]["cleanup_errors"] = [
        {"operation": "residual_image_sweep", "type": "InjectedError", "message": "x"}
    ]
    assert batch_cleanup_passed(
        hostile_receipt, driver_rc=0, job_root_removed=True, socket_root_removed=True
    ) is False

    assert not any(receipt["credential_presence_only"].values())
    boundary = receipt["boundary"]
    assert boundary["public_base_dockerfile_body_opened"] is True
    for key in (
        "benchmark_archive_opened",
        "benchmark_entries_opened",
        "official_task_or_prediction_body_opened",
        "gold_evaluator_rubric_or_result_body_opened",
        "official_evaluator_invoked",
    ):
        assert boundary[key] is False, key
    assert boundary["official_tasks_run"] == 0
    assert boundary["official_outcomes_opened"] == 0
    assert boundary["scientific_authority_delta"] == "NONE"
    assert all(value.startswith("CANNOT_CHECK") for value in receipt["cannot_check"].values())

    atlas = load(ROOT / "FAILURE_ATLAS_V1.json")
    assert atlas["terminal"] == (
        "P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_FAILURE_CHAIN_BOUND__"
        "8_RUNTIME_FAILURES_AND_1_SUPERSEDED_PASS_REPAIRED_TO_REVIEWED_PASS__"
        "ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
    )
    assert [item["slurm_job_id"] for item in atlas["jobs"]] == [
        "3533829", "3533832", "3533835", "3533838", "3533841",
        "3533843", "3533844", "3533851", "3533961",
    ]
    for item in atlas["jobs"][:-1]:
        failure_path = ROOT / item["receipt_path"]
        failure = load(failure_path)
        assert item["status"] == failure["status"] == "FAIL"
        assert item["receipt_sha256"] == sha256(failure_path)
        assert failure["error"] is not None
        assert failure["cleanup"]["node_local_job_root_removed"] is True
        assert not any(failure["credential_presence_only"].values())
        assert failure["boundary"]["official_tasks_run"] == 0
        assert failure["boundary"]["official_outcomes_opened"] == 0
    assert atlas["jobs"][-1]["receipt_sha256"] == sha256(
        ROOT / "SLURM_OFFICIAL_BASE_RECEIPT_V1.json"
    )
    superseded = atlas["superseded_cleanup_guard_witness"]
    assert superseded["slurm_job_id"] == "3533859"
    assert superseded["status"] == (
        "PASS_RECEIPT_SUPERSEDED_BY_FAIL_CLOSED_HARNESS_REVIEW"
    )
    superseded_path = ROOT / superseded["receipt_path"]
    assert superseded["receipt_sha256"] == sha256(superseded_path)
    assert load(superseded_path)["host"]["slurm_job_id"] == "3533859"

    sacct = (ROOT / "SLURM_JOB_CHAIN_SACCT_V1.txt").read_text(encoding="utf-8")
    assert "3533844.batch|batch|FAILED|00:09:10|1:0|cn121|4||15317472K" in sacct
    assert "3533859.batch|batch|COMPLETED|00:07:07|0:0|cn121|4||25610608K" in sacct
    assert "3533961.batch|batch|COMPLETED|00:06:56|0:0|cn045|4||25801412K" in sacct

    remote_sums = parse_sums(ROOT / "REMOTE_SHA256SUMS")
    remote_by_name = {Path(path).name: digest for path, digest in remote_sums.items()}
    for name in (
        "SLURM_OFFICIAL_BASE_RECEIPT_V1.json",
        "SOURCE_BINDING_V1.json",
        "OFFICIAL_BASE_DOCKERFILE_V1",
        "apt_rootless_sandbox_v1.conf",
        "singlemap_identity_normalization_v1.c",
        "singlemap_owner_command_v1.pl",
        "singlemap_adduser_v1.sh",
        "docker_sdk_owner_normalization_v1.py",
        "cleanup_gate_v1.py",
        "official_base_docker_sdk_smoke_v1.py",
        "run_lunarc_official_base_smoke_v1.sh",
        "REMOTE_INPUT_SHA256SUMS",
    ):
        assert remote_by_name[name] == sha256(ROOT / name), name
    assert len(parse_sums(ROOT / "EXTERNAL_LOG_SHA256SUMS")) == 2

    recorded = parse_sums(ROOT / "SHA256SUMS")
    files = {
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    assert set(recorded) == files
    for name, digest in recorded.items():
        assert sha256(ROOT / name) == digest, name
    assert max((ROOT / name).stat().st_size for name in files) < 1_000_000

    print(
        "P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_V1_STATIC_VALIDATION_PASS "
        "job=3533961 dockerfile_bytes=1251 "
        f"dockerfile_sha256={EXPECTED_DOCKERFILE_SHA256} "
        "failures=8 tasks=0 outcomes=0 cleanup=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
