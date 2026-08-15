from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from .model import MechanicCell
from .questioning import MechanicQuestion, generate_mechanic_questions


class MechanicAuditVerdict(str, Enum):
    READY_FOR_BENCHMARK = "READY_FOR_BENCHMARK"
    OPEN = "OPEN"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class MechanicAuditReport:
    mechanic_id: str
    verdict: MechanicAuditVerdict
    open_questions: tuple[MechanicQuestion, ...]
    waived_dimensions: tuple[str, ...]


@dataclass(frozen=True)
class RecursiveMechanicAudit:
    root_mechanic_id: str
    reports: tuple[MechanicAuditReport, ...]
    unknown_child_ids: tuple[str, ...] = ()
    cycle_paths: tuple[str, ...] = ()

    @property
    def bounded_ready(self) -> bool:
        return not self.unknown_child_ids and not self.cycle_paths and all(
            item.verdict is MechanicAuditVerdict.READY_FOR_BENCHMARK for item in self.reports
        )


def audit_mechanic(cell: MechanicCell) -> MechanicAuditReport:
    questions = generate_mechanic_questions(cell)
    return MechanicAuditReport(
        mechanic_id=cell.mechanic_id,
        verdict=MechanicAuditVerdict.READY_FOR_BENCHMARK if not questions else MechanicAuditVerdict.OPEN,
        open_questions=questions,
        waived_dimensions=tuple(sorted(item.dimension.value for item in cell.waivers)),
    )


def audit_recursive(cells: Mapping[str, MechanicCell], root_mechanic_id: str) -> RecursiveMechanicAudit:
    """Run the same mechanic audit recursively over declared child mechanics."""

    if root_mechanic_id not in cells:
        return RecursiveMechanicAudit(root_mechanic_id, (), (root_mechanic_id,), ())

    reports: list[MechanicAuditReport] = []
    unknown: set[str] = set()
    cycles: set[str] = set()
    visited: set[str] = set()
    active: list[str] = []

    def visit(mechanic_id: str) -> None:
        if mechanic_id in active:
            start = active.index(mechanic_id)
            cycles.add(" -> ".join(active[start:] + [mechanic_id]))
            return
        if mechanic_id in visited:
            return
        cell = cells.get(mechanic_id)
        if cell is None:
            unknown.add(mechanic_id)
            return
        active.append(mechanic_id)
        reports.append(audit_mechanic(cell))
        for child_id in cell.child_mechanic_ids:
            visit(child_id)
        active.pop()
        visited.add(mechanic_id)

    visit(root_mechanic_id)
    return RecursiveMechanicAudit(
        root_mechanic_id=root_mechanic_id,
        reports=tuple(reports),
        unknown_child_ids=tuple(sorted(unknown)),
        cycle_paths=tuple(sorted(cycles)),
    )
