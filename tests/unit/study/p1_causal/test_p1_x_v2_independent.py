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

spec = importlib.util.spec_from_file_location("p1x_v2_independent", V2 / "verify_p1_x_v2_independent.py")
assert spec is not None and spec.loader is not None
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def test_independent_v2_verifier_passes_all_bound_checks() -> None:
    result = verifier.verify()
    assert result["ok"] is True
    assert result["terminal"] == "P1_X_V2_INDEPENDENT_VERIFICATION_PASS"
    assert result["arm_correct"] == {
        "P1X_MINIMAL_SCIENTIFIC_ESCALATION": 400,
        "B1_DONOR_COMPLETE_GREEDY": 275,
        "B2_SUCCESS_AUTHORIZES_REFRAME": 200,
        "B3_IDEAL_TYPED_PRODUCT": 400,
    }
    assert result["b3_decision_mismatches"] == 0
