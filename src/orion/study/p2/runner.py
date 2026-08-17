"""Cap-enforcing executor for the ORION-P2 offline discovery study.

The session is the whole enforcement story. It hands out the only access a
system has to the world, meters every call against the frozen matched caps,
records what happened as it happens, and stays closed once a cap is reached. A
system that catches `CapReached` and keeps going gains nothing: the next call
raises again. Spend is charged against counters that only increment, never
against the length of a log the candidate could clear, and `gold` audits the
recorded run against the caps afterwards — the guarantee that survives Python
having no hard private attribute.

Failures are outcomes. `matched_budget_policy.cap_hit_rule` is explicit that a
capped run is RETAINED and scored as-is with `failure_class TRUNCATED_AT_CAP`,
and `exclusion_policy.retained_always` keeps candidate errors, timeouts,
abstentions, transport failures and cannot-check outcomes in the denominator.
Discarding a truncated run is forbidden.

Read encounters use ORION's own `decide_read`: oracle O3 names
`src/orion/knowledge/identity.py` as the mechanism source, so the metric is
defined as that function's output and reimplementing it would compute a
different quantity.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orion.knowledge.identity import (
    ReadReceipt,
    SourceIdentity,
    decide_read,
    merge_identities,
)

from .cases import PROTOCOL_TASK_FAMILY, Budget, DiscoveryTask
from .corpus import (
    ROUTE_SPEC_BY_ROUTE,
    DiscoveryRoute,
    DiscoveryWorld,
    Document,
    sha256_digest,
)
from .gold import EvaluationInputs, evaluate, evaluator_hash
from .systems import (
    OBLIGATION_STATUSES,
    Capture,
    ReadEncounter,
    ReadOutcome,
    ResourceUse,
    RetrievedRecord,
    RouteOutcome,
    RouteTrial,
    StopDecision,
    StopScope,
    SystemReport,
    SystemTrace,
    SystemUnderTest,
    TransportStatus,
)

RESULT_RECORD_SCHEMA_VERSION = "orion.publication-result-record.v1"
P2_PROTOCOL_ID = "P2.open-world-discovery.v1"
_HEX = set("0123456789abcdef")


class CapReached(RuntimeError):
    """Raised when an action would exceed a frozen matched cap."""

    def __init__(self, resource: str) -> None:
        super().__init__(f"cap reached: {resource}")
        self.resource = resource


def _as_record(document: Document) -> RetrievedRecord:
    """Project a corpus document down to what a system may see.

    `concept_tags` is dropped here. It is the relevance rule; handing it over as
    a structured field would be handing over the gold.
    """

    return RetrievedRecord(
        doc_id=document.doc_id,
        content_identity=document.content_identity,
        content_digest=document.content_digest,
        version=document.version,
        title=document.title,
        abstract=document.abstract,
        venue=document.venue,
        year=document.year,
        authors=document.authors,
        references=document.references,
    )


def merged_source_ids(identities: Iterable[str]) -> dict[str, str]:
    """Map each content identity to its post-`merge_identities` primary key.

    B4 forbids raw retrieval ids. The world already keys works by content
    identity, but running the repository's own merge over them is what makes the
    emitted key the *same object* the rest of ORION means by a source — and a
    test asserts the two groupings agree, so a divergence fails loudly rather
    than silently shifting every oracle id.
    """

    ordered = tuple(sorted(set(identities)))
    merged = merge_identities(tuple(SourceIdentity(source_id=item) for item in ordered))
    mapping: dict[str, str] = {}
    for identity in merged:
        for key in sorted(identity.keys):
            mapping[key] = identity.source_id
    return {item: mapping.get(item, item) for item in ordered}


@dataclass(frozen=True)
class PublicIndex:
    """The world as a system may encounter it: records and reachability, no labels.

    Built once per run and handed to the session *instead of* the world. Python
    offers no hard private attribute, so custody has to be arranged rather than
    declared: if the session never holds a `DiscoveryWorld`, then no amount of
    poking at the session's internals reaches `Document.concept_tags`, which is
    the relevance rule, or `DiscoveryTask.protected_gold`, which is the answer.
    """

    records: tuple[tuple[str, RetrievedRecord], ...]
    postings: tuple[tuple[str, str, tuple[str, ...]], ...]
    merged: tuple[tuple[str, str], ...]

    @property
    def by_id(self) -> dict[str, RetrievedRecord]:
        return dict(self.records)

    @property
    def merged_of(self) -> dict[str, str]:
        return dict(self.merged)

    def lookup(self, route: str, probe: str) -> tuple[RetrievedRecord, ...]:
        by_id = self.by_id
        for name, key, doc_ids in self.postings:
            if name == route and key == probe:
                return tuple(by_id[item] for item in doc_ids if item in by_id)
        return ()


def build_public_index(world: DiscoveryWorld) -> PublicIndex:
    """Project a world into the label-free index a session may expose."""

    records = tuple(
        (item.doc_id, _as_record(item))
        for item in sorted(world.documents, key=lambda doc: doc.doc_id)
    )
    postings: list[tuple[str, str, tuple[str, ...]]] = []
    for route in DiscoveryRoute:
        for probe in world.probes_for(route):
            doc_ids = tuple(item.doc_id for item in world.lookup(route, probe))
            if doc_ids:
                postings.append((route.value, probe, doc_ids))
    mapping = merged_source_ids(item.content_identity for item in world.documents)
    return PublicIndex(
        records=records,
        postings=tuple(sorted(postings)),
        merged=tuple(sorted(mapping.items())),
    )


@dataclass(frozen=True)
class SessionConfig:
    """Everything the session needs to enforce a task. Deliberately gold-free."""

    task_id: str
    availability: tuple[Any, ...]
    budget: Budget
    extraction_questions: tuple[str, ...]
    extraction_schemas: tuple[str, ...]
    extraction_shift_after_reads: int | None

    @classmethod
    def from_task(cls, task: DiscoveryTask) -> SessionConfig:
        return cls(
            task_id=task.task_id,
            availability=task.availability,
            budget=task.budget,
            extraction_questions=task.extraction_questions,
            extraction_schemas=task.extraction_schemas,
            extraction_shift_after_reads=task.extraction_shift_after_reads,
        )

    def availability_for(self, route: DiscoveryRoute) -> Any:
        for item in self.availability:
            if item.route is route:
                return item
        return None


class BudgetedSession:
    """Host-owned, metered, recording access to the world for exactly one run."""

    def __init__(
        self,
        index: PublicIndex,
        config: SessionConfig,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._index = index
        self._task = config
        self._clock = clock
        self._started = clock()
        self._sequence = 0
        self._route_attempts: dict[str, int] = {}
        self._zero_novelty: dict[str, int] = {}
        self._route_trials: list[RouteTrial] = []
        self._encounters: list[ReadEncounter] = []
        self._stop_decisions: list[StopDecision] = []
        self._seen_identities: set[str] = set()
        self._retrieved_doc_ids: set[str] = set()
        self._receipts: list[ReadReceipt] = []
        self._open_obligations: dict[str, str] = {}
        self._resolved_obligations: set[str] = set()
        # Spend is charged against counters that only ever increment, never
        # against the length of a log a candidate could clear.
        self.__queries_made = 0
        self.__reads_made = 0
        self.__model_tokens = 0
        self.__tool_calls = 0
        self.__capped = ""

    # -- state a system may observe -------------------------------------

    @property
    def _stage(self) -> int:
        shift = self._task.extraction_shift_after_reads
        if shift is None:
            return 0
        return len(self._receipts) // shift

    @property
    def current_extraction_question(self) -> str:
        questions = self._task.extraction_questions
        return questions[min(self._stage, len(questions) - 1)]

    @property
    def current_extraction_schema(self) -> str:
        schemas = self._task.extraction_schemas
        return schemas[min(self._stage, len(schemas) - 1)]

    # -- host-side accessors (never exposed through the Protocol) --------

    @property
    def route_trials(self) -> tuple[RouteTrial, ...]:
        return tuple(self._route_trials)

    @property
    def read_encounters(self) -> tuple[ReadEncounter, ...]:
        return tuple(self._encounters)

    @property
    def stop_decisions(self) -> tuple[StopDecision, ...]:
        return tuple(self._stop_decisions)

    @property
    def capped_resource(self) -> str:
        return self.__capped

    @property
    def unresolved_obligation_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._open_obligations))

    @property
    def resources(self) -> ResourceUse:
        return ResourceUse(
            wallclock_seconds=max(0.0, self._clock() - self._started),
            model_tokens=self.__model_tokens,
            tool_calls=self.__tool_calls,
            query_count=self.__queries_made,
            reads=self.__reads_made,
        )

    # -- enforcement ----------------------------------------------------

    def _charge(self, resource: str, current: int | float, ceiling: int | float) -> None:
        """Refuse the action, and stay refusing. A reached cap is terminal."""

        if self.__capped:
            raise CapReached(self.__capped)
        elapsed = self._clock() - self._started
        if elapsed > self._task.budget.wallclock_seconds:
            self.__capped = "wallclock_seconds"
            raise CapReached(self.__capped)
        if current >= ceiling:
            self.__capped = resource
            raise CapReached(resource)

    def _next_index(self) -> int:
        """Monotone position in the run timeline. Oracles replay against it."""

        self._sequence += 1
        return self._sequence

    # -- the system-facing surface --------------------------------------

    def query(self, route: str, probe: str) -> RouteOutcome:
        self._charge("query_count", self.__queries_made, self._task.budget.query_count)
        self.__queries_made += 1
        try:
            kind = DiscoveryRoute(route)
        except ValueError:
            return self._record_trial(route, probe, TransportStatus.ERROR, (), "unknown_route", admissible=False)

        used = self._route_attempts.get(route, 0)
        availability = self._task.availability_for(kind)

        if availability is not None and availability.goes_unavailable_after_calls is not None:
            if used >= availability.goes_unavailable_after_calls:
                # A dead provider censors what it held. Under O4 this opens an
                # obligation; it does not report that nothing is there.
                return self._record_trial(route, probe, TransportStatus.UNAVAILABLE, (), "provider_down")

        if kind is DiscoveryRoute.CITATION and probe not in self._retrieved_doc_ids:
            # An inadmissible probe is not a transport failure, so it must not
            # open an unavailability obligation — that would let a system
            # manufacture CANNOT_CHECK outcomes by chaining from nothing.
            return self._record_trial(
                route, probe, TransportStatus.ERROR, (), "citation_seed_not_retrieved", admissible=False
            )

        documents = self._index.lookup(route, probe)

        if availability is not None and availability.goes_flat_after_calls is not None:
            if used >= availability.goes_flat_after_calls:
                # Exhaustion: the route answers, and has nothing new to say.
                return self._record_trial(route, probe, TransportStatus.OK, (), "route_flat")

        return self._record_trial(route, probe, TransportStatus.OK, documents, "")

    def _record_trial(
        self,
        route: str,
        probe: str,
        status: TransportStatus,
        documents: tuple[RetrievedRecord, ...],
        note: str,
        *,
        admissible: bool = True,
    ) -> RouteOutcome:
        attempt_index = self._route_attempts.get(route, 0)
        self._route_attempts[route] = attempt_index + 1
        merged_of = self._index.merged_of

        captures = tuple(
            Capture(
                merged_source_id=merged_of.get(item.content_identity, item.content_identity),
                content_digest=item.content_digest,
                doc_id=item.doc_id,
            )
            for item in sorted(documents, key=lambda record: record.doc_id)
        )
        identities = tuple(sorted({item.merged_source_id for item in captures}))
        novel = tuple(sorted(set(identities) - self._seen_identities))

        spec = ROUTE_SPEC_BY_ROUTE.get(
            DiscoveryRoute(route) if route in {item.value for item in DiscoveryRoute} else DiscoveryRoute.LEXICAL
        )
        derivation = spec.query_derivation_identity if spec else "unknown"
        backend = spec.backend_identity if spec else "unknown"

        # O4 obligations. A non-OK transport opens one; a later successful trial
        # on the same route and query derivation resolves it.
        opened = ""
        obligation_key = f"{route}:{derivation}"
        if status.value in OBLIGATION_STATUSES and admissible:
            opened = f"{obligation_key}@{attempt_index}"
            self._open_obligations[opened] = obligation_key
        elif status is TransportStatus.OK:
            for identifier, key in sorted(self._open_obligations.items()):
                if key == obligation_key:
                    self._resolved_obligations.add(identifier)
            self._open_obligations = {
                identifier: key
                for identifier, key in self._open_obligations.items()
                if key != obligation_key
            }

        # B3, in the currency of FrozenRouteControlPolicy: consecutive attempts
        # that succeeded at transport and returned nothing new. Read *before* this
        # attempt updates it, which is what the binding asks for.
        before = self._zero_novelty.get(route, 0)
        if status is TransportStatus.OK and admissible:
            self._zero_novelty[route] = 0 if novel else before + 1
        elif status is not TransportStatus.OK:
            # A failed or unavailable trial is not evidence of flatness.
            self._zero_novelty[route] = before

        self._seen_identities.update(identities)
        self._retrieved_doc_ids.update(item.doc_id for item in captures)

        self._route_trials.append(
            RouteTrial(
                index=self._next_index(),
                route_id=route,
                attempt_index=attempt_index,
                probe=probe,
                backend_identity=backend,
                query_derivation_identity=derivation,
                transport_status=status.value,
                consecutive_zero_novelty_before=before,
                captures=captures,
                novel_merged_source_ids=novel,
                open_obligation_ids=tuple(sorted(self._open_obligations)),
                opened_obligation_id=opened,
                probe_admissible=admissible,
                note=note,
            )
        )
        # Every presentation is a read encounter, whether or not a read follows.
        for record in sorted(documents, key=lambda item: item.doc_id):
            self._record_encounter(record, executed=False)
        return RouteOutcome(route=route, probe=probe, status=status, records=documents, note=note)

    def _record_encounter(self, record: RetrievedRecord, *, executed: bool) -> ReadEncounter:
        merged = self._index.merged_of.get(record.content_identity, record.content_identity)
        question = self.current_extraction_question
        schema = self.current_extraction_schema
        decision = decide_read(
            merged, record.content_digest, schema, question, tuple(self._receipts)
        )
        encounter = ReadEncounter(
            index=self._next_index(),
            merged_source_id=merged,
            content_digest=record.content_digest,
            schema_version=schema,
            frame_id=question,
            decision_before_execution=decision.value,
            executed=executed,
            doc_id=record.doc_id,
        )
        self._encounters.append(encounter)
        return encounter

    def read(self, doc_id: str) -> ReadOutcome:
        self._charge("tool_calls", self.__tool_calls, self._task.budget.tool_calls)
        if doc_id not in self._retrieved_doc_ids:
            raise ValueError(f"{doc_id} has not been retrieved by any route")
        record = self._index.by_id[doc_id]
        merged = self._index.merged_of.get(record.content_identity, record.content_identity)
        question = self.current_extraction_question
        schema = self.current_extraction_schema
        decision = decide_read(
            merged, record.content_digest, schema, question, tuple(self._receipts)
        )

        # Mark the most recent matching unexecuted presentation as executed. If
        # the frame or schema moved since the document was presented, no
        # presentation matches — reading it now is a genuinely different
        # encounter, so it gets its own record rather than back-dating an old one.
        matched = False
        for position in range(len(self._encounters) - 1, -1, -1):
            candidate = self._encounters[position]
            if candidate.executed:
                continue
            if (
                candidate.merged_source_id == merged
                and candidate.content_digest == record.content_digest
                and candidate.schema_version == schema
                and candidate.frame_id == question
            ):
                self._encounters[position] = ReadEncounter(
                    index=candidate.index,
                    merged_source_id=candidate.merged_source_id,
                    content_digest=candidate.content_digest,
                    schema_version=candidate.schema_version,
                    frame_id=candidate.frame_id,
                    decision_before_execution=candidate.decision_before_execution,
                    executed=True,
                    doc_id=candidate.doc_id,
                )
                matched = True
                break
        if not matched:
            self._record_encounter(record, executed=True)

        self.__reads_made += 1
        self.__tool_calls += 1
        self._receipts.append(
            ReadReceipt(
                source_id=merged,
                content_digest=record.content_digest,
                schema_version=schema,
                frame_id=question,
            )
        )
        return ReadOutcome(
            doc_id=doc_id,
            merged_source_id=merged,
            content_digest=record.content_digest,
            extraction_question=question,
            extraction_schema=schema,
            decision=decision.value,
            text=f"{record.title}\n\n{record.abstract}",
        )

    def declare_route_stop(self, route: str, reason: str) -> None:
        self._stop_decisions.append(
            StopDecision(
                index=self._next_index(),
                scope=StopScope.ROUTE.value,
                route_id=route,
                attempt_index=max(0, self._route_attempts.get(route, 0) - 1),
                reason=reason,
                declared=True,
            )
        )

    def spend(self, *, model_tokens: int = 0, tool_calls: int = 0) -> None:
        self._charge(
            "model_tokens", self.__model_tokens + model_tokens, self._task.budget.model_tokens
        )
        self._charge("tool_calls", self.__tool_calls + tool_calls, self._task.budget.tool_calls)
        self.__model_tokens += max(0, model_tokens)
        self.__tool_calls += max(0, tool_calls)

    def record_task_stop(self, *, reason: str, declared: bool) -> None:
        """Host-invoked at the end of a run so closure carries a timeline position."""

        self._stop_decisions.append(
            StopDecision(
                index=self._next_index(),
                scope=StopScope.TASK.value,
                route_id="",
                attempt_index=-1,
                reason=reason,
                declared=declared,
            )
        )


@dataclass(frozen=True)
class RunOutcome:
    """One executed (system, task, seed) cell: the record, and the artifact it hashes."""

    record: dict[str, Any]
    artifact: dict[str, Any]
    trace: SystemTrace

    @property
    def artifact_hash(self) -> str:
        return sha256_digest(self.artifact)


def execute(
    system: SystemUnderTest,
    world: DiscoveryWorld,
    task: DiscoveryTask,
    *,
    seed: int,
    run_manifest_hash: str,
    repeat_index: int = 0,
    caps: Budget | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> RunOutcome:
    """Run one system on one task once, and normalize the outcome.

    `run_manifest_hash` is supplied by the caller rather than minted here. A run
    manifest binds a subject revision, provider revisions and evaluator hash; none
    of those exist while the world is outcome-blind, and manufacturing one would
    assert bindings that were never made.

    `caps` likewise overrides the suite's reference budget, because the plan makes
    caps a property of the run manifest derived from a pilot, not a property of
    the corpus. The frozen reference cap exists so the world's difficulty is a
    checkable property before any pilot has been run.
    """

    if len(run_manifest_hash) != 64 or not set(run_manifest_hash) <= _HEX:
        raise ValueError("run_manifest_hash must be a lowercase SHA-256 hex digest")

    config = SessionConfig.from_task(task)
    if caps is not None:
        config = SessionConfig(
            task_id=config.task_id,
            availability=config.availability,
            budget=caps,
            extraction_questions=config.extraction_questions,
            extraction_schemas=config.extraction_schemas,
            extraction_shift_after_reads=config.extraction_shift_after_reads,
        )

    session = BudgetedSession(build_public_index(world), config, clock=clock)
    error_class = ""
    try:
        report = system.run(task.public_view, session, seed=seed)
    except CapReached:
        report = SystemReport(notes="run truncated at a matched cap")
    except Exception as exc:  # noqa: BLE001 - a crashing candidate is an outcome
        error_class = type(exc).__name__
        report = SystemReport(notes=f"candidate raised {error_class}")

    truncated = session.capped_resource
    # cap_hit_rule: a truncated task did not declare closure. Recording it as a
    # closure would let truncation be scored as safe stopping.
    declared = report.task_closed_as_complete and not truncated
    session.record_task_stop(
        reason="declared_closure"
        if declared
        else ("truncated_at_cap" if truncated else ("candidate_error" if error_class else "run_ended")),
        declared=declared,
    )

    trace = SystemTrace(
        task_id=task.task_id,
        system_id=system.system_id,
        seed=seed,
        repeat_index=repeat_index,
        report=report,
        route_trials=session.route_trials,
        read_encounters=session.read_encounters,
        stop_decisions=session.stop_decisions,
        resources=session.resources,
        truncated_at_cap=truncated,
        error_class=error_class,
        unresolved_obligation_ids=session.unresolved_obligation_ids,
    )

    evaluation = evaluate(EvaluationInputs(world=world, task=task, trace=trace, caps=config.budget))
    artifact = {
        "schema_version": "orion.p2.run-artifact.v2",
        "task_id": task.task_id,
        "case_family": task.case_family.value,
        "system_id": system.system_id,
        "seed": seed,
        "repeat_index": repeat_index,
        "trace": trace.as_json(),
        "route_trials": [item.as_json() for item in trace.route_trials],
        "read_encounters": [item.as_json() for item in trace.read_encounters],
        "task_closure": trace.task_closure,
        "oracle": evaluation.oracle_block(),
        "evaluation": evaluation.as_json(),
    }
    record = {
        "schema_version": RESULT_RECORD_SCHEMA_VERSION,
        "paper_id": "P2",
        "protocol_id": P2_PROTOCOL_ID,
        "run_manifest_hash": run_manifest_hash,
        "result_id": f"{system.system_id}:{task.task_id}:{repeat_index}:{seed}",
        "system_id": system.system_id,
        "task_id": task.task_id,
        "task_family": PROTOCOL_TASK_FAMILY,
        "seed": seed,
        "status": evaluation.status,
        "metrics": evaluation.numeric_metrics(),
        "cost": {
            "wallclock_seconds": trace.resources.wallclock_seconds,
            "model_tokens": float(trace.resources.model_tokens),
            "tool_calls": float(trace.resources.tool_calls),
            "query_count": float(trace.resources.query_count),
        },
        "failure_class": evaluation.failure_class,
        "raw_artifact_hash": sha256_digest(artifact),
        "authority_flags": evaluation.authority_flags(),
        "contamination": {
            # B13. A synthetic offline world has no search-time contamination
            # surface: nothing is fetched, so no benchmark answer can leak in.
            "evaluator_hash": evaluator_hash(),
            "contamination_flagged": False,
            "contamination_evidence": "offline synthetic world; no external retrieval performed",
        },
        "repeat_index": repeat_index,
        "notes": task.case_family.value,
    }
    return RunOutcome(record=record, artifact=artifact, trace=trace)


def run_suite(
    system: SystemUnderTest,
    world: DiscoveryWorld,
    tasks: Iterable[DiscoveryTask],
    *,
    seeds: tuple[int, ...],
    run_manifest_hash: str,
    caps: Budget | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> Iterator[RunOutcome]:
    """Every task, every repeat, in a fixed order. Repeats nest, never pool."""

    if not seeds:
        raise ValueError("at least one seed is required")
    for task in sorted(tasks, key=lambda item: item.task_id):
        for repeat_index, seed in enumerate(seeds):
            yield execute(
                system,
                world,
                task,
                seed=seed,
                repeat_index=repeat_index,
                run_manifest_hash=run_manifest_hash,
                caps=caps,
                clock=clock,
            )


def write_records(outcomes: Iterable[RunOutcome], path: Path) -> int:
    """Write normalized records as JSONL. Returns the number written."""

    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for outcome in outcomes:
            handle.write(json.dumps(outcome.record, sort_keys=True, ensure_ascii=False) + "\n")
            count += 1
    return count


def write_artifacts(outcomes: Iterable[RunOutcome], root: Path) -> tuple[Path, ...]:
    """Write the rich per-run artifacts the records' `raw_artifact_hash` addresses."""

    root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for outcome in outcomes:
        target = root / f"{outcome.record['result_id'].replace(':', '__')}.json"
        target.write_text(
            json.dumps(outcome.artifact, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(target)
    return tuple(written)


__all__ = [
    "BudgetedSession",
    "CapReached",
    "P2_PROTOCOL_ID",
    "PublicIndex",
    "RESULT_RECORD_SCHEMA_VERSION",
    "RunOutcome",
    "SessionConfig",
    "build_public_index",
    "execute",
    "merged_source_ids",
    "run_suite",
    "write_artifacts",
    "write_records",
]
