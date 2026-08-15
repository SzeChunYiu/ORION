from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.mechanics.model import MechanicCell
from orion.mechanics.program import MechanicsProgramMetrics, observe_mechanics_program
from orion.self_orion.completion_program import completion_program_cells
from orion.self_orion.rakl_transfer import (
    RaklTransferReceipt,
    apply_rakl_transfer_profiles,
    rakl_transfer_receipts,
    transfer_coverage,
)


class DevelopmentKnowledgeClass(str, Enum):
    LOCAL_ORION = "LOCAL_ORION"
    RAKL_TRANSFER = "RAKL_TRANSFER"
    EXTERNAL_RESEARCH = "EXTERNAL_RESEARCH"
    LIVE_EVIDENCE = "LIVE_EVIDENCE"
    PROTECTED_ASSURANCE = "PROTECTED_ASSURANCE"


class SelfDrivingStage(str, Enum):
    STRUCTURAL_OPEN = "STRUCTURAL_OPEN"
    STRUCTURAL_DRIVER_READY = "STRUCTURAL_DRIVER_READY"
    LIVE_EVIDENCE_REQUIRED = "LIVE_EVIDENCE_REQUIRED"
    GOVERNED_SELF_ORION_READY = "GOVERNED_SELF_ORION_READY"


@dataclass(frozen=True)
class EmpiricalWorkItem:
    work_id: str
    mechanic_id: str
    coordinate: str
    knowledge_class: DevelopmentKnowledgeClass
    priority: int
    reason: str


@dataclass(frozen=True)
class DevelopmentDriveReport:
    before: MechanicsProgramMetrics
    after: MechanicsProgramMetrics
    transfer_receipts: tuple[RaklTransferReceipt, ...]
    transferred_mechanics: int
    direct_rakl_mechanics: int
    composed_orion_mechanics: int
    structurally_closed_questions: int
    empirical_work_items: tuple[EmpiricalWorkItem, ...]
    stage: SelfDrivingStage
    can_drive_next_work_mechanically: bool
    can_self_promote: bool
    boundary: str


def _knowledge_class(coordinate: str) -> DevelopmentKnowledgeClass:
    text = coordinate.lower()
    if any(token in text for token in ("fresh", "real-task", "prospective", "live", "production", "ablation", "benchmark")):
        return DevelopmentKnowledgeClass.LIVE_EVIDENCE
    if any(token in text for token in ("authority", "promotion", "assurance", "evaluator", "independence")):
        return DevelopmentKnowledgeClass.PROTECTED_ASSURANCE
    if any(token in text for token in ("parent-domain", "retrieval", "search", "nlp", "measurement", "metrology", "external")):
        return DevelopmentKnowledgeClass.EXTERNAL_RESEARCH
    return DevelopmentKnowledgeClass.LOCAL_ORION


def _priority(coordinate: str, knowledge_class: DevelopmentKnowledgeClass) -> int:
    text = coordinate.lower()
    if knowledge_class is DevelopmentKnowledgeClass.PROTECTED_ASSURANCE:
        return 10
    if any(token in text for token in ("validity", "failure", "verification", "false", "authority", "safety")):
        return 9
    if knowledge_class is DevelopmentKnowledgeClass.LIVE_EVIDENCE:
        return 8
    if knowledge_class is DevelopmentKnowledgeClass.EXTERNAL_RESEARCH:
        return 7
    return 5


def empirical_frontier(cells: tuple[MechanicCell, ...]) -> tuple[EmpiricalWorkItem, ...]:
    rows: list[EmpiricalWorkItem] = []
    for cell in cells:
        for index, coordinate in enumerate(cell.empirical_open_coordinates):
            knowledge_class = _knowledge_class(coordinate)
            rows.append(
                EmpiricalWorkItem(
                    work_id=f"empirical:{cell.mechanic_id}:{index}",
                    mechanic_id=cell.mechanic_id,
                    coordinate=coordinate,
                    knowledge_class=knowledge_class,
                    priority=_priority(coordinate, knowledge_class),
                    reason=(
                        "Structural specification is available, but this coordinate requires evidence/research rather than declaration."
                    ),
                )
            )
    rows.sort(key=lambda item: (-item.priority, item.knowledge_class.value, item.mechanic_id, item.work_id))
    return tuple(rows)


class SelfOrionDevelopmentDriver:
    """Mechanical controller for the LLM-led -> Shadow Self-ORION transition.

    V1 automatically consumes the trusted local/RAKL transfer basis. It does not
    execute arbitrary external research, edit source code, or self-promote. Those
    actions remain provider/host governed and are represented as explicit frontier
    items after the local transfer pass.
    """

    def local_transfer_cells(self) -> tuple[MechanicCell, ...]:
        return apply_rakl_transfer_profiles(completion_program_cells())

    def drive_local_transfer(self) -> DevelopmentDriveReport:
        before_cells = completion_program_cells()
        before = observe_mechanics_program(before_cells)
        after_cells = apply_rakl_transfer_profiles(before_cells)
        after = observe_mechanics_program(after_cells)
        receipts = rakl_transfer_receipts(before_cells)
        transferred, direct, composed = transfer_coverage(before_cells)
        empirical = empirical_frontier(after_cells)
        structural_ready = (
            after.open_question_count == 0
            and after.unknown_child_count == 0
            and after.cycle_count == 0
            and after.unknown_dependency_count == 0
            and after.dependency_cycle_count == 0
        )
        stage = (
            SelfDrivingStage.LIVE_EVIDENCE_REQUIRED
            if structural_ready and empirical
            else SelfDrivingStage.STRUCTURAL_DRIVER_READY
            if structural_ready
            else SelfDrivingStage.STRUCTURAL_OPEN
        )
        return DevelopmentDriveReport(
            before=before,
            after=after,
            transfer_receipts=receipts,
            transferred_mechanics=transferred,
            direct_rakl_mechanics=direct,
            composed_orion_mechanics=composed,
            structurally_closed_questions=max(0, before.open_question_count - after.open_question_count),
            empirical_work_items=empirical,
            stage=stage,
            can_drive_next_work_mechanically=structural_ready,
            can_self_promote=False,
            boundary=(
                "Local/RAKL transfer may close specification questions and schedule the empirical frontier. "
                "It cannot create scientific authority, validate real-task performance, or satisfy Governed Self-ORION readiness."
            ),
        )

    def plan_empirical_work(self, *, limit: int = 64) -> tuple[EmpiricalWorkItem, ...]:
        if limit < 1:
            raise ValueError("empirical work limit must be positive")
        return self.drive_local_transfer().empirical_work_items[:limit]


__all__ = [
    "DevelopmentDriveReport",
    "DevelopmentKnowledgeClass",
    "EmpiricalWorkItem",
    "SelfDrivingStage",
    "SelfOrionDevelopmentDriver",
    "empirical_frontier",
]
