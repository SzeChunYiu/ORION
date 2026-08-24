#!/usr/bin/env python3
"""Fail-closed audit of the P1–P15 theorem ledger, packages, and proofs."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    errors: list[str] = []
    ledger = json.loads((ROOT / "PAPER_THEOREM_LEDGER_V1.json").read_text(encoding="utf-8"))
    programme = json.loads((ROOT / "THEOREM_LEDGER_V1.json").read_text(encoding="utf-8"))
    backlog = json.loads((ROOT / "EXECUTION_ONLY_BACKLOG_V1.json").read_text(encoding="utf-8"))
    package = (ROOT / "PAPER_THEOREM_PACKAGES_V1.md").read_text(encoding="utf-8")
    proofs = (ROOT / "PAPER_THEOREM_PROOFS_V1.md").read_text(encoding="utf-8")

    rows = ledger.get("papers")
    if not isinstance(rows, list):
        errors.append("papers must be a list")
        rows = []
    expected = [f"P{i}" for i in range(1, 16)]
    actual = [str(row.get("paper")) for row in rows if isinstance(row, dict)]
    if actual != expected:
        errors.append(f"paper order mismatch: {actual}")

    ostc = {
        str(row.get("theorem_id"))
        for row in programme.get("theorems", [])
        if isinstance(row, dict)
    }
    jobs = {
        str(row.get("job_id"))
        for row in backlog.get("jobs", [])
        if isinstance(row, dict)
    }
    seen_execution_jobs: set[str] = set()
    seen_paper_theorems: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            errors.append("non-object paper row")
            continue
        paper = str(row.get("paper"))
        if row.get("status") != "THEORY_COMPLETE_EXECUTION_PENDING":
            errors.append(f"unexpected status for {paper}: {row.get('status')}")
        if not str(row.get("object", "")).strip():
            errors.append(f"missing object for {paper}")
        theorem_names = row.get("theorems")
        if not isinstance(theorem_names, list) or not theorem_names:
            errors.append(f"missing theorem family for {paper}")
            theorem_names = []
        else:
            for theorem_name in theorem_names:
                if not str(theorem_name).startswith(f"{paper}-T"):
                    errors.append(f"bad theorem name for {paper}: {theorem_name}")
        for theorem_id in row.get("ostc_dependencies", []):
            if theorem_id not in ostc:
                errors.append(f"{paper} references unknown {theorem_id}")
        job_id = str(row.get("execution_job", ""))
        if job_id not in jobs:
            errors.append(f"{paper} references unknown execution job {job_id}")
        if job_id in seen_execution_jobs:
            errors.append(f"duplicate paper execution job {job_id}")
        seen_execution_jobs.add(job_id)
        if not re.search(rf"^# {re.escape(paper)} —", package, flags=re.MULTILINE):
            errors.append(f"paper package missing heading for {paper}")
        if not re.search(rf"^# {re.escape(paper)} proofs\b", proofs, flags=re.MULTILINE):
            errors.append(f"paper proof appendix missing heading for {paper}")
        for theorem_name in theorem_names:
            theorem_id = str(theorem_name).split(" ", 1)[0]
            seen_paper_theorems.append(theorem_id)
            if not re.search(rf"^## {re.escape(theorem_id)}\b", package, flags=re.MULTILINE):
                errors.append(f"paper package missing theorem {theorem_id}")
            if not re.search(rf"^## {re.escape(theorem_id)}\b", proofs, flags=re.MULTILINE):
                errors.append(f"paper proof appendix missing theorem {theorem_id}")

    if len(seen_paper_theorems) != 77:
        errors.append(f"expected 77 paper theorems, found {len(seen_paper_theorems)}")
    if len(set(seen_paper_theorems)) != len(seen_paper_theorems):
        errors.append("duplicate paper theorem IDs")

    result = {
        "schema_version": "orion.foundations.paper-theorem-audit.v2",
        "status": "PASS" if not errors else "FAIL",
        "paper_count": len(actual),
        "paper_theorem_count": len(seen_paper_theorems),
        "execution_job_count": len(seen_execution_jobs),
        "errors": errors,
        "paper_authority_delta": "NONE",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
