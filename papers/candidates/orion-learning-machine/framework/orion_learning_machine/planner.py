from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Hashable
import math
from .library import MechanicLibrary
from .competence import CompetenceMap
from .types import PlanStep, SolverPlan, Verdict

FeatureFn = Callable[[Any, str], dict[str, float]]
GoalFn = Callable[[Any], bool]
TransitionFn = Callable[[Any, str], Any | None]
StateKeyFn = Callable[[Any], Hashable]

@dataclass
class _Node:
    state: Any
    steps: tuple[PlanStep, ...]
    p: float
    cost: float
    visited: tuple[Hashable, ...] = ()

class ExplicitPlanner:
    """Beam-search planner over named mechanics.

    Plans remain inspectable rather than hidden in model weights.  Optional
    state keys provide fail-closed cycle pruning for domains where a stable
    state identity is available; the planner does not invent identity by
    stringifying arbitrary states.
    """
    def __init__(self, library: MechanicLibrary, competence: CompetenceMap) -> None:
        self.library = library
        self.competence = competence

    def plan(
        self,
        state: Any,
        feature_fn: FeatureFn,
        transition_model: TransitionFn,
        goal_fn: GoalFn,
        max_depth: int = 8,
        beam: int = 16,
        unknown_penalty: float = 0.35,
        state_key: StateKeyFn | None = None,
        max_state_visits: int = 1,
    ) -> SolverPlan:
        if max_depth < 0 or beam <= 0 or max_state_visits <= 0:
            raise ValueError("invalid planner bounds")
        first_key=state_key(state) if state_key else None
        frontier=[_Node(state, (), 1.0, 0.0, (() if state_key is None else (first_key,)))]
        best_unknown=False
        for depth in range(max_depth+1):
            for n in frontier:
                if goal_fn(n.state):
                    prov=tuple(p for s in n.steps for p in self.library.resolve(s.mechanic_id).provenance)
                    return SolverPlan(n.steps, n.p, n.cost, Verdict.SUCCESS, prov)
            if depth == max_depth:
                break
            nxt=[]
            for n in frontier:
                for spec in self.library.mechanics:
                    est=self.competence.estimate(spec.mechanic_id, feature_fn(n.state, spec.mechanic_id))
                    if est.status == Verdict.UNKNOWN:
                        best_unknown=True
                        p=unknown_penalty
                    elif est.status == Verdict.FAIL and est.p_success < 0.25:
                        continue
                    else:
                        p=max(est.p_success, 1e-4)
                    ns=transition_model(n.state, spec.mechanic_id)
                    if ns is None:
                        continue
                    visited=n.visited
                    if state_key is not None:
                        k=state_key(ns)
                        if sum(1 for old in visited if old == k) >= max_state_visits:
                            continue
                        visited=visited+(k,)
                    step=PlanStep(spec.mechanic_id,p,spec.cost,f"competence={est.status.value};distance={est.nearest_distance:.3g}")
                    nxt.append(_Node(ns,n.steps+(step,),n.p*p,n.cost+spec.cost,visited))
            if not nxt:
                break
            def score(x: _Node):
                return math.log(max(x.p,1e-12)) - 0.035*x.cost
            nxt.sort(key=score, reverse=True)
            frontier=nxt[:beam]
        return SolverPlan((),0.0,0.0,Verdict.UNKNOWN if best_unknown else Verdict.FAIL,())
