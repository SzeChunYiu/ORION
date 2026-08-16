"""Interfaces for ORION-P2 systems under test. No implementations live here.

Every compared system — ORION, every baseline, every ablation — is exactly a
`SystemUnderTest`. It receives a `PublicView` and a `DiscoverySession`, never a
task, a world or a gold set, so the protocol's `hidden_labels` policy is enforced
by the signature rather than by discipline.

The custody split matters. A system returns a `SystemReport`: its claims, and
nothing else. The *record* of what it did — every route call, every read, every
stop decision, every unit of budget — is built host-side by the session as those
actions happen. A system therefore cannot under-report a route it used, over-
report a document it never retrieved, or edit its own trace after the fact, which
is what "candidate outputs cannot modify evaluator state" has to mean in code.

This module deliberately holds no scoring and no retrieval logic. Whatever
lexical, dense or hybrid machinery the baselines need is next-phase work; freezing
the world before any system exists is what stops a system being tuned to it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from .cases import PublicView


class TransportStatus(str, Enum):
    """Route call outcomes, sharing the vocabulary of `ROUTE_TRIAL_SCHEMA_V1`."""

    OK = "OK"
    RATE_LIMITED = "RATE_LIMITED"
    UNAVAILABLE = "UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


class StopScope(str, Enum):
    """Route-stop and task-stop are different claims and are typed separately.

    A route that is exhausted, dead or out of budget licenses abandoning *that
    route*. Nothing about it licenses the claim that the question is answered.
    Collapsing the two is the premature-closure failure P2.H3 measures.
    """

    ROUTE = "ROUTE"
    TASK = "TASK"


class ReadClassification(str, Enum):
    """Why a read was or was not new work.

    Mirrors `orion.knowledge.identity.ReadDecision` on purpose but is computed
    independently by the host. An evaluator that classified reads by calling the
    subsystem under test would hide that subsystem's bugs inside its own score.
    """

    FIRST_READ = "FIRST_READ"
    DUPLICATE = "DUPLICATE"
    REVISION_REREAD = "REVISION_REREAD"
    NEW_QUESTION_REREAD = "NEW_QUESTION_REREAD"


@dataclass(frozen=True)
class ResourceUse:
    """Matched-budget accounting. A system that wins by spending more has not won."""

    wallclock_seconds: float = 0.0
    model_tokens: int = 0
    tool_calls: int = 0
    search_queries: int = 0
    reads: int = 0

    def as_json(self) -> dict[str, Any]:
        return {
            "wallclock_seconds": self.wallclock_seconds,
            "model_tokens": self.model_tokens,
            "tool_calls": self.tool_calls,
            "search_queries": self.search_queries,
            "reads": self.reads,
        }


@dataclass(frozen=True)
class RetrievedRecord:
    """What a system sees of a document: bibliography, not labels.

    `concept_tags` is absent by construction — it is the relevance rule, and a
    structured relevance field would hand the system the gold. Relevance stays
    inferable from `title`/`abstract`, because a world where relevance cannot be
    judged from content makes screening impossible rather than hard.
    """

    doc_id: str
    content_identity: str
    content_digest: str
    version: int
    title: str
    abstract: str
    venue: str
    year: int
    authors: tuple[str, ...]
    references: tuple[str, ...]


@dataclass(frozen=True)
class RouteOutcome:
    """What one route call returned to the system."""

    route: str
    probe: str
    status: TransportStatus
    records: tuple[RetrievedRecord, ...]
    note: str = ""

    @property
    def usable(self) -> bool:
        return self.status is TransportStatus.OK


@dataclass(frozen=True)
class ReadOutcome:
    """What one read returned. `classification` is the host's verdict, not a hint."""

    doc_id: str
    content_identity: str
    content_digest: str
    extraction_question: str
    classification: ReadClassification
    text: str


@dataclass(frozen=True)
class RouteEvent:
    """Host record of one route call, in the order it happened."""

    index: int
    route: str
    probe: str
    backend_identity: str
    query_derivation_identity: str
    status: str
    retrieved_doc_ids: tuple[str, ...]
    retrieved_content_identities: tuple[str, ...]
    novel_content_identities: tuple[str, ...]
    note: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "route": self.route,
            "probe": self.probe,
            "backend_identity": self.backend_identity,
            "query_derivation_identity": self.query_derivation_identity,
            "status": self.status,
            "retrieved_doc_ids": list(self.retrieved_doc_ids),
            "retrieved_content_identities": list(self.retrieved_content_identities),
            "novel_content_identities": list(self.novel_content_identities),
            "note": self.note,
        }


@dataclass(frozen=True)
class ReadEvent:
    """Host record of one read, keyed on the four coordinates a reread turns on."""

    index: int
    doc_id: str
    content_identity: str
    content_digest: str
    extraction_question: str
    classification: str

    def as_json(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "doc_id": self.doc_id,
            "content_identity": self.content_identity,
            "content_digest": self.content_digest,
            "extraction_question": self.extraction_question,
            "classification": self.classification,
        }


@dataclass(frozen=True)
class StopDecision:
    """A declared stop, with the position in the timeline it was declared at.

    The index is what lets the oracle replay world state at the moment of the
    decision and report how much was still reachable then. A stop reported
    without its position cannot be scored for prematurity at all.
    """

    index: int
    scope: str
    route: str
    reason: str
    claimed_complete: bool = False

    def as_json(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "scope": self.scope,
            "route": self.route,
            "reason": self.reason,
            "claimed_complete": self.claimed_complete,
        }


@dataclass(frozen=True)
class SystemReport:
    """Everything a system returns. Claims only; the record of its actions is host-owned."""

    claimed_relevant_content_identities: tuple[str, ...] = ()
    task_closed_as_complete: bool = False
    abstained: bool = False
    notes: str = ""


@dataclass(frozen=True)
class SystemTrace:
    """One system's full run on one task, assembled host-side.

    `route_events`, `read_events` and `resources` come from the session, not from
    the system. Only the fields under `report` are the system's own words.
    """

    task_id: str
    system_id: str
    seed: int
    report: SystemReport
    route_events: tuple[RouteEvent, ...] = ()
    read_events: tuple[ReadEvent, ...] = ()
    stop_decisions: tuple[StopDecision, ...] = ()
    resources: ResourceUse = field(default_factory=ResourceUse)
    budget_exhausted: str = ""
    error_class: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "system_id": self.system_id,
            "seed": self.seed,
            "claimed_relevant_content_identities": list(
                self.report.claimed_relevant_content_identities
            ),
            "task_closed_as_complete": self.report.task_closed_as_complete,
            "abstained": self.report.abstained,
            "route_events": [item.as_json() for item in self.route_events],
            "read_events": [item.as_json() for item in self.read_events],
            "stop_decisions": [item.as_json() for item in self.stop_decisions],
            "resources": self.resources.as_json(),
            "budget_exhausted": self.budget_exhausted,
            "error_class": self.error_class,
            "notes": self.report.notes,
        }


class DiscoverySession(Protocol):
    """The only handle a system has on the world. Host-owned and recording.

    Every method call is metered and logged before it returns. Once a budget
    dimension is spent the session stays closed and keeps raising, so a system
    that swallows the exception gains nothing by continuing — budget enforcement
    is a property of the harness, not a courtesy the candidate extends.
    """

    @property
    def current_extraction_question(self) -> str:
        """The frame reads are currently charged against. Host-controlled."""
        ...

    def query(self, route: str, probe: str) -> RouteOutcome:
        """Spend one route call. Raises `BudgetExhausted` when none remain."""
        ...

    def read(self, doc_id: str) -> ReadOutcome:
        """Spend one read of an already-retrieved document."""
        ...

    def declare_route_stop(self, route: str, reason: str) -> None:
        """Record abandoning one route. Never closes the task."""
        ...

    def spend(self, *, model_tokens: int = 0, tool_calls: int = 0) -> None:
        """Declare model/tool consumption so budgets stay matched across systems."""
        ...


class SystemUnderTest(Protocol):
    """ORION, every baseline and every ablation are exactly this."""

    system_id: str

    def run(
        self, view: PublicView, session: DiscoverySession, *, seed: int
    ) -> SystemReport: ...


__all__ = [
    "DiscoverySession",
    "ReadClassification",
    "ReadEvent",
    "ReadOutcome",
    "ResourceUse",
    "RetrievedRecord",
    "RouteEvent",
    "RouteOutcome",
    "StopDecision",
    "StopScope",
    "SystemReport",
    "SystemTrace",
    "SystemUnderTest",
    "TransportStatus",
]
