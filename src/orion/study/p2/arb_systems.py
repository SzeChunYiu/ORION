"""The systems under test on AutoResearchBench Wide, behind one interface.

Five systems plus six single-mechanism ablations, all sharing one route engine,
one budget meter and one output record. Sharing the engine is deliberate: if
each system had its own retrieval loop, a difference in the loops would be
indistinguishable from a difference in the mechanisms under study.

What distinguishes the systems is exactly three things -- which routes exist,
how each route's next query is chosen, and which governance mechanisms are on.
Everything else is common code.

Naming honesty: ``dense_like_single_route`` is **not** a neural retriever we
trained or ran. It is OpenAlex's own relevance ranking over the same question.
It occupies the "different ranking function, different backend" slot in the
baseline set, and it is named ``_like`` so no reader mistakes it for a dense
embedding model.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from typing import Protocol, runtime_checkable

from orion.core.search import SearchRouteKind
from orion.knowledge.identity import (
    ReadDecision,
    ReadReceipt,
    SourceIdentity,
    canonical_source_id,
    decide_read,
    merge_identities,
)
from orion.knowledge.route_control import (
    FrozenRouteControlPolicy,
    RouteAttempt,
    RouteControlAction,
    RouteControlState,
    decide_route,
)
from orion.knowledge.routes import RouteCapture, assess_pair, estimate_coverage

from .arb_runtime import (
    Budget,
    BudgetExhausted,
    BudgetMeter,
    CapturedWork,
    ProviderOutcome,
    ProviderStatus,
    QueryDerivation,
    ReadEncounterRecord,
    RouteTrialRecord,
    SystemRun,
    content_digest,
    derive_citation_seed_query,
    derive_current_vocabulary_query,
    derive_lexical_variant_query,
    merged_capture_rows,
)
from .arb_wide import TaskPrompt, arxiv_predictions_from_identities

__all__ = [
    "ABLATION_IDS",
    "BASELINE_IDS",
    "Backends",
    "CitationBackend",
    "Mechanisms",
    "SYSTEM_IDS",
    "SearchBackend",
    "SystemSpec",
    "build_system",
    "run_system",
]

SCHEMA_VERSION = "arb-wide-extraction-v1"

#: Route-control policy, frozen before any outcome. Recorded in every trial; it
#: is a route-local heuristic and never a task-saturation authority.
POLICY = FrozenRouteControlPolicy(
    policy_id="P2.arb-wide.route-control.v1",
    reformulate_after_zero_novelty=1,
    switch_after_zero_novelty=2,
)


@runtime_checkable
class SearchBackend(Protocol):
    """A keyword/relevance search backend. Injected, so tests need no network."""

    backend_id: str

    def search(self, query: str, *, max_results: int = 25) -> ProviderOutcome: ...


@runtime_checkable
class CitationBackend(Protocol):
    """A backend that can follow a captured work's reference list."""

    backend_id: str

    def references(self, source_id: str, *, max_results: int = 25) -> ProviderOutcome: ...


@dataclass(frozen=True)
class Backends:
    """Every provider a system may reach. Missing ones are typed, not absent."""

    arxiv: SearchBackend | None = None
    openalex: SearchBackend | None = None
    openalex_citations: CitationBackend | None = None


@dataclass(frozen=True)
class Mechanisms:
    """ORION's governance mechanisms. Each ablation flips exactly one field.

    The two fields that default to ``False`` name *defects*: letting a route
    stop close a task, and letting a coverage diagnostic control stopping. Full
    ORION has them off; the corresponding ablation turns one on.
    """

    route_independence_check: bool = True
    question_conditioned_read_ledger: bool = True
    content_identity_dedup: bool = True
    unavailable_route_open_state: bool = True
    route_stop_can_close_task: bool = False
    coverage_diagnostic_controls_stopping: bool = False


@dataclass(frozen=True)
class RouteSpec:
    """One route: an identity, a backend and a way of choosing its next query."""

    route_id: str
    route_kind: SearchRouteKind
    backend_name: str
    derivation_rule: str
    is_citation_route: bool = False


@dataclass(frozen=True)
class SystemSpec:
    """A system under test: its routes, its stopping style, its mechanisms."""

    system_id: str
    routes: tuple[RouteSpec, ...]
    mechanisms: Mechanisms
    control_driven: bool
    description: str


# ---------------------------------------------------------------------------
# Route definitions.
# ---------------------------------------------------------------------------

_ARXIV_ROUTE = RouteSpec(
    route_id="r-arxiv-keyword",
    route_kind=SearchRouteKind.CURRENT_VOCABULARY,
    backend_name="arxiv",
    derivation_rule="D1_CURRENT_VOCABULARY",
)
_OPENALEX_ROUTE = RouteSpec(
    route_id="r-openalex-keyword",
    route_kind=SearchRouteKind.LEXICAL_VARIANT,
    backend_name="openalex",
    derivation_rule="D2_LEXICAL_VARIANT",
)
_OPENALEX_CITATION_ROUTE = RouteSpec(
    route_id="r-openalex-citation",
    route_kind=SearchRouteKind.CITATION_NEIGHBORHOOD,
    backend_name="openalex_citations",
    derivation_rule="D3_CITATION_NEIGHBORHOOD",
    is_citation_route=True,
)

BASELINE_IDS = (
    "lexical_single_route",
    "dense_like_single_route",
    "hybrid_union",
    "agentic_single_route",
)
ABLATION_IDS = (
    "orion_no_route_independence_check",
    "orion_no_question_conditioned_read_ledger",
    "orion_route_stop_can_close_task",
    "orion_no_unavailable_route_open_state",
    "orion_coverage_diagnostic_controls_stopping",
    "orion_no_content_identity_dedup",
)
SYSTEM_IDS = (*BASELINE_IDS, "orion_full", *ABLATION_IDS)

_ORION_ROUTES = (_ARXIV_ROUTE, _OPENALEX_ROUTE, _OPENALEX_CITATION_ROUTE)

_ABLATION_FIELD = {
    "orion_no_route_independence_check": ("route_independence_check", False),
    "orion_no_question_conditioned_read_ledger": (
        "question_conditioned_read_ledger",
        False,
    ),
    "orion_route_stop_can_close_task": ("route_stop_can_close_task", True),
    "orion_no_unavailable_route_open_state": ("unavailable_route_open_state", False),
    "orion_coverage_diagnostic_controls_stopping": (
        "coverage_diagnostic_controls_stopping",
        True,
    ),
    "orion_no_content_identity_dedup": ("content_identity_dedup", False),
}


def build_system(system_id: str) -> SystemSpec:
    """Return the frozen specification for one system id."""

    if system_id == "lexical_single_route":
        return SystemSpec(
            system_id,
            (_ARXIV_ROUTE,),
            Mechanisms(
                route_independence_check=False,
                question_conditioned_read_ledger=False,
                content_identity_dedup=False,
                unavailable_route_open_state=False,
            ),
            control_driven=False,
            description=(
                "One arXiv keyword route under D1, queries issued on a fixed "
                "open-loop broadening ladder until the query budget is spent. "
                "This is the SAGE-derived promotion gate: strong lexical "
                "retrieval is competitive, so it is given the full budget."
            ),
        )
    if system_id == "dense_like_single_route":
        return SystemSpec(
            system_id,
            (_OPENALEX_ROUTE,),
            Mechanisms(
                route_independence_check=False,
                question_conditioned_read_ledger=False,
                content_identity_dedup=False,
                unavailable_route_open_state=False,
            ),
            control_driven=False,
            description=(
                "OpenAlex relevance ranking over the same question under D2. A "
                "different backend's ranking function, not a neural retriever "
                "we trained."
            ),
        )
    if system_id == "hybrid_union":
        return SystemSpec(
            system_id,
            (_ARXIV_ROUTE, _OPENALEX_ROUTE),
            Mechanisms(
                route_independence_check=False,
                question_conditioned_read_ledger=False,
                content_identity_dedup=False,
                unavailable_route_open_state=False,
            ),
            control_driven=False,
            description=(
                "Union of the lexical and dense-like routes under one shared "
                "total budget, so the union cannot win by spending twice."
            ),
        )
    if system_id == "agentic_single_route":
        return SystemSpec(
            system_id,
            (_ARXIV_ROUTE,),
            Mechanisms(
                route_independence_check=False,
                question_conditioned_read_ledger=False,
                content_identity_dedup=True,
                unavailable_route_open_state=False,
            ),
            control_driven=True,
            description=(
                "One backend, iterative reformulation driven by "
                "route_control.decide_route under the frozen policy. Novelty is "
                "measured on content digests, so reformulation responds to what "
                "was actually new."
            ),
        )
    if system_id == "orion_full":
        return SystemSpec(
            system_id, _ORION_ROUTES, Mechanisms(), control_driven=True,
            description=(
                "Three routes across two backends with three distinct query "
                "derivations, content-identity dedup, question-conditioned read "
                "state, per-route control decisions, earned-independence "
                "assessment, and task closure that no route decision can certify."
            ),
        )
    if system_id in _ABLATION_FIELD:
        field_name, value = _ABLATION_FIELD[system_id]
        return SystemSpec(
            system_id,
            _ORION_ROUTES,
            replace(Mechanisms(), **{field_name: value}),
            control_driven=True,
            description=f"orion_full with {field_name} set to {value}.",
        )
    raise KeyError(f"unknown system id {system_id!r}; known: {SYSTEM_IDS}")


# ---------------------------------------------------------------------------
# Shared execution.
# ---------------------------------------------------------------------------


@dataclass
class _Workspace:
    """Per-task accumulated state: identities, read receipts, obligations."""

    mechanisms: Mechanisms
    frame_id: str
    identities: list[SourceIdentity] = field(default_factory=list)
    receipts: list[ReadReceipt] = field(default_factory=list)
    encounters: list[ReadEncounterRecord] = field(default_factory=list)
    seen_digests: set[str] = field(default_factory=set)
    obligations: list[str] = field(default_factory=list)

    def merged(self) -> tuple[SourceIdentity, ...]:
        if not self.mechanisms.content_identity_dedup:
            # Ablation: no merge. Aliases of one work stay separate, so the same
            # paper found by two routes counts twice in every coverage number.
            return tuple(self.identities)
        return merge_identities(tuple(self.identities))

    def primary_of(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for identity in self.merged():
            for key in identity.keys:
                mapping[key] = identity.source_id
        return mapping

    def absorb(self, records: Sequence[CapturedWork]) -> tuple[str, ...]:
        """Record an attempt's captures; return the digests that were new.

        Novelty is measured on **content digests**, never on provider ids: two
        routes that found one paper under two identifiers must not both count it
        as new, or a route looks productive precisely when it is repeating.
        """

        novel: list[str] = []
        for record in records:
            digest = record.content_digest or content_digest(
                record.source_id, record.title
            )
            self.identities.append(
                SourceIdentity(
                    source_id=record.source_id,
                    aliases=record.aliases,
                    title=record.title,
                )
            )
            self._encounter(record, digest)
            if digest not in self.seen_digests:
                self.seen_digests.add(digest)
                novel.append(digest)
        return tuple(novel)

    def _encounter(self, record: CapturedWork, digest: str) -> None:
        """Log one presented source and whether a read followed (B14, B15)."""

        primary = self.primary_of().get(record.source_id, record.source_id)
        if self.mechanisms.question_conditioned_read_ledger:
            decision = decide_read(
                primary, digest, SCHEMA_VERSION, self.frame_id, tuple(self.receipts)
            )
        else:
            # Ablation: read state is not conditioned on the question frame or
            # the content version, so any previously seen source reads as done.
            decision = (
                ReadDecision.ALREADY_READ
                if any(item.source_id == primary for item in self.receipts)
                else ReadDecision.UNSEEN
            )
        executed = decision is not ReadDecision.ALREADY_READ
        if executed:
            self.receipts.append(
                ReadReceipt(
                    source_id=primary,
                    content_digest=digest,
                    schema_version=SCHEMA_VERSION,
                    frame_id=self.frame_id,
                )
            )
        self.encounters.append(
            ReadEncounterRecord(
                merged_source_id=primary,
                content_digest=digest,
                schema_version=SCHEMA_VERSION,
                frame_id=self.frame_id,
                decision_before_execution=decision.value,
                executed=executed,
            )
        )


def _derive(rule: str, question: str, breadth: int) -> QueryDerivation:
    """Next query on a route's deterministic broadening ladder.

    Reformulation broadens by dropping the least salient term, which is the one
    reformulation that cannot accidentally narrow a search that already returned
    nothing.
    """

    if rule == "D1_CURRENT_VOCABULARY":
        return derive_current_vocabulary_query(question, limit=max(2, 6 - breadth))
    if rule == "D2_LEXICAL_VARIANT":
        return derive_lexical_variant_query(question, limit=max(2, 8 - breadth))
    raise ValueError(f"rule {rule!r} has no text derivation ladder")


def _outcome_to_status(outcome: ProviderOutcome) -> str:
    return outcome.status.value


def _call_backend(
    spec: RouteSpec,
    backends: Backends,
    derivation: QueryDerivation,
    max_results: int,
) -> ProviderOutcome:
    backend = getattr(backends, spec.backend_name, None)
    if backend is None:
        return ProviderOutcome(
            ProviderStatus.UNAVAILABLE,
            note=f"no backend configured for route {spec.route_id}",
        )
    if spec.is_citation_route:
        return backend.references(derivation.query, max_results=max_results)
    return backend.search(derivation.query, max_results=max_results)


def run_system(
    system_id: str,
    prompt: TaskPrompt,
    backends: Backends,
    budget: Budget,
    clock: Callable[[], float],
    *,
    repeat_index: int = 0,
    seed: int = 0,
    max_results: int = 25,
    wait: Callable[[str], None] | None = None,
) -> SystemRun:
    """Run one system on one task under a hard matched budget.

    ``wait`` is the caller's rate-gate hook, invoked with a provider name before
    every call. The runner owns waiting; ``RateGate`` only reports how long to
    wait, it does not sleep.
    """

    spec = build_system(system_id)
    meter = BudgetMeter(budget=budget, clock=clock)
    meter.start()
    workspace = _Workspace(mechanisms=spec.mechanisms, frame_id=prompt.task_id)

    trials: list[RouteTrialRecord] = []
    captures_by_route: dict[str, set[str]] = {item.route_id: set() for item in spec.routes}
    stopped: dict[str, str] = {}
    budget_exhausted = False

    for route in spec.routes:
        if budget_exhausted:
            break
        attempts: list[RouteAttempt] = []
        breadth = 0
        while True:
            zero_novelty_before = RouteControlState(
                route_id=route.route_id,
                route_kind=route.route_kind,
                attempts=tuple(attempts),
                budget_units=float(budget.query_count),
            ).consecutive_zero_novelty

            derivation = _next_derivation(route, prompt, workspace, breadth)
            if derivation is None:
                stopped[route.route_id] = "no_citation_seed_available"
                break
            try:
                meter.charge_provider_call()
            except BudgetExhausted as error:
                budget_exhausted = True
                stopped[route.route_id] = f"budget_exhausted:{error}"
                break
            if wait is not None:
                wait(route.backend_name)
            outcome = _call_backend(route, backends, derivation, max_results)

            novel = workspace.absorb(outcome.records) if outcome.ok else ()
            digests = tuple(
                item.content_digest or content_digest(item.source_id, item.title)
                for item in outcome.records
            )
            captures_by_route[route.route_id] |= set(digests)

            obligation_ids: tuple[str, ...] = ()
            if outcome.status.opens_obligation:
                obligation = (
                    f"obl:{route.route_id}:{derivation.rule_id}:"
                    f"{len(attempts)}:{outcome.status.value}"
                )
                if spec.mechanisms.unavailable_route_open_state:
                    workspace.obligations.append(obligation)
                    obligation_ids = (obligation,)
                else:
                    # Ablation: an unavailable route is treated as if it had
                    # been searched and found nothing.
                    obligation_ids = ()

            attempts.append(
                RouteAttempt(
                    attempt_id=f"{route.route_id}#{len(attempts)}",
                    query_id=f"{derivation.rule_id}#{breadth}",
                    retrieved_digests=tuple(dict.fromkeys(digests)),
                    novel_digests=tuple(
                        item for item in dict.fromkeys(novel) if item in set(digests)
                    ),
                    cost_units=1.0,
                    execution_failure_signatures=(
                        () if outcome.ok else (outcome.status.value,)
                    ),
                )
            )
            state = RouteControlState(
                route_id=route.route_id,
                route_kind=route.route_kind,
                attempts=tuple(attempts),
                budget_units=float(budget.query_count),
                alternative_route_kinds=tuple(
                    item.route_kind for item in spec.routes if item.route_kind is not route.route_kind
                ),
            )
            decision = decide_route(state, POLICY)

            trials.append(
                RouteTrialRecord(
                    route_id=route.route_id,
                    route_kind=route.route_kind,
                    backend=route.backend_name,
                    attempt_index=len(attempts) - 1,
                    consecutive_zero_novelty_before=zero_novelty_before,
                    query_derivation_rule=derivation.rule_id,
                    query=derivation.query,
                    transport_status=_outcome_to_status(outcome),
                    captures=merged_capture_rows(outcome.records, workspace.primary_of()),
                    novel_digests=tuple(novel),
                    open_obligation_ids=obligation_ids,
                    control_action=decision.action.value,
                    control_reasons=decision.reasons,
                    raw_response_sha256=outcome.raw_response_sha256,
                    note=outcome.note,
                )
            )

            if spec.control_driven:
                if decision.action in (
                    RouteControlAction.STOP,
                    RouteControlAction.SUSPEND,
                    RouteControlAction.SWITCH,
                ):
                    stopped[route.route_id] = decision.action.value
                    break
                if decision.action is RouteControlAction.REFORMULATE:
                    breadth += 1
            else:
                # Open-loop baselines broaden every attempt regardless of novelty.
                breadth += 1
            if meter.remaining_queries() <= 0:
                budget_exhausted = True
                stopped[route.route_id] = "budget_exhausted"
                break
            if route.is_citation_route and breadth >= 2:
                stopped[route.route_id] = "citation_seeds_exhausted"
                break
            if not spec.control_driven and breadth >= _open_loop_attempts(spec, budget):
                stopped[route.route_id] = "fixed_ladder_complete"
                break

    identities = workspace.merged()
    predicted = arxiv_predictions_from_identities(identities)

    pairs, refusal = _independence(spec, captures_by_route, workspace)
    closed, closure_reason = _task_closure(spec, stopped, workspace, budget_exhausted, refusal)

    return SystemRun(
        system_id=system_id,
        task_id=prompt.task_id,
        repeat_index=repeat_index,
        seed=seed,
        predicted_arxiv_ids=predicted,
        route_trials=tuple(trials),
        read_encounters=tuple(workspace.encounters),
        task_closure_declared=closed,
        task_closure_reason=closure_reason,
        budget_exhausted=budget_exhausted,
        cost=meter.cost(),
        open_obligation_ids=tuple(workspace.obligations),
        independence_pairs=pairs,
        coverage_refusal_reason=refusal,
        failure_class=None if trials else "no_route_attempt_executed",
    )


def _open_loop_attempts(spec: SystemSpec, budget: Budget) -> int:
    """How many attempts an open-loop route may make before its ladder ends.

    The whole query budget is divided evenly across the system's routes, so a
    two-route baseline does not get twice the calls of a one-route baseline.
    """

    return max(1, budget.query_count // max(1, len(spec.routes)))


def _next_derivation(
    route: RouteSpec, prompt: TaskPrompt, workspace: _Workspace, breadth: int
) -> QueryDerivation | None:
    if not route.is_citation_route:
        return _derive(route.derivation_rule, prompt.question, breadth)
    seeds = [
        item.source_id
        for item in workspace.merged()
        if canonical_source_id(item.source_id).scheme.value == "openalex"
    ]
    if len(seeds) <= breadth:
        return None
    return derive_citation_seed_query(sorted(seeds)[breadth])


def _independence(
    spec: SystemSpec, captures_by_route: dict[str, set[str]], workspace: _Workspace
) -> tuple[tuple[dict[str, str], ...], str]:
    """Assess which route pairs earned independence, or record why we cannot."""

    if not spec.mechanisms.route_independence_check:
        return (), "route_independence_check_disabled_by_ablation"
    route_captures = [
        RouteCapture(
            route_kind=item.route_kind,
            backend=item.backend_name,
            query_derivation=item.derivation_rule,
            captured=frozenset(captures_by_route.get(item.route_id, set())),
        )
        for item in spec.routes
    ]
    if len(route_captures) < 2:
        return (), "single route: capture-recapture needs at least two occasions"
    pairs = tuple(
        {
            "left": assessment.left.value,
            "right": assessment.right.value,
            "verdict": assessment.verdict.value,
            "overlap": str(assessment.overlap),
        }
        for assessment in (
            assess_pair(route_captures[i], route_captures[j])
            for i in range(len(route_captures))
            for j in range(i + 1, len(route_captures))
        )
    )
    estimate = estimate_coverage(route_captures)
    return pairs, estimate.refusal_reason


def _task_closure(
    spec: SystemSpec,
    stopped: dict[str, str],
    workspace: _Workspace,
    budget_exhausted: bool,
    refusal: str,
) -> tuple[bool, str]:
    """Decide whether the task was *declared* closed, and on what authority.

    Truncation at a cap is not closure. An unresolved unavailability obligation
    blocks closure outright: a route we could not reach is not a route we
    searched, so a closure declared over it would be scoring absence of evidence
    as coverage.
    """

    if spec.mechanisms.route_stop_can_close_task and stopped:
        return True, f"ablation: route stop closed the task ({sorted(stopped)[0]})"
    if budget_exhausted:
        return False, "truncated at the budget cap; the task did not close"
    if spec.mechanisms.unavailable_route_open_state and workspace.obligations:
        return False, (
            f"{len(workspace.obligations)} unresolved route obligation(s); "
            "an unreachable route is not an exhausted one"
        )
    if len(stopped) < len(spec.routes):
        return False, "not every route reached a stop"
    if spec.mechanisms.coverage_diagnostic_controls_stopping:
        return True, (
            "ablation: a coverage diagnostic was given stopping authority "
            f"({refusal or 'estimate available'})"
        )
    return True, "every route stopped, no open obligation, closure declared by the task"
