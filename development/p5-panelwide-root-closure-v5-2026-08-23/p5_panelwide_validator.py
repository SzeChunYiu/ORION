#!/usr/bin/env python3
"""Native scientific validator for the P5 V5 panel-wide closure packet."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPECTED_TERMINAL = (
    "P5_V5_PANELWIDE_ROOT_CAUSE_CONTRACT_AND_SIX_PARSER_DISPATCH_BOUND__"
    "EIGHTY_FOUR_BLOCKER_INSTANCES_COLLAPSED_TO_FIVE_ROOT_WORK_PACKAGES__"
    "ZERO_ARM_FIELD_BINDINGS_CREATED_WITHOUT_MISSING_EXTERNAL_OR_ARM_SPECIFIC_EVIDENCE__"
    "FORTY_TWO_OF_ONE_HUNDRED_TWENTY_SIX_FIELDS_BOUND__EIGHTY_FOUR_BLOCKING__"
    "ZERO_OF_SIX_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    checks = 0
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(label)

    json_names = [
        "P5_PANELWIDE_ROOT_CLOSURE_PROTOCOL_V5.json",
        "P5_PANELWIDE_BLOCKER_EQUIVALENCE_REGISTRY_V5.json",
        "P5_PANELWIDE_ROOT_CLOSURE_RESULT_V5.json",
        "P5_PANELWIDE_ROOT_CLOSURE_NEGATIVE_LEDGER_V5.json",
    ]
    payloads = {}
    for name in json_names:
        try:
            payloads[name] = json.loads((HERE / name).read_text())
            check(True, f"json:{name}")
        except Exception:
            check(False, f"json:{name}")

    protocol = payloads[json_names[0]]
    registry = payloads[json_names[1]]
    result = payloads[json_names[2]]
    negative = payloads[json_names[3]]

    check(protocol["outcomes_accessed"] is False, "protocol:outcomes_accessed_false")
    check(protocol["protected_outcomes_accessed"] is False, "protocol:protected_false")
    check(protocol["arm_executions_performed"] == 0, "protocol:no_arm_execution")
    check(protocol["models_accessed_or_executed"] is False, "protocol:no_model_execution")
    check(protocol["benchmarks_accessed_or_executed"] is False, "protocol:no_benchmark_execution")
    check(len(protocol["required_field_paths"]) == 21, "protocol:21_fields")
    check(protocol["common_parser_contract"]["parser_count"] == 6, "protocol:6_parsers")
    check(protocol["terminal"] == EXPECTED_TERMINAL, "protocol:terminal")

    check(registry["arm_count"] == 6, "registry:6_arms")
    check(registry["field_instances_total"] == 126, "registry:126_instances")
    check(registry["v4_bound_instances"] == 42, "registry:42_v4_bound")
    check(registry["v4_blocking_instances"] == 84, "registry:84_v4_blocking")
    check(registry["v5_new_arm_field_bindings"] == 0, "registry:0_new_bindings")
    check(registry["v5_bound_instances"] == 42, "registry:42_v5_bound")
    check(registry["v5_blocking_instances"] == 84, "registry:84_v5_blocking")
    check(registry["blocker_delta"] == 0, "registry:delta_zero")
    check(sum(x["blocking_instances"] for x in registry["equivalence_classes"]) == 84, "registry:equivalence_partition")
    check(sum(x["blocking_instances"] for x in registry["root_work_packages"]) == 84, "registry:root_partition")
    check(len(registry["equivalence_classes"]) == 14, "registry:14_equivalence_classes")
    check(len(registry["root_work_packages"]) == 5, "registry:5_roots")
    check(all(len(a["bound_fields"]) + len(a["blocking_fields"]) == 21 for a in registry["arms"]), "registry:per_arm_21")
    check(sum(a["bound_field_count"] for a in registry["arms"]) == 42, "registry:per_arm_bound_sum")
    check(sum(a["blocking_field_count"] for a in registry["arms"]) == 84, "registry:per_arm_blocking_sum")
    check(all(a["execution_ready"] is False for a in registry["arms"]), "registry:zero_ready")
    check(registry["terminal"] == EXPECTED_TERMINAL, "registry:terminal")
    check(registry["matched_exposure_audit"]["status"] == "BLOCKING_COMMON_EFFECTIVE_VECTOR_NOT_YET_FROZEN", "matched_exposure:blocking")
    check(registry["matched_exposure_audit"]["arm_field_delta"] == 0, "matched_exposure:no_field_inflation")
    boundary = registry["fresh_verification_boundary"]
    check(boundary["v4_field_registry_result_and_parser_hashes"] == "PASS_FOR_ALL_SIX", "assurance:core_six_pass")
    check(boundary["packet_sha256sum_manifests"]["C4"]["status"] == "CANNOT_CHECK_MANIFEST_MISMATCH", "assurance:c4_manifest_negative_retained")
    check(len(boundary["packet_sha256sum_manifests"]["C4"]["failures"]) == 1, "assurance:c4_one_manifest_mismatch")
    check(boundary["native_validator_observations"]["C6"]["status"] == "CANNOT_CHECK", "assurance:c6_native_cannot_check")

    for arm in registry["arms"]:
        rp = ROOT / arm["v4_registry_path"]
        resultp = ROOT / arm["v4_result_path"]
        pp = ROOT / arm["parser"]["path"]
        check(rp.is_file() and sha256(rp) == arm["v4_registry_sha256"], f"{arm['arm_code']}:registry_hash")
        check(resultp.is_file() and sha256(resultp) == arm["v4_result_sha256"], f"{arm['arm_code']}:result_hash")
        check(pp.is_file() and sha256(pp) == arm["parser"]["sha256"], f"{arm['arm_code']}:parser_hash")

    exact = result["exact_recomputation"]
    check(exact["v5_bound_instances"] == 42, "result:42_bound")
    check(exact["v5_blocking_instances"] == 84, "result:84_blocking")
    check(exact["blocker_delta"] == 0, "result:delta_zero")
    check(result["execution"]["confirmatory_ready_arms"] == 0, "result:zero_ready")
    check(result["panelwide_repairs"]["arm_field_bindings_created"] == 0, "result:no_inflation")
    check(result["panelwide_repairs"]["coordination_work_item_delta"] == -79, "result:coordination_delta_minus_79")
    check(result["preserved_claims"]["performance"] == "CANNOT_CHECK", "result:performance_boundary")
    check(result["preserved_claims"]["superiority"] == "CANNOT_CHECK", "result:superiority_boundary")
    check(result["preserved_claims"]["top_tier_publication_readiness"] == "NOT_ESTABLISHED", "result:readiness_boundary")
    check(result["terminal"] == EXPECTED_TERMINAL, "result:terminal")

    check(negative["root_count"] == 5, "negative:5_roots")
    check(negative["blocking_instances_before"] == 84, "negative:84_before")
    check(negative["blocking_instances_after"] == 84, "negative:84_after")
    check(negative["arm_field_blocker_delta"] == 0, "negative:delta_zero")
    check(all(x["preserved_terminal"] == "CANNOT_CHECK" for x in negative["records"]), "negative:preserved")
    check(negative["terminal"] == EXPECTED_TERMINAL, "negative:terminal")

    terminal_text = (HERE / "TERMINAL_V5.txt").read_text().strip()
    check(terminal_text == EXPECTED_TERMINAL, "terminal_file:exact")

    gate = subprocess.run(
        [sys.executable, str(HERE / "p5_panelwide_contract_gate.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    check(gate.returncode == 2, "gate:fail_closed_without_handoff")
    check("eligible_to_execute" in gate.stdout and "false" in gate.stdout.lower(), "gate:refusal_receipt")

    manifest_entries = []
    for line in (HERE / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        manifest_entries.append((digest, name))
    expected_manifest_names = sorted(p.name for p in HERE.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    check(sorted(name for _, name in manifest_entries) == expected_manifest_names, "manifest:exact_file_set")
    check(all(sha256(HERE / name) == digest for digest, name in manifest_entries), "manifest:all_hashes")

    if failures:
        print(json.dumps({"checks": checks, "failures": failures, "status": "FAIL"}, indent=2))
        return 1
    print(json.dumps({"checks": checks, "failures": 0, "status": "PASS", "terminal": EXPECTED_TERMINAL}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
