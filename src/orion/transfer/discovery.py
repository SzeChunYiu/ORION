from __future__ import annotations

from dataclasses import dataclass, field
from math import log, sqrt


@dataclass
class RouteEvidence:
    route_id: str
    observed_reward: float = 0.0
    observed_attempts: int = 0
    censored_attempts: int = 0

    @property
    def mean_reward(self) -> float | None:
        if self.observed_attempts == 0:
            return None
        return self.observed_reward / self.observed_attempts


@dataclass
class ConservativeRouteAllocator:
    """Baseline-preserving route exploration with censored feedback.

    The guarantee is expressed on a *declared lower-bound ledger*, not on unknown true
    reward. If ``credit >= 0`` before and after every action, the declared cumulative
    lower bound stays above ``(1-alpha)`` times the baseline guarantee.
    """

    baseline_route: str
    baseline_lower_bound: float
    alpha: float
    exploration_bonus: float = 1.0
    routes: dict[str, RouteEvidence] = field(default_factory=dict)
    steps: int = 0
    cumulative_lower_bound: float = 0.0

    def __post_init__(self) -> None:
        if self.baseline_lower_bound <= 0:
            raise ValueError("baseline_lower_bound must be positive")
        if not 0.0 < self.alpha < 1.0:
            raise ValueError("alpha must be in (0,1)")
        self.routes.setdefault(self.baseline_route, RouteEvidence(self.baseline_route))

    @property
    def required_floor(self) -> float:
        return (1.0 - self.alpha) * self.baseline_lower_bound * self.steps

    @property
    def safety_credit(self) -> float:
        return self.cumulative_lower_bound - self.required_floor

    def register(self, route_id: str) -> None:
        self.routes.setdefault(route_id, RouteEvidence(route_id))

    def _can_explore(self) -> bool:
        exploration_floor = 0.0
        next_required = (1.0 - self.alpha) * self.baseline_lower_bound * (self.steps + 1)
        return self.cumulative_lower_bound + exploration_floor >= next_required - 1e-12

    def _optimistic_score(self, route: RouteEvidence) -> float:
        if route.observed_attempts == 0:
            return float("inf")
        mean = route.observed_reward / route.observed_attempts
        bonus = self.exploration_bonus * sqrt(
            2.0 * log(max(2, self.steps + 1)) / route.observed_attempts
        )
        return mean + bonus

    def select(self) -> str:
        candidates = [r for r in self.routes.values() if r.route_id != self.baseline_route]
        if not candidates or not self._can_explore():
            return self.baseline_route
        return max(candidates, key=lambda r: (self._optimistic_score(r), r.route_id)).route_id

    def record(
        self,
        route_id: str,
        *,
        reward: float | None,
        censored: bool = False,
        lower_bound: float | None = None,
    ) -> None:
        if route_id not in self.routes:
            raise KeyError(route_id)
        if censored:
            if reward is not None:
                raise ValueError("censored observations cannot carry a reward")
        else:
            if reward is None or reward < 0:
                raise ValueError("observed reward must be a non-negative number")

        if lower_bound is None:
            lower_bound = self.baseline_lower_bound if route_id == self.baseline_route else 0.0
        if lower_bound < 0:
            raise ValueError("lower_bound must be non-negative")
        next_steps = self.steps + 1
        next_lower_bound = self.cumulative_lower_bound + lower_bound
        next_required = (1.0 - self.alpha) * self.baseline_lower_bound * next_steps
        if next_lower_bound < next_required - 1e-9:
            raise AssertionError("conservative safety invariant violated")

        # Commit state only after the lower-bound invariant has been checked.
        if censored:
            self.routes[route_id].censored_attempts += 1
        else:
            route = self.routes[route_id]
            route.observed_reward += reward
            route.observed_attempts += 1
        self.cumulative_lower_bound = next_lower_bound
        self.steps = next_steps
