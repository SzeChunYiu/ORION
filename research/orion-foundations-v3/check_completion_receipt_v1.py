#!/usr/bin/env python3
"""Verify the final foundations receipt and formalization-coverage ledger."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    errors: list[str] = []
    receipt = json.loads((ROOT / "AUDIT_RECEIPT_V1.json").read_text(encoding="utf-8"))
    coverage = json.loads((ROOT / "FORMALIZATION_COVERAGE_V1.json").read_text(encoding="utf-8"))
    theorem_ledger = json.loads((ROOT / "THEOREM_LEDGER_V1.json").read_text(encoding="utf-8"))
    paper_ledger = json.loads((ROOT / "PAPER_THEOREM_LEDGER_V1.json").read_text(encoding="utf-8"))
    backlog = json.loads((ROOT / "EXECUTION_ONLY_BACKLOG_V1.json").read_text(encoding="utf-8"))

    expected_counts = {
        "theorem_count": len(theorem_ledger.get("theorems", [])),
        "paper_theorem_count": sum(
            len(row.get("theorems", []))
            for row in paper_ledger.get("papers", [])
            if isinstance(row, dict)
        ),
        "paper_count": len(paper_ledger.get("papers", [])),
        "execution_job_count": len(backlog.get("jobs", [])),
    }
    for key, value in expected_counts.items():
        if receipt.get(key) != value:
            errors.append(f"receipt {key}={receipt.get(key)!r}, expected {value}")
    if receipt.get("breakthrough_theorem_count") != 8:
        errors.append("receipt must bind eight programme breakthrough theorems")
    if receipt.get("assumption_count") != 10:
        errors.append("receipt must bind ten W-dagger assumptions")
    if receipt.get("paper_authority_delta") != "NONE":
        errors.append("receipt paper authority delta must be NONE")
    if receipt.get("workflow_run_conclusion") != "success":
        errors.append("receipt must bind a successful workflow run")
    if receipt.get("structural_audit", {}).get("job_conclusion") != "success":
        errors.append("structural audit is not bound green")
    if receipt.get("lean", {}).get("job_conclusion") != "success":
        errors.append("Lean kernel is not bound green")

    rows = coverage.get("theorems")
    if not isinstance(rows, list):
        errors.append("formalization coverage must contain theorem rows")
        rows = []
    ids = [row.get("theorem_id") for row in rows if isinstance(row, dict)]
    expected_ids = [f"OSTC-T{i}" for i in range(24)]
    if ids != expected_ids:
        errors.append(f"formalization coverage IDs mismatch: {ids}")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("non-object formalization coverage row")
            continue
        for field in ("lean_status", "machine_checked", "not_machine_checked"):
            if not str(row.get(field, "")).strip():
                errors.append(f"coverage row {row.get('theorem_id')} missing {field}")
    if coverage.get("paper_authority_delta") != "NONE":
        errors.append("formalization coverage paper authority delta must be NONE")

    result = {
        "schema_version": "orion.foundations.completion-receipt-audit.v1",
        "status": "PASS" if not errors else "FAIL",
        "receipt_verified_source_head": receipt.get("verified_source_head"),
        "formalization_row_count": len(rows),
        "expected_counts": expected_counts,
        "errors": errors,
        "paper_authority_delta": "NONE",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
