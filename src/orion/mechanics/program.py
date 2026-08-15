from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .audit import MechanicAuditVerdict, audit_recursive
from .model import MechanicCell
from .questioning import MechanicQuestion
from .research import MechanicResearchTask, research_task_for_question
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


def observe_mechanics_program(
    cells: tuple[MechanicCell, ...],
    *,
    root_mechanic_id: str = ORION_WORKFLOW_ROOT_ID,
) -> MechanicsProgramMetrics:
    """Expose machine-readable development observables for the recursive mechanic graph."""

    by_id = {cell.mechanic_id: cell for cell in cells}
    report = audit_recursive(by_id, root_mechanic_id)
    counts: dict[str, int] = {}
    for item in report.reports:
        for question in item.open_questions:
            counts[question.dimension.value] = counts.get(question.dimension.value, 0) + 1
    return MechanicsProgramMetrics(
        root_mechanic_id=root_mechanic_id,
        mechanic_count=len(report.reports),
        ready_mechanic_count=sum(
            item.verdict is MechanicAuditVerdict.READY_FOR_BENCHMARK for item in report.reports
        ),
        open_question_count=sum(len(item.open_questions) for item in report.reports),
        open_by_dimension=tuple(sorted(counts.items())),
        unknown_child_count=len(report.unknown_child_ids),
        cycle_count=len(report.cycle_paths),
    )


def plan_program_questions(
    cells: tuple[MechanicCell, ...],
    *,
    limit: int = 64,
    root_mechanic_id: str = ORION_WORKFLOW_ROOT_ID,
) -> tuple[MechanicQuestion, ...]:
    """V0 breadth-first/gate-first global scheduler over open mechanic questions.

    Each cell's local question order already encodes the fixed gate priority. This
    scheduler takes rank 0 across cells before rank 1, preventing one coarse mechanic
    from consuming the entire research budget before peer mechanics are inspected.
    """

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
