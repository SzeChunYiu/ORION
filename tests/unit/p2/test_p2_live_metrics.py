"""Denominator-free metrics, and the refusals that keep them honest.

The guard is the point of this file. A live campaign cannot report recall, and
"cannot check" must not be readable as "checked and fine" — so asking for a
denominator-bound metric raises a typed error naming the reason, rather than
returning zero, ``None`` or a plausible number.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.core.search import SearchRouteKind
from orion.kernel.store import LedgerStore
from orion.knowledge.providers.arxiv import ArxivClient, TransportResponse
from orion.knowledge.providers.openalex import OpenAlexClient
from orion.knowledge.rate import RateGate
from orion.knowledge.route_control import FrozenRouteControlPolicy
from orion.study.p2.live_campaign import (
    LiveOutcome,
    LiveRoute,
    ResearchQuestion,
    arxiv_searcher,
    keyword_planner,
    openalex_keyword_searcher,
    run_campaign,
)
from orion.study.p2.live_metrics import (
    DENOMINATOR_BOUND_METRICS,
    IncompleteDenominator,
    campaign_report,
    completeness,
    cost_and_latency,
    coverage_diagnostic,
    denominator_bound_metric,
    earned_independent_pairs,
    false_negative_count,
    independence_verdicts,
    marginal_gain,
    metric_is_reportable,
    open_obligation_census,
    outcome_census,
    read_state_census,
    recall,
    require_complete_denominator,
    route_overlap,
    unique_contribution_per_route,
)

POLICY = FrozenRouteControlPolicy("p2.live.v1", 2, 3)
QUESTION = ResearchQuestion("q1", "route independence", "frame:x", "schema-v0")
DOI = "10.1103/PhysRevD.94.025011"


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        self.now += 0.01
        return self.now


def _atom(*entries: tuple[str, str, str, str]) -> str:
    body = [
        "<feed xmlns:arxiv='http://arxiv.org/schemas/atom' "
        "xmlns='http://www.w3.org/2005/Atom'>"
    ]
    for raw_id, title, summary, doi in entries:
        body.append(
            f"<entry><id>{raw_id}</id><title>{title}</title>"
            f"<summary>{summary}</summary>"
            + (f"<arxiv:doi>{doi}</arxiv:doi>" if doi else "")
            + "</entry>"
        )
    body.append("</feed>")
    return "".join(body)


def _works(*records: tuple[str, str, str, str]) -> str:
    results = [
        {
            "id": raw_id,
            "display_name": title,
            "abstract_inverted_index": {abstract: [0]} if abstract else None,
            "ids": {"doi": doi} if doi else {},
        }
        for raw_id, title, abstract, doi in records
    ]
    return json.dumps({"results": results, "meta": {"count": 3, "cost_usd": 0.001}})


def _scripted(*responses):
    queue = list(responses)

    def transport(url: str):
        item = queue.pop(0) if queue else responses[-1]
        if isinstance(item, Exception):
            raise item
        return item

    return transport


def _campaign(tmp_path: Path, arxiv_body, openalex_body, *, variants=("a",)):
    gate = RateGate(clock=Clock())
    arxiv = LiveRoute(
        route_id="arxiv-topic",
        route_kind=SearchRouteKind.CURRENT_VOCABULARY,
        backend="arxiv",
        query_derivation="frozen-question-terms",
        provider="arxiv",
        searcher=arxiv_searcher(ArxivClient(transport=_scripted(arxiv_body), gate=gate)),
        plan_query=keyword_planner("frozen-question-terms", variants),
        budget_units=float(len(variants)),
    )
    openalex = LiveRoute(
        route_id="openalex-keyword",
        route_kind=SearchRouteKind.PARENT_DISCIPLINE,
        backend="openalex",
        query_derivation="discipline-keyword-mapping",
        provider="openalex",
        searcher=openalex_keyword_searcher(
            OpenAlexClient(
                transport=_scripted(openalex_body), api_key="test-key", gate=gate
            )
        ),
        plan_query=keyword_planner("discipline-keyword-mapping", variants),
        budget_units=float(len(variants)),
    )
    return run_campaign(
        "c1",
        QUESTION,
        [arxiv, openalex],
        store=LedgerStore(tmp_path / "state"),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )


def _shared_work_campaign(tmp_path: Path):
    """Both routes find the same paper, plus one of their own."""

    return _campaign(
        tmp_path,
        TransportResponse(
            200,
            _atom(
                ("http://arxiv.org/abs/1606.01772v2", "Shared", "author abstract", DOI),
                ("http://arxiv.org/abs/2001.00001", "ArxivOnly", "s", ""),
            ),
        ),
        TransportResponse(
            200,
            _works(
                ("https://openalex.org/W1", "Shared", "reconstructed", f"https://doi.org/{DOI}"),
                ("https://openalex.org/W2", "OpenAlexOnly", "o", ""),
            ),
        ),
    )


# --- the guard: cannot check is not a pass ---------------------------------


@pytest.mark.parametrize("metric", sorted(DENOMINATOR_BOUND_METRICS))
def test_every_denominator_bound_metric_is_refused(tmp_path: Path, metric: str) -> None:
    result = _shared_work_campaign(tmp_path)
    with pytest.raises(IncompleteDenominator) as error:
        denominator_bound_metric(result, metric)
    assert "complete denominator" in str(error.value)


def test_recall_raises_rather_than_returning_a_number(tmp_path: Path) -> None:
    result = _shared_work_campaign(tmp_path)
    with pytest.raises(IncompleteDenominator):
        recall(result)


def test_false_negative_count_raises(tmp_path: Path) -> None:
    result = _shared_work_campaign(tmp_path)
    with pytest.raises(IncompleteDenominator):
        false_negative_count(result)


def test_completeness_raises(tmp_path: Path) -> None:
    result = _shared_work_campaign(tmp_path)
    with pytest.raises(IncompleteDenominator):
        completeness(result)


def test_the_refusal_explains_that_the_quantity_is_undefined_not_unmeasured(
    tmp_path: Path,
) -> None:
    with pytest.raises(IncompleteDenominator) as error:
        recall(_shared_work_campaign(tmp_path))
    message = str(error.value)
    assert "indistinguishable from a nonexistent one" in message
    assert "complete-gold" in message


def test_an_unrecognised_metric_is_also_refused(tmp_path: Path) -> None:
    """Silence on an unknown name would let a typo read as a passing check."""

    with pytest.raises(IncompleteDenominator):
        denominator_bound_metric(_shared_work_campaign(tmp_path), "made_up_metric")


def test_reportable_metrics_are_not_refused() -> None:
    """The no-alarm case: the guard must not block what a live run can measure."""

    assert metric_is_reportable("unique_relevant_per_route")
    assert metric_is_reportable("route_overlap_content_digest")
    require_complete_denominator("marginal_relevant_gain")  # must not raise


def test_the_guard_is_case_insensitive() -> None:
    assert not metric_is_reportable("Recall")
    assert not metric_is_reportable("  FALSE_NEGATIVE_COUNT ")


# --- what a live campaign can honestly report ------------------------------


def test_unique_contribution_counts_a_shared_work_for_neither_route(
    tmp_path: Path,
) -> None:
    contributions = unique_contribution_per_route(_shared_work_campaign(tmp_path))
    by_route = {item.route_id: item for item in contributions}
    assert by_route["arxiv-topic"].retrieved == 2
    assert by_route["openalex-keyword"].retrieved == 2
    assert by_route["arxiv-topic"].unique_to_route == 1
    assert by_route["openalex-keyword"].unique_to_route == 1


def test_route_overlap_is_computed_over_resolved_works(tmp_path: Path) -> None:
    overlap = route_overlap(_shared_work_campaign(tmp_path))
    assert overlap[("arxiv-topic", "openalex-keyword")] == 1


def test_marginal_gain_reports_what_each_added_route_bought(tmp_path: Path) -> None:
    curve = marginal_gain(_shared_work_campaign(tmp_path))
    assert curve[0] == ("arxiv-topic", 2, 2)
    assert curve[1] == ("openalex-keyword", 3, 1)


def test_independence_is_reported_for_every_pair(tmp_path: Path) -> None:
    result = _shared_work_campaign(tmp_path)
    assert len(independence_verdicts(result)) == 1
    assert len(earned_independent_pairs(result)) == 1


def test_the_coverage_estimate_is_marked_diagnostic_only(tmp_path: Path) -> None:
    estimate = coverage_diagnostic(_shared_work_campaign(tmp_path))
    assert estimate.diagnostic_only is True
    assert estimate.population_estimate == pytest.approx(4.0)  # 2*2/1


def test_the_outcome_census_retains_failures(tmp_path: Path) -> None:
    result = _campaign(
        tmp_path,
        TransportResponse(503, ""),
        TransportResponse(200, _works(("https://openalex.org/W1", "A", "a", ""))),
    )
    census = outcome_census(result)
    assert census[LiveOutcome.PROVIDER_ERROR.value] == 1
    assert census[LiveOutcome.RESULTS.value] == 1
    assert open_obligation_census(result) == {"arxiv-topic": ("PROVIDER_ERROR",)}


def test_a_clean_campaign_reports_no_open_obligations(tmp_path: Path) -> None:
    """The no-alarm case: a healthy run must not manufacture an obligation."""

    assert open_obligation_census(_shared_work_campaign(tmp_path)) == {}


def test_the_read_state_census_separates_reread_from_duplicate_processing(
    tmp_path: Path,
) -> None:
    census = read_state_census(_shared_work_campaign(tmp_path))
    assert census["UNSEEN"] >= 3
    # The shared work arrives a second time as a different rendition, which is
    # a legitimate content-changed reread, not duplicate processing.
    assert census.get("CONTENT_CHANGED", 0) == 1
    assert census.get("ALREADY_READ", 0) == 0


def test_cost_and_latency_are_reported(tmp_path: Path) -> None:
    numbers = cost_and_latency(_shared_work_campaign(tmp_path))
    assert numbers["attempts"] == 2.0
    assert numbers["queries"] == 2.0
    assert numbers["spent_usd"] == pytest.approx(0.001)
    assert numbers["wallclock_seconds"] > 0


def test_the_report_declares_its_own_denominator_and_omits_recall(
    tmp_path: Path,
) -> None:
    report = campaign_report(_shared_work_campaign(tmp_path))
    assert report["denominator"] == "INCOMPLETE_OPEN_WORLD"
    assert report["recall_reportable"] is False
    serialized = json.dumps(report)
    for forbidden in ("\"recall\"", "false_negative", "completeness"):
        assert forbidden not in serialized


def test_the_report_is_reproducible_from_the_same_recorded_run(
    tmp_path: Path,
) -> None:
    first = campaign_report(_shared_work_campaign(tmp_path / "one"))
    second = campaign_report(_shared_work_campaign(tmp_path / "two"))
    for key in first:
        if key == "cost_and_latency":
            continue  # wallclock is the one field a rerun legitimately moves
        assert first[key] == second[key], f"{key} was not reproducible"
