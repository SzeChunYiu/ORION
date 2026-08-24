#!/usr/bin/env python3
"""Independent stdlib validation for the P3 V6 evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/billy/Documents/Codex/2026-08-23/can-x20")
LANE = ROOT / "work/lane-handoffs/p3-comparator-native-preflight-v6"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str):
    return json.loads((LANE / name).read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    checks: list[dict] = []

    def check(name: str, condition: bool, evidence=None) -> None:
        checks.append({"check": name, "pass": bool(condition), "evidence": evidence})

    json_paths = sorted(p for p in LANE.glob("*.json") if p.name != "VALIDATION_RECEIPT_V6.json")
    parsed = {}
    for p in json_paths:
        try:
            parsed[p.name] = json.loads(p.read_text())
            check(f"json_parse:{p.name}", True)
        except Exception as exc:
            check(f"json_parse:{p.name}", False, f"{type(exc).__name__}: {exc}")

    protocol = load("PROTOCOL_V6.json")
    freeze = load("PROTOCOL_FREEZE_RECEIPT_V6.json")
    check("protocol_freeze_hash", freeze["protocol_sha256"] == sha(LANE / "PROTOCOL_V6.json"), freeze["protocol_sha256"])
    for stem in ["INTERFACE", "K3_INPUT", "K3_LAUNCHER", "K3_STDIN"]:
        artifact = LANE / f"PROTOCOL_{stem}_AMENDMENT_V6.json"
        receipt = load(f"PROTOCOL_{stem}_AMENDMENT_FREEZE_V6.json")
        frozen_sha = receipt.get("sha256", receipt.get("amendment_sha256"))
        check(f"{stem.lower()}_amendment_freeze_hash", frozen_sha == sha(artifact), frozen_sha)

    for key, binding in protocol["inherited_bindings"].items():
        p = Path(binding["path"])
        check(f"inherited_binding_exists:{key}", p.is_file(), str(p))
        check(f"inherited_binding_hash:{key}", p.is_file() and sha(p) == binding["sha256"], binding["sha256"])

    k1 = load("K1_AML_RESULT_V6.json")
    check("k1_terminal", k1["terminal"] == "NATIVE_SMOKE_PASS")
    check("k1_exit_zero", k1["runtime"]["exit_code"] == 0 and not k1["runtime"]["timeout"])
    check("k1_cell_count", k1["native_artifact"]["cell_count"] == 3)
    check("k1_namespace_guards", k1["native_artifact"]["source_namespace_guard"] and k1["native_artifact"]["target_namespace_guard"])

    k2 = load("K2_LOGMAP_RESULT_V6.json")
    check("k2_terminal_guarded_pass", k2["terminal"] == "NATIVE_SMOKE_PASS_WITH_MANDATORY_RDF_HEADER_METADATA_GUARD")
    check("k2_exit_zero", k2["runtime"]["exit_code"] == 0 and not k2["runtime"]["timeout"])
    check("k2_three_rows_each", k2["native_artifacts"]["rdf"]["row_count"] == 3 and k2["native_artifacts"]["tsv"]["row_count"] == 3)
    check("k2_rdf_tsv_equivalence", k2["native_artifacts"]["rdf_tsv_row_equivalence"])
    check("k2_namespace_guards", k2["native_artifacts"]["rdf_source_namespace_guard"] and k2["native_artifacts"]["rdf_target_namespace_guard"])
    check("k2_header_defect_guard", k2["mandatory_metadata_guard"]["status"] == "UPSTREAM_RDF_HEADER_DEFECT_CONFIRMED" and k2["mandatory_metadata_guard"]["duplicate_ontology_1_call_found"])

    k3 = load("K3_BERTMAP_RESULT_V6.json")
    check("k3_terminal_cannot_check", k3["terminal"] == "CANNOT_CHECK_PINNED_DEPENDENCY_API_INCOMPATIBILITY")
    check("k3_nonzero_not_timeout", k3["runtime"]["exit_code"] == 1 and not k3["runtime"]["timeout"])
    check("k3_exact_failure", k3["failure"]["exact_terminal_present_in_stderr"] and k3["failure"]["deeponto_passes_evaluation_strategy"] and k3["failure"]["installed_transformers_constructor_uses_eval_strategy"])
    check("k3_required_artifacts_zero_of_five", k3["required_native_artifact_count"] == 5 and k3["required_native_artifact_present_count"] == 0 and not any(x["exists"] for x in k3["required_native_artifacts"]))
    check("k3_no_training_prediction_scoring", not k3["input_derived_progress_trace"]["training_started"] and not k3["input_derived_progress_trace"]["prediction_started"] and not k3["input_derived_progress_trace"]["performance_scoring_started"])
    check("k3_model_hash_match", k3["model"]["weight_hash_match"])

    result = load("RESULT_V6.json")
    check("overall_two_of_three", result["native_smoke_readiness"]["passed"] == 2 and result["native_smoke_readiness"]["total"] == 3)
    check("overall_v5_unchanged", result["scientific_readiness"] == {"changed_by_v6": False, "v5_comparator_readiness": "0/3"})
    check("overall_no_gold_protected_scoring", not result["gold_or_reference_alignment_accessed"] and not result["protected_data_accessed"] and not result["performance_scoring_performed"])
    check("preserved_v3_exact", result["preserved_terminals"]["v3"] == "PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS__PUBLIC_V3_NO_HARM_SUPERIORITY__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY")
    check("preserved_v4_exact", result["preserved_terminals"]["v4_source_admission"] == "0/7" and result["preserved_terminals"]["v4_comparator_readiness"] == "0/3")
    check("preserved_v5_exact", result["preserved_terminals"]["v5_comparator_readiness"] == "0/3")

    successor = load("K3_V7_COMPATIBILITY_SUCCESSOR_PROTOCOL.json")
    check("successor_prospective_only", successor["status"] == "PROSPECTIVE_NOT_EXECUTED")
    check("successor_wheel_hash_match", successor["candidate_dependency_tuple"]["transformers_wheel_sha256"] == successor["candidate_dependency_tuple"]["transformers_wheel_expected_sha256"])
    check("successor_api_field_source_checked", successor["candidate_dependency_tuple"]["evaluation_strategy_field_present"])

    ledger = load("NEGATIVE_RESULT_LEDGER_V6.json")
    check("negative_ledger_entry_count", len(ledger["entries"]) == 10)
    check("negative_ledger_complete_fields", all(all(e.get(k) for k in ["id", "negative_result", "cause", "residual", "next_discriminator"]) for e in ledger["entries"]))

    manifest = load("RUNTIME_MANIFEST_V6.json")
    check("runtime_manifest_logmap_dependencies", len(manifest["logmap_dependency_jars"]) == 88)
    check("runtime_manifest_python_packages", manifest["python_unique_package_record_count"] == len(manifest["python_packages"]) == 121)

    audit_path = LANE / "RESOURCE_AND_CLEANUP_AUDIT_V6.json"
    if audit_path.exists():
        audit = load(audit_path.name)
        check("cleanup_runtime_removed", audit["post_cleanup"]["temporary_runtime_exists"] is False)
        check("cleanup_raw_large_residue_zero", audit["post_cleanup"]["raw_or_large_residue_file_count"] == 0)
        check("cleanup_pycache_pyc_zero", audit["post_cleanup"]["pycache_directory_count"] == 0 and audit["post_cleanup"]["pyc_file_count"] == 0)

    failed = [c for c in checks if not c["pass"]]
    receipt = {
        "schema_version": "orion.p3.comparator-native-preflight.validation-receipt.v6",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "validator": "validate_v6.py stdlib assertions; no pytest or CI",
        "json_file_count_excluding_receipt": len(json_paths),
        "check_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "checks": checks,
        "terminal": "PASS" if not failed else "FAIL",
    }
    if args.write:
        (LANE / "VALIDATION_RECEIPT_V6.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: receipt[k] for k in ["check_count", "passed", "failed", "terminal"]}, sort_keys=True))
    if failed:
        for item in failed:
            print(json.dumps(item, sort_keys=True))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
