#!/usr/bin/env python3
"""Build, inspect, and remove only the pinned public SAB base Dockerfile.

This program must never receive a benchmark archive, task, prediction,
evaluator, rubric, result, or credential. Container state is confined to the
node-local graph root configured by the enclosing Slurm job.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import socket
import tempfile
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import docker

from cleanup_gate_v1 import driver_cleanup_passed
from docker_sdk_owner_normalization_v1 import install as install_owner_normalization


EXPECTED_DOCKERFILE_SHA256 = (
    "08045fc892652a6835adb808ee6db4dc5715ae64f65878eb0d0140e7d8c29a15"
)
EXPECTED_DOCKERFILE_BYTES = 1251
EXPECTED_SOURCE_COMMIT = "c26e151ed601ba109dc4d35e057ff8e73fec469d"
EXPECTED_SOURCE_BLOB = "d0e11f6a2beb89080a242eb77a9f211dabf74069"
EXPECTED_SOURCE_SHA256 = (
    "b0122b82a64165389a134216dffda8d6e9d3ff8bfc3ebb3795a00d54f2194b25"
)
EXPECTED_OWNER_NORMALIZATION_SHA256 = (
    "a7c3e02fe61d464ff30202366c325d8497a8b7a9d17622c78d8ab8a9e9251c69"
)
EXPECTED_APT_RUNTIME_CONFIG_SHA256 = (
    "3abdae1e98cd78a24d4de9f6707f611d21b8495a8f04228dda69c9d69f62d7b3"
)
CREDENTIAL_NAMES = (
    "OPENAI_API_KEY",
    "AZURE_OPENAI_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
)
PROBE_DISTRIBUTIONS = (
    "numpy",
    "scipy",
    "matplotlib",
    "torch",
    "tensorflow",
    "rdkit",
    "tf_keras",
    "pandas",
    "scikit-learn",
    "httpx",
    "openai",
    "code_bert_score",
    "transformers",
    "pipreqs",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bounded(value: Any, limit: int = 4000) -> str:
    return str(value).replace("\x00", "")[:limit]


def normalized_event(item: Any) -> bytes:
    return (json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8", errors="replace"
    )


def consume_build_log(
    items: Iterable[Any], hasher: Any, tail: deque[str]
) -> tuple[int, int]:
    count = 0
    byte_count = 0
    for item in items:
        payload = normalized_event(item)
        hasher.update(payload)
        count += 1
        byte_count += len(payload)
        tail.append(bounded(payload.decode("utf-8", errors="replace"), 1000))
    return count, byte_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dockerfile", required=True)
    parser.add_argument("--source-receipt", required=True)
    parser.add_argument("--apt-runtime-config", required=True)
    parser.add_argument("--owner-normalization", required=True)
    parser.add_argument("--singlemap-shim-source", required=True)
    parser.add_argument("--singlemap-shim-binary", required=True)
    parser.add_argument("--singlemap-owner-command", required=True)
    parser.add_argument("--singlemap-adduser", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    dockerfile_path = Path(args.dockerfile)
    source_receipt_path = Path(args.source_receipt)
    apt_runtime_config_path = Path(args.apt_runtime_config)
    owner_normalization_path = Path(args.owner_normalization)
    singlemap_shim_source_path = Path(args.singlemap_shim_source)
    singlemap_shim_binary_path = Path(args.singlemap_shim_binary)
    singlemap_owner_command_path = Path(args.singlemap_owner_command)
    singlemap_adduser_path = Path(args.singlemap_adduser)
    receipt_path = Path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)

    dockerfile_bytes = dockerfile_path.read_bytes()
    source_receipt_bytes = source_receipt_path.read_bytes()
    apt_runtime_config_bytes = apt_runtime_config_path.read_bytes()
    owner_normalization_bytes = owner_normalization_path.read_bytes()
    singlemap_shim_source_bytes = singlemap_shim_source_path.read_bytes()
    singlemap_shim_binary_bytes = singlemap_shim_binary_path.read_bytes()
    singlemap_owner_command_bytes = singlemap_owner_command_path.read_bytes()
    singlemap_adduser_bytes = singlemap_adduser_path.read_bytes()
    source = json.loads(source_receipt_bytes)
    assert len(dockerfile_bytes) == EXPECTED_DOCKERFILE_BYTES
    assert sha256_bytes(dockerfile_bytes) == EXPECTED_DOCKERFILE_SHA256
    assert source["upstream"]["commit"] == EXPECTED_SOURCE_COMMIT
    assert source["upstream"]["git_blob_sha1"] == EXPECTED_SOURCE_BLOB
    assert source["source_file"]["sha256"] == EXPECTED_SOURCE_SHA256
    assert source["rendered_base_dockerfile"]["sha256"] == EXPECTED_DOCKERFILE_SHA256
    assert sha256_bytes(apt_runtime_config_bytes) == EXPECTED_APT_RUNTIME_CONFIG_SHA256
    assert (
        sha256_bytes(owner_normalization_bytes)
        == EXPECTED_OWNER_NORMALIZATION_SHA256
    )

    node_local_job_root = Path(os.environ["ORION_SAB_NODE_LOCAL_JOB_ROOT"])
    node_local_graphroot = Path(os.environ["ORION_SAB_NODE_LOCAL_GRAPHROOT"])
    initial_disk = shutil.disk_usage(node_local_job_root)

    tag = f"orion-sab-official-base-v1:{os.environ.get('SLURM_JOB_ID', 'local')}"
    build_log_hasher = hashlib.sha256()
    build_log_tail: deque[str] = deque(maxlen=200)
    build_log_events = 0
    build_log_bytes = 0
    client = None
    image_id = None
    base_image_id = None
    container_id = None
    adapter_probe_container_id = None
    adapter_probe_container_removed = False
    container_removed = False
    built_image_removed = False
    base_image_removed = False
    remaining_image_ids: list[str] = []
    base_repo_digests: list[str] = []
    image_inspect: dict[str, Any] = {}
    runtime_probe: dict[str, Any] = {}
    adapter_probe: dict[str, Any] = {}
    ping = False
    server_version: dict[str, Any] = {}
    runtime_status = "FAIL"
    error_type = None
    error_message = None
    cleanup_errors: list[dict[str, str]] = []

    def record_cleanup_error(operation: str, exc: Exception) -> None:
        cleanup_errors.append(
            {
                "operation": operation,
                "type": type(exc).__name__,
                "message": bounded(exc),
            }
        )

    credential_presence = {name: bool(os.environ.get(name)) for name in CREDENTIAL_NAMES}
    if any(credential_presence.values()):
        error_type = "CredentialBoundaryError"
        error_message = "one or more forbidden credential variables were present"
    else:
        try:
            install_owner_normalization()
            client = docker.from_env()
            ping = bool(client.ping())
            server_version = client.version()
            base_image = client.images.pull(
                "docker.io/library/ubuntu", tag="22.04"
            )
            base_image_id = base_image.id
            base_repo_digests = sorted(base_image.attrs.get("RepoDigests", []) or [])
            adapter_container = client.containers.create(
                base_image.id,
                command=[
                    "/bin/sh",
                    "-c",
                    "set -eu; printf 'ld_preload=%s\\n' \"$LD_PRELOAD\"; "
                    "printf 'chown_command=%s\\n' \"$(command -v chown)\"; "
                    "touch /tmp/orion-owner; chown 100:4 /tmp/orion-owner; "
                    "chgrp 4 /tmp/orion-owner; stat -c 'owner=%u:%g' /tmp/orion-owner",
                ],
            )
            adapter_probe_container_id = adapter_container.id
            adapter_container.start()
            adapter_result = adapter_container.wait()
            adapter_output = adapter_container.logs(stdout=True, stderr=True)
            adapter_probe = {
                "exit_code": adapter_result.get("StatusCode"),
                "stdout_sha256": sha256_bytes(adapter_output),
                "bounded_output": bounded(
                    adapter_output.decode("utf-8", errors="replace")
                ),
            }
            if adapter_result.get("StatusCode") != 0 or b"owner=0:0" not in adapter_output:
                raise RuntimeError(f"single-map adapter probe failed: {adapter_probe}")
            adapter_container.remove(force=True)
            adapter_probe_container_removed = True
            adapter_probe_container_id = None

            with tempfile.TemporaryDirectory(prefix="orion-sab-official-base-") as td:
                context = Path(td)
                (context / "Dockerfile").write_bytes(dockerfile_bytes)
                image, logs = client.images.build(
                    path=str(context),
                    tag=tag,
                    rm=True,
                    forcerm=True,
                    pull=True,
                )
                image_id = image.id
                events, size = consume_build_log(
                    logs, build_log_hasher, build_log_tail
                )
                build_log_events += events
                build_log_bytes += size

            image.reload()
            attrs = image.attrs
            config = attrs.get("Config", {}) or {}
            config_bytes = json.dumps(
                config, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            image_inspect = {
                "id": image.id,
                "architecture": attrs.get("Architecture"),
                "os": attrs.get("Os"),
                "created": attrs.get("Created"),
                "size_bytes": attrs.get("Size"),
                "virtual_size_bytes": attrs.get("VirtualSize"),
                "repo_tags": sorted(attrs.get("RepoTags", []) or []),
                "repo_digests": sorted(attrs.get("RepoDigests", []) or []),
                "config_sha256": sha256_bytes(config_bytes),
                "config_contains_credential_name": any(
                    name.encode("utf-8") in config_bytes for name in CREDENTIAL_NAMES
                ),
            }

            container = client.containers.create(
                image.id, command=["sleep", "300"], detach=True
            )
            container_id = container.id
            container.start()
            probe_program = (
                "import importlib.metadata as m,json,platform;"
                f"names={list(PROBE_DISTRIBUTIONS)!r};"
                "print(json.dumps({'python':platform.python_version(),"
                "'distributions':{n:m.version(n) for n in names}},sort_keys=True))"
            )
            probe_result = container.exec_run(
                ["/opt/miniconda3/bin/python", "-c", probe_program]
            )
            probe_output = bytes(probe_result.output)
            if probe_result.exit_code != 0:
                raise RuntimeError(
                    "package inspection failed: "
                    f"exit={probe_result.exit_code} output={bounded(probe_output)}"
                )
            package_probe = json.loads(probe_output.decode("utf-8"))

            conda_result = container.exec_run(
                ["/opt/miniconda3/bin/conda", "--version"]
            )
            nonroot_result = container.exec_run(["id", "nonroot"])
            if conda_result.exit_code != 0 or nonroot_result.exit_code != 0:
                raise RuntimeError(
                    "base command inspection failed: "
                    f"conda_exit={conda_result.exit_code} "
                    f"nonroot_exit={nonroot_result.exit_code}"
                )
            runtime_probe = {
                "package_probe": package_probe,
                "package_probe_stdout_sha256": sha256_bytes(probe_output),
                "conda_version": conda_result.output.decode(
                    "utf-8", errors="replace"
                ).strip(),
                "nonroot_identity": nonroot_result.output.decode(
                    "utf-8", errors="replace"
                ).strip(),
            }
            runtime_status = "PASS"
        except docker.errors.BuildError as exc:
            events, size = consume_build_log(
                exc.build_log or [], build_log_hasher, build_log_tail
            )
            build_log_events += events
            build_log_bytes += size
            error_type = type(exc).__name__
            error_message = bounded(exc)
        except Exception as exc:
            error_type = type(exc).__name__
            error_message = bounded(exc)
        finally:
            if client is not None:
                if adapter_probe_container_id:
                    try:
                        client.containers.get(adapter_probe_container_id).remove(force=True)
                    except Exception as exc:
                        record_cleanup_error("remove_adapter_probe_container", exc)
                    try:
                        client.containers.get(adapter_probe_container_id)
                    except docker.errors.NotFound:
                        adapter_probe_container_removed = True
                    except Exception as exc:
                        record_cleanup_error("verify_adapter_probe_container_removed", exc)
                if container_id:
                    try:
                        client.containers.get(container_id).remove(force=True)
                    except Exception as exc:
                        record_cleanup_error("remove_runtime_probe_container", exc)
                    try:
                        client.containers.get(container_id)
                    except docker.errors.NotFound:
                        container_removed = True
                    except Exception as exc:
                        record_cleanup_error("verify_runtime_probe_container_removed", exc)
                if image_id:
                    try:
                        client.images.remove(image=image_id, force=True)
                    except Exception as exc:
                        record_cleanup_error("remove_built_image", exc)
                    try:
                        client.images.get(image_id)
                    except docker.errors.ImageNotFound:
                        built_image_removed = True
                    except Exception as exc:
                        record_cleanup_error("verify_built_image_removed", exc)
                if base_image_id:
                    try:
                        client.images.remove(image=base_image_id, force=True)
                    except Exception as exc:
                        record_cleanup_error("remove_base_image", exc)
                    try:
                        client.images.get(base_image_id)
                    except docker.errors.ImageNotFound:
                        base_image_removed = True
                    except Exception as exc:
                        record_cleanup_error("verify_base_image_removed", exc)
                try:
                    for residual in client.images.list(all=True):
                        try:
                            client.images.remove(image=residual.id, force=True)
                        except Exception as exc:
                            record_cleanup_error(
                                f"remove_residual_image:{residual.id}", exc
                            )
                    client.images.prune(filters={"dangling": True})
                    remaining_image_ids = sorted(
                        img.id for img in client.images.list(all=True)
                    )
                except Exception as exc:
                    record_cleanup_error("residual_image_sweep", exc)
                try:
                    client.close()
                except Exception as exc:
                    record_cleanup_error("close_docker_client", exc)

    cleanup_ok = driver_cleanup_passed(
        adapter_probe_container_removed=adapter_probe_container_removed,
        container_removed=container_removed,
        built_image_removed=built_image_removed,
        base_image_removed=base_image_removed,
        remaining_image_ids=remaining_image_ids,
        cleanup_errors=cleanup_errors,
    )
    if not cleanup_ok:
        runtime_status = "FAIL"
        if error_type is None:
            error_type = "CleanupVerificationError"
            error_message = (
                f"adapter_probe_container_removed={adapter_probe_container_removed} "
                f"container_removed={container_removed} "
                f"built_image_removed={built_image_removed} "
                f"base_image_removed={base_image_removed} "
                f"remaining_images={remaining_image_ids} "
                f"cleanup_errors={cleanup_errors}"
            )

    post_image_cleanup_disk = shutil.disk_usage(node_local_job_root)

    receipt = {
        "schema": "orion.p1.sab.lunarc.official-public-base-smoke.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": runtime_status,
        "terminal": (
            "P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_RUNTIME_PASS__BATCH_CLEANUP_PENDING__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
            if runtime_status == "PASS"
            else "P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_RUNTIME_FAIL__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
        ),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "slurm_job_partition": os.environ.get("SLURM_JOB_PARTITION"),
            "slurm_cpus_per_task": os.environ.get("SLURM_CPUS_PER_TASK"),
            "tmpdir": os.environ.get("TMPDIR"),
        },
        "source_binding": {
            "repository": "https://github.com/OSU-NLP-Group/ScienceAgentBench",
            "commit": EXPECTED_SOURCE_COMMIT,
            "path": "evaluation/harness/dockerfiles.py",
            "git_blob_sha1": EXPECTED_SOURCE_BLOB,
            "source_file_sha256": EXPECTED_SOURCE_SHA256,
            "source_receipt_sha256": sha256_bytes(source_receipt_bytes),
            "rendered_platform": "linux/x86_64",
            "rendered_arch": "x86_64",
            "rendered_dockerfile_bytes": len(dockerfile_bytes),
            "rendered_dockerfile_sha256": sha256_bytes(dockerfile_bytes),
        },
        "docker_sdk": {
            "package_version": importlib.metadata.version("docker"),
            "docker_host_scheme": os.environ.get("DOCKER_HOST", "").split(":", 1)[0],
            "ping": ping,
            "server_version": server_version,
        },
        "rootless_runtime_adapter": {
            "docker_sdk_context_owner_normalization_sha256": sha256_bytes(
                owner_normalization_bytes
            ),
            "apt_sandbox_config_sha256": sha256_bytes(apt_runtime_config_bytes),
            "apt_sandbox_config_bytes": len(apt_runtime_config_bytes),
            "apt_sandbox_config_mounted_read_only_for_run_steps": True,
            "apt_sandbox_user_forced_to_root": True,
            "singlemap_identity_normalization_source_sha256": sha256_bytes(
                singlemap_shim_source_bytes
            ),
            "singlemap_identity_normalization_binary_sha256": sha256_bytes(
                singlemap_shim_binary_bytes
            ),
            "singlemap_identity_normalization_binary_bytes": len(
                singlemap_shim_binary_bytes
            ),
            "singlemap_identity_normalization_mounted_read_only": True,
            "singlemap_identity_change_requests_acknowledged_without_unrepresentable_change": True,
            "singlemap_owner_command_sha256": sha256_bytes(
                singlemap_owner_command_bytes
            ),
            "singlemap_owner_command_bytes": len(singlemap_owner_command_bytes),
            "singlemap_owner_command_mounted_read_only": True,
            "singlemap_owner_command_mount_paths": [
                "/usr/bin/chown",
                "/usr/bin/chgrp",
            ],
            "singlemap_owner_commands_are_noop": True,
            "singlemap_adduser_sha256": sha256_bytes(singlemap_adduser_bytes),
            "singlemap_adduser_bytes": len(singlemap_adduser_bytes),
            "singlemap_adduser_mount_path": "/usr/local/sbin/adduser",
            "singlemap_adduser_exact_arguments_fail_closed": True,
            "singlemap_adduser_home_owner_fidelity": "CANNOT_CHECK_SINGLEMAP_ROOT_OWNED",
            "singlemap_adapter_probe": adapter_probe,
            "singlemap_adapter_probe_container_removed": adapter_probe_container_removed,
            "dockerfile_bytes_modified": False,
            "reason": "single-map rootless namespace cannot represent upstream package and user ownership or privilege-drop identities",
        },
        "resolved_identities": {
            "ubuntu_22_04_image_id": base_image_id,
            "ubuntu_22_04_repo_digests": base_repo_digests,
            "built_image": image_inspect,
        },
        "bounded_inspection": runtime_probe,
        "build_log": {
            "normalized_json_event_count": build_log_events,
            "normalized_json_bytes": build_log_bytes,
            "normalized_json_sha256": build_log_hasher.hexdigest(),
            "bounded_tail": list(build_log_tail),
            "raw_log_retained_in_repository": False,
        },
        "cleanup": {
            "container_removed": container_removed,
            "built_image_removed": built_image_removed,
            "resolved_base_image_removed": base_image_removed,
            "remaining_image_ids": remaining_image_ids,
            "cleanup_errors": cleanup_errors,
            "node_local_job_root": str(node_local_job_root),
            "node_local_graphroot": str(node_local_graphroot),
            "node_local_filesystem_bytes": initial_disk.total,
            "node_local_free_bytes_before_build": initial_disk.free,
            "node_local_free_bytes_after_image_cleanup": post_image_cleanup_disk.free,
            "node_local_job_root_removal_pending": True,
        },
        "credential_presence_only": credential_presence,
        "boundary": {
            "public_base_dockerfile_body_opened": True,
            "benchmark_archive_opened": False,
            "benchmark_entries_opened": False,
            "official_task_or_prediction_body_opened": False,
            "gold_evaluator_rubric_or_result_body_opened": False,
            "official_evaluator_invoked": False,
            "official_tasks_run": 0,
            "official_outcomes_opened": 0,
            "scientific_authority_delta": "NONE",
        },
        "cannot_check": {
            "official_instance_images": "CANNOT_CHECK_NOT_BUILT",
            "official_evaluator": "CANNOT_CHECK_NOT_IMPORTED_OR_INVOKED",
            "benchmark_archive": "CANNOT_CHECK_NOT_RETAINED_OR_EXTRACTED",
            "credentials_and_judge_route": "CANNOT_CHECK_CREDENTIALS_ABSENT",
            "full_102_task_execution": "CANNOT_CHECK_ZERO_TASKS_RUN",
            "dependency_reproducibility": "CANNOT_CHECK_OFFICIAL_DOCKERFILE_PINS_RANGES_OR_LATEST_CHANNEL_RESOLUTION",
            "miniconda_installer_digest": "CANNOT_CHECK_NOT_PINNED_BY_OFFICIAL_DOCKERFILE",
            "multi_owner_filesystem_fidelity": "CANNOT_CHECK_SINGLEMAP_IDENTITY_NORMALIZATION_ACTIVE",
            "package_install_privilege_drop_fidelity": "CANNOT_CHECK_APT_AND_IDENTITY_NORMALIZATION_ACTIVE",
        },
        "error": None
        if error_type is None
        else {"type": error_type, "message": error_message},
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(receipt["terminal"])
    return 0 if runtime_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
