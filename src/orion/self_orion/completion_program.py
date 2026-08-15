from __future__ import annotations

from dataclasses import dataclass

from orion.mechanics.actions import apply_candidate_action_plans
from orion.mechanics.diagnosis import apply_default_diagnosis_plans
from orion.mechanics.engineering import apply_default_engineering_contracts
from orion.mechanics.objectives import apply_candidate_objectives
from orion.mechanics.optimization import apply_default_optimization_policies
from orion.mechanics.program import (
    MechanicsProgramMetrics,
    current_program_cells as saturated_base_cells,
    observe_mechanics_program,
    plan_program_questions,
    plan_program_research,
)
from orion.mechanics.provenance import apply_default_provenance_contracts
from orion.mechanics.resources import apply_default_resource_plans
from orion.mechanics.storage import apply_default_storage_contracts


@dataclass(frozen=True)
class ShadowCompletionState:
    metrics: MechanicsProgramMetrics
    benchmarkable: bool
    boundary: str


def completion_program_cells():
    """Compose the full V0 specification surface without mutating the bootstrap controller.

    The base controller owns epistemic/search/saturation mechanics. This continuation
    adds execution/control/persistence/engineering specification layers. It does not
    add empirical PASS evidence.
    """

    cells = saturated_base_cells()
    for apply in (
        apply_candidate_action_plans,
        apply_candidate_objectives,
        apply_default_optimization_policies,
        apply_default_resource_plans,
        apply_default_diagnosis_plans,
        apply_default_storage_contracts,
        apply_default_provenance_contracts,
        apply_default_engineering_contracts,
    ):
        cells = apply(cells)
    return cells


def observe_completion_program() -> ShadowCompletionState:
    metrics = observe_mechanics_program(completion_program_cells())
    benchmarkable = metrics.open_question_count == 0 and metrics.ready_mechanic_count == metrics.mechanic_count
    return ShadowCompletionState(
        metrics=metrics,
        benchmarkable=benchmarkable,
        boundary=(
            "READY_FOR_BENCHMARK means every registered mechanic dimension has a declared specification or justified waiver. "
            "It does not establish step-specific empirical validity, live search saturation, fresh transfer, or Self-ORION promotion authority."
        ),
    )


def next_completion_questions(*, limit: int = 64):
    return plan_program_questions(completion_program_cells(), limit=limit)


def next_completion_research(*, limit: int = 64):
    return plan_program_research(completion_program_cells(), limit=limit)
