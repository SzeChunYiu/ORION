from __future__ import annotations

from pathlib import Path

from orion.core.search import SearchRouteKind
from orion.kernel.store import LedgerStore
from orion.knowledge.identity import ReadDecision
from orion.knowledge.research_loop import (
    RetrievedDoc,
    RouteBinding,
    derive_route_query,
    packet_summary,
    run_research_round,
)
from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.questioning import generate_mechanic_questions

CELL = MechanicCell(
    mechanic_id="SEARCH.ROUTE_STOP.v0",
    purpose="Decide when one search route is exhausted.",
    scope="one route",
)


def _question(dimension=MechanicDimension.MATHEMATICS):
    return next(
        item for item in generate_mechanic_questions(CELL) if item.dimension is dimension
    )


class _Fixed:
    def __init__(self, docs): self._docs = docs
    def search(self, query): return self._docs


class _Broken:
    def search(self, query):
        raise TimeoutError("backend unreachable")


_D1 = RetrievedDoc("arxiv:2404.01176", "chao estimator as a stopping criterion", "Chao TAR")
_D2 = RetrievedDoc("arxiv:2606.15380", "confidence based stopping methods", "Confidence stopping")
_D3 = RetrievedDoc("doi:10.1186/s13643-020-01521-4", "hypergeometric stopping criteria", "Statistical stopping")


def _store(tmp_path): return LedgerStore(tmp_path / "state")


def _bindings(*, second_backend="openalex", second_derivation="discipline-mapping"):
    return [
        RouteBinding(SearchRouteKind.CURRENT_VOCABULARY, "arxiv", "topic-terms", _Fixed([_D1, _D2])),
        RouteBinding(SearchRouteKind.PARENT_DISCIPLINE, second_backend, second_derivation, _Fixed([_D2, _D3])),
    ]


# --- the bridge ----------------------------------------------------------


def test_an_open_question_becomes_retrieved_deduped_evidence(tmp_path: Path) -> None:
    packet = run_research_round(_store(tmp_path), CELL, _question(), _bindings())

    assert packet.mechanic_id == "SEARCH.ROUTE_STOP.v0"
    assert len(packet.candidates) == 3          # D2 found twice, counted once
    assert all(item.read_decision is ReadDecision.UNSEEN for item in packet.candidates)


def test_a_document_found_by_two_routes_is_marked_corroborated(tmp_path: Path) -> None:
    packet = run_research_round(_store(tmp_path), CELL, _question(), _bindings())
    corroborated = [item for item in packet.candidates if item.corroborated]

    assert len(corroborated) == 1
    assert corroborated[0].source_id == "arxiv:2606.15380"
    assert len(corroborated[0].found_by) == 2


def test_routes_derive_different_queries(tmp_path: Path) -> None:
    """Routes that merely reword one query are not separate occasions; an
    ensemble built from them measures the phrasing, not the literature."""

    question = _question()
    queries = {
        derive_route_query(CELL, question, route)
        for route in (
            SearchRouteKind.CURRENT_VOCABULARY,
            SearchRouteKind.FUNCTION_ONLY,
            SearchRouteKind.PARENT_DISCIPLINE,
            SearchRouteKind.ADVERSARIAL_OMISSION,
        )
    }
    assert len(queries) == 4


# --- what the packet refuses to do --------------------------------------


def test_the_packet_stops_short_of_an_answer(tmp_path: Path) -> None:
    """Turning evidence into a claim needs comprehension, which is a provider
    port — not something this module may quietly perform."""

    packet = run_research_round(_store(tmp_path), CELL, _question(), _bindings())
    assert not hasattr(packet, "answer")
    assert not hasattr(packet, "conclusion")


def test_a_declared_route_with_no_backend_is_an_open_gap(tmp_path: Path) -> None:
    packet = run_research_round(
        _store(tmp_path),
        CELL,
        _question(),
        _bindings(),
        declared_routes=[
            SearchRouteKind.CURRENT_VOCABULARY,
            SearchRouteKind.PARENT_DISCIPLINE,
            SearchRouteKind.ADVERSARIAL_OMISSION,
        ],
    )
    assert packet.unavailable_routes == (SearchRouteKind.ADVERSARIAL_OMISSION,)
    assert packet.coverage_obligations_open


def test_a_failing_backend_becomes_a_coverage_gap_not_a_silent_zero(tmp_path: Path) -> None:
    bindings = [
        RouteBinding(SearchRouteKind.CURRENT_VOCABULARY, "arxiv", "topic-terms", _Fixed([_D1])),
        RouteBinding(SearchRouteKind.FRESHNESS, "europepmc", "recency", _Broken()),
    ]
    packet = run_research_round(_store(tmp_path), CELL, _question(), bindings)

    assert SearchRouteKind.FRESHNESS in packet.unavailable_routes
    assert len(packet.candidates) == 1


# --- independence is checked, not assumed -------------------------------


def test_routes_sharing_a_backend_yield_no_coverage_estimate(tmp_path: Path) -> None:
    packet = run_research_round(
        _store(tmp_path), CELL, _question(), _bindings(second_backend="arxiv")
    )
    assert packet.coverage.population_estimate is None
    assert "no independent pair" in packet.coverage.refusal_reason


def test_genuinely_independent_routes_yield_a_diagnostic_estimate(tmp_path: Path) -> None:
    packet = run_research_round(_store(tmp_path), CELL, _question(), _bindings())
    assert packet.coverage.independent_pairs == 1
    assert packet.coverage.population_estimate == 4.0   # 2*2/1
    assert packet.coverage.diagnostic_only


# --- the read ledger, framed by question ---------------------------------


def test_the_same_search_run_twice_reads_nothing_new(tmp_path: Path) -> None:
    run_research_round(_store(tmp_path), CELL, _question(), _bindings())
    again = run_research_round(_store(tmp_path), CELL, _question(), _bindings())
    assert again.fresh == ()


def test_the_same_paper_is_read_again_for_a_different_question(tmp_path: Path) -> None:
    """'We have seen this paper' is not 'we have covered this question'."""

    run_research_round(_store(tmp_path), CELL, _question(), _bindings())
    other = run_research_round(
        _store(tmp_path), CELL, _question(MechanicDimension.FAILURE), _bindings()
    )
    assert all(
        item.read_decision is ReadDecision.NEW_FRAME for item in other.candidates
    )


def test_the_summary_is_machine_readable(tmp_path: Path) -> None:
    packet = run_research_round(_store(tmp_path), CELL, _question(), _bindings())
    summary = packet_summary(packet)
    assert summary["corroborated"] == 1
    assert summary["observed"] == 3
    assert summary["independent_pairs"] == 1
