from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts/check_orion_v1_freeze.py"
PACKAGE = Path("research/orion-v1-freeze")
MANIFEST = PACKAGE / "V1_FREEZE_MANIFEST_V1.json"



def _load_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location("orion_v1_freeze_checker", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = _load_checker()
ValidationError = CHECKER.ValidationError
FIXED = [Path(p) for p in sorted(CHECKER.FIXED)]


def _copy_control_plane(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / PACKAGE, target / PACKAGE)
    for relative in FIXED:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / relative, destination)
    return target


def _read_json(root: Path, relative: Path) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _write_json(root: Path, relative: Path, value: dict[str, Any]) -> None:
    (root / relative).write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _rehash(root: Path, *relative_paths: Path) -> None:
    manifest = _read_json(root, MANIFEST)
    rows = {row["path"]: row for row in manifest["files"]}
    for relative in relative_paths:
        content = (root / relative).read_bytes()
        row = rows[relative.as_posix()]
        row["sha256"] = hashlib.sha256(content).hexdigest()
        row["bytes"] = len(content)
    _write_json(root, MANIFEST, manifest)


def test_bootstrap_package_validates() -> None:
    summary = CHECKER.validate(REPO_ROOT)
    assert summary["checker_terminal"] == "ORION_V1_FREEZE_BOOTSTRAP_GREEN"
    assert summary["scientific_terminal"] == "NOT_EARNED"
    assert summary["counts"] == {
        "components": 14,
        "theorem_authority_rows": 10,
        "issues": 159,
        "pending_issue_audits": 0,
        "jobs": 8,
        "gaps": 9,
        "open_internal_gaps": 5,
        "external_blockers": 3,
        "paper_candidates": 3,
        "manifest_files": 15,
    }


def test_component_cycle_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "V1_COMPONENT_GRAPH_V1.json"
    data = _read_json(root, relative)
    first = next(row for row in data["nodes"] if row["id"] == "OSTC_FOUNDATIONS")
    first["depends_on"] = ["V1_FREEZE_CONTROL_PLANE"]
    _write_json(root, relative, data)
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="contains a cycle"):
        CHECKER.validate(root)


def test_unknown_issue_disposition_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "V1_ISSUE_DISPOSITION_LEDGER_V1.json"
    data = _read_json(root, relative)
    data["entries"][0]["disposition"] = "CLAIMED_SOLVED_BY_ASSERTION"
    _write_json(root, relative, data)
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="invalid disposition"):
        CHECKER.validate(root)


def test_issue_denominator_drift_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "V1_ISSUE_DISPOSITION_LEDGER_V1.json"
    data = _read_json(root, relative)
    data["coverage"]["known_entries"] -= 1
    _write_json(root, relative, data)
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="known_entries denominator mismatch"):
        CHECKER.validate(root)


def test_missing_execution_packet_member_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "V1_EXECUTION_JOB_LEDGER_V1.json"
    data = _read_json(root, relative)
    data["jobs"][0]["required_outputs"].remove("TRANSFER_RESULT")
    _write_json(root, relative, data)
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="exact eight-file packet required"):
        CHECKER.validate(root)


def test_premature_manuscript_authorization_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "V1_PAPER_CANDIDATE_GATE_V1.json"
    data = _read_json(root, relative)
    data["candidates"][0]["status"] = "MANUSCRIPT_AUTHORIZED"
    _write_json(root, relative, data)
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="manuscript authorization is premature"):
        CHECKER.validate(root)


def test_quantum_advantage_overclaim_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "ORION_V1_FREEZE_CONTRACT_V1.json"
    data = _read_json(root, relative)
    data["authority_ceiling"]["quantum_advantage"] = "QUANTUM_ADVANTAGE_SUPPORTED"
    _write_json(root, relative, data)
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="cannot grant quantum advantage"):
        CHECKER.validate(root)


def test_forged_final_terminal_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    contract_path = PACKAGE / "ORION_V1_FREEZE_CONTRACT_V1.json"
    component_path = PACKAGE / "V1_COMPONENT_GRAPH_V1.json"
    theorem_path = PACKAGE / "V1_THEOREM_AUTHORITY_LEDGER_V1.json"

    contract = _read_json(root, contract_path)
    contract["freeze_state"] = "FROZEN"
    contract["terminal"] = "ORION_V1_ARCHITECTURE_AND_LOCAL_FORMALISM_FROZEN"
    contract["terminal_requirements"] = {
        "architecture_and_local_formalism_frozen": True,
        "internal_implementation_gaps_zero": True,
        "unclassified_open_issues_zero": True,
        "external_or_heavy_blockers_explicitly_ledgered": True,
        "all_manifest_digests_valid": True,
        "paper_authority_delta": "NONE",
    }
    _write_json(root, contract_path, contract)

    components = _read_json(root, component_path)
    next(row for row in components["nodes"] if row["id"] == "V1_FREEZE_CONTROL_PLANE")["status"] = "FROZEN"
    _write_json(root, component_path, components)

    theorems = _read_json(root, theorem_path)
    next(row for row in theorems["entries"] if row["id"] == "V1-AUTH-FREEZE")["status"] = "ORION_V1_ARCHITECTURE_AND_LOCAL_FORMALISM_FROZEN"
    _write_json(root, theorem_path, theorems)

    _rehash(root, contract_path, component_path, theorem_path)
    with pytest.raises(ValidationError, match="terminal requirements do not equal checker-derived"):
        CHECKER.validate(root)


def test_unmanifested_byte_change_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "README.md"
    with (root / relative).open("a", encoding="utf-8") as handle:
        handle.write("\nunauthorized byte drift\n")
    with pytest.raises(ValidationError, match="manifest digest drift"):
        CHECKER.validate(root)


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "ORION_V1_FREEZE_CONTRACT_V1.json"
    original = (root / relative).read_text(encoding="utf-8")
    (root / relative).write_text('{"schema": "forged",' + original[1:], encoding="utf-8")
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="duplicate JSON key: schema"):
        CHECKER.validate(root)


def test_external_blocker_laundering_is_rejected(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "V1_EXECUTION_GAP_LEDGER_V1.json"
    data = _read_json(root, relative)
    row = next(item for item in data["gaps"] if item["class"] == "EXTERNAL_AUTHORITY")
    row["status"] = "CLOSED"
    _write_json(root, relative, data)
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="status must be CANNOT_CHECK"):
        CHECKER.validate(root)


def test_p18_negative_twin_gate_cannot_be_dropped(tmp_path: Path) -> None:
    root = _copy_control_plane(tmp_path)
    relative = PACKAGE / "V1_PAPER_CANDIDATE_GATE_V1.json"
    data = _read_json(root, relative)
    row = next(item for item in data["candidates"] if item["paper_id"] == "P18")
    row["minimum_internal_prerequisites"] = [
        item for item in row["minimum_internal_prerequisites"] if "negative twin" not in item
    ]
    _write_json(root, relative, data)
    _rehash(root, relative)
    with pytest.raises(ValidationError, match="P18 gate missing: negative twin"):
        CHECKER.validate(root)
