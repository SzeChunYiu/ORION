#!/usr/bin/env python3
"""Independent generic-harness admission check for QG-3 stage-1 evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE1_PATH = REPO_ROOT / "artifacts" / "orion-qg-qg3-stage1.json"
PROTOCOL_PATH = (
    REPO_ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "QG3_POSITIVE_FORECAST_PROTOCOL_V1.md"
)
NOVELTY_PATH = (
    REPO_ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "QG3_NOVELTY_THREAT_FREEZE_2026-08-21.md"
)
TOKEN_PREFIX = "ORIONQG_QG3_GENERIC_ADMISSION="
FROZEN_BASE = "13a0fc6afb1d150a114ec318d72830e3c6722b03"
EXPECTED_NOVELTY_BOUNDARY = (
    "NO_CLOSE_PARENT_FOUND_FOR_EXACT_COMPILATION_FAMILY_REGIME_GEOMETRY_AS_DEFINED__NOVELTY_NOT_AUTHORIZED"
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stage1_self_digest_valid(stage1: dict[str, Any]) -> bool:
    observed = stage1.get("stage1_digest")
    unsigned = dict(stage1)
    unsigned.pop("stage1_digest", None)
    expected = hashlib.sha256(_canonical(unsigned).encode("utf-8")).hexdigest()
    return isinstance(observed, str) and observed == expected


def decide(stage1: dict[str, Any], novelty_text: str) -> dict[str, Any]:
    selected = stage1.get("selected")
    prediction = selected.get("prediction") if isinstance(selected, dict) else None
    strict_gap = (
        int(selected.get("strict_donor_gap_predicted", 0))
        if isinstance(selected, dict)
        else 0
    )
    protocol_sha = _sha256(PROTOCOL_PATH)
    novelty_sha = _sha256(NOVELTY_PATH)

    custody_checks = {
        "stage1_self_digest_valid": _stage1_self_digest_valid(stage1),
        "frozen_base_identity": stage1.get("base_revision") == FROZEN_BASE,
        "protocol_binding_exact": stage1.get("protocol_sha256") == protocol_sha,
        "novelty_freeze_binding_exact": stage1.get("novelty_threat_sha256") == novelty_sha,
        "admission_gates_pass": stage1.get("admission_gates_pass") is True,
        "freshness_pass": stage1.get("freshness_pass") is True,
        "protected_unread": stage1.get("protected_unread") is True,
        "no_dp_calls": (
            stage1.get("no_dp_calls") is True
            and int(stage1.get("dp_call_count", -1)) == 0
        ),
        "predicate_binding_exact": stage1.get("predicate_binding_exact") is True,
        "ground_truth_still_closed": stage1.get("ground_truth_opened") is False,
        "novelty_authority_still_false": stage1.get("novelty_authority") is False,
        "novelty_threat_freeze_present": EXPECTED_NOVELTY_BOUNDARY in novelty_text,
    }
    positive_checks = {
        "positive_found": stage1.get("positive_found") is True,
        "strict_predicted_donor_gap": strict_gap >= 1,
        "prediction_payload_present": isinstance(prediction, dict),
        "predicted_cost_strictly_below_donor": False,
        "positive_regime": False,
    }
    if positive_checks["prediction_payload_present"]:
        positive_checks["predicted_cost_strictly_below_donor"] = (
            int(prediction["predicted_C_DP"]) < int(prediction["C_R6L"])
        )
        positive_checks["positive_regime"] = prediction.get("predicted_regime") in {
            "split",
            "borrow",
        }

    custody_green = all(custody_checks.values())
    if custody_green and all(positive_checks.values()):
        decision = "OPEN"
    elif custody_green and stage1.get("positive_found") is False:
        decision = "NO_POSITIVE"
    else:
        decision = "INVALID"

    return {
        "schema": "ORION.QG.QG3.GenericAdmission.v2",
        "decision": decision,
        "stage1_digest": str(stage1.get("stage1_digest", "")),
        "custody_checks": custody_checks,
        "positive_checks": positive_checks,
        "protocol_sha256": protocol_sha,
        "novelty_threat_sha256": novelty_sha,
        "ground_truth_opened": False,
        "novelty_authority": False,
        "authority": "QG3_GENERIC_HARNESS_ADMISSION_ONLY__PRE_GROUND_TRUTH",
    }


def main() -> int:
    stage1 = json.loads(STAGE1_PATH.read_text(encoding="utf-8"))
    novelty_text = NOVELTY_PATH.read_text(encoding="utf-8")
    result = decide(stage1, novelty_text)
    print(TOKEN_PREFIX + _canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
