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
    provisional_dimensions: tuple[str, ...]


@dataclass(frozen=True)
class RecursiveMechanicAudit:
    root_mechanic_id: str
    reports: tuple[MechanicAuditReport, ...]
    unknown_child_ids: tuple[str, ...] = ()
    cycle_paths: tuple[str, ...] = ()
    unknown_dependency_ids: tuple[str, ...] = ()
    dependency_cycle_paths: tuple[str, ...] = ()
    mixed_cycle_paths: tuple[str, ...] = ()

    @property
    def bounded_ready(self) -> bool:
        return (
            not self.unknown_child_ids
            and not self.cycle_paths
            and not self.unknown_dependency_ids
            and not self.dependency_cycle_paths
            and not self.mixed_cycle_paths
            and all(
                item.verdict is MechanicAuditVerdict.READY_FOR_BENCHMARK
                for item in self.reports
            )
        )


def audit_mechanic(cell: MechanicCell) -> MechanicAuditReport:
    questions = generate_mechanic_questions(cell)
    return MechanicAuditReport(
        mechanic_id=cell.mechanic_id,
        verdict=MechanicAuditVerdict.READY_FOR_BENCHMARK
        if not questions
        else MechanicAuditVerdict.OPEN,
        open_questions=questions,
        waived_dimensions=tuple(sorted(item.dimension.value for item in cell.waivers)),
        provisional_dimensions=tuple(
            sorted(item.value for item in cell.provisional_dimensions)
        ),
    )


def audit_recursive(
    cells: Mapping[str, MechanicCell], root_mechanic_id: str
) -> RecursiveMechanicAudit:
    """Audit the full child-and-dependency closure from one root mechanic."""

    if root_mechanic_id not in cells:
        return RecursiveMechanicAudit(root_mechanic_id, (), (root_mechanic_id,), ())

    reports: list[MechanicAuditReport] = []
    unknown_children: set[str] = set()
    unknown_dependencies: set[str] = set()
    discovered: set[str] = set()

    def discover(mechanic_id: str) -> None:
        if mechanic_id in discovered:
            return
        cell = cells.get(mechanic_id)
        if cell is None:
            return
        discovered.add(mechanic_id)
        reports.append(audit_mechanic(cell))
        for child_id in cell.child_mechanic_ids:
            if child_id not in cells:
                unknown_children.add(child_id)
            else:
                discover(child_id)
        for dependency_id in cell.dependency_ids:
            if dependency_id not in cells:
                unknown_dependencies.add(dependency_id)
            else:
                discover(dependency_id)

    discover(root_mechanic_id)

    def cycle_paths(edge_name: str) -> set[str]:
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
            active.append(mechanic_id)
            for target_id in getattr(cells[mechanic_id], edge_name):
                if target_id in discovered:
                    visit(target_id)
            active.pop()
            visited.add(mechanic_id)

        for mechanic_id in sorted(discovered):
            visit(mechanic_id)
        return cycles

    containment_cycles = cycle_paths("child_mechanic_ids")
    dependency_cycles = cycle_paths("dependency_ids")

    mixed_cycles: set[str] = set()
    mixed_visited: set[str] = set()
    mixed_active_nodes: list[str] = []
    mixed_active_edges: list[str] = []

    def visit_mixed(mechanic_id: str) -> None:
        mixed_active_nodes.append(mechanic_id)
        edges = (
            *(("containment", item) for item in cells[mechanic_id].child_mechanic_ids),
            *(("dependency", item) for item in cells[mechanic_id].dependency_ids),
        )
        for edge_kind, target_id in edges:
            if target_id not in discovered:
                continue
            if target_id in mixed_active_nodes:
                start = mixed_active_nodes.index(target_id)
                cycle_edge_kinds = (*mixed_active_edges[start:], edge_kind)
                if set(cycle_edge_kinds) == {"containment", "dependency"}:
                    cycle_nodes = mixed_active_nodes[start:]
                    first_node = (
                        root_mechanic_id
                        if root_mechanic_id in cycle_nodes
                        else min(cycle_nodes)
                    )
                    first_index = cycle_nodes.index(first_node)
                    canonical_nodes = (
                        cycle_nodes[first_index:] + cycle_nodes[:first_index]
                    )
                    mixed_cycles.add(
                        " -> ".join(canonical_nodes + [canonical_nodes[0]])
                    )
                continue
            if target_id in mixed_visited:
                continue
            mixed_active_edges.append(edge_kind)
            visit_mixed(target_id)
            mixed_active_edges.pop()
        mixed_active_nodes.pop()
        mixed_visited.add(mechanic_id)

    for mechanic_id in sorted(discovered):
        if mechanic_id not in mixed_visited:
            visit_mixed(mechanic_id)
    return RecursiveMechanicAudit(
        root_mechanic_id=root_mechanic_id,
        reports=tuple(reports),
        unknown_child_ids=tuple(sorted(unknown_children)),
        cycle_paths=tuple(sorted(containment_cycles)),
        unknown_dependency_ids=tuple(sorted(unknown_dependencies)),
        dependency_cycle_paths=tuple(sorted(dependency_cycles)),
        mixed_cycle_paths=tuple(sorted(mixed_cycles)),
    )
