from __future__ import annotations

import pytest

from orion.core.search import SearchRouteKind
from orion.knowledge.routes import (
    IndependenceVerdict,
    RouteCapture,
    assess_pair,
    build_ensemble,
    estimate_coverage,
    lincoln_petersen,
)


def _capture(kind, backend, derivation, items) -> RouteCapture:
    return RouteCapture(kind, backend, derivation, frozenset(items))


_A = _capture(
    SearchRouteKind.CURRENT_VOCABULARY, "arxiv", "topic-terms", {"a", "b", "c", "d"}
)
_B = _capture(
    SearchRouteKind.PARENT_DISCIPLINE, "openalex", "discipline-mapping", {"c", "d", "e", "f"}
)


# --- independence must be constructed, not asserted ----------------------


def test_a_capture_must_declare_what_makes_it_its_own_occasion() -> None:
    with pytest.raises(ValueError):
        RouteCapture(SearchRouteKind.FRESHNESS, "  ", "d", frozenset())


def test_routes_hitting_one_backend_are_not_independent() -> None:
    """Their overlap is driven by the shared index, not by the population."""

    other = _capture(
        SearchRouteKind.FUNCTION_ONLY, "arxiv", "capability-terms", {"a", "b"}
    )
    assert assess_pair(_A, other).verdict is IndependenceVerdict.SHARED_BACKEND


def test_routes_deriving_queries_the_same_way_are_not_independent() -> None:
    other = _capture(
        SearchRouteKind.LEXICAL_VARIANT, "crossref", "topic-terms", {"a", "b"}
    )
    assert (
        assess_pair(_A, other).verdict is IndependenceVerdict.SHARED_QUERY_DERIVATION
    )


def test_one_route_kind_is_one_occasion_however_often_it_runs() -> None:
    twin = _capture(
        SearchRouteKind.CURRENT_VOCABULARY, "openalex", "other", {"a", "z"}
    )
    assert assess_pair(_A, twin).verdict is IndependenceVerdict.SAME_ROUTE_KIND


def test_genuinely_separate_routes_are_accepted() -> None:
    assert assess_pair(_A, _B).independent
    assert assess_pair(_A, _B).overlap == 2


# --- estimation, and the refusals that dominate --------------------------


def test_a_single_occasion_cannot_estimate_anything() -> None:
    estimate = estimate_coverage([_A])
    assert estimate.population_estimate is None
    assert "at least two" in estimate.refusal_reason


def test_dependent_occasions_are_refused_rather_than_estimated() -> None:
    """Positive dependence biases unseen mass downward, so an estimate from
    dependent routes is worse than none: it fails toward 'nearly done'."""

    dependent = _capture(
        SearchRouteKind.FUNCTION_ONLY, "arxiv", "capability-terms", {"a", "b", "x"}
    )
    estimate = estimate_coverage([_A, dependent])
    assert estimate.population_estimate is None
    assert "no independent pair" in estimate.refusal_reason


def test_zero_overlap_places_no_upper_bound() -> None:
    """Two routes sharing nothing constrain the population not at all;
    returning a huge number would read as a measurement."""

    disjoint = _capture(
        SearchRouteKind.FRESHNESS, "europepmc", "recency", {"x", "y", "z"}
    )
    estimate = estimate_coverage([_A, disjoint])
    assert estimate.population_estimate is None
    assert "unbounded above" in estimate.refusal_reason
    assert lincoln_petersen(4, 3, 0) is None


def test_an_independent_overlapping_pair_yields_a_diagnostic_estimate() -> None:
    estimate = estimate_coverage([_A, _B])
    assert estimate.population_estimate == pytest.approx(8.0)  # 4*4/2
    assert estimate.observed == 6
    assert estimate.estimated_unseen == pytest.approx(2.0)
    assert estimate.coverage_fraction == pytest.approx(0.75)
    assert estimate.diagnostic_only


def test_the_most_conservative_independent_estimate_is_taken() -> None:
    """The largest population implies the most still unfound — the direction
    that fails safe."""

    third = _capture(
        SearchRouteKind.CITATION_NEIGHBORHOOD, "crossref", "reference-graph", {"a", "q", "r", "s"}
    )
    estimate = estimate_coverage([_A, _B, third])
    # A-B gives 8.0; A-third overlaps on {a} alone giving 16.0.
    assert estimate.population_estimate == pytest.approx(16.0)


def test_no_estimate_is_ever_a_stopping_authority() -> None:
    assert estimate_coverage([_A, _B]).diagnostic_only is True


# --- the ensemble view ---------------------------------------------------


def test_the_frequency_spectrum_is_computed_over_content_not_ids() -> None:
    report = build_ensemble([_A, _B])
    assert report.union == frozenset({"a", "b", "c", "d", "e", "f"})
    assert report.singletons == 4  # a, b, e, f
    assert report.doubletons == 2  # c, d


def test_every_pair_is_judged_not_only_the_accepted_ones() -> None:
    same_backend = _capture(
        SearchRouteKind.FUNCTION_ONLY, "arxiv", "capability", {"a"}
    )
    report = build_ensemble([_A, _B, same_backend])
    assert len(report.pairs) == 3
    assert sum(1 for item in report.pairs if item.independent) == 2
