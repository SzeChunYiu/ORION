from __future__ import annotations

from dataclasses import replace

from orion.core.problem import Problem
from orion.core.state import OrionState
from orion.donors.composition import normal_orion_donor_graph, orion_q_donor_graph
from orion.engine.navigation import PaperParityNavigator, ProblemNavigationPlan
from orion.engine.solver import OrionSolver


class PaperParityOrionSolver(OrionSolver):
    """Canonical ORION solver with paper-described navigation bound into M_t.

    The existing operator kernel still performs FRAME/SEARCH/ABSORB/RECONSTRUCT/
    DETECT/DIAGNOSE/REFRAME/REOPEN/SATURATE. This wrapper makes recursive atomization,
    fibre navigation, capability modality, strongest-incumbent donors and their
    composition graph part of the state whose endpoints the trace binds.
    """

    def __init__(self, *args, navigator: PaperParityNavigator | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._paper_navigator = navigator or PaperParityNavigator.normal()
        self._last_navigation_plan: ProblemNavigationPlan | None = None

    @property
    def last_navigation_plan(self) -> ProblemNavigationPlan | None:
        return self._last_navigation_plan

    def _bind_navigation(
        self,
        problem: Problem,
        state: OrionState,
    ) -> tuple[OrionState, ProblemNavigationPlan]:
        plan = self._paper_navigator.plan(problem)
        graph = orion_q_donor_graph() if plan.profile == "orion-q" else normal_orion_donor_graph()
        graph.validate(self._paper_navigator.donor_registry)
        method = state.method
        if method.navigation_plan_digest and method.navigation_plan_digest != plan.plan_digest:
            raise ValueError(
                "initial ORION state is bound to a stale/different navigation plan; "
                "reopen or reconstruct the state before replay"
            )
        if (
            method.donor_composition_graph_digest
            and method.donor_composition_graph_digest != graph.graph_digest
        ):
            raise ValueError(
                "initial ORION state is bound to a stale/different donor composition graph"
            )
        bound_method = replace(
            method,
            navigation_profile=plan.profile,
            navigation_plan_digest=plan.plan_digest,
            atomization_digest=plan.atomization_digest,
            donor_registry_id=plan.donor_registry_id,
            donor_registry_digest=plan.donor_registry_digest,
            donor_composition_graph_id=graph.graph_id,
            donor_composition_graph_digest=graph.graph_digest,
            active_fibre_ids=plan.active_fibre_ids,
            deferred_donor_obligation_ids=plan.deferred_donor_obligation_ids,
        )
        metadata = dict(state.metadata)
        metadata.update(
            {
                "navigation_plan_digest": plan.plan_digest,
                "atomization_digest": plan.atomization_digest,
                "donor_registry_digest": plan.donor_registry_digest,
                "donor_composition_graph_digest": graph.graph_digest,
                "navigation_profile": plan.profile,
            }
        )
        bound = replace(state, method=bound_method, metadata=tuple(sorted(metadata.items())))
        self._last_navigation_plan = plan
        return bound, plan

    def bind_initial_state(self, problem: Problem, state: OrionState) -> OrionState:
        """Return the exact navigation-bound state at which tracing starts."""

        bound, _ = self._bind_navigation(problem, state)
        return bound

    def initial_state(self, problem: Problem) -> OrionState:
        state = super().initial_state(problem)
        return self.bind_initial_state(problem, state)

    def solve(
        self,
        problem: Problem,
        *,
        initial_state: OrionState | None = None,
        trace_id: str | None = None,
    ):
        state = (
            initial_state
            if initial_state is not None
            else super().initial_state(problem)
        )
        bound = self.bind_initial_state(problem, state)
        return super().solve(problem, initial_state=bound, trace_id=trace_id)


__all__ = ["PaperParityOrionSolver"]
