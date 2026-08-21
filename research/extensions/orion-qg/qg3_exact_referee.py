#!/usr/bin/env python3
"""QG-3 stage-2 exact referee. DP opens only after dual-harness agreement."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q_DIR = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q_DIR))

import max_r6r_prospective_fresh_subject as r6r  # noqa: E402

DEFAULT_STAGE1 = REPO_ROOT / "artifacts" / "orion-qg-qg3-stage1.json"
DEFAULT_DUAL = REPO_ROOT / "artifacts" / "orion-qg-qg3-dual-admission.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg3-result.json"
TOKEN_PREFIX = "ORIONQG_QG3_RESULT="


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _stage1_digest_valid(packet: dict[str, Any]) -> bool:
    observed = packet.get("stage1_digest")
    base = dict(packet)
    base.pop("stage1_digest", None)
    expected = hashlib.sha256(_canonical(base).encode("utf-8")).hexdigest()
    return isinstance(observed, str) and observed == expected


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _honest_terminal(stage1: dict[str, Any], dual: dict[str, Any]) -> str | None:
    if not _stage1_digest_valid(stage1):
        return "QG3_ACCESS_OR_PROVENANCE_CANNOT_CHECK"
    if dual.get("stage1_digest") != stage1.get("stage1_digest"):
        return "QG3_ACCESS_OR_PROVENANCE_CANNOT_CHECK"
    if stage1.get("admission_gates_pass") is not True:
        return "QG3_ACCESS_OR_PROVENANCE_CANNOT_CHECK"
    if stage1.get("positive_found") is not True:
        return "QG3_NO_POSITIVE_PREDICTION_IN_FROZEN_SCAN"
    if dual.get("both_open") is not True:
        return "QG3_DUAL_HARNESS_DISAGREEMENT"
    if dual.get("generic_lane", {}).get("decision") != "OPEN":
        return "QG3_DUAL_HARNESS_DISAGREEMENT"
    if dual.get("native_lane", {}).get("decision") != "OPEN":
        return "QG3_DUAL_HARNESS_DISAGREEMENT"
    return None


def run_referee(stage1: dict[str, Any], dual: dict[str, Any]) -> dict[str, Any]:
    early = _honest_terminal(stage1, dual)
    if early is not None:
        return {
            "schema": "ORION.QG.QG3.Result.v1",
            "authority": early + "__NOVELTY_NOT_AUTHORIZED",
            "terminal": early,
            "stage1_digest": stage1.get("stage1_digest"),
            "ground_truth_opened": False,
            "novelty_authority": False,
        }

    selected = stage1.get("selected")
    if not isinstance(selected, dict):
        raise TypeError("dual-open packet has no selected positive candidate")
    subject = selected.get("subject")
    prediction = selected.get("prediction")
    if not isinstance(subject, dict) or not isinstance(prediction, dict):
        raise TypeError("selected subject/prediction malformed")
    if subject.get("path") == r6r.PROTECTED_STRETCHED_N2_PATH:
        raise AssertionError("protected stretched N2 selected in QG-3")
    if subject.get("blob") in set(r6r.COMMITTED_SUBJECT_BLOBS) | {
        "5c02c72b88e12b391ea1d8f77eb6b3e04fc2a915"
    }:
        raise AssertionError("QG-3 stage 2 selected a prior committed subject blob")

    cfg = {
        "commit": subject["commit"],
        "blob": subject["blob"],
        "path": subject["path"],
        "n_occ": int(subject["n_occ"]),
        "n_virt": int(subject["n_virt"]),
        "n_orb": int(subject["n_orb"]),
        "n_qubits": int(subject["n_qubits"]),
    }
    admission = r6r.try_admit(cfg)
    if not admission.get("admitted"):
        raise AssertionError({"qg3_stage2_readmission_failed": admission.get("reason")})
    six = [int(x) for x in admission["six"]]
    if six != [int(x) for x in selected["six_source_indices"]]:
        raise AssertionError("QG-3 stage2 six-term batch differs from sealed stage1")
    pairs = tuple(tuple(int(x) for x in pair) for pair in selected["matching"])
    if pairs not in tuple(r6r.r6m.perfect_matchings(six)):
        raise AssertionError("selected matching is not a canonical frozen matching")

    terms = admission["terms"]
    n = int(subject["n_qubits"])
    r6r.r6m._local_table.cache_clear()
    witness = r6r.r6m.exact_r6m_matching(terms, pairs, n, six)
    if not all(witness["checks"].values()):
        raise AssertionError("QG-3 exact DP witness verification failed")
    c_dp = int(witness["C_R6M"])
    c_r6l = int(prediction["C_R6L"])
    c_dplus = int(prediction["C_Dplus"])
    f_b = int(prediction["f_B"])
    predicted = int(prediction["predicted_C_DP"])
    predicted_regime = str(prediction["predicted_regime"])

    if not (c_dp <= c_dplus <= c_r6l):
        raise AssertionError({"qg3_sandwich_violated": [c_dp, c_dplus, c_r6l]})
    if c_dp > f_b:
        raise AssertionError({"qg3_borrow_soundness_violated": [c_dp, f_b]})

    if c_dp == c_r6l:
        truth_regime = "donor_exact"
    elif c_dp == c_dplus:
        truth_regime = "split"
    else:
        truth_regime = "borrow"

    strict_gap = c_r6l - c_dp
    confirmed = bool(
        predicted < c_r6l
        and strict_gap >= 1
        and c_dp == predicted
        and truth_regime == predicted_regime
    )
    terminal = (
        "QG3_PROSPECTIVE_POSITIVE_TRADE_FORECAST_CONFIRMED"
        if confirmed
        else "QG3_PREDICTION_REFUTED"
    )
    result = {
        "schema": "ORION.QG.QG3.Result.v1",
        "authority": terminal + "__NOVELTY_NOT_AUTHORIZED",
        "terminal": terminal,
        "stage1_digest": stage1["stage1_digest"],
        "selected_subject": subject,
        "six_source_indices": six,
        "matching": [list(pair) for pair in pairs],
        "prediction": prediction,
        "truth": {
            "C_DP": c_dp,
            "truth_regime": truth_regime,
            "strict_donor_gap": strict_gap,
            "dp_witness_checks_pass": True,
        },
        "gates": {
            "dual_harness_open": True,
            "stage1_digest_valid": True,
            "fresh_subject": True,
            "protected_stretched_n2_unread": True,
            "prediction_strictly_below_donor": predicted < c_r6l,
            "exact_cost_match": c_dp == predicted,
            "regime_match": truth_regime == predicted_regime,
            "strict_donor_gap_at_least_one": strict_gap >= 1,
            "dp_witness_checks_pass": True,
        },
        "ground_truth_opened": True,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1", default=str(DEFAULT_STAGE1))
    parser.add_argument("--dual", default=str(DEFAULT_DUAL))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    stage1 = json.loads(Path(args.stage1).read_text(encoding="utf-8"))
    dual = json.loads(Path(args.dual).read_text(encoding="utf-8"))
    result = run_referee(stage1, dual)
    _write(Path(args.output), result)
    print(TOKEN_PREFIX + _canonical(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
