from __future__ import annotations

from dataclasses import dataclass

from orion.benchmarks.result import BenchmarkReport, BenchmarkStatus, report_from_checks
from orion.core.closure import ClosureCertificate
from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.engine.operators.reframe import ReframeOperator
from orion.engine.operators.reopen import ReopenOperator
from orion.providers.reasoner.base import Diagnosis, ReframeProposal


@dataclass(frozen=True)
class HiddenShiftCase:
    case_id: str
    residual_kind: ResidualKind
    responsibility: Responsibility
    add_domain_ids: tuple[str, ...] = ()
    add_representation_ids: tuple[str, ...] = ()
    closure_dependencies: tuple[str, ...] = ()
    expect_local_reframe: bool = True


class _CaseReasoner:
    def __init__(self, proposal: ReframeProposal) -> None:
        self._proposal = proposal

    def propose_reframe(self, *args, **kwargs) -> ReframeProposal:  # noqa: ANN002, ANN003
        del args, kwargs
        return self._proposal


def _state(case: HiddenShiftCase) -> OrionState:
    certificates = ()
    if case.closure_dependencies:
        certificates = (
            ClosureCertificate(
                certificate_id=f"certificate:{case.case_id}",
                scope=case.case_id,
                dependency_coordinates=case.closure_dependencies,
            ),
        )
    return OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(active_domain_ids=("seed-domain",)),
        method=MethodState(method_version="benchmark-incumbent"),
        closure_certificates=certificates,
    )


def run_hidden_shift_case(case: HiddenShiftCase) -> BenchmarkReport:
    """Exercise the real REFRAME/REOPEN boundary on one exact known world."""

    state = _state(case)
    problem = Problem(
        problem_id=f"problem:{case.case_id}",
        question="Which research state coordinate is wrong?",
        initial_domain_ids=("seed-domain",),
    )
    residual = Residual(
        residual_id=f"residual:{case.case_id}",
        kind=case.residual_kind,
        description="Frozen hidden-shift benchmark residual.",
        candidate_responsibilities=(case.responsibility,),
    )
    diagnosis = Diagnosis(
        responsibilities=(case.responsibility,),
        rationale="Frozen benchmark responsibility.",
    )
    proposal = ReframeProposal(
        add_domain_ids=case.add_domain_ids,
        add_representation_ids=case.add_representation_ids,
        note="benchmark repair",
    )
    operator = ReframeOperator(_CaseReasoner(proposal))

    if not case.expect_local_reframe:
        try:
            operator.run(residual, diagnosis, problem, state)
        except (ValueError, PermissionError) as exc:
            return BenchmarkReport(
                paper_id="P1",
                case_id=case.case_id,
                status=BenchmarkStatus.PASS,
                metrics=(("unnecessary_reframe", 0.0),),
                observations=(str(exc),),
            )
        return BenchmarkReport(
            paper_id="P1",
            case_id=case.case_id,
            status=BenchmarkStatus.FAIL,
            metrics=(("unnecessary_reframe", 1.0),),
            blockers=("non-formulation responsibility entered REFRAME",),
        )

    reframed = operator.run(residual, diagnosis, problem, state)
    reopened = ReopenOperator().run(
        reframed.state,
        changed_coordinates=reframed.transition.changed_coordinates,
        reason=f"benchmark:{case.case_id}",
    )
    expected_changed = set()
    if case.add_domain_ids:
        expected_changed.add("W.ACTIVE_DOMAINS")
    if case.add_representation_ids:
        expected_changed.add("W.REPRESENTATIONS")
    expected_stale = bool(expected_changed.intersection(case.closure_dependencies))

    checks = (
        (
            "domain transport",
            set(case.add_domain_ids).issubset(reframed.state.search_universe.active_domain_ids),
        ),
        (
            "representation transport",
            set(case.add_representation_ids).issubset(
                reframed.state.search_universe.representation_ids
            ),
        ),
        (
            "typed changed coordinates",
            set(reframed.transition.changed_coordinates) == expected_changed,
        ),
        (
            "negative history retained",
            len(reframed.state.knowledge.negative_history)
            == len(state.knowledge.negative_history) + 1,
        ),
        (
            "dependent closure staled precisely",
            bool(reopened.output) is expected_stale,
        ),
        (
            "unrelated closure preserved",
            all(
                cert.stale is expected_stale
                for cert in reopened.state.closure_certificates
            ),
        ),
        ("no authority minted", not reframed.transition.authority_increase),
    )
    return report_from_checks(
        paper_id="P1",
        case_id=case.case_id,
        checks=checks,
        metrics=(
            ("correct_responsibility", 1.0),
            ("unnecessary_reframe", 0.0),
            ("closure_staled", float(expected_stale)),
        ),
    )


def frozen_reconstruction_suite() -> tuple[HiddenShiftCase, ...]:
    return (
        HiddenShiftCase(
            case_id="hidden-parent-domain",
            residual_kind=ResidualKind.SEARCH_COVERAGE_FAILURE,
            responsibility=Responsibility.SEARCH,
            add_domain_ids=("previously-hidden-parent-domain",),
            closure_dependencies=("W.ACTIVE_DOMAINS",),
        ),
        HiddenShiftCase(
            case_id="hidden-representation",
            residual_kind=ResidualKind.REPRESENTATION_FAILURE,
            responsibility=Responsibility.REPRESENTATION,
            add_representation_ids=("representation:new-coordinate-system",),
            closure_dependencies=("W.REPRESENTATIONS",),
        ),
        HiddenShiftCase(
            case_id="missing-evidence-only",
            residual_kind=ResidualKind.MISSING_EVIDENCE,
            responsibility=Responsibility.EVIDENCE,
            add_domain_ids=("should-not-be-activated",),
            expect_local_reframe=False,
        ),
        HiddenShiftCase(
            case_id="execution-bug-only",
            residual_kind=ResidualKind.UNCLASSIFIED,
            responsibility=Responsibility.EXECUTION,
            add_representation_ids=("should-not-be-added",),
            expect_local_reframe=False,
        ),
    )


__all__ = ["HiddenShiftCase", "frozen_reconstruction_suite", "run_hidden_shift_case"]
