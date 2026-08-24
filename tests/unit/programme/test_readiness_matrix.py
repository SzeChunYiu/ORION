"""The P1-P15 readiness matrix must be derived, complete in shape, and honest about gaps."""

from __future__ import annotations

import json
from pathlib import Path

from orion.programme.specialist_readiness_matrix import (
    CANONICAL,
    EXIT_CANNOT_CHECK,
    FIELDS,
    build,
    main,
)

ARTIFACT = (
    Path(__file__).resolve().parents[3]
    / "papers/paper-15-orion-research-harness/matrix/P1_P15_SPECIALIST_READINESS_MATRIX_V1.json"
)

REQUIRED = {
    "SCIENTIFIC_RESULT", "CURRENT_MANUSCRIPT", "CURRENT_PDF", "RIGHTS",
    "REVIEWER_ACCESS", "TARGET_FIT", "INDEPENDENT_AUDIT", "SUBMISSION_BYTES",
    "TOP_TIER_GATE",
}


def test_artifact_carries_every_required_field_for_every_paper() -> None:
    m = json.loads(ARTIFACT.read_text())
    assert set(m["fields"]) == REQUIRED
    assert len(m["papers"]) == 15
    for pid, rec in m["papers"].items():
        assert set(rec["fields"]) == REQUIRED, pid


def test_every_present_cell_names_its_source() -> None:
    """A value without a source is an assertion."""
    m = json.loads(ARTIFACT.read_text())
    for pid, rec in m["papers"].items():
        for field, cell in rec["fields"].items():
            if cell["status"] == "PRESENT":
                assert cell.get("source"), f"{pid}.{field} has no source"
                assert cell.get("value"), f"{pid}.{field} has no value"


def test_every_absent_cell_names_what_was_looked_for() -> None:
    m = json.loads(ARTIFACT.read_text())
    for pid, rec in m["papers"].items():
        for field, cell in rec["fields"].items():
            if cell["status"] != "PRESENT":
                assert cell.get("reason"), f"{pid}.{field} is absent with no reason"


def test_paper_numbers_map_to_the_intended_directories() -> None:
    """Two directories start paper-02 and two start paper-04.

    Taking the first alphabetically silently reports a different paper.
    """
    slugs = dict(CANONICAL)
    assert slugs["P2"] == "paper-02-open-world-scientific-discovery"
    assert slugs["P4"] == "paper-04-verified-scientific-discovery"
    live = build()
    assert live["papers"]["P2"]["directory"] == slugs["P2"]
    assert live["papers"]["P4"]["directory"] == slugs["P4"]


def test_the_matrix_records_the_reviewer_access_gap() -> None:
    """Absent for all fifteen. A uniform gap is a finding, not a formatting issue."""
    m = json.loads(ARTIFACT.read_text())
    absent = [p for p, r in m["papers"].items() if r["fields"]["REVIEWER_ACCESS"]["status"] != "PRESENT"]
    assert len(absent) == 15


def test_missing_tree_is_not_an_empty_matrix() -> None:
    assert main(["--root", str(Path("/nonexistent"))]) == EXIT_CANNOT_CHECK
