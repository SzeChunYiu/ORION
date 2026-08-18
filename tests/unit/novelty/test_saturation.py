"""Search saturation protocol: seven routes and two consecutive empty rounds."""

import pytest

from orion.novelty import (
    NoveltySearchRoute,
    REQUIRED_SEARCH_ROUTES,
    SearchRoundRecord,
    SearchSaturationProtocol,
    SaturationStopReport,
    assess_saturation,
    seal_certificate,
)

from orion.novelty.fixtures import example_supported_draft as _draft
from orion.novelty.fixtures import saturated_rounds as _saturated_rounds


def test_required_routes_are_exactly_the_issue_seven():
    assert len(REQUIRED_SEARCH_ROUTES) == 7
    assert NoveltySearchRoute.HOSTILE_ALREADY_SOLVED in REQUIRED_SEARCH_ROUTES
    assert NoveltySearchRoute.EXACT_TERM in REQUIRED_SEARCH_ROUTES


def test_stop_rule_requires_two_consecutive_empty_rounds():
    rounds = _saturated_rounds()
    report = assess_saturation(rounds)
    assert report.stop_rule_satisfied is True
    assert report.consecutive_empty_rounds >= 2
    assert set(report.covered_routes) == set(REQUIRED_SEARCH_ROUTES)


def test_one_empty_round_is_not_enough_to_stop():
    rounds = [
        SearchRoundRecord(
            round_index=index,
            route=route,
            queries=(f"query for {route.value}",),
            finding_ids=("hit",),
            changed_residual_or_disposition=True,
        )
        for index, route in enumerate(REQUIRED_SEARCH_ROUTES, start=1)
    ]
    rounds.append(
        SearchRoundRecord(
            round_index=len(rounds) + 1,
            route=NoveltySearchRoute.EXACT_TERM,
            queries=("single empty confirmation",),
            finding_ids=(),
            changed_residual_or_disposition=False,
        )
    )
    report = assess_saturation(tuple(rounds))
    assert report.stop_rule_satisfied is False
    assert report.consecutive_empty_rounds == 1


def test_empty_count_resets_when_a_later_round_changes_the_residual():
    rounds = list(_saturated_rounds())
    rounds.append(
        SearchRoundRecord(
            round_index=99,
            route=NoveltySearchRoute.PARENT_DISCIPLINE_HISTORY,
            queries=("historical mechanism found",),
            finding_ids=("arxiv:9999.99999",),
            changed_residual_or_disposition=True,
        )
    )
    report = assess_saturation(tuple(rounds))
    assert report.stop_rule_satisfied is False
    assert report.consecutive_empty_rounds == 0


def test_missing_hostile_route_blocks_saturation_even_with_two_empty_rounds():
    rounds = [
        SearchRoundRecord(1, NoveltySearchRoute.EXACT_TERM, ("q",), (), False),
        SearchRoundRecord(2, NoveltySearchRoute.SYNONYM_FUNCTION_ONLY, ("q",), (), False),
    ]
    report = assess_saturation(tuple(rounds))
    assert report.stop_rule_satisfied is False
    assert NoveltySearchRoute.HOSTILE_ALREADY_SOLVED in report.missing_routes


def test_incomplete_saturation_seals_as_cannot_check():
    incomplete = SearchSaturationProtocol.from_rounds(
        (
            SearchRoundRecord(1, NoveltySearchRoute.EXACT_TERM, ("q",), ("hit",), True),
            SearchRoundRecord(2, NoveltySearchRoute.EXACT_TERM, ("q2",), (), False),
            SearchRoundRecord(3, NoveltySearchRoute.EXACT_TERM, ("q3",), (), False),
        )
    )
    cert = seal_certificate(_draft(saturation=incomplete))
    from orion.novelty import NoveltyFinalState

    assert cert.final_state is NoveltyFinalState.CANNOT_CHECK
    assert any("route" in reason.lower() or "saturat" in reason.lower() for reason in cert.authority_reasons)


def test_protocol_rejects_unknown_route_injection():
    with pytest.raises((ValueError, TypeError)):
        SearchRoundRecord(
            round_index=1,
            route="NOT_A_ROUTE",  # type: ignore[arg-type]
            queries=("q",),
            finding_ids=(),
            changed_residual_or_disposition=False,
        )


def test_saturation_report_type():
    report = assess_saturation(_saturated_rounds())
    assert isinstance(report, SaturationStopReport)
    assert report.required_consecutive_empty_rounds == 2
