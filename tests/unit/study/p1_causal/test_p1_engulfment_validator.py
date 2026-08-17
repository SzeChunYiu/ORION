from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P1 = ROOT / "research" / "revival" / "p1"
CHECKER = P1 / "check_p1_engulfment.py"
COVERAGE = P1 / "P1_DONOR_ASSIMILATION_COVERAGE_V1.json"
ENGULFMENT = P1 / "P1_DONOR_ENGULFMENT_V1.json"

_spec = importlib.util.spec_from_file_location("p1_engulfment_checker", CHECKER)
assert _spec is not None and _spec.loader is not None
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def _payloads():
    return json.loads(COVERAGE.read_text()), json.loads(ENGULFMENT.read_text())


def test_committed_engulfment_is_complete() -> None:
    coverage, engulfment = _payloads()
    assert checker.validate_engulfment(coverage, engulfment) == ()


def test_adopted_donor_cannot_be_downgraded_to_watchlist() -> None:
    coverage, engulfment = _payloads()
    mutated = copy.deepcopy(engulfment)
    component = next(
        item
        for item in mutated["components"]
        if "P1-NW-005" in item["matrix_rows"]
    )
    component["integration_mode"] = "DEFERRED_WATCHLIST"
    errors = checker.validate_engulfment(coverage, mutated)
    assert "active_donor_not_integrated:P1-NW-005:DEFERRED_WATCHLIST" in errors


def test_matrix_row_cannot_disappear_after_novelty_strike() -> None:
    coverage, engulfment = _payloads()
    mutated = copy.deepcopy(engulfment)
    for component in mutated["components"]:
        if "P1-NW-009" in component["matrix_rows"]:
            component["matrix_rows"].remove("P1-NW-009")
            break
    errors = checker.validate_engulfment(coverage, mutated)
    assert "unengulfed_matrix_row:P1-NW-009" in errors


def test_rejected_source_cannot_become_executable_substrate() -> None:
    coverage, engulfment = _payloads()
    mutated = copy.deepcopy(engulfment)
    component = next(
        item
        for item in mutated["components"]
        if "P1-NW-031" in item["matrix_rows"]
    )
    component["integration_mode"] = "EXECUTABLE_SUBSTRATE"
    errors = checker.validate_engulfment(coverage, mutated)
    assert "rejected_donor_granted_wrong_mode:P1-NW-031:EXECUTABLE_SUBSTRATE" in errors
