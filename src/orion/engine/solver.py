from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from functools import partial
from time import perf_counter
from typing import TypeVar
from uuid import uuid4

from orion.core.claims import ClaimAuthority
from orion.core.evidence import EvidenceRecord, evidence_record_fingerprint
from orion.core.history import IterationRecord
from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.search_universe import SearchUniverseState
from orion.core.solution import Solution, SolutionStatus
from orion.core.state import KnowledgeState, OrionState
from orion.engine.cycle import CycleOperator, Transition
from orion.engine.guards import MechanicGuard
from orion.engine.operators.absorb import AbsorbOperator
from orion.engine.operators.detect import DetectOperator
from orion.engine.operators.diagnose import DiagnoseOperator
from orion.engine.operators.frame import FrameOperator
from orion.engine.operators.reconstruct import ReconstructOperator
from orion.engine.operators.reframe import ReframeOperator
from orion.engine.operators.reopen import ReopenOperator
from orion.engine.operators.saturate import SaturateOperator, SaturationBasis
from orion.engine.operators.search import SearchOperator
from orion.engine.trace import MECHANIC_ID_BY_OPERATOR, SolveTrace, TraceEvent
from orion.mechanics.receipt import MechanicReceipt, MechanicRunStatus
from orion.providers.reasoner.base import ResearchReasoner

from .deterministic_route import attempt_deterministic_route
from .deterministic_solver import CompiledProblem, DeterministicProblemSolver
from orion.providers.retrieval.base import RetrievalProvider
from orion.providers.verification.base import VerificationProvider
from orion.registry import CORE_OPERATOR_IDS, FRAMEWORK_VERSION

_T = TypeVar("_T")


class _MechanicGuardEvaluationError(RuntimeError):
    """Distinguish a guard crash from a target-operator crash."""

    def __init__(self, guard_id: str, cause: Exception) -> None:
        super().__init__(f"mechanic guard {guard_id} failed: {cause}")
        self.guard_id = guard_id
        self.cause = cause


@dataclass(frozen=True)
class SolverConfig:
    max_iterations: int = 8
    search_limit_per_query: int = 8
    require_verified_answer: bool = True
    saturation_basis: SaturationBasis = field(default_factory=SaturationBasis)


class OrionSolver:
    """Minimum governed ORION problem-solving loop.

    Finalization requires verified evidence when configured and bounded saturation of
    knowledge, search-universe and formulation under the frozen saturation basis.
    """

    def __init__(
        self,
        *,
        reasoner: ResearchReasoner,
        retrieval: RetrievalProvider,
        verification: VerificationProvider,
        config: SolverConfig | None = None,
        guards: tuple[MechanicGuard, ...] = (),
        deterministic: DeterministicProblemSolver | None = None,
        compiled_problems: Mapping[str, CompiledProblem] | None = None,
    ) -> None:
        self._reasoner = reasoner
        # When a problem has a typed model, it is closed by verified transition
        # search and the reasoner is never consulted. Uncompiled problems keep
        # the existing route; nothing is silently delegated.
        self._deterministic = deterministic
        self._compiled_problems = dict(compiled_problems or {})
        self._config = config or SolverConfig()
        self._frame = FrameOperator()
        self._search = SearchOperator(
            reasoner, retrieval, limit_per_query=self._config.search_limit_per_query
        )
        self._absorb = AbsorbOperator(reasoner, verification)
        self._reconstruct = ReconstructOperator(reasoner)
        self._detect = DetectOperator()
        self._diagnose = DiagnoseOperator(reasoner)
        self._reframe = ReframeOperator(reasoner)
        self._reopen = ReopenOperator()
        self._saturate = SaturateOperator(self._config.saturation_basis)
        self._guards = guards
        guard_ids = [guard.guard_id for guard in guards]
        if len(set(guard_ids)) != len(guard_ids):
            raise ValueError("mechanic guard ids must be unique")
        known_mechanics = set(MECHANIC_ID_BY_OPERATOR.values())
        if any(guard.mechanic_id not in known_mechanics for guard in guards):
            raise ValueError("mechanic guard target must be a runtime mechanic")

    def initial_state(self, problem: Problem) -> OrionState:
        return OrionState(
            knowledge=KnowledgeState(),
            search_universe=SearchUniverseState(
                active_domain_ids=problem.initial_domain_ids
            ),
            method=MethodState(
                method_version=FRAMEWORK_VERSION,
                operator_ids=CORE_OPERATOR_IDS,
                evaluator_id="external-verification-provider",
            ),
        )

    def bind_initial_state(self, problem: Problem, state: OrionState) -> OrionState:
        """Prepare a caller-supplied state before the runtime captures its endpoint.

        The kernel solver has no additional state bindings, so its implementation is
        deliberately the identity.  Solver variants override this hook when their
        method contract adds deterministic bindings such as paper-parity navigation.
        """

        return state

    @staticmethod
    def _state_hash(state: OrionState) -> str:
        return hashlib.sha256(repr(state).encode("utf-8")).hexdigest()

    def _attempt_mechanic(
        self,
        operator: CycleOperator,
        problem: Problem,
        state: OrionState,
        action: Callable[[], _T],
    ) -> tuple[
        _T | None,
        float,
        Exception | None,
        tuple[str, ...],
        tuple[str, ...],
    ]:
        """Evaluate current-state guards immediately before one invocation."""

        started_at = perf_counter()
        invoked_guard_ids: list[str] = []
        mechanic_id = MECHANIC_ID_BY_OPERATOR[operator]
        for guard in self._guards:
            if guard.mechanic_id != mechanic_id:
                continue
            invoked_guard_ids.append(guard.guard_id)
            try:
                guard_result = guard.evaluate(problem, state)
            except Exception as exc:  # noqa: BLE001 - guard failure is evidence
                return (
                    None,
                    perf_counter() - started_at,
                    _MechanicGuardEvaluationError(guard.guard_id, exc),
                    tuple(invoked_guard_ids),
                    (),
                )
            if not guard_result.passed:
                return (
                    None,
                    perf_counter() - started_at,
                    None,
                    tuple(invoked_guard_ids),
                    guard_result.residual_ids,
                )
        try:
            result = action()
        except Exception as exc:  # noqa: BLE001 - operator failure is evidence
            return (
                None,
                perf_counter() - started_at,
                exc,
                tuple(invoked_guard_ids),
                (),
            )
        return (
            result,
            perf_counter() - started_at,
            None,
            tuple(invoked_guard_ids),
            (),
        )

    @staticmethod
    def _attempt_action(
        action: Callable[[], _T],
    ) -> tuple[_T | None, float, Exception | None]:
        """Attempt an internal action without re-entering the root guard."""

        started_at = perf_counter()
        try:
            return action(), perf_counter() - started_at, None
        except Exception as exc:  # noqa: BLE001 - internal failure is evidence
            return None, perf_counter() - started_at, exc

    @classmethod
    def _failure_from_attempt(
        cls,
        *,
        problem: Problem,
        state: OrionState,
        events: list[TraceEvent],
        trace_id: str,
        operator: CycleOperator,
        error: Exception | None,
        guard_residuals: tuple[str, ...],
        invoked_guard_ids: tuple[str, ...],
        latency_seconds: float,
        iterations: int,
    ) -> tuple[Solution, OrionState, SolveTrace] | None:
        if guard_residuals:
            return cls._operator_failure(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=operator,
                error=RuntimeError("mechanic guard rejected execution"),
                latency_seconds=latency_seconds,
                iterations=iterations,
                action_ids=invoked_guard_ids,
                status=MechanicRunStatus.BLOCKED,
                residual_ids=guard_residuals,
                failure_signature=("mechanic_guard_rejected",),
                operator_invoked=False,
            )
        if isinstance(error, _MechanicGuardEvaluationError):
            return cls._operator_failure(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=operator,
                error=error.cause,
                latency_seconds=latency_seconds,
                iterations=iterations,
                action_ids=invoked_guard_ids,
                residual_ids=(
                    f"mechanic-guard-exception:{operator.value}:{type(error.cause).__name__}",
                ),
                failure_signature=(
                    "mechanic_guard_exception",
                    f"exception_type:{type(error.cause).__name__}",
                ),
                operator_invoked=False,
            )
        if error is not None:
            return cls._operator_failure(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=operator,
                error=error,
                latency_seconds=latency_seconds,
                iterations=iterations,
                action_ids=invoked_guard_ids,
            )
        return None

    @classmethod
    def _trace_event(
        cls,
        *,
        trace_id: str,
        index: int,
        operator: CycleOperator,
        before_state: OrionState,
        after_state: OrionState,
        summary: str,
        transition: Transition,
        status: MechanicRunStatus = MechanicRunStatus.SUCCEEDED,
        failure_signature: tuple[str, ...] = (),
        latency_seconds: float | None = None,
        action_ids: tuple[str, ...] = (),
        evidence_bindings: tuple[tuple[str, str], ...] = (),
        operator_invoked: bool = True,
        experience_eligible: bool = True,
    ) -> TraceEvent:
        if transition.input_epoch != before_state.epoch:
            raise ValueError("trace transition input epoch does not match pre-state")
        if transition.output_epoch != after_state.epoch:
            raise ValueError("trace transition output epoch does not match post-state")
        evidence_by_id = {
            record.evidence_id: record for record in after_state.knowledge.evidence
        }
        supplied_bindings = dict(evidence_bindings)
        missing_evidence = tuple(
            evidence_id
            for evidence_id in transition.evidence_ids
            if evidence_id not in evidence_by_id
            and evidence_id not in supplied_bindings
        )
        if missing_evidence:
            raise ValueError(
                "trace transition references evidence absent from post-state: "
                + ",".join(missing_evidence)
            )
        residual_ids = transition.residual_ids
        receipt = MechanicReceipt(
            receipt_id=f"{trace_id}:receipt:{index}:{operator.value}",
            mechanic_id=MECHANIC_ID_BY_OPERATOR[operator],
            status=status,
            action_ids=(
                (*((operator.value,) if operator_invoked else ()), *action_ids)
            ),
            handoff_values=(
                ("changed_coordinates", ",".join(transition.changed_coordinates)),
            ),
            residual_ids=residual_ids,
            failure_signature=failure_signature,
            evidence_ids=transition.evidence_ids,
            evidence_bindings=tuple(
                (
                    evidence_id,
                    supplied_bindings.get(evidence_id)
                    or evidence_record_fingerprint(evidence_by_id[evidence_id]),
                )
                for evidence_id in transition.evidence_ids
            ),
            provenance_ids=transition.scientific_authority_certificate_ids,
            latency_seconds=latency_seconds,
            experience_eligible=experience_eligible,
        )
        return TraceEvent(
            operator,
            after_state.epoch,
            summary,
            transition,
            receipt,
            cls._state_hash(before_state),
            cls._state_hash(after_state),
        )

    @classmethod
    def _operator_failure(
        cls,
        *,
        problem: Problem,
        state: OrionState,
        events: list[TraceEvent],
        trace_id: str,
        operator: CycleOperator,
        error: Exception,
        latency_seconds: float,
        iterations: int,
        action_ids: tuple[str, ...] = (),
        status: MechanicRunStatus = MechanicRunStatus.FAILED,
        residual_ids: tuple[str, ...] = (),
        failure_signature: tuple[str, ...] = (),
        operator_invoked: bool = True,
    ) -> tuple[Solution, OrionState, SolveTrace]:
        if not residual_ids:
            residual_ids = (
                f"operator-exception:{operator.value}:{type(error).__name__}",
            )
        if not failure_signature:
            failure_signature = (
                "operator_exception",
                f"exception_type:{type(error).__name__}",
            )
        transition = Transition(
            operator=operator,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
            residual_ids=residual_ids,
        )
        event = cls._trace_event(
            trace_id=trace_id,
            index=len(events),
            operator=operator,
            before_state=state,
            after_state=state,
            summary=f"failed:{type(error).__name__}",
            transition=transition,
            status=status,
            failure_signature=failure_signature,
            latency_seconds=latency_seconds,
            action_ids=action_ids,
            operator_invoked=operator_invoked,
        )
        trace = SolveTrace(trace_id, (*events, event))
        solution = Solution(
            problem_id=problem.problem_id,
            status=SolutionStatus.BLOCKED,
            answer=f"ORION operator {operator.value} failed closed; inspect its immutable receipt.",
            evidence_ids=state.knowledge.evidence_ids,
            residual_ids=residual_ids,
            iterations=iterations,
            trace_id=trace_id,
        )
        return solution, state, trace

    def _record_iteration(
        self,
        state: OrionState,
        *,
        iteration: int,
        before_claims: set[str],
        before_evidence: set[str],
        before_domains: set[str],
        residual_ids: tuple[str, ...],
        changed_coordinates: tuple[str, ...],
        route_kind_ids: tuple[str, ...],
    ) -> OrionState:
        record = IterationRecord(
            iteration=iteration,
            new_claim_ids=tuple(
                claim.claim_id
                for claim in state.knowledge.claims
                if claim.claim_id not in before_claims
            ),
            new_evidence_ids=tuple(
                evidence_id
                for evidence_id in state.knowledge.evidence_ids
                if evidence_id not in before_evidence
            ),
            new_domain_ids=tuple(
                domain_id
                for domain_id in state.search_universe.active_domain_ids
                if domain_id not in before_domains
            ),
            residual_ids=residual_ids,
            changed_coordinates=changed_coordinates,
            route_kind_ids=route_kind_ids,
        )
        return replace(
            state, iterations=(*state.iterations, record), epoch=state.epoch + 1
        )

    def solve(
        self,
        problem: Problem,
        *,
        initial_state: OrionState | None = None,
        trace_id: str | None = None,
    ) -> tuple[Solution, OrionState, SolveTrace]:
        # Only ``None`` requests construction of a fresh state; preserve the
        # identity of every caller-supplied state explicitly.
        state = (
            initial_state
            if initial_state is not None
            else self.initial_state(problem)
        )
        events: list[TraceEvent] = []
        trace_id = trace_id or f"trace:{problem.problem_id}:{uuid4().hex}"

        route = attempt_deterministic_route(
            problem,
            self._compiled_problems.get(problem.problem_id),
            self._deterministic,
        )
        if route.solution is not None:
            self._last_route = route
            return route.solution, state, SolveTrace(trace_id=trace_id, events=())
        self._last_route = route

        # ORION_SOLVE is one guarded root invocation, not merely the later
        # iteration-record/final-composition steps that share its RECURSE receipt
        # identity.  Evaluate its guard before FRAME or any provider can run.
        _, latency_seconds, error, invoked_guard_ids, guard_residuals = (
            self._attempt_mechanic(
                CycleOperator.RECURSE,
                problem,
                state,
                lambda: True,
            )
        )
        failure = self._failure_from_attempt(
            problem=problem,
            state=state,
            events=events,
            trace_id=trace_id,
            operator=CycleOperator.RECURSE,
            error=error,
            guard_residuals=guard_residuals,
            invoked_guard_ids=invoked_guard_ids,
            latency_seconds=latency_seconds,
            iterations=0,
        )
        if failure is not None:
            return failure
        root_transition = Transition(
            operator=CycleOperator.RECURSE,
            input_epoch=state.epoch,
            output_epoch=state.epoch,
        )
        events.append(
            self._trace_event(
                trace_id=trace_id,
                index=len(events),
                operator=CycleOperator.RECURSE,
                before_state=state,
                after_state=state,
                summary="solve_started",
                transition=root_transition,
                latency_seconds=latency_seconds,
                action_ids=invoked_guard_ids,
                experience_eligible=False,
            )
        )

        before_operator = state
        frame, latency_seconds, error, invoked_guard_ids, guard_residuals = (
            self._attempt_mechanic(
                CycleOperator.FRAME,
                problem,
                state,
                lambda: self._frame.run(problem, state),
            )
        )
        failure = self._failure_from_attempt(
            problem=problem,
            state=state,
            events=events,
            trace_id=trace_id,
            operator=CycleOperator.FRAME,
            error=error,
            guard_residuals=guard_residuals,
            invoked_guard_ids=invoked_guard_ids,
            latency_seconds=latency_seconds,
            iterations=0,
        )
        if failure is not None:
            return failure
        assert frame is not None
        state = frame.state
        events.append(
            self._trace_event(
                trace_id=trace_id,
                index=len(events),
                operator=CycleOperator.FRAME,
                before_state=before_operator,
                after_state=state,
                summary=f"frame={frame.output.frame_id}",
                transition=frame.transition,
                latency_seconds=latency_seconds,
                action_ids=invoked_guard_ids,
            )
        )

        last_saturation_reasons: tuple[str, ...] = ()
        for iteration in range(self._config.max_iterations):
            before_claims = {claim.claim_id for claim in state.knowledge.claims}
            before_evidence = set(state.knowledge.evidence_ids)
            before_domains = set(state.search_universe.active_domain_ids)

            before_operator = state
            search, latency_seconds, error, invoked_guard_ids, guard_residuals = (
                self._attempt_mechanic(
                    CycleOperator.SEARCH,
                    problem,
                    state,
                    lambda state=state: self._search.run(problem, state),
                )
            )
            failure = self._failure_from_attempt(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=CycleOperator.SEARCH,
                error=error,
                guard_residuals=guard_residuals,
                invoked_guard_ids=invoked_guard_ids,
                latency_seconds=latency_seconds,
                iterations=iteration,
            )
            if failure is not None:
                return failure
            assert search is not None
            state = search.state
            current_route_kinds = tuple(
                dict.fromkeys(query.route_kind.value for query in search.output.queries)
            )
            events.append(
                self._trace_event(
                    trace_id=trace_id,
                    index=len(events),
                    operator=CycleOperator.SEARCH,
                    before_state=before_operator,
                    after_state=state,
                    summary=f"queries={len(search.output.queries)} items={len(search.output.items)}",
                    transition=search.transition,
                    latency_seconds=latency_seconds,
                    evidence_bindings=tuple(
                        (
                            item.item_id,
                            evidence_record_fingerprint(
                                EvidenceRecord(
                                    item.item_id,
                                    item.content,
                                    item.source_uri,
                                    item.domain_ids,
                                )
                            ),
                        )
                        for item in search.output.items
                    ),
                    action_ids=invoked_guard_ids,
                )
            )

            before_operator = state
            absorb, latency_seconds, error, invoked_guard_ids, guard_residuals = (
                self._attempt_mechanic(
                    CycleOperator.ABSORB,
                    problem,
                    state,
                    lambda state=state, search=search: self._absorb.run(
                        problem, state, search.output
                    ),
                )
            )
            failure = self._failure_from_attempt(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=CycleOperator.ABSORB,
                error=error,
                guard_residuals=guard_residuals,
                invoked_guard_ids=invoked_guard_ids,
                latency_seconds=latency_seconds,
                iterations=iteration,
            )
            if failure is not None:
                return failure
            assert absorb is not None
            state = absorb.state
            events.append(
                self._trace_event(
                    trace_id=trace_id,
                    index=len(events),
                    operator=CycleOperator.ABSORB,
                    before_state=before_operator,
                    after_state=state,
                    summary=f"contributions={len(absorb.output)}",
                    transition=absorb.transition,
                    latency_seconds=latency_seconds,
                    action_ids=invoked_guard_ids,
                )
            )

            before_operator = state
            reconstruct, latency_seconds, error, invoked_guard_ids, guard_residuals = (
                self._attempt_mechanic(
                    CycleOperator.RECONSTRUCT,
                    problem,
                    state,
                    lambda state=state: self._reconstruct.run(problem, state),
                )
            )
            failure = self._failure_from_attempt(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=CycleOperator.RECONSTRUCT,
                error=error,
                guard_residuals=guard_residuals,
                invoked_guard_ids=invoked_guard_ids,
                latency_seconds=latency_seconds,
                iterations=iteration,
            )
            if failure is not None:
                return failure
            assert reconstruct is not None
            state = reconstruct.state
            events.append(
                self._trace_event(
                    trace_id=trace_id,
                    index=len(events),
                    operator=CycleOperator.RECONSTRUCT,
                    before_state=before_operator,
                    after_state=state,
                    summary=reconstruct.output.portrait_id,
                    transition=reconstruct.transition,
                    latency_seconds=latency_seconds,
                    action_ids=invoked_guard_ids,
                )
            )

            before_operator = state
            detect, latency_seconds, error, invoked_guard_ids, guard_residuals = (
                self._attempt_mechanic(
                    CycleOperator.DETECT,
                    problem,
                    state,
                    lambda state=state: self._detect.run(problem, state),
                )
            )
            failure = self._failure_from_attempt(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=CycleOperator.DETECT,
                error=error,
                guard_residuals=guard_residuals,
                invoked_guard_ids=invoked_guard_ids,
                latency_seconds=latency_seconds,
                iterations=iteration,
            )
            if failure is not None:
                return failure
            assert detect is not None
            state = detect.state
            events.append(
                self._trace_event(
                    trace_id=trace_id,
                    index=len(events),
                    operator=CycleOperator.DETECT,
                    before_state=before_operator,
                    after_state=state,
                    summary=f"residuals={len(detect.output)}",
                    transition=detect.transition,
                    latency_seconds=latency_seconds,
                    action_ids=invoked_guard_ids,
                )
            )

            material = tuple(
                residual for residual in detect.output if residual.material
            )
            changed_coordinates: list[str] = []
            blocked_residual_ids: list[str] = []

            for residual in material:
                before_operator = state
                (
                    diagnosis_result,
                    latency_seconds,
                    error,
                    invoked_guard_ids,
                    guard_residuals,
                ) = self._attempt_mechanic(
                    CycleOperator.DIAGNOSE,
                    problem,
                    state,
                    lambda residual=residual, state=state: self._diagnose.run(
                        residual, problem, state
                    ),
                )
                failure = self._failure_from_attempt(
                    problem=problem,
                    state=state,
                    events=events,
                    trace_id=trace_id,
                    operator=CycleOperator.DIAGNOSE,
                    error=error,
                    guard_residuals=guard_residuals,
                    invoked_guard_ids=invoked_guard_ids,
                    latency_seconds=latency_seconds,
                    iterations=iteration,
                )
                if failure is not None:
                    return failure
                assert diagnosis_result is not None
                state = diagnosis_result.state
                events.append(
                    self._trace_event(
                        trace_id=trace_id,
                        index=len(events),
                        operator=CycleOperator.DIAGNOSE,
                        before_state=before_operator,
                        after_state=state,
                        summary=diagnosis_result.output.rationale,
                        transition=diagnosis_result.transition,
                        latency_seconds=latency_seconds,
                        action_ids=invoked_guard_ids,
                    )
                )
                before_operator = state
                (
                    reframe_result,
                    latency_seconds,
                    error,
                    invoked_guard_ids,
                    guard_residuals,
                ) = self._attempt_mechanic(
                    CycleOperator.REFRAME,
                    problem,
                    state,
                    lambda residual=residual, diagnosis_result=diagnosis_result, state=state: (
                        self._reframe.run(
                            residual, diagnosis_result.output, problem, state
                        )
                    ),
                )
                if guard_residuals or isinstance(error, _MechanicGuardEvaluationError):
                    failure = self._failure_from_attempt(
                        problem=problem,
                        state=state,
                        events=events,
                        trace_id=trace_id,
                        operator=CycleOperator.REFRAME,
                        error=error,
                        guard_residuals=guard_residuals,
                        invoked_guard_ids=invoked_guard_ids,
                        latency_seconds=latency_seconds,
                        iterations=iteration,
                    )
                    assert failure is not None
                    return failure
                if isinstance(error, (ValueError, PermissionError)):
                    exc = error
                    blocked_residual_ids.append(residual.residual_id)
                    blocked_transition = Transition(
                        operator=CycleOperator.REFRAME,
                        input_epoch=state.epoch,
                        output_epoch=state.epoch,
                        residual_ids=(residual.residual_id,),
                    )
                    events.append(
                        self._trace_event(
                            trace_id=trace_id,
                            index=len(events),
                            operator=CycleOperator.REFRAME,
                            before_state=before_operator,
                            after_state=state,
                            summary=f"blocked:{type(exc).__name__}:{exc}",
                            transition=blocked_transition,
                            status=MechanicRunStatus.BLOCKED,
                            failure_signature=("unsafe_or_ambiguous_reframe",),
                            latency_seconds=latency_seconds,
                            action_ids=invoked_guard_ids,
                        )
                    )
                    continue
                if error is not None:
                    failure = self._failure_from_attempt(
                        problem=problem,
                        state=state,
                        events=events,
                        trace_id=trace_id,
                        operator=CycleOperator.REFRAME,
                        error=error,
                        guard_residuals=(),
                        invoked_guard_ids=invoked_guard_ids,
                        latency_seconds=latency_seconds,
                        iterations=iteration,
                    )
                    assert failure is not None
                    return failure
                assert reframe_result is not None
                state = reframe_result.state
                changed_coordinates.extend(
                    reframe_result.transition.changed_coordinates
                )
                events.append(
                    self._trace_event(
                        trace_id=trace_id,
                        index=len(events),
                        operator=CycleOperator.REFRAME,
                        before_state=before_operator,
                        after_state=state,
                        summary=reframe_result.output.note,
                        transition=reframe_result.transition,
                        latency_seconds=latency_seconds,
                        action_ids=invoked_guard_ids,
                    )
                )

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

            if changed_coordinates:
                before_operator = state
                reopen_state = state
                reopen_coordinates = tuple(dict.fromkeys(changed_coordinates))
                reopen_reason = f"material reframe at iteration {iteration}"
                (
                    reopen,
                    latency_seconds,
                    error,
                    invoked_guard_ids,
                    guard_residuals,
                ) = self._attempt_mechanic(
                    CycleOperator.REOPEN,
                    problem,
                    state,
                    lambda reopen_state=reopen_state, reopen_coordinates=reopen_coordinates, reopen_reason=reopen_reason: (
                        self._reopen.run(
                            reopen_state,
                            changed_coordinates=reopen_coordinates,
                            reason=reopen_reason,
                        )
                    ),
                )
                failure = self._failure_from_attempt(
                    problem=problem,
                    state=state,
                    events=events,
                    trace_id=trace_id,
                    operator=CycleOperator.REOPEN,
                    error=error,
                    guard_residuals=guard_residuals,
                    invoked_guard_ids=invoked_guard_ids,
                    latency_seconds=latency_seconds,
                    iterations=iteration,
                )
                if failure is not None:
                    return failure
                assert reopen is not None
                state = reopen.state
                events.append(
                    self._trace_event(
                        trace_id=trace_id,
                        index=len(events),
                        operator=CycleOperator.REOPEN,
                        before_state=before_operator,
                        after_state=state,
                        summary=f"staled={len(reopen.output)}",
                        transition=reopen.transition,
                        latency_seconds=latency_seconds,
                        action_ids=invoked_guard_ids,
                    )
                )

            before_iteration_record = state
            iteration_residual_ids = tuple(
                residual.residual_id for residual in material
            )
            iteration_changed_coordinates = tuple(dict.fromkeys(changed_coordinates))
            recorded_state, latency_seconds, error = self._attempt_action(
                partial(
                    self._record_iteration,
                    state,
                    iteration=iteration,
                    before_claims=before_claims,
                    before_evidence=before_evidence,
                    before_domains=before_domains,
                    residual_ids=iteration_residual_ids,
                    changed_coordinates=iteration_changed_coordinates,
                    route_kind_ids=current_route_kinds,
                )
            )
            invoked_guard_ids: tuple[str, ...] = ()
            guard_residuals: tuple[str, ...] = ()
            failure = self._failure_from_attempt(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=CycleOperator.RECURSE,
                error=error,
                guard_residuals=guard_residuals,
                invoked_guard_ids=invoked_guard_ids,
                latency_seconds=latency_seconds,
                iterations=iteration,
            )
            if failure is not None:
                return failure
            assert recorded_state is not None
            state = recorded_state
            recurse_transition = Transition(
                operator=CycleOperator.RECURSE,
                input_epoch=before_iteration_record.epoch,
                output_epoch=state.epoch,
                residual_ids=iteration_residual_ids,
            )
            events.append(
                self._trace_event(
                    trace_id=trace_id,
                    index=len(events),
                    operator=CycleOperator.RECURSE,
                    before_state=before_iteration_record,
                    after_state=state,
                    summary=f"iteration_recorded={iteration + 1}",
                    transition=recurse_transition,
                    latency_seconds=latency_seconds,
                    action_ids=invoked_guard_ids,
                )
            )

            (
                saturation,
                latency_seconds,
                error,
                invoked_guard_ids,
                guard_residuals,
            ) = self._attempt_mechanic(
                CycleOperator.SATURATE_BOUNDED,
                problem,
                state,
                lambda state=state: self._saturate.assess(state),
            )
            failure = self._failure_from_attempt(
                problem=problem,
                state=state,
                events=events,
                trace_id=trace_id,
                operator=CycleOperator.SATURATE_BOUNDED,
                error=error,
                guard_residuals=guard_residuals,
                invoked_guard_ids=invoked_guard_ids,
                latency_seconds=latency_seconds,
                iterations=iteration + 1,
            )
            if failure is not None:
                return failure
            assert saturation is not None
            last_saturation_reasons = saturation.reasons
            sat_transition = Transition(
                operator=CycleOperator.SATURATE_BOUNDED,
                input_epoch=state.epoch,
                output_epoch=state.epoch,
                residual_ids=state.knowledge.residual_ids,
            )
            events.append(
                self._trace_event(
                    trace_id=trace_id,
                    index=len(events),
                    operator=CycleOperator.SATURATE_BOUNDED,
                    before_state=state,
                    after_state=state,
                    summary="BOUNDED_SATURATED"
                    if saturation.bounded_closed
                    else "OPEN:" + ",".join(saturation.reasons),
                    transition=sat_transition,
                    status=(
                        MechanicRunStatus.SUCCEEDED
                        if saturation.bounded_closed
                        else MechanicRunStatus.PARTIAL
                    ),
                    failure_signature=(
                        ()
                        if saturation.bounded_closed
                        else ("bounded_saturation_open", *saturation.reasons)
                    ),
                    latency_seconds=latency_seconds,
                    action_ids=invoked_guard_ids,
                )
            )

            if not material and saturation.bounded_closed:
                verified_claims = tuple(
                    claim
                    for claim in state.knowledge.claims
                    if claim.authority is ClaimAuthority.VERIFIED
                )
                if self._config.require_verified_answer and not verified_claims:
                    solution = Solution(
                        problem_id=problem.problem_id,
                        status=SolutionStatus.CANNOT_CHECK,
                        answer="Bounded saturation reached but no verified evidence supports a final answer.",
                        evidence_ids=state.knowledge.evidence_ids,
                        residual_ids=state.knowledge.residual_ids,
                        iterations=iteration + 1,
                        trace_id=trace_id,
                    )
                else:
                    answer, latency_seconds, error = self._attempt_action(
                        lambda state=state: self._reasoner.compose_answer(
                            problem, state
                        )
                    )
                    invoked_guard_ids = ()
                    guard_residuals = ()
                    failure = self._failure_from_attempt(
                        problem=problem,
                        state=state,
                        events=events,
                        trace_id=trace_id,
                        operator=CycleOperator.RECURSE,
                        error=error,
                        guard_residuals=guard_residuals,
                        invoked_guard_ids=invoked_guard_ids,
                        latency_seconds=latency_seconds,
                        iterations=iteration + 1,
                    )
                    if failure is not None:
                        return failure
                    assert answer is not None
                    compose_transition = Transition(
                        operator=CycleOperator.RECURSE,
                        input_epoch=state.epoch,
                        output_epoch=state.epoch,
                    )
                    events.append(
                        self._trace_event(
                            trace_id=trace_id,
                            index=len(events),
                            operator=CycleOperator.RECURSE,
                            before_state=state,
                            after_state=state,
                            summary="answer_composed",
                            transition=compose_transition,
                            latency_seconds=latency_seconds,
                            action_ids=invoked_guard_ids,
                        )
                    )
                    solution = Solution(
                        problem_id=problem.problem_id,
                        status=SolutionStatus.SOLVED_VERIFIED
                        if verified_claims
                        else SolutionStatus.PROVISIONAL,
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

        solution = Solution(
            problem_id=problem.problem_id,
            status=SolutionStatus.CANNOT_CHECK,
            answer=(
                "Resource bound reached before bounded saturation. Open saturation coordinates: "
                + ", ".join(last_saturation_reasons)
            ),
            evidence_ids=state.knowledge.evidence_ids,
            residual_ids=state.knowledge.residual_ids,
            iterations=self._config.max_iterations,
            trace_id=trace_id,
        )
        return solution, state, SolveTrace(trace_id, tuple(events))
