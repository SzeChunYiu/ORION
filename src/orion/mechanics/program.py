from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .audit import MechanicAuditVerdict, audit_recursive
from .decomposition import expanded_workflow_cells
from .failure import apply_default_failure_plans
from .handoff import apply_default_handoff_plans
from .model import MechanicCell
from .observability import apply_default_observation_plans
from .questioning import MechanicQuestion
from .research import MechanicResearchTask, research_task_for_question
from .verification import apply_default_verification_plans
from .workflow import ORION_WORKFLOW_ROOT_ID


@dataclass(frozen=True)
class MechanicsProgramMetrics:
    root_mechanic_id: str
    mechanic_count: int
    ready_mechanic_count: int
    open_question_count: int
    open_by_dimension: tuple[tuple[str, int], ...]
    unknown_child_count: int
    cycle_count: int

    @property
    def open_mechanic_count(self) -> int:
        return self.mechanic_count - self.ready_mechanic_count


def current_program_cells() -> tuple[MechanicCell, ...]:
    cells = expanded_workflow_cells()
    cells = apply_default_verification_plans(cells)
    cells = apply_default_failure_plans(cells)
    cells = apply_default_observation_plans(cells)
    cells = apply_default_handoff_plans(cells)
    return cells


def observe_mechanics_program(
    cells: tuple[MechanicCell, ...],
    *,
    root_mechanic_id: str = ORION_WORKFLOW_ROOT_ID,
) -> MechanicsProgramMetrics:
    by_id = {cell.mechanic_id: cell for cell in cells}
    report = audit_recursive(by_id, root_mechanic_id)
    counts: dict[str, int] = {}
    for item in report.reports:
        for question in item.open_questions:
            counts[question.dimension.value] = counts.get(question.dimension.value, 0) + 1
    return MechanicsProgramMetrics(
        root_mechanic_id=root_mechanic_id,
        mechanic_count=len(report.reports),
        ready_mechanic_count=sum(item.verdict is MechanicAuditVerdict.READY_FOR_BENCHMARK for item in report.reports),
        open_question_count=sum(len(item.open_questions) for item in report.reports),
        open_by_dimension=tuple(sorted(counts.items())),
        unknown_child_count=len(report.unknown_child_ids),
        cycle_count=len(report.cycle_paths),
    )


def observe_current_mechanics_program() -> MechanicsProgramMetrics:
    return observe_mechanics_program(current_program_cells())


def plan_program_questions(
    cells: tuple[MechanicCell, ...],
    *,
    limit: int = 64,
    root_mechanic_id: str = ORION_WORKFLOW_ROOT_ID,
) -> tuple[MechanicQuestion, ...]:
    if limit < 1:
        raise ValueError("program question limit must be positive")
    by_id = {cell.mechanic_id: cell for cell in cells}
    report = audit_recursive(by_id, root_mechanic_id)
    rows = tuple(item.open_questions for item in report.reports)
    max_depth = max((len(row) for row in rows), default=0)
    selected: list[MechanicQuestion] = []
    for rank in range(max_depth):
        for row in rows:
            if rank < len(row):
                selected.append(row[rank])
                if len(selected) >= limit:
                    return tuple(selected)
    return tuple(selected)


def plan_program_research(
    cells: tuple[MechanicCell, ...],
    *,
    limit: int = 64,
    root_mechanic_id: str = ORION_WORKFLOW_ROOT_ID,
) -> tuple[MechanicResearchTask, ...]:
    by_id: Mapping[str, MechanicCell] = {cell.mechanic_id: cell for cell in cells}
    questions = plan_program_questions(cells, limit=limit, root_mechanic_id=root_mechanic_id)
    return tuple(research_task_for_question(by_id[question.mechanic_id], question) for question in questions)


def plan_current_program_questions(*, limit: int = 64) -> tuple[MechanicQuestion, ...]:
    return plan_program_questions(current_program_cells(), limit=limit)


def plan_current_program_research(*, limit: int = 64) -> tuple[MechanicResearchTask, ...]:
    return plan_program_research(current_program_cells(), limit=limit)
