#!/usr/bin/env python3
"""Fresh native-system conformance replay for P8-DES-01."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
from typing import Any


JOB = "P8-DES-01"
CANNOT = "NATIVE_EQUIVALENCE_REPLAY_INTERNAL_ONLY_EXTERNAL_ADJUDICATION_UNAVAILABLE"
CEILING = (
    "FRESH_NATIVE_BINARY_CONFORMANCE_REPLAY_AND_SAME_PROGRAMME_SCIENTIFIC_GOLD_ONLY__"
    "NOT_PROSPECTIVE__NO_EXTERNAL_ADJUDICATION_OR_DEPLOYED_IDEAL_PRODUCT_AUTHORITY"
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: Any) -> None:
    path.write_bytes(canonical(value))


def run_json(command: list[str], cwd: Path | None = None) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(json.dumps({"command": command, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}, sort_keys=True))
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--scratch", type=Path, required=True)
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
    scratch = args.scratch.resolve()
    out = args.out.resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = bundle / "FREEZE_V1.json"
    runner_path = bundle / "run_p8_des_01.py"
    freeze = json.loads(freeze_path.read_text())
    if sha(runner_path) != freeze["implementation"]["runner_sha256"]:
        raise SystemExit("runner digest drift")
    for item in freeze["frozen_inputs"]:
        path = repo / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            raise SystemExit(f"frozen input drift:{item['path']}")
    for item in freeze["native_tools"]:
        path = Path(item["path"])
        if not path.is_file() or sha(path) != item["sha256"]:
            raise SystemExit(f"native tool drift:{item['name']}")
        resolved = shutil.which(item["name"])
        if resolved is None or Path(resolved).resolve() != path.resolve():
            raise SystemExit(f"native tool PATH mismatch:{item['name']}")
    if platform.python_version() != freeze["environment"]["python"]:
        raise SystemExit("python version drift")

    base = repo / "papers/paper-08-epistemic-authority-autonomous-science"
    native = run_json(
        [
            sys.executable,
            str(base / "formal/run_p8_native_cross_system_v1.py"),
            str(scratch / "native"),
            str(base / "formal/P8_NATIVE_CROSS_SYSTEM_PROTOCOL_2026-08-24.json"),
        ],
        cwd=base / "formal",
    )
    evidence = run_json([sys.executable, str(base / "top_tier/run_real_evidence_discharge_v1.py")], cwd=base / "top_tier")
    if native.get("slot_count") != 24 or len(native.get("slots", [])) != 24:
        raise SystemExit("native slot denominator drift")
    if evidence.get("case_count") != 20 or len(evidence.get("rows", [])) != 20:
        raise SystemExit("scientific evidence denominator drift")
    native_green = (
        native["summary"]["slots_filled"] == 24
        and native["summary"]["cannot_check"] == 0
        and native["summary"]["hostile_authorized"] == 0
        and native["summary"]["clean_not_authorized"] == 0
    )
    evidence_green = evidence["terminal"] == "P8_REAL_EVIDENCE_DISCHARGE_V1_SUPPORTED" and all(row["correct"] for row in evidence["rows"])
    campaign = {
        "schema": "orion.p8.dynamic-authority-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "case_denominator": 44,
        "native_slot_denominator": 24,
        "scientific_obligation_case_denominator": 20,
        "executed_case_denominator": 44,
        "dropped_case_denominator": 0,
        "fresh_native_replay_green": native_green,
        "same_programme_scientific_gold_green": evidence_green,
        "prospective_outcome_blind": False,
        "external_adjudication": False,
        "native_receipt": native,
        "scientific_obligation_receipt": evidence,
        "exact_terminal": CANNOT,
        "authority_ceiling": CEILING,
    }
    primary = {
        "schema": "orion.des.primary-result.v1",
        "job_id": JOB,
        "executed_at": args.executed_at,
        "exact_terminal": CANNOT,
        "case_denominator": 44,
        "executed_case_denominator": 44,
        "dropped_case_denominator": 0,
        "bounded_internal_native_green": native_green,
        "bounded_internal_scientific_gold_green": evidence_green,
        "claim_ceiling": CEILING,
        "paper_authority_delta": "NONE",
    }
    donor = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": JOB,
        "state": "BOUNDED_INTERNAL_EQUIVALENCE_REPLAY" if native_green else "BOUNDED_INTERNAL_DIVERGENCE",
        "ideal_typed_product_slots": 24,
        "native_equivalent_slots": sum(not row["diverges_from_baseline"] for row in native["slots"]),
        "deployed_integrated_donor": False,
        "external_adjudication": False,
        "weak_proxy_substituted": False,
    }
    controls = {
        "schema": "orion.des.negative-controls.v1",
        "job_id": JOB,
        "controls": [
            {"id": "ALL_NATIVE_POLARITY_CONTROLS", "passed": all(row["usable"] for row in native["polarity_controls"].values())},
            {"id": "ZERO_HOSTILE_AUTHORIZED", "passed": native["summary"]["hostile_authorized"] == 0},
            {"id": "ALL_CLEAN_AUTHORIZED", "passed": native["summary"]["clean_not_authorized"] == 0},
            {"id": "NO_SAME_PROGRAMME_GOLD_AS_EXTERNAL", "passed": True},
            {"id": "PREEXISTING_OUTCOME_NOT_CALLED_PROSPECTIVE", "passed": True},
            {"id": "ALL_44_CASES_RETAINED", "passed": len(native["slots"]) + len(evidence["rows"]) == 44},
        ],
        "all_pass": native_green and evidence_green,
    }
    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": JOB,
        "resource_vector": {
            "case_rows": 44,
            "native_subprocess_slots": 24,
            "scientific_obligation_cases": 20,
            "cpu_nanoseconds": time.process_time_ns() - start_cpu,
            "wall_nanoseconds": time.monotonic_ns() - start_wall,
            "gpu": 0,
            "network_calls": 0,
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "cap_hit": False,
        "censored": False,
    }
    transfer = {"schema": "orion.des.transfer-result.v1", "job_id": JOB, "state": "CANNOT_CHECK", "reason": CANNOT, "authority_delta": "NONE"}
    outputs = {
        "P8_DYNAMIC_AUTHORITY_RESULT_V1.json": campaign,
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
        "case_denominator": 44,
        "executed_case_denominator": 44,
        "dropped_case_denominator": 0,
        "hard_preconditions": {
            "four_pinned_native_systems": True,
            "all_ordered_pair_slots": native_green,
            "scientific_obligation_cases": evidence_green,
            "prospective_outcome_blind": False,
            "independent_external_gold": False,
            "deployed_integrated_donor": False,
            "external_adjudication": False,
        },
        "leakage": {"same_programme_gold_relabelled_external": False, "preexisting_outcome_called_prospective": False},
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
    print(f"{JOB}={CANNOT} cases=44 native_green={native_green} evidence_green={evidence_green}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
