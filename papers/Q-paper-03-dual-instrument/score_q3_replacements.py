#!/usr/bin/env python3
"""Apply the frozen Q3 replacement deferred-scoring maps.

This script reads committed QG19/QG20 scientific results only after the pre-outcome
instrument files already exist. It does not produce scientific outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
Q3 = ROOT / "papers/Q-paper-03-dual-instrument"


def canonical(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def score_instance(instance_dir: Path, result_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    a = load(instance_dir / "LANE_A_RECEIPT.json")
    b = load(instance_dir / "LANE_B_RECEIPT.json")
    pre = load(instance_dir / "PREOUTCOME_AGREEMENT.json")
    result = load(result_path)
    if a.get("scientific_outcome_accessed") is not False or b.get("scientific_outcome_accessed") is not False:
        raise AssertionError("pre-outcome instrument receipt claims outcome access")
    if pre.get("scientific_outcome_accessed") is not False:
        raise AssertionError("pre-outcome agreement claims outcome access")

    q = a["frontier_question_id"]
    if q == "QG-19":
        if result["terminal"] == "QG19_SUPPORT3_WITNESS_FOUND_ON_FROZEN_PANEL":
            expected_diag = "R2_SUPPORT3_LIKELY_NEAR_CENTRAL_FACE"
        elif result["terminal"] == "QG19_ZERO_GAP_ON_FROZEN_PANEL__SHARPNESS_REMAINS_OPEN":
            expected_diag = "R1_CERTIFICATE_SILENCE_SHARPNESS_OPEN"
        else:
            expected_diag = None
        expected_move = "M1_TARGETED_EXACT_OUTSIDE_CONE_PANEL" if expected_diag else None
    elif q == "QG-20":
        if result["terminal"] == "QG20_P0_REWEIGHTED_BOUNDARY_REFUTED":
            expected_diag = "S1_P0_BOUNDARY_OBJECTIVE_SCOPED"
        elif result["terminal"] == "QG20_P0_ZERO_MISMATCH_ON_COMPLETE_N1_N2":
            expected_diag = "S2_P0_STRUCTURALLY_INVARIANT_UNDER_SELECT_RESCALE"
        else:
            expected_diag = None
        expected_move = "N1_COMPLETE_REWEIGHTED_CENSUS" if expected_diag else None
    else:
        raise AssertionError(q)

    binding = {
        "schema": "ORIONQ.Q3DeferredOutcomeBinding.v2",
        "instance_id": a["instance_id"],
        "frontier_question_id": q,
        "scientific_result_path": str(result_path.relative_to(ROOT)),
        "scientific_result_sha256": sha_file(result_path),
        "scientific_result_digest": result.get("result_digest"),
        "scientific_terminal": result.get("terminal"),
        "outcome_produced_by_q3_instruments": False,
        "scientific_authority_inherited_by_q3": False,
    }
    score = {
        "schema": "ORIONQ.Q3FinalInstanceScore.v2",
        "instance_id": a["instance_id"],
        "frontier_question_id": q,
        "preoutcome_instrument_relation": {
            "responsibility": pre["responsibility_relation"],
            "next_move": pre["next_move_relation"],
            "revision_abstention": pre["revision_abstention_relation"],
        },
        "deferred_map_expected_primary_diagnosis": expected_diag,
        "deferred_map_expected_primary_move": expected_move,
        "lane_a": {
            "primary_diagnosis": a["primary_diagnosis"],
            "primary_move": a["primary_move"],
            "responsibility_alignment": None if expected_diag is None else a["primary_diagnosis"] == expected_diag,
            "move_alignment": None if expected_move is None else a["primary_move"] == expected_move,
        },
        "lane_b": {
            "primary_diagnosis": b["primary_diagnosis"],
            "primary_move": b["primary_move"],
            "responsibility_alignment": None if expected_diag is None else b["primary_diagnosis"] == expected_diag,
            "move_alignment": None if expected_move is None else b["primary_move"] == expected_move,
        },
        "scientific_terminal": result.get("terminal"),
        "score_status": "SCORED" if expected_diag is not None else "UNRESOLVED",
        "aggregate_reliability_claim_authorized": False,
        "scientific_authority": False,
    }
    score["score_digest"] = hashlib.sha256(canonical(score)).hexdigest()
    return binding, score


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qg19", type=Path, required=True)
    ap.add_argument("--qg20", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ns = ap.parse_args()
    pairs = [
        (Q3 / "instances/Q3-R1-QG19", ns.qg19),
        (Q3 / "instances/Q3-R2-QG20", ns.qg20),
    ]
    ns.output_root.mkdir(parents=True, exist_ok=True)
    for inst, res in pairs:
        binding, score = score_instance(inst, res)
        out = ns.output_root / inst.name
        out.mkdir(parents=True, exist_ok=True)
        (out / "DEFERRED_OUTCOME_BINDING.json").write_text(json.dumps(binding, indent=2, sort_keys=True)+"\n")
        (out / "FINAL_SCORE.json").write_text(json.dumps(score, indent=2, sort_keys=True)+"\n")
        print(inst.name, score["score_status"], score["score_digest"])


if __name__ == "__main__":
    main()
