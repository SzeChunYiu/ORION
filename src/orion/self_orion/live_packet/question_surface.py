"""Section 4b -- the mechanical question surface over the fixed cells.

Emission is deliberately not routed through the default selector: the surface
must report what the fixed grammar asks, not what a starving selector survives.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.questioning import MechanicQuestion, generate_mechanic_questions

from .mechanic_cells import ISSUE_8_DIMENSIONS, live_trial_mechanic_cells


def emit_open_questions(
    cells: Sequence[MechanicCell] | None = None,
    *,
    dimensions: Sequence[MechanicDimension] = ISSUE_8_DIMENSIONS,
) -> tuple[MechanicQuestion, ...]:
    """Emit the open questions for the named dimensions. No provider involved.

    Deliberately calls `generate_mechanic_questions` per cell and filters, rather
    than routing through `plan_next_questions`: that selector's default window is
    eight slots taken in `_PRIORITY` order, which cuts PARENT_DISCIPLINE,
    SATURATION and STORAGE -- three of the eight this issue requires -- before
    they are ever asked. A selection window that never asks is the starvation
    failure the kernel already names; it must not be reintroduced here.
    """

    wanted = tuple(dimensions)
    resolved = tuple(cells) if cells is not None else live_trial_mechanic_cells()
    questions: list[MechanicQuestion] = []
    for cell in resolved:
        questions.extend(
            item
            for item in generate_mechanic_questions(cell)
            if item.dimension in wanted
        )
    return tuple(questions)


@dataclass(frozen=True)
class QuestionSurfaceCoverage:
    covered: tuple[MechanicDimension, ...]
    missing: tuple[MechanicDimension, ...]

    @property
    def complete(self) -> bool:
        return not self.missing


def question_surface_coverage(
    cells: Sequence[MechanicCell] | None = None,
) -> QuestionSurfaceCoverage:
    """Which of the eight dimensions the fixed cells actually expose."""

    emitted = {item.dimension for item in emit_open_questions(cells)}
    return QuestionSurfaceCoverage(
        covered=tuple(item for item in ISSUE_8_DIMENSIONS if item in emitted),
        missing=tuple(item for item in ISSUE_8_DIMENSIONS if item not in emitted),
    )


def question_surface_summary(
    cells: Sequence[MechanicCell] | None = None,
) -> dict[str, object]:
    """Machine-readable view of the surface, filtered and unfiltered.

    Both counts are reported so the eight-dimension filter cannot hide the rest
    of the audit grammar: a surface that showed only what it was asked for would
    be the completeness problem this substrate exists to remove.
    """

    resolved = tuple(cells) if cells is not None else live_trial_mechanic_cells()
    total = sum(len(generate_mechanic_questions(cell)) for cell in resolved)
    emitted = emit_open_questions(resolved)
    by_dimension: dict[str, int] = {}
    for item in emitted:
        by_dimension[item.dimension.value] = by_dimension.get(item.dimension.value, 0) + 1
    coverage = question_surface_coverage(resolved)
    return {
        "provider_required": False,
        "mechanic_cells": len(resolved),
        "open_questions_total": total,
        "open_questions_issue_8": len(emitted),
        "by_dimension": dict(sorted(by_dimension.items())),
        "uncovered_dimensions": [item.value for item in coverage.missing],
        "question_ids": [item.question_id for item in emitted],
    }
