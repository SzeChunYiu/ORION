"""What the candidate may not see, and what the host must record.

The forbidden list is read from the committed freeze, so these tests fail if the
enforcement and the freeze ever drift apart -- which is the only way this kind
of rule usually breaks.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from orion.study.p5.candidate_custody import (
    EDIT_DISPOSITIONS,
    EXIT_CANNOT_CHECK,
    EXIT_FORBIDDEN_FIELD,
    EXIT_INCOMPLETE_RECORD,
    EXIT_PASS,
    EXIT_UNRECONCILED,
    REQUIRED_OUTCOME_FIELDS,
    check_candidate_packet,
    check_outcome_record,
    load_forbidden_fields,
)


def _root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "development").is_dir() and (parent / "src").is_dir():
            return parent
    pytest.skip("repository root not found")


@pytest.fixture(scope="module")
def forbidden() -> tuple[str, ...]:
    fields = load_forbidden_fields(_root())
    if fields is None:
        pytest.skip("frozen requirements not present")
    return fields


def _clean_packet() -> dict:
    return {
        "instance_id": "astropy__astropy-12345",
        "problem_statement": "Something is wrong when the unit is dimensionless.",
        "repo": "astropy/astropy",
        "base_commit": "a" * 40,
        "environment": {"image": "swebench/astropy:latest"},
    }


def _clean_record() -> dict:
    return {
        "instance_id": "astropy__astropy-12345",
        "fail_to_pass": {"passed": 3, "total": 3},
        "pass_to_pass": {"passed": 120, "total": 120},
        "edit_disposition": "APPLIED_RESOLVED",
        "cost": 0.42,
        "diff_bytes": 812,
    }


# --- the freeze is the source of truth -------------------------------------


def test_the_forbidden_list_comes_from_the_committed_freeze(forbidden):
    assert set(forbidden) >= {"gold_patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"}
    assert len(forbidden) == 10


def test_a_clean_packet_passes(forbidden):
    verdict = check_candidate_packet(_clean_packet(), forbidden)
    assert verdict.exit_code == EXIT_PASS, verdict.problems


@pytest.mark.parametrize(
    "leaked", ["gold_patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS", "resolved", "reward", "score"]
)
def test_every_forbidden_field_is_caught_at_the_top_level(forbidden, leaked):
    packet = _clean_packet()
    packet[leaked] = "anything"
    verdict = check_candidate_packet(packet, forbidden)
    assert verdict.exit_code == EXIT_FORBIDDEN_FIELD
    assert leaked in verdict.problems[0]


def test_a_forbidden_field_buried_in_a_nested_object_is_caught(forbidden):
    """Burying it hides it from a reader, not from the candidate."""

    packet = _clean_packet()
    packet["environment"] = {"image": "x", "metadata": {"extra": {"gold_patch": "diff --git"}}}
    verdict = check_candidate_packet(packet, forbidden)
    assert verdict.exit_code == EXIT_FORBIDDEN_FIELD
    assert "environment.metadata.extra.gold_patch" in verdict.problems[0]


def test_a_forbidden_field_inside_a_list_is_caught(forbidden):
    packet = _clean_packet()
    packet["attachments"] = [{"name": "a"}, {"test_patch": "diff --git"}]
    assert check_candidate_packet(packet, forbidden).exit_code == EXIT_FORBIDDEN_FIELD


def test_the_match_is_case_insensitive(forbidden):
    packet = _clean_packet()
    packet["Gold_Patch"] = "diff"
    assert check_candidate_packet(packet, forbidden).exit_code == EXIT_FORBIDDEN_FIELD


@pytest.mark.parametrize("bad", [None, "packet", 5, []])
def test_a_malformed_packet_cannot_be_checked(forbidden, bad):
    assert check_candidate_packet(bad, forbidden).exit_code == EXIT_CANNOT_CHECK


def test_an_unavailable_freeze_is_cannot_check_not_pass():
    assert check_candidate_packet(_clean_packet(), ()).exit_code == EXIT_CANNOT_CHECK


# --- the host outcome record -----------------------------------------------


def test_a_complete_record_passes():
    assert check_outcome_record(_clean_record()).exit_code == EXIT_PASS


@pytest.mark.parametrize("omitted", REQUIRED_OUTCOME_FIELDS)
def test_omitting_any_required_field_is_refused(omitted):
    record = _clean_record()
    del record[omitted]
    verdict = check_outcome_record(record)
    assert verdict.exit_code == EXIT_INCOMPLETE_RECORD
    assert omitted in verdict.problems[0]


def test_the_disposition_vocabulary_is_closed():
    assert EDIT_DISPOSITIONS == {
        "APPLIED_RESOLVED",
        "APPLIED_UNRESOLVED",
        "INVALID",
        "NO_OP",
        "HARMFUL",
    }


def test_an_unclassified_edit_is_refused():
    record = _clean_record()
    record["edit_disposition"] = "PROBABLY_FINE"
    assert check_outcome_record(record).exit_code == EXIT_INCOMPLETE_RECORD


def test_passed_greater_than_total_is_refused():
    record = _clean_record()
    record["fail_to_pass"] = {"passed": 5, "total": 3}
    verdict = check_outcome_record(record)
    assert verdict.exit_code == EXIT_UNRECONCILED
    assert "does not reconcile" in verdict.problems[0]


def test_a_resolved_claim_with_a_failing_test_is_refused():
    """The claim has to be consistent with the tests it rests on."""

    record = _clean_record()
    record["fail_to_pass"] = {"passed": 2, "total": 3}
    verdict = check_outcome_record(record)
    assert verdict.exit_code == EXIT_UNRECONCILED
    assert "APPLIED_RESOLVED requires" in verdict.problems[0]


def test_a_resolved_claim_that_broke_a_passing_test_is_refused():
    record = _clean_record()
    record["pass_to_pass"] = {"passed": 119, "total": 120}
    assert check_outcome_record(record).exit_code == EXIT_UNRECONCILED


def test_a_no_op_with_a_non_empty_diff_is_refused():
    record = _clean_record()
    record["edit_disposition"] = "NO_OP"
    record["fail_to_pass"] = {"passed": 0, "total": 3}
    assert check_outcome_record(record).exit_code == EXIT_UNRECONCILED


def test_a_harmful_edit_that_broke_nothing_is_refused():
    """HARMFUL is defined by broken PASS_TO_PASS, not by a label."""

    record = _clean_record()
    record["edit_disposition"] = "HARMFUL"
    record["fail_to_pass"] = {"passed": 0, "total": 3}
    verdict = check_outcome_record(record)
    assert verdict.exit_code == EXIT_UNRECONCILED
    assert "still passes" in verdict.problems[0]


def test_a_genuine_harmful_edit_is_accepted():
    record = _clean_record()
    record["edit_disposition"] = "HARMFUL"
    record["fail_to_pass"] = {"passed": 0, "total": 3}
    record["pass_to_pass"] = {"passed": 118, "total": 120}
    assert check_outcome_record(record).exit_code == EXIT_PASS


def test_a_boolean_is_not_an_integer_count():
    record = _clean_record()
    record["fail_to_pass"] = {"passed": True, "total": 3}
    assert check_outcome_record(record).exit_code == EXIT_UNRECONCILED


def test_a_negative_or_boolean_cost_is_refused():
    for bad in (-1, True):
        record = _clean_record()
        record["cost"] = bad
        assert check_outcome_record(record).exit_code == EXIT_UNRECONCILED


def test_a_zero_cost_is_allowed():
    record = _clean_record()
    record["cost"] = 0
    assert check_outcome_record(record).exit_code == EXIT_PASS


@pytest.mark.parametrize("bad", [None, "record", 7, []])
def test_a_malformed_record_cannot_be_checked(bad):
    assert check_outcome_record(bad).exit_code == EXIT_CANNOT_CHECK


def test_each_failure_mode_has_its_own_exit_code():
    assert len({EXIT_PASS, EXIT_FORBIDDEN_FIELD, EXIT_INCOMPLETE_RECORD, EXIT_UNRECONCILED, EXIT_CANNOT_CHECK}) == 5
