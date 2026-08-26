from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts/audit_p1_p15_result_identities_v1.py"
LEDGER = REPO_ROOT / "papers/P1_P15_RESULT_BOUND_CLAIM_LEDGER_V1.json"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("p1_p15_identity_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = _load_module()


def _green_row() -> dict[str, object]:
    return {
        "commit_object_exists": True,
        "ancestor_of_integration": True,
        "ancestor_of_subject": True,
        "result_subtree_oid_commit": "a" * 40,
        "result_subtree_stable": True,
        "result_commit_touches_expected_subtree": True,
        "protected_writing_path_violations": [],
        "packet_blob_stable": True,
        "packet_job_id_matches": True,
        "packet_terminal_matches": True,
        "packet_authority_boundary_valid": True,
        "binding_errors": [],
    }


def test_current_writing_ledger_has_exact_25_unique_rows() -> None:
    ledger = AUDIT.load_json_bytes(LEDGER.read_bytes(), str(LEDGER))
    rows = AUDIT.validate_ledger_shape(ledger)
    assert len(rows) == 25
    assert len({row["job_id"] for row in rows}) == 25
    assert len({row["sha"] for row in rows}) == 25
    assert {row["paper"] for row in rows if row["ledger_section"] == "papers"} == {
        f"P{number}" for number in range(1, 16)
    }


def test_duplicate_json_key_is_rejected() -> None:
    with pytest.raises(AUDIT.AuditError, match="duplicate JSON key: schema"):
        AUDIT.load_json_bytes(b'{"schema":"one","schema":"two"}', "hostile")


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ({"commit_object_exists": False}, "IDENTITY_OBJECT_MISSING"),
        ({"ancestor_of_subject": False}, "IDENTITY_ANCESTRY_MISMATCH"),
        ({"result_subtree_oid_commit": None}, "RESULT_SUBTREE_MISSING_AT_LEDGER_COMMIT"),
        ({"result_subtree_stable": False}, "RESULT_SUBTREE_DRIFT"),
        (
            {"result_commit_touches_expected_subtree": False},
            "INTENDED_COMMIT_RESULT_RELATIONSHIP_MISSING",
        ),
        (
            {"protected_writing_path_violations": ["papers/manuscript.tex"]},
            "WRITING_BOUNDARY_VIOLATION",
        ),
        ({"packet_blob_stable": False}, "RESULT_BINDING_PACKET_DRIFT"),
        ({"packet_job_id_matches": False}, "RESULT_BINDING_PACKET_JOB_MISMATCH"),
        (
            {"packet_terminal_matches": False},
            "RESULT_BINDING_PACKET_TERMINAL_MISMATCH",
        ),
        (
            {"packet_authority_boundary_valid": False},
            "RESULT_BINDING_PACKET_AUTHORITY_MISMATCH",
        ),
        (
            {"binding_errors": ["forged bytes"]},
            "RESULT_ARTIFACT_BINDING_MISMATCH",
        ),
    ],
)
def test_every_hostile_identity_mutation_fails_closed(
    mutation: dict[str, object], expected: str
) -> None:
    row = _green_row()
    row.update(mutation)
    assert AUDIT.classify_row(row) == expected


def test_complete_row_has_identity_only_terminal() -> None:
    assert (
        AUDIT.classify_row(_green_row())
        == "IDENTITY_BOUND_BYTES_VERIFIED_NO_RERUN_AUTHORITY"
    )


@pytest.mark.parametrize(
    "job_id",
    [
        "DES-UPDATE-01",
        "DES-DONOR-FRONTIER-01",
        "P1-DES-01",
        "P15-DES-01",
    ],
)
def test_expected_job_ids_map_only_below_result_root(job_id: str) -> None:
    assert AUDIT.safe_result_dir(job_id).as_posix() == (
        f"research/orion-epistemic-state-v1/results/{job_id}"
    )


@pytest.mark.parametrize(
    "job_id",
    ["../P1-DES-01", "P0-DES-01", "P16-DES-01", "DES/update", ""],
)
def test_unsafe_or_out_of_denominator_job_ids_are_rejected(job_id: str) -> None:
    with pytest.raises(AUDIT.AuditError):
        AUDIT.safe_result_dir(job_id)


def test_protected_writing_path_detection_is_narrow_and_explicit() -> None:
    paths = [
        "research/orion-epistemic-state-v1/results/P1-DES-01/PRIMARY_RESULT_V1.json",
        "scripts/helper.py",
        "papers/paper-01/manuscript/main.tex",
        "research/example/ACTIVE_CLAIM_AUTHORITY_V1.json",
    ]
    assert AUDIT.protected_writing_paths(paths) == [
        "papers/paper-01/manuscript/main.tex",
        "research/example/ACTIVE_CLAIM_AUTHORITY_V1.json",
    ]


def test_binding_packet_declares_no_scientific_rerun_by_construction(tmp_path: Path) -> None:
    summary = {
        "scientific_rerun_performed": False,
        "paper_authority_delta": "NONE",
        "external_validation": "CANNOT_CHECK",
        "top_tier_readiness": "NOT_GRANTED",
    }
    record = AUDIT.write_json(tmp_path / "SUMMARY.json", summary)
    assert record["bytes"] == len((tmp_path / "SUMMARY.json").read_bytes())
    assert len(record["sha256"]) == 64
    assert json.loads((tmp_path / "SUMMARY.json").read_text()) == summary
