from __future__ import annotations

import hashlib
import json
from pathlib import Path


JOB_DIR = Path(__file__).resolve().parents[1]
TERMINAL = (
    "NQ_CRB_FULL_REPLAY_JOB_3544056_FAILED_CENSUS_RECEIPT_SERIALIZATION"
    "__D2_D3_AUTHORITY_CANNOT_CHECK"
)
KEY = "741454d7d6b513ccd80d2aa9a78d2a9f5076fe8075341d0ecc8e95566ecc28ea"


def load_json(name: str) -> dict[str, object]:
    return json.loads((JOB_DIR / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((JOB_DIR / name).read_bytes()).hexdigest()


def test_raw_evidence_and_remote_hashes_are_bound() -> None:
    receipt = load_json("POST_EXECUTION_FAILURE_RECEIPT.json")
    for name, binding in receipt["evidence"].items():
        assert binding["path"] == name
        assert sha256(name) == binding["sha256"]
    remote = (JOB_DIR / "REMOTE_COLLECTION.txt").read_text(encoding="utf-8")
    expected = {
        "SLURM_STDOUT.txt": "db0aac735f51ff6eeb4141f05bd77dac631c054bc8c100189b66561ed211bb61",
        "SLURM_STDERR.txt": "c0c1926c7f5c7ff09b676feccce1e0627823d54399ddc60a42c51cb760c2ab2e",
        "CRB_SUBMISSION_REGISTRY_REMOTE.json": "d76a9257a6c9ecc6bff64492cbe540aac8f3bcb65844d96d05a86b120593e268",
        "CRB_SUBMISSION_RECORD_REMOTE.json": "fac76b406752a4e8b0a09d7116306f018751f09593506a1eeeb355f1b60b7f2a",
    }
    for name, digest in expected.items():
        assert sha256(name) == digest
        assert digest in remote


def test_scheduler_failure_and_exact_exception_are_preserved() -> None:
    accounting = (JOB_DIR / "SACCT_RAW.txt").read_text(encoding="utf-8").splitlines()
    row = accounting[1].split("|")
    header = accounting[0].split("|")
    values = dict(zip(header, row, strict=True))
    assert values["JobIDRaw"] == "3544056"
    assert values["State"] == "FAILED"
    assert values["ExitCode"] == "1:0"
    assert values["Elapsed"] == "08:08:42"
    assert values["AllocCPUS"] == "48"
    assert values["NodeList"] == "cx08"
    stderr = (JOB_DIR / "SLURM_STDERR.txt").read_text(encoding="utf-8")
    assert "build_generation_receipt" in stderr
    assert "TypeError: value is not canonical JSON: float" in stderr
    stdout = (JOB_DIR / "SLURM_STDOUT.txt").read_text(encoding="utf-8")
    assert "external checker built at 2e3b2dc0ecf938addbd779d42877b6ed69d9a985" in stdout
    assert "census generated: 98622 + 230983 records" not in stdout
    assert "external DRUP batch verified" not in stdout


def test_consumed_key_and_commit_boundary_are_exact() -> None:
    registry = load_json("CRB_SUBMISSION_REGISTRY_REMOTE.json")
    record = load_json("CRB_SUBMISSION_RECORD_REMOTE.json")
    entries = [row for row in registry["submissions"] if row["nonduplication_key"] == KEY]
    assert entries == [
        {
            "authorized_commit": "2273e7a6936180bce50fb5caf446c4ae5d21b549",
            "job_id": 3544056,
            "nonduplication_key": KEY,
            "submitted_at_utc": "2026-08-26T23:51:28Z",
        }
    ]
    assert record["job_id"] == 3544056
    assert record["authorized_commit"] == entries[0]["authorized_commit"]
    assert record["nonduplication_key"] == KEY
    identity = load_json("SOURCE_IDENTITY.json")
    assert identity["nonduplication_key_matches_packet"] is True
    assert identity["interpretation"] == {
        "current_root_authorized_commit_executed": False,
        "exact_current_root_replay_authority": "CANNOT_CHECK",
        "same_core_scientific_engine_authorization_and_submission_blobs": True,
        "same_nonduplication_subject_key": True,
        "same_replay_source_manifest": False,
    }


def test_failure_receipt_enforces_claim_ceiling() -> None:
    receipt = load_json("POST_EXECUTION_FAILURE_RECEIPT.json")
    assert (JOB_DIR / "TERMINAL.txt").read_text(encoding="utf-8") == TERMINAL + "\n"
    assert receipt["terminal"] == TERMINAL
    assert receipt["submission_identity"]["attempt_budget_consumed_for_nonduplication_key"] is True
    assert receipt["phase_status"]["phase_2_per_record_sat_execution"] == "NOT_RUN"
    assert receipt["phase_status"]["phase_3_external_drup_verification"] == "NOT_RUN"
    assert receipt["phase_status"]["positive_witness_independent_evaluation"] == "NOT_RUN"
    assert receipt["phase_status"]["durable_result_directory"] == "NOT_CREATED"
    assert receipt["authority"] == {
        "d2_numerical_replay_authority": False,
        "d3_numerical_replay_authority": False,
        "d4": "OPEN",
        "external_independence": False,
        "full_census_executed": False,
        "independent_replay_authority": "CANNOT_CHECK",
        "journal_authority": False,
        "paper_authority_delta": "NONE",
        "scientific_authority_delta": "NONE",
    }
    assert receipt["supersession"]["issue_1516_replay_prerequisite"] == "NOT_SATISFIED"
    assert receipt["supersession"]["issue_1522_gate"] == "REMAINS_CLOSED"
    assert receipt["supersession"]["d4_rounds_consumed"] == 0


def test_defect_reproduction_and_local_control_scope_are_explicit() -> None:
    defect = (JOB_DIR / "DEFECT_REPRODUCTION.txt").read_text(encoding="utf-8")
    assert "observed_exception=TypeError: value is not canonical JSON: float" in defect
    assert "integer_control_type=int" in defect
    control = (JOB_DIR / "LOCAL_CONTROL_REPLAY.txt").read_text(encoding="utf-8")
    assert "source_blob=fedeb8d1158331cbd9752ed88d1b09dfe2f16315" in control
    assert "engine_blob=b3640f473337dccb4642ecce7f97f2554233bfba" in control
    assert "70 passed, 3 skipped" in control


def test_sha256_manifest_covers_the_complete_additive_bundle() -> None:
    rows = {}
    for line in (JOB_DIR / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        rows[name] = digest
    actual = {
        path.relative_to(JOB_DIR).as_posix()
        for path in JOB_DIR.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts
    }
    assert set(rows) == actual
    for name, digest in rows.items():
        assert sha256(name) == digest
