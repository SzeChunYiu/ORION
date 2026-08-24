#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / "SLURM_SYNTHETIC_RECEIPT_V1.json"


def main() -> int:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["schema"] == "orion.p1.sab.lunarc.synthetic-docker-sdk-smoke.v1"
    assert data["status"] == "PASS"
    assert data["docker_sdk"]["package_version"] == "7.1.0"
    assert data["docker_sdk"]["ping"] is True
    assert data["docker_sdk"]["docker_host_scheme"] == "unix"
    assert data["synthetic_build"]["container_and_image_removed"] is True
    assert data["synthetic_build"]["base_image_repo_digests"]
    assert re.fullmatch(
        r"sha256:[0-9a-f]{64}", data["synthetic_build"]["built_image_id"]
    )
    assert not any(data["credential_presence_only"].values())
    assert data["benchmark_archive_opened"] is False
    assert data["benchmark_entries_opened"] is False
    assert data["gold_evaluator_rubric_or_result_body_opened"] is False
    assert data["official_evaluator_invoked"] is False
    assert data["official_tasks_run"] == 0
    assert data["official_outcomes_opened"] == 0
    assert data["scientific_authority_delta"] == "NONE"
    assert data["error"] is None

    remote_sums = {}
    for line in (ROOT / "REMOTE_SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, remote_path = line.split("  ", 1)
        remote_sums[Path(remote_path).name] = digest
    for name in (
        "docker_sdk_owner_normalization_v1.py",
        "synthetic_docker_sdk_smoke_v1.py",
        "run_lunarc_synthetic_smoke_v1.sh",
    ):
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == remote_sums[name]

    sums = {}
    for line in (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        sums[name] = digest
    for name, expected in sums.items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        assert actual == expected, (name, expected, actual)

    print(
        "P1_SAB_LUNARC_RUNTIME_V1_STATIC_VALIDATION_PASS "
        f"node={data['host']['hostname']} docker_sdk=7.1.0 tasks=0 outcomes=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
