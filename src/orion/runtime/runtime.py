from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from orion.core.claims import ClaimAuthority
from orion.core.evidence import evidence_record_fingerprint
from orion.core.problem import Problem
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import OrionState
from orion.engine.guards import MechanicGuard
from orion.engine.solver import OrionSolver, SolverConfig
from orion.engine.trace import SolveTrace
from orion.experience.model import EpisodeOutcome, TaskEpisode
from orion.experience.recording import episode_from_receipt
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
    mechanic_experience_episode_ids: tuple[str, ...] = ()


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

    def __init__(
        self,
        solver: OrionSolver,
        *,
        experience_store: ExperienceStore | None = None,
        producer_process_lineage_hash: str | None = None,
        evaluator_artifact_hash: str | None = None,
    ) -> None:
        self._solver = solver
        self._experience_store = experience_store
        self._producer_process_lineage_hash = producer_process_lineage_hash
        self._evaluator_artifact_hash = evaluator_artifact_hash

    @classmethod
    def from_providers(
        cls,
        *,
        llm: LLMProvider,
        retrieval: RetrievalProvider,
        verification: VerificationProvider,
        experience_store: ExperienceStore | None = None,
        config: SolverConfig | None = None,
        guards: tuple[MechanicGuard, ...] = (),
        producer_process_lineage_hash: str | None = None,
        evaluator_artifact_hash: str | None = None,
    ) -> OrionRuntime:
        reasoner = LLMResearchReasoner(llm)
        solver = OrionSolver(
            reasoner=reasoner,
            retrieval=retrieval,
            verification=verification,
            config=config,
            guards=guards,
        )
        return cls(
            solver,
            experience_store=experience_store,
            producer_process_lineage_hash=producer_process_lineage_hash,
            evaluator_artifact_hash=evaluator_artifact_hash,
        )

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
        evaluation_epoch_id: str,
        split_id: str,
        producer_process_lineage_hash: str | None,
        evaluator_artifact_hash: str | None,
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
        action_ids = tuple(
            dict.fromkeys(
                action_id
                for event in trace.events
                if event.receipt.mechanic_id == "ORION_SOLVE.v1"
                for action_id in event.receipt.action_ids
            )
        ) or (
            "ORION_SOLVE",
        )
        observations = tuple(
            dict.fromkeys(
                tuple(f"evidence:{item}" for item in solution.evidence_ids)
                + tuple(f"residual:{item}" for item in solution.residual_ids)
                + tuple(
                    f"trace:{index}:{event.operator.value}"
                    for index, event in enumerate(trace.events)
                )
            )
        )
        failure_signature = ()
        if solution.status is not SolutionStatus.SOLVED_VERIFIED:
            failure_signature = tuple(
                dict.fromkeys(
                    (f"solution_status:{solution.status.value}", *solution.residual_ids)
                )
            )
        episode = TaskEpisode(
            episode_id=episode_id,
            task_id=problem.problem_id,
            run_id=run_id,
            parent_run_id=None,
            evaluation_epoch_id=evaluation_epoch_id,
            split_id=split_id,
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
            evidence_bindings=tuple(
                (
                    evidence_id,
                    evidence_record_fingerprint(
                        next(
                            record
                            for record in final_state.knowledge.evidence
                            if record.evidence_id == evidence_id
                        )
                    ),
                )
                for evidence_id in solution.evidence_ids
            ),
            post_state_hash=post_hash,
            timestamp=datetime.now(UTC).isoformat(),
            producer_process_lineage_hash=producer_process_lineage_hash,
            evaluator_artifact_hash=evaluator_artifact_hash,
        )
        self._experience_store.append(episode)
        return episode_id

    def _record_mechanic_episodes(
        self,
        *,
        problem: Problem,
        variation_signature: tuple[str, ...],
        trace: SolveTrace,
        root_run_id: str,
        evaluation_epoch_id: str,
        split_id: str,
        producer_process_lineage_hash: str | None,
        evaluator_artifact_hash: str | None,
    ) -> tuple[str, ...]:
        if self._experience_store is None:
            return ()
        episode_ids: list[str] = []
        problem_signature = tuple(
            item
            for item in (
                problem.question,
                problem.scope,
                *problem.initial_domain_ids,
                *problem.success_criteria,
            )
            if item
        )
        for index, event in enumerate(trace.events):
            if not event.receipt.experience_eligible:
                continue
            mechanic_run_id = f"{root_run_id}:mechanic:{index}"
            episode_id = (
                "episode:"
                + hashlib.sha256(
                    f"{mechanic_run_id}|{event.receipt.receipt_id}".encode()
                ).hexdigest()
            )
            episode = episode_from_receipt(
                event.receipt,
                episode_id=episode_id,
                task_id=problem.problem_id,
                run_id=mechanic_run_id,
                parent_run_id=root_run_id,
                evaluation_epoch_id=evaluation_epoch_id,
                split_id=split_id,
                problem_signature=problem_signature,
                variation_signature=variation_signature,
                pre_state_hash=event.pre_state_hash,
                post_state_hash=event.post_state_hash,
                timestamp=datetime.now(UTC).isoformat(),
                producer_process_lineage_hash=producer_process_lineage_hash,
                evaluator_artifact_hash=evaluator_artifact_hash,
            )
            self._experience_store.append(episode)
            episode_ids.append(episode_id)
        return tuple(episode_ids)

    def solve(
        self,
        problem: Problem,
        *,
        initial_state: OrionState | None = None,
        variation_signature: tuple[str, ...] = (),
        evaluation_epoch_id: str = "evaluation:unfrozen",
        split_id: str = "split:unassigned",
    ) -> RuntimeResult:
        # Treat only ``None`` as absence so caller-supplied state identity is
        # never selected by incidental truthiness semantics.
        start_state = (
            initial_state
            if initial_state is not None
            else self._solver.initial_state(problem)
        )
        # Capture the requested endpoint before handing it to the solver.
        start_state_hash = _state_hash(start_state)
        run_id = uuid4().hex
        producer_process_lineage_hash = self._producer_process_lineage_hash
        evaluator_artifact_hash = self._evaluator_artifact_hash
        trace_id = f"trace:{problem.problem_id}:{run_id}"
        solution, final_state, trace = self._solver.solve(
            problem,
            initial_state=start_state,
            trace_id=trace_id,
        )
        if trace.trace_id != trace_id or solution.trace_id != trace_id:
            raise ValueError("solver result is not bound to the requested trace identity")
        if solution.problem_id != problem.problem_id:
            raise ValueError("solver result is not bound to the requested problem")
        missing_solution_evidence = tuple(
            evidence_id
            for evidence_id in solution.evidence_ids
            if evidence_id not in final_state.knowledge.evidence_ids
        )
        if missing_solution_evidence:
            raise ValueError(
                "solution evidence is absent from the returned final state: "
                + ",".join(missing_solution_evidence)
            )
        if solution.status is SolutionStatus.SOLVED_VERIFIED:
            verified_support = {
                evidence_id
                for claim in final_state.knowledge.claims
                if claim.authority is ClaimAuthority.VERIFIED
                for evidence_id in claim.evidence_ids
            }
            unsupported = tuple(
                evidence_id
                for evidence_id in solution.evidence_ids
                if evidence_id not in verified_support
            )
            if unsupported:
                raise ValueError(
                    "verified solution evidence lacks a verified supporting claim: "
                    + ",".join(unsupported)
                )
        trace.validate_endpoints(
            pre_state_hash=start_state_hash,
            post_state_hash=_state_hash(final_state),
        )
        mechanic_episode_ids = self._record_mechanic_episodes(
            problem=problem,
            variation_signature=variation_signature,
            trace=trace,
            root_run_id=run_id,
            evaluation_epoch_id=evaluation_epoch_id,
            split_id=split_id,
            producer_process_lineage_hash=producer_process_lineage_hash,
            evaluator_artifact_hash=evaluator_artifact_hash,
        )
        episode_id = self._record_root_episode(
            problem=problem,
            variation_signature=variation_signature,
            initial_state=start_state,
            solution=solution,
            final_state=final_state,
            trace=trace,
            run_id=run_id,
            evaluation_epoch_id=evaluation_epoch_id,
            split_id=split_id,
            producer_process_lineage_hash=producer_process_lineage_hash,
            evaluator_artifact_hash=evaluator_artifact_hash,
        )
        return RuntimeResult(
            solution=solution,
            final_state=final_state,
            trace=trace,
            experience_episode_id=episode_id,
            mechanic_experience_episode_ids=mechanic_episode_ids,
        )
