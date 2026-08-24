"""The P3 analysis-unit rule must fail closed, and must not fire on honest reports.

The rule these tests protect is that a P3 aggregate takes an ontology pair, a
track or a case as its unit -- never a correspondence row. The interesting
half is the negative: a guard that also rejects correct reports is worse than
no guard, because it gets switched off. So the honest V21 stance is asserted
to PASS alongside every violation that must fail.
"""

from __future__ import annotations

import pytest

from orion.study.p3.analysis_unit_guard import (
    ADMISSIBLE_UNITS,
    EXIT_CANNOT_CHECK,
    EXIT_INADMISSIBLE_UNIT,
    EXIT_INTERVAL_UNDERPOWERED,
    EXIT_NO_UNIT,
    EXIT_PASS,
    assess_report,
)


def _report(**aggregate):
    return {"aggregates": [{"name": "primary", **aggregate}]}


def test_the_v21_stance_passes():
    """V21 reported exact counts on one case and no interval. That must pass."""

    verdict = assess_report(_report(analysis_unit="case", case_count=1))
    assert verdict.exit_code == EXIT_PASS
    assert verdict.passed
    assert verdict.problems == ()


@pytest.mark.parametrize("unit", sorted(ADMISSIBLE_UNITS))
def test_every_admissible_unit_passes(unit):
    assert assess_report(_report(analysis_unit=unit, case_count=1)).exit_code == EXIT_PASS


def test_a_correspondence_row_unit_is_refused():
    verdict = assess_report(_report(analysis_unit="correspondence_row", case_count=91))
    assert verdict.exit_code == EXIT_INADMISSIBLE_UNIT
    assert "correspondence_row" in verdict.problems[0]


def test_a_pair_cell_unit_is_refused_even_with_many_rows():
    """91 correspondences inside one pair are still n=1, not n=91."""

    assert assess_report(_report(analysis_unit="pair_cell", case_count=91)).exit_code == EXIT_INADMISSIBLE_UNIT


def test_an_unrecognised_unit_is_refused_rather_than_assumed_fine():
    verdict = assess_report(_report(analysis_unit="ontology_pairs", case_count=9))
    assert verdict.exit_code == EXIT_INADMISSIBLE_UNIT
    assert "unrecognised" in verdict.problems[0]


def test_an_aggregate_with_no_declared_unit_is_refused():
    assert assess_report(_report(case_count=9)).exit_code == EXIT_NO_UNIT


def test_an_interval_on_one_case_is_refused():
    verdict = assess_report(_report(analysis_unit="case", case_count=1, ci_lower=0.1, ci_upper=0.4))
    assert verdict.exit_code == EXIT_INTERVAL_UNDERPOWERED


def test_a_zero_p_value_still_counts_as_a_population_claim():
    """Presence, not truthiness: p=0.0 is a claim, and 0.0 is falsy."""

    assert assess_report(_report(analysis_unit="case", case_count=1, p_value=0.0)).exit_code == EXIT_INTERVAL_UNDERPOWERED


def test_a_bootstrap_over_few_cases_is_refused():
    assert assess_report(_report(analysis_unit="track", case_count=3, bootstrap={"resamples": 10000})).exit_code == EXIT_INTERVAL_UNDERPOWERED


def test_an_interval_at_the_minimum_case_count_passes():
    assert assess_report(_report(analysis_unit="case", case_count=7, ci_lower=0.1)).exit_code == EXIT_PASS


def test_an_interval_without_a_case_count_cannot_be_checked():
    """Missing the denominator is CANNOT_CHECK, never a pass."""

    assert assess_report(_report(analysis_unit="case", ci_lower=0.1)).exit_code == EXIT_CANNOT_CHECK


@pytest.mark.parametrize("bad", [None, "report", 3, [], {}, {"aggregates": []}, {"aggregates": {}}])
def test_malformed_reports_cannot_be_checked_and_never_pass(bad):
    verdict = assess_report(bad)
    assert verdict.exit_code == EXIT_CANNOT_CHECK
    assert not verdict.passed


def test_cannot_check_is_a_distinct_code_from_pass_and_from_failure():
    assert len({EXIT_PASS, EXIT_INADMISSIBLE_UNIT, EXIT_INTERVAL_UNDERPOWERED, EXIT_NO_UNIT, EXIT_CANNOT_CHECK}) == 5


def test_the_worst_problem_across_several_aggregates_decides_the_exit_code():
    report = {
        "aggregates": [
            {"name": "ok", "analysis_unit": "case", "case_count": 1},
            {"name": "bad", "analysis_unit": "mapping", "case_count": 1},
        ]
    }
    assert assess_report(report).exit_code == EXIT_INADMISSIBLE_UNIT
