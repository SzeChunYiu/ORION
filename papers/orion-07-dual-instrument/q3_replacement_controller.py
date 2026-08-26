#!/usr/bin/env python3
"""Deterministic typed Lane-B controller for Q3 replacement instances.

This controller has no access to QG19/QG20 outcome files. It maps only the frozen
manifest observations to a primary diagnosis/move. Scientific correctness is not
claimed by the controller; later deferred scoring is separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def decide(m: dict[str, Any]) -> dict[str, Any]:
    q = m["frontier_question_id"]
    obs = m["typed_observations"]
    if q == "QG-19":
        if not obs.get("weighted_referee_bound", False):
            diag, move = "R3_OBJECTIVE_PARAMETERIZATION_OR_REFEREE_DEFECT", "M4_REAUDIT_WEIGHTED_REFEREE"
        elif not obs.get("outside_sufficient_cone", False):
            diag, move = "R4_CANNOT_CHECK", "M5_STOP_CANNOT_CHECK"
        else:
            # Outside QG8 means proof silence, not support-three necessity. The clean
            # discriminating action is exact DP versus the theorem family on a frozen panel.
            diag, move = "R1_CERTIFICATE_SILENCE_SHARPNESS_OPEN", "M1_TARGETED_EXACT_OUTSIDE_CONE_PANEL"
    elif q == "QG-20":
        if not obs.get("unary_incumbent_remains_incumbent", False):
            diag, move = "S3_REWEIGHTED_INCUMBENT_OR_REFEREE_SCOPE_DEFECT", "N4_REAUDIT_REWEIGHTED_REFEREE"
        elif obs.get("objective_changes_select_gain_coefficients", False):
            diag, move = "S1_P0_BOUNDARY_OBJECTIVE_SCOPED", "N1_COMPLETE_REWEIGHTED_CENSUS"
        else:
            diag, move = "S4_CANNOT_CHECK", "N5_STOP_CANNOT_CHECK"
    else:
        raise ValueError(f"unsupported frontier question: {q}")
    return {
        "schema": "ORIONQ.Q3LaneBReceipt.v2",
        "frontier_question_id": q,
        "manifest_sha256": hashlib.sha256(canonical(m)).hexdigest(),
        "primary_diagnosis": diag,
        "primary_move": move,
        "abstained": move.endswith("CANNOT_CHECK"),
        "scientific_outcome_accessed": False,
        "scientific_authority": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--output")
    ns = ap.parse_args()
    m = json.loads(Path(ns.manifest).read_text())
    out = decide(m)
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if ns.output:
        Path(ns.output).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
