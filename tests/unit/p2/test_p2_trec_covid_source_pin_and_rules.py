"""The Round-5 source pin, and NIST's evaluation rules as refusals.

The pin is asserted against its own recorded measurements rather than against a
citation, because a citation cannot tell you whether the file you have is the
file NIST served. The rules are asserted by breaking them.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p2.trec_covid_rules import (
    EXIT_CANNOT_CHECK,
    EXIT_CROSS_ROUND,
    EXIT_PASS,
    EXIT_REJUDGMENT,
    EXIT_RESIDUAL,
    Judgment,
    check_cross_round_comparison,
    check_residual_run,
    resolve_rejudged,
)

PIN = "papers/paper-02-open-world-scientific-discovery/protocol/P2_TREC_COVID_ROUND5_SOURCE_PIN_V1.json"


def _root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / PIN).is_file():
            return parent
    pytest.skip("source pin not found")


@pytest.fixture(scope="module")
def pin() -> dict:
    return json.loads((_root() / PIN).read_text(encoding="utf-8"))


# --- the pin ---------------------------------------------------------------


def test_the_release_is_named_not_left_as_bare_cord19(pin):
    """'CORD-19' without a date does not identify a document set."""

    assert pin["document_collection"]["release"] == "2020-07-16"
    assert pin["document_collection"]["valid_document_count"] == 191175


def test_every_pinned_file_carries_a_full_sha256_and_a_byte_count(pin):
    assert len(pin["pinned_files"]) == 4
    for entry in pin["pinned_files"]:
        assert len(entry["sha256"]) == 64, entry["file"]
        assert int(entry["bytes"]) > 0
        assert entry["url"].startswith("https://ir.nist.gov/covidSubmit/data/")


def test_the_four_files_are_the_ones_that_define_the_round(pin):
    names = {entry["file"] for entry in pin["pinned_files"]}
    assert names == {
        "docids-rnd5.txt",
        "topics-rnd5.xml",
        "qrels-covid_d5_j0.5-5.txt",
        "rejudgments.txt",
    }


def test_the_judged_documents_are_contained_in_the_valid_identifiers(pin):
    """The integrity check that would catch a mismatched corpus revision."""

    qrels = next(e for e in pin["pinned_files"] if e["file"].startswith("qrels"))
    judged = qrels["measured"]["distinct_judged_docids"]
    assert judged == 37924
    assert judged < pin["document_collection"]["valid_document_count"]
    assert any("zero orphans" in check for check in pin["integrity_checks_that_passed_at_pin_time"])


def test_the_topic_set_is_the_full_fifty(pin):
    topics = next(e for e in pin["pinned_files"] if e["file"].startswith("topics"))
    assert topics["measured"]["topics"] == 50
    assert topics["measured"]["topic_number_range"] == [1, 50]
    qrels = next(e for e in pin["pinned_files"] if e["file"].startswith("qrels"))
    assert qrels["measured"]["distinct_topics"] == 50


def test_the_out_of_scale_label_is_recorded_and_not_repaired(pin):
    """Two rows carry -1. Coercing them silently would move the denominator."""

    qrels = next(e for e in pin["pinned_files"] if e["file"].startswith("qrels"))
    assert qrels["measured"]["judgment_label_counts"]["-1"] == 2
    anomaly = pin["anomaly_recorded_not_repaired"]
    assert "not repaired" in anomaly["disposition"]


def test_the_pin_does_not_claim_to_redistribute_the_corpus(pin):
    assert "cord19_document_bodies" in pin["not_pinned_here"]
    assert pin["results_exist"] is False and pin["campaign_executed"] is False


# --- residual collection ---------------------------------------------------


def test_a_clean_residual_run_passes():
    verdict = check_residual_run({"1": ["a", "b"]}, {"1": ["c", "d"]})
    assert verdict.exit_code == EXIT_PASS and verdict.passed


def test_returning_a_previously_judged_document_is_refused():
    verdict = check_residual_run({"1": ["a", "c"]}, {"1": ["c"]})
    assert verdict.exit_code == EXIT_RESIDUAL
    assert "previously judged" in verdict.problems[0]


def test_a_duplicate_docid_in_the_ranking_is_refused():
    verdict = check_residual_run({"1": ["a", "a"]}, {"1": []})
    assert verdict.exit_code == EXIT_RESIDUAL
    assert "duplicate" in verdict.problems[0]


def test_a_topic_with_no_prior_judgments_is_unconstrained():
    assert check_residual_run({"9": ["a"]}, {"1": ["a"]}).exit_code == EXIT_PASS


@pytest.mark.parametrize("bad", [({}, {}), ("run", {}), ({"1": "abc"}, {})])
def test_malformed_residual_input_cannot_be_checked(bad):
    assert check_residual_run(*bad).exit_code == EXIT_CANNOT_CHECK


# --- cross-round comparison ------------------------------------------------


def test_comparing_different_topic_sets_unrestricted_is_refused():
    """NIST: merged qrels scores may not be compared to a round's own scores."""

    verdict = check_cross_round_comparison(
        ["1", "2", "3"], ["1"], left_round="1", right_round="2", restricted_to_common_subset=False
    )
    assert verdict.exit_code == EXIT_CROSS_ROUND
    assert "common topic subset" in verdict.problems[0]


def test_restricting_to_the_common_subset_is_allowed():
    assert check_cross_round_comparison(
        ["1", "2", "3"], ["1"], left_round="1", right_round="2", restricted_to_common_subset=True
    ).exit_code == EXIT_PASS


def test_identical_topic_sets_need_no_restriction():
    assert check_cross_round_comparison(
        ["1", "2"], ["2", "1"], left_round="4", right_round="5", restricted_to_common_subset=False
    ).exit_code == EXIT_PASS


def test_rounds_sharing_no_topics_have_no_valid_comparison():
    verdict = check_cross_round_comparison(
        ["1"], ["9"], left_round="1", right_round="2", restricted_to_common_subset=True
    )
    assert verdict.exit_code == EXIT_CROSS_ROUND
    assert "share no topics" in verdict.problems[-1]


# --- rejudgment ------------------------------------------------------------


def test_rounds_order_numerically_not_lexically():
    """'4.5' precedes '5'; string ordering would put '4.5' after '10'."""

    resolved, _ = resolve_rejudged(
        [Judgment("1", "4.5", "d", 1), Judgment("1", "5", "d", 2)], target_round="5"
    )
    assert resolved[("1", "d")] == 2


def test_a_changed_judgment_is_resolved_but_reported():
    resolved, verdict = resolve_rejudged(
        [Judgment("1", "1", "d", 0), Judgment("1", "4.5", "d", 2)], target_round="5"
    )
    assert resolved[("1", "d")] == 2
    assert verdict.exit_code == EXIT_REJUDGMENT
    assert "rejudged" in verdict.problems[0]


def test_a_judgment_from_a_later_round_is_not_used_for_an_earlier_one():
    resolved, verdict = resolve_rejudged([Judgment("1", "5", "d", 2)], target_round="2")
    assert ("1", "d") not in resolved
    assert "not resolvable" in verdict.problems[0]


def test_a_single_stable_judgment_passes_quietly():
    resolved, verdict = resolve_rejudged([Judgment("1", "2", "d", 1)], target_round="5")
    assert resolved == {("1", "d"): 1}
    assert verdict.exit_code == EXIT_PASS


def test_an_unorderable_round_cannot_be_checked():
    _, verdict = resolve_rejudged([Judgment("1", "x", "d", 1)], target_round="5")
    assert verdict.exit_code == EXIT_CANNOT_CHECK


def test_each_failure_mode_has_its_own_exit_code():
    assert len({EXIT_PASS, EXIT_RESIDUAL, EXIT_CROSS_ROUND, EXIT_REJUDGMENT, EXIT_CANNOT_CHECK}) == 5
