#!/usr/bin/env python3
"""Fail-closed structural audit for the ORION Discovery V1 package."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "orion-discovery-v1"

REQUIRED_FILES = (
    "README.md",
    "EPISTEMIC_DECISION_GEOMETRY_V1.md",
    "THEOREM_IDENTIFYING_HARNESS_V1.md",
    "GENERATIVE_REACH_AND_DISCOVERY_CREDIT_V1.md",
    "HISTORICAL_COUNTERFACTUAL_PROSPECTIVE_TRIANGULATION_V1.md",
    "DISCOVERY_THEOREM_LEDGER_V1.json",
    "EXECUTION_BACKLOG_V1.json",
    "AI_EXECUTOR_PROMPT_V1.md",
    "EXPERT_REVIEW_AND_ATOMIC_GAP_MAP_V1.md",
    "run_edg_finite_census.py",
    "EDG_FINITE_CENSUS_V1.json",
    "OSTC_EXECUTION_IDENTIFIABILITY_MATRIX_V1.json",
)

FORBIDDEN_AUTHORITY_PHRASES = (
    "present_day_discovery_authority = SUPPORTED",
    "external_novelty_authority = SUPPORTED",
    "paper_authority_delta = PROMOTED",
    "historical_rediscovery_authority = SUPPORTED",
)

REQUIRED_THEOREM_PREFIX_COUNTS = {
    "EDG-T": 11,
    "HIF-T": 11,
    "GRT-T": 11,
    "HCP-T": 5,
}

REQUIRED_JOB_IDS = {
    "DISC-EDG-01",
    "DISC-HIF-01",
    "DISC-T19-01",
    "DISC-P9-SETCOVER-01",
    "DISC-ORIGIN-01",
    "DISC-HIST-01",
    "DISC-CF-01",
    "DISC-FRONTIER-MATH-01",
    "DISC-RSE-01",
    "DISC-NOV-01",
    "DISC-NATSCI-01",
}

REQUIRED_OSTC_EXECUTION_ROWS = {
    "EXEC-CM-01",
    "EXEC-PA-01",
    "EXEC-NOV-01",
    "EXEC-P1-01",
    "EXEC-P2-01",
    "EXEC-P3-01",
    "EXEC-P4-01",
    "EXEC-P5-01",
    "EXEC-P6-01",
    "EXEC-P7-01",
    "EXEC-P8-01",
    "EXEC-P9-01",
    "EXEC-P10-01",
    "EXEC-P10-02",
    "EXEC-P11-01",
    "EXEC-P12-01",
    "EXEC-P13-01",
    "EXEC-P14-01",
    "EXEC-P15-01",
    "EXEC-XP-01",
}

EXPECTED_IDENTIFIABILITY_COUNTS = {
    "IDENTIFYING_IN_REGISTERED_FINITE_CLASS": 10,
    "STRUCTURAL_IDENTIFYING_EXTERNAL_CAMPAIGN_BLOCKED": 3,
    "PARTIALLY_IDENTIFYING": 4,
    "NON_IDENTIFYING_VACUOUS": 2,
    "EXTERNAL_AUTHORITY_ONLY_CANNOT_CHECK": 1,
}

REQUIRED_CODE = (
    ROOT / "src/orion/discovery/decision_geometry.py",
    ROOT / "src/orion/discovery/harness_identifiability.py",
    ROOT / "src/orion/discovery/proposal_origin.py",
    ROOT / "src/orion/discovery/model_chronology.py",
)

REQUIRED_TESTS = (
    ROOT / "tests/unit/discovery/test_decision_geometry.py",
    ROOT / "tests/unit/discovery/test_harness_identifiability.py",
    ROOT / "tests/unit/discovery/test_proposal_origin.py",
    ROOT / "tests/unit/discovery/test_model_chronology.py",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load JSON {path.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        fail(f"top-level JSON must be an object: {path.relative_to(ROOT)}")
    return data


def main() -> int:
    missing = [name for name in REQUIRED_FILES if not (PACKAGE / name).is_file()]
    if missing:
        fail("missing discovery package files: " + ", ".join(missing))

    for path in REQUIRED_CODE + REQUIRED_TESTS:
        if not path.is_file():
            fail(f"missing required implementation/test: {path.relative_to(ROOT)}")

    combined_text = "\n".join(
        (PACKAGE / name).read_text(encoding="utf-8")
        for name in REQUIRED_FILES
        if name.endswith(".md")
    )
    for phrase in FORBIDDEN_AUTHORITY_PHRASES:
        if phrase in combined_text:
            fail(f"forbidden authority phrase present: {phrase}")

    ledger = load_json(PACKAGE / "DISCOVERY_THEOREM_LEDGER_V1.json")
    theorem_rows = ledger.get("theorems")
    if not isinstance(theorem_rows, list) or not theorem_rows:
        fail("discovery theorem ledger requires a non-empty theorem list")
    theorem_ids = [str(row.get("id", "")) for row in theorem_rows if isinstance(row, dict)]
    if len(theorem_ids) != len(theorem_rows):
        fail("every theorem row must be an object with an id")
    if len(theorem_ids) != len(set(theorem_ids)):
        fail("duplicate theorem IDs")
    declared_count = ledger.get("theorem_count")
    if declared_count != len(theorem_ids):
        fail(
            f"theorem_count mismatch: declared={declared_count}, actual={len(theorem_ids)}"
        )
    for prefix, expected in REQUIRED_THEOREM_PREFIX_COUNTS.items():
        actual = sum(theorem_id.startswith(prefix) for theorem_id in theorem_ids)
        if actual != expected:
            fail(f"{prefix} theorem count mismatch: expected={expected}, actual={actual}")

    authority = ledger.get("authority")
    if not isinstance(authority, dict):
        fail("theorem ledger authority must be an object")
    if authority.get("paper_claim_delta") != "NONE":
        fail("Discovery V1 may not promote paper claims")
    for field in ("external_proof_review", "naturalistic_transfer", "present_day_novelty"):
        if authority.get(field) != "CANNOT_CHECK":
            fail(f"authority field {field} must remain CANNOT_CHECK")

    backlog = load_json(PACKAGE / "EXECUTION_BACKLOG_V1.json")
    jobs = backlog.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        fail("execution backlog requires jobs")
    job_ids = [str(row.get("job_id", "")) for row in jobs if isinstance(row, dict)]
    if len(job_ids) != len(jobs) or len(job_ids) != len(set(job_ids)):
        fail("job rows must be objects with unique job IDs")
    if set(job_ids) != REQUIRED_JOB_IDS:
        fail(
            "execution backlog job set mismatch: "
            f"missing={sorted(REQUIRED_JOB_IDS - set(job_ids))}, "
            f"extra={sorted(set(job_ids) - REQUIRED_JOB_IDS)}"
        )
    for row in jobs:
        assert isinstance(row, dict)
        for field in (
            "job_id",
            "class",
            "title",
            "required_outputs",
            "positive_terminal",
            "negative_terminal",
            "cannot_check_terminal",
            "gate",
            "authority",
        ):
            if not row.get(field):
                fail(f"job {row.get('job_id')} missing required field {field}")

    census = load_json(PACKAGE / "EDG_FINITE_CENSUS_V1.json")
    if census.get("terminal") != "EDG_FINITE_CORRESPONDENCE_GREEN":
        fail("EDG finite census is not green")
    totals = census.get("totals")
    if not isinstance(totals, dict):
        fail("EDG finite census totals must be an object")
    expected_totals = {
        "loss_tables": 139520,
        "common_optimum_tables": 59264,
        "unique_distinct_optima_tables": 16800,
        "hedge_present_tables": 210,
        "no_hedge_tables": 16590,
        "all_correspondence_violations": 0,
    }
    for field, expected in expected_totals.items():
        if totals.get(field) != expected:
            fail(
                f"EDG finite census total mismatch for {field}: "
                f"expected={expected}, actual={totals.get(field)}"
            )
    partition = census.get("partition_refinement")
    if not isinstance(partition, dict):
        fail("EDG partition-refinement result must be an object")
    if partition.get("comparisons") != 49152 or partition.get("violations") != 0:
        fail("EDG partition-refinement correspondence mismatch")
    census_authority = census.get("authority")
    if not isinstance(census_authority, dict):
        fail("EDG census authority must be an object")
    if census_authority.get("paper_claim_delta") != "NONE":
        fail("EDG census may not promote paper claims")

    matrix = load_json(PACKAGE / "OSTC_EXECUTION_IDENTIFIABILITY_MATRIX_V1.json")
    matrix_rows = matrix.get("rows")
    if not isinstance(matrix_rows, list) or not matrix_rows:
        fail("OSTC identifiability matrix requires rows")
    matrix_ids = [str(row.get("job_id", "")) for row in matrix_rows if isinstance(row, dict)]
    if len(matrix_ids) != len(matrix_rows) or len(matrix_ids) != len(set(matrix_ids)):
        fail("OSTC identifiability rows require unique job IDs")
    if set(matrix_ids) != REQUIRED_OSTC_EXECUTION_ROWS:
        fail(
            "OSTC identifiability row set mismatch: "
            f"missing={sorted(REQUIRED_OSTC_EXECUTION_ROWS - set(matrix_ids))}, "
            f"extra={sorted(set(matrix_ids) - REQUIRED_OSTC_EXECUTION_ROWS)}"
        )
    actual_classes = Counter(
        str(row.get("classification", "")) for row in matrix_rows if isinstance(row, dict)
    )
    if dict(actual_classes) != EXPECTED_IDENTIFIABILITY_COUNTS:
        fail(
            "OSTC identifiability classification mismatch: "
            f"expected={EXPECTED_IDENTIFIABILITY_COUNTS}, actual={dict(actual_classes)}"
        )
    summary = matrix.get("summary")
    if not isinstance(summary, dict) or summary.get("rows") != len(matrix_rows):
        fail("OSTC identifiability summary row count mismatch")
    for classification, expected in EXPECTED_IDENTIFIABILITY_COUNTS.items():
        if summary.get(classification) != expected:
            fail(
                f"OSTC identifiability summary mismatch for {classification}: "
                f"expected={expected}, actual={summary.get(classification)}"
            )
    matrix_authority = matrix.get("authority")
    if not isinstance(matrix_authority, dict):
        fail("OSTC identifiability matrix authority must be an object")
    if matrix_authority.get("paper_claim_delta") != "NONE":
        fail("OSTC identifiability audit may not promote paper claims")

    print(
        "ORION_DISCOVERY_V1_STRUCTURE_GREEN "
        f"theorems={len(theorem_ids)} jobs={len(job_ids)} files={len(REQUIRED_FILES)} "
        f"edg_tables={totals['loss_tables']} ostc_rows={len(matrix_rows)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ORION_DISCOVERY_V1_STRUCTURE_RED: {exc}", file=sys.stderr)
        raise SystemExit(1)
