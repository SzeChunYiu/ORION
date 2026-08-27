from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/verify_orion11_negative_revival_v1.py"


def _run(tmp_path: Path) -> dict:
    out = tmp_path / "receipt.json"
    run = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(ROOT), "--out", str(out)],
        text=True,
        capture_output=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    return json.loads(out.read_text())


def _load_module():
    spec = importlib.util.spec_from_file_location("orion11_revival_audit", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_preserves_all_four_negative_classes_without_freeze_authority(tmp_path: Path) -> None:
    receipt = _run(tmp_path)

    assert receipt["audit_passed"] is True
    assert receipt["historical_broad_h1"] == {
        "baseline_root_success": "1/48",
        "comparator_system_id": "arex_like_recursive_audit_followup",
        "difference": 0.0,
        "subject_root_success": "1/48",
        "terminal": "NOT_SUPPORTED",
    }

    necessity = receipt["necessity_v2_2_4"]
    assert necessity["primary"]["n_worlds"] == 2882
    assert necessity["primary"]["n_score_rows"] == 40348
    assert necessity["primary"]["terminal"] == "P1_MUTATION_NECESSITY_SUPPORTED"
    assert necessity["replication"]["n_worlds"] == 2882
    assert necessity["replication"]["n_score_rows"] == 40348
    assert necessity["replication"]["terminal"] == "P1_MUTATION_NECESSITY_SUPPORTED"
    assert necessity["task_id_intersection_count"] == 0
    assert necessity["historical_prospective_order"]["status"] == "CANNOT_CHECK_HISTORICAL_PROSPECTIVE_ORDER"
    assert len(necessity["historical_prospective_order"]["missing_commits"]) == 3

    adapters = receipt["adapter_maps"]
    assert adapters["enumeration"] == {
        "fully_certified": 0,
        "known_rejected": 116929,
        "not_disproved_but_uncertified": 720,
        "total": 117649,
    }
    assert adapters["registry_exact_match"] is True
    assert adapters["in_repo_reauditable"] == 720
    assert adapters["in_repo_resolvable"] == 0
    assert adapters["externally_blocked"] == 720
    assert adapters["setup_failure_count"] == 0
    assert adapters["terminal"] == "CANNOT_CHECK_EXTERNAL_OWNER_ALGEBRA"

    assert receipt["rse_donor_subtraction"]["terminal"] == "GENERIC_JUSTIFICATION_DONOR_SUFFICIENT"
    assert receipt["freeze_authority"] == "NONE__DO_NOT_FREEZE_OR_MERGE"


def test_duplicate_adapter_registry_row_is_rejected() -> None:
    module = _load_module()
    adapter_dir = ROOT / "development/p1-source-native-target-semantics-v8-2026-08-23"
    adjudication = json.loads((adapter_dir / "P1_V8_ADAPTER_ADJUDICATION_RESULT.json").read_text())
    registry = json.loads((adapter_dir / "P1_V8_720_ADAPTER_REGISTRY.json").read_text())
    registry["rows"][1] = registry["rows"][0]
    try:
        module.audit_adapter_payloads(adjudication, registry)
    except module.AuditError as exc:
        assert "registry" in str(exc).lower()
    else:
        raise AssertionError("duplicate adapter row was accepted")


def test_manifest_drift_is_rejected(tmp_path: Path) -> None:
    module = _load_module()
    source = ROOT / "research/revival/p1/confirmatory/v2.2/primary"
    copied = tmp_path / "primary"
    copied.mkdir()
    for name in ["SHA256SUMS", "PRIMARY_RESULT.json"]:
        (copied / name).write_bytes((source / name).read_bytes())
    (copied / "PRIMARY_RESULT.json").write_text("{}\n")
    try:
        module.verify_manifest(copied / "SHA256SUMS", allow_missing=False)
    except module.AuditError as exc:
        assert "manifest" in str(exc).lower()
    else:
        raise AssertionError("manifest drift was accepted")
