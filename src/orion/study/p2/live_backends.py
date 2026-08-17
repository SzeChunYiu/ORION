"""Backend registry and transport adapters for the live campaign.

The OpenAlex 429 (see ``LIVE_ENDPOINT_CHECK_2026-08-16.md``) made a single-backend
plan untenable, so the route set is now selectable across several independent
literature backends. Each one gets its own adapter, because each one fails in its
own way and the differences are exactly what must not be flattened: a DBLP query
with no matches, a Semantic Scholar 429 and an OpenAlex credential wall are three
different facts, and only the first is a statement about the literature.

Every parser here was written against real captured responses rather than
documentation. That mattered: DBLP omits the ``hit`` key entirely when nothing
matches, so a parser built from the documented shape would raise on its zero-result
path and record a successful empty look as a malformed response.

OpenAlex is retained as a credentialed, disabled-by-default route. A route that is
unavailable for economic reasons is a first-class open obligation in this paper, not
a deletion.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlencode

from orion.core.search import SearchRouteKind
from orion.knowledge.providers.arxiv import TransportResponse
from orion.knowledge.rate import PROVIDER_BUDGETS, BudgetBasis, ProviderBudget, RateGate

from .live_campaign import (
    LiveOutcome,
    LiveQuery,
    LiveRecord,
    LiveRoute,
    RouteFetch,
    Searcher,
    classify_transport_note,
    keyword_planner,
)

Transport = Callable[[str], TransportResponse]

# Crossref abstracts arrive as a JATS fragment, not a document, so a real XML
# parser has nothing well-formed to attach to. A tag strip is the honest minimal
# treatment: it keeps the prose that the rendition digest should cover and drops
# markup that would otherwise make two identical abstracts hash differently.
_TAG = re.compile(r"<[^>]+>")


class ShapeVerification(str, Enum):
    """Whether this adapter's success path was written against real bytes."""

    VERIFIED = "VERIFIED"
    SHAPE_UNVERIFIED = "SHAPE_UNVERIFIED"


@dataclass(frozen=True)
class BackendSpec:
    """One literature backend and what is actually known about it."""

    name: str
    endpoint: str
    provider: str
    route_kind: SearchRouteKind
    query_derivation: str
    requires_credential: bool
    enabled_by_default: bool
    success_shape: ShapeVerification
    verified_on: str
    population_note: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.endpoint.strip():
            raise ValueError("a backend needs a name and an endpoint")
        if not self.population_note.strip():
            raise ValueError(
                "a backend must state which population it indexes; independence "
                "arguments rest on that, not on the backend's name"
            )


# Rate budgets for backends the shared registry does not cover. Composed onto
# PROVIDER_BUDGETS rather than edited into it: rate.py carries verified numbers
# for the providers ORION already characterized, and an unverified guess must not
# be laundered into that table. Both are ASSUMED and say so.
STUDY_PROVIDER_BUDGETS: dict[str, ProviderBudget] = {
    **PROVIDER_BUDGETS,
    "openaire": ProviderBudget(
        provider="openaire",
        min_interval_seconds=1.0,
        max_concurrent=1,
        basis=BudgetBasis.ASSUMED,
        citation=(
            "No published per-second figure located for the OpenAIRE search API. "
            "1 req/s assumed as a conservative default; two keyless requests "
            "succeeded on 2026-08-16, which establishes reachability, not a limit"
        ),
    ),
    "dblp": ProviderBudget(
        provider="dblp",
        min_interval_seconds=1.0,
        max_concurrent=1,
        basis=BudgetBasis.ASSUMED,
        citation=(
            "No published per-second figure located for the DBLP search API. "
            "1 req/s assumed as a conservative default; DBLP asks for moderate "
            "automated use without naming a rate"
        ),
    ),
}


BACKENDS: dict[str, BackendSpec] = {
    "arxiv": BackendSpec(
        name="arxiv",
        endpoint="https://export.arxiv.org/api/query",
        provider="arxiv",
        route_kind=SearchRouteKind.CURRENT_VOCABULARY,
        query_derivation="frozen-question-terms",
        requires_credential=False,
        enabled_by_default=True,
        success_shape=ShapeVerification.VERIFIED,
        verified_on="2026-08-16",
        population_note="preprints; arXiv ids native, DOIs sometimes present",
    ),
    "openaire": BackendSpec(
        name="openaire",
        endpoint="https://api.openaire.eu/search/publications",
        provider="openaire",
        route_kind=SearchRouteKind.LITERATURE_BRIDGE,
        query_derivation="title-field-terms",
        requires_credential=False,
        enabled_by_default=True,
        success_shape=ShapeVerification.VERIFIED,
        verified_on="2026-08-16",
        population_note=(
            "cross-repository aggregator; aggregates arXiv and carries arXiv ids "
            "alongside DOIs in its pid list"
        ),
    ),
    "dblp": BackendSpec(
        name="dblp",
        endpoint="https://dblp.org/search/publ/api",
        provider="dblp",
        route_kind=SearchRouteKind.PARENT_DISCIPLINE,
        query_derivation="venue-bibliography-terms",
        requires_credential=False,
        enabled_by_default=True,
        success_shape=ShapeVerification.VERIFIED,
        verified_on="2026-08-16",
        population_note=(
            "computer-science bibliography; CS-skewed, no abstracts, entries carry "
            "'ee' links that often resolve to arXiv"
        ),
    ),
    "crossref": BackendSpec(
        name="crossref",
        endpoint="https://api.crossref.org/works",
        provider="crossref_list",
        route_kind=SearchRouteKind.CROSS_DOMAIN,
        query_derivation="registered-record-terms",
        requires_credential=False,
        enabled_by_default=True,
        success_shape=ShapeVerification.VERIFIED,
        verified_on="2026-08-16",
        population_note=(
            "publisher-registered DOIs. arXiv preprint DOIs are registered with "
            "DataCite, NOT Crossref, so this indexes a genuinely different "
            "population: strong for independence, weak for arXiv recall"
        ),
    ),
    "semanticscholar": BackendSpec(
        name="semanticscholar",
        endpoint="https://api.semanticscholar.org/graph/v1/paper/search",
        provider="semantic_scholar",
        route_kind=SearchRouteKind.CITATION_NEIGHBORHOOD,
        query_derivation="graph-paper-search-terms",
        requires_credential=False,
        enabled_by_default=True,
        success_shape=ShapeVerification.SHAPE_UNVERIFIED,
        verified_on="2026-08-16",
        population_note=(
            "cross-disciplinary graph, returns externalIds.ArXiv. Intermittently "
            "available: the unauthenticated pool is shared and returned 429 on "
            "both probes, so the SUCCESS shape here is written from documentation "
            "and has never been checked against real bytes"
        ),
    ),
    "openalex": BackendSpec(
        name="openalex",
        endpoint="https://api.openalex.org/works",
        provider="openalex",
        route_kind=SearchRouteKind.FUNCTION_ONLY,
        query_derivation="discipline-keyword-mapping",
        requires_credential=True,
        enabled_by_default=False,
        success_shape=ShapeVerification.SHAPE_UNVERIFIED,
        verified_on="2026-08-16",
        population_note=(
            "cross-disciplinary index. DISABLED BY DEFAULT: requires funded API "
            "credentials since Feb 2026, returned 429 on the first keyless request "
            "with $0 of a $0.1 daily per-IP allowance remaining. Retained rather "
            "than deleted because a route unavailable for economic reasons is an "
            "open obligation, not an absence"
        ),
    ),
}


def verified_backends() -> tuple[str, ...]:
    """Backends whose success shape was written against real captured bytes."""

    return tuple(
        sorted(
            name
            for name, spec in BACKENDS.items()
            if spec.success_shape is ShapeVerification.VERIFIED
        )
    )


def default_backend_names() -> tuple[str, ...]:
    return tuple(sorted(name for name, spec in BACKENDS.items() if spec.enabled_by_default))


def study_gate(clock: Callable[[], float]) -> RateGate:
    """A gate covering both the shared providers and this study's additions."""

    return RateGate(clock=clock, budgets=STUDY_PROVIDER_BUDGETS)


# --- shape coercion, in one place ------------------------------------------


def _as_list(node: object) -> list:
    """Coerce a field that is a dict when singular and a list when plural.

    Both OpenAIRE and DBLP serialize XML to JSON, so a one-element sequence
    arrives as a bare object. Handling only the plural case is the classic way to
    parse the two-author record correctly and crash on the one-author record.
    """

    if node is None:
        return []
    if isinstance(node, list):
        return node
    return [node]


def _dnet_text(node: object) -> str:
    """Read OpenAIRE's ``{"$": value}`` wrapper, singular or plural."""

    for item in _as_list(node):
        if isinstance(item, dict) and item.get("$") is not None:
            return str(item["$"]).strip()
        if isinstance(item, str) and item.strip():
            return item.strip()
    return ""


def _strip_markup(text: str) -> str:
    return _TAG.sub(" ", text or "").strip()


def _http(
    transport: Transport, url: str, gate: RateGate, provider: str
) -> tuple[TransportResponse | None, RouteFetch | None]:
    """Perform one request, recording it on the gate, or return a typed failure."""

    try:
        response = transport(url)
    except Exception as error:  # noqa: BLE001 - transport failures are evidence
        return None, RouteFetch(
            outcome=classify_transport_note(f"{type(error).__name__}: {error}"),
            note=f"{type(error).__name__}: {error}",
        )
    gate.record_request(provider)
    return response, None


def _retry_after(headers: Mapping[str, str] | None) -> float | None:
    for key, value in (headers or {}).items():
        if key.lower() in {"retry-after", "retryafter"}:
            try:
                return float(value)
            except ValueError:
                return None
    return None


def _status_outcome(response: TransportResponse) -> RouteFetch | None:
    """Map a non-200 HTTP status to its own typed outcome, or pass through."""

    status = response.status
    if status == 200:
        return None
    if status == 429:
        # A rate limit with no Retry-After hint is still a rate limit, and still
        # an open obligation. Falling through to PROVIDER_ERROR here would file a
        # shared-pool saturation as a backend fault.
        return RouteFetch(
            outcome=LiveOutcome.RATE_LIMIT_DEFERRED,
            retry_after_seconds=_retry_after(response.headers),
            note=f"HTTP 429: {response.body[:200]}",
        )
    if status in {401, 403}:
        return RouteFetch(
            outcome=LiveOutcome.CREDENTIAL_REQUIRED,
            note=f"HTTP {status}: {response.body[:200]}",
        )
    if status >= 500:
        return RouteFetch(
            outcome=LiveOutcome.PROVIDER_ERROR, note=f"HTTP {status}"
        )
    return RouteFetch(outcome=LiveOutcome.TRANSPORT_ERROR, note=f"HTTP {status}")


def _json_body(response: TransportResponse) -> tuple[dict | None, RouteFetch | None]:
    try:
        payload = json.loads(response.body)
    except (ValueError, TypeError) as error:
        return None, RouteFetch(
            outcome=LiveOutcome.MALFORMED_RESPONSE, note=f"{type(error).__name__}: {error}"
        )
    if not isinstance(payload, dict):
        return None, RouteFetch(
            outcome=LiveOutcome.MALFORMED_RESPONSE, note="top-level JSON is not an object"
        )
    return payload, None


# --- per-backend adapters ---------------------------------------------------


def openaire_searcher(transport: Transport, gate: RateGate, *, size: int = 25) -> Searcher:
    """OpenAIRE cross-repository aggregation.

    Fields arrive under dnet's ``{"$": value}`` wrapper and flip between object
    and list with cardinality, so every access goes through the coercion helpers.
    """

    def search(query: LiveQuery) -> RouteFetch:
        url = (
            f"{BACKENDS['openaire'].endpoint}?"
            + urlencode({"title": query.text, "size": size, "format": "json"})
        )
        response, failure = _http(transport, url, gate, "openaire")
        if failure is not None:
            return failure
        assert response is not None
        failure = _status_outcome(response)
        if failure is not None:
            return failure
        payload, failure = _json_body(response)
        if failure is not None:
            return failure
        assert payload is not None
        body = payload.get("response") or {}
        results = (body.get("results") or {}) if isinstance(body, dict) else {}
        total_node = (body.get("header") or {}).get("total") if isinstance(body, dict) else None
        total = _dnet_text(total_node)
        records: list[LiveRecord] = []
        for item in _as_list(results.get("result") if isinstance(results, dict) else None):
            entity = ((item or {}).get("metadata") or {}).get("oaf:entity") or {}
            work = entity.get("oaf:result") or {}
            if not isinstance(work, dict):
                continue
            identifiers = [
                (str(pid.get("@classid", "")).lower(), str(pid.get("$", "")).strip())
                for pid in _as_list(work.get("pid"))
                if isinstance(pid, dict)
            ]
            primary = ""
            aliases: list[str] = []
            for scheme, value in identifiers:
                if not value:
                    continue
                marked = f"arXiv:{value}" if scheme == "arxiv" else value
                if not primary:
                    primary = marked
                else:
                    aliases.append(marked)
            if not primary:
                continue
            records.append(
                LiveRecord(
                    raw_identifier=primary,
                    title=_dnet_text(work.get("title")),
                    text=_dnet_text(work.get("description")),
                    aliases=tuple(aliases),
                )
            )
        return RouteFetch(
            outcome=LiveOutcome.RESULTS,
            records=tuple(records),
            reported_total=int(total) if total.isdigit() else None,
        )

    return search


def dblp_searcher(transport: Transport, gate: RateGate, *, hits: int = 25) -> Searcher:
    """DBLP computer-science bibliography.

    DBLP omits ``hits.hit`` entirely when nothing matches — verified against a
    real zero-result response. Reading that key directly would raise and turn a
    successful empty look into a malformed-response failure, which is precisely
    the unavailable-versus-absent confusion this paper is about.
    """

    def search(query: LiveQuery) -> RouteFetch:
        url = (
            f"{BACKENDS['dblp'].endpoint}?"
            + urlencode({"q": query.text, "format": "json", "h": hits})
        )
        response, failure = _http(transport, url, gate, "dblp")
        if failure is not None:
            return failure
        assert response is not None
        failure = _status_outcome(response)
        if failure is not None:
            return failure
        payload, failure = _json_body(response)
        if failure is not None:
            return failure
        assert payload is not None
        result = payload.get("result") or {}
        hit_block = result.get("hits") or {}
        total_raw = str(hit_block.get("@total", "")).strip()
        records: list[LiveRecord] = []
        for hit in _as_list(hit_block.get("hit")):
            info = (hit or {}).get("info") or {}
            doi = str(info.get("doi", "")).strip()
            electronic = str(info.get("ee", "")).strip()
            key = str(info.get("key", "")).strip()
            primary = doi or electronic or (f"dblp:{key}" if key else "")
            if not primary:
                continue
            aliases = [item for item in (doi, electronic) if item and item != primary]
            records.append(
                LiveRecord(
                    raw_identifier=primary,
                    title=str(info.get("title", "")).strip(),
                    # DBLP publishes no abstracts; venue and year are the only
                    # content it offers, and pretending otherwise would make its
                    # rendition digests look like abstracts.
                    text=" ".join(
                        part
                        for part in (
                            str(info.get("venue", "")).strip(),
                            str(info.get("year", "")).strip(),
                        )
                        if part
                    ),
                    aliases=tuple(aliases),
                )
            )
        return RouteFetch(
            outcome=LiveOutcome.RESULTS,
            records=tuple(records),
            reported_total=int(total_raw) if total_raw.isdigit() else None,
        )

    return search


def crossref_searcher(
    transport: Transport, gate: RateGate, *, rows: int = 25, mailto: str = ""
) -> Searcher:
    """Crossref registered-record search.

    ``mailto`` is passed through only when the caller supplies one; no address is
    invented here. Crossref's polite pool is a real courtesy tier, unlike the
    OpenAlex mailto parameter, which is now ignored.
    """

    def search(query: LiveQuery) -> RouteFetch:
        params: dict[str, object] = {"query": query.text, "rows": rows}
        if mailto.strip():
            params["mailto"] = mailto.strip()
        url = f"{BACKENDS['crossref'].endpoint}?" + urlencode(params)
        response, failure = _http(transport, url, gate, "crossref_list")
        if failure is not None:
            return failure
        assert response is not None
        failure = _status_outcome(response)
        if failure is not None:
            return failure
        payload, failure = _json_body(response)
        if failure is not None:
            return failure
        assert payload is not None
        message = payload.get("message") or {}
        records: list[LiveRecord] = []
        for item in _as_list(message.get("items")):
            doi = str((item or {}).get("DOI", "")).strip()
            if not doi:
                continue
            titles = _as_list(item.get("title"))
            records.append(
                LiveRecord(
                    raw_identifier=doi,
                    title=str(titles[0]).strip() if titles else "",
                    text=_strip_markup(str(item.get("abstract", ""))),
                )
            )
        total = message.get("total-results")
        return RouteFetch(
            outcome=LiveOutcome.RESULTS,
            records=tuple(records),
            reported_total=int(total) if isinstance(total, int) else None,
        )

    return search


def semanticscholar_searcher(
    transport: Transport, gate: RateGate, *, limit: int = 25
) -> Searcher:
    """Semantic Scholar graph search — intermittently available.

    Both probes returned 429 from the shared unauthenticated pool, so the failure
    path below is verified and the success path is not. The registry records that
    asymmetry as ``SHAPE_UNVERIFIED`` rather than letting two guessed field names
    pass as characterized behaviour.
    """

    def search(query: LiveQuery) -> RouteFetch:
        url = (
            f"{BACKENDS['semanticscholar'].endpoint}?"
            + urlencode(
                {
                    "query": query.text,
                    "limit": limit,
                    "fields": "title,abstract,externalIds",
                }
            )
        )
        response, failure = _http(transport, url, gate, "semantic_scholar")
        if failure is not None:
            return failure
        assert response is not None
        failure = _status_outcome(response)
        if failure is not None:
            return failure
        payload, failure = _json_body(response)
        if failure is not None:
            return failure
        assert payload is not None
        records: list[LiveRecord] = []
        for item in _as_list(payload.get("data")):
            external = (item or {}).get("externalIds") or {}
            doi = str(external.get("DOI", "") or "").strip()
            arxiv = str(external.get("ArXiv", "") or "").strip()
            paper = str((item or {}).get("paperId", "") or "").strip()
            candidates = [
                value
                for value in (doi, f"arXiv:{arxiv}" if arxiv else "", f"s2:{paper}" if paper else "")
                if value
            ]
            if not candidates:
                continue
            records.append(
                LiveRecord(
                    raw_identifier=candidates[0],
                    title=str((item or {}).get("title", "") or "").strip(),
                    text=str((item or {}).get("abstract", "") or "").strip(),
                    aliases=tuple(candidates[1:]),
                )
            )
        total = payload.get("total")
        return RouteFetch(
            outcome=LiveOutcome.RESULTS,
            records=tuple(records),
            reported_total=int(total) if isinstance(total, int) else None,
        )

    return search


SEARCHER_FACTORIES: dict[str, Callable[..., Searcher]] = {
    "openaire": openaire_searcher,
    "dblp": dblp_searcher,
    "crossref": crossref_searcher,
    "semanticscholar": semanticscholar_searcher,
}


def build_route(
    backend: str,
    *,
    transport: Transport,
    gate: RateGate,
    variants: Sequence[str],
    budget_units: float | None = None,
    cost_budget_usd: float | None = None,
    searcher: Searcher | None = None,
) -> LiveRoute:
    """Build one live route from the registry.

    ``searcher`` is injectable so arXiv and OpenAlex can keep using the
    repository's own provider clients, which carry their own typed error
    handling, while the new backends use the adapters above.
    """

    spec = BACKENDS.get(backend)
    if spec is None:
        raise ValueError(
            f"unknown backend '{backend}'; known backends are {sorted(BACKENDS)}"
        )
    if searcher is None:
        factory = SEARCHER_FACTORIES.get(backend)
        if factory is None:
            raise ValueError(
                f"backend '{backend}' has no built-in adapter; pass a searcher "
                "built from its provider client"
            )
        searcher = factory(transport, gate)
    return LiveRoute(
        route_id=f"{spec.name}-search",
        route_kind=spec.route_kind,
        backend=spec.name,
        query_derivation=spec.query_derivation,
        provider=spec.provider,
        searcher=searcher,
        plan_query=keyword_planner(spec.query_derivation, variants),
        budget_units=budget_units if budget_units is not None else float(len(variants)),
        cost_budget_usd=cost_budget_usd,
    )


def select_backends(
    names: Sequence[str] | None = None, *, include_disabled: bool = False
) -> tuple[BackendSpec, ...]:
    """Choose the campaign's backend set by name, defaulting to the enabled ones."""

    if names is None:
        chosen = [
            spec
            for spec in BACKENDS.values()
            if include_disabled or spec.enabled_by_default
        ]
    else:
        unknown = [item for item in names if item not in BACKENDS]
        if unknown:
            raise ValueError(f"unknown backends {unknown}; known are {sorted(BACKENDS)}")
        chosen = [BACKENDS[item] for item in names]
    return tuple(sorted(chosen, key=lambda item: item.name))


__all__ = [
    "BACKENDS",
    "BackendSpec",
    "STUDY_PROVIDER_BUDGETS",
    "SEARCHER_FACTORIES",
    "ShapeVerification",
    "build_route",
    "crossref_searcher",
    "dblp_searcher",
    "default_backend_names",
    "openaire_searcher",
    "select_backends",
    "semanticscholar_searcher",
    "study_gate",
    "verified_backends",
]
