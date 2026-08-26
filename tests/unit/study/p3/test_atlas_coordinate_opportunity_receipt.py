from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "papers/orion-13-global-knowledge-portrait/measure_atlas_coordinate_opportunity.py"
ARTIFACT = ROOT / (
    "papers/orion-13-global-knowledge-portrait/gold/adjudicated/"
    "public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl"
)
RECEIPT = ROOT / "papers/orion-13-global-knowledge-portrait/evidence/P3_ATLAS_COORDINATE_OPPORTUNITY_2026-08-23.json"


def _module():
    spec = importlib.util.spec_from_file_location("measure_atlas_coordinate_opportunity", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repo_artifact_locator_is_stable_and_relative() -> None:
    module = _module()
    expected = ARTIFACT.relative_to(ROOT).as_posix()
    assert module.REPO_ROOT == ROOT
    assert module.artifact_locator(ARTIFACT) == expected


def test_machine_local_input_has_no_authoritative_locator(tmp_path: Path) -> None:
    module = _module()
    outside = tmp_path / "gold.jsonl"
    outside.write_text("{}\n", encoding="utf-8")
    assert module.artifact_locator(outside) is None


def test_committed_receipt_names_the_repository_artifact() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["artifact"] == ARTIFACT.relative_to(ROOT).as_posix()
    assert not Path(receipt["artifact"]).is_absolute()
    assert receipt["outcome_accessed"] is False
