#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

INTERVENTIONS = ("INFORMATION", "ACCESSIBILITY", "COMPUTATION", "RECONSTRUCTION")
EXPECTED_COORDINATE = {
    "INFORMATION": "information",
    "ACCESSIBILITY": "accessibility",
    "COMPUTATION": "computation",
    "RECONSTRUCTION": "reconstruction",
}
FORBIDDEN_FEATURE_TOKENS = (
    "gold", "oracle", "intervention_success", "intervention_outcome",
    "post_intervention", "hidden_label", "hidden_gold",
)


def _num(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    out = float(value)
    if out < 0:
        raise ValueError(f"{name} must be nonnegative")
    return out


def cost_vector(intervention_id: str, rec: dict[str, Any]) -> tuple[float, float, float, float, float, int]:
    return (
        _num(rec["total_charged_cost"], "total_charged_cost"),
        _num(rec["added_information_bytes"], "added_information_bytes"),
        _num(rec["added_compute_units"], "added_compute_units"),
        _num(rec["representation_delta_units"], "representation_delta_units"),
        _num(rec["reconstruction_ops"], "reconstruction_ops"),
        INTERVENTIONS.index(intervention_id),
    )


def validate_atomic(intervention_id: str, rec: dict[str, Any]) -> None:
    if intervention_id not in INTERVENTIONS:
        raise ValueError(f"unknown intervention: {intervention_id}")
    if rec.get("budget_frozen") is not True:
        raise ValueError(f"{intervention_id} budget was not frozen")
    changed = rec.get("changed_coordinates")
    if changed != [EXPECTED_COORDINATE[intervention_id]]:
        raise ValueError(f"{intervention_id} is not one-coordinate atomic: {changed}")
    if not isinstance(rec.get("success"), bool):
        raise ValueError(f"{intervention_id} success must be boolean")
    cost_vector(intervention_id, rec)


def validate_leakage(task: dict[str, Any]) -> None:
    if task.get("diagnosis_sealed_before_interventions") is not True:
        raise ValueError("diagnosis was not sealed before intervention outcomes")
    common_hash = task.get("common_visible_packet_hash")
    if not isinstance(common_hash, str) or not common_hash:
        raise ValueError("common visible packet hash missing")
    router_hashes = task.get("router_visible_packet_hashes")
    if not isinstance(router_hashes, dict) or not router_hashes:
        raise ValueError("router visible packet hashes missing")
    if any(v != common_hash for v in router_hashes.values()):
        raise ValueError("router information-parity violation")
    features = task.get("diagnostic_feature_names")
    if not isinstance(features, list) or not all(isinstance(x, str) for x in features):
        raise ValueError("diagnostic_feature_names must be string list")
    lowered = [x.lower() for x in features]
    for name in lowered:
        if any(token in name for token in FORBIDDEN_FEATURE_TOKENS):
            raise ValueError(f"forbidden diagnostic feature leaks outcome/gold: {name}")


def construct_task_gold(task: dict[str, Any]) -> dict[str, Any]:
    for key in ("task_id", "domain", "split", "source_family_id"):
        if not isinstance(task.get(key), str) or not task[key]:
            raise ValueError(f"missing task field: {key}")
    if task["split"] not in ("development", "primary", "replication"):
        raise ValueError("bad split")
    if not isinstance(task.get("base_success"), bool):
        raise ValueError("base_success must be boolean")
    validate_leakage(task)
    interventions = task.get("interventions")
    if not isinstance(interventions, dict) or set(interventions) != set(INTERVENTIONS):
        raise ValueError("all four and only four interventions are required")
    for iid in INTERVENTIONS:
        validate_atomic(iid, interventions[iid])

    if task["base_success"]:
        return {
            "task_id": task["task_id"],
            "gold_cause": "EXCLUDED_BASE_SUCCESS",
            "identifiable": False,
            "selected_intervention": None,
            "selected_cost_vector": None,
        }

    successful = [(cost_vector(iid, interventions[iid]), iid) for iid in INTERVENTIONS if interventions[iid]["success"]]
    if not successful:
        return {
            "task_id": task["task_id"],
            "gold_cause": "METHOD/CANNOT_CHECK",
            "identifiable": False,
            "selected_intervention": None,
            "selected_cost_vector": None,
        }
    successful.sort()
    vec, iid = successful[0]
    return {
        "task_id": task["task_id"],
        "gold_cause": iid,
        "identifiable": True,
        "selected_intervention": iid,
        "selected_cost_vector": list(vec),
    }


def construct(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != "ORION.A4.HiddenCauseInterventionInput.v1":
        raise ValueError("wrong schema")
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")
    seen: set[str] = set()
    source_by_split: dict[str, set[str]] = {"development": set(), "primary": set(), "replication": set()}
    out = []
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("task must be object")
        tid = task.get("task_id")
        if tid in seen:
            raise ValueError(f"duplicate task_id: {tid}")
        seen.add(tid)
        row = construct_task_gold(task)
        row.update({"domain": task["domain"], "split": task["split"], "source_family_id": task["source_family_id"]})
        out.append(row)
        source_by_split[task["split"]].add(task["source_family_id"])
    overlap = source_by_split["replication"] & (source_by_split["development"] | source_by_split["primary"])
    if overlap:
        raise ValueError(f"replication source-family overlap: {sorted(overlap)[:10]}")
    return {
        "schema": "ORION.A4.HiddenCauseCausalGoldResult.v1",
        "tasks": out,
        "denominator_n": sum(r["gold_cause"] != "EXCLUDED_BASE_SUCCESS" for r in out),
        "identifiable_n": sum(r["identifiable"] for r in out),
        "cannot_check_n": sum(r["gold_cause"] == "METHOD/CANNOT_CHECK" for r in out),
        "leakage_check": "PASS",
        "source_disjoint_replication": True,
    }


def _intervention(success: bool, coordinate: str, cost: float, **extras: float) -> dict[str, Any]:
    return {
        "success": success,
        "budget_frozen": True,
        "changed_coordinates": [coordinate],
        "total_charged_cost": cost,
        "added_information_bytes": extras.get("info", 0.0),
        "added_compute_units": extras.get("compute", 0.0),
        "representation_delta_units": extras.get("repr", 0.0),
        "reconstruction_ops": extras.get("recon", 0.0),
    }


def self_test() -> dict[str, Any]:
    common = {
        "domain": "fixture-domain",
        "split": "primary",
        "source_family_id": "source-a",
        "base_success": False,
        "diagnosis_sealed_before_interventions": True,
        "common_visible_packet_hash": "h0",
        "router_visible_packet_hashes": {"candidate": "h0", "compute-first": "h0"},
        "diagnostic_feature_names": ["pre_outcome_error_class", "declared_budget"],
    }
    t1 = dict(common, task_id="t1", interventions={
        "INFORMATION": _intervention(True, "information", 2.0, info=100),
        "ACCESSIBILITY": _intervention(True, "accessibility", 1.0, repr=1),
        "COMPUTATION": _intervention(True, "computation", 1.0, compute=2),
        "RECONSTRUCTION": _intervention(False, "reconstruction", 1.0, recon=1),
    })
    # ACCESSIBILITY wins the exact cost tie because it has fewer added compute units.
    r1 = construct_task_gold(t1)
    assert r1["gold_cause"] == "ACCESSIBILITY"
    t2 = dict(common, task_id="t2", source_family_id="source-b", interventions={
        iid: _intervention(False, EXPECTED_COORDINATE[iid], 1.0) for iid in INTERVENTIONS
    })
    assert construct_task_gold(t2)["gold_cause"] == "METHOD/CANNOT_CHECK"
    bad = dict(t1)
    bad["diagnostic_feature_names"] = ["gold_cause"]
    try:
        construct_task_gold(bad)
    except ValueError as exc:
        assert "forbidden" in str(exc)
    else:
        raise AssertionError("gold leakage mutant was not rejected")
    bad2 = json.loads(json.dumps(t1))
    bad2["interventions"]["COMPUTATION"]["changed_coordinates"] = ["computation", "information"]
    try:
        construct_task_gold(bad2)
    except ValueError as exc:
        assert "not one-coordinate atomic" in str(exc)
    else:
        raise AssertionError("non-atomic intervention mutant was not rejected")
    return {"decision": "GREEN", "tie_gold": r1["gold_cause"], "no_success": "METHOD/CANNOT_CHECK"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.input is None:
        parser.error("input JSON required unless --self-test")
    result = construct(json.loads(args.input.read_text(encoding="utf-8")))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
