from __future__ import annotations

import importlib.util
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

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


def _isolated_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    base_relative = Path("research/revival/p1/confirmatory/v2.2")
    shutil.copytree(ROOT / base_relative, root / base_relative)

    source_paths: set[str] = set()
    for filename in (
        "PRIMARY_WORLD_FREEZE.json",
        "PRIMARY_EXECUTION_FREEZE.json",
        "PRIMARY_EXECUTION_FREEZE_V2.json",
        "PRIMARY_EXECUTION_FREEZE_V3.json",
    ):
        receipt = json.loads((ROOT / base_relative / filename).read_text())
        source_paths.update(receipt["source_sha256"])
    for relative in source_paths:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    return root


def _mutate_v1_and_rebind(
    tmp_path: Path,
    mutate: Callable[[dict], None],
) -> Path:
    root = _isolated_root(tmp_path)
    base = root / "research/revival/p1/confirmatory/v2.2"
    v1_path = base / "PRIMARY_EXECUTION_FREEZE.json"
    amendment_v1_path = base / "EXECUTION_BINDING_AMENDMENT_V1.json"

    v1 = json.loads(v1_path.read_text())
    mutate(v1)
    v1_path.write_text(json.dumps(v1, indent=2, sort_keys=True) + "\n")

    amendment_v1 = json.loads(amendment_v1_path.read_text())
    amendment_v1["old_execution_receipt_sha256"] = hashlib.sha256(
        v1_path.read_bytes()
    ).hexdigest()
    amendment_v1_path.write_text(
        json.dumps(amendment_v1, indent=2, sort_keys=True) + "\n"
    )
    return root


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


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("parent", lambda receipt: receipt.__setitem__("control_parent", "hostile_parent")),
        (
            "statistics",
            lambda receipt: receipt["statistics"].__setitem__(
                "H1_superiority_margin_each_parent", 0.9
            ),
        ),
        (
            "protocol",
            lambda receipt: receipt.__setitem__("protocol_id", "P1.hostile-unrecorded-protocol"),
        ),
        (
            "source-map",
            lambda receipt: receipt["source_sha256"].__setitem__(
                "src/orion/study/p1_causal/necessity_engine.py", "0" * 64
            ),
        ),
    ],
)
def test_v1_v2_may_differ_only_in_world_freeze_binding(
    tmp_path: Path,
    label: str,
    mutate: Callable[[dict], None],
) -> None:
    validator = _load_validator()
    root = _mutate_v1_and_rebind(tmp_path, mutate)

    with pytest.raises(
        validator.AmendmentValidationError,
        match="execution V1/V2 differ outside the world-freeze amendment",
    ):
        validator.validate_amendment_chain(root, _fresh_world_freeze(tmp_path / label))


def test_workflow_correction_preserves_failed_runs_and_authority_boundary() -> None:
    assert CORRECTION_RECEIPT.is_file(), "workflow-correction receipt is missing"
    receipt = json.loads(CORRECTION_RECEIPT.read_text())

    assert receipt["failed_runs_preserved"] == [33144032180, 33144032234]
    assert receipt["mechanistic_cause"] == "VALIDATOR_FLATTENED_PRE_OUTCOME_SOURCE_AMENDMENT_V2"
    assert receipt["authority"]["historical_prospective_order"] == "CANNOT_CHECK"
    assert receipt["authority"]["freeze_authorized"] is False
    assert receipt["authority"]["submission_authorized"] is False
