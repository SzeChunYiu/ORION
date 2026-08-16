from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.residuals import Responsibility
from orion.engine.cycle import CycleOperator, Transition, local_reframe_allowed, revision_allowed
from orion.mechanics.program import MechanicsProgramMetrics, observe_current_mechanics_program
from orion.mechanics.workflow import ORION_WORKFLOW_CELLS, ORION_WORKFLOW_ROOT_ID
from orion.registry import CORE_OPERATOR_IDS


class FormalEngineStatus(str, Enum):
    STRUCTURAL_DEFECT = "STRUCTURAL_DEFECT"
    INDEPENDENT_VERIFICATION_OPEN = "INDEPENDENT_VERIFICATION_OPEN"
    FORMALLY_CLOSED_REGISTERED_SURFACE = "FORMALLY_CLOSED_REGISTERED_SURFACE"


@dataclass(frozen=True)
class FormalProofCheck:
    obligation_id: str
    passed: bool
    note: str


@dataclass(frozen=True)
class FormalEngineReadiness:
    status: FormalEngineStatus
    metrics: MechanicsProgramMetrics
    operator_contract_count: int
    proof_checks: tuple[FormalProofCheck, ...]
    blockers: tuple[str, ...]

    @property
    def structurally_sound(self) -> bool:
        return self.status is not FormalEngineStatus.STRUCTURAL_DEFECT

    @property
    def formally_closed(self) -> bool:
        return self.status is FormalEngineStatus.FORMALLY_CLOSED_REGISTERED_SURFACE


def _non_authority_guard_works() -> bool:
    try:
        Transition(
            operator=CycleOperator.SEARCH,
            input_epoch=0,
            output_epoch=0,
            authority_increase=True,
            scientific_authority_certificate_ids=("certificate:fake",),
        ).validate()
    except ValueError:
        return True
    return False


def _operator_contracts_present() -> tuple[bool, int, tuple[str, ...]]:
    by_id = {cell.mechanic_id: cell for cell in ORION_WORKFLOW_CELLS}
    missing: list[str] = []
    for operator_id in CORE_OPERATOR_IDS:
        cell = by_id.get(operator_id)
        if cell is None:
            missing.append(f"{operator_id}: missing workflow cell")
            continue
        required = {
            "inputs": bool(cell.input_ids),
            "outputs": bool(cell.output_ids),
            "authority": bool(cell.authority_boundaries),
            "reopen": bool(cell.reopen_triggers),
            "empirical_open": bool(cell.empirical_open_coordinates),
        }
        for coordinate, present in required.items():
            if not present:
                missing.append(f"{operator_id}: missing {coordinate}")
    root = by_id.get(ORION_WORKFLOW_ROOT_ID)
    if root is None:
        missing.append("root workflow cell missing")
    elif tuple(root.child_mechanic_ids) != tuple(CORE_OPERATOR_IDS):
        missing.append("root child operator order does not match canonical registry")
    return not missing, len(CORE_OPERATOR_IDS), tuple(missing)


def assess_formal_engine_readiness() -> FormalEngineReadiness:
    """Separate structural/formal contract presence from independent closure.

    A fully specified-looking cell is not formally closed while the recursive
    mechanic audit still has open questions that lack independent verified
    answers. This gate exists so issue/Paper status follows the machine state
    rather than documentation optimism.
    """

    metrics = observe_current_mechanics_program()
    contracts_ok, contract_count, contract_blockers = _operator_contracts_present()
    proof_checks = (
        FormalProofCheck(
            "PO-SEARCH-NONAUTHORITY",
            _non_authority_guard_works(),
            "SEARCH cannot mint scientific authority even when given a certificate id.",
        ),
        FormalProofCheck(
            "PO-AMBIGUOUS-RESPONSIBILITY-BLOCKS-REVISION",
            not revision_allowed((Responsibility.SEARCH, Responsibility.EVIDENCE)),
            "Multiple responsibility hypotheses cannot authorize high-impact revision.",
        ),
        FormalProofCheck(
            "PO-EVIDENCE-IS-NOT-REFRAME",
            not local_reframe_allowed(Responsibility.EVIDENCE),
            "A diagnosed evidence deficit requires acquisition rather than formulation rewrite.",
        ),
        FormalProofCheck(
            "PO-EXECUTION-IS-NOT-REFRAME",
            not local_reframe_allowed(Responsibility.EXECUTION),
            "An execution defect requires execution repair rather than formulation rewrite.",
        ),
        FormalProofCheck(
            "PO-METHOD-CHANGE-IS-PROTECTED",
            not local_reframe_allowed(Responsibility.METHOD),
            "Method change is outside local REFRAME and requires the protected Self-ORION path.",
        ),
        FormalProofCheck(
            "PO-REGISTERED-GRAPH-INTEGRITY",
            metrics.unknown_child_count == 0
            and metrics.cycle_count == 0
            and metrics.unknown_dependency_count == 0
            and metrics.dependency_cycle_count == 0
            and metrics.mixed_cycle_count == 0,
            "The registered recursive mechanic graph must have no unknown/cyclic structural references.",
        ),
    )
    proof_ok = all(item.passed for item in proof_checks)

    structural_blockers = list(contract_blockers)
    structural_blockers.extend(
        item.note for item in proof_checks if not item.passed
    )
    if not contracts_ok or not proof_ok:
        return FormalEngineReadiness(
            status=FormalEngineStatus.STRUCTURAL_DEFECT,
            metrics=metrics,
            operator_contract_count=contract_count,
            proof_checks=proof_checks,
            blockers=tuple(structural_blockers),
        )

    if metrics.open_question_count > 0 or metrics.ready_mechanic_count < metrics.mechanic_count:
        blockers = (
            f"{metrics.open_question_count} independently unclosed mechanic questions remain",
            f"{metrics.open_mechanic_count} of {metrics.mechanic_count} reachable mechanics are not READY_FOR_BENCHMARK",
            "formal closure of the registered surface requires independently verified answers/checks; generic envelopes or self-authored answers do not count",
        )
        return FormalEngineReadiness(
            status=FormalEngineStatus.INDEPENDENT_VERIFICATION_OPEN,
            metrics=metrics,
            operator_contract_count=contract_count,
            proof_checks=proof_checks,
            blockers=blockers,
        )

    return FormalEngineReadiness(
        status=FormalEngineStatus.FORMALLY_CLOSED_REGISTERED_SURFACE,
        metrics=metrics,
        operator_contract_count=contract_count,
        proof_checks=proof_checks,
        blockers=(),
    )


__all__ = [
    "FormalEngineReadiness",
    "FormalEngineStatus",
    "FormalProofCheck",
    "assess_formal_engine_readiness",
]
