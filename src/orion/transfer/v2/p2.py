from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from ..discovery import ConservativeRouteAllocator
from .canonical import content_digest


@dataclass(frozen=True)
class RouteConfig:
    baseline_route: str
    baseline_lower_bound: float
    alpha: float
    exploration_bonus: float = 1.0


@dataclass(frozen=True)
class RouteStep:
    route_id: str
    reward: float | None
    censored: bool = False
    lower_bound: float | None = None


class RouteStepStatus(str, Enum):
    APPLIED = "APPLIED"
    REJECTED_SAFETY = "REJECTED_SAFETY"


@dataclass(frozen=True)
class RouteStepReceipt:
    route_id: str
    status: RouteStepStatus
    reward: float | None
    censored: bool
    lower_bound: float | None
    before_state_digest: str
    after_state_digest: str
    safety_credit: float
    receipt_digest: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "ORION_P2_ROUTE_STEP_RECEIPT_V2",
            "route_id": self.route_id,
            "status": self.status.value,
            "reward": self.reward,
            "censored": self.censored,
            "lower_bound": self.lower_bound,
            "before_state_digest": self.before_state_digest,
            "after_state_digest": self.after_state_digest,
            "safety_credit": self.safety_credit,
            "authority_scope": "ROUTE_ALLOCATION_ONLY",
            "can_close_task": False,
        }

    def to_payload(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["receipt_digest"] = self.receipt_digest
        return payload

    def verify(self) -> None:
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("P2 route receipt digest mismatch")


def allocator_state_payload(allocator: ConservativeRouteAllocator) -> dict[str, object]:
    return {
        "baseline_route": allocator.baseline_route,
        "baseline_lower_bound": allocator.baseline_lower_bound,
        "alpha": allocator.alpha,
        "exploration_bonus": allocator.exploration_bonus,
        "steps": allocator.steps,
        "cumulative_lower_bound": allocator.cumulative_lower_bound,
        "required_floor": allocator.required_floor,
        "safety_credit": allocator.safety_credit,
        "routes": {
            route_id: {
                "observed_reward": route.observed_reward,
                "observed_attempts": route.observed_attempts,
                "censored_attempts": route.censored_attempts,
                "mean_reward": route.mean_reward,
            }
            for route_id, route in sorted(allocator.routes.items())
        },
    }


class ReplayableRouteSession:
    def __init__(self, config: RouteConfig, routes: Sequence[str]) -> None:
        if len(routes) != len(set(routes)):
            raise ValueError("route ids must be unique")
        self.config = config
        self.routes = tuple(sorted(set(routes)))
        self.allocator = ConservativeRouteAllocator(
            baseline_route=config.baseline_route,
            baseline_lower_bound=config.baseline_lower_bound,
            alpha=config.alpha,
            exploration_bonus=config.exploration_bonus,
        )
        for route_id in self.routes:
            self.allocator.register(route_id)
        self.receipts: list[RouteStepReceipt] = []

    @property
    def state_digest(self) -> str:
        return content_digest(allocator_state_payload(self.allocator))

    def select_route(self) -> str:
        return self.allocator.select()

    def apply(self, step: RouteStep) -> RouteStepReceipt:
        before_payload = allocator_state_payload(self.allocator)
        before_digest = content_digest(before_payload)
        try:
            self.allocator.record(
                step.route_id,
                reward=step.reward,
                censored=step.censored,
                lower_bound=step.lower_bound,
            )
        except AssertionError:
            after_payload = allocator_state_payload(self.allocator)
            after_digest = content_digest(after_payload)
            if after_payload != before_payload:
                raise AssertionError("rejected route action mutated allocator state")
            receipt = self._receipt(step, RouteStepStatus.REJECTED_SAFETY, before_digest, after_digest)
            self.receipts.append(receipt)
            return receipt
        after_digest = self.state_digest
        receipt = self._receipt(step, RouteStepStatus.APPLIED, before_digest, after_digest)
        self.receipts.append(receipt)
        return receipt

    def _receipt(
        self,
        step: RouteStep,
        status: RouteStepStatus,
        before_digest: str,
        after_digest: str,
    ) -> RouteStepReceipt:
        unsigned = {
            "receipt_version": "ORION_P2_ROUTE_STEP_RECEIPT_V2",
            "route_id": step.route_id,
            "status": status.value,
            "reward": step.reward,
            "censored": step.censored,
            "lower_bound": step.lower_bound,
            "before_state_digest": before_digest,
            "after_state_digest": after_digest,
            "safety_credit": self.allocator.safety_credit,
            "authority_scope": "ROUTE_ALLOCATION_ONLY",
            "can_close_task": False,
        }
        return RouteStepReceipt(
            route_id=step.route_id,
            status=status,
            reward=step.reward,
            censored=step.censored,
            lower_bound=step.lower_bound,
            before_state_digest=before_digest,
            after_state_digest=after_digest,
            safety_credit=self.allocator.safety_credit,
            receipt_digest=content_digest(unsigned),
        )


def replay_route_session(
    config: RouteConfig,
    routes: Sequence[str],
    steps: Sequence[RouteStep],
) -> ReplayableRouteSession:
    session = ReplayableRouteSession(config, routes)
    for step in steps:
        session.apply(step)
    return session
