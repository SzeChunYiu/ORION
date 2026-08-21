from __future__ import annotations

from typing import Any

from orion.core.solution import Solution, SolutionStatus
from orion.runtime import RuntimeResult

from . import recursive_runner as _rr


_INSTALLED = False


def install_recursive_budget_hardening() -> None:
    """Preserve receipted state when root recursion exhausts its node budget.

    The recursive controller records a CANNOT_CHECK resource bound before attempting
    a root snapshot. The legacy snapshot call consumes another node and therefore
    re-raises once the hard budget is already full. This hardening returns a
    root-bound CANNOT_CHECK snapshot over the last successfully receipted state;
    it never relabels a child result as root success and never invents evidence.
    """

    global _INSTALLED
    if _INSTALLED:
        return

    session_cls = _rr._RecursiveSession
    original_record_runtime = session_cls._record_runtime
    original_solve_root = session_cls.solve_root

    def record_runtime_with_checkpoint(self, *args: Any, **kwargs: Any) -> None:
        result = kwargs.get("result")
        if result is None and len(args) >= 2:
            result = args[1]
        original_record_runtime(self, *args, **kwargs)
        if result is not None:
            self._last_completed_runtime_result = result

    def solve_root_preserving_checkpoint(self, *, problem, state):
        try:
            return original_solve_root(self, problem=problem, state=state)
        except RuntimeError as exc:
            if str(exc) != "RECURSIVE_NODE_BUDGET_EXHAUSTED":
                raise
            self.resource_bound_hit = True
            last_result = getattr(self, "_last_completed_runtime_result", None)
            if last_result is None:
                # No completed node exists to preserve. The outer runner exposes the
                # original hard resource-bound CANNOT_CHECK without a forged snapshot.
                raise
            if not any(
                row.get("stop_reason") == "CANNOT_CHECK_RESOURCE_BOUND"
                for row in self.stop_records
            ):
                self._record_stop(
                    problem_id=problem.problem_id,
                    residual_id="",
                    stop_reason="CANNOT_CHECK_RESOURCE_BOUND",
                )

            final_state = last_result.final_state
            snapshot = RuntimeResult(
                solution=Solution(
                    problem_id=problem.problem_id,
                    status=SolutionStatus.CANNOT_CHECK,
                    answer=(
                        "Recursive node budget exhausted before the root problem could "
                        "be closed; accumulated verified/negative state is preserved."
                    ),
                    evidence_ids=(),
                    residual_ids=final_state.knowledge.residual_ids,
                    iterations=0,
                    trace_id=last_result.trace.trace_id,
                ),
                final_state=final_state,
                trace=last_result.trace,
                experience_episode_id=last_result.experience_episode_id,
                mechanic_experience_episode_ids=(
                    last_result.mechanic_experience_episode_ids
                ),
            )
            return snapshot, _rr._without_problem_local_residuals(final_state)

    session_cls._record_runtime = record_runtime_with_checkpoint
    session_cls.solve_root = solve_root_preserving_checkpoint
    session_cls._recursive_budget_hardening_installed = True
    _INSTALLED = True


install_recursive_budget_hardening()


__all__ = ["install_recursive_budget_hardening"]
