#!/usr/bin/env python3
"""Strict-unanimity calibration harness for three independent lower-bound routes.

This compares only committed/frozen small controls. It does not construct or run
any protected D4 target. PySAT UNSAT is consumed as a committed solver terminal
whose proof still requires external checking; it is not promoted to certificate
authority by this harness.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

ROUTES = ("DP_LB", "PYSAT_LA", "Z3_INDEPENDENT")
DECISIONS = ("SAT", "UNSAT")


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import route module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{lineno} is not an object")
        rows.append(obj)
    return rows


def pysat_decision(certificate: dict[str, Any]) -> str:
    status = certificate.get("status")
    if status == "SAT_K_DISJOINT_ZERO_SUMS":
        return "SAT"
    if status == "UNSAT_PROOF_EMITTED_REQUIRES_EXTERNAL_CHECK":
        proof = certificate.get("proof")
        if not isinstance(proof, dict) or proof.get("externally_checked") is not False:
            raise ValueError("PySAT UNSAT calibration certificate launders external checking")
        return "UNSAT"
    return "UNKNOWN"


def verify_pysat_sat_witness(record: dict[str, Any], certificate: dict[str, Any]) -> bool:
    if pysat_decision(certificate) != "SAT":
        return False
    sequence = record["sequence"]
    k = record["required_bins"]
    bins = certificate.get("witness_bins")
    if not isinstance(bins, list) or len(bins) != k or any(not isinstance(b, list) or not b for b in bins):
        return False
    used: set[int] = set()
    for members in bins:
        for idx in members:
            if isinstance(idx, bool) or not isinstance(idx, int) or not 0 <= idx < len(sequence) or idx in used:
                return False
            used.add(idx)
        if sum(sequence[i] for i in members) % 5 != 0:
            return False
    return True


def consensus(route_decisions: dict[str, str]) -> str:
    if set(route_decisions) != set(ROUTES):
        return "CANNOT_CHECK_ROUTE"
    values = [route_decisions[r] for r in ROUTES]
    if any(v not in DECISIONS for v in values):
        return "CANNOT_CHECK_ROUTE"
    if len(set(values)) != 1:
        return "ADVERSE_ROUTE_DISAGREEMENT"
    return "CONSENSUS_SAT_CONTROL" if values[0] == "SAT" else "CONSENSUS_UNSAT_CONTROL"


def compare(
    engine_a_path: Path,
    z3_path: Path,
    records_path: Path,
    certificates_path: Path,
) -> dict[str, Any]:
    engine_a = load_module(engine_a_path, "orion04_route_disagreement_engine_a")
    z3_route = load_module(z3_path, "orion04_route_disagreement_z3")

    records = load_jsonl(records_path)
    certs = load_jsonl(certificates_path)
    if len(records) != len(certs):
        raise ValueError("record/certificate count mismatch")
    by_cert = {c.get("record_id"): c for c in certs}
    if len(by_cert) != len(certs):
        raise ValueError("duplicate/missing certificate record id")

    rows = []
    for record in records:
        if record.get("schema") != "ORION.NQ.EngineB.SequenceRecord.v1":
            raise ValueError("unexpected control record schema")
        if record.get("scope") != "SMALL_CONTROL":
            raise ValueError("route-disagreement harness only accepts SMALL_CONTROL records")
        rid = record.get("record_id")
        if not isinstance(rid, str) or not rid:
            raise ValueError("control record id missing")
        cert = by_cert.get(rid)
        if cert is None:
            raise ValueError(f"missing certificate for {rid}")
        sequence = record.get("sequence")
        k = record.get("required_bins")
        if not isinstance(sequence, list) or not sequence or any(type(x) is not int or not 0 <= x < 5 for x in sequence):
            raise ValueError(f"control {rid} is not a rank-1 C5 sequence")
        if type(k) is not int or not 1 <= k <= 4:
            raise ValueError(f"bad k for {rid}")

        dp_count = engine_a.max_disjoint_zero_sums([(x,) for x in sequence], (5,))
        dp_decision = "SAT" if dp_count >= k else "UNSAT"
        z3_decision = z3_route.solve((5,), [(x,) for x in sequence], k)["decision"]
        py_decision = pysat_decision(cert)
        if z3_decision not in DECISIONS:
            z3_decision = "UNKNOWN"
        witness_ok = None
        if py_decision == "SAT":
            witness_ok = verify_pysat_sat_witness(record, cert)
            if not witness_ok:
                raise ValueError(f"PySAT SAT witness failed primitive verification for {rid}")

        decisions = {
            "DP_LB": dp_decision,
            "PYSAT_LA": py_decision,
            "Z3_INDEPENDENT": z3_decision,
        }
        rows.append({
            "record_id": rid,
            "sequence": sequence,
            "required_bins": k,
            "route_decisions": decisions,
            "terminal": consensus(decisions),
            "dp_max_disjoint_zero_sums": dp_count,
            "pysat_sat_witness_verified": witness_ok,
            "pysat_unsat_proof_externally_checked": (
                cert.get("proof", {}).get("externally_checked") if py_decision == "UNSAT" else None
            ),
        })

    return {
        "schema": "ORION04.A1.RouteDisagreementCalibrationResult.v1",
        "target_d4_execution_performed": False,
        "protected_d4_outcome_accessed": False,
        "d4_rounds_consumed": 0,
        "routes": list(ROUTES),
        "rows": rows,
        "all_base_controls_unanimous": all(r["terminal"] in ("CONSENSUS_SAT_CONTROL", "CONSENSUS_UNSAT_CONTROL") for r in rows),
        "majority_vote_used": False,
        "scientific_authority_delta": "NONE__CALIBRATION_DISAGREEMENT_GUARD_ONLY",
    }


def hostile_controls(base: dict[str, Any]) -> dict[str, Any]:
    by_id = {r["record_id"]: r for r in base["rows"]}
    positive = by_id.get("positive-batch")
    negative = by_id.get("negative-batch")
    if positive is None or negative is None:
        raise ValueError("required positive-batch/negative-batch controls missing")
    if positive["terminal"] != "CONSENSUS_SAT_CONTROL" or negative["terminal"] != "CONSENSUS_UNSAT_CONTROL":
        raise ValueError("base controls do not provide both consensus directions")

    pos_mut = dict(positive["route_decisions"])
    pos_mut["DP_LB"] = "UNSAT"
    neg_mut = dict(negative["route_decisions"])
    neg_mut["PYSAT_LA"] = "SAT"
    missing = dict(positive["route_decisions"])
    missing.pop("Z3_INDEPENDENT")

    controls = {
        "two_to_one_sat_control_is_adverse": consensus(pos_mut) == "ADVERSE_ROUTE_DISAGREEMENT",
        "two_to_one_unsat_control_is_adverse": consensus(neg_mut) == "ADVERSE_ROUTE_DISAGREEMENT",
        "missing_route_is_cannot_check": consensus(missing) == "CANNOT_CHECK_ROUTE",
    }
    return {
        "controls": controls,
        "all_hostile_controls_pass": all(controls.values()),
        "majority_vote_can_rescue_disagreement": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine-a", required=True, type=Path)
    ap.add_argument("--z3-route", required=True, type=Path)
    ap.add_argument("--records", required=True, type=Path)
    ap.add_argument("--certificates", required=True, type=Path)
    args = ap.parse_args()
    base = compare(args.engine_a, args.z3_route, args.records, args.certificates)
    hostile = hostile_controls(base)
    result = {**base, "hostile_controls": hostile}
    good = base["all_base_controls_unanimous"] and hostile["all_hostile_controls_pass"]
    result["decision"] = "GREEN" if good else "REJECT"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
