from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P1X = ROOT / "research" / "claim_expansion" / "p1"
V2 = P1X / "v2"
ARCH = P1X / "architecture"
for path in (str(P1X), str(V2), str(ARCH)):
    if path not in sys.path:
        sys.path.insert(0, path)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


analysis = _load("p1x_v2_analysis_bound", V2 / "analyze_p1_x_v2.py")
architecture = _load("p1x_arch_analysis_bound", ARCH / "run_p1_x_architecture_independence.py")


def test_committed_v2_headline_reproduces_from_frozen_subject() -> None:
    committed = json.loads((V2 / "P1_X_PROTECTED_RESULT_V2.json").read_text())
    live = analysis.analyze()
    assert live["terminal"] == committed["terminal"]
    assert live["arm_esrd"] == committed["arm_esrd"]
    assert live["primary"]["difference"] == committed["primary"]["difference"]
    assert live["primary"]["bootstrap_95ci"] == committed["primary"]["bootstrap_95ci"]
    assert live["primary"]["mcnemar"]["b_left_only_correct"] == committed["primary"]["mcnemar"]["b_p1x_only_correct"]
    assert live["primary"]["mcnemar"]["c_right_only_correct"] == committed["primary"]["mcnemar"]["c_b1_only_correct"]
    assert live["b3_equivalence"] == committed["b3_equivalence"]
    assert live["non_regression"]["all_pass"] is True


def test_committed_architecture_substitution_result_reproduces() -> None:
    committed = json.loads((ARCH / "P1_X_ARCHITECTURE_INDEPENDENCE_RESULT_V1.json").read_text())
    live = architecture.run()
    assert live["terminal"] == committed["terminal"]
    assert live["pass"] is True
    assert live["identity_pairs_sha256"] == committed["identity_pairs_sha256"]
    for name, item in committed["combinations"].items():
        observed = live["combinations"][name]
        assert observed["arm_correct"] == item["arm_correct"]
        assert observed["b3_mismatches"] == 0
        assert observed["p1x_false_high_level_reframes"] == 0
        assert observed["p1x_invariant_violations"] == 0
        assert observed["budget_violations"] == 0
        assert observed["pass"] is True
