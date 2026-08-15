from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from orion.core.problem import Problem
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import OrionState
from orion.engine.solver import OrionSolver, SolverConfig
from orion.engine.trace import SolveTrace
from orion.experience.model import EpisodeOutcome, TaskEpisode
from orion.providers.experience.base import ExperienceStore
from orion.providers.llm.base import LLMProvider
from orion.providers.reasoner.llm import LLMResearchReasoner
from orion.providers.retrieval.base import RetrievalProvider
from orion.providers.verification.base import VerificationProvider


@dataclass(frozen=True)
class RuntimeResult:
    solution: Solution
    final_state: OrionState
    trace: SolveTrace
    experience_episode_id: str | None = None


_OUTCOME_BY_STATUS = {
    SolutionStatus.SOLVED_VERIFIED: EpisodeOutcome.SUCCESS,
    SolutionStatus.PROVISIONAL: EpisodeOutcome.PARTIAL_SUCCESS,
    SolutionStatus.BLOCKED: EpisodeOutcome.BLOCKED,
    SolutionStatus.CANNOT_CHECK: EpisodeOutcome.CANNOT_CHECK,
}


def _state_hash(state: OrionState) -> str:
    return hashlib.sha256(repr(state).encode("utf-8")).hexdigest()


def _episode_id(
    run_id: str,
    problem: Problem,
    variation_signature: tuple[str, ...],
    pre_state_hash: str,
    post_state_hash: str,
    solution: Solution,
    trace: SolveTrace,
) -> str:
    payload = "|".join(
        (
            run_id,
            problem.problem_id,
            repr(variation_signature),
            pre_state_hash,
            post_state_hash,
            solution.status.value,
            repr(tuple(item.value for item in trace.operator_sequence)),
        )
    )
    return "episode:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


class OrionRuntime:
    """Composition root for a running ORION instance.

    External providers enter here. The engine and scientific authority semantics remain
    independent of the concrete LLM, retriever, verifier or experience persistence.
    """

    def __init__(self, solver: OrionSolver, *, experience_store: ExperienceStore | None = None) -> None:
        self._solver = solver
        self._experience_store = experience_store

    @classmethod
    def from_providers(
        cls,
        *,
        llm: LLMProvider,
        retrieval: RetrievalProvider,
        verification: VerificationProvider,
        experience_store: ExperienceStore | None = None,
        config: SolverConfig | None = None,
    ) -> OrionRuntime:
        reasoner = LLMResearchReasoner(llm)
        solver = OrionSolver(
            reasoner=reasoner,
            retrieval=retrieval,
            verification=verification,
            config=config,
        )
        return cls(solver, experience_store=experience_store)

    def _record_root_episode(
        self,
        *,
        problem: Problem,
        variation_signature: tuple[str, ...],
        initial_state: OrionState,
        solution: Solution,
        final_state: OrionState,
        trace: SolveTrace,
        run_id: str,
    ) -> str | None:
        if self._experience_store is None:
            return None
        pre_hash = _state_hash(initial_state)
        post_hash = _state_hash(final_state)
        episode_id = _episode_id(
            run_id,
            problem,
            variation_signature,
            pre_hash,
            post_hash,
            solution,
            trace,
        )
        action_ids = tuple(event.operator.value for event in trace.events) or ("ORION_SOLVE",)
        observations = tuple(
            dict.fromkeys(
                tuple(f"evidence:{item}" for item in solution.evidence_ids)
                + tuple(f"residual:{item}" for item in solution.residual_ids)
                + tuple(f"trace:{index}:{event.operator.value}" for index, event in enumerate(trace.events))
            )
        )
        failure_signature = ()
        if solution.status is not SolutionStatus.SOLVED_VERIFIED:
            failure_signature = tuple(
                dict.fromkeys((f"solution_status:{solution.status.value}", *solution.residual_ids))
            )
        episode = TaskEpisode(
            episode_id=episode_id,
            task_id=problem.problem_id,
            mechanic_id="ORION_SOLVE.v1",
            problem_signature=tuple(
                item
                for item in (
                    problem.question,
                    problem.scope,
                    *problem.initial_domain_ids,
                    *problem.success_criteria,
                )
                if item
            ),
            variation_signature=variation_signature,
            pre_state_hash=pre_hash,
            action_ids=action_ids,
            observation_ids=observations,
            outcome=_OUTCOME_BY_STATUS[solution.status],
            failure_signature=failure_signature,
            residual_ids=solution.residual_ids,
            evidence_ids=solution.evidence_ids,
            post_state_hash=post_hash,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self._experience_store.append(episode)
        return episode_id

    def solve(
        self,
        problem: Problem,
        *,
        initial_state: OrionState | None = None,
        variation_signature: tuple[str, ...] = (),
    ) -> RuntimeResult:
        start_state = initial_state or self._solver.initial_state(problem)
        run_id = uuid4().hex
        solution, final_state, trace = self._solver.solve(problem, initial_state=start_state)
        episode_id = self._record_root_episode(
            problem=problem,
            variation_signature=variation_signature,
            initial_state=start_state,
            solution=solution,
            final_state=final_state,
            trace=trace,
            run_id=run_id,
        )
        return RuntimeResult(
            solution=solution,
            final_state=final_state,
            trace=trace,
            experience_episode_id=episode_id,
        )
