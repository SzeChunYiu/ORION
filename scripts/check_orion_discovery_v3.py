#!/usr/bin/env python3
"""Structural checker for the additive ORION Discovery V3 package."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "orion-discovery-v3"
REQUIRED = (
    RESEARCH / "SCIENTIFIC_FRONTIER_DOMINANCE_V1.md",
    RESEARCH / "RESIDUAL_NOVELTY_CALCULUS_V1.md",
    RESEARCH / "NEAREST_WORK_ABSORPTION_AND_RESIDUAL_V1.md",
    RESEARCH / "HUMAN_DISCOVERY_PARENT_SOURCE_MAP_V1.json",
    RESEARCH / "ATOMIC_NOVELTY_AND_SUPERIORITY_MAP_V1.json",
    RESEARCH / "THEOREM_LEDGER_V1.json",
    RESEARCH / "EXECUTION_BACKLOG_V1.json",
    RESEARCH / "AI_EXECUTOR_PROMPT_V1.md",
    ROOT / "src" / "orion" / "discovery" / "frontier_dominance.py",
    ROOT / "tests" / "unit" / "discovery" / "test_frontier_dominance.py",
    ROOT / "scripts" / "run_frontier_dominance_census_v1.py",
    RESEARCH / "FINITE_REFERENCE_RECEIPT_V1.json",
)


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.is_file()]
    if missing:
        print("ORION_DISCOVERY_V3_MISSING", *missing, sep="\n")
        return 2

    theorem_rows = json.loads((RESEARCH / "THEOREM_LEDGER_V1.json").read_text())
    jobs = json.loads((RESEARCH / "EXECUTION_BACKLOG_V1.json").read_text())
    atoms = json.loads((RESEARCH / "ATOMIC_NOVELTY_AND_SUPERIORITY_MAP_V1.json").read_text())
    parents = json.loads((RESEARCH / "HUMAN_DISCOVERY_PARENT_SOURCE_MAP_V1.json").read_text())

    ids = [row["theorem_id"] for row in theorem_rows["theorems"]]
    if len(ids) != len(set(ids)) or not ids:
        print("ORION_DISCOVERY_V3_THEOREM_ID_ERROR")
        return 1
    if any(row["authority_delta"] != "NONE" for row in theorem_rows["theorems"]):
        print("ORION_DISCOVERY_V3_AUTHORITY_LAUNDERING")
        return 1
    if any(row["paper_authority_delta"] != "NONE" for row in jobs["jobs"]):
        print("ORION_DISCOVERY_V3_JOB_AUTHORITY_LAUNDERING")
        return 1
    if not any(row["atom_id"] == "OPEN_MORPHOLOGY" for row in atoms["atoms"]):
        print("ORION_DISCOVERY_V3_OPEN_MORPHOLOGY_MISSING")
        return 1
    if len(parents["parents"]) < 6:
        print("ORION_DISCOVERY_V3_PARENT_COVERAGE_TOO_SMALL")
        return 1

    print(
        "ORION_DISCOVERY_V3_STRUCTURE_GREEN",
        f"theorems={len(ids)}",
        f"jobs={len(jobs['jobs'])}",
        f"atoms={len(atoms['atoms'])}",
        f"parents={len(parents['parents'])}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
