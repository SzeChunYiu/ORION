"""Live-provider discovery campaign over real backends.

This is the open-world half of P2. The offline complete-gold world measures
mechanism against a known denominator; a live campaign measures behaviour
against real indices that have no denominator at all. Neither substitutes for
the other, and the difference is not cosmetic: offline, a paper we failed to
retrieve is a countable false negative, while live, a paper we failed to
retrieve is indistinguishable from a paper that does not exist. Everything in
this module is arranged so that the second case can never be reported as the
first.

The engine composes the existing knowledge modules rather than reimplementing
them: identity/ledger for work identity and question-conditioned read state,
``rate`` for request spacing, ``route_control`` for the route state machine and
``routes`` for earned independence. Transport is injected throughout, so the
whole campaign is exercisable without a network.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum

from orion.core.search import SearchRouteKind
from orion.kernel.store import LedgerStore
from orion.knowledge.identity import (
    ReadDecision,
    ReadReceipt,
    SourceIdentity,
    canonical_source_id,
)
from orion.knowledge.ledger import (
    decide_read_from_ledger,
    known_sources,
    record_read,
    record_source,
)
from orion.knowledge.providers.arxiv import ArxivClient, FetchStatus
from orion.knowledge.providers.openalex import OpenAlexClient, OpenAlexStatus
from orion.knowledge.rate import RateGate
from orion.knowledge.route_control import (
    FrozenRouteControlPolicy,
    RouteAttempt,
    RouteControlAction,
    RouteControlDecision,
    RouteControlState,
    decide_route,
)
from orion.knowledge.routes import RouteCapture

_WHITESPACE = re.compile(r"\s+")


class LiveOutcome(str, Enum):
    """The typed result of one route attempt against a live backend.

    Every member that is not ``RESULTS`` or ``EMPTY`` describes a failure to
    *observe* the index. The distinction the whole module rests on is that no
    member of this enum — including ``EMPTY`` — is a statement that a work does
    not exist. ``EMPTY`` says this query, against this index, at this moment,
    matched nothing; the others say we never got to look.
    """

    RESULTS = "RESULTS"
    EMPTY = "EMPTY"
    CREDENTIAL_REQUIRED = "CREDENTIAL_REQUIRED"
    RATE_LIMIT_DEFERRED = "RATE_LIMIT_DEFERRED"
    COST_BUDGET_EXHAUSTED = "COST_BUDGET_EXHAUSTED"
    RATE_GATE_DEFERRED = "RATE_GATE_DEFERRED"
    NO_DERIVABLE_QUERY = "NO_DERIVABLE_QUERY"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    TRANSPORT_ERROR = "TRANSPORT_ERROR"
    TIMEOUT = "TIMEOUT"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    REFUSED_UNSAFE_PAGING = "REFUSED_UNSAFE_PAGING"

    @property
    def observed_the_index(self) -> bool:
        """Whether the backend actually answered about its contents."""

        return self in {LiveOutcome.RESULTS, LiveOutcome.EMPTY}

    @property
    def leaves_open_obligation(self) -> bool:
        """Whether this outcome leaves a route owing an unmet look.

        A deferred, refused, failed or unfunded attempt is a suspended route
        with an open obligation, never a stop. Collapsing these into a stop is
        exactly how an outage becomes evidence of absence.
        """

        return not self.observed_the_index

    @property
    def is_evidence_of_absence(self) -> bool:
        """Never true, for any outcome. Kept explicit so it can be asserted."""

        return False


# The provider clients catch every transport exception and report one
# TRANSPORT_ERROR status, with the exception type preserved in the note. A
# timeout and a refused connection are different operational facts — one says
# the backend is slow, the other that it is unreachable — so the exception name
# the client already recorded is used to recover that distinction rather than
# reaching into modules this study may not modify.
_TIMEOUT_EXCEPTIONS = frozenset(
    {"TimeoutError", "timeout", "socket.timeout", "ReadTimeout", "ReadTimeoutError"}
)


def classify_transport_note(note: str) -> LiveOutcome:
    """Separate a timeout from an otherwise unreachable backend."""

    name = note.split(":", 1)[0].strip()
    return LiveOutcome.TIMEOUT if name in _TIMEOUT_EXCEPTIONS else LiveOutcome.TRANSPORT_ERROR


_OUTCOME_FROM_ARXIV: dict[FetchStatus, LiveOutcome] = {
    FetchStatus.OK: LiveOutcome.RESULTS,
    FetchStatus.RATE_LIMITED: LiveOutcome.RATE_LIMIT_DEFERRED,
    FetchStatus.REFUSED_UNSAFE_PAGING: LiveOutcome.REFUSED_UNSAFE_PAGING,
    FetchStatus.TRANSPORT_ERROR: LiveOutcome.TRANSPORT_ERROR,
    FetchStatus.MALFORMED_RESPONSE: LiveOutcome.MALFORMED_RESPONSE,
    FetchStatus.SERVICE_ERROR: LiveOutcome.PROVIDER_ERROR,
}

_OUTCOME_FROM_OPENALEX: dict[OpenAlexStatus, LiveOutcome] = {
    OpenAlexStatus.OK: LiveOutcome.RESULTS,
    OpenAlexStatus.KEY_REQUIRED: LiveOutcome.CREDENTIAL_REQUIRED,
    OpenAlexStatus.RATE_LIMITED: LiveOutcome.RATE_LIMIT_DEFERRED,
    OpenAlexStatus.REFUSED_BASIC_PAGING_CEILING: LiveOutcome.REFUSED_UNSAFE_PAGING,
    OpenAlexStatus.TRANSPORT_ERROR: LiveOutcome.TRANSPORT_ERROR,
    OpenAlexStatus.MALFORMED_RESPONSE: LiveOutcome.MALFORMED_RESPONSE,
    OpenAlexStatus.SERVICE_ERROR: LiveOutcome.PROVIDER_ERROR,
}


@dataclass(frozen=True)
class ResearchQuestion:
    """One frozen question, and the extraction frame it is asked under."""

    question_id: str
    text: str
    frame_id: str
    extraction_schema_version: str

    def __post_init__(self) -> None:
        if not self.question_id.strip() or not self.text.strip():
            raise ValueError("a research question needs an id and text")
        if not self.frame_id.strip() or not self.extraction_schema_version.strip():
            raise ValueError("read state is question-conditioned: frame and schema required")


@dataclass(frozen=True)
class LiveQuery:
    """One query, carrying how it was derived rather than only what it says."""

    query_id: str
    text: str
    derivation: str
    seed_work_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.query_id.strip() or not self.text.strip():
            raise ValueError("a query needs an id and text")
        if not self.derivation.strip():
            raise ValueError("a query must record how it was derived")


@dataclass(frozen=True)
class LiveRecord:
    """One retrieved rendition, as a single backend described it."""

    raw_identifier: str
    title: str
    text: str
    aliases: tuple[str, ...] = ()
    referenced_works: tuple[str, ...] = ()

    @property
    def rendition_digest(self) -> str:
        """Digest of *this backend's copy* of the work.

        Deliberately backend-sensitive. arXiv serves an author abstract and
        OpenAlex serves one reconstructed from an inverted index, so the same
        paper legitimately has two rendition digests. That is what makes a
        changed-content reread detectable; it is emphatically not an overlap
        key, and using it as one would make every cross-backend re-encounter
        look like a distinct work.
        """

        return _digest("rendition", _normalize(self.title), _normalize(self.text))


@dataclass(frozen=True)
class ContentIdentity:
    """A work-level content identity, stable across backends.

    ``overlap_digest`` is what enters :class:`RouteCapture`. It is computed
    from the alias-closure-resolved work key, not from the retrieved text,
    because the live multi-backend setting breaks the single-backend intuition
    that one work has one content digest. Only when a record carries no
    resolvable identifier at all does the digest fall back to normalized text,
    so an unidentifiable record still participates in overlap rather than being
    silently dropped.
    """

    work_key: str
    overlap_digest: str
    rendition_digest: str
    resolvable: bool


@dataclass(frozen=True)
class RouteFetch:
    """What one searcher call produced, including why it produced nothing."""

    outcome: LiveOutcome
    records: tuple[LiveRecord, ...] = ()
    retry_after_seconds: float | None = None
    cost_usd: float | None = None
    reported_total: int | None = None
    note: str = ""


Searcher = Callable[[LiveQuery], RouteFetch]
QueryPlanner = Callable[[ResearchQuestion, tuple[str, ...], int], LiveQuery | None]


@dataclass(frozen=True)
class LiveRoute:
    """A route family bound to a real backend and a real derivation.

    The three coordinates ``route_kind``/``backend``/``query_derivation`` are
    the same ones :func:`orion.knowledge.routes.assess_pair` judges. Binding
    them here means the :class:`RouteCapture` for an ensemble is *constructed
    from what actually ran*, so an independence verdict is a fact about the
    campaign rather than a label the campaign asserted about itself.
    """

    route_id: str
    route_kind: SearchRouteKind
    backend: str
    query_derivation: str
    provider: str
    searcher: Searcher
    plan_query: QueryPlanner
    budget_units: float
    cost_units_per_attempt: float = 1.0
    cost_budget_usd: float | None = None

    def __post_init__(self) -> None:
        if not self.route_id.strip() or not self.provider.strip():
            raise ValueError("a live route needs a route id and a rate-gate provider")
        if not self.backend.strip() or not self.query_derivation.strip():
            raise ValueError(
                "a live route must name its backend and query derivation; "
                "independence is constructed, not assumed"
            )
        if self.budget_units <= 0:
            raise ValueError("a live route needs a positive attempt budget")
        if self.cost_units_per_attempt < 0:
            raise ValueError("attempt cost cannot be negative")
        if self.cost_budget_usd is not None and self.cost_budget_usd < 0:
            raise ValueError("a monetary budget cannot be negative")


@dataclass(frozen=True)
class AttemptRecord:
    """One attempt, retained whatever it produced."""

    attempt_id: str
    route_id: str
    query: LiveQuery
    outcome: LiveOutcome
    identities: tuple[ContentIdentity, ...] = ()
    route_novel_digests: tuple[str, ...] = ()
    campaign_novel_digests: tuple[str, ...] = ()
    read_decisions: tuple[tuple[str, str], ...] = ()
    cost_units: float = 0.0
    cost_usd: float | None = None
    latency_seconds: float = 0.0
    retry_after_seconds: float | None = None
    reported_total: int | None = None
    trace_refs: tuple[str, ...] = ()
    note: str = ""

    @property
    def overlap_digests(self) -> tuple[str, ...]:
        return tuple(item.overlap_digest for item in self.identities)

    @property
    def failure_signatures(self) -> tuple[str, ...]:
        """Non-empty exactly when the attempt failed to observe the index."""

        return () if self.outcome.observed_the_index else (self.outcome.value,)


@dataclass(frozen=True)
class RouteRun:
    """Everything one route did, and the decision it ended on."""

    route: LiveRoute
    attempts: tuple[AttemptRecord, ...]
    decision: RouteControlDecision
    capture: RouteCapture
    spent_usd: float

    @property
    def open_obligations(self) -> tuple[str, ...]:
        """Outcomes that left this route owing a look it never got."""

        return tuple(
            dict.fromkeys(
                item.outcome.value
                for item in self.attempts
                if item.outcome.leaves_open_obligation
            )
        )


@dataclass(frozen=True)
class TaskClosure:
    """Whether the task may close — a judgement over the ensemble, not a route.

    Separate from every route decision by construction. Proposition
    ``failclosed`` in the formalism holds because no route decision certifies
    saturation; this type is where the only certification lives, and it refuses
    while any route holds an open obligation.
    """

    certified: bool
    open_obligations: tuple[str, ...]
    reasons: tuple[str, ...]
    certified_by_route_decision: bool = False


@dataclass(frozen=True)
class CampaignResult:
    campaign_id: str
    question: ResearchQuestion
    policy_id: str
    runs: tuple[RouteRun, ...]

    @property
    def captures(self) -> tuple[RouteCapture, ...]:
        return tuple(item.capture for item in self.runs)

    @property
    def attempts(self) -> tuple[AttemptRecord, ...]:
        return tuple(item for run in self.runs for item in run.attempts)

    @property
    def union_digests(self) -> frozenset[str]:
        union: set[str] = set()
        for run in self.runs:
            union |= run.capture.captured
        return frozenset(union)


def _normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text or "").strip().lower()


def _digest(domain: str, *parts: str) -> str:
    payload = "\x1f".join((domain, *parts)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def resolve_identity(
    store: LedgerStore, record: LiveRecord
) -> ContentIdentity:
    """Resolve one retrieved record to a work-level content identity.

    The record's own identifier and aliases are recorded first, so the alias
    closure in the ledger can join this rendition to any earlier one — that is
    what lets a paper found by arXiv id and again by DOI count once. The
    resolved key, not the retrieved text, becomes the overlap digest.
    """

    record_source(
        store,
        SourceIdentity(
            source_id=record.raw_identifier,
            aliases=record.aliases,
            title=record.title,
        ),
    )
    canonical = canonical_source_id(record.raw_identifier)
    primary_of: dict[str, str] = {}
    for identity in known_sources(store):
        for key in identity.keys:
            primary_of[key] = identity.source_id
    work_key = primary_of.get(str(canonical), str(canonical))
    if canonical.is_resolvable:
        overlap = _digest("work", work_key)
    else:
        # No resolvable identifier: fall back to normalized text so the record
        # still participates in overlap. Dropping it would quietly shrink the
        # observed union and flatter every coverage quantity built on it.
        overlap = _digest("text", _normalize(record.title), _normalize(record.text))
    return ContentIdentity(
        work_key=work_key,
        overlap_digest=overlap,
        rendition_digest=record.rendition_digest,
        resolvable=canonical.is_resolvable,
    )


def _record_reads(
    store: LedgerStore,
    question: ResearchQuestion,
    records: Sequence[LiveRecord],
    identities: Sequence[ContentIdentity],
) -> tuple[tuple[str, str], ...]:
    """Apply question-conditioned read state to a batch of retrieved records.

    The decision is taken on all four coordinates (work, rendition digest,
    schema version, frame), so a reread forced by a changed extraction question
    is distinguishable from duplicate processing of the same rendition.
    """

    decisions: list[tuple[str, str]] = []
    for record, identity in zip(records, identities, strict=True):
        decision = decide_read_from_ledger(
            store,
            record.raw_identifier,
            identity.rendition_digest,
            question.extraction_schema_version,
            question.frame_id,
        )
        if decision is not ReadDecision.ALREADY_READ:
            record_read(
                store,
                ReadReceipt(
                    source_id=identity.work_key,
                    content_digest=identity.rendition_digest,
                    schema_version=question.extraction_schema_version,
                    frame_id=question.frame_id,
                ),
            )
        decisions.append((identity.work_key, decision.value))
    return tuple(decisions)


def run_route(
    route: LiveRoute,
    question: ResearchQuestion,
    *,
    store: LedgerStore,
    gate: RateGate,
    policy: FrozenRouteControlPolicy,
    clock: Callable[[], float],
    seed_work_keys: tuple[str, ...] = (),
    campaign_seen: set[str] | None = None,
    recorder: object | None = None,
    alternative_route_kinds: tuple[SearchRouteKind, ...] = (),
    max_attempts: int = 8,
) -> RouteRun:
    """Drive one route to a terminal decision, retaining every outcome.

    The loop is deliberately decision-first: ``decide_route`` is consulted
    before each attempt under a frozen policy, so route control is the same
    code path the offline harness and the manuscript describe, not a bespoke
    live heuristic.
    """

    campaign_seen = campaign_seen if campaign_seen is not None else set()
    attempts: list[AttemptRecord] = []
    control: list[RouteAttempt] = []
    route_seen: set[str] = set()
    spent_usd = 0.0

    for index in range(max_attempts):
        state = RouteControlState(
            route.route_id,
            route.route_kind,
            tuple(control),
            route.budget_units,
            alternative_route_kinds,
        )
        decision = decide_route(state, policy)
        if decision.action in {
            RouteControlAction.STOP,
            RouteControlAction.SUSPEND,
            RouteControlAction.SWITCH,
        }:
            break

        attempt_id = f"{route.route_id}.a{index}"
        query = route.plan_query(question, seed_work_keys, index)
        if query is None:
            attempts.append(
                AttemptRecord(
                    attempt_id=attempt_id,
                    route_id=route.route_id,
                    query=LiveQuery(
                        f"{attempt_id}.q", question.text, route.query_derivation
                    ),
                    outcome=LiveOutcome.NO_DERIVABLE_QUERY,
                    note="route had no derivable query at this point in the campaign",
                )
            )
            control.append(
                RouteAttempt(
                    attempt_id, f"{attempt_id}.q", (), (), 0.0,
                    (LiveOutcome.NO_DERIVABLE_QUERY.value,),
                )
            )
            continue

        # Monetary budget is a separate constraint from request spacing.
        # OpenAlex meters per-call dollars against a daily per-IP allowance;
        # the RateGate models only the interval between calls, so exhausting
        # money must be its own recorded outcome rather than a silent stall.
        if route.cost_budget_usd is not None and spent_usd >= route.cost_budget_usd:
            attempts.append(
                AttemptRecord(
                    attempt_id=attempt_id,
                    route_id=route.route_id,
                    query=query,
                    outcome=LiveOutcome.COST_BUDGET_EXHAUSTED,
                    note=f"spent {spent_usd} of {route.cost_budget_usd} USD",
                )
            )
            control.append(
                RouteAttempt(
                    attempt_id, query.query_id, (), (), 0.0,
                    (LiveOutcome.COST_BUDGET_EXHAUSTED.value,),
                )
            )
            continue

        wait = gate.wait_seconds(route.provider)
        if wait > 0:
            attempts.append(
                AttemptRecord(
                    attempt_id=attempt_id,
                    route_id=route.route_id,
                    query=query,
                    outcome=LiveOutcome.RATE_GATE_DEFERRED,
                    retry_after_seconds=wait,
                    note=f"{wait:.6f}s of provider spacing remaining",
                )
            )
            control.append(
                RouteAttempt(
                    attempt_id, query.query_id, (), (), 0.0,
                    (LiveOutcome.RATE_GATE_DEFERRED.value,),
                )
            )
            continue

        mark = recorder.mark() if recorder is not None else None
        started = clock()
        fetch = route.searcher(query)
        latency = max(0.0, clock() - started)
        trace_refs: tuple[str, ...] = ()
        if recorder is not None and mark is not None:
            trace_refs = tuple(item.response_sha256 for item in recorder.since(mark))
        if fetch.cost_usd:
            spent_usd += fetch.cost_usd

        identities: tuple[ContentIdentity, ...] = ()
        reads: tuple[tuple[str, str], ...] = ()
        if fetch.records:
            identities = tuple(resolve_identity(store, item) for item in fetch.records)
            reads = _record_reads(store, question, fetch.records, identities)

        outcome = fetch.outcome
        if outcome is LiveOutcome.RESULTS and not fetch.records:
            # A successful transport with no rows is EMPTY, which is a fact
            # about this query against this index — never about the world.
            outcome = LiveOutcome.EMPTY

        retrieved = tuple(dict.fromkeys(item.overlap_digest for item in identities))
        route_novel = tuple(item for item in retrieved if item not in route_seen)
        campaign_novel = tuple(item for item in retrieved if item not in campaign_seen)
        route_seen.update(retrieved)
        campaign_seen.update(retrieved)

        attempts.append(
            AttemptRecord(
                attempt_id=attempt_id,
                route_id=route.route_id,
                query=query,
                outcome=outcome,
                identities=identities,
                route_novel_digests=route_novel,
                campaign_novel_digests=campaign_novel,
                read_decisions=reads,
                cost_units=route.cost_units_per_attempt,
                cost_usd=fetch.cost_usd,
                latency_seconds=latency,
                retry_after_seconds=fetch.retry_after_seconds,
                reported_total=fetch.reported_total,
                trace_refs=trace_refs,
                note=fetch.note,
            )
        )
        control.append(
            RouteAttempt(
                attempt_id=attempt_id,
                query_id=query.query_id,
                retrieved_digests=retrieved,
                novel_digests=route_novel,
                cost_units=route.cost_units_per_attempt,
                execution_failure_signatures=(
                    () if outcome.observed_the_index else (outcome.value,)
                ),
            )
        )

    decision = decide_route(
        RouteControlState(
            route.route_id,
            route.route_kind,
            tuple(control),
            route.budget_units,
            alternative_route_kinds,
        ),
        policy,
    )
    capture = RouteCapture(
        route_kind=route.route_kind,
        backend=route.backend,
        query_derivation=route.query_derivation,
        captured=frozenset(route_seen),
    )
    return RouteRun(
        route=route,
        attempts=tuple(attempts),
        decision=decision,
        capture=capture,
        spent_usd=spent_usd,
    )


def run_campaign(
    campaign_id: str,
    question: ResearchQuestion,
    routes: Sequence[LiveRoute],
    *,
    store: LedgerStore,
    gate: RateGate,
    policy: FrozenRouteControlPolicy,
    clock: Callable[[], float],
    recorder: object | None = None,
    max_attempts: int = 8,
) -> CampaignResult:
    """Run every route for one question, feeding confirmed seeds forward.

    Routes run in the given order and each one sees the work keys confirmed so
    far, which is what gives a citation-chaining route a genuinely different
    query derivation: its queries are functions of retrieved works rather than
    of the question text.
    """

    if not routes:
        raise ValueError("a campaign needs at least one route")
    seen: set[str] = set()
    confirmed: list[str] = []
    runs: list[RouteRun] = []
    for route in routes:
        run = run_route(
            route,
            question,
            store=store,
            gate=gate,
            policy=policy,
            clock=clock,
            seed_work_keys=tuple(confirmed),
            campaign_seen=seen,
            recorder=recorder,
            # The other routes in the ensemble are this route's alternatives,
            # which is what makes SWITCH a real option rather than dead code:
            # a route stops being worth pushing when another can be tried.
            alternative_route_kinds=tuple(
                dict.fromkeys(
                    item.route_kind for item in routes if item.route_kind is not route.route_kind
                )
            ),
            max_attempts=max_attempts,
        )
        runs.append(run)
        for attempt in run.attempts:
            for identity in attempt.identities:
                if identity.resolvable and identity.work_key not in confirmed:
                    confirmed.append(identity.work_key)
    return CampaignResult(
        campaign_id=campaign_id,
        question=question,
        policy_id=policy.policy_id,
        runs=tuple(runs),
    )


def assess_task_closure(result: CampaignResult) -> TaskClosure:
    """Decide whether the task may close, over the whole route ensemble.

    Route decisions are inputs, never authority: a route that stops because its
    own budget ran out has said nothing about the task. Closure requires that
    no route holds an open obligation — a suspended route, a deferred attempt,
    an unfunded backend — because each of those is a look we owe and never took.
    """

    obligations: list[str] = []
    reasons: list[str] = []
    for run in result.runs:
        for item in run.open_obligations:
            obligations.append(f"{run.route.route_id}:{item}")
        if run.decision.action is RouteControlAction.SUSPEND:
            obligations.append(f"{run.route.route_id}:SUSPENDED")
        if run.decision.certifies_task_saturation:  # pragma: no cover - invariant
            raise AssertionError(
                "a route decision claimed task saturation; fail-closed stopping violated"
            )
    if obligations:
        reasons.append("open route obligations remain unmet")
    else:
        reasons.append("every route reached a terminal state with no unmet obligation")
    return TaskClosure(
        certified=not obligations,
        open_obligations=tuple(dict.fromkeys(obligations)),
        reasons=tuple(reasons),
        certified_by_route_decision=False,
    )


# --- searcher adapters over the existing provider clients ------------------


def _require_gated(client: object, provider: str) -> None:
    """Refuse a provider client that cannot record its own requests.

    The engine asks the gate how long to wait, but only the client records that
    a request happened. An ungated client therefore leaves the gate permanently
    at zero, and the route would burst a public API while appearing to respect
    its budget — a politeness failure that is invisible until it is a ban.
    """

    if getattr(client, "gate", None) is None:
        raise ValueError(
            f"the {provider} client must be constructed with the campaign's RateGate; "
            "an ungated client never records its requests, so spacing is never enforced"
        )


def arxiv_searcher(client: ArxivClient, *, max_results: int = 25) -> Searcher:
    """Bind an arXiv client as a route searcher with typed outcomes."""

    _require_gated(client, "arxiv")

    def search(query: LiveQuery) -> RouteFetch:
        result = client.fetch(search_query=f"all:{query.text}", max_results=max_results)
        outcome = _OUTCOME_FROM_ARXIV.get(result.status, LiveOutcome.PROVIDER_ERROR)
        if outcome is LiveOutcome.TRANSPORT_ERROR:
            outcome = classify_transport_note(result.note)
        records = tuple(
            LiveRecord(
                raw_identifier=item.source_id,
                title=item.title,
                text=item.summary,
                aliases=item.aliases,
            )
            for item in result.records
        )
        return RouteFetch(
            outcome=outcome,
            records=records,
            retry_after_seconds=result.retry_after_seconds,
            note=result.note,
        )

    return search


def openalex_keyword_searcher(
    client: OpenAlexClient, *, per_page: int = 25
) -> Searcher:
    """Bind OpenAlex keyword search as a route searcher."""

    _require_gated(client, "openalex")

    def search(query: LiveQuery) -> RouteFetch:
        page = client.fetch_works(search=query.text, per_page=per_page)
        return _openalex_fetch(page)

    return search


def openalex_citation_searcher(
    client: OpenAlexClient, *, per_page: int = 25
) -> Searcher:
    """Bind OpenAlex citation chaining as a route searcher.

    Queries are ``cites:``/``cited_by`` filters over seed works rather than
    free text, which is what makes this route's query derivation genuinely
    different from keyword search on the same backend. The backend is still
    shared, so the two remain non-independent — a fact the ensemble reports
    rather than one this module can wish away.
    """

    _require_gated(client, "openalex")

    def search(query: LiveQuery) -> RouteFetch:
        if not query.seed_work_keys:
            return RouteFetch(
                outcome=LiveOutcome.NO_DERIVABLE_QUERY,
                note="citation chaining needs at least one confirmed seed work",
            )
        page = client.fetch_works(filters=query.text, per_page=per_page)
        return _openalex_fetch(page)

    return search


def _openalex_fetch(page: object) -> RouteFetch:
    outcome = _OUTCOME_FROM_OPENALEX.get(
        getattr(page, "status"), LiveOutcome.PROVIDER_ERROR
    )
    if outcome is LiveOutcome.TRANSPORT_ERROR:
        outcome = classify_transport_note(str(getattr(page, "note", "")))
    records = tuple(
        LiveRecord(
            raw_identifier=item.source_id,
            title=item.title,
            text=item.abstract,
            aliases=item.aliases,
            referenced_works=item.referenced_works,
        )
        for item in getattr(page, "records", ())
    )
    return RouteFetch(
        outcome=outcome,
        records=records,
        retry_after_seconds=getattr(page, "retry_after_seconds", None),
        cost_usd=getattr(page, "cost_usd", None),
        reported_total=getattr(page, "total", None),
        note=getattr(page, "note", ""),
    )


# --- query planners --------------------------------------------------------


def keyword_planner(derivation: str, variants: Sequence[str]) -> QueryPlanner:
    """Plan queries from the frozen question text and fixed lexical variants."""

    def plan(
        question: ResearchQuestion, seeds: tuple[str, ...], index: int
    ) -> LiveQuery | None:
        if index >= len(variants):
            return None
        return LiveQuery(
            query_id=f"{question.question_id}.{derivation}.{index}",
            text=variants[index],
            derivation=derivation,
        )

    return plan


def citation_planner(derivation: str, *, seeds_per_query: int = 5) -> QueryPlanner:
    """Plan OpenAlex filter queries from works confirmed by earlier routes."""

    def plan(
        question: ResearchQuestion, seeds: tuple[str, ...], index: int
    ) -> LiveQuery | None:
        openalex_seeds = [item for item in seeds if item.startswith("openalex:")]
        if not openalex_seeds:
            return None
        window = openalex_seeds[
            index * seeds_per_query : (index + 1) * seeds_per_query
        ]
        if not window:
            return None
        ids = "|".join(item.split(":", 1)[1] for item in window)
        return LiveQuery(
            query_id=f"{question.question_id}.{derivation}.{index}",
            text=f"cites:{ids}",
            derivation=derivation,
            seed_work_keys=tuple(window),
        )

    return plan


__all__ = [
    "AttemptRecord",
    "CampaignResult",
    "ContentIdentity",
    "LiveOutcome",
    "LiveQuery",
    "LiveRecord",
    "LiveRoute",
    "ResearchQuestion",
    "RouteFetch",
    "RouteRun",
    "TaskClosure",
    "arxiv_searcher",
    "assess_task_closure",
    "citation_planner",
    "classify_transport_note",
    "keyword_planner",
    "openalex_citation_searcher",
    "openalex_keyword_searcher",
    "resolve_identity",
    "run_campaign",
    "run_route",
]
