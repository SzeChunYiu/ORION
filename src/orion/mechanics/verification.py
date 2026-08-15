from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import MechanicCell


class VerificationMethod(str, Enum):
    INSPECTION = "INSPECTION"
    ANALYSIS = "ANALYSIS"
    DEMONSTRATION = "DEMONSTRATION"
    TEST = "TEST"
    BENCHMARK = "BENCHMARK"
    FRESH_TRANSFER = "FRESH_TRANSFER"
    PROTECTED_REVIEW = "PROTECTED_REVIEW"


class VerificationStage(str, Enum):
    SPECIFICATION = "SPECIFICATION"
    IMPLEMENTATION = "IMPLEMENTATION"
    EMPIRICAL_PROMOTION = "EMPIRICAL_PROMOTION"


@dataclass(frozen=True)
class VerificationObligation:
    obligation_id: str
    mechanic_id: str
    requirement: str
    method: VerificationMethod
    stage: VerificationStage
    required_artifact_kind: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.obligation_id,
                self.mechanic_id,
                self.requirement,
                self.required_artifact_kind,
            )
        ):
            raise ValueError("verification obligation fields cannot be empty")


@dataclass(frozen=True)
class MechanicVerificationPlan:
    mechanic_id: str
    obligations: tuple[VerificationObligation, ...]

    def __post_init__(self) -> None:
        if not self.mechanic_id.strip() or not self.obligations:
            raise ValueError("mechanic verification plan requires identity and obligations")
        if any(item.mechanic_id != self.mechanic_id for item in self.obligations):
            raise ValueError("verification obligation mechanic mismatch")
        ids = [item.obligation_id for item in self.obligations]
        if len(set(ids)) != len(ids):
            raise ValueError("verification obligation ids must be unique")


def default_verification_plan(cell: MechanicCell) -> MechanicVerificationPlan:
    """Build the minimum V0 verification matrix for one mechanic specification.

    The plan states how claims should be checked. It is not evidence that those checks
    have run or passed.
    """

    prefix = f"verify:{cell.mechanic_id}"
    return MechanicVerificationPlan(
        mechanic_id=cell.mechanic_id,
        obligations=(
            VerificationObligation(
                f"{prefix}:spec",
                cell.mechanic_id,
                "All claimed mechanic dimensions are explicit or carry a justified waiver for the declared scope.",
                VerificationMethod.ANALYSIS,
                VerificationStage.SPECIFICATION,
                "MechanicAuditReport",
            ),
            VerificationObligation(
                f"{prefix}:failure-path",
                cell.mechanic_id,
                "Registered failure/block/cannot-check semantics are exercised by a known-answer or hostile case before implementation conformance is claimed.",
                VerificationMethod.TEST,
                VerificationStage.IMPLEMENTATION,
                "TestReceipt",
            ),
            VerificationObligation(
                f"{prefix}:interface",
                cell.mechanic_id,
                "Declared input/output/handoff requirements are checked at the actual interface or a fidelity-declared substitute.",
                VerificationMethod.TEST,
                VerificationStage.IMPLEMENTATION,
                "InterfaceVerificationReceipt",
            ),
            VerificationObligation(
                f"{prefix}:fresh",
                cell.mechanic_id,
                "Any claim of real-task improvement or transfer is tested on fresh tasks not used to construct the mechanic.",
                VerificationMethod.FRESH_TRANSFER,
                VerificationStage.EMPIRICAL_PROMOTION,
                "FreshTransferReceipt",
            ),
        ),
    )


def apply_default_verification_plan(cell: MechanicCell) -> MechanicCell:
    plan = default_verification_plan(cell)
    return replace(cell, verification_contracts=tuple(item.obligation_id for item in plan.obligations))


def apply_default_verification_plans(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_default_verification_plan(cell) for cell in cells)
