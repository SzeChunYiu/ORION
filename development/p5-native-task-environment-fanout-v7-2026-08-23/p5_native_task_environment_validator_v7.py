#!/usr/bin/env python3
"""Fail-closed validator for the P5 V7 task-environment packet."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ORION = HERE.parent.parent
PROTOCOL_SHA256 = "3a6cc70a0f91957ef4e7fbc5ec42e66875084f7985c2250c056e00d865aa4fe0"
EXPECTED_TERMINAL = (
    "P5_V7_C1_NATIVE_TASK_ENVIRONMENT_BOUND__ONE_OF_SIX_ENVIRONMENTS_CLOSED__"
    "FIFTY_FIVE_OF_ONE_HUNDRED_TWENTY_SIX_FIELDS_BOUND__SEVENTY_ONE_BLOCKING__"
    "FIVE_R2_NATIVE_ENVIRONMENT_INSTANCES_REMAIN__ZERO_OF_SIX_READY__"
    "PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)
ARM_IDS = {
    "C1": "C1_FIXED_AGENT__SWE_AGENT",
    "C2": "C2_DIRECT_SELF_EDIT__MOSS",
    "C3": "C3_ARCHIVE_BASED_SELF_EDIT__DGM",
    "C4": "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS",
    "C5": "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY",
    "C6": "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(name: str) -> dict[str, Any]:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_references(value: Any, context: str = "root") -> int:
    count = 0
    if isinstance(value, dict):
        if {"path", "sha256", "size_bytes"}.issubset(value):
            path_text = value["path"]
            require(isinstance(path_text, str) and path_text.startswith("development/"), f"unsafe ref path at {context}")
            path = ORION / path_text
            require(path.is_file(), f"missing referenced file at {context}: {path_text}")
            require(path.stat().st_size == value["size_bytes"], f"size mismatch at {context}: {path_text}")
            require(sha256(path) == value["sha256"], f"SHA-256 mismatch at {context}: {path_text}")
            count += 1
        for key, item in value.items():
            count += verify_references(item, f"{context}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            count += verify_references(item, f"{context}[{index}]")
    return count


def validate_sha256sums() -> int:
    sums = HERE / "SHA256SUMS"
    require(sums.is_file(), "SHA256SUMS missing")
    rows = []
    for line in sums.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"malformed SHA256SUMS row: {line!r}")
        rows.append((match.group(1), match.group(2)))
    expected_names = sorted(p.name for p in HERE.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    require(sorted(name for _, name in rows) == expected_names, "SHA256SUMS membership mismatch")
    for digest, name in rows:
        require(sha256(HERE / name) == digest, f"SHA256SUMS digest mismatch: {name}")
    return len(rows)


def main() -> None:
    require(sha256(HERE / "P5_NATIVE_TASK_ENVIRONMENT_PROTOCOL_V7.json") == PROTOCOL_SHA256, "protocol drift")
    protocol = load("P5_NATIVE_TASK_ENVIRONMENT_PROTOCOL_V7.json")
    require(protocol["protocol_frozen_before_environment_outputs"] is True, "protocol ordering claim absent")
    require(protocol["field_scope"]["only_mutable_field"] == "runtime.task_environment", "field scope widened")
    require(protocol["field_scope"]["all_other_120_field_instances"] == "UNCHANGED_FROM_V6", "other-field boundary changed")
    require(protocol["field_scope"]["arm_execution_allowed"] is False, "arm execution allowed")
    require(protocol["field_scope"]["model_execution_allowed"] is False, "model execution allowed")

    schema = load("P5_NATIVE_TASK_ENVIRONMENT_MANIFEST_SCHEMA_V7.json")
    require(schema["properties"]["status"]["enum"] == ["BOUND", "BLOCKING"], "manifest status vocabulary changed")

    manifests: dict[str, dict[str, Any]] = {}
    receipts: dict[str, dict[str, Any]] = {}
    reference_count = 0
    for code, arm_id in ARM_IDS.items():
        manifest_name = f"P5_{code}_NATIVE_TASK_ENVIRONMENT_MANIFEST_V7.json"
        receipt_name = f"P5_{code}_NATIVE_TASK_ENVIRONMENT_ACCEPTANCE_V7.json"
        manifest = load(manifest_name)
        receipt = load(receipt_name)
        manifests[code] = manifest
        receipts[code] = receipt
        require(manifest["schema_version"] == "orion.p5.native-task-environment-manifest.v7", f"{code} schema")
        require(manifest["arm_code"] == code and manifest["arm_id"] == arm_id, f"{code} identity")
        require(manifest["case_id"] == "P5-PUBLIC-LANG1-COMMON-001", f"{code} case")
        expected_status = "BOUND" if code == "C1" else "BLOCKING"
        require(manifest["status"] == expected_status, f"{code} inadmissible status")
        require(receipt["status"] == expected_status, f"{code} receipt status")
        require(receipt["field"] == "runtime.task_environment", f"{code} wrong field")
        require(receipt["protocol_sha256"] == PROTOCOL_SHA256, f"{code} protocol ref")
        require(receipt["arm_or_model_executed"] is False, f"{code} execution claim")
        require(receipt["field_instances_closed"] == (1 if code == "C1" else 0), f"{code} closure count")
        require(receipt["manifest"]["sha256"] == sha256(HERE / manifest_name), f"{code} manifest receipt hash")
        reference_count += verify_references(manifest, f"manifest.{code}")
        reference_count += verify_references(receipt, f"receipt.{code}")
        if code != "C1":
            require(manifest["future_or_planned_bytes_promoted_to_evidence"] is False, f"{code} future promise promoted")
            require(len(manifest["missing_byte_artifacts"]) > 0, f"{code} missing-byte list empty")
            require(bool(manifest["residual"]) and bool(manifest["next_discriminator"]), f"{code} residual incomplete")

    c1 = manifests["C1"]
    require(len(c1["criteria_satisfied"]) == 8, "C1 criterion count")
    policy = c1["policy"]
    require(policy == {
        "action_sampler": None,
        "chooser_or_reviewer_loop": False,
        "gold_or_outcome_payloads": False,
        "open_pr": False,
        "retry_agent": False,
        "review_on_submit_m": False,
        "setup_network": "DENY",
    }, "C1 effective policy drift")
    require(c1["field_scope"] == "runtime.task_environment only", "C1 widened scope")
    require(c1["arm_or_model_executed"] is False, "C1 execution claim")
    require(c1["runtime_or_container_identity_claimed"] is False, "C1 runtime spillover")
    require(c1["performance_or_superiority_claimed"] is False, "C1 performance spillover")

    config = load("P5_C1_EFFECTIVE_AGENT_CONFIG_V7.json")
    agent = config["agent"]
    require(agent["type"] == "default", "C1 agent type")
    require(agent["action_sampler"] is None, "C1 action sampler")
    require(agent["retry_agent"] is False and agent["max_candidate_attempts"] == 1, "C1 retry policy")
    require(agent["review_on_submit_m"] is False, "C1 review policy")
    require(agent["chooser_or_reviewer_loop"] is False, "C1 chooser/reviewer policy")
    require(agent["actions"] == {"apply_patch_locally": False, "open_pr": False}, "C1 action policy")
    require(config["task"]["network_during_setup"] == "DENY", "C1 setup network")
    require(config["outcome_and_gold_payloads_present"] is False, "C1 outcome payload")
    require(config["execution_authorized_by_v7"] is False, "C1 execution authorization")

    setup_text = (HERE / "P5_C1_TASK_SETUP_V7.sh").read_text(encoding="utf-8")
    require("f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08" in setup_text, "C1 archive check absent")
    require("src/main/java/org/apache/commons/lang3/math/NumberUtils.java" in setup_text, "C1 mutable path absent")
    for forbidden in ["curl ", "wget ", "git clone", "http://", "https://"]:
        require(forbidden not in setup_text, f"C1 setup contains network surface: {forbidden!r}")

    aggregate = load("P5_SIX_ARM_NATIVE_TASK_ENVIRONMENT_ACCEPTANCE_V7.json")
    require(aggregate["accepted_arm_count"] == 1 and aggregate["blocking_arm_count"] == 5, "aggregate counts")
    require(aggregate["accepted_arms"] == ["C1"], "accepted arms")
    require(aggregate["blocking_arms"] == ["C2", "C3", "C4", "C5", "C6"], "blocking arms")
    require(aggregate["arm_or_model_executions"] == 0, "aggregate execution count")
    require(len(aggregate["receipts"]) == 6, "aggregate receipt count")
    reference_count += verify_references(aggregate, "aggregate")

    result = load("P5_NATIVE_TASK_ENVIRONMENT_RESULT_V7.json")
    delta = result["field_delta"]
    require(delta == {
        "after_blocking": 71,
        "after_bound": 55,
        "before_blocking": 72,
        "before_bound": 54,
        "new_bindings": 1,
        "per_arm": {
            "C1": {"blocking": 9, "bound": 12},
            "C2": {"blocking": 12, "bound": 9},
            "C3": {"blocking": 13, "bound": 8},
            "C4": {"blocking": 13, "bound": 8},
            "C5": {"blocking": 10, "bound": 11},
            "C6": {"blocking": 14, "bound": 7},
        },
        "ready_arms": 0,
    }, "result arithmetic changed")
    require(sum(x["bound"] + x["blocking"] for x in delta["per_arm"].values()) == 126, "field total")
    require(result["root_r2"]["after_blocking_instances"] == 5, "R2 count")
    require(result["executions"] == {"arms": 0, "benchmarks": 0, "models": 0, "outcomes_accessed": 0, "protected_scorers": 0}, "execution boundary")
    require(result["terminal"] == EXPECTED_TERMINAL, "result terminal")
    require((HERE / "TERMINAL_V7.txt").read_text(encoding="utf-8").strip() == EXPECTED_TERMINAL, "terminal file")

    ledger = load("P5_NATIVE_TASK_ENVIRONMENT_NEGATIVE_LEDGER_V7.json")
    require(len(ledger["entries"]) == 5, "ledger entry count")
    require([row["arm_id"] for row in ledger["entries"]] == [ARM_IDS[c] for c in ["C2", "C3", "C4", "C5", "C6"]], "ledger arms")
    require(all(row["missing_byte_artifacts"] for row in ledger["entries"]), "ledger missing bytes")
    require(ledger["terminal"] == EXPECTED_TERMINAL, "ledger terminal")

    checksum_rows = validate_sha256sums()
    print(
        "P5_V7_NATIVE_TASK_ENVIRONMENT_VALIDATED__"
        "1_BOUND__5_BLOCKING__55_OF_126_BOUND__71_BLOCKING__0_OF_6_READY__"
        f"{reference_count}_BYTE_REFERENCES_VERIFIED__{checksum_rows}_PACKET_FILES_HASHED"
    )


if __name__ == "__main__":
    main()
