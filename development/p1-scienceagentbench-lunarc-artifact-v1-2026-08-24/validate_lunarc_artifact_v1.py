#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RECEIPT = ROOT / "LUNARC_ARTIFACT_STAGE_RECEIPT_V1.json"
ARCHIVE_BYTES = 1_769_478_786
ARCHIVE_SHA256 = "46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610"
OFFICIAL_COMMIT = "c26e151ed601ba109dc4d35e057ff8e73fec469d"


def main() -> int:
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["schema"] == "orion.p1.sab.lunarc.protected-artifact-stage.v1"
    assert data["status"] == "PASS"
    assert data["terminal"] == (
        "P1_SAB_LUNARC_ARCHIVE_STAGED_AND_HASH_MANIFESTED__"
        "EXTRACTED_TREE_QUARANTINED__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
    )
    assert data["archive"]["bytes"] == ARCHIVE_BYTES
    assert data["archive"]["sha256"] == ARCHIVE_SHA256
    assert data["archive"]["mode"] == "0o600"
    assert len(data["archive"]["remote_path_sha256"]) == 64

    extraction = data["extraction"]
    assert extraction["zip_entries"] == extraction["files"] + extraction["directories"]
    assert extraction["files"] == extraction["encrypted_files"] == 845
    assert extraction["decrypted_file_bytes"] > ARCHIVE_BYTES
    assert extraction["path_bearing_manifest_bytes"] > 0
    assert len(extraction["path_bearing_manifest_sha256"]) == 64
    assert extraction["path_bearing_manifest_retained_off_repository"] is True
    assert extraction["entry_names_or_bodies_printed"] is False
    assert extraction["entry_bodies_semantically_inspected"] is False
    assert extraction["quarantined_root_mode"] == "0o0"

    assert data["password_source"] == "official_public_README_at_pinned_commit"
    assert data["official_source_commit"] == OFFICIAL_COMMIT
    assert data["official_tasks_run"] == 0
    assert data["official_outcomes_opened"] == 0
    assert data["official_evaluator_invoked"] is False
    assert data["scientific_authority_delta"] == "NONE"

    remote_sums: dict[str, str] = {}
    for line in (ROOT / "REMOTE_SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, remote_path = line.split("  ", 1)
        remote_sums[Path(remote_path).name] = digest
    for name in (
        "LUNARC_ARTIFACT_STAGE_RECEIPT_V1.json",
        "stage_archive_v1.py",
        "run_lunarc_archive_stage_v1.sh",
    ):
        assert name in remote_sums
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == remote_sums[name]

    sums: dict[str, str] = {}
    for line in (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        sums[name] = digest
    for name, expected in sums.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected

    print(
        "P1_SAB_LUNARC_ARTIFACT_V1_STATIC_VALIDATION_PASS "
        f"files={extraction['files']} bytes={extraction['decrypted_file_bytes']} "
        "tasks=0 outcomes=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
