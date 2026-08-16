"""The live campaign engine, driven entirely by fake transports.

No network. Every provider behaviour that matters operationally — results,
empty result sets, service errors, timeouts, rate limits, missing credentials
and a mid-campaign outage — is scripted here, and each is asserted to land in
its own recorded outcome. The invariant under all of them is that none is ever
readable as evidence that a work does not exist.
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
from orion.knowledge.route_control import FrozenRouteControlPolicy, RouteControlAction
from orion.knowledge.routes import IndependenceVerdict, estimate_coverage
from orion.study.p2.live_campaign import (
    LiveOutcome,
    LiveRoute,
    ResearchQuestion,
    arxiv_searcher,
    assess_task_closure,
    citation_planner,
    classify_transport_note,
    keyword_planner,
    openalex_citation_searcher,
    openalex_keyword_searcher,
    run_campaign,
    run_route,
)

POLICY = FrozenRouteControlPolicy("p2.live.v1", 2, 3)
QUESTION = ResearchQuestion(
    question_id="q1",
    text="route independence",
    frame_id="frame:open-world-discovery",
    extraction_schema_version="claim-extraction-v0",
)
DOI = "10.1103/PhysRevD.94.025011"


# --- fake backends ---------------------------------------------------------


def _atom(*entries: tuple[str, str, str, str]) -> str:
    body = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<feed xmlns:arxiv='http://arxiv.org/schemas/atom' "
        "xmlns='http://www.w3.org/2005/Atom'>",
    ]
    for raw_id, title, summary, doi in entries:
        body.append("<entry>")
        body.append(f"<id>{raw_id}</id>")
        body.append(f"<title>{title}</title>")
        body.append(f"<summary>{summary}</summary>")
        if doi:
            body.append(f"<arxiv:doi>{doi}</arxiv:doi>")
        body.append("</entry>")
    body.append("</feed>")
    return "".join(body)


def _works(*records: tuple[str, str, str, str], cost: float = 0.001, count: int = 7) -> str:
    results = []
    for raw_id, title, abstract, doi in records:
        inverted: dict[str, list[int]] = {}
        for position, token in enumerate(abstract.split()):
            inverted.setdefault(token, []).append(position)
        results.append(
            {
                "id": raw_id,
                "display_name": title,
                "abstract_inverted_index": inverted,
                "ids": {"doi": doi} if doi else {},
                "referenced_works": [],
            }
        )
    return json.dumps(
        {"results": results, "meta": {"count": count, "cost_usd": cost, "next_cursor": ""}}
    )


class Clock:
    """A clock the test drives, so rate spacing is exercised without waiting."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        self.now += 0.01
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _scripted(*responses):
    """A transport returning each scripted response in turn.

    A response may be a ``TransportResponse`` or an exception instance, which
    is raised — that is how a timeout or a refused connection is scripted.
    """

    queue = list(responses)

    def transport(url: str):
        item = queue.pop(0) if queue else responses[-1]
        if isinstance(item, Exception):
            raise item
        return item

    return transport


def _ok(body: str) -> TransportResponse:
    return TransportResponse(200, body)


def _store(tmp_path: Path, name: str = "state") -> LedgerStore:
    return LedgerStore(tmp_path / name)


def _arxiv_route(
    transport, *, budget: float = 3.0, variants=("route independence",), gate=None
) -> LiveRoute:
    return LiveRoute(
        route_id="arxiv-topic",
        route_kind=SearchRouteKind.CURRENT_VOCABULARY,
        backend="arxiv",
        query_derivation="frozen-question-terms",
        provider="arxiv",
        searcher=arxiv_searcher(
            ArxivClient(transport=transport, gate=gate or RateGate(clock=Clock()))
        ),
        plan_query=keyword_planner("frozen-question-terms", variants),
        budget_units=budget,
    )


def _openalex_route(
    transport, *, budget: float = 3.0, variants=("route independence",), gate=None
) -> LiveRoute:
    return LiveRoute(
        route_id="openalex-keyword",
        route_kind=SearchRouteKind.PARENT_DISCIPLINE,
        backend="openalex",
        query_derivation="discipline-keyword-mapping",
        provider="openalex",
        searcher=openalex_keyword_searcher(
            OpenAlexClient(
                transport=transport,
                api_key="test-key",
                gate=gate or RateGate(clock=Clock()),
            )
        ),
        plan_query=keyword_planner("discipline-keyword-mapping", variants),
        budget_units=budget,
        cost_budget_usd=0.05,
    )


def _citation_route(transport, *, budget: float = 3.0, gate=None) -> LiveRoute:
    return LiveRoute(
        route_id="openalex-citation",
        route_kind=SearchRouteKind.CITATION_NEIGHBORHOOD,
        backend="openalex",
        query_derivation="reference-graph-from-confirmed-seeds",
        provider="openalex",
        searcher=openalex_citation_searcher(
            OpenAlexClient(
                transport=transport,
                api_key="test-key",
                gate=gate or RateGate(clock=Clock()),
            )
        ),
        plan_query=citation_planner("reference-graph-from-confirmed-seeds"),
        budget_units=budget,
        cost_budget_usd=0.05,
    )


# --- every transport outcome is its own recorded fact ----------------------


def test_results_are_recorded_as_results(tmp_path: Path) -> None:
    transport = _scripted(_ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", DOI))))
    run = run_route(
        _arxiv_route(transport),
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert run.attempts[0].outcome is LiveOutcome.RESULTS
    assert run.attempts[0].identities[0].work_key == "arxiv:1606.01772"
    assert len(run.capture.captured) == 1


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (TransportResponse(503, ""), LiveOutcome.PROVIDER_ERROR),
        (TransportResponse(403, ""), LiveOutcome.TRANSPORT_ERROR),
        (TimeoutError("read timed out"), LiveOutcome.TIMEOUT),
        (ConnectionRefusedError("no route to host"), LiveOutcome.TRANSPORT_ERROR),
        (TransportResponse(429, "", {"Retry-After": "30"}), LiveOutcome.RATE_LIMIT_DEFERRED),
        (TransportResponse(200, "not xml at all <"), LiveOutcome.MALFORMED_RESPONSE),
    ],
)
def test_each_transport_failure_gets_its_own_outcome(
    tmp_path: Path, response, expected: LiveOutcome
) -> None:
    """A failure to look is never a look that found nothing."""

    run = run_route(
        _arxiv_route(_scripted(response)),
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert run.attempts[0].outcome is expected
    assert expected.leaves_open_obligation
    assert not expected.observed_the_index


def test_no_outcome_whatsoever_is_evidence_of_absence() -> None:
    """The invariant the whole open-world half depends on."""

    assert not any(item.is_evidence_of_absence for item in LiveOutcome)


def test_an_empty_result_set_is_a_successful_look_not_an_absence(
    tmp_path: Path,
) -> None:
    """EMPTY says this query matched nothing on this index at this moment."""

    run = run_route(
        _arxiv_route(_scripted(_ok(_atom())), budget=5.0, variants=("a", "b", "c", "d")),
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
        alternative_route_kinds=(SearchRouteKind.PARENT_DISCIPLINE,),
    )
    assert run.attempts[0].outcome is LiveOutcome.EMPTY
    assert run.attempts[0].outcome.observed_the_index
    assert not run.attempts[0].outcome.leaves_open_obligation
    assert not run.attempts[0].outcome.is_evidence_of_absence
    # Empty looks are successful looks, so they drive the zero-novelty streak
    # to a route switch rather than leaving an obligation behind.
    assert run.decision.action is RouteControlAction.SWITCH
    assert run.open_obligations == ()


def test_a_rate_limit_retains_the_providers_own_retry_after(tmp_path: Path) -> None:
    run = run_route(
        _arxiv_route(_scripted(TransportResponse(429, "", {"Retry-After": "22503"}))),
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert run.attempts[0].retry_after_seconds == pytest.approx(22503.0)
    assert run.attempts[0].outcome is LiveOutcome.RATE_LIMIT_DEFERRED


def test_a_missing_credential_is_recorded_not_treated_as_an_empty_index(
    tmp_path: Path,
) -> None:
    """OpenAlex has required a funded key since Feb 2026; unfunded is not empty."""

    route = LiveRoute(
        route_id="openalex-keyword",
        route_kind=SearchRouteKind.PARENT_DISCIPLINE,
        backend="openalex",
        query_derivation="discipline-keyword-mapping",
        provider="openalex",
        searcher=openalex_keyword_searcher(
            OpenAlexClient(
                transport=_scripted(_ok(_works())),
                api_key="",
                gate=RateGate(clock=Clock()),
            )
        ),
        plan_query=keyword_planner("discipline-keyword-mapping", ("x",)),
        budget_units=2.0,
    )
    run = run_route(
        route,
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert run.attempts[0].outcome is LiveOutcome.CREDENTIAL_REQUIRED
    assert run.open_obligations == ("CREDENTIAL_REQUIRED",)


def test_a_failed_route_suspends_with_an_open_obligation_rather_than_stopping(
    tmp_path: Path,
) -> None:
    run = run_route(
        _arxiv_route(_scripted(TransportResponse(503, ""))),
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert run.decision.action is RouteControlAction.SUSPEND
    assert run.decision.action is not RouteControlAction.STOP
    assert run.open_obligations == ("PROVIDER_ERROR",)


def test_a_mid_campaign_outage_keeps_what_was_already_found(tmp_path: Path) -> None:
    """The outage suspends the route; it does not retract earlier evidence."""

    transport = _scripted(
        _ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", DOI))),
        TransportResponse(503, ""),
    )
    clock = Clock()
    gate = RateGate(clock=clock)
    run = run_route(
        _arxiv_route(transport, variants=("first", "second", "third")),
        QUESTION,
        store=_store(tmp_path),
        gate=gate,
        policy=POLICY,
        clock=clock,
    )
    outcomes = [item.outcome for item in run.attempts]
    assert LiveOutcome.RESULTS in outcomes
    assert LiveOutcome.PROVIDER_ERROR in outcomes
    assert len(run.capture.captured) == 1  # earlier evidence survives
    assert run.decision.action is RouteControlAction.SUSPEND


def test_transport_note_classification_separates_timeout_from_unreachable() -> None:
    assert classify_transport_note("TimeoutError: read timed out") is LiveOutcome.TIMEOUT
    assert (
        classify_transport_note("ConnectionRefusedError: nope")
        is LiveOutcome.TRANSPORT_ERROR
    )


# --- one work, two identifiers, two routes ---------------------------------


def test_one_work_reached_by_doi_and_by_arxiv_id_counts_once(tmp_path: Path) -> None:
    """The overlap key must be the resolved work, not the retrieved text.

    The two backends deliberately serve *different* abstract text for the same
    paper, which is what really happens: arXiv returns the author abstract and
    OpenAlex returns one rebuilt from an inverted index. If overlap were keyed
    on the retrieved rendition these would look like two distinct works, every
    route would appear to contribute uniquely, and route overlap would collapse
    to zero on a run where both routes found the very same paper.
    """

    arxiv = _scripted(
        _ok(_atom(("http://arxiv.org/abs/1606.01772v2", "Gamma5 ambiguities", "AUTHOR ABSTRACT TEXT", DOI)))
    )
    openalex = _scripted(
        _ok(_works(("https://openalex.org/W123", "Gamma5 ambiguities", "entirely different reconstructed wording", f"https://doi.org/{DOI}")))
    )
    result = run_campaign(
        "c1",
        QUESTION,
        [_arxiv_route(arxiv), _openalex_route(openalex)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    left, right = result.runs[0].capture, result.runs[1].capture
    assert len(left.captured & right.captured) == 1
    assert len(result.union_digests) == 1


def test_distinct_works_are_not_collapsed(tmp_path: Path) -> None:
    """The no-alarm case: dedup must not merge genuinely different papers."""

    arxiv = _scripted(
        _ok(_atom(("http://arxiv.org/abs/1606.01772v2", "One", "S", DOI)))
    )
    openalex = _scripted(
        _ok(_works(("https://openalex.org/W999", "Another", "different paper", "https://doi.org/10.1234/other")))
    )
    result = run_campaign(
        "c1",
        QUESTION,
        [_arxiv_route(arxiv), _openalex_route(openalex)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert len(result.union_digests) == 2
    left, right = result.runs[0].capture, result.runs[1].capture
    assert not (left.captured & right.captured)


# --- independence is earned, never labelled --------------------------------


def test_two_routes_on_one_backend_are_refused_independence(tmp_path: Path) -> None:
    """Different queries do not make one index into two capture occasions."""

    keyword = _scripted(_ok(_works(("https://openalex.org/W1", "A", "a", ""))))
    citation = _scripted(_ok(_works(("https://openalex.org/W2", "B", "b", ""))))
    result = run_campaign(
        "c1",
        QUESTION,
        [_openalex_route(keyword), _citation_route(citation)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    from orion.knowledge.routes import assess_pair

    verdict = assess_pair(result.runs[0].capture, result.runs[1].capture)
    assert verdict.verdict is IndependenceVerdict.SHARED_BACKEND
    assert not verdict.independent


def test_arxiv_and_openalex_earn_independence(tmp_path: Path) -> None:
    """The no-alarm case: genuinely different backends must not be refused."""

    arxiv = _scripted(_ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", DOI))))
    openalex = _scripted(
        _ok(_works(("https://openalex.org/W123", "T", "s", f"https://doi.org/{DOI}")))
    )
    result = run_campaign(
        "c1",
        QUESTION,
        [_arxiv_route(arxiv), _openalex_route(openalex)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    from orion.knowledge.routes import assess_pair

    assert assess_pair(result.runs[0].capture, result.runs[1].capture).independent


def test_every_pair_in_the_three_route_ensemble_gets_the_expected_verdict(
    tmp_path: Path,
) -> None:
    """Both arXiv pairs earn independence; the two OpenAlex routes do not.

    This is the whole independence structure the campaign rests on, asserted in
    one place: the campaign's only independent pairs both involve arXiv, so its
    capacity to produce any coverage diagnostic depends on that one backend.
    """

    arxiv = _scripted(_ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", DOI))))
    keyword = _scripted(_ok(_works(("https://openalex.org/W1", "A", "a", ""))))
    citation = _scripted(_ok(_works(("https://openalex.org/W2", "B", "b", ""))))
    result = run_campaign(
        "c1",
        QUESTION,
        [_arxiv_route(arxiv), _openalex_route(keyword), _citation_route(citation)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    from orion.knowledge.routes import assess_pair

    by_id = {run.route.route_id: run.capture for run in result.runs}
    assert assess_pair(by_id["arxiv-topic"], by_id["openalex-keyword"]).independent
    assert assess_pair(by_id["arxiv-topic"], by_id["openalex-citation"]).independent
    shared = assess_pair(by_id["openalex-keyword"], by_id["openalex-citation"])
    assert shared.verdict is IndependenceVerdict.SHARED_BACKEND
    assert not shared.independent


def test_the_estimator_refuses_when_no_pair_is_independent(tmp_path: Path) -> None:
    keyword = _scripted(_ok(_works(("https://openalex.org/W1", "A", "a", ""))))
    citation = _scripted(_ok(_works(("https://openalex.org/W1", "A", "a", ""))))
    result = run_campaign(
        "c1",
        QUESTION,
        [_openalex_route(keyword), _citation_route(citation)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    estimate = estimate_coverage(result.captures)
    assert estimate.population_estimate is None
    assert "no independent pair" in estimate.refusal_reason


def test_the_estimator_refuses_when_independent_routes_share_nothing(
    tmp_path: Path,
) -> None:
    arxiv = _scripted(_ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", ""))))
    openalex = _scripted(_ok(_works(("https://openalex.org/W123", "Other", "o", ""))))
    result = run_campaign(
        "c1",
        QUESTION,
        [_arxiv_route(arxiv), _openalex_route(openalex)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    estimate = estimate_coverage(result.captures)
    assert estimate.population_estimate is None
    assert "unbounded above" in estimate.refusal_reason


# --- budgets and gates are outcomes, never silent drops ---------------------


def test_route_budget_exhaustion_stops_the_route_and_is_reported(
    tmp_path: Path,
) -> None:
    transport = _scripted(_ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", ""))))
    clock = Clock()
    run = run_route(
        _arxiv_route(transport, budget=1.0, variants=("a", "b", "c")),
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=clock),
        policy=POLICY,
        clock=clock,
    )
    assert run.decision.action is RouteControlAction.STOP
    assert "route_budget_exhausted" in run.decision.reasons
    assert run.decision.remaining_budget_units == 0.0


def test_a_monetary_budget_is_separate_from_request_spacing(tmp_path: Path) -> None:
    """OpenAlex meters dollars per call; the RateGate only meters intervals."""

    transport = _scripted(_ok(_works(("https://openalex.org/W1", "A", "a", ""), cost=0.06)))
    route = _openalex_route(transport, budget=4.0, variants=("a", "b", "c"))
    clock = Clock()
    run = run_route(
        route,
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=clock),
        policy=POLICY,
        clock=clock,
    )
    outcomes = [item.outcome for item in run.attempts]
    assert LiveOutcome.COST_BUDGET_EXHAUSTED in outcomes
    assert run.spent_usd == pytest.approx(0.06)


def test_rate_gate_deferral_is_retained_as_an_outcome(tmp_path: Path) -> None:
    """arXiv allows one request per three seconds; a frozen clock must defer."""

    transport = _scripted(_ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", ""))))

    class Frozen:
        def __call__(self) -> float:
            return 500.0

    gate = RateGate(clock=Frozen())
    run = run_route(
        _arxiv_route(transport, variants=("a", "b", "c"), gate=gate),
        QUESTION,
        store=_store(tmp_path),
        gate=gate,
        policy=POLICY,
        clock=Frozen(),
    )
    outcomes = [item.outcome for item in run.attempts]
    assert LiveOutcome.RESULTS in outcomes
    assert LiveOutcome.RATE_GATE_DEFERRED in outcomes
    deferred = next(item for item in run.attempts if item.outcome is LiveOutcome.RATE_GATE_DEFERRED)
    assert deferred.retry_after_seconds == pytest.approx(3.0)


def test_a_route_with_no_derivable_query_is_suspended_not_silently_skipped(
    tmp_path: Path,
) -> None:
    """Citation chaining with no confirmed seed owes a look it never took."""

    citation = _citation_route(_scripted(_ok(_works())))
    run = run_route(
        citation,
        QUESTION,
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert run.attempts[0].outcome is LiveOutcome.NO_DERIVABLE_QUERY
    assert run.decision.action is RouteControlAction.SUSPEND
    assert run.open_obligations == ("NO_DERIVABLE_QUERY",)


def test_citation_chaining_derives_queries_from_confirmed_seeds(
    tmp_path: Path,
) -> None:
    """Its query derivation is a function of retrieved works, not of the question."""

    openalex = _scripted(_ok(_works(("https://openalex.org/W123", "Seed", "s", ""))))
    citation = _scripted(_ok(_works(("https://openalex.org/W456", "Citing", "c", ""))))
    result = run_campaign(
        "c1",
        QUESTION,
        [_openalex_route(openalex), _citation_route(citation)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    chained = result.runs[1].attempts[0]
    assert chained.outcome is LiveOutcome.RESULTS
    assert chained.query.text == "cites:W123"
    assert chained.query.seed_work_keys == ("openalex:W123",)


# --- question-conditioned read state ---------------------------------------


def test_a_reread_forced_by_a_new_question_is_not_duplicate_processing(
    tmp_path: Path,
) -> None:
    """Same paper, same text, different frame: a legitimate reread."""

    store = _store(tmp_path)
    body = _atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", DOI))
    first = run_route(
        _arxiv_route(_scripted(_ok(body))),
        QUESTION,
        store=store,
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert first.attempts[0].read_decisions[0][1] == "UNSEEN"

    other_frame = ResearchQuestion(
        question_id="q2",
        text="route independence",
        frame_id="frame:stopping-rules",
        extraction_schema_version="claim-extraction-v0",
    )
    second = run_route(
        _arxiv_route(_scripted(_ok(body))),
        other_frame,
        store=store,
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert second.attempts[0].read_decisions[0][1] == "NEW_FRAME"


def test_the_same_rendition_under_the_same_question_is_already_read(
    tmp_path: Path,
) -> None:
    """The no-alarm case: an unchanged reread must be recognised as duplicate."""

    store = _store(tmp_path)
    body = _atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", DOI))
    run_route(
        _arxiv_route(_scripted(_ok(body))),
        QUESTION,
        store=store,
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    again = run_route(
        _arxiv_route(_scripted(_ok(body))),
        QUESTION,
        store=store,
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert again.attempts[0].read_decisions[0][1] == "ALREADY_READ"


# --- fail-closed stopping ---------------------------------------------------


def test_no_route_decision_ever_certifies_task_saturation(tmp_path: Path) -> None:
    arxiv = _scripted(_ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", DOI))))
    openalex = _scripted(_ok(_works(("https://openalex.org/W1", "A", "a", ""))))
    result = run_campaign(
        "c1",
        QUESTION,
        [_arxiv_route(arxiv), _openalex_route(openalex)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    assert not any(run.decision.certifies_task_saturation for run in result.runs)
    assert not assess_task_closure(result).certified_by_route_decision


def test_task_closure_is_refused_while_any_route_owes_a_look(tmp_path: Path) -> None:
    arxiv = _scripted(TransportResponse(503, ""))
    openalex = _scripted(_ok(_works(("https://openalex.org/W1", "A", "a", ""))))
    result = run_campaign(
        "c1",
        QUESTION,
        [_arxiv_route(arxiv), _openalex_route(openalex)],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    closure = assess_task_closure(result)
    assert not closure.certified
    assert "arxiv-topic:PROVIDER_ERROR" in closure.open_obligations


def test_a_clean_run_closes_without_raising_a_false_obligation(
    tmp_path: Path,
) -> None:
    """The no-alarm case: a campaign where nothing went wrong must certify."""

    arxiv = _scripted(_ok(_atom(("http://arxiv.org/abs/1606.01772v2", "T", "S", DOI))))
    openalex = _scripted(_ok(_works(("https://openalex.org/W1", "A", "a", ""))))
    result = run_campaign(
        "c1",
        QUESTION,
        [
            _arxiv_route(arxiv, budget=1.0),
            _openalex_route(openalex, budget=1.0),
        ],
        store=_store(tmp_path),
        gate=RateGate(clock=Clock()),
        policy=POLICY,
        clock=Clock(),
    )
    closure = assess_task_closure(result)
    assert closure.open_obligations == ()
    assert closure.certified


# --- route definitions must declare what makes them their own occasion -----


def test_a_route_without_a_declared_backend_is_rejected() -> None:
    with pytest.raises(ValueError):
        LiveRoute(
            route_id="r",
            route_kind=SearchRouteKind.FRESHNESS,
            backend="  ",
            query_derivation="d",
            provider="arxiv",
            searcher=lambda query: None,  # type: ignore[arg-type,return-value]
            plan_query=lambda question, seeds, index: None,
            budget_units=1.0,
        )


def test_an_ungated_provider_client_is_refused() -> None:
    """An ungated client never records requests, so spacing is never enforced."""

    with pytest.raises(ValueError, match="RateGate"):
        arxiv_searcher(ArxivClient(transport=_scripted(_ok(_atom()))))


def test_a_gated_provider_client_is_accepted() -> None:
    """The no-alarm case: a correctly wired client must not be refused."""

    assert arxiv_searcher(
        ArxivClient(transport=_scripted(_ok(_atom())), gate=RateGate(clock=Clock()))
    )


def test_a_question_without_a_frame_is_rejected() -> None:
    """Read state is question-conditioned; an unframed question cannot key it."""

    with pytest.raises(ValueError):
        ResearchQuestion("q", "text", "  ", "schema-v0")
