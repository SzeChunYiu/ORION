#!/usr/bin/env python3
"""Synthetic, outcome-free conformance for the frozen P5 V2 adapter contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

UNRESOLVED = "UNRESOLVED"
SUCCESS = "COMPLETE_SUCCESS"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(case: dict, support: dict[str, set[str]]) -> tuple[str, str]:
    arm = case["arm_id"]
    status = case["native_status"]
    certificates = case.get("certificate_classes", [])
    writes = case.get("write_classes", [])
    if status != SUCCESS:
        return UNRESOLVED, f"NATIVE_{status}_PRESERVED"
    if case.get("mixed_fibre_witness", False):
        return UNRESOLVED, "MIXED_FIBRE"
    if len(certificates) != 1:
        return UNRESOLVED, "CERTIFICATE_NOT_UNIQUE"
    if len(writes) != 1:
        return UNRESOLVED, "WRITE_SURFACE_NOT_UNIQUE"
    if certificates[0] != writes[0]:
        return UNRESOLVED, "CERTIFICATE_WRITE_MISMATCH"
    candidate = certificates[0]
    if candidate not in support[arm]:
        return UNRESOLVED, "UNSUPPORTED_CLASS"
    if arm == "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY":
        if not case.get("solver_bytes_unchanged", False):
            return UNRESOLVED, "SOLVER_DRIFT"
        if not case.get("evaluator_only_mutation", False):
            return UNRESOLVED, "NON_EVALUATOR_MUTATION"
        if not case.get("development_validity_passed", False):
            return UNRESOLVED, "DEVELOPMENT_VALIDITY_NOT_PASSED"
    return candidate, "UNIQUE_SUPPORTED_CERTIFIED_FIBRE"


def build_cases(protocol: dict, fixtures: dict) -> list[dict]:
    cases: list[dict] = []
    support = {
        arm: row["conditionally_supported"]
        for arm, row in protocol["arm_support_sets"].items()
    }
    for arm_row in fixtures["arms"]:
        cases.append(
            {
                "case_id": f'{arm_row["arm_id"]}__MIXED',
                "arm_id": arm_row["arm_id"],
                "native_status": SUCCESS,
                "certificate_classes": [],
                "write_classes": [],
                "mixed_fibre_witness": True,
                "expected": UNRESOLVED,
            }
        )
    for arm, classes in fixtures["positive_conformance_templates"].items():
        for cls in classes:
            case = {
                "case_id": f"{arm}__POSITIVE__{cls}",
                "arm_id": arm,
                "native_status": SUCCESS,
                "certificate_classes": [cls],
                "write_classes": [cls],
                "expected": cls,
            }
            if arm == "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY":
                case.update(
                    solver_bytes_unchanged=True,
                    evaluator_only_mutation=True,
                    development_validity_passed=True,
                )
            cases.append(case)
    proper = protocol["revision_classes"][:-1]
    for arm, allowed in support.items():
        unsupported = [c for c in proper if c not in allowed]
        for cls in unsupported:
            cases.append(
                {
                    "case_id": f"{arm}__UNSUPPORTED__{cls}",
                    "arm_id": arm,
                    "native_status": SUCCESS,
                    "certificate_classes": [cls],
                    "write_classes": [cls],
                    "expected": UNRESOLVED,
                }
            )
    for arm, allowed in support.items():
        cert = allowed[0] if allowed else proper[0]
        write = next((c for c in proper if c != cert), proper[-1])
        cases.append(
            {
                "case_id": f"{arm}__MISMATCH",
                "arm_id": arm,
                "native_status": SUCCESS,
                "certificate_classes": [cert],
                "write_classes": [write],
                "expected": UNRESOLVED,
            }
        )
    for arm in support:
        for terminal in fixtures["negative_terminal_templates"]:
            cases.append(
                {
                    "case_id": f"{arm}__TERMINAL__{terminal}",
                    "arm_id": arm,
                    "native_status": terminal,
                    "certificate_classes": [],
                    "write_classes": [],
                    "expected": UNRESOLVED,
                }
            )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text())
    fixtures = json.loads(args.fixtures.read_text())
    assert protocol["freeze_boundary"]["native_output_examples_accessed_before_freeze"] is False
    assert fixtures["native_output_examples_used"] is False
    assert set(protocol["arm_support_sets"]) == {
        row["arm_id"] for row in fixtures["arms"]
    }
    fibre_checks = []
    for row in fixtures["arms"]:
        classes = {w["minimal_class"] for w in row["counterexample_worlds"]}
        assert len(classes) >= 2
        assert row["expected_without_certificate"] == UNRESOLVED
        fibre_checks.append(
            {
                "arm_id": row["arm_id"],
                "same_visible_symptom": row["same_visible_symptom"],
                "distinct_latent_classes": sorted(classes),
                "mixed_fibre_proved": True,
            }
        )

    support = {
        arm: set(row["conditionally_supported"])
        for arm, row in protocol["arm_support_sets"].items()
    }
    cases = build_cases(protocol, fixtures)
    rows = []
    for case in cases:
        observed, reason = emit(case, support)
        rows.append(
            {
                "case_id": case["case_id"],
                "arm_id": case["arm_id"],
                "expected": case["expected"],
                "observed": observed,
                "reason": reason,
                "passed": observed == case["expected"],
            }
        )
    assert all(row["passed"] for row in rows)
    by_output = Counter(row["observed"] for row in rows)
    by_arm = Counter(row["arm_id"] for row in rows)
    by_reason = Counter(row["reason"] for row in rows)
    receipt = {
        "schema_version": "orion.p5.terminal-adapter-synthetic-conformance-receipt.v2",
        "protocol_id": protocol["protocol_id"],
        "authority": "SYNTHETIC_FIXTURE_CONFORMANCE_ONLY__NOT_COMPARATOR_PERFORMANCE",
        "protocol_sha256": digest(args.protocol),
        "fixture_sha256": digest(args.fixtures),
        "native_output_examples_accessed": False,
        "public_or_protected_outcome_rows_accessed": False,
        "comparators_executed": False,
        "fibre_counterexample_checks": fibre_checks,
        "n_fibre_counterexamples": len(fibre_checks),
        "n_cases": len(rows),
        "n_passed": sum(row["passed"] for row in rows),
        "n_failed": sum(not row["passed"] for row in rows),
        "observed_output_counts": dict(sorted(by_output.items())),
        "cases_by_arm": dict(sorted(by_arm.items())),
        "reason_counts": dict(sorted(by_reason.items())),
        "singleton_support_counts_by_arm": {
            arm: len(classes) for arm, classes in sorted(support.items())
        },
        "raw_native_symptom_singletons_licensed": 0,
        "interpretation": (
            "All raw same-visible-symptom fibres were mixed and therefore "
            "UNRESOLVED. Singleton outputs occurred only in synthetic records "
            "with one supported host-validated class certificate and matching "
            "single-class write surface; these are interface conformance, not "
            "correctness, preservation, transfer, or performance."
        ),
        "rows": rows,
        "terminal": "P5_V2_TERMINAL_PRESERVATION_SYNTHETIC_CONFORMANCE_PASS__ZERO_NATIVE_EXAMPLES__ZERO_PERFORMANCE_AUTHORITY",
    }
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

