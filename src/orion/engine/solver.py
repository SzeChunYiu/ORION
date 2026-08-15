from __future__ import annotations

from dataclasses import dataclass, replace

from orion.core.claims import ClaimAuthority
from orion.core.history import IterationRecord
from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine.cycle import CycleOperator
from orion.engine.operators.absorb import AbsorbOperator
from orion.engine.operators.detect import DetectOperator
from orion.engine.operators.diagnose import DiagnoseOperator
from orion.engine.operators.frame import FrameOperator
from orion.engine.operators.reconstruct import ReconstructOperator
from orion.engine.operators.reframe import ReframeOperator
from orion.engine.operators.reopen import ReopenOperator
from orion.engine.operators.search import SearchOperator
from orion.engine.trace import SolveTrace, TraceEvent
from orion.providers.reasoner.base import ResearchReasoner
from orion.providers.retrieval.base import RetrievalProvider
from orion.providers.verification.base import VerificationProvider


@dataclass(frozen=True)
class SolverConfig:
    max_iterations: int = 6
    search_limit_per_query: int = 8
    require_verified_answer: bool = True


class OrionSolver:
    """Minimum governed ORION problem-solving loop.

    The solver owns orchestration. LLMs/retrievers/verifiers are replaceable providers.
    """

    def __init__(
        self,
        *,
        reasoner: ResearchReasoner,
        retrieval: RetrievalProvider,
        verification: VerificationProvider,
        config: SolverConfig | None = None,
    ) -> None:
        self._reasoner = reasoner
        self._config = config or SolverConfig()
        self._frame = FrameOperator()
        self._search = SearchOperator(reasoner, retrieval, limit_per_query=self._config.search_limit_per_query)
        self._absorb = AbsorbOperator(reasoner, verification)
        self._reconstruct = ReconstructOperator(reasoner)
        self._detect = DetectOperator()
        self._diagnose = DiagnoseOperator(reasoner)
        self._reframe = ReframeOperator(reasoner)
        self._reopen = ReopenOperator()

    def initial_state(self, problem: Problem) -> OrionState:
        return OrionState(
            knowledge=KnowledgeState(),
            search_universe=SearchUniverseState(active_domain_ids=problem.initial_domain_ids),
            method=MethodState(
                method_version="orion-minimum-autonomous-v0",
                operator_ids=(
                    "FRAME.v1",
                    "SEARCH.v1",
                    "ABSORB.v1",
                    "RECONSTRUCT.v1",
                    "DETECT.v1",
                    "DIAGNOSE.v1",
                    "REFRAME.v1",
                    "REOPEN.v1",
                ),
                evaluator_id="external-verification-provider",
            ),
        )

    def solve(
        self,
        problem: Problem,
        *,
        initial_state: OrionState | None = None,
    ) -> tuple[Solution, OrionState, SolveTrace]:
        state = initial_state or self.initial_state(problem)
        events: list[TraceEvent] = []
        trace_id = f"trace:{problem.problem_id}"

        frame = self._frame.run(problem, state)
        state = frame.state
        events.append(TraceEvent(CycleOperator.FRAME, state.epoch, f"frame={frame.output.frame_id}", frame.transition))

        for iteration in range(self._config.max_iterations):
            before_claims = {claim.claim_id for claim in state.knowledge.claims}
            before_evidence = set(state.knowledge.evidence_ids)
            before_domains = set(state.search_universe.active_domain_ids)

            search = self._search.run(problem, state)
            state = search.state
            events.append(
                TraceEvent(
                    CycleOperator.SEARCH,
                    state.epoch,
                    f"queries={len(search.output.queries)} items={len(search.output.items)}",
                    search.transition,
                )
            )

            absorb = self._absorb.run(problem, state, search.output)
            state = absorb.state
            events.append(TraceEvent(CycleOperator.ABSORB, state.epoch, f"contributions={len(absorb.output)}", absorb.transition))

            reconstruct = self._reconstruct.run(problem, state)
            state = reconstruct.state
            events.append(TraceEvent(CycleOperator.RECONSTRUCT, state.epoch, reconstruct.output.portrait_id, reconstruct.transition))

            detect = self._detect.run(problem, state)
            state = detect.state
            events.append(TraceEvent(CycleOperator.DETECT, state.epoch, f"residuals={len(detect.output)}", detect.transition))

            material = tuple(residual for residual in detect.output if residual.material)
            if not material:
                verified_claims = tuple(
                    claim for claim in state.knowledge.claims if claim.authority is ClaimAuthority.VERIFIED
                )
                if self._config.require_verified_answer and not verified_claims:
                    solution = Solution(
                        problem_id=problem.problem_id,
                        status=SolutionStatus.CANNOT_CHECK,
                        answer="No verified evidence supports a final answer.",
                        evidence_ids=state.knowledge.evidence_ids,
                        residual_ids=state.knowledge.residual_ids,
                        iterations=iteration + 1,
                        trace_id=trace_id,
                    )
                else:
                    answer = self._reasoner.compose_answer(problem, state)
                    solution = Solution(
                        problem_id=problem.problem_id,
                        status=SolutionStatus.SOLVED_VERIFIED if verified_claims else SolutionStatus.PROVISIONAL,
                        answer=answer,
                        evidence_ids=tuple(
                            dict.fromkeys(
                                evidence_id
                                for claim in verified_claims
                                for evidence_id in claim.evidence_ids
                            )
                        ),
                        iterations=iteration + 1,
                        trace_id=trace_id,
                    )
                return solution, state, SolveTrace(trace_id, tuple(events))

            changed_coordinates: list[str] = []
            blocked_residual_ids: list[str] = []
            for residual in material:
                diagnosis_result = self._diagnose.run(residual, problem, state)
                events.append(
                    TraceEvent(
                        CycleOperator.DIAGNOSE,
                        state.epoch,
                        diagnosis_result.output.rationale,
                        diagnosis_result.transition,
                    )
                )
                try:
                    reframe_result = self._reframe.run(residual, diagnosis_result.output, problem, state)
                except (ValueError, PermissionError):
                    blocked_residual_ids.append(residual.residual_id)
                    continue
                state = reframe_result.state
                changed_coordinates.extend(reframe_result.transition.changed_coordinates)
                events.append(TraceEvent(CycleOperator.REFRAME, state.epoch, reframe_result.output.note, reframe_result.transition))

            if blocked_residual_ids:
                solution = Solution(
                    problem_id=problem.problem_id,
                    status=SolutionStatus.BLOCKED,
                    answer="ORION could not safely localize or authorize the required reframe.",
                    evidence_ids=state.knowledge.evidence_ids,
                    residual_ids=tuple(blocked_residual_ids),
                    iterations=iteration + 1,
                    trace_id=trace_id,
                )
                return solution, state, SolveTrace(trace_id, tuple(events))

            reopen = self._reopen.run(
                state,
                changed_coordinates=tuple(dict.fromkeys(changed_coordinates)),
                reason=f"material reframe at iteration {iteration}",
            )
            state = reopen.state
            events.append(TraceEvent(CycleOperator.REOPEN, state.epoch, f"staled={len(reopen.output)}", reopen.transition))

            new_claims = tuple(
                claim.claim_id for claim in state.knowledge.claims if claim.claim_id not in before_claims
            )
            new_evidence = tuple(
                evidence_id for evidence_id in state.knowledge.evidence_ids if evidence_id not in before_evidence
            )
            new_domains = tuple(
                domain_id for domain_id in state.search_universe.active_domain_ids if domain_id not in before_domains
            )
            record = IterationRecord(
                iteration=iteration,
                new_claim_ids=new_claims,
                new_evidence_ids=new_evidence,
                new_domain_ids=new_domains,
                residual_ids=tuple(residual.residual_id for residual in material),
                changed_coordinates=tuple(dict.fromkeys(changed_coordinates)),
            )
            state = replace(state, iterations=(*state.iterations, record), epoch=state.epoch + 1)
            recurse_transition = reopen.transition.__class__(
                operator=CycleOperator.RECURSE,
                input_epoch=state.epoch - 1,
                output_epoch=state.epoch,
                residual_ids=record.residual_ids,
            )
            events.append(TraceEvent(CycleOperator.RECURSE, state.epoch, f"iteration={iteration + 1}", recurse_transition))

        solution = Solution(
            problem_id=problem.problem_id,
            status=SolutionStatus.CANNOT_CHECK,
            answer="Resource bound reached with material residuals still open.",
            evidence_ids=state.knowledge.evidence_ids,
            residual_ids=state.knowledge.residual_ids,
            iterations=self._config.max_iterations,
            trace_id=trace_id,
        )
        return solution, state, SolveTrace(trace_id, tuple(events))
