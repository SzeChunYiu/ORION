"""Section 5 -- raw trace retention and evidence-use classification.

Every query is retained verbatim, including the empty and errored occasions:
no filter exists to drop them, so "all failures and nulls preserved" is a
property of the type. Retrieved-but-unused is distinguished from
present-but-missed only where ground truth permits, and reported as
CANNOT_CHECK where it does not.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from enum import Enum

from orion.core.search import SearchRouteKind

from .constants import _sha256


@dataclass(frozen=True)
class TraceItem:
    item_id: str
    content_digest: str
    source_uri: str

    def __post_init__(self) -> None:
        if not self.item_id.strip() or not self.content_digest.strip():
            raise ValueError("trace item identity and content digest are required")


@dataclass(frozen=True)
class QueryTrace:
    """One raw retrieval occasion, retained whether or not it produced anything.

    An errored or empty query is kept with the same status as a productive one.
    A trace that drops its empties cannot distinguish "this route found nothing"
    from "this route was never tried", and those are different failures.
    """

    query_id: str
    query_text: str
    route_kind: SearchRouteKind
    backend: str
    query_derivation: str
    items: tuple[TraceItem, ...] = ()
    error: str = ""

    def __post_init__(self) -> None:
        if not self.query_id.strip() or not self.query_text.strip():
            raise ValueError("query trace identity and text are required")
        if not self.backend.strip() or not self.query_derivation.strip():
            raise ValueError(
                "a query trace must declare its backend and query derivation; "
                "independence is constructed, not assumed"
            )

    @property
    def productive(self) -> bool:
        return bool(self.items) and not self.error


@dataclass(frozen=True)
class RawTrialTrace:
    """Append-only record of every query issued for one task.

    There is no filter, predicate or `skip_if_empty` on this path by design:
    "preserve all failures and nulls" is only true if there is nowhere for a
    record to be dropped.
    """

    task_id: str
    records: tuple[QueryTrace, ...] = ()

    def extend(self, *queries: QueryTrace) -> RawTrialTrace:
        return replace(self, records=self.records + tuple(queries))

    @property
    def item_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(item.item_id for record in self.records for item in record.items)
        )

    @property
    def empty_queries(self) -> tuple[QueryTrace, ...]:
        return tuple(item for item in self.records if not item.items)

    @property
    def errored_queries(self) -> tuple[QueryTrace, ...]:
        return tuple(item for item in self.records if item.error)

    @property
    def route_kinds(self) -> tuple[SearchRouteKind, ...]:
        return tuple(dict.fromkeys(item.route_kind for item in self.records))

    @property
    def productive_route_kinds(self) -> tuple[SearchRouteKind, ...]:
        return tuple(
            dict.fromkeys(item.route_kind for item in self.records if item.productive)
        )

    def routes_for(self, item_id: str) -> tuple[tuple[SearchRouteKind, str], ...]:
        """(route, backend) pairs that returned this item."""

        return tuple(
            dict.fromkeys(
                (record.route_kind, record.backend)
                for record in self.records
                if any(item.item_id == item_id for item in record.items)
            )
        )

    @property
    def fingerprint(self) -> str:
        return _sha256(
            {
                "task_id": self.task_id,
                "records": [
                    {
                        "query_id": record.query_id,
                        "query_text": record.query_text,
                        "route_kind": record.route_kind.value,
                        "backend": record.backend,
                        "query_derivation": record.query_derivation,
                        "error": record.error,
                        "items": [
                            {
                                "item_id": item.item_id,
                                "content_digest": item.content_digest,
                                "source_uri": item.source_uri,
                            }
                            for item in record.items
                        ],
                    }
                    for record in self.records
                ],
            }
        )


class EvidenceUseClass(str, Enum):
    """Why a piece of evidence did or did not reach the answer."""

    USED = "USED"
    RETRIEVED_BUT_UNUSED = "RETRIEVED_BUT_UNUSED"
    PRESENT_BUT_MISSED = "PRESENT_BUT_MISSED"
    CITED_BUT_UNRETRIEVED = "CITED_BUT_UNRETRIEVED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class EvidenceUseReport:
    task_id: str
    classes: tuple[tuple[str, EvidenceUseClass], ...]
    ground_truth_bound: bool
    cannot_check_reason: str = ""

    def _of(self, kind: EvidenceUseClass) -> tuple[str, ...]:
        return tuple(item for item, value in self.classes if value is kind)

    @property
    def used(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.USED)

    @property
    def retrieved_but_unused(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.RETRIEVED_BUT_UNUSED)

    @property
    def present_but_missed(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.PRESENT_BUT_MISSED)

    @property
    def cited_but_unretrieved(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.CITED_BUT_UNRETRIEVED)

    @property
    def cannot_check(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.CANNOT_CHECK)


def classify_evidence_use(
    trace: RawTrialTrace,
    *,
    cited_ids: Sequence[str],
    corpus_present_ids: frozenset[str] | None = None,
) -> EvidenceUseReport:
    """Classify every trace item, every citation and every known-present item.

    The distinction issue #8 asks for lives in `corpus_present_ids`. When ground
    truth is bound, an item the corpus contains but the trace never returned is
    PRESENT_BUT_MISSED: a search failure, not an answering failure. When it is
    unbound, the same item is unobservable, and the report says CANNOT_CHECK
    rather than reporting zero misses -- an unbound answer key that silently
    reads as "nothing was missed" is the exact conflation the P1 provider's
    typed refusal exists to prevent.

    Classification is total: every id from the trace, the citations and the
    corpus appears exactly once, so no item can fall out of the report.
    """

    cited = tuple(dict.fromkeys(cited_ids))
    retrieved = set(trace.item_ids)
    classes: list[tuple[str, EvidenceUseClass]] = []
    seen: set[str] = set()

    def _add(item_id: str, kind: EvidenceUseClass) -> None:
        if item_id in seen:
            return
        seen.add(item_id)
        classes.append((item_id, kind))

    for item_id in cited:
        _add(
            item_id,
            EvidenceUseClass.USED
            if item_id in retrieved
            else EvidenceUseClass.CITED_BUT_UNRETRIEVED,
        )
    for item_id in trace.item_ids:
        _add(item_id, EvidenceUseClass.RETRIEVED_BUT_UNUSED)
    if corpus_present_ids is not None:
        for item_id in sorted(corpus_present_ids):
            _add(item_id, EvidenceUseClass.PRESENT_BUT_MISSED)
        reason = ""
    else:
        reason = (
            "ground truth for this task is UNBOUND, so present-but-missed cannot "
            "be separated from absent-from-corpus; this is CANNOT_CHECK, not zero"
        )
        _add(f"{trace.task_id}:present_but_missed", EvidenceUseClass.CANNOT_CHECK)
    return EvidenceUseReport(
        task_id=trace.task_id,
        classes=tuple(classes),
        ground_truth_bound=corpus_present_ids is not None,
        cannot_check_reason=reason,
    )
