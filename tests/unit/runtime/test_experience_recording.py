from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine import CallableMechanicGuard, MechanicGuardResult
from orion.engine.cycle import CycleOperator, Transition
from orion.engine.trace import SolveTrace, TraceEvent
from orion.experience import EpisodeOutcome
from orion.mechanics import MechanicReceipt, MechanicRunStatus
from orion.providers.experience.memory import InMemoryExperienceStore
from orion.providers.llm import CallableLLMProvider
from orion.providers.retrieval import InMemoryRetrievalProvider
from orion.providers.verification import InMemoryVerificationProvider
from orion.runtime import OrionRuntime


class _FakeSolver:
    def __init__(self, status: SolutionStatus, *, atomic_failure: bool = False) -> None:
        self.status = status
        self.atomic_failure = atomic_failure

    def initial_state(self, problem: Problem) -> OrionState:
        return OrionState(KnowledgeState(), SearchUniverseState(), MethodState("test"))

    def solve(self, problem: Problem, *, initial_state=None, trace_id=None):
        assert initial_state is not None
        final_state = initial_state.advance()
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
                    "1" * 64,
                    "2" * 64,
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
    assert len(store.episodes()) == 1
    episode = store.episodes()[0]
    assert episode.mechanic_id == "ORION_SOLVE.v1"
    assert episode.variation_signature == ("vocabulary-mask-a",)
    assert "solution_status:BLOCKED" in episode.failure_signature
    assert episode.residual_ids == ("coverage-open",)


def test_runtime_records_success_without_inventing_failure_signature():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime(
        _FakeSolver(SolutionStatus.SOLVED_VERIFIED), experience_store=store
    )
    runtime.solve(
        Problem("task:success", "Solve fixture."), variation_signature=("baseline",)
    )
    episode = store.episodes()[0]
    assert episode.outcome.value == "SUCCESS"
    assert episode.failure_signature == ()


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
    assert len(store.episodes()) == 2


def test_real_solver_trace_projects_every_mechanic_receipt_into_experience():
    store = InMemoryExperienceStore()
    runtime = OrionRuntime.from_providers(
        llm=CallableLLMProvider(
            lambda request: '{"queries":[]}', model_id="known-world"
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
    assert len(result.mechanic_experience_episode_ids) == len(result.trace.events)
    by_id = {episode.episode_id: episode for episode in store.episodes()}
    root = by_id[result.experience_episode_id]
    for event, episode_id in zip(
        result.trace.events,
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
            lambda request: '{"queries":[]}', model_id="guard-fixture"
        ),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        experience_store=store,
        guards=(guard,),
    )

    result = runtime.solve(
        Problem("task:guard-runtime", "Run the protected search guard.")
    )

    search_episode = next(
        episode for episode in store.episodes() if episode.mechanic_id == "SEARCH.v1"
    )
    assert calls == [("task:guard-runtime", 0)]
    assert guard.guard_id in search_episode.action_ids
    assert search_episode.source_receipt_id
    assert result.mechanic_experience_episode_ids


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
        if episode.mechanic_id == "ORION_SOLVE.v1"
    )
    assert failed.parent_run_id == root.run_id
