from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P2X = ROOT / "research" / "claim_expansion" / "p2"
if str(P2X) not in sys.path:
    sys.path.insert(0, str(P2X))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


analysis = _load("p2x_analysis_bound", P2X / "analyze_p2_x_protected.py")
verifier = _load("p2x_independent_bound", P2X / "verify_p2_x_independent.py")


def test_committed_p2_x_headline_reproduces() -> None:
    committed = json.loads((P2X / "P2_X_PROTECTED_RESULT_V1.json").read_text())
    live = analysis.analyze()
    assert live["terminal"] == committed["terminal"]
    assert live["arm_escd"] == committed["arm_escd"]
    assert live["primary"]["difference"] == committed["primary"]["difference"]
    assert live["primary"]["bootstrap_95ci"] == committed["primary"]["bootstrap_95ci"]
    assert live["primary"]["mcnemar"]["b_left_only_correct"] == committed["primary"]["mcnemar"]["b_p2x_only_correct"]
    assert live["primary"]["mcnemar"]["c_right_only_correct"] == committed["primary"]["mcnemar"]["c_b1_only_correct"]
    assert live["b3_equivalence"] == committed["b3_equivalence"]
    assert live["non_regression"]["all_pass"] is True


def test_independent_verifier_matches_all_bound_receipts() -> None:
    result = verifier.verify()
    assert result["ok"] is True
    assert result["terminal"] == "P2_X_INDEPENDENT_VERIFICATION_PASS"
    assert result["arm_correct"] == {
        "P2X_FAIL_CLOSED_ROUTE_AUTHORITY": 400,
        "B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT": 250,
        "B2_GLOBAL_SUFFICIENCY_AGGREGATOR": 100,
        "B3_IDEAL_TYPED_ROUTE_PRODUCT": 400,
    }
    assert result["b3_decision_mismatches"] == 0
