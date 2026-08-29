"""Hostile tests for the ORION-01–25 atomic science-gap ledger."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "check_top_tier_atomic_gap_ledger_v2.py"
LEDGER = (
    ROOT
    / "papers"
    / "publication_closure"
    / "TOP_TIER_ATOMIC_GAP_LEDGER_V2.json"
)

SPEC = importlib.util.spec_from_file_location("top_tier_atomic_gap_checker", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def _data() -> dict[str, Any]:
    return CHECKER.load_ledger(LEDGER)


def _paper(data: dict[str, Any], paper_id: str) -> dict[str, Any]:
    return next(row for row in data["papers"] if row["paper_id"] == paper_id)


def _replace_everywhere(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [_replace_everywhere(item, old, new) for item in value]
    if isinstance(value, dict):
        return {
            key: _replace_everywhere(item, old, new)
            for key, item in value.items()
        }
    return value


def test_live_ledger_passes() -> None:
    assert CHECKER.validate_ledger(_data()) == []


def test_cli_passes_on_live_ledger() -> None:
    assert CHECKER.main(["--ledger", str(LEDGER)]) == CHECKER.EXIT_PASS


def test_authority_delta_cannot_be_promoted_by_prose() -> None:
    data = _data()
    data["scientific_authority_delta"] = "TOP_TIER"
    errors = CHECKER.validate_ledger(data)
    assert any("scientific_authority_delta" in error for error in errors)


def test_erasing_orion11_retraction_history_fails() -> None:
    data = _data()
    row = _paper(data, "ORION-11")
    for marker in ("R4", "Active-VOI", "retract"):
        row = _replace_everywhere(row, marker, "REMOVED")
    index = next(
        index
        for index, candidate in enumerate(data["papers"])
        if candidate["paper_id"] == "ORION-11"
    )
    data["papers"][index] = row
    errors = CHECKER.validate_ledger(data)
    assert any("ORION-11: missing load-bearing marker" in error for error in errors)


def test_e14_cannot_be_reused_as_fresh_orion17_evidence() -> None:
    data = _data()
    _paper(data, "ORION-17")["external_sources"].append("E14")
    errors = CHECKER.validate_ledger(data)
    assert any("E14 may not be fresh external evidence" in error for error in errors)


def test_orion17_active_lane_collision_guard_is_mandatory() -> None:
    data = _data()
    _paper(data, "ORION-17")["active_lane"]["reference"] = "unowned"
    errors = CHECKER.validate_ledger(data)
    assert any("ORION-17: active lane must reference #1730" in error for error in errors)


def test_all_25_paper_identities_are_required_and_ordered() -> None:
    data = _data()
    data["papers"][24]["paper_id"] = "ORION-24"
    errors = CHECKER.validate_ledger(data)
    assert any("ordered ORION-01 through ORION-25" in error for error in errors)


def test_success_refutation_and_cannot_check_must_not_collapse() -> None:
    data = _data()
    row = _paper(data, "ORION-03")
    row["refutation_gate"] = row["success_gate"]
    errors = CHECKER.validate_ledger(data)
    assert any("gates must differ" in error for error in errors)


def test_orion07_temporal_freeze_cannot_be_accelerated() -> None:
    data = _data()
    _paper(data, "ORION-07")["protocol_state"] = "EXECUTE_NOW"
    errors = CHECKER.validate_ledger(data)
    assert any("ORION-07 must remain FROZEN_DO_NOT_TOUCH" in error for error in errors)


def test_result_artifact_cannot_masquerade_as_next_design_step() -> None:
    data = _data()
    _paper(data, "ORION-20")["next_artifact"] = (
        "papers/orion-20-structured-problem-solving/top_tier/RESULT.json"
    )
    errors = CHECKER.validate_ledger(data)
    assert any("pre-outcome design/traceability" in error for error in errors)


def test_earned_top_tier_terminal_is_forbidden() -> None:
    data = _data()
    _paper(data, "ORION-25")["current_ceiling"] = "TOP_TIER_SUCCESSOR_EARNED"
    errors = CHECKER.validate_ledger(data)
    assert any("cannot assert an earned top-tier successor" in error for error in errors)


def test_orion02_paired_correction_cannot_be_dropped() -> None:
    data = _data()
    row = _paper(data, "ORION-02")
    row = _replace_everywhere(row, "paired", "separate")
    row = _replace_everywhere(row, "Paired", "Separate")
    index = next(
        index
        for index, candidate in enumerate(data["papers"])
        if candidate["paper_id"] == "ORION-02"
    )
    data["papers"][index] = row
    errors = CHECKER.validate_ledger(data)
    assert any("ORION-02: missing load-bearing marker 'paired'" in error for error in errors)


def test_missing_open_pr_guard_fails() -> None:
    data = _data()
    data["open_pr_collision_guards"] = [
        guard for guard in data["open_pr_collision_guards"] if guard["pr"] != 1695
    ]
    errors = CHECKER.validate_ledger(data)
    assert any("missing open-PR collision guard #1695" in error for error in errors)


def test_missing_shard_fails_closed(tmp_path: Path) -> None:
    manifest = json.loads(LEDGER.read_text(encoding="utf-8"))
    manifest_path = tmp_path / "TOP_TIER_ATOMIC_GAP_LEDGER_V2.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert CHECKER.main(["--ledger", str(manifest_path)]) == CHECKER.EXIT_FAIL
