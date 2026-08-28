from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
VALIDATOR = (
    ROOT
    / "research"
    / "revival"
    / "p1"
    / "validate_mutation_necessity_amendment_chain.py"
)
FREEZER = ROOT / "research" / "revival" / "p1" / "freeze_mutation_necessity_worlds.py"
CORRECTION_RECEIPT = (
    ROOT
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "revival"
    / "r1-negative-revival-audit"
    / "R3_DEDICATED_WORKFLOW_CORRECTION_20260828.json"
)


def _load_validator():
    assert VALIDATOR.is_file(), "amendment-chain validator is missing"
    spec = importlib.util.spec_from_file_location("p1_amendment_chain", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fresh_world_freeze(tmp_path: Path) -> Path:
    outdir = tmp_path / "worlds"
    subprocess.run(
        [sys.executable, str(FREEZER), "--outdir", str(outdir)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return outdir / "WORLD_FREEZE.json"


def test_current_pre_outcome_source_amendment_chain_is_explicit(tmp_path: Path) -> None:
    validator = _load_validator()
    receipt = validator.validate_amendment_chain(ROOT, _fresh_world_freeze(tmp_path))

    assert receipt["status"] == "AMENDMENT_CHAIN_VALID"
    assert receipt["world_rows_changed"] is False
    assert receipt["source_change_count"] == 2
    assert receipt["authority"]["scientific_authority_delta"] == "NONE"
    assert receipt["authority"]["freeze_authorized"] is False


def test_unrecorded_fresh_source_drift_is_rejected(tmp_path: Path) -> None:
    validator = _load_validator()
    fresh_path = _fresh_world_freeze(tmp_path)
    payload = json.loads(fresh_path.read_text())
    payload["source_sha256"]["src/orion/study/p1_causal/necessity_engine.py"] = "0" * 64
    fresh_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    with pytest.raises(
        validator.AmendmentValidationError,
        match="fresh world source mismatch",
    ):
        validator.validate_amendment_chain(ROOT, fresh_path)


def test_fresh_world_geometry_drift_is_rejected(tmp_path: Path) -> None:
    validator = _load_validator()
    fresh_path = _fresh_world_freeze(tmp_path)
    payload = json.loads(fresh_path.read_text())
    payload["by_family"]["hidden_representation_formulation"] += 1
    fresh_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    with pytest.raises(
        validator.AmendmentValidationError,
        match="fresh world identity drift: by_family",
    ):
        validator.validate_amendment_chain(ROOT, fresh_path)


def test_workflow_correction_preserves_failed_runs_and_authority_boundary() -> None:
    assert CORRECTION_RECEIPT.is_file(), "workflow-correction receipt is missing"
    receipt = json.loads(CORRECTION_RECEIPT.read_text())

    assert receipt["failed_runs_preserved"] == [33144032180, 33144032234]
    assert receipt["mechanistic_cause"] == "VALIDATOR_FLATTENED_PRE_OUTCOME_SOURCE_AMENDMENT_V2"
    assert receipt["authority"]["historical_prospective_order"] == "CANNOT_CHECK"
    assert receipt["authority"]["freeze_authorized"] is False
    assert receipt["authority"]["submission_authorized"] is False
