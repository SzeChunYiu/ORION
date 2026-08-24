#!/usr/bin/env python3
"""Exercise the Docker SDK surface used by the pinned SAB harness on synthetic data.

This program must never receive benchmark paths or credentials.  It builds one
tiny public Alpine image, creates one container, executes one fixed command,
and removes both before writing a bounded JSON receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import socket
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import docker

from docker_sdk_owner_normalization_v1 import install as install_owner_normalization


DOCKERFILE = """FROM docker.io/library/alpine:3.20.3
RUN printf 'ORION_SAB_SYNTHETIC_DOCKER_SDK_SMOKE_V1\\n' > /orion-smoke.txt
CMD [\"sleep\", \"300\"]
"""
EXPECTED = "ORION_SAB_SYNTHETIC_DOCKER_SDK_SMOKE_V1"
CREDENTIAL_NAMES = (
    "OPENAI_API_KEY",
    "AZURE_OPENAI_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    receipt_path = Path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    tag = f"orion-sab-synthetic-smoke-v1:{os.environ.get('SLURM_JOB_ID', 'local')}"
    build_log_bytes = bytearray()
    image_id = None
    container_id = None
    base_repo_digests: list[str] = []
    container_removed = False
    image_removed = False
    status = "FAIL"
    error_type = None
    error_message = None
    install_owner_normalization()
    client = docker.from_env()

    try:
        ping = bool(client.ping())
        version = client.version()
        with tempfile.TemporaryDirectory(prefix="orion-sab-smoke-") as td:
            context = Path(td)
            (context / "Dockerfile").write_text(DOCKERFILE, encoding="utf-8")
            image, logs = client.images.build(
                path=str(context),
                tag=tag,
                rm=True,
                forcerm=True,
                pull=True,
            )
            image_id = image.id
            base_repo_digests = sorted(
                client.images.get("docker.io/library/alpine:3.20.3").attrs.get(
                    "RepoDigests", []
                )
                or []
            )
            for item in logs:
                build_log_bytes.extend(
                    (json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n").encode()
                )
            container = client.containers.create(image.id, detach=True)
            container_id = container.id
            container.start()
            result = container.exec_run(["cat", "/orion-smoke.txt"])
            output = result.output.decode("utf-8", errors="replace").strip()
            if result.exit_code != 0 or output != EXPECTED:
                raise RuntimeError(
                    f"synthetic exec mismatch: exit={result.exit_code!r} output={output!r}"
                )
            status = "PASS"
    except Exception as exc:  # receipt must preserve the exact bounded failure type
        error_type = type(exc).__name__
        error_message = str(exc)[:2000]
        version = locals().get("version", {})
        ping = locals().get("ping", False)
    finally:
        if container_id:
            try:
                c = client.containers.get(container_id)
                c.remove(force=True)
            except Exception:
                pass
            try:
                client.containers.get(container_id)
            except docker.errors.NotFound:
                container_removed = True
        if image_id:
            try:
                client.images.remove(image=image_id, force=True)
            except Exception:
                pass
            try:
                client.images.get(image_id)
            except docker.errors.ImageNotFound:
                image_removed = True

    if status == "PASS" and not (container_removed and image_removed):
        status = "FAIL"
        error_type = "CleanupVerificationError"
        error_message = (
            f"container_removed={container_removed} image_removed={image_removed}"
        )

    credential_presence = {name: bool(os.environ.get(name)) for name in CREDENTIAL_NAMES}
    receipt = {
        "schema": "orion.p1.sab.lunarc.synthetic-docker-sdk-smoke.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "terminal": (
            "P1_SAB_LUNARC_PODMAN_DOCKER_SDK_SYNTHETIC_SMOKE_PASS__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
            if status == "PASS"
            else "P1_SAB_LUNARC_PODMAN_DOCKER_SDK_SYNTHETIC_SMOKE_FAIL__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
        ),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "slurm_job_partition": os.environ.get("SLURM_JOB_PARTITION"),
            "slurm_cpus_per_task": os.environ.get("SLURM_CPUS_PER_TASK"),
        },
        "docker_sdk": {
            "package_version": importlib.metadata.version("docker"),
            "docker_host_scheme": os.environ.get("DOCKER_HOST", "").split(":", 1)[0],
            "ping": ping,
            "server_version": version,
        },
        "synthetic_build": {
            "base_image_reference": "docker.io/library/alpine:3.20.3",
            "base_image_repo_digests": base_repo_digests,
            "built_image_id": image_id,
            "dockerfile_sha256": sha256_bytes(DOCKERFILE.encode()),
            "build_log_sha256": sha256_bytes(bytes(build_log_bytes)),
            "container_exec_expected_sha256": sha256_bytes((EXPECTED + "\n").encode()),
            "container_and_image_removed": container_removed and image_removed,
        },
        "credential_presence_only": credential_presence,
        "benchmark_archive_opened": False,
        "benchmark_entries_opened": False,
        "gold_evaluator_rubric_or_result_body_opened": False,
        "official_evaluator_invoked": False,
        "official_tasks_run": 0,
        "official_outcomes_opened": 0,
        "scientific_authority_delta": "NONE",
        "error": None
        if error_type is None
        else {"type": error_type, "message": error_message},
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["terminal"])
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
