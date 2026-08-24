"""Interfaces for ORION-P2 systems under test. No implementations live here.

Every compared system — ORION, every baseline, every ablation — is exactly a
`SystemUnderTest`. It receives a `PublicView` and a `DiscoverySession`, never a
task, a world or a gold set, so the protocol's `hidden_labels` policy is enforced
by the signature rather than by discipline.

The custody split matters. A system returns a `SystemReport`: its claims, and
nothing else. The *record* of what it did — every route trial, every read
encounter, every stop decision, every unit of budget — is built host-side by the
session as those actions happen. A system therefore cannot under-report a route
it used, over-report a document it never retrieved, or edit its own trace after
the fact, which is what "candidate outputs cannot modify evaluator state" has to
mean in code.

Field names follow `STATISTICAL_PLAN_V1.json` `required_bindings` exactly, so the
analysis lane binds names rather than translating them.

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


#: O4: any of these opens an unavailability obligation on the route.
OBLIGATION_STATUSES: frozenset[str] = frozenset(
    {
        TransportStatus.RATE_LIMITED.value,
        TransportStatus.UNAVAILABLE.value,
        TransportStatus.TIMEOUT.value,
        TransportStatus.ERROR.value,
    }
)


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

    Deprecated: the vocabulary refactor (landed as #1078 from
    `claude/p2-harness-wip-refactor`) replaced read *classifications* with the
    plain-string `decision` field on `ReadOutcome`/`ReadEncounter`. This enum is
    restored verbatim from 2a692316 (pre-landing main) because the landing
    propagated the new `systems`/`gold` without migrating `runner.py` or the
    p2 test suite, leaving imports of this name broken. Do not build new code
    on it; migrate to the `decision` strings.
    """

    FIRST_READ = "FIRST_READ"
    DUPLICATE = "DUPLICATE"
    REVISION_REREAD = "REVISION_REREAD"
    NEW_QUESTION_REREAD = "NEW_QUESTION_REREAD"


@dataclass(frozen=True)
class ResourceUse:
    """Matched-budget accounting, in the plan's capped-resource currency."""

    wallclock_seconds: float = 0.0
    model_tokens: int = 0
    tool_calls: int = 0
    query_count: int = 0
    reads: int = 0

    def as_json(self) -> dict[str, Any]:
        return {
            "wallclock_seconds": self.wallclock_seconds,
            "model_tokens": self.model_tokens,
            "tool_calls": self.tool_calls,
            "query_count": self.query_count,
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
    """What one read returned. `decision` is the host's verdict, not a hint."""

    doc_id: str
    merged_source_id: str
    content_digest: str
    extraction_question: str
    extraction_schema: str
    decision: str
    text: str


@dataclass(frozen=True)
class Capture:
    """One work caught by a route trial (B4, B7).

    `merged_source_id` is the post-`merge_identities` primary key, never a raw
    retrieval id: two routes that found one paper under different locators must
    not look disjoint, which is the failure that inflates every overlap and
    coverage estimate built on top of them.
    """

    merged_source_id: str
    content_digest: str
    doc_id: str

    def as_json(self) -> dict[str, Any]:
        return {
            "merged_source_id": self.merged_source_id,
            "content_digest": self.content_digest,
            "doc_id": self.doc_id,
        }


@dataclass(frozen=True)
class RouteTrial:
    """Host record of one route call. Field names are the plan's `route_trial.*`."""

    index: int
    route_id: str
    attempt_index: int
    probe: str
    backend_identity: str
    query_derivation_identity: str
    transport_status: str
    consecutive_zero_novelty_before: int
    captures: tuple[Capture, ...]
    novel_merged_source_ids: tuple[str, ...]
    open_obligation_ids: tuple[str, ...]
    opened_obligation_id: str = ""
    probe_admissible: bool = True
    note: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "route_id": self.route_id,
            "attempt_index": self.attempt_index,
            "probe": self.probe,
            "backend_identity": self.backend_identity,
            "query_derivation_identity": self.query_derivation_identity,
            "transport_status": self.transport_status,
            "consecutive_zero_novelty_before": self.consecutive_zero_novelty_before,
            "captures": [item.as_json() for item in self.captures],
            "novel_merged_source_ids": list(self.novel_merged_source_ids),
            "open_obligation_ids": list(self.open_obligation_ids),
            "opened_obligation_id": self.opened_obligation_id,
            "probe_admissible": self.probe_admissible,
            "note": self.note,
        }


@dataclass(frozen=True)
class ReadEncounter:
    """One presentation of a work under a frame (B14, B15).

    The denominator O3 insists on. An execution-only denominator hides
    suppression: a system that silently refuses legitimate rereads never executes
    them, so they vanish from numerator and denominator together and the rate
    looks healthy. Recording the presentation is what makes the refusal visible.
    """

    index: int
    merged_source_id: str
    content_digest: str
    schema_version: str
    frame_id: str
    decision_before_execution: str
    executed: bool
    doc_id: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "merged_source_id": self.merged_source_id,
            "content_digest": self.content_digest,
            "schema_version": self.schema_version,
            "frame_id": self.frame_id,
            "decision_before_execution": self.decision_before_execution,
            "executed": self.executed,
            "doc_id": self.doc_id,
        }


@dataclass(frozen=True)
class RouteEvent:
    """Host record of one route call, in the order it happened.

    Deprecated: superseded by `RouteTrial` in the vocabulary refactor landed as
    #1078. Restored verbatim from 2a692316 (pre-landing main) because the
    landing propagated the new `systems`/`gold` without migrating `runner.py`
    or the p2 test suite, leaving imports of this name broken. Do not build new
    code on it; use `RouteTrial`.
    """

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
    """Host record of one read, keyed on the four coordinates a reread turns on.

    Deprecated: superseded by `ReadEncounter` in the vocabulary refactor landed
    as #1078. Restored verbatim from 2a692316 (pre-landing main) because the
    landing propagated the new `systems`/`gold` without migrating `runner.py`
    or the p2 test suite, leaving imports of this name broken. Do not build new
    code on it; use `ReadEncounter`.
    """

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
    route_id: str
    attempt_index: int
    reason: str
    declared: bool = False

    def as_json(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "scope": self.scope,
            "route_id": self.route_id,
            "attempt_index": self.attempt_index,
            "reason": self.reason,
            "declared": self.declared,
        }


@dataclass(frozen=True)
class SystemReport:
    """Everything a system returns. Claims only; the record of its actions is host-owned."""

    claimed_relevant_merged_source_ids: tuple[str, ...] = ()
    task_closed_as_complete: bool = False
    abstained: bool = False
    notes: str = ""


@dataclass(frozen=True)
class SystemTrace:
    """One system's full run on one task, assembled host-side."""

    task_id: str
    system_id: str
    seed: int
    repeat_index: int
    report: SystemReport
    route_trials: tuple[RouteTrial, ...] = ()
    read_encounters: tuple[ReadEncounter, ...] = ()
    stop_decisions: tuple[StopDecision, ...] = ()
    resources: ResourceUse = field(default_factory=ResourceUse)
    truncated_at_cap: str = ""
    error_class: str = ""
    unresolved_obligation_ids: tuple[str, ...] = ()

    @property
    def task_closure(self) -> dict[str, Any]:
        """B9. Distinguishes a declared closure from cap truncation."""

        declared = next(
            (
                item
                for item in self.stop_decisions
                if item.scope == StopScope.TASK.value and item.declared
            ),
            None,
        )
        return {
            "declared": declared is not None,
            "index": declared.index if declared else None,
            "wallclock_seconds": self.resources.wallclock_seconds,
            "truncated_at_cap": bool(self.truncated_at_cap),
            "truncating_resource": self.truncated_at_cap,
            "unresolved_obligation_ids": list(self.unresolved_obligation_ids),
        }

    def as_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "system_id": self.system_id,
            "seed": self.seed,
            "repeat_index": self.repeat_index,
            "claimed_relevant_merged_source_ids": list(
                self.report.claimed_relevant_merged_source_ids
            ),
            "task_closed_as_complete": self.report.task_closed_as_complete,
            "abstained": self.report.abstained,
            "route_trials": [item.as_json() for item in self.route_trials],
            "read_encounters": [item.as_json() for item in self.read_encounters],
            "stop_decisions": [item.as_json() for item in self.stop_decisions],
            "resources": self.resources.as_json(),
            "truncated_at_cap": self.truncated_at_cap,
            "error_class": self.error_class,
            "unresolved_obligation_ids": list(self.unresolved_obligation_ids),
            "notes": self.report.notes,
        }


class DiscoverySession(Protocol):
    """The only handle a system has on the world. Host-owned and recording.

    Every method call is metered and logged before it returns. Once a capped
    resource is spent the session stays closed and keeps raising, so a system that
    swallows the exception gains nothing by continuing — budget enforcement is a
    property of the harness, not a courtesy the candidate extends.
    """

    @property
    def current_extraction_question(self) -> str:
        """The frame reads are currently charged against. Host-controlled."""
        ...

    @property
    def current_extraction_schema(self) -> str:
        """The extraction schema version in force. Host-controlled."""
        ...

    def query(self, route: str, probe: str) -> RouteOutcome:
        """Spend one query. Raises `CapReached` when the cap is hit."""
        ...

    def read(self, doc_id: str) -> ReadOutcome:
        """Spend one tool call to extract from an already-retrieved document."""
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
    "Capture",
    "DiscoverySession",
    "OBLIGATION_STATUSES",
    "ReadClassification",
    "ReadEncounter",
    "ReadEvent",
    "ReadOutcome",
    "ResourceUse",
    "RetrievedRecord",
    "RouteEvent",
    "RouteOutcome",
    "RouteTrial",
    "StopDecision",
    "StopScope",
    "SystemReport",
    "SystemTrace",
    "SystemUnderTest",
    "TransportStatus",
]
