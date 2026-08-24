#!/usr/bin/env python3
"""Packet-native integrity and scientific-consistency validator for P2 V7."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(body).hexdigest()


def exact_forbidden_row_keys(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"text", "title", "abstract", "label"}:
                hits.append(f"{path}.{key}")
            hits.extend(exact_forbidden_row_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(exact_forbidden_row_keys(child, f"{path}[{index}]"))
    return hits


def main() -> int:
    failures: list[str] = []
    json_files = sorted(HERE.glob("*.json"))
    objects = {path.name: json.loads(path.read_text()) for path in json_files}
    for path in HERE.glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))

    protocol = objects["PROTOCOL_FREEZE_V7.json"]
    implementation = objects["IMPLEMENTATION_FREEZE_V7.json"]
    result = objects["RESULT_V7.json"]
    ledger = objects["NEGATIVE_RESULT_LEDGER_V7.json"]

    for role, filename in {
        "protocol_v7": "PROTOCOL_FREEZE_V7.json",
        "runner_v7": "run_kifms_transparent_execution_v7.py",
        "pinned_active_core_v3": "pinned_active_core_v3.py",
        "pinned_factorial_core_v4": "pinned_factorial_core_v4.py",
    }.items():
        if sha256(HERE / filename) != implementation["fixed_sha256"][role]:
            failures.append(f"fixed hash mismatch: {role}")

    payload = dict(result)
    claimed_payload_hash = payload.pop("result_payload_sha256")
    if canonical_hash(payload) != claimed_payload_hash:
        failures.append("result payload hash mismatch")
    if result["terminal"] != protocol["terminals"]["public_performance_adverse"]:
        failures.append("unexpected terminal")
    if ledger["terminal"] != result["terminal"]:
        failures.append("ledger terminal mismatch")
    if result["custody"]["independent_custody"] is not False:
        failures.append("independence overclaim")
    if result["confirmatory_terminal_available"] is not False:
        failures.append("confirmatory overclaim")
    if result["population_reconstruction_receipt"]["canonical_rows"] != 4934:
        failures.append("canonical row mismatch")
    if result["population_reconstruction_receipt"]["candidate_count"] != 1:
        failures.append("population reconstruction not unique")
    if len(result["class_counts"]) != 14:
        failures.append("review count mismatch")
    if any(counts["positive"] <= 0 or counts["negative"] <= 0 for counts in result["class_counts"].values()):
        failures.append("both-class requirement failed")

    effects = result["unweighted_mean_component_effects"]["learner_balancer_main_effect"]
    full = result["mean_full_arm_candidate_minus_u4"]
    signs = result["strictly_positive_review_counts"]
    gates = result["performance_gates"]
    recomputed = {
        "C1_CRE20_MAGNITUDE": effects["cre20"] >= 0.010858985820770889,
        "C2_CRE20_SIGN": signs["learner_cre20"] >= 12,
        "C3_R10_MAGNITUDE": effects["recall_at_010"] >= 0.010858985820770889,
        "C4_R10_SIGN": signs["learner_r10"] >= 12,
        "C5_LEARNER_WORK_SAVING": effects["wss_at_95"] >= 0,
        "C6_LEARNER_HARM": min(
            row["learner_balancer_main_effect"]["recall_at_010"]
            for row in result["effects_by_review"].values()
        ) >= -0.05,
        "G3_FULL_ARM_R10_MARGIN": full["recall_at_010"] >= 0.05,
        "G4_FULL_ARM_WORK_SAVING": full["wss_at_95"] >= 0,
        "G5_FULL_ARM_HARM": min(
            row["recall_at_010"] for row in result["full_arm_candidate_minus_u4_by_review"].values()
        ) >= -0.05,
        "G6_ABSOLUTE_WORK_SAVING": all(
            row["R0_L0"]["metrics"]["wss_at_95"] > 0 for row in result["arms_by_review"].values()
        ),
    }
    if recomputed != gates:
        failures.append("gate recomputation mismatch")
    expected_failed = sorted(name for name, value in recomputed.items() if not value)
    if sorted(result["failed_performance_gates"]) != expected_failed:
        failures.append("failed-gate list mismatch")
    if signs != {"learner_cre20": 11, "learner_r10": 9}:
        failures.append("sign-count mismatch")
    if exact_forbidden_row_keys(result):
        failures.append("row-level source content leaked into result")
    if list(HERE.glob("*.csv")):
        failures.append("source CSV redistributed in packet")

    manifest = HERE / "SHA256SUMS"
    manifested = 0
    if manifest.is_file():
        for line in manifest.read_text().splitlines():
            if not line.strip():
                continue
            expected, relative = line.split(maxsplit=1)
            path = HERE / relative.lstrip(" *")
            manifested += 1
            if not path.is_file() or sha256(path) != expected:
                failures.append(f"manifest mismatch: {relative}")
    else:
        failures.append("SHA256SUMS absent")

    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, indent=2))
        return 1
    print(
        f"PASS P2 V7 scientific packet: {len(json_files)} JSON, "
        f"{len(list(HERE.glob('*.py')))} Python, {manifested} manifested files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

