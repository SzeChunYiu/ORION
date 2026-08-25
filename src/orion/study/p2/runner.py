"""Budget-enforcing executor for the ORION-P2 offline discovery study.

The session is the whole enforcement story. It hands out the only access a
system has to the world, meters every call against the task's frozen budget,
records what happened as it happens, and stays closed once a budget dimension is
spent. A system that catches `BudgetExhausted` and keeps going gains nothing: the
next call raises again. Enforcement is a property of the harness rather than a
courtesy the candidate extends.

Failures are outcomes. A budget-exhausted run, a crashed system, a timeout and an
abstention all produce records; none are dropped. `ANALYSIS_STANDARD_V1` is
explicit that candidate-caused failures stay in the denominator, and a harness
that quietly retries or discards them would make every rate it reports optimistic.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .cases import DiscoveryTask, PROTOCOL_TASK_FAMILY
from .corpus import (
    ROUTE_SPEC_BY_ROUTE,
    DiscoveryRoute,
    DiscoveryWorld,
    Document,
    sha256_digest,
)
from .gold import EvaluationInputs, evaluate
from .systems import (
    Capture,
    ReadClassification,
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


class BudgetExhausted(RuntimeError):
    """Raised when an action would exceed a frozen budget dimension."""

    def __init__(self, dimension: str) -> None:
        super().__init__(f"budget exhausted: {dimension}")
        self.dimension = dimension


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

    @property
    def by_id(self) -> dict[str, RetrievedRecord]:
        return dict(self.records)

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
    return PublicIndex(records=records, postings=tuple(sorted(postings)))


@dataclass(frozen=True)
class SessionConfig:
    """Everything the session needs to enforce a task. Deliberately gold-free."""

    task_id: str
    availability: tuple[Any, ...]
    budget: Any
    extraction_questions: tuple[str, ...]
    extraction_shift_after_reads: int | None
    #: The extraction schema version in force. Host-controlled, as the
    #: DiscoverySession protocol requires. DiscoveryTask does not carry one, so
    #: it defaults here rather than being invented per call site.
    extraction_schema: str = "P2.Extraction.v1"

    @classmethod
    def from_task(cls, task: DiscoveryTask) -> SessionConfig:
        return cls(
            task_id=task.task_id,
            availability=task.availability,
            budget=task.budget,
            extraction_questions=task.extraction_questions,
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
        self._route_calls: dict[str, int] = {}
        self._route_trials: list[RouteTrial] = []
        self._read_encounters: list[ReadEncounter] = []
        # Post-#1078 trial state. The semantics are taken from the working
        # implementation in baselines.py rather than invented here: attempts
        # count per route, the zero-novelty run advances only when a route
        # ANSWERED and returned nothing new, and a non-OK transport opens an
        # obligation keyed "<route>:<attempt_index>".
        self._route_attempts: dict[str, int] = {}
        self._route_zero_novelty: dict[str, int] = {}
        self._open_obligations: dict[str, str] = {}
        self._stop_decisions: list[StopDecision] = []
        self._seen_identities: set[str] = set()
        self._retrieved_doc_ids: set[str] = set()
        self._read_keys: set[tuple[str, str, str]] = set()
        self._read_identity_digests: set[tuple[str, str]] = set()
        # Spend is charged against monotone counters that only ever increment,
        # never against `len(self._route_trials)`. The event log is an ordinary
        # list, so charging against its length let a system clear the log and
        # keep querying forever — the budget was enforced against a number the
        # candidate could edit. These are name-mangled, which is obfuscation and
        # not a boundary; the guarantee is the post-run overrun check in
        # `gold._status_and_failure`, which compares the recorded event count
        # against the frozen budget and voids any run that exceeded it.
        self.__route_calls_made = 0
        self.__reads_made = 0
        self.__model_tokens = 0
        self.__tool_calls = 0
        self.__exhausted = ""

    @property
    def current_extraction_question(self) -> str:
        """The active frame, advanced by the host after the frozen number of reads."""

        shift = self._task.extraction_shift_after_reads
        questions = self._task.extraction_questions
        if shift is None or len(questions) < 2:
            return questions[0]
        stage = min(len(self._read_encounters) // shift, len(questions) - 1)
        return questions[stage]

    @property
    def current_extraction_schema(self) -> str:
        """The extraction schema version in force.

        Required by the DiscoverySession protocol. BudgetedSession did not
        implement it, so any read that recorded the schema raised
        AttributeError -- the protocol declared a member no implementation
        provided, and nothing checked.
        """

        return self._task.extraction_schema

    @property
    def open_obligations(self) -> tuple[str, ...]:
        """Obligations still open when the run ended.

        An obligation opens when a provider did not answer. One still open at
        the end means the run finished without ever learning what that provider
        held, which is exactly what must not be reported as absence.
        """

        return tuple(sorted(self._open_obligations))

    @property
    def route_trials(self) -> tuple[RouteTrial, ...]:
        return tuple(self._route_trials)

    @property
    def read_encounters(self) -> tuple[ReadEncounter, ...]:
        return tuple(self._read_encounters)

    @property
    def stop_decisions(self) -> tuple[StopDecision, ...]:
        return tuple(self._stop_decisions)

    @property
    def exhausted_dimension(self) -> str:
        return self.__exhausted

    @property
    def resources(self) -> ResourceUse:
        return ResourceUse(
            wallclock_seconds=max(0.0, self._clock() - self._started),
            model_tokens=self.__model_tokens,
            tool_calls=self.__tool_calls,
            query_count=self.__route_calls_made,
            reads=self.__reads_made,
        )

    def _charge(self, dimension: str, current: int | float, ceiling: int | float) -> None:
        """Refuse the action, and stay refusing. Exhaustion is terminal by design."""

        if self.__exhausted:
            raise BudgetExhausted(self.__exhausted)
        elapsed = self._clock() - self._started
        if elapsed > self._task.budget.max_wallclock_seconds:
            self.__exhausted = "wallclock_seconds"
            raise BudgetExhausted(self.__exhausted)
        if current >= ceiling:
            self.__exhausted = dimension
            raise BudgetExhausted(dimension)

    def _next_index(self) -> int:
        """Monotone position in the run timeline. Stop audits replay against it."""

        self._sequence += 1
        return self._sequence

    def query(self, route: str, probe: str) -> RouteOutcome:
        self._charge("route_calls", self.__route_calls_made, self._task.budget.max_route_calls)
        self.__route_calls_made += 1
        try:
            kind = DiscoveryRoute(route)
        except ValueError:
            return self._record_route(route, probe, TransportStatus.ERROR, (), "unknown_route")

        used = self._route_calls.get(route, 0)
        self._route_calls[route] = used + 1
        availability = self._task.availability_for(kind)

        if availability is not None and availability.goes_unavailable_after_calls is not None:
            if used >= availability.goes_unavailable_after_calls:
                return self._record_route(route, probe, TransportStatus.UNAVAILABLE, (), "provider_down")

        if kind is DiscoveryRoute.CITATION and probe not in self._retrieved_doc_ids:
            return self._record_route(route, probe, TransportStatus.ERROR, (), "citation_seed_not_retrieved")

        documents = self._index.lookup(route, probe)

        if availability is not None and availability.goes_flat_after_calls is not None:
            if used >= availability.goes_flat_after_calls:
                return self._record_route(route, probe, TransportStatus.OK, (), "route_flat")

        return self._record_route(route, probe, TransportStatus.OK, documents, "")

    def _record_route(
        self,
        route: str,
        probe: str,
        status: TransportStatus,
        documents: tuple[RetrievedRecord, ...],
        note: str,
    ) -> RouteOutcome:
        identities = tuple(sorted({item.content_identity for item in documents}))
        novel = tuple(sorted(set(identities) - self._seen_identities))
        self._seen_identities.update(identities)
        self._retrieved_doc_ids.update(item.doc_id for item in documents)
        spec = ROUTE_SPEC_BY_ROUTE.get(DiscoveryRoute(route)) if route in {
            item.value for item in DiscoveryRoute
        } else None
        attempt_index = self._route_attempts.get(route, 0)
        zero_novelty_before = self._route_zero_novelty.get(route, 0)
        self._route_attempts[route] = attempt_index + 1

        opened_obligation_id = ""
        if status is TransportStatus.OK:
            # Only an ANSWERED route can extend a zero-novelty run. A route that
            # did not answer has said nothing about novelty either way.
            self._route_zero_novelty[route] = 0 if novel else zero_novelty_before + 1
        else:
            # A provider that did not answer censors what it holds. Recording an
            # obligation is what stops the run treating silence as absence.
            opened_obligation_id = f"{route}:{attempt_index}"
            self._open_obligations[opened_obligation_id] = status.value
            self._route_zero_novelty[route] = zero_novelty_before

        self._route_trials.append(
            RouteTrial(
                index=self._next_index(),
                route_id=route,
                attempt_index=attempt_index,
                probe=probe,
                backend_identity=spec.backend_identity if spec else "unknown",
                query_derivation_identity=spec.query_derivation_identity if spec else "unknown",
                transport_status=status.value,
                consecutive_zero_novelty_before=zero_novelty_before,
                captures=tuple(
                    Capture(
                        merged_source_id=item.content_identity,
                        content_digest=item.content_digest,
                        doc_id=item.doc_id,
                    )
                    for item in documents
                ),
                novel_merged_source_ids=novel,
                open_obligation_ids=tuple(sorted(self._open_obligations)),
                opened_obligation_id=opened_obligation_id,
                note=note,
            )
        )
        return RouteOutcome(
            route=route,
            probe=probe,
            status=status,
            records=documents,
            note=note,
        )

    def read(self, doc_id: str) -> ReadOutcome:
        self._charge("reads", self.__reads_made, self._task.budget.max_reads)
        if doc_id not in self._retrieved_doc_ids:
            raise ValueError(f"{doc_id} has not been retrieved by any route")
        self.__reads_made += 1
        document = self._index.by_id[doc_id]
        question = self.current_extraction_question
        classification = self._classify_read(document, question)
        self._read_keys.add((document.content_identity, document.content_digest, question))
        self._read_identity_digests.add((document.content_identity, document.content_digest))
        self._read_encounters.append(
            ReadEncounter(
                index=self._next_index(),
                merged_source_id=document.content_identity,
                content_digest=document.content_digest,
                schema_version=self.current_extraction_schema,
                frame_id=question,
                # Computed BEFORE the read is registered above, which is what
                # makes it a decision *before execution* rather than after.
                decision_before_execution=classification.value,
                executed=True,
                doc_id=doc_id,
            )
        )
        return ReadOutcome(
            doc_id=doc_id,
            # post-#1078 names: the record's identity is the merged source it
            # resolves to, and the host's verdict is a decision, not a
            # classification. Renames only; the values are unchanged.
            merged_source_id=document.content_identity,
            content_digest=document.content_digest,
            extraction_question=question,
            extraction_schema=self.current_extraction_schema,
            decision=classification.value,
            text=f"{document.title}\n\n{document.abstract}",
        )

    def _classify_read(self, document: RetrievedRecord, question: str) -> ReadClassification:
        """Classify independently of the subsystem under test."""

        key = (document.content_identity, document.content_digest, question)
        if key in self._read_keys:
            return ReadClassification.DUPLICATE
        identity_seen = any(
            identity == document.content_identity
            for identity, _ in self._read_identity_digests
        )
        if not identity_seen:
            return ReadClassification.FIRST_READ
        if (document.content_identity, document.content_digest) not in self._read_identity_digests:
            return ReadClassification.REVISION_REREAD
        return ReadClassification.NEW_QUESTION_REREAD

    def declare_route_stop(self, route: str, reason: str) -> None:
        self._stop_decisions.append(
            StopDecision(
                index=self._next_index(),
                scope=StopScope.ROUTE.value,
                route_id=route,
                # how many times this route had already been called when the
                # system gave up on it; the oracle needs it to tell an early
                # abandonment from one taken after genuine attempts
                attempt_index=self._route_calls.get(route, 0),
                reason=reason,
                declared=False,
            )
        )

    def spend(self, *, model_tokens: int = 0, tool_calls: int = 0) -> None:
        self._charge(
            "model_tokens", self.__model_tokens + model_tokens, self._task.budget.max_model_tokens
        )
        self._charge(
            "tool_calls", self.__tool_calls + tool_calls, self._task.budget.max_tool_calls
        )
        self.__model_tokens += max(0, model_tokens)
        self.__tool_calls += max(0, tool_calls)

    def record_task_stop(self, *, reason: str, claimed_complete: bool) -> None:
        """Host-invoked at the end of a run so task closure carries a timeline position."""

        self._stop_decisions.append(
            StopDecision(
                index=self._next_index(),
                scope=StopScope.TASK.value,
                route_id="",
                attempt_index=0,
                reason=reason,
                declared=claimed_complete,
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
    clock: Callable[[], float] = time.monotonic,
    index: PublicIndex | None = None,
    repeat_index: int = 0,
) -> RunOutcome:
    """Run one system on one task once, and normalize the outcome.

    `run_manifest_hash` is supplied by the caller rather than minted here. A run
    manifest binds a subject revision, provider revisions and evaluator hash; none
    of those exist while the world is outcome-blind and no system is configured,
    and manufacturing one would be asserting bindings that were never made.

    `index` is an optional host-built, label-free projection of `world`. Supplying
    it only avoids rebuilding the same pure public index across a batch; systems
    still receive only the `BudgetedSession`, never the world or protected gold.
    """

    if len(run_manifest_hash) != 64 or not set(run_manifest_hash) <= _HEX:
        raise ValueError("run_manifest_hash must be a lowercase SHA-256 hex digest")

    public_index = build_public_index(world) if index is None else index
    session = BudgetedSession(public_index, SessionConfig.from_task(task), clock=clock)
    error_class = ""
    try:
        report = system.run(task.public_view, session, seed=seed)
    except BudgetExhausted:
        report = SystemReport(notes="run terminated by budget enforcement")
    except Exception as exc:  # noqa: BLE001 - a crashing candidate is an outcome
        error_class = type(exc).__name__
        report = SystemReport(notes=f"candidate raised {error_class}")

    session.record_task_stop(
        reason="run_complete" if not error_class else "candidate_error",
        claimed_complete=report.task_closed_as_complete,
    )

    trace = SystemTrace(
        task_id=task.task_id,
        system_id=system.system_id,
        seed=seed,
        # The sweep runs every task against every seed and its own docstring
        # says repeats are nested, never pooled -- so a repeat IS a seed's
        # position in that tuple, and the sweep passes it. A single execute()
        # call is repeat 0 of one.
        repeat_index=repeat_index,
        report=report,
        route_trials=session.route_trials,
        read_encounters=session.read_encounters,
        stop_decisions=session.stop_decisions,
        resources=session.resources,
        truncated_at_cap=session.exhausted_dimension,
        error_class=error_class,
        unresolved_obligation_ids=tuple(sorted(session.open_obligations)),
    )

    # EvaluationInputs requires caps; omitting it raised TypeError. The
    # budget is the task's own, which is what the evaluator compares the
    # recorded spend against.
    evaluation = evaluate(
        EvaluationInputs(world=world, task=task, trace=trace, caps=task.budget)
    )
    artifact = {
        "schema_version": "orion.p2.run-artifact.v1",
        "task_id": task.task_id,
        "case_family": task.case_family.value,
        "system_id": system.system_id,
        "seed": seed,
        "trace": trace.as_json(),
        "evaluation": evaluation.as_json(),
    }
    record = {
        "schema_version": RESULT_RECORD_SCHEMA_VERSION,
        "paper_id": "P2",
        "protocol_id": P2_PROTOCOL_ID,
        "run_manifest_hash": run_manifest_hash,
        "result_id": f"{system.system_id}:{task.task_id}:{seed}",
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
            # The record key stays "search_queries" -- it is the external
            # contract other consumers read. The SOURCE field is query_count;
            # ResourceUse has never had a search_queries attribute, so this
            # line raised on every run that reached it.
            "search_queries": float(trace.resources.query_count),
        },
        "failure_class": evaluation.failure_class,
        "raw_artifact_hash": sha256_digest(artifact),
        "authority_flags": evaluation.authority_flags(),
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
    clock: Callable[[], float] = time.monotonic,
) -> Iterator[RunOutcome]:
    """Every task, every seed, in a fixed order. Repeats are nested, never pooled."""

    if not seeds:
        raise ValueError("at least one seed is required")
    for task in sorted(tasks, key=lambda item: item.task_id):
        for repeat_index, seed in enumerate(seeds):
            yield execute(
                system,
                world,
                task,
                seed=seed,
                run_manifest_hash=run_manifest_hash,
                clock=clock,
                repeat_index=repeat_index,
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
    "BudgetExhausted",
    "BudgetedSession",
    "P2_PROTOCOL_ID",
    "PublicIndex",
    "RESULT_RECORD_SCHEMA_VERSION",
    "RunOutcome",
    "SessionConfig",
    "build_public_index",
    "execute",
    "run_suite",
    "write_artifacts",
    "write_records",
]
