from __future__ import annotations

from typing import Any

from . import recursive_runner as _rr


_INSTALLED = False


def install_recursive_budget_hardening() -> None:
    """Preserve receipted state when root recursion exhausts its node budget.

    The recursive controller now handles the pre-child root budget boundary directly.
    This fallback covers any hard node-budget exception reached after a completed
    child (for example, while attempting a parent refresh). It returns the same
    root-scoped CANNOT_CHECK snapshot helper over the last completed semantic state,
    never relabels a child trace as a root trace, and never invents evidence.
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

            final_state = _rr._without_problem_local_residuals(last_result.final_state)
            snapshot = self._resource_bound_snapshot(
                problem=problem,
                state=final_state,
            )
            return snapshot, final_state

    session_cls._record_runtime = record_runtime_with_checkpoint
    session_cls.solve_root = solve_root_preserving_checkpoint
    session_cls._recursive_budget_hardening_installed = True
    _INSTALLED = True


install_recursive_budget_hardening()


__all__ = ["install_recursive_budget_hardening"]
