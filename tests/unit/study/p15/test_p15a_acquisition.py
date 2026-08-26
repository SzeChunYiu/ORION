from __future__ import annotations

import json
from pathlib import Path

from orion.study.p15.acquisition import (
    BLOCKED_TERMINAL,
    INPUT_DIRECTORY,
    REQUIRED_ARTIFACTS,
    build_acquisition_preflight,
)

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/orion-25-orion-research-harness"


def test_committed_preflight_matches_absent_protected_inputs() -> None:
    committed = json.loads(
        (PAPER / "P15A_ACQUISITION_PREFLIGHT_V1.json").read_text(encoding="utf-8")
    )
    assert committed == build_acquisition_preflight(ROOT)
    assert committed["terminal"] == BLOCKED_TERMINAL
    assert committed["execution_authorized"] is False
    assert committed["missing_artifacts"] == list(REQUIRED_ARTIFACTS)


def test_local_labels_do_not_turn_inputs_into_a_protected_campaign(tmp_path: Path) -> None:
    input_root = tmp_path / INPUT_DIRECTORY
    input_root.mkdir(parents=True)
    for artifact in REQUIRED_ARTIFACTS:
        (input_root / artifact).write_text('{"claims_protected": true}\n', encoding="utf-8")

    preflight = build_acquisition_preflight(tmp_path)
    assert preflight["missing_artifacts"] == []
    assert preflight["trusted_protected_input_verifier_configured"] is False
    assert preflight["protected_inputs_verified"] is False
    assert preflight["execution_authorized"] is False
    assert preflight["terminal"] == BLOCKED_TERMINAL
