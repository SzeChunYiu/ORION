#!/usr/bin/env python3
"""Fail-closed structural audit for the ORION Foundations V3 theory package."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED_FILES = {
    "README.md",
    "ORION_SCIENTIFIC_TRANSITION_CALCULUS_V1.md",
    "THEOREM_DERIVATIONS_T0_T23_V1.md",
    "P1_P15_THEORY_UPGRADES_V1.md",
    "P1_THEORY_SUPERSESSION_V1.md",
    "THEOREM_LEDGER_V1.json",
    "ASSUMPTION_LEDGER_V1.json",
    "EXECUTION_ONLY_BACKLOG_V1.json",
    "AI_EXECUTION_PROMPT_V1.md",
    "ISSUE_COMPLETION_MATRIX_V1.md",
}


def load_json(name: str) -> dict[str, object]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    present = {p.name for p in ROOT.iterdir() if p.is_file()}
    missing = sorted(REQUIRED_FILES - present)
    if missing:
        errors.append(f"missing required files: {missing}")

    theorem_ledger = load_json("THEOREM_LEDGER_V1.json")
    assumptions = load_json("ASSUMPTION_LEDGER_V1.json")
    backlog = load_json("EXECUTION_ONLY_BACKLOG_V1.json")

    rows = theorem_ledger.get("theorems")
    if not isinstance(rows, list):
        errors.append("theorems must be a list")
        rows = []
    ids = [str(row.get("theorem_id")) for row in rows if isinstance(row, dict)]
    expected = [f"OSTC-T{i}" for i in range(24)]
    if ids != expected:
        errors.append(f"theorem IDs/order mismatch: {ids}")
    if len(set(ids)) != len(ids):
        errors.append("duplicate theorem IDs")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("non-object theorem row")
            continue
        if row.get("status") != "PROVED_SCHEMA":
            errors.append(f"unexpected theorem status: {row}")
        if row.get("paper_authority_delta") != "NONE":
            errors.append(f"paper authority delta must be NONE: {row}")

    derivations = (ROOT / "THEOREM_DERIVATIONS_T0_T23_V1.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## T(\d+) —", derivations, flags=re.MULTILINE)
    if headings != [str(i) for i in range(24)]:
        errors.append(f"derivation headings mismatch: {headings}")

    assumption_rows = assumptions.get("assumptions")
    if not isinstance(assumption_rows, list):
        errors.append("assumptions must be a list")
        assumption_rows = []
    assumption_ids = [str(row.get("id")) for row in assumption_rows if isinstance(row, dict)]
    if assumption_ids != [f"A{i}" for i in range(1, 11)]:
        errors.append(f"assumption IDs mismatch: {assumption_ids}")

    if backlog.get("theory_frozen") is not True:
        errors.append("execution backlog must freeze the theory")
    jobs = backlog.get("jobs")
    if not isinstance(jobs, list):
        errors.append("jobs must be a list")
        jobs = []
    job_ids = [str(job.get("job_id")) for job in jobs if isinstance(job, dict)]
    if len(job_ids) != len(set(job_ids)):
        errors.append("duplicate execution job IDs")
    theorem_set = set(expected)
    papers_seen: set[str] = set()
    for job in jobs:
        if not isinstance(job, dict):
            errors.append("non-object execution job")
            continue
        for key in ("job_id", "task", "positive", "negative", "cannot_check", "type"):
            if not str(job.get(key, "")).strip():
                errors.append(f"job missing {key}: {job}")
        for theorem_id in job.get("theorems", []):
            if theorem_id not in theorem_set:
                errors.append(f"job references unknown theorem {theorem_id}")
        paper = job.get("paper")
        if isinstance(paper, str) and re.fullmatch(r"P(?:[1-9]|1[0-5])", paper):
            papers_seen.add(paper)
    expected_papers = {f"P{i}" for i in range(1, 16)}
    if papers_seen != expected_papers:
        errors.append(f"paper execution coverage mismatch: {sorted(papers_seen)}")

    p1 = (ROOT / "P1_THEORY_SUPERSESSION_V1.md").read_text(encoding="utf-8")
    for phrase in (
        "minimal responsibility-conditioned epistemic mutation",
        "RR1 is an empirical/protocol instantiation",
        "Infrastructure failure yields a typed execution terminal",
    ):
        if phrase not in p1:
            errors.append(f"P1 supersession missing phrase: {phrase}")

    digest_rows = {}
    for name in sorted(REQUIRED_FILES):
        path = ROOT / name
        if path.is_file():
            data = path.read_bytes()
            digest_rows[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    result = {
        "schema_version": "orion.foundations.v3-audit.v1",
        "status": "PASS" if not errors else "FAIL",
        "theorem_count": len(ids),
        "assumption_count": len(assumption_ids),
        "execution_job_count": len(job_ids),
        "paper_execution_coverage": sorted(papers_seen),
        "errors": errors,
        "files": digest_rows,
        "paper_authority_delta": "NONE",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
