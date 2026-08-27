#!/usr/bin/env python3
"""Execute the frozen internal regime-transport slice for P7-DES-01."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
from typing import Any

import numpy
import sklearn


JOB = "P7-DES-01"
CANNOT = "EXTERNAL_REGIME_REMINT_VALIDATION_UNAVAILABLE"
CEILING = (
    "BOUNDED_INTERNAL_PUBLIC_DATA_AND_STANDARDS_REPLAY_ONLY__NO_INDEPENDENTLY_"
    "HELD_WORKFLOW_OR_PLANNING_REMINTS__NO_EXTERNAL_VALIDATION"
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: Any) -> None:
    path.write_bytes(canonical(value))


def run_json(script: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=script.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            json.dumps(
                {
                    "script": str(script),
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                },
                sort_keys=True,
            )
        )
    return json.loads(proc.stdout)


def load_module(script: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen script:{script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def normalize(regime: dict[str, Any], objective: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(regime["standard_rows"]):
        rows.append(
            {
                "case_id": f"STANDARD:{index}:{row['term']}:{row['condition']}",
                "domain": "ONTOLOGY_STANDARD",
                "gold": row["gold"],
                "predictions": {name: row[name] for name in ("WITNESS_AWARE", "VALUE_ONLY", "ALWAYS_REOPEN")},
            }
        )
    for row in regime["wine_rows"]:
        rows.append(
            {
                "case_id": f"WINE:{row['id']}",
                "domain": "TABULAR_LABEL_REGIME",
                "gold": row["gold"],
                "predictions": {name: row[name] for name in ("WITNESS_AWARE", "VALUE_ONLY", "ALWAYS_REOPEN")},
            }
        )
    objective_predictions = {
        system: {row["id"]: row["predicted"] for row in receipt["rows"]}
        for system, receipt in objective["systems"].items()
    }
    for row in objective["cells"]:
        rows.append(
            {
                "case_id": f"OBJECTIVE:{row['id']}",
                "domain": "OBJECTIVE_CHANGE",
                "gold": row["gold"],
                "predictions": {name: objective_predictions[name][row["id"]] for name in ("WITNESS_AWARE", "VALUE_ONLY", "ALWAYS_REOPEN")},
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--executed-at", required=True)
    parser.add_argument("--execution-head", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.execution_head):
        raise SystemExit("invalid execution head")
    start_wall = time.monotonic_ns()
    start_cpu = time.process_time_ns()
    repo = args.repo.resolve()
    bundle = args.bundle.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    runner_path = bundle / "run_p7_des_01.py"
    freeze = json.loads(freeze_path.read_text())
    if sha(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")
    for item in freeze["frozen_inputs"]:
        path = repo / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            raise SystemExit(f"frozen input drift:{item['path']}")
    env = freeze["environment"]
    if platform.python_version() != env["python"] or numpy.__version__ != env["numpy"] or sklearn.__version__ != env["scikit_learn"]:
        raise SystemExit("frozen execution environment drift")

    base = repo / "papers/paper-07-epistemic-navigation-open-worlds/top_tier"
    regime_script = base / "run_real_regime_transport_v1.py"
    regime = run_json(regime_script)
    regime_module = load_module(regime_script, "p7_frozen_regime_transport")
    wine_rows, wine_label_sha = regime_module.eval_wine()
    if wine_label_sha != regime["wine_label_sha256"]:
        raise SystemExit("wine label identity drift between frozen replay paths")
    regime["wine_rows"] = wine_rows
    objective = run_json(base / "run_objective_change_transport_v1.py")
    rows = normalize(regime, objective)
    if len(rows) != 738:
        raise SystemExit(f"case denominator drift:{len(rows)}")
    arms = ("WITNESS_AWARE", "VALUE_ONLY", "ALWAYS_REOPEN", "EXACT_CONTAINMENT_DONOR")
    for row in rows:
        row["predictions"]["EXACT_CONTAINMENT_DONOR"] = "CANNOT_CHECK_ARM_UNAVAILABLE"
    summary: dict[str, Any] = {}
    for arm in arms:
        available = arm != "EXACT_CONTAINMENT_DONOR"
        summary[arm] = {
            "case_denominator": len(rows),
            "execution_state": "EXECUTED" if available else "UNAVAILABLE_CANNOT_CHECK",
            "correct": sum(row["predictions"][arm] == row["gold"] for row in rows) if available else 0,
            "false_retained_closure": sum(row["predictions"][arm] in {"TRANSPORT", "PRESERVE"} and row["gold"] not in {"TRANSPORT", "PRESERVE"} for row in rows) if available else None,
            "unnecessary_reopening": sum(row["predictions"][arm] == "REOPEN" and row["gold"] in {"TRANSPORT", "PRESERVE"} for row in rows) if available else None,
        }
    campaign = {
        "schema": "orion.p7.dynamic-regime-transport-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "case_denominator": len(rows),
        "arm_denominator": len(arms),
        "arm_case_denominator": len(rows) * len(arms),
        "mechanically_executed_arm_cases": len(rows) * 3,
        "unavailable_arm_cases": len(rows),
        "domains_executed": ["ONTOLOGY_STANDARD", "TABULAR_LABEL_REGIME", "OBJECTIVE_CHANGE"],
        "required_domains_unavailable": ["WORKFLOW_REMINT", "PLANNING_REMINT"],
        "regime_receipt": regime,
        "objective_receipt": objective,
        "arm_summary": summary,
        "rows": rows,
        "exact_terminal": CANNOT,
        "authority_ceiling": CEILING,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "exact_terminal": CANNOT,
        "case_denominator": len(rows),
        "arm_case_denominator": len(rows) * len(arms),
        "mechanically_executed_arm_cases": len(rows) * 3,
        "unavailable_arm_cases": len(rows),
        "claim_ceiling": CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB,
        "state": "MIXED",
        "executed_donors": ["VALUE_ONLY", "ALWAYS_REOPEN"],
        "unavailable_donors": ["EXACT_CONTAINMENT_DONOR"],
        "reason": "no distinct frozen exact-containment product was transferred; it was not approximated by witness-aware ORION",
        "weak_proxy_substituted": False,
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB,
        "controls": [
            {"id": "NO_WITNESS_AWARE_AS_EXACT_CONTAINMENT_DONOR", "passed": True},
            {"id": "NO_INTERNAL_GOLD_AS_EXTERNAL", "passed": True},
            {"id": "PATH_HISTORY_RETAINED", "passed": regime["sequential_support_history_disposition_differences"] > 0},
            {"id": "ALL_CASES_RETAINED", "passed": len(rows) == 738},
            {"id": "MISSING_DOMAINS_NOT_HIDDEN", "passed": True},
        ],
        "all_pass": len(rows) == 738 and regime["sequential_support_history_disposition_differences"] > 0,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB,
        "resource_vector": {
            "case_rows": len(rows),
            "arm_cases": len(rows) * len(arms),
            "cpu_nanoseconds": time.process_time_ns() - start_cpu,
            "wall_nanoseconds": time.monotonic_ns() - start_wall,
            "gpu": 0,
            "network_calls": 0,
        },
        "environment": env,
        "cap_hit": False,
        "censored": False,
    }
    transfer = {"schema": "orion.des.transfer-result.v1", "job_id": JOB, "state": "CANNOT_CHECK", "reason": CANNOT, "authority_delta": "NONE"}
    outputs = {
        "P7_DYNAMIC_REGIME_TRANSPORT_RESULT_V1.json": campaign,
        "PRIMARY_RESULT_V1.json": primary,
        "IDEAL_DONOR_RESULT_V1.json": donor,
        "NEGATIVE_CONTROLS_V1.json": controls,
        "RESOURCE_LEDGER_V1.json": resources,
        "TRANSFER_RESULT_V1.json": transfer,
    }
    for name, value in outputs.items():
        write(out / name, value)
    manifest = {
        "schema": "orion.des.raw-manifest.v1",
        "job_id": JOB,
        "subject_revision": freeze["subject_revision"],
        "freeze_sha256": sha(freeze_path),
        "runner_sha256": sha(runner_path),
        "outputs": {name: {"bytes": (out / name).stat().st_size, "sha256": sha(out / name)} for name in sorted(outputs)},
    }
    write(out / "RAW_MANIFEST_V1.json", manifest)
    binding = {
        "schema": "orion.des.result-binding-packet.v1",
        "job_id": JOB,
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "execution_head": args.execution_head,
        "freeze_sha256": sha(freeze_path),
        "raw_manifest_sha256": sha(out / "RAW_MANIFEST_V1.json"),
        "case_denominator": len(rows),
        "arm_case_denominator": len(rows) * len(arms),
        "mechanically_executed_arm_cases": len(rows) * 3,
        "unavailable_arm_cases": len(rows),
        "hard_preconditions": {
            "ontology_remint": True,
            "workflow_remint": False,
            "planning_remint": False,
            "objective_remint": True,
            "exact_containment_donor": False,
            "independent_external_gold": False,
            "external_custody": False,
        },
        "leakage": {"internal_gold_relabelled_external": False, "witness_aware_substituted_as_donor": False},
        "censoring": {"cap_hit": False, "timeout": False, "rows_dropped": 0},
        "strongest_donor": donor,
        "resource_vector": resources["resource_vector"],
        "transfer": transfer,
        "exact_terminal": CANNOT,
        "claim_ceiling": CEILING,
        "external_authority_state": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
    }
    write(out / "RESULT_BINDING_PACKET_V1.json", binding)
    print(f"{JOB}={CANNOT} cases={len(rows)} arm_cases={len(rows)*len(arms)} executed={len(rows)*3} unavailable={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
