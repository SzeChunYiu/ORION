#!/usr/bin/env python3
"""Packet-local fail-closed validation; not pytest or repository CI."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TERMINAL = (
    "P3_V15_PROVIDER_NATIVE_OAEI_101_103_IDENTITY_PASS__EXACT_VERSION_RIGHTS_"
    "ONTOLOGY_REFERENCE_AND_SAME_UNIVERSE_AML_BOUND__REFERENCE_SEMANTICS_UNPARSED_"
    "ONE_BERTMAP_SUCCESSOR_AUTHORIZED__SCIENTIFIC_READINESS_ZERO_OF_THREE_UNCHANGED"
)


def load(name: str) -> dict[str, Any]:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def sha(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main() -> None:
    protocol = load("PROTOCOL_V15.json")
    result = load("RESULT_V15.json")
    receipt = load("RECEIPT_V15.json")
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, evidence: Any = None) -> None:
        checks.append({"check": name, "pass": bool(condition), "evidence": evidence})
        if not condition:
            raise AssertionError(f"{name}: {evidence!r}")

    check("protocol_prefrozen", protocol["frozen_before_execution"] is True)
    check("terminal_file_exact", (ROOT / "TERMINAL_V15.txt").read_text(encoding="utf-8") == TERMINAL + "\n")
    check("result_terminal", result["terminal"] == TERMINAL)
    check("receipt_terminal", receipt["terminal"] == TERMINAL)
    check("receipt_protocol_hash", receipt["protocol_sha256"] == sha("PROTOCOL_V15.json"))
    check("live_gate_all_pass", receipt["checks_passed"] == receipt["checks_total"] == 70)
    check("technical_failure_preserved", receipt["identity_gate_invocations_total"] == 2 and (ROOT / "ATTEMPT_1_FAILURE.txt").is_file())
    check("technical_failure_no_outcome", receipt["prior_technical_invocations"]["outcomes_opened"] is False)
    check("provider_live_http", all(row["http_status"] == 200 for row in receipt["http_receipts"].values()))
    check("provider_archive_not_retained", result["execution_boundary"]["archive_written_to_disk"] is False)
    check("reference_semantics_unparsed", result["execution_boundary"]["reference_semantics_parsed"] is False)
    check("zero_gold_rows", result["execution_boundary"]["public_gold_rows_interpreted"] == 0)
    check("zero_metrics", result["execution_boundary"]["metrics_computed"] == 0)
    check("zero_scoring", result["execution_boundary"]["scientific_scoring_performed"] is False)
    check("zero_matcher_attempts", result["execution_boundary"]["matcher_attempts"] == 0)
    check("zero_java_attempts", result["execution_boundary"]["java_attempts"] == 0)
    check("zero_training_attempts", result["execution_boundary"]["training_attempts"] == 0)
    check("zero_prediction_attempts", result["execution_boundary"]["prediction_attempts"] == 0)
    check("zero_repair_attempts", result["execution_boundary"]["repair_attempts"] == 0)
    check("provider_pair_bound", all(result["admission"][key] is True for key in (
        "exact_provider_native_case_found", "exact_version_bound", "rights_bound",
        "source_ontology_hash_bound", "target_ontology_hash_bound", "reference_hash_bound",
        "same_universe_comparator_identity_bound", "one_separate_bertmap_successor_authorized"
    )))
    check("source_hash", result["provider_native_pair"]["source"]["sha256"] == protocol["selected_provider_native_pair"]["source"]["sha256"])
    check("target_hash", result["provider_native_pair"]["target"]["sha256"] == protocol["selected_provider_native_pair"]["target"]["sha256"])
    check("reference_hash", result["provider_native_pair"]["reference"]["sha256"] == protocol["selected_provider_native_pair"]["reference"]["sha256"])
    check("aml_output_hash", result["same_universe_comparator"]["pre_reference_output"]["output_sha256"] == protocol["same_universe_comparator"]["expected_target_103_output_sha256"])
    check("readiness_unchanged", result["blocker_delta"]["scientific_comparator_readiness"] == "0/3_TO_0/3")
    check("not_top_tier_ready", result["blocker_delta"]["top_tier_submission_ready"] is False)
    check("all_scientific_claims_cannot_check", set(result["claim_boundary"].values()) == {"CANNOT_CHECK"})
    check("result_output_hash", receipt["outputs"]["result"]["sha256"] == sha("RESULT_V15.json"))
    check("terminal_output_hash", receipt["outputs"]["terminal"]["sha256"] == sha("TERMINAL_V15.txt"))

    validation = {
        "schema_version": "orion.p3.provider-native-identity.validation.v15",
        "terminal": "P3_V15_PACKET_LOCAL_VALIDATION_PASS",
        "checks_passed": sum(row["pass"] for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "validated_hashes": {
            name: sha(name) for name in (
                "PROTOCOL_V15.json", "RESULT_V15.json", "RECEIPT_V15.json",
                "TERMINAL_V15.txt", "SCIENTIFIC_REPORT_V15.md",
                "ATTEMPT_1_FAILURE.txt", "run_identity_gate_v15.py", "validate_v15.py"
            )
        },
    }
    (ROOT / "VALIDATION_RECEIPT_V15.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "terminal": validation["terminal"],
        "checks": f"{validation['checks_passed']}/{validation['checks_total']}",
        "validation_sha256": sha("VALIDATION_RECEIPT_V15.json"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
