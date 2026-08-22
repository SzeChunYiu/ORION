from __future__ import annotations

from typing import Any, Mapping

from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.solution import SolutionStatus

from . import recursive_runner as _rr
from .research_director import direct_research


_INSTALLED = False


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _material_residuals_from_record(record: Mapping[str, Any]) -> tuple[Residual, ...]:
    final_state = _mapping(record.get("final_state"))
    knowledge = _mapping(final_state.get("knowledge"))
    raw_rows = knowledge.get("residuals", ())
    if isinstance(raw_rows, (str, bytes)) or not isinstance(raw_rows, (list, tuple)):
        return ()
    residuals: list[Residual] = []
    for raw in raw_rows:
        row = _mapping(raw)
        if not row or row.get("material", True) is not True:
            continue
        raw_responsibilities = row.get("candidate_responsibilities", ())
        if isinstance(raw_responsibilities, (str, bytes)) or not isinstance(
            raw_responsibilities, (list, tuple)
        ):
            responsibilities: tuple[Responsibility, ...] = ()
        else:
            responsibilities = tuple(
                Responsibility(str(item)) for item in raw_responsibilities
            )
        raw_metadata = row.get("metadata", ())
        metadata: list[tuple[str, str]] = []
        if isinstance(raw_metadata, (list, tuple)):
            for item in raw_metadata:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    metadata.append((str(item[0]), str(item[1])))
        residuals.append(
            Residual(
                residual_id=str(row.get("residual_id", "")),
                kind=ResidualKind(str(row.get("kind", ResidualKind.UNCLASSIFIED.value))),
                description=str(row.get("description", "")),
                material=True,
                candidate_responsibilities=responsibilities,
                metadata=tuple(metadata),
            )
        )
    return tuple(residuals)


def _solution_status_from_record(record: Mapping[str, Any]) -> SolutionStatus:
    solution = _mapping(record.get("final_solution"))
    raw = solution.get("status")
    if raw is None:
        return SolutionStatus.CANNOT_CHECK
    return SolutionStatus(str(raw))


def install_research_director_integration() -> None:
    """Attach a deterministic paper-aware next-action directive to solve outcomes.

    The underlying recursive runner and its immutable run receipt remain unchanged.
    The directive is a derived control-plane projection over that immutable receipt,
    so it cannot rewrite scientific evidence or mint closure authority.
    """

    global _INSTALLED
    if _INSTALLED:
        return
    original = _rr.run_problem_recursive

    def run_problem_recursive_with_director(
        workspace,
        problem_data,
        *,
        max_iterations: int = 3,
        require_verified_answer: bool = True,
        limits=None,
    ):
        outcome = original(
            workspace,
            problem_data,
            max_iterations=max_iterations,
            require_verified_answer=require_verified_answer,
            limits=limits,
        )
        run_id = outcome.get("run_id") if isinstance(outcome, Mapping) else None
        if not isinstance(run_id, str) or not run_id:
            return outcome
        record = workspace.load_run(run_id)
        directive = direct_research(
            solution_status=_solution_status_from_record(record),
            material_residuals=_material_residuals_from_record(record),
            resource_bound_hit=bool(record.get("resource_bound_hit", False)),
            identity_ambiguity_hit=bool(record.get("identity_ambiguity_hit", False)),
        )
        return {**dict(outcome), "research_directive": directive.as_dict()}

    _rr.run_problem_recursive = run_problem_recursive_with_director
    _rr._research_director_integration_installed = True
    _INSTALLED = True


install_research_director_integration()


__all__ = ["install_research_director_integration"]
