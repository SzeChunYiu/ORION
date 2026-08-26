#!/usr/bin/env python3
"""Fail-closed audit for P12's transfer/negative/successor lifecycle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/orion-22-adaptive-state-reasoning"
AUTHORITY = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V4.json"
V3 = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V3.json"
LIFECYCLE_BINDINGS = {
    "transfer_result_receipt": "top_tier/P12_TRANSFER_ALLOCATION_RESULT_RECEIPT_V1.md",
    "robustness_result_receipt": "top_tier/P12_ROBUSTNESS_STRESS_RESULT_RECEIPT_V1.md",
    "price_aware_preregistration": "top_tier/P12_PRICE_AWARE_SUCCESSOR_PROTOCOL_PREREG_V1.json",
    "price_aware_result": "top_tier/P12_PRICE_AWARE_SUCCESSOR_RESULT_V1.json",
    "price_aware_result_receipt": "top_tier/P12_PRICE_AWARE_SUCCESSOR_RESULT_RECEIPT_V1.md",
    "selection_sufficiency_receipt": "top_tier/P12_SELECTION_SUFFICIENCY_RESULT_RECEIPT_V1.md",
    "certificate_necessity_receipt": "top_tier/P12_CERTIFICATE_NECESSITY_RESULT_RECEIPT_V1.md",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot parse {label}: {exc}")
        return {}
    return value if isinstance(value, dict) else {}


def audit(authority_path: Path = AUTHORITY, *, check_package: bool = True) -> dict[str, object]:
    errors: list[str] = []
    authority = _load(authority_path, errors, "V4 authority")
    v3 = _load(V3, errors, "V3 authority")
    if authority.get("schema") != "ORION.P12.ActiveClaimAuthority.v4":
        errors.append("wrong schema")
    if authority.get("paper_id") != "P12":
        errors.append("wrong paper id")
    if authority.get("active_terminal") != v3.get("active_terminal"):
        errors.append("V3 active terminal changed")
    for key in ("active_claim_leaf", "historical_boundary_leaf"):
        if authority.get(key) != v3.get(key):
            errors.append(f"V3 {key} changed")
    if authority.get("top_tier_submission_allowed") is not False:
        errors.append("top-tier submission gate must remain false")
    if authority.get("promotion_allowed") != v3.get("promotion_allowed"):
        errors.append("V3 bounded promotion flag changed")
    if authority.get("external_public_benchmark_status") != "CANNOT_CHECK_NO_BOUND_PUBLIC_DATA_RESULT":
        errors.append("public benchmark CANNOT_CHECK boundary missing")
    if authority.get("artifact_identity_note") != (
        "No P12C artifact exists. The adverse landed study is "
        "P12_ROBUSTNESS_STRESS_V1; the later successor is conditional on exact "
        "published charge certificates and is not public-data validation."
    ):
        errors.append("P12C identity boundary missing or drifted")
    required_forbidden = {
        "PRICE_OR_SHIFT_ROBUSTNESS_OF_V1_ALLOCATOR",
        "FORWARD_TIME_DEPLOYABILITY_FROM_EXACT_CERTIFICATES",
        "SCIENCEAGENTBENCH_OR_EXTERNAL_TRANSFER",
        "P12C_ARTIFACT_IDENTITY",
    }
    if not required_forbidden.issubset(set(authority.get("forbidden_promotions", []))):
        errors.append("required lifecycle forbidden promotions missing")

    transfer = authority.get("transfer_claim_leaf", {})
    if transfer.get("terminal") != "P12_TRANSFER_ALLOCATION_V1_SUPPORTED":
        errors.append("transfer terminal drifted")
    if transfer.get("scope") != {
        "allocator_regret_positive_cells": 0,
        "cases": 9,
        "domain_specific_parameters": 0,
        "domains": ["SAT_PROPAGATION", "PATH_PLANNING", "KNAPSACK"],
        "exact_outputs_all_arms": True,
    }:
        errors.append("transfer scope drifted")
    robust = authority.get("robustness_boundary_leaf", {})
    if (
        robust.get("authority") != "BINDING_NEGATIVE_BOUNDARY"
        or robust.get("terminal") != "P12_ROBUSTNESS_STRESS_V1_EXECUTED"
        or robust.get("price_axis") != "BROKEN"
        or robust.get("distribution_shift_axis") != "BROKEN"
        or robust.get("flat_replication") != "SUPPORTED"
        or robust.get("retuned") is not False
    ):
        errors.append("robustness negative drifted")
    successor = authority.get("price_aware_successor_leaf", {})
    if successor.get("terminal") != "P12_PRICE_AWARE_SUCCESSOR_SUPPORTED":
        errors.append("successor terminal drifted")
    if successor.get("status") != "SUPPORTED_CONDITIONAL_ON_EXACT_PUBLISHED_CERTIFICATES":
        errors.append("successor conditional status drifted")
    if successor.get("battery_cells_cross_checked") != 195:
        errors.append("successor coverage drifted")
    if successor.get("successor_positive_cells") != 0:
        errors.append("successor regret cells drifted")
    if successor.get("new_free_parameters") != 0:
        errors.append("successor free-parameter count drifted")
    if successor.get("forward_time_deployability") != "CANNOT_CHECK":
        errors.append("forward-time boundary missing")

    bindings = authority.get("evidence_bindings", {})
    for key, rel in LIFECYCLE_BINDINGS.items():
        expected_path = f"papers/orion-22-adaptive-state-reasoning/{rel}"
        item = bindings.get(key)
        if not isinstance(item, dict) or item.get("artifact") != expected_path:
            errors.append(f"missing or wrong lifecycle binding: {key}")
            continue
        path = ROOT / expected_path
        if not path.is_file() or item.get("sha256") != _sha(path):
            errors.append(f"lifecycle digest mismatch: {key}")
    for key, item in v3.get("evidence_bindings", {}).items():
        if bindings.get(key) != item:
            errors.append(f"inherited V3 binding changed: {key}")

    result = _load(PAPER / LIFECYCLE_BINDINGS["price_aware_result"], errors, "price-aware result")
    if result.get("terminal") != "P12_PRICE_AWARE_SUCCESSOR_SUPPORTED":
        errors.append("bound result terminal drifted")
    before_after = result.get("before_after", {})
    if before_after.get("verdicts_before") != {
        "price_axis": "BROKEN",
        "distribution_shift_axis": "BROKEN",
    }:
        errors.append("bound result did not retain both prior negatives")
    if before_after.get("successor_positive_cells") != 0:
        errors.append("bound successor regret cells drifted")
    criteria = result.get("success_criteria", {})
    if criteria.get("SC4_two_implementations", {}).get("cells_cross_checked") != {
        "case_regime_cells": 180,
        "joint_mix_regime_cells": 15,
    }:
        errors.append("bound two-implementation coverage drifted")

    required = {
        PAPER / "README.md": ("both **BROKEN**", "CANNOT_CHECK", "P12_ACTIVE_CLAIM_AUTHORITY_V4.json"),
        PAPER / "CLAIM_EVIDENCE_LEDGER.md": ("NEGATIVE / FALSE", "195 cells", "P12C"),
        PAPER / "PEER_REVIEW_READINESS.md": ("top-tier-submission-ready", "CANNOT_CHECK"),
        PAPER / "manuscript/sections/00-abstract.md": ("195", "BROKEN", "external"),
        PAPER / "manuscript/sections/05-results.md": ("price-axis verdict is **BROKEN**", "without retuning", "7,147,140"),
        PAPER / "manuscript/sections/07-related-work-and-limitations.md": ("P12C", "ScienceAgentBench", "CANNOT_CHECK"),
        PAPER / "manuscript/sections/08-discussion-and-conclusion.md": ("P12_ACTIVE_CLAIM_AUTHORITY_V4.json", "conditional"),
    }
    for path, phrases in required.items():
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path.relative_to(ROOT)} missing: {phrase}")

    if check_package:
        manifest = _load(PAPER / "CONTENT_MANIFEST_V1.json", errors, "manifest")
        paths = {
            item.get("path")
            for item in manifest.get("bound_files", [])
            if isinstance(item, dict)
        }
        required_paths = {
            str(AUTHORITY.relative_to(ROOT)),
            str(Path(__file__).resolve().relative_to(ROOT)),
            str((PAPER / "manuscript/main.pdf").relative_to(ROOT)),
            *(f"papers/orion-22-adaptive-state-reasoning/{v}" for v in LIFECYCLE_BINDINGS.values()),
        }
        missing = sorted(required_paths - paths)
        if missing:
            errors.append(f"manifest missing paths: {missing}")
        sums = {}
        try:
            for line in (PAPER / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
                digest, path = line.split("  ", 1)
                sums[path] = digest
        except (OSError, ValueError) as exc:
            errors.append(f"cannot parse SHA256SUMS: {exc}")
        for path in required_paths:
            if (ROOT / path).is_file() and sums.get(path) != _sha(ROOT / path):
                errors.append(f"SHA256SUMS missing or stale: {path}")

    return {
        "schema": "orion.p12.lifecycle-integration-check.v4",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "external_validation": "CANNOT_CHECK",
        "top_tier_submission_allowed": False,
    }


if __name__ == "__main__":
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
