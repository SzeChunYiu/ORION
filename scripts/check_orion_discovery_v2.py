#!/usr/bin/env python3
"""Fail-closed structural audit for ORION Discovery V2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "orion-discovery-v2"

REQUIRED_FILES = (
    "README.md",
    "KNOWLEDGE_WEB_NAVIGATION_PROOF_ECONOMY_AND_SELF_APPLICATION_V1.md",
    "THEOREM_LEDGER_V1.json",
    "EXECUTION_BACKLOG_V1.json",
)

REQUIRED_JOB_IDS = {
    "DISC-WEB-01",
    "DISC-PROOF-ECONOMY-01",
    "DISC-IMPACT-01",
    "DISC-Q-TRANSFER-01",
    "DISC-SELF-01",
    "DISC-HUMAN-DECOMP-01",
    "DISC-OOD-MORPH-01",
    "DISC-WEB-FRONTIER-MATH-01",
    "DISC-NOV-02",
}

REQUIRED_PREFIX_COUNTS = {
    "KW-T": 6,
    "NAV-T": 5,
    "PE-T": 6,
    "QX-T": 3,
    "SELF-T": 4,
    "SYNC-T": 4,
}

FORBIDDEN_AUTHORITY_PHRASES = (
    "paper_authority_delta = SUPPORTED",
    "present_day_discovery_authority = SUPPORTED",
    "quantum_scientific_authority_transfer = ALLOWED",
    "external_novelty_authority = SUPPORTED",
    "external_adoption_authority = SUPPORTED",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_object(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        fail(f"top-level JSON must be an object: {path.relative_to(ROOT)}")
    return data


def main() -> int:
    missing = [name for name in REQUIRED_FILES if not (PACKAGE / name).is_file()]
    if missing:
        fail("missing Discovery V2 files: " + ", ".join(missing))

    code = ROOT / "src/orion/discovery/knowledge_web.py"
    tests = ROOT / "tests/unit/discovery/test_knowledge_web.py"
    for path in (code, tests):
        if not path.is_file():
            fail(f"missing required executable artifact: {path.relative_to(ROOT)}")

    combined = "\n".join(
        (PACKAGE / name).read_text(encoding="utf-8")
        for name in REQUIRED_FILES
        if name.endswith(".md")
    )
    for phrase in FORBIDDEN_AUTHORITY_PHRASES:
        if phrase in combined:
            fail(f"forbidden authority phrase present: {phrase}")

    ledger = load_object(PACKAGE / "THEOREM_LEDGER_V1.json")
    rows = ledger.get("theorems")
    if not isinstance(rows, list) or not rows:
        fail("theorem ledger requires a non-empty theorem list")
    ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            fail("every theorem row must be an object")
        theorem_id = row.get("id")
        if not isinstance(theorem_id, str) or not theorem_id:
            fail("every theorem requires an id")
        if row.get("paper_authority_delta") != "NONE":
            fail(f"theorem {theorem_id} attempts a paper authority delta")
        ids.append(theorem_id)
    if len(ids) != len(set(ids)):
        fail("duplicate theorem IDs")
    if ledger.get("theorem_count") != len(ids):
        fail("theorem_count does not match theorem rows")
    for prefix, expected in REQUIRED_PREFIX_COUNTS.items():
        actual = sum(theorem_id.startswith(prefix) for theorem_id in ids)
        if actual != expected:
            fail(f"{prefix} theorem count mismatch: expected={expected}, actual={actual}")
    authority = ledger.get("authority")
    if not isinstance(authority, dict):
        fail("theorem ledger authority must be an object")
    expected_authority = {
        "paper_claim_delta": "NONE",
        "present_day_discovery": "CANNOT_CHECK",
        "quantum_scientific_authority_transfer": "FORBIDDEN",
        "external_novelty": "CANNOT_CHECK",
        "external_adoption": "CANNOT_CHECK",
    }
    for field, expected in expected_authority.items():
        if authority.get(field) != expected:
            fail(f"authority field {field} must equal {expected}")

    backlog = load_object(PACKAGE / "EXECUTION_BACKLOG_V1.json")
    jobs = backlog.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        fail("execution backlog requires jobs")
    job_ids: list[str] = []
    for row in jobs:
        if not isinstance(row, dict):
            fail("every job row must be an object")
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
                fail(f"job {row.get('job_id')} missing field {field}")
        job_ids.append(str(row["job_id"]))
    if len(job_ids) != len(set(job_ids)):
        fail("duplicate job IDs")
    if set(job_ids) != REQUIRED_JOB_IDS:
        fail(
            "execution job set mismatch: "
            f"missing={sorted(REQUIRED_JOB_IDS - set(job_ids))}, "
            f"extra={sorted(set(job_ids) - REQUIRED_JOB_IDS)}"
        )

    print(
        "ORION_DISCOVERY_V2_STRUCTURE_GREEN "
        f"theorems={len(ids)} jobs={len(job_ids)} files={len(REQUIRED_FILES)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ORION_DISCOVERY_V2_STRUCTURE_RED: {exc}", file=sys.stderr)
        raise SystemExit(1)
