import hashlib

import pytest

from orion.core.claims import ClaimAuthority, ClaimRecord
from orion.core.evidence import EvidenceRecord
from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine import CallableMechanicGuard, MechanicGuardResult
from orion.engine.cycle import CycleOperator, Transition
from orion.engine.solver import SolverConfig
from orion.engine.trace import SolveTrace, TraceEvent
from orion.experience import EpisodeOutcome
from orion.mechanics import MechanicReceipt, MechanicRunStatus
from orion.providers.experience.memory import InMemoryExperienceStore
from orion.providers.llm import CallableLLMProvider
from orion.providers.retrieval import InMemoryRetrievalProvider
from orion.providers.verification import InMemoryVerificationProvider
from orion.runtime import OrionRuntime

_EMPTY_RESULT_SEARCH_PLAN = (
    '{"queries":[{"query_id":"q:fixture","text":"fixture query",'
    '"route_id":"route:fixture","route_kind":"PARENT_DISCIPLINE",'
    '"domain_hint":null}]}'
)


class _FakeSolver:
    def __init__(self, status: SolutionStatus, *, atomic_failure: bool = False) -> None:
        self.status = status
        self.atomic_failure = atomic_failure

    def initial_state(self, problem: Problem) -> OrionState:
        knowledge = KnowledgeState()
        if self.status is SolutionStatus.SOLVED_VERIFIED:
            knowledge = KnowledgeState(
                claims=(
                    ClaimRecord(
                        "claim:verified-fixture",
                        "Verified fixture claim.",
                        ("evidence:verified-fixture",),
                        authority=ClaimAuthority.VERIFIED,
                        certificate_ids=("certificate:verified-fixture",),
                    ),
                ),
                evidence=(
                    EvidenceRecord(
                        "evidence:verified-fixture",
                        "Verified fixture evidence.",
                        "fixture://verified-solution",
                    ),
                )
            )
        return OrionState(knowledge, SearchUniverseState(), MethodState("test"))

    def solve(self, problem: Problem, *, initial_state=None, trace_id=None):
        assert initial_state is not None
        final_state = initial_state.advance() if self.atomic_failure else initial_state
        events = ()
        if self.atomic_failure:
            transition = Transition(
                CycleOperator.SEARCH,
                input_epoch=initial_state.epoch,
                output_epoch=final_state.epoch,
                residual_ids=("search:coverage-open",),
            )
            events = (
                TraceEvent(
                    CycleOperator.SEARCH,
                    final_state.epoch,
                    "search failed",
                    transition,
                    MechanicReceipt(
                        "receipt:search-failure",
                        "SEARCH.v1",
                        MechanicRunStatus.FAILED,
                        action_ids=(CycleOperator.SEARCH.value,),
                        handoff_values=(("changed_coordinates", ""),),
                        residual_ids=("search:coverage-open",),
                        failure_signature=("missed-parent-domain",),
                    ),
                    hashlib.sha256(repr(initial_state).encode()).hexdigest(),
                    hashlib.sha256(repr(final_state).encode()).hexdigest(),
                ),
            )
        else:
            residual_ids = (
                ("coverage-open",)
                if self.status is SolutionStatus.BLOCKED
                else (
                    (f"solution-status:{self.status.value}",)
                    if self.status is not SolutionStatus.SOLVED_VERIFIED
                    else ()
                )
            )
            receipt_status = {
                SolutionStatus.SOLVED_VERIFIED: MechanicRunStatus.SUCCEEDED,
                SolutionStatus.PROVISIONAL: MechanicRunStatus.PARTIAL,
                SolutionStatus.BLOCKED: MechanicRunStatus.BLOCKED,
                SolutionStatus.CANNOT_CHECK: MechanicRunStatus.CANNOT_CHECK,
            }[self.status]
            transition = Transition(
                CycleOperator.RECURSE,
                input_epoch=initial_state.epoch,
                output_epoch=final_state.epoch,
                residual_ids=residual_ids,
            )
            state_hash = hashlib.sha256(repr(initial_state).encode()).hexdigest()
            events = (
                TraceEvent(
                    CycleOperator.RECURSE,
                    final_state.epoch,
                    "fixture root outcome",
                    transition,
                    MechanicReceipt(
                        "receipt:fixture-root",
                        "ORION_SOLVE.v1",
                        receipt_status,
                        action_ids=(CycleOperator.RECURSE.value,),
                        handoff_values=(("changed_coordinates", ""),),
                        residual_ids=residual_ids,
                        failure_signature=(
                            (f"solution_status:{self.status.value}",)
                            if residual_ids
                            else ()
                        ),
                    ),
                    state_hash,
                    state_hash,
                ),
            )
        return (
            Solution(
                problem.problem_id,
                self.status,
                "fixture",
                residual_ids=("coverage-open",)
                if self.status is SolutionStatus.BLOCKED
                else (),
                evidence_ids=("evidence:verified-fixture",)
                if self.status is SolutionStatus.SOLVED_VERIFIED
                else (),
                trace_id=trace_id,
            ),
            final_state,
            SolveTrace(trace_id, events),
        )


def test_runtime_records_blocked_task_as_reusable_failure_episode():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(_FakeSolver(SolutionStatus.BLOCKED), experience_store=store)
    result = runtime.solve(
        Problem("task:blocked", "Find the missing parent discipline."),
        variation_signature=("vocabulary-mask-a",),
    )
    assert result.experience_episode_id is not None
    assert len(store.episodes()) == 2
    episode = next(
        item
        for item in store.episodes()
        if item.episode_id == result.experience_episode_id
    )
    assert episode.mechanic_id == "ORION_SOLVE.v1"
    assert episode.variation_signature == ("vocabulary-mask-a",)
    assert "solution_status:BLOCKED" in episode.failure_signature
    assert episode.residual_ids == ("coverage-open",)


def test_runtime_records_success_without_inventing_failure_signature():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(
        _FakeSolver(SolutionStatus.SOLVED_VERIFIED), experience_store=store
    )
    result = runtime.solve(
        Problem("task:success", "Solve fixture."), variation_signature=("baseline",)
    )
    episode = next(
        item
        for item in store.episodes()
        if item.episode_id == result.experience_episode_id
    )
    assert episode.outcome.value == "SUCCESS"
    assert episode.failure_signature == ()
    assert episode.evidence_ids == ("evidence:verified-fixture",)


def test_runtime_records_atomic_failure_episode_with_root_parent_identity():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(
        _FakeSolver(SolutionStatus.BLOCKED, atomic_failure=True),
        experience_store=store,
    )

    runtime.solve(
        Problem("task:atomic", "Find the hidden parent discipline."),
        variation_signature=("mask-a",),
        evaluation_epoch_id="evaluation:shadow-001",
        split_id="split:diagnostic",
    )

    atomic, root = store.episodes()
    assert atomic.mechanic_id == "SEARCH.v1"
    assert atomic.outcome is EpisodeOutcome.FAILURE
    assert atomic.parent_run_id == root.run_id
    assert atomic.run_id != root.run_id
    assert atomic.evaluation_epoch_id == root.evaluation_epoch_id
    assert atomic.split_id == root.split_id


def test_repeated_identical_runtime_attempts_are_distinct_immutable_episodes():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(_FakeSolver(SolutionStatus.BLOCKED), experience_store=store)
    problem = Problem("task:retry", "Retry the same failed task.")

    first = runtime.solve(problem, variation_signature=("same-variation",))
    second = runtime.solve(problem, variation_signature=("same-variation",))

    assert first.experience_episode_id != second.experience_episode_id
    assert first.trace.trace_id != second.trace.trace_id
    assert len(store.episodes()) == 4


def test_real_solver_trace_projects_every_mechanic_receipt_into_experience():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime.from_providers(
        llm=CallableLLMProvider(
            lambda request: _EMPTY_RESULT_SEARCH_PLAN, model_id="known-world"
        ),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        experience_store=store,
    )

    result = runtime.solve(
        Problem("task:known-world-trace", "What can this empty fixture establish?"),
        variation_signature=("known-world",),
        evaluation_epoch_id="evaluation:known-world-v1",
        split_id="split:known-world",
    )

    assert result.trace.events
    eligible_events = tuple(
        event for event in result.trace.events if event.receipt.experience_eligible
    )
    assert len(result.mechanic_experience_episode_ids) == len(eligible_events)
    by_id = {episode.episode_id: episode for episode in store.episodes()}
    root = by_id[result.experience_episode_id]
    for event, episode_id in zip(
        eligible_events,
        result.mechanic_experience_episode_ids,
        strict=True,
    ):
        episode = by_id[episode_id]
        assert event.receipt.receipt_id
        assert event.receipt.mechanic_id == episode.mechanic_id
        assert event.pre_state_hash == episode.pre_state_hash
        assert event.post_state_hash == episode.post_state_hash
        assert event.epoch == event.transition.output_epoch
        assert episode.parent_run_id == root.run_id


def test_real_runtime_records_executed_failure_pattern_guard_action():
    store = InMemoryExperienceStore()
    calls = []
    guard = CallableMechanicGuard(
        "guard:pattern:search-parent-domain",
        "SEARCH.v1",
        lambda problem, state: (
            calls.append((problem.problem_id, state.epoch))
            or MechanicGuardResult(passed=True)
        ),
    )
    runtime = OrionRuntime.from_providers(
        llm=CallableLLMProvider(
            lambda request: _EMPTY_RESULT_SEARCH_PLAN, model_id="guard-fixture"
        ),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        experience_store=store,
        config=SolverConfig(max_iterations=2),
        guards=(guard,),
    )

    initial_state = OrionState(
        KnowledgeState(
            claims=(
                ClaimRecord(
                    "claim:guard-fixture",
                    "Known fixture claim.",
                    ("evidence:guard-fixture",),
                    authority=ClaimAuthority.VERIFIED,
                    certificate_ids=("certificate:guard-fixture",),
                ),
            ),
            evidence=(
                EvidenceRecord(
                    "evidence:guard-fixture",
                    "Known fixture evidence.",
                    "fixture://guard",
                    certificate_ids=("certificate:guard-fixture",),
                ),
            ),
        ),
        SearchUniverseState(),
        MethodState("test"),
    )
    result = runtime.solve(
        Problem("task:guard-runtime", "Run the protected search guard."),
        initial_state=initial_state,
    )

    search_episodes = tuple(
        episode
        for episode in store.episodes()
        if episode.mechanic_id == "SEARCH.v1"
    )
    assert calls == [("task:guard-runtime", 0), ("task:guard-runtime", 1)]
    assert len(search_episodes) == 2
    assert all(guard.guard_id in item.action_ids for item in search_episodes)
    assert all(item.source_receipt_id for item in search_episodes)
    assert result.mechanic_experience_episode_ids
    root_episode = next(
        episode
        for episode in store.episodes()
        if episode.episode_id == result.experience_episode_id
    )
    assert guard.guard_id not in root_episode.action_ids


def test_root_solve_guard_rejects_before_any_provider_or_operator_side_effect():
    store = InMemoryExperienceStore()
    provider_calls = []
    guard_calls = []
    guard = CallableMechanicGuard(
        "guard:pattern:root-solve-policy",
        "ORION_SOLVE.v1",
        lambda problem, state: (
            guard_calls.append((problem.problem_id, state.epoch))
            or MechanicGuardResult(
                passed=False,
                residual_ids=("guard:root-solve:policy-rejected",),
            )
        ),
    )
    runtime = OrionRuntime.from_providers(
        llm=CallableLLMProvider(
            lambda request: (
                provider_calls.append(request) or _EMPTY_RESULT_SEARCH_PLAN
            ),
            model_id="must-not-run",
        ),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        experience_store=store,
        guards=(guard,),
    )

    result = runtime.solve(
        Problem("task:root-guard", "Reject before starting the root solve.")
    )

    assert guard_calls == [("task:root-guard", 0)]
    assert provider_calls == []
    assert result.solution.status is SolutionStatus.BLOCKED
    assert len(result.trace.events) == 1
    event = result.trace.events[0]
    assert event.operator is CycleOperator.RECURSE
    assert event.receipt.status is MechanicRunStatus.BLOCKED
    assert event.receipt.action_ids == (guard.guard_id,)
    assert event.receipt.failure_signature == ("mechanic_guard_rejected",)


def test_root_solve_guard_executes_once_for_one_root_invocation():
    calls = []
    guard = CallableMechanicGuard(
        "guard:pattern:root-solve-once",
        "ORION_SOLVE.v1",
        lambda problem, state: (
            calls.append((problem.problem_id, state.epoch))
            or MechanicGuardResult(passed=True)
        ),
    )
    runtime = OrionRuntime.from_providers(
        llm=CallableLLMProvider(
            lambda request: _EMPTY_RESULT_SEARCH_PLAN, model_id="root-guard-once"
        ),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        config=SolverConfig(max_iterations=2),
        guards=(guard,),
    )
    initial_state = OrionState(
        KnowledgeState(
            claims=(
                ClaimRecord(
                    "claim:root-guard-once",
                    "Known fixture claim.",
                    ("evidence:root-guard-once",),
                    authority=ClaimAuthority.VERIFIED,
                    certificate_ids=("certificate:root-guard-once",),
                ),
            ),
            evidence=(
                EvidenceRecord(
                    "evidence:root-guard-once",
                    "Known fixture evidence.",
                    "fixture://root-guard-once",
                    certificate_ids=("certificate:root-guard-once",),
                ),
            ),
        ),
        SearchUniverseState(),
        MethodState("test"),
    )

    result = runtime.solve(
        Problem("task:root-guard-once", "Invoke one root solve."),
        initial_state=initial_state,
    )

    guarded_events = tuple(
        event for event in result.trace.events if guard.guard_id in event.receipt.action_ids
    )
    assert calls == [("task:root-guard-once", 0)]
    assert len(guarded_events) == 1
    assert guarded_events[0].summary == "solve_started"


def test_search_guard_is_rechecked_at_current_epoch_and_rejection_is_not_execution():
    store = InMemoryExperienceStore()
    calls = []

    def guard_search(problem, state):
        calls.append((problem.problem_id, state.epoch))
        if state.epoch == 0:
            return MechanicGuardResult(passed=True)
        return MechanicGuardResult(
            passed=False,
            residual_ids=("guard:search:epoch-policy-rejected",),
        )

    guard = CallableMechanicGuard(
        "guard:pattern:search-current-state",
        "SEARCH.v1",
        guard_search,
    )
    runtime = OrionRuntime.from_providers(
        llm=CallableLLMProvider(
            lambda request: _EMPTY_RESULT_SEARCH_PLAN, model_id="guard-current-state-fixture"
        ),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        experience_store=store,
        config=SolverConfig(max_iterations=2),
        guards=(guard,),
    )

    initial_state = OrionState(
        KnowledgeState(
            claims=(
                ClaimRecord(
                    "claim:guard-current-state",
                    "Known fixture claim.",
                    ("evidence:guard-current-state",),
                    authority=ClaimAuthority.VERIFIED,
                    certificate_ids=("certificate:guard-current-state",),
                ),
            ),
            evidence=(
                EvidenceRecord(
                    "evidence:guard-current-state",
                    "Known fixture evidence.",
                    "fixture://guard-current-state",
                    certificate_ids=("certificate:guard-current-state",),
                ),
            ),
        ),
        SearchUniverseState(),
        MethodState("test"),
    )
    result = runtime.solve(
        Problem("task:guard-current-state", "Recheck the search guard each round."),
        initial_state=initial_state,
    )

    search_events = tuple(
        event
        for event in result.trace.events
        if event.operator is CycleOperator.SEARCH
    )
    assert calls == [
        ("task:guard-current-state", 0),
        ("task:guard-current-state", 1),
    ]
    assert len(search_events) == 2
    assert search_events[0].receipt.status is MechanicRunStatus.SUCCEEDED
    assert CycleOperator.SEARCH.value in search_events[0].receipt.action_ids
    assert guard.guard_id in search_events[0].receipt.action_ids
    assert search_events[1].receipt.status is MechanicRunStatus.BLOCKED
    assert search_events[1].receipt.action_ids == (guard.guard_id,)
    assert search_events[1].receipt.failure_signature == (
        "mechanic_guard_rejected",
    )
    assert result.solution.status is SolutionStatus.BLOCKED


def test_provider_exception_becomes_atomic_and_root_failure_experience():
    store = InMemoryExperienceStore()

    def crash(request):
        raise ConnectionError("known-world provider outage")

    runtime = OrionRuntime.from_providers(
        llm=CallableLLMProvider(crash, model_id="crashing-provider"),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        experience_store=store,
    )

    result = runtime.solve(
        Problem("task:provider-crash", "Exercise failure persistence.")
    )

    assert result.solution.status is SolutionStatus.BLOCKED
    failed = next(
        episode for episode in store.episodes() if episode.mechanic_id == "SEARCH.v1"
    )
    assert failed.outcome is EpisodeOutcome.FAILURE
    assert "operator_exception" in failed.failure_signature
    assert any("ConnectionError" in item for item in failed.failure_signature)
    assert failed.latency_seconds is not None
    root = next(
        episode
        for episode in store.episodes()
        if episode.episode_id == result.experience_episode_id
    )
    assert failed.parent_run_id == root.run_id


def test_failed_root_run_cannot_turn_solve_started_into_successful_guard_replay():
    store = InMemoryExperienceStore()
    guard = CallableMechanicGuard(
        "guard:pattern:root-replay-boundary",
        "ORION_SOLVE.v1",
        lambda problem, state: MechanicGuardResult(passed=True),
    )

    def crash(request):
        raise ConnectionError("provider fails after root guard")

    runtime = OrionRuntime.from_providers(
        llm=CallableLLMProvider(crash, model_id="root-replay-crash"),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        experience_store=store,
        guards=(guard,),
    )

    result = runtime.solve(
        Problem("task:root-replay-boundary", "Do not promote a started run.")
    )

    root_episodes = tuple(
        episode
        for episode in store.episodes()
        if episode.mechanic_id == "ORION_SOLVE.v1"
    )
    assert result.solution.status is SolutionStatus.BLOCKED
    assert len(root_episodes) == 1
    assert root_episodes[0].episode_id == result.experience_episode_id
    assert root_episodes[0].outcome is EpisodeOutcome.BLOCKED
    assert guard.guard_id in root_episodes[0].action_ids
    assert not any(item.outcome is EpisodeOutcome.SUCCESS for item in root_episodes)


def test_runtime_rejects_unrelated_trace_endpoints_before_recording_experience():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(
        _FakeSolver(SolutionStatus.BLOCKED, atomic_failure=True),
        experience_store=store,
    )
    original_solve = runtime._solver.solve

    def substitute_trace(problem, *, initial_state=None, trace_id=None):
        solution, final_state, trace = original_solve(
            problem,
            initial_state=initial_state,
            trace_id=trace_id,
        )
        event = trace.events[0]
        substituted = TraceEvent(
            event.operator,
            event.epoch,
            event.summary,
            event.transition,
            event.receipt,
            "a" * 64,
            "b" * 64,
        )
        return solution, final_state, SolveTrace(trace.trace_id, (substituted,))

    runtime._solver.solve = substitute_trace

    with pytest.raises(ValueError, match="pre-state endpoint mismatch"):
        runtime.solve(Problem("task:unrelated-trace", "Reject unrelated history."))

    assert store.episodes() == ()


def test_runtime_rejects_solver_result_with_substituted_trace_identity():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(
        _FakeSolver(SolutionStatus.CANNOT_CHECK), experience_store=store
    )
    original_solve = runtime._solver.solve

    def substitute_trace_id(problem, *, initial_state=None, trace_id=None):
        solution, final_state, trace = original_solve(
            problem,
            initial_state=initial_state,
            trace_id=trace_id,
        )
        return solution, final_state, SolveTrace("trace:substituted", trace.events)

    runtime._solver.solve = substitute_trace_id

    with pytest.raises(ValueError, match="requested trace identity"):
        runtime.solve(Problem("task:trace-id", "Reject substituted identity."))

    assert store.episodes() == ()


def test_runtime_rejects_empty_trace_that_mutates_state_before_recording():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(
        _FakeSolver(SolutionStatus.CANNOT_CHECK), experience_store=store
    )
    original_solve = runtime._solver.solve

    def mutate_without_trace(problem, *, initial_state=None, trace_id=None):
        solution, _, _ = original_solve(
            problem,
            initial_state=initial_state,
            trace_id=trace_id,
        )
        return solution, initial_state.advance(), SolveTrace(trace_id, ())

    runtime._solver.solve = mutate_without_trace

    with pytest.raises(ValueError, match="endpoint-bound event"):
        runtime.solve(Problem("task:empty-trace", "Reject untraced mutation."))

    assert store.episodes() == ()


def test_runtime_rejects_empty_trace_even_for_unchanged_verified_state():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(
        _FakeSolver(SolutionStatus.SOLVED_VERIFIED), experience_store=store
    )
    original_solve = runtime._solver.solve

    def erase_trace(problem, *, initial_state=None, trace_id=None):
        solution, final_state, _ = original_solve(
            problem,
            initial_state=initial_state,
            trace_id=trace_id,
        )
        return solution, final_state, SolveTrace(trace_id, ())

    runtime._solver.solve = erase_trace

    with pytest.raises(ValueError, match="endpoint-bound event"):
        runtime.solve(Problem("task:empty-verified", "Reject untraced success."))

    assert store.episodes() == ()
