"""The published 62/66 is re-derivable, and the table says what the arm did.

`research/verification/records/P1.mechanical-arm-62-66.json` sits at
`CANNOT_CHECK` because the number existed only in markdown: *"cannot audit 62/66
without the case table"*. These tests re-run the arm rather than reading the
committed table, so a drift in `orion.study.p1.contradiction` fails here instead
of silently invalidating a published count.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers" / "orion-11-recursive-epistemic-reconstruction"
SCRIPT = PAPER / "scripts" / "make_mechanical_arm_case_table.py"
TABLE = PAPER / "evidence" / "MECHANICAL_ARM_CASE_TABLE_V1.json"

# Declared in the verification record as the frozen bindings for this result.
PILOT_FINGERPRINT = "7a50a2d5025beb7dea4835911fa7dbf4a191431447397c73939c276b71dc49b5"
TEST_FINGERPRINT = "21b461d89280631b93b766d6fb000c7f9f5fbeccee7cb6664f238c2c5c8e6420"


def _load_script():
    spec = importlib.util.spec_from_file_location("make_mechanical_arm_case_table", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_arm_reproduces_the_published_counts() -> None:
    summary = _load_script().build_table()["summary"]
    assert summary["total_cases"] == 66
    assert summary["correct"] == 62
    assert summary["negative_controls"] == 22
    assert summary["controls_given_a_formulation_responsibility"] == 0


def test_table_is_bound_to_the_frozen_suite_the_record_names() -> None:
    """A replay over a different suite would reproduce a number and prove nothing."""

    fingerprints = _load_script().build_table()["split_suite_fingerprints"]
    assert fingerprints["PILOT"] == PILOT_FINGERPRINT
    assert fingerprints["TEST"] == TEST_FINGERPRINT


def test_committed_table_matches_a_live_rerun() -> None:
    module = _load_script()
    committed = json.loads(TABLE.read_text(encoding="utf-8"))
    derived = module.build_table()
    assert committed["summary"] == derived["summary"]
    assert committed["cases"] == derived["cases"]
    assert committed["mismatches"] == derived["mismatches"]


def test_the_four_mismatches_are_named_not_absorbed() -> None:
    """The four failures are the point of a case table, so they are pinned.

    A table that recorded only the 62 successes would be a worse artifact than
    the prose it replaces: the published claim is explicitly bounded as
    descriptive, and the shape of what it gets wrong is what makes that bound
    checkable. Three of the four are one confusion (DECOMPOSITION read as
    INTERFACE) and the fourth is an abstention, not a wrong answer.
    """

    mismatches = _load_script().build_table()["mismatches"]
    assert len(mismatches) == 4
    by_case = {row["case_id"]: row for row in mismatches}
    assert set(by_case) == {"p1-c016", "p1-c018", "p1-c103", "p1-c147"}
    assert by_case["p1-c016"]["responsibility_predicted"] is None
    for case_id in ("p1-c018", "p1-c103", "p1-c147"):
        assert by_case[case_id]["responsibility_gold"] == "DECOMPOSITION"
        assert by_case[case_id]["responsibility_predicted"] == "INTERFACE"


def test_table_grants_no_authority_and_stays_descriptive() -> None:
    committed = json.loads(TABLE.read_text(encoding="utf-8"))
    assert committed["grants_authority"] == "NONE"
    assert committed["closes_gate"] is None
    assert "Not H1 support" in committed["claim_scope"]
