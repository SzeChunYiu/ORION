from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
Q1 = ROOT / "papers" / "five-paper-top-tier-r8" / "Q1"
CHECK = Q1 / "check_q1_c_authority_r9.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("q1c_check", CHECK)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(name: str):
    return json.loads((Q1 / name).read_text(encoding="utf-8"))


def test_q1_c_bundle_passes_fail_closed_checker():
    done = subprocess.run(["python", str(CHECK)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert done.returncode == 0, done.stderr
    receipt = json.loads(done.stdout)
    assert receipt == {
        "binding_terminal": "Q1_C_INPUTS_CONTENT_BOUND__PORTFOLIO_AUTHORITY_BINDING_STILL_REQUIRED",
        "journal_authority": False,
        "literature_terminal": "NOVELTY_NOT_ESTABLISHED",
        "ok": True,
        "resource_terminal": "PARTIAL_RESOURCE_MAP",
        "schema": "ORION.Q1C.AuthorityCheckR9.v1",
    }


def test_resource_map_rejects_unearned_faithful_terminal():
    check = load_checker()
    value = load("Q1_C_PRODUCTION_RESOURCE_MAP_R9.json")
    value["production_headline"]["terminal"] = "FAITHFUL_RESOURCE_MAP"
    with pytest.raises(AssertionError):
        check.validate_resource(ROOT, value)


def test_literature_rejects_unearned_novelty_authority():
    check = load_checker()
    value = load("Q1_C_CURRENT_LITERATURE_SUBTRACTION_R9.json")
    value["authority"]["grants_external_novelty_authority"] = True
    with pytest.raises(AssertionError):
        check.validate_literature(ROOT, value)


def test_literature_preserves_source_specific_subtraction_and_cannot_check():
    value = load("Q1_C_CURRENT_LITERATURE_SUBTRACTION_R9.json")
    source_ids = {row["source_id"] for row in value["nearest_work_rows"]}
    assert {"TARE-v4", "SYMPHONY-v2", "LI-SPARSE-v1", "HARVEST-v1", "FTCIRCUITBENCH-v1"} <= source_ids
    assert value["subtraction_summary"]["novelty_established"] is False
    assert len(value["cannot_check"]) >= 6


def test_production_map_preserves_adverse_and_unmapped_metrics():
    value = load("Q1_C_PRODUCTION_RESOURCE_MAP_R9.json")
    assert "donor-exact" in value["internal_crosscheck"]["adverse_result_preserved"]
    unmapped = {row["metric"]: row["status"] for row in value["unmapped_metrics"]}
    assert unmapped["T count / magic states"] == "NO_DIRECT_MAP"
    assert unmapped["fault-tolerant spacetime volume and failure probability"] == "CANNOT_CHECK"
