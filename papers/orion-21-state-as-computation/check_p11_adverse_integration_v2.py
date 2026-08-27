#!/usr/bin/env python3
"""Fail-closed audit for P11's adverse query-family integration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/orion-21-state-as-computation"
AUTHORITY = PAPER / "P11_ACTIVE_CLAIM_AUTHORITY_V2.json"
AUTHORITY_V1 = PAPER / "P11_ACTIVE_CLAIM_AUTHORITY_V1.json"
PROTOCOL_SHA = "16147dd984776994279623cde3847bbeb48ec198e8b491d5644c68dc40e1f995"
COUNTS = {"KNN": 5, "LINEAR": 3, "RBF": 5}
QUERY_BINDINGS = {
    "query_family_binding": (
        "papers/orion-21-state-as-computation/top_tier/"
        "p11_query_family_phase_binding_v1.json",
        "0c944d6215d0f8e993e31685c2fe20f5539558a05aa4d5b8a1caf876c7e36d06",
    ),
    "query_family_independent": (
        "papers/orion-21-state-as-computation/top_tier/"
        "p11_query_family_phase_independent_v1.json",
        "b1e92a6be419a26d442fd0e0e6a8026279a70686e3f6b7b09ea64700b8742760",
    ),
    "query_family_primary": (
        "papers/orion-21-state-as-computation/top_tier/"
        "p11_query_family_phase_primary_v1.json",
        "9a1f1f9b62955296bcff891f1f93f97af03448d311ae63b62a95d407e3de138f",
    ),
    "query_family_receipt": (
        "papers/orion-21-state-as-computation/top_tier/"
        "P11_QUERY_FAMILY_PHASE_RESULT_RECEIPT_V1.md",
        "489f9d667e7d45a24f6146dd5dffde4ad2abb65c8aa20763b8e46b12a1a4dfe3",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot parse {label}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label} is not a JSON object")
        return {}
    return value


def audit(authority_path: Path = AUTHORITY, *, check_package: bool = True) -> dict[str, object]:
    errors: list[str] = []
    authority = _load(authority_path, errors, "V2 authority")
    prior = _load(AUTHORITY_V1, errors, "V1 authority")

    if authority.get("schema") != "ORION.P11.ActiveClaimAuthority.v2":
        errors.append("wrong V2 schema")
    if authority.get("paper_id") != "P11":
        errors.append("wrong paper id")
    if authority.get("active_terminal") != "P11_WIDTH_CONDITIONED_AUTHORITY_SUPPORTED":
        errors.append("active terminal must remain the V1 width-conditioned terminal")
    if authority.get("promotion_allowed") is not True:
        errors.append("promotion flag drifted")
    if authority.get("active_claim_leaf") != prior.get("active_claim_leaf"):
        errors.append("V2 active claim leaf differs from V1")
    if authority.get("historical_boundary_leaf") != prior.get("historical_boundary_leaf"):
        errors.append("V2 historical boundary leaf differs from V1")

    adverse = authority.get("adverse_query_family_leaf", {})
    if adverse.get("authority") != "BINDING_NEGATIVE_BOUNDARY":
        errors.append("wrong adverse authority class")
    if adverse.get("terminal") != "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET":
        errors.append("wrong or missing adverse terminal")
    if adverse.get("frozen_gate") != (
        "at_least_8_of_10_responsibilities_within_0.02_quality_tolerance"
    ):
        errors.append("adverse frozen gate drifted")
    if adverse.get("observed_support_counts") != {**COUNTS, "responsibilities": 10}:
        errors.append("adverse support counts drifted")
    if adverse.get("retuned") is not False:
        errors.append("negative retune boundary missing")

    bindings = authority.get("evidence_bindings", {})
    prior_bindings = prior.get("evidence_bindings", {})
    for name, binding in prior_bindings.items():
        if bindings.get(name) != binding:
            errors.append(f"V2 weakened or changed inherited binding: {name}")
    actual_query_bindings = {
        name: (value.get("artifact"), value.get("sha256"))
        for name, value in bindings.items()
        if name.startswith("query_family_") and isinstance(value, dict)
    }
    if actual_query_bindings != QUERY_BINDINGS:
        errors.append("query-family binding key/path/hash set drifted")
    for name, binding in bindings.items():
        if not isinstance(binding, dict) or set(binding) != {"artifact", "sha256"}:
            errors.append(f"malformed binding: {name}")
            continue
        path = ROOT / str(binding["artifact"])
        if not path.is_file():
            errors.append(f"missing binding {name}: {path}")
        elif _sha(path) != binding["sha256"]:
            errors.append(f"digest mismatch: {name}")

    primary = _load(ROOT / QUERY_BINDINGS["query_family_primary"][0], errors, "primary")
    independent = _load(
        ROOT / QUERY_BINDINGS["query_family_independent"][0], errors, "independent"
    )
    binding = _load(ROOT / QUERY_BINDINGS["query_family_binding"][0], errors, "binding")
    if primary.get("schema") != "P11.QueryFamilyPhaseResult.v1":
        errors.append("primary schema drifted")
    if primary.get("terminal") != "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET":
        errors.append("primary terminal drifted")
    if primary.get("support_counts") != COUNTS or primary.get("query_count") != 10:
        errors.append("primary counts drifted")
    if independent.get("schema") != "P11.QueryFamilyPhaseIndependent.v1":
        errors.append("independent schema drifted")
    if independent.get("terminal") != "P11_QUERY_FAMILY_PHASE_SECOND_CHECKER_GATE_NOT_MET":
        errors.append("independent terminal drifted")
    if independent.get("support_counts") != COUNTS:
        errors.append("independent counts drifted")
    for label, payload in (("primary", primary), ("independent", independent), ("binding", binding)):
        if payload.get("protocol_sha256") != PROTOCOL_SHA:
            errors.append(f"{label} protocol binding drifted")
    for key in (
        "byte_replay_identical",
        "negative_retained",
        "no_retuning_performed",
        "two_implementations_agree",
    ):
        if binding.get(key) is not True:
            errors.append(f"binding flag drifted: {key}")
    if binding.get("recorded_terminal") != "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET":
        errors.append("binding recorded terminal drifted")
    gate = binding.get("frozen_gate", {})
    if gate != {
        "frozen_positive_terminal": False,
        "gate_future_query_cost": True,
        "gate_linear_ge_8_of_10": False,
        "gate_memory_crossover": True,
        "gate_stronger_ge_8_of_10": False,
        "knn_supported_queries": 5,
        "linear_supported_queries": 3,
        "rbf_supported_queries": 5,
    }:
        errors.append("binding frozen gate or counts drifted")
    if binding.get("primary", {}).get("sha256") != QUERY_BINDINGS["query_family_primary"][1]:
        errors.append("binding-to-primary digest drifted")
    if binding.get("independent", {}).get("sha256") != QUERY_BINDINGS["query_family_independent"][1]:
        errors.append("binding-to-independent digest drifted")

    required = {
        PAPER / "README.md": ("P11_ACTIVE_CLAIM_AUTHORITY_V2.json", "no artifact with that identity exists"),
        PAPER / "CLAIM_EVIDENCE_LEDGER.md": ("P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET", "3/10", "5/10"),
        PAPER / "MANUSCRIPT.md": ("P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET", "3/10", "5/10", "thresholds were not retuned"),
        PAPER / "manuscript/sections/00-abstract.md": ("3/10", "5/10", "8/10"),
        PAPER / "manuscript/sections/05-hostile-decoder-substitution.md": ("P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET", "thresholds were not retuned"),
        PAPER / "manuscript/sections/08-limitations-discussion-conclusion.md": ("3/10", "5/10", "P11_ACTIVE_CLAIM_AUTHORITY_V2.json"),
    }
    for path, phrases in required.items():
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path.relative_to(ROOT)} missing: {phrase}")
    if "FAMILY_SCALE_COMPILATION_SUPPORT_ON_DIGITS" not in authority.get("forbidden_promotions", []):
        errors.append("family-scale forbidden promotion missing")

    if check_package:
        manifest = _load(PAPER / "CONTENT_MANIFEST_V1.json", errors, "content manifest")
        manifest_paths = {
            item.get("path")
            for item in manifest.get("bound_files", [])
            if isinstance(item, dict)
        }
        required_paths = {
            str(AUTHORITY.relative_to(ROOT)),
            str(Path(__file__).resolve().relative_to(ROOT)),
            str((PAPER / "MANUSCRIPT.md").relative_to(ROOT)),
            *(path for path, _ in QUERY_BINDINGS.values()),
        }
        missing = sorted(required_paths - manifest_paths)
        if missing:
            errors.append(f"content manifest missing paths: {missing}")
        sums: dict[str, str] = {}
        try:
            for line in (PAPER / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
                digest, path = line.split("  ", 1)
                sums[path] = digest
        except (OSError, ValueError) as exc:
            errors.append(f"cannot parse SHA256SUMS: {exc}")
        for path in required_paths:
            full = ROOT / path
            if full.is_file() and sums.get(path) != _sha(full):
                errors.append(f"SHA256SUMS missing or stale: {path}")

    return {
        "schema": "orion.p11.adverse-integration-check.v2",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "scientific_authority_delta": "BOUNDARY_NARROWING_ONLY",
        "external_validation": "CANNOT_CHECK",
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
