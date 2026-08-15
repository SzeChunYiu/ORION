from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine.trace import SolveTrace
from orion.providers.experience.memory import InMemoryExperienceStore
from orion.runtime import OrionRuntime


class _FakeSolver:
    def __init__(self, status: SolutionStatus) -> None:
        self.status = status

    def initial_state(self, problem: Problem) -> OrionState:
        return OrionState(KnowledgeState(), SearchUniverseState(), MethodState("test"))

    def solve(self, problem: Problem, *, initial_state=None):
        assert initial_state is not None
        final_state = initial_state.advance()
        return (
            Solution(
                problem.problem_id,
                self.status,
                "fixture",
                residual_ids=("coverage-open",) if self.status is SolutionStatus.BLOCKED else (),
                trace_id=f"trace:{problem.problem_id}",
            ),
            final_state,
            SolveTrace(f"trace:{problem.problem_id}", ()),
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
    runtime = OrionRuntime(_FakeSolver(SolutionStatus.SOLVED_VERIFIED), experience_store=store)
    runtime.solve(Problem("task:success", "Solve fixture."), variation_signature=("baseline",))
    episode = store.episodes()[0]
    assert episode.outcome.value == "SUCCESS"
    assert episode.failure_signature == ()
