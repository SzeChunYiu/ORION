from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

RUNNER = Path(__file__).with_name("run_p11_des_01.py")
SPEC = importlib.util.spec_from_file_location("p11_des_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_absent_manifest_is_cannot_check(tmp_path: Path) -> None:
    req = {"id": "DATA", "manifest": "data.json"}
    row = MODULE.audit_requirement(tmp_path, req)
    assert row["status"] == "CANNOT_CHECK"
    assert row["reason"] == "MANIFEST_ABSENT"


def test_content_bound_objects_are_verified(tmp_path: Path) -> None:
    obj = tmp_path / "objects" / "one.bin"
    obj.parent.mkdir()
    obj.write_bytes(b"frozen\n")
    manifest = {
        "schema": "orion.external-content-binding.v1",
        "requirement_id": "MODELS",
        "objects": [
            {
                "path": "objects/one.bin",
                "bytes": obj.stat().st_size,
                "sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
                "family_id": "family-one",
            }
        ],
    }
    (tmp_path / "models.json").write_text(json.dumps(manifest))
    row = MODULE.audit_requirement(
        tmp_path,
        {"id": "MODELS", "manifest": "models.json", "minimum_distinct_families": 1},
    )
    assert row["status"] == "BOUND"
    assert row["verified_objects"] == 1


def test_positive_terminal_is_not_reachable_from_zero_cases() -> None:
    assert MODULE.TERMINAL == "P11_DATASETS_MODELS_TRANSCRIPTS_NOT_CONTENT_BOUND"
    assert "ZERO_SCIENTIFIC_CASES_EXECUTED" in MODULE.CEILING
