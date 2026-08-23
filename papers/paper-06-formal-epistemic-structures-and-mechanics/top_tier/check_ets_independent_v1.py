#!/usr/bin/env python3
"""Second independent checker for the frozen P6 ETS V1 evidence.

This implementation deliberately does not import, execute, or mirror the control
flow of ``check_ets_top_tier_v1.py``.  It reads only the prospectively frozen
case facts and gold dispositions, evaluates the ETS contract through a
set-of-defects formulation, and independently reconstructs the bounded T6.1--T6.3
witness summaries.

The checker grants verification authority only for the frozen finite study.  It
does not grant broad P6 scientific or submission authority.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "ets_cases_v1.jsonl"
GOLD_PATH = HERE / "ets_gold_v1.json"

TERMINALS = {"ADMISSIBLE", "REOPEN", "DENIED", "CANNOT_CHECK"}
DONOR_OBSERVABLE_FIELDS = (
    "computational_support",
    "provenance_bound",
    "generic_permission",
    "generic_obligations_clear",
    "footprint_audit_pass",
    "independent_support",
    "preservation_certificate",
)


def load_cases() -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in CASES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 18:
        raise SystemExit(f"expected 18 frozen ETS cases, found {len(rows)}")
    ids = [row.get("id") for row in rows]
    if len(set(ids)) != len(rows):
        raise SystemExit("duplicate frozen ETS case identity")
    return rows


def load_gold() -> dict[str, str]:
    value = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value.values()) - TERMINALS:
        raise SystemExit("malformed frozen ETS gold")
    return {str(key): str(item) for key, item in value.items()}


def classify(case: dict[str, Any]) -> str:
    """Evaluate the scientific-admission contract as prioritized defect sets.

    This is intentionally a different formulation from the original checker:
    facts first populate epistemic defect classes, then the terminal is selected
    by the contract's precedence relation.  Case IDs, families, and fixture types
    are never consulted.
    """

    unresolved: set[str] = set()
    denied: set[str] = set()
    reopen: set[str] = set()

    if not case["footprint_audit_pass"]:
        unresolved.add("execution_footprint_unknown")
    if not case["provenance_bound"]:
        unresolved.add("provenance_unbound")
    if not case["evidence_transport_known"]:
        unresolved.add("evidence_transport_unknown")

    if not case["generic_permission"]:
        denied.add("generic_permission_missing")
    if not case["scientific_commit_authority"]:
        denied.add("scientific_commit_authority_missing")

    if not case["computational_support"]:
        reopen.add("computational_support_invalidated")
    if case["evidence_transport_known"] and not case["evidence_transport_valid"]:
        reopen.add("evidence_transport_invalid")
    if not case["scientific_obligations_clear"]:
        reopen.add("scientific_obligation_open")

    if unresolved:
        return "CANNOT_CHECK"
    if denied:
        return "DENIED"
    if reopen:
        return "REOPEN"
    return "ADMISSIBLE"


def audit_label_independence(cases: list[dict[str, Any]]) -> None:
    for original in cases:
        reminted = dict(original)
        reminted["id"] = "opaque-remint"
        reminted["family"] = "opaque-family"
        reminted["case_type"] = "opaque-type"
        if classify(reminted) != classify(original):
            raise SystemExit(f"label leakage detected for {original['id']}")


def t61_factorization() -> dict[str, Any]:
    required = (
        "computational_support",
        "evidence_transport_valid",
        "scientific_obligations_clear",
        "scientific_commit_authority",
    )
    base: dict[str, Any] = {
        "footprint_audit_pass": True,
        "provenance_bound": True,
        "evidence_transport_known": True,
        "generic_permission": True,
    }

    admissible_patterns: list[str] = []
    single_factor_terminals: dict[str, str] = {}
    for mask in range(16):
        row = dict(base)
        bits = f"{mask:04b}"
        for key, bit in zip(required, bits):
            row[key] = bit == "1"
        terminal = classify(row)
        if terminal == "ADMISSIBLE":
            admissible_patterns.append(bits)

    for index, key in enumerate(required):
        row = dict(base)
        for required_key in required:
            row[required_key] = True
        row[key] = False
        single_factor_terminals[key] = classify(row)

    if admissible_patterns != ["1111"]:
        raise SystemExit(f"T6.1 factorization violated: {admissible_patterns!r}")
    if any(value == "ADMISSIBLE" for value in single_factor_terminals.values()):
        raise SystemExit("T6.1 single-factor non-implication missing")

    return {
        "admissible_assignment_count": 1,
        "admissible_pattern": "1111",
        "single_factor_terminals": single_factor_terminals,
    }


def _local_certificate(
    *, source_epoch: int, target_epoch: int, source_scope: str, target_scope: str,
    computational_support: bool = True, evidence_transport_valid: bool = True,
    obligations_clear: bool = True, authority: bool = True,
) -> dict[str, Any]:
    return {
        "source_epoch": source_epoch,
        "target_epoch": target_epoch,
        "source_scope": source_scope,
        "target_scope": target_scope,
        "computational_support": computational_support,
        "evidence_transport_valid": evidence_transport_valid,
        "obligations_clear": obligations_clear,
        "authority": authority,
    }


def _local_ok(cert: dict[str, Any]) -> bool:
    return all(
        (
            cert["computational_support"],
            cert["evidence_transport_valid"],
            cert["obligations_clear"],
            cert["authority"],
        )
    )


def _composes(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        _local_ok(left)
        and _local_ok(right)
        and left["target_epoch"] == right["source_epoch"]
        and left["target_scope"] == right["source_scope"]
    )


def t62_composition() -> dict[str, Any]:
    first = _local_certificate(source_epoch=10, target_epoch=11, source_scope="claim", target_scope="claim")
    good = _local_certificate(source_epoch=11, target_epoch=12, source_scope="claim", target_scope="claim")
    epoch_mismatch = _local_certificate(source_epoch=13, target_epoch=14, source_scope="claim", target_scope="claim")
    scope_mismatch = _local_certificate(source_epoch=11, target_epoch=12, source_scope="expanded", target_scope="expanded")
    obligation_open = _local_certificate(
        source_epoch=11,
        target_epoch=12,
        source_scope="claim",
        target_scope="claim",
        obligations_clear=False,
    )

    checks = {
        "positive": _composes(first, good),
        "epoch_mismatch_blocked": not _composes(first, epoch_mismatch),
        "scope_mismatch_blocked": not _composes(first, scope_mismatch),
        "open_obligation_blocked": not _composes(first, obligation_open),
    }
    if not all(checks.values()):
        raise SystemExit(f"T6.2 composition invariant failed: {checks!r}")
    return checks


def t63_erasure(cases: list[dict[str, Any]], gold: dict[str, str]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in cases:
        projection = {key: row[key] for key in DONOR_OBSERVABLE_FIELDS}
        signature = json.dumps(projection, sort_keys=True, separators=(",", ":"))
        buckets[signature].append(row)

    witnesses: list[tuple[str, str]] = []
    for bucket in buckets.values():
        ordered = sorted(bucket, key=lambda row: row["id"])
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                if gold[left["id"]] != gold[right["id"]]:
                    witnesses.append((left["id"], right["id"]))

    if not witnesses:
        raise SystemExit("T6.3 donor-observable erasure witness missing")
    return {
        "witness_count": len(witnesses),
        "first_witness": list(witnesses[0]),
    }


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    cases = load_cases()
    gold = load_gold()
    if set(gold) != {row["id"] for row in cases}:
        raise SystemExit("frozen case/gold identity mismatch")

    audit_label_independence(cases)
    classifications = {row["id"]: classify(row) for row in cases}
    mismatches = {
        case_id: {"expected": gold[case_id], "actual": classifications[case_id]}
        for case_id in sorted(gold)
        if gold[case_id] != classifications[case_id]
    }
    if mismatches:
        raise SystemExit(json.dumps({"classification_mismatches": mismatches}, sort_keys=True))

    theorem_summary = {
        "T6.1": t61_factorization(),
        "T6.2": t62_composition(),
        "T6.3": t63_erasure(cases, gold),
    }
    receipt: dict[str, Any] = {
        "schema": "P6.ETSIndependentVerification.v1",
        "case_count": len(cases),
        "case_sha256": hashlib.sha256(CASES_PATH.read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256(GOLD_PATH.read_bytes()).hexdigest(),
        "classification_accuracy": 1.0,
        "classifications": {key: classifications[key] for key in sorted(classifications)},
        "theorems": theorem_summary,
        "implementation_independence": (
            "NO_IMPORT_OR_EXECUTION_OF_PRIMARY_CHECKER__DEFECT_SET_FORMULATION"
        ),
        "claim_authority": "FROZEN_P6_ETS_V1_VERIFICATION_ONLY",
        "terminal": "P6_ETS_SECOND_INDEPENDENT_CHECKER_GREEN",
    }
    receipt["receipt_sha256"] = canonical_digest(receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
