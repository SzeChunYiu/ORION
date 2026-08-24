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
    "PAPER_THEOREM_PACKAGES_V1.md",
    "P1_P15_THEORY_UPGRADES_V1.md",
    "P1_THEORY_SUPERSESSION_V1.md",
    "THEOREM_LEDGER_V1.json",
    "ASSUMPTION_LEDGER_V1.json",
    "EXECUTION_ONLY_BACKLOG_V1.json",
    "AI_EXECUTION_PROMPT_V1.md",
    "ISSUE_COMPLETION_MATRIX_V1.md",
}
REQUIRED_PATHS = {
    "formal/lean/lean-toolchain",
    "formal/lean/lakefile.toml",
    "formal/lean/OrionFoundations.lean",
    "formal/lean/OrionFoundations/Core.lean",
}


def load_json(name: str) -> dict[str, object]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    present = {p.name for p in ROOT.iterdir() if p.is_file()}
    missing = sorted(REQUIRED_FILES - present)
    if missing:
        errors.append(f"missing required files: {missing}")
    missing_paths = sorted(path for path in REQUIRED_PATHS if not (ROOT / path).is_file())
    if missing_paths:
        errors.append(f"missing required paths: {missing_paths}")

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

    paper_packages = (ROOT / "PAPER_THEOREM_PACKAGES_V1.md").read_text(encoding="utf-8")
    paper_headings = re.findall(r"^# P(\d+) —", paper_packages, flags=re.MULTILINE)
    if paper_headings != [str(i) for i in range(1, 16)]:
        errors.append(f"paper theorem package headings mismatch: {paper_headings}")
    for paper_id in range(1, 16):
        if not re.search(rf"^## P{paper_id}-T1\b", paper_packages, flags=re.MULTILINE):
            errors.append(f"P{paper_id} has no first theorem in paper package")

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

    lean_core = (ROOT / "formal/lean/OrionFoundations/Core.lean").read_text(encoding="utf-8")
    required_lean_theorems = {
        "ostc_t1_donor_conservativity",
        "ostc_t2_exact_target_sufficiency",
        "ostc_t3_fiberwise_optimality",
        "ostc_t4_no_silent_amplification",
        "ostc_t5_bridge_necessity",
        "ostc_t6_normal_form_soundness",
        "ostc_t7_normal_form_completeness",
        "ostc_t8_factor_independence",
        "ostc_t9_full_abstraction",
        "ostc_t10_composition_attenuates",
        "ostc_t11_exact_revocation",
        "ostc_t12_open_world_impossibility",
        "ostc_t13_transport_associativity",
        "ostc_t14_collision_defeats_diagnosis",
        "ostc_t15_old_closure_obstruction",
        "ostc_t16_break_even",
        "ostc_t17_coarsened_signal_regret",
        "ostc_t18_joint_responsibility_sufficiency",
        "ostc_t19_reflexive_custody_impossibility",
        "ostc_t20_execution_noninterference_validity",
        "ostc_t21_no_infinite_nat_descent",
        "ostc_t22_supplied_witness_checks",
        "ostc_t23_coupled_advance",
    }
    for theorem_name in sorted(required_lean_theorems):
        if not re.search(rf"\btheorem\s+{re.escape(theorem_name)}\b", lean_core):
            errors.append(f"Lean core missing theorem {theorem_name}")
    if re.search(r"(^|[^A-Za-z0-9_])(sorry|admit|axiom)([^A-Za-z0-9_]|$)", lean_core):
        errors.append("Lean core contains incomplete proof marker")

    digest_rows = {}
    for name in sorted(REQUIRED_FILES):
        path = ROOT / name
        if path.is_file():
            data = path.read_bytes()
            digest_rows[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    for name in sorted(REQUIRED_PATHS):
        path = ROOT / name
        if path.is_file():
            data = path.read_bytes()
            digest_rows[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    result = {
        "schema_version": "orion.foundations.v3-audit.v2",
        "status": "PASS" if not errors else "FAIL",
        "theorem_count": len(ids),
        "assumption_count": len(assumption_ids),
        "paper_theory_count": len(paper_headings),
        "lean_theorem_count": len(required_lean_theorems),
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
