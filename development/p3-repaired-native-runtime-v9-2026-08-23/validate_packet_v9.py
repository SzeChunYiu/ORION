#!/usr/bin/env python3
"""Validate the retained P3 V9 packet after its one failed native attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PROTOCOL_SHA256 = "7e5eac0b04988cf936a9517043e63f8599866d215e1c5b3537fb47271d87f2e8"
RIGHTS_GATE_SHA256 = "1c92df931ee57e6d743484461c43e8d26c8d2e0773eb834be05a4133264a602a"
REQUIRED = (
    "raw_mappings.json",
    "raw_mappings.tsv",
    "extended_mappings.tsv",
    "filtered_mappings.tsv",
    "repaired_mappings.tsv",
)
MATCH = ROOT / "runtime/results/bertmap-out/bertmap/match"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path: str) -> dict[str, Any]:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not an object")
    return value


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-receipt", type=Path, default=ROOT / "VALIDATION_RECEIPT_V9.json")
    args = ap.parse_args()
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = None) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    try:
        protocol = load("PROTOCOL_V9.json")
        freeze = load("PROTOCOL_FREEZE_RECEIPT_V9.json")
        gate = load("RUNTIME_RIGHTS_GATE_V9.json")
        attempt = load("NATIVE_ATTEMPT_LOCK_V9.json")
        execution = load("NATIVE_EXECUTION_RECEIPT_V9.json")
        parser = load("NATIVE_ARTIFACT_CONTRACT_V9.json")
        ledger = load("NEGATIVE_RESULT_LEDGER_V9.json")
        result = load("RESULT_V9.json")
        cleanup = load("CLEANUP_AUDIT_V9.json")
    except Exception as exc:
        receipt = {
            "schema_version": "orion.p3.repaired-native-runtime.validation-receipt.v9",
            "terminal": "FAIL__PACKET_LOAD_ERROR",
            "error": f"{type(exc).__name__}: {exc}",
        }
        args.write_receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 2

    check("protocol_hash", sha256(ROOT / "PROTOCOL_V9.json") == PROTOCOL_SHA256)
    check("protocol_identity", protocol.get("protocol_id") == "P3_V9_BERTMAP_COMPLETE_RUNTIME_RIGHTS_AND_NO_GOLD_NATIVE_SMOKE")
    check("protocol_required_artifacts", protocol.get("required_actual_artifacts") == list(REQUIRED))
    check("protocol_no_retry", protocol.get("unchanged_no_gold_smoke", {}).get("retries") == 0)
    check("protocol_timeout", protocol.get("unchanged_no_gold_smoke", {}).get("wall_seconds") == 1800)
    check("prospective_freeze", freeze.get("native_execution_before_freeze") is False and freeze.get("runtime_staged_before_freeze") is False)
    check("rights_gate_hash", sha256(ROOT / "RUNTIME_RIGHTS_GATE_V9.json") == RIGHTS_GATE_SHA256)
    check("rights_gate_pass", gate.get("checks_passed") == gate.get("checks_total") == 30 and gate.get("native_execution_authorized") is True)
    check("attempt_no_retry", attempt.get("retries_permitted") == 0)
    check("attempt_exact_stdin", attempt.get("stdin_utf8") == r"2g\n")

    check("execution_failed_closed", execution.get("success") is False and execution.get("exit_code") == 1)
    check("execution_not_timeout", execution.get("timed_out") is False)
    check("execution_no_retry", execution.get("retries_used") == execution.get("retries_permitted") == 0)
    check("execution_artifact_incomplete", execution.get("artifacts_complete") is False)
    check("execution_scientific_boundary", execution.get("outcome_boundary", {}).get("scientific_scoring_performed") is False)

    live_present = []
    artifact_hash_match = True
    for name in REQUIRED:
        path = MATCH / name
        present = path.is_file() and not path.is_symlink()
        if present:
            live_present.append(name)
            recorded = execution.get("artifacts", {}).get(name, {})
            artifact_hash_match = artifact_hash_match and recorded.get("sha256") == sha256(path)
    check("four_of_five_artifacts", live_present == list(REQUIRED[:4]), live_present)
    check("partial_artifact_hashes", artifact_hash_match)
    check("repaired_artifact_absent", not (MATCH / "repaired_mappings.tsv").exists())
    check(
        "frozen_parser_failure",
        parser.get("terminal") == "CANNOT_CHECK_NATIVE_ARTIFACT_CONTRACT_FAILURE"
        and parser.get("error") == "repaired_mappings.tsv: required regular non-symlink artifact is absent",
    )

    stdout = (ROOT / "NATIVE_STDOUT_V9.log").read_text(encoding="utf-8", errors="replace")
    stderr = (ROOT / "NATIVE_STDERR_V9.log").read_text(encoding="utf-8", errors="replace")
    completed_markers = (
        "Fine-tuning finished",
        "Finished mapping prediction for each class in the source ontology.",
        "Finished iterative mapping extension",
        "Filtered the extended mappings by a threshold of 0.9995",
    )
    check("positive_stage_markers", all(marker in stdout or marker in stderr for marker in completed_markers))
    check("primary_exception_bound", "java.lang.reflect.InaccessibleObjectException" in stderr)
    check("module_open_cause_bound", 'module java.base does not "opens java.lang"' in stderr)
    check("secondary_missing_file_bound", "FileNotFoundError" in stderr and "mappings_repaired_with_LogMap.tsv" in stderr)

    check("ledger_primary_issue", ledger.get("primary_issue", {}).get("issue_id") == "P3-V9-JAVA17-GUICE4-STRONG-ENCAPSULATION")
    check("ledger_secondary_issue", ledger.get("secondary_issue", {}).get("issue_id") == "P3-V9-DEEPONTO-RUN-JAR-EXIT-STATUS-NOT-PROPAGATED")
    check("ledger_candidate_unexecuted", ledger.get("successor_discriminator", {}).get("status") == "PROSPECTIVE_DESIGN_ONLY__NOT_EXECUTED_IN_V9")
    check("ledger_no_prohibited_action", all(value is False for value in ledger.get("prohibitions_honored", {}).values()))
    check("result_native_readiness", result.get("native_positive_delta", {}).get("native_smoke_ready_after") == "2/3")
    check("result_scientific_readiness", result.get("native_positive_delta", {}).get("scientific_comparator_ready_after") == "0/3")
    check("result_claim_boundary", all(result.get("claim_boundary", {}).get(key) == "CANNOT_CHECK" for key in ("correctness", "performance", "harm", "coverage", "transport", "superiority")))

    check("cleanup_complete", cleanup.get("completed") is True)
    deletion_state = {item["path"]: item.get("exists_after_cleanup") for item in cleanup.get("deleted", [])}
    check("cleanup_targets_absent", deletion_state and all(value is False for value in deletion_state.values()), deletion_state)

    sums_path = ROOT / "SHA256SUMS"
    sums_ok = sums_path.is_file()
    sums_count = 0
    if sums_ok:
        for line in sums_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            try:
                digest, rel = line.split("  ", 1)
                path = ROOT / rel
                sums_ok = sums_ok and path.is_file() and not path.is_symlink() and sha256(path) == digest
                sums_count += 1
            except Exception:
                sums_ok = False
    check("sha256sums", sums_ok and sums_count >= 20, sums_count)

    failed = [item for item in checks if not item["pass"]]
    receipt = {
        "schema_version": "orion.p3.repaired-native-runtime.validation-receipt.v9",
        "terminal": "PASS__PACKET_INTERNAL_CONSISTENCY_AND_CLEANUP_BOUND__NATIVE_AND_SCIENTIFIC_CANNOT_CHECK_PRESERVED" if not failed else "FAIL__PACKET_INTERNAL_CONSISTENCY",
        "authority": "PACKET_INTERNAL_CONSISTENCY_ONLY__NO_NATIVE_SUCCESS_OR_SCIENTIFIC_AUTHORITY",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "checks": checks,
    }
    args.write_receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
