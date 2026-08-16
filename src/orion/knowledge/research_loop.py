from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from orion.core.evidence import EvidenceRecord, content_fingerprint
from orion.core.search import SearchRouteKind
from orion.kernel.store import LedgerStore
from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.questioning import MechanicQuestion

from .identity import ReadDecision, ReadReceipt, SourceIdentity, canonical_source_id
from .ledger import decide_read_from_ledger, record_read, record_source
from .routes import CoverageEstimate, EnsembleReport, RouteCapture, build_ensemble


@dataclass(frozen=True)
class RetrievedDoc:
    """One document a route returned, identified by content."""

    source_id: str
    content: str
    title: str = ""

    @property
    def digest(self) -> str:
        return content_fingerprint(
            EvidenceRecord(
                evidence_id=self.source_id,
                content=self.content or self.source_id,
                source_uri=self.source_id,
            )
        )


class RouteSearcher(Protocol):
    """A backend able to answer one route family's queries."""

    def search(self, query: str) -> Sequence[RetrievedDoc]: ...


@dataclass(frozen=True)
class RouteBinding:
    """Which backend serves a route, and what makes its queries its own.

    The binding is where independence is constructed. Two routes bound to one
    backend, or deriving their queries the same way, are one capture occasion
    wearing two names — and the ensemble will say so rather than trusting the
    label.
    """

    route_kind: SearchRouteKind
    backend: str
    query_derivation: str
    searcher: RouteSearcher


_DERIVATIONS: dict[SearchRouteKind, Callable[[MechanicCell, MechanicQuestion], str]] = {
    SearchRouteKind.CURRENT_VOCABULARY: lambda cell, q: f"{cell.purpose} {q.dimension.value.lower()}",
    SearchRouteKind.FUNCTION_ONLY: lambda cell, q: (
        f"how to {cell.purpose.lower().rstrip('.')} regardless of framework"
    ),
    SearchRouteKind.PARENT_DISCIPLINE: lambda cell, q: (
        f"canonical treatment of {q.dimension.value.lower()} in an established discipline"
    ),
    SearchRouteKind.LITERATURE_BRIDGE: lambda cell, q: (
        f"survey of {q.dimension.value.lower()} methods across fields"
    ),
    SearchRouteKind.ADVERSARIAL_OMISSION: lambda cell, q: (
        f"critiques and failure modes of {q.dimension.value.lower()} approaches"
    ),
    SearchRouteKind.CITATION_NEIGHBORHOOD: lambda cell, q: (
        f"works citing established {q.dimension.value.lower()} results"
    ),
    SearchRouteKind.FRESHNESS: lambda cell, q: (
        f"recent advances in {q.dimension.value.lower()}"
    ),
}


def derive_route_query(
    cell: MechanicCell, question: MechanicQuestion, route: SearchRouteKind
) -> str:
    """Turn one open mechanic question into one route's query.

    The derivations differ per route on purpose. Routes that merely reword one
    query are not separate occasions, and an ensemble built from them measures
    the phrasing rather than the literature.
    """

    builder = _DERIVATIONS.get(route)
    if builder is None:
        return f"{cell.purpose} {question.question}"
    return builder(cell, question)


@dataclass(frozen=True)
class EvidenceCandidate:
    """One document offered as evidence, with which routes found it."""

    source_id: str
    digest: str
    title: str
    found_by: tuple[SearchRouteKind, ...]
    read_decision: ReadDecision

    @property
    def corroborated(self) -> bool:
        """Found by more than one independent-capable route."""

        return len(self.found_by) > 1


@dataclass(frozen=True)
class ResearchPacket:
    """Everything gathered for one open question, ready to be answered from.

    Deliberately stops short of an answer. Turning retrieved material into a
    claim requires comprehension, which is a provider port, not something this
    module may quietly perform. The packet is the honest handoff: here is the
    evidence, here is how much of the space it plausibly covers, and here is
    what was not searched.
    """

    question_id: str
    mechanic_id: str
    dimension: MechanicDimension
    candidates: tuple[EvidenceCandidate, ...]
    ensemble: EnsembleReport
    unavailable_routes: tuple[SearchRouteKind, ...]
    queries: tuple[tuple[str, str], ...]

    @property
    def coverage(self) -> CoverageEstimate:
        return self.ensemble.estimate

    @property
    def fresh(self) -> tuple[EvidenceCandidate, ...]:
        return tuple(
            item for item in self.candidates
            if item.read_decision is not ReadDecision.ALREADY_READ
        )

    @property
    def coverage_obligations_open(self) -> bool:
        """A declared route with no backend is a gap, not an absence."""

        return bool(self.unavailable_routes)


def run_research_round(
    store: LedgerStore,
    cell: MechanicCell,
    question: MechanicQuestion,
    bindings: Sequence[RouteBinding],
    *,
    declared_routes: Sequence[SearchRouteKind] = (),
    schema_version: str = "packet-v0",
) -> ResearchPacket:
    """Search one open question across route families and record what came back.

    The frame is the question itself, so a paper already read for a different
    question is read again for this one — which is the distinction the read
    ledger exists to keep, and the reason "we have seen this paper" is not the
    same claim as "we have covered this question".
    """

    frame_id = f"question:{question.question_id}"
    bound = {item.route_kind for item in bindings}
    unavailable = tuple(
        route for route in declared_routes if route not in bound
    )

    captures: list[RouteCapture] = []
    found_by: dict[str, list[SearchRouteKind]] = {}
    documents: dict[str, RetrievedDoc] = {}
    queries: list[tuple[str, str]] = []

    for binding in bindings:
        query = derive_route_query(cell, question, binding.route_kind)
        queries.append((binding.route_kind.value, query))
        try:
            results = binding.searcher.search(query)
        except Exception:  # noqa: BLE001 - a failed route is a coverage gap
            results = ()
            unavailable = (*unavailable, binding.route_kind)
        digests: set[str] = set()
        for doc in results:
            digest = doc.digest
            digests.add(digest)
            documents.setdefault(digest, doc)
            found_by.setdefault(digest, []).append(binding.route_kind)
        captures.append(
            RouteCapture(
                route_kind=binding.route_kind,
                backend=binding.backend,
                query_derivation=binding.query_derivation,
                captured=frozenset(digests),
            )
        )

    candidates: list[EvidenceCandidate] = []
    for digest, doc in sorted(documents.items(), key=lambda item: item[1].source_id):
        decision = decide_read_from_ledger(
            store, doc.source_id, digest, schema_version, frame_id
        )
        if decision is not ReadDecision.ALREADY_READ:
            record_source(
                store,
                SourceIdentity(
                    source_id=str(canonical_source_id(doc.source_id)),
                    title=doc.title,
                ),
            )
            record_read(
                store,
                ReadReceipt(
                    source_id=doc.source_id,
                    content_digest=digest,
                    schema_version=schema_version,
                    frame_id=frame_id,
                ),
            )
        candidates.append(
            EvidenceCandidate(
                source_id=doc.source_id,
                digest=digest,
                title=doc.title,
                found_by=tuple(dict.fromkeys(found_by.get(digest, ()))),
                read_decision=decision,
            )
        )

    return ResearchPacket(
        question_id=question.question_id,
        mechanic_id=question.mechanic_id,
        dimension=question.dimension,
        candidates=tuple(candidates),
        ensemble=build_ensemble(captures),
        unavailable_routes=tuple(dict.fromkeys(unavailable)),
        queries=tuple(queries),
    )


def packet_summary(packet: ResearchPacket) -> Mapping[str, object]:
    """Machine-readable view, for the diagnostic surface rather than a figure."""

    return {
        "question_id": packet.question_id,
        "mechanic_id": packet.mechanic_id,
        "dimension": packet.dimension.value,
        "candidates": len(packet.candidates),
        "fresh": len(packet.fresh),
        "corroborated": sum(1 for item in packet.candidates if item.corroborated),
        "routes_searched": [kind.value for kind in packet.ensemble.route_kinds],
        "unavailable_routes": [item.value for item in packet.unavailable_routes],
        "independent_pairs": packet.coverage.independent_pairs,
        "observed": packet.coverage.observed,
        "population_estimate": packet.coverage.population_estimate,
        "coverage_fraction": packet.coverage.coverage_fraction,
        "coverage_refusal": packet.coverage.refusal_reason,
        "singletons": packet.ensemble.singletons,
        "doubletons": packet.ensemble.doubletons,
    }
