from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P1X = ROOT / "research" / "claim_expansion" / "p1"
V2 = P1X / "v2"
for path in (str(P1X), str(V2)):
    if path not in sys.path:
        sys.path.insert(0, path)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dev = _load("p1x_dev_v2_preflight", P1X / "generate_p1_x_dev_cases.py")
v2 = _load("p1x_execution_v2_preflight", V2 / "p1_x_execution_v2.py")


def test_v2_fix_restores_clean_no_change_for_b1_b2() -> None:
    controls = [case for case in dev.generate_dev_cases() if case["protected_gold"]["correct_terminal"] == "NO_CHANGE"]
    assert controls
    for case in controls:
        assert v2.run_arm_v2(case, "B1_DONOR_COMPLETE_GREEDY")["terminal"] == "NO_CHANGE"
        assert v2.run_arm_v2(case, "B2_SUCCESS_AUTHORIZES_REFRAME")["terminal"] == "NO_CHANGE"


def test_v2_p1x_and_b3_still_tie_exactly_on_all_dev_cases() -> None:
    for case in dev.generate_dev_cases():
        p1x = v2.run_arm_v2(case, "P1X_MINIMAL_SCIENTIFIC_ESCALATION")
        b3 = v2.run_arm_v2(case, "B3_IDEAL_TYPED_PRODUCT")
        assert p1x == b3
        assert v2.score_esrd(case, p1x) == 1


def test_v2_primary_baseline_is_nontrivial_on_dev() -> None:
    cases = dev.generate_dev_cases()
    b1 = sum(v2.score_esrd(case, v2.run_arm_v2(case, "B1_DONOR_COMPLETE_GREEDY")) for case in cases)
    b2 = sum(v2.score_esrd(case, v2.run_arm_v2(case, "B2_SUCCESS_AUTHORIZES_REFRAME")) for case in cases)
    assert 0 < b1 < len(cases)
    assert 0 < b2 < len(cases)
    assert b1 > b2


def test_v2_changes_only_b1_b2_arm_implementations() -> None:
    assert v2.ARM_FUNCTIONS_V2["P1X_MINIMAL_SCIENTIFIC_ESCALATION"] is v2.v1.decide_p1x
    assert v2.ARM_FUNCTIONS_V2["B3_IDEAL_TYPED_PRODUCT"] is v2.v1.decide_b3_ideal_typed_product
