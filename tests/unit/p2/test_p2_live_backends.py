"""Backend registry and per-backend transport adapters.

Every fixture here is derived from a real captured response, not from provider
documentation. That distinction earned its keep immediately: DBLP omits the
``hit`` key entirely when nothing matches, so a parser written from the
documented shape raises on its zero-result path and files a successful empty
look as a malformed response.

No network.
"""

from __future__ import annotations

import json

import pytest

from orion.core.search import SearchRouteKind
from orion.knowledge.providers.arxiv import TransportResponse
from orion.knowledge.rate import RateGate
from orion.study.p2.live_backends import (
    BACKENDS,
    STUDY_PROVIDER_BUDGETS,
    BackendSpec,
    ShapeVerification,
    build_route,
    crossref_searcher,
    dblp_searcher,
    default_backend_names,
    openaire_searcher,
    select_backends,
    semanticscholar_searcher,
    study_gate,
    verified_backends,
)
from orion.study.p2.live_campaign import LiveOutcome, LiveQuery

QUERY = LiveQuery("q1", "route independence", "test-derivation")


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        self.now += 0.001
        return self.now


def _gate() -> RateGate:
    return study_gate(Clock())


def _transport(status: int, body: str, headers: dict | None = None):
    def send(url: str) -> TransportResponse:
        return TransportResponse(status, body, headers)

    return send


# --- fixtures derived from real captured responses (2026-08-16) ------------

# OpenAIRE: dnet JSON-from-XML. Values wrapped in {"$": v}; `title` arrives as a
# list, `description` as a bare object — the polymorphism is the point.
OPENAIRE_REAL = json.dumps(
    {
        "response": {
            "header": {"total": {"$": 445}},
            "results": {
                "result": [
                    {
                        "metadata": {
                            "oaf:entity": {
                                "oaf:result": {
                                    "title": [
                                        {"@classid": "main title", "$": "Compact Routing with Name Independence"},
                                        {"@classid": "main title", "$": "Compact routing with name independence"},
                                    ],
                                    "pid": [
                                        {"@classid": "doi", "$": "10.1137/04062053"},
                                        {"@classid": "doi", "$": "10.1145/777412.777442"},
                                    ],
                                    "description": {"$": "This paper is concerned with compact routing schemes."},
                                }
                            }
                        }
                    }
                ]
            },
        }
    }
)

# The singular case the plural fixture cannot exercise: one title, one pid, each
# a bare object rather than a one-element list.
OPENAIRE_SINGULAR = json.dumps(
    {
        "response": {
            "header": {"total": {"$": 1}},
            "results": {
                "result": {
                    "metadata": {
                        "oaf:entity": {
                            "oaf:result": {
                                "title": {"@classid": "main title", "$": "Only One Title"},
                                "pid": {"@classid": "arXiv", "$": "1606.01772"},
                                "description": {"$": "Single abstract."},
                            }
                        }
                    }
                }
            },
        }
    }
)

# DBLP: verbatim structure of a real zero-hit response. Note `hits` carries no
# `hit` key at all.
DBLP_ZERO = json.dumps(
    {
        "result": {
            "query": "route* independence*",
            "status": {"@code": "200", "text": "OK"},
            "hits": {"@total": "0", "@computed": "0", "@sent": "0", "@first": "0"},
        }
    }
)

DBLP_REAL = json.dumps(
    {
        "result": {
            "hits": {
                "@total": "17336",
                "hit": [
                    {
                        "info": {
                            "title": "BotMHG: a hybrid deep learning-based graphical approach.",
                            "venue": "Neural Comput. Appl.",
                            "year": "2025",
                            "doi": "10.1007/S00521-025-11402-3",
                            "ee": "https://doi.org/10.1007/s00521-025-11402-3",
                            "key": "journals/nca/GururajK25",
                            "authors": {
                                "author": [
                                    {"@pid": "384/9998", "text": "Mohan Honnagudi Gururaj"},
                                    {"@pid": "168/6922", "text": "Jalesh Kumar"},
                                ]
                            },
                        }
                    }
                ],
            }
        }
    }
)

# One hit, one author: DBLP collapses both to bare objects.
DBLP_SINGULAR = json.dumps(
    {
        "result": {
            "hits": {
                "@total": "1",
                "hit": {
                    "info": {
                        "title": "A Single Result.",
                        "venue": "Venue",
                        "year": "2024",
                        "doi": "10.1000/SOLO",
                        "key": "journals/x/Solo24",
                        "authors": {"author": {"@pid": "1/1", "text": "Solo Author"}},
                    }
                },
            }
        }
    }
)

CROSSREF_REAL = json.dumps(
    {
        "status": "ok",
        "message": {
            "total-results": 182752,
            "items": [
                {
                    "DOI": "10.31234/osf.io/qh39s",
                    "title": ["Finding a route to independence"],
                    "abstract": "<jats:p>Navigation is the ability to find our way.</jats:p>",
                    "type": "posted-content",
                }
            ],
        },
    }
)

# Real Semantic Scholar 429 body: no Retry-After header accompanied it.
S2_RATE_LIMITED = json.dumps(
    {"message": "Too Many Requests. Please wait and try again or apply for a key.", "code": "429"}
)


# --- registry ---------------------------------------------------------------


def test_openalex_is_retained_but_disabled_and_credentialed() -> None:
    """A route unavailable for economic reasons is an obligation, not a deletion."""

    spec = BACKENDS["openalex"]
    assert spec.requires_credential
    assert not spec.enabled_by_default
    assert "429" in spec.population_note
    assert "openalex" not in default_backend_names()


def test_the_default_backend_set_is_the_reachable_ones() -> None:
    assert default_backend_names() == (
        "arxiv",
        "crossref",
        "dblp",
        "openaire",
        "semanticscholar",
    )


def test_shape_verification_is_recorded_per_backend_not_assumed() -> None:
    """Semantic Scholar 429'd on every probe, so its success path is unverified."""

    assert BACKENDS["semanticscholar"].success_shape is ShapeVerification.SHAPE_UNVERIFIED
    assert BACKENDS["openalex"].success_shape is ShapeVerification.SHAPE_UNVERIFIED
    assert verified_backends() == ("arxiv", "crossref", "dblp", "openaire")


def test_every_backend_states_which_population_it_indexes() -> None:
    for name, spec in BACKENDS.items():
        assert spec.population_note.strip(), f"{name} does not say what it indexes"


def test_crossref_population_caveat_is_recorded() -> None:
    """arXiv preprint DOIs are DataCite-registered, so Crossref misses them."""

    note = BACKENDS["crossref"].population_note
    assert "DataCite" in note and "NOT Crossref" in note


def test_a_backend_without_a_population_note_is_refused() -> None:
    with pytest.raises(ValueError, match="population"):
        BackendSpec(
            name="x",
            endpoint="https://x",
            provider="arxiv",
            route_kind=SearchRouteKind.FRESHNESS,
            query_derivation="d",
            requires_credential=False,
            enabled_by_default=True,
            success_shape=ShapeVerification.VERIFIED,
            verified_on="2026-08-16",
            population_note="   ",
        )


def test_every_backend_has_a_usable_rate_budget() -> None:
    """A provider key absent from the budget map raises UnknownProvider live."""

    gate = _gate()
    for name, spec in BACKENDS.items():
        budget = gate.budget_for(spec.provider)
        assert budget.min_interval_seconds >= 0, name
        assert budget.citation.strip(), f"{name} budget cites no basis"


def test_added_budgets_are_labelled_assumed_not_observed() -> None:
    """Two successful requests establish reachability, never a rate limit."""

    for name in ("openaire", "dblp"):
        budget = STUDY_PROVIDER_BUDGETS[name]
        assert budget.basis.value == "ASSUMED"
        assert "assumed" in budget.citation.lower()


def test_route_kinds_and_derivations_are_pairwise_distinct() -> None:
    """Independence needs all three coordinates to differ across backends."""

    kinds = [spec.route_kind for spec in BACKENDS.values()]
    derivations = [spec.query_derivation for spec in BACKENDS.values()]
    assert len(set(kinds)) == len(kinds)
    assert len(set(derivations)) == len(derivations)


def test_backend_selection_is_configurable() -> None:
    chosen = select_backends(["arxiv", "dblp"])
    assert [item.name for item in chosen] == ["arxiv", "dblp"]
    assert "openalex" in {item.name for item in select_backends(include_disabled=True)}
    with pytest.raises(ValueError, match="unknown backends"):
        select_backends(["not-a-backend"])


# --- OpenAIRE ---------------------------------------------------------------


def test_openaire_parses_a_real_response() -> None:
    fetch = openaire_searcher(_transport(200, OPENAIRE_REAL), _gate())(QUERY)
    assert fetch.outcome is LiveOutcome.RESULTS
    assert fetch.reported_total == 445
    record = fetch.records[0]
    assert record.raw_identifier == "10.1137/04062053"
    assert record.aliases == ("10.1145/777412.777442",)
    assert record.title == "Compact Routing with Name Independence"
    assert record.text.startswith("This paper is concerned")


def test_openaire_handles_the_singular_case_the_plural_fixture_cannot() -> None:
    """One title and one pid arrive as bare objects, not one-element lists."""

    fetch = openaire_searcher(_transport(200, OPENAIRE_SINGULAR), _gate())(QUERY)
    assert fetch.outcome is LiveOutcome.RESULTS
    assert fetch.records[0].title == "Only One Title"
    assert fetch.records[0].raw_identifier == "arXiv:1606.01772"


# --- DBLP -------------------------------------------------------------------


def test_dblp_zero_hits_is_an_empty_look_not_a_malformed_response() -> None:
    """The real trap: DBLP omits `hit` entirely when nothing matched."""

    fetch = dblp_searcher(_transport(200, DBLP_ZERO), _gate())(QUERY)
    assert fetch.outcome is LiveOutcome.RESULTS
    assert fetch.outcome is not LiveOutcome.MALFORMED_RESPONSE
    assert fetch.records == ()
    assert fetch.reported_total == 0


def test_dblp_parses_a_real_response() -> None:
    fetch = dblp_searcher(_transport(200, DBLP_REAL), _gate())(QUERY)
    record = fetch.records[0]
    assert fetch.reported_total == 17336
    assert record.raw_identifier == "10.1007/S00521-025-11402-3"
    assert "https://doi.org/10.1007/s00521-025-11402-3" in record.aliases
    assert record.text == "Neural Comput. Appl. 2025"


def test_dblp_handles_a_single_hit_and_a_single_author() -> None:
    """Both collapse from list to object; parsing only the plural case breaks here."""

    fetch = dblp_searcher(_transport(200, DBLP_SINGULAR), _gate())(QUERY)
    assert fetch.outcome is LiveOutcome.RESULTS
    assert len(fetch.records) == 1
    assert fetch.records[0].raw_identifier == "10.1000/SOLO"


# --- Crossref ---------------------------------------------------------------


def test_crossref_parses_a_real_response_and_strips_jats() -> None:
    fetch = crossref_searcher(_transport(200, CROSSREF_REAL), _gate())(QUERY)
    record = fetch.records[0]
    assert fetch.reported_total == 182752
    assert record.raw_identifier == "10.31234/osf.io/qh39s"
    assert record.title == "Finding a route to independence"
    assert "<jats:p>" not in record.text
    assert record.text.startswith("Navigation is the ability")


def test_crossref_sends_no_mailto_unless_one_is_supplied() -> None:
    """No address is invented here."""

    seen: list[str] = []

    def send(url: str) -> TransportResponse:
        seen.append(url)
        return TransportResponse(200, CROSSREF_REAL)

    crossref_searcher(send, _gate())(QUERY)
    assert "mailto" not in seen[0]
    seen.clear()
    crossref_searcher(send, _gate(), mailto="someone@example.org")(QUERY)
    assert "mailto=someone%40example.org" in seen[0]


# --- Semantic Scholar -------------------------------------------------------


def test_semantic_scholar_429_is_a_deferral_not_a_provider_fault() -> None:
    """Shared-pool saturation with no Retry-After hint is still a rate limit."""

    fetch = semanticscholar_searcher(_transport(429, S2_RATE_LIMITED), _gate())(QUERY)
    assert fetch.outcome is LiveOutcome.RATE_LIMIT_DEFERRED
    assert fetch.outcome is not LiveOutcome.PROVIDER_ERROR
    assert fetch.retry_after_seconds is None
    assert fetch.outcome.leaves_open_obligation
    assert not fetch.outcome.is_evidence_of_absence


def test_semantic_scholar_uses_a_retry_after_header_when_one_is_present() -> None:
    fetch = semanticscholar_searcher(
        _transport(429, S2_RATE_LIMITED, {"Retry-After": "60"}), _gate()
    )(QUERY)
    assert fetch.retry_after_seconds == pytest.approx(60.0)


# --- status and transport mapping, shared across adapters -------------------


@pytest.mark.parametrize("factory", [openaire_searcher, dblp_searcher, crossref_searcher])
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, LiveOutcome.CREDENTIAL_REQUIRED),
        (403, LiveOutcome.CREDENTIAL_REQUIRED),
        (429, LiveOutcome.RATE_LIMIT_DEFERRED),
        (500, LiveOutcome.PROVIDER_ERROR),
        (503, LiveOutcome.PROVIDER_ERROR),
        (400, LiveOutcome.TRANSPORT_ERROR),
    ],
)
def test_http_status_maps_to_its_own_outcome(factory, status: int, expected) -> None:
    fetch = factory(_transport(status, "{}"), _gate())(QUERY)
    assert fetch.outcome is expected
    assert fetch.outcome.leaves_open_obligation


@pytest.mark.parametrize("factory", [openaire_searcher, dblp_searcher, crossref_searcher])
def test_unparseable_json_is_malformed_not_empty(factory) -> None:
    fetch = factory(_transport(200, "not json at all"), _gate())(QUERY)
    assert fetch.outcome is LiveOutcome.MALFORMED_RESPONSE
    assert fetch.records == ()


@pytest.mark.parametrize("factory", [openaire_searcher, dblp_searcher, crossref_searcher])
def test_a_timeout_is_distinguished_from_an_unreachable_host(factory) -> None:
    def timeout(url: str):
        raise TimeoutError("read timed out")

    def refused(url: str):
        raise ConnectionRefusedError("no route to host")

    assert factory(timeout, _gate())(QUERY).outcome is LiveOutcome.TIMEOUT
    assert factory(refused, _gate())(QUERY).outcome is LiveOutcome.TRANSPORT_ERROR


# --- rate gate --------------------------------------------------------------


def test_adapters_record_their_requests_so_spacing_is_enforced() -> None:
    """An adapter that never records leaves the gate at zero and bursts the API."""

    class Frozen:
        def __call__(self) -> float:
            return 500.0

    gate = study_gate(Frozen())
    assert gate.wait_seconds("dblp") == 0.0
    dblp_searcher(_transport(200, DBLP_ZERO), gate)(QUERY)
    assert gate.wait_seconds("dblp") == pytest.approx(1.0)


# --- route construction -----------------------------------------------------


def test_build_route_binds_the_registry_identity_to_the_route() -> None:
    route = build_route(
        "dblp",
        transport=_transport(200, DBLP_REAL),
        gate=_gate(),
        variants=("a", "b"),
    )
    assert route.backend == "dblp"
    assert route.route_kind is BACKENDS["dblp"].route_kind
    assert route.query_derivation == BACKENDS["dblp"].query_derivation
    assert route.provider == "dblp"
    assert route.budget_units == 2.0


def test_building_an_unknown_backend_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown backend"):
        build_route("nope", transport=_transport(200, "{}"), gate=_gate(), variants=("a",))


def test_a_backend_without_a_builtin_adapter_requires_an_injected_searcher() -> None:
    """arXiv and OpenAlex keep their own provider clients and typed errors."""

    with pytest.raises(ValueError, match="no built-in adapter"):
        build_route("arxiv", transport=_transport(200, ""), gate=_gate(), variants=("a",))
    route = build_route(
        "arxiv",
        transport=_transport(200, ""),
        gate=_gate(),
        variants=("a",),
        searcher=lambda query: None,  # type: ignore[arg-type,return-value]
    )
    assert route.backend == "arxiv"
