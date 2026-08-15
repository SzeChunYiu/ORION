from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.search import SearchRouteKind
from orion.core.state import OrionState


class SaturationStatus(str, Enum):
    OPEN = "OPEN"
    BOUNDED_SATURATED = "BOUNDED_SATURATED"


DEFAULT_REQUIRED_ROUTE_KINDS = (
    SearchRouteKind.CURRENT_VOCABULARY,
    SearchRouteKind.FUNCTION_ONLY,
    SearchRouteKind.PARENT_DISCIPLINE,
    SearchRouteKind.LITERATURE_BRIDGE,
    SearchRouteKind.ADVERSARIAL_OMISSION,
    SearchRouteKind.FRESHNESS,
)


@dataclass(frozen=True)
class SaturationBasis:
    """Frozen stopping semantics for one scoped solve."""

    basis_id: str = "orion-bootstrap-saturation-v2"
    required_consecutive_flat_rounds: int = 2
    required_route_kinds: tuple[SearchRouteKind, ...] = DEFAULT_REQUIRED_ROUTE_KINDS

    def __post_init__(self) -> None:
        if self.required_consecutive_flat_rounds < 1:
            raise ValueError("required_consecutive_flat_rounds must be positive")
        if not self.required_route_kinds:
            raise ValueError("at least one search route kind is required")


@dataclass(frozen=True)
class SaturationAssessment:
    status: SaturationStatus
    semantic_flat_rounds: int
    search_universe_flat_rounds: int
    formulation_flat_rounds: int
    covered_route_kind_ids: tuple[str, ...]
    missing_route_kind_ids: tuple[str, ...]
    reasons: tuple[str, ...]

    @property
    def bounded_closed(self) -> bool:
        return self.status is SaturationStatus.BOUNDED_SATURATED

    @property
    def absolute_complete(self) -> bool:
        return False


class SaturateOperator:
    """Bounded saturation requires both knowledge flatness and basis challenge."""

    operator_id = "SATURATE_BOUNDED.v3"

    def __init__(self, basis: SaturationBasis | None = None) -> None:
        self._basis = basis or SaturationBasis()

    @staticmethod
    def _suffix(state: OrionState, attribute: str) -> int:
        count = 0
        for record in reversed(state.iterations):
            if bool(getattr(record, attribute)):
                count += 1
            else:
                break
        return count

    def assess(self, state: OrionState) -> SaturationAssessment:
        semantic_flat = self._suffix(state, "semantic_flat")
        universe_flat = self._suffix(state, "search_universe_flat")
        formulation_flat = self._suffix(state, "formulation_flat")
        covered = tuple(state.search_universe.route_kind_ids)
        covered_set = set(covered)
        missing = tuple(
            kind.value for kind in self._basis.required_route_kinds if kind.value not in covered_set
        )

        reasons: list[str] = []
        if any(residual.material for residual in state.knowledge.residuals):
            reasons.append("material_residual_open")
        if semantic_flat < self._basis.required_consecutive_flat_rounds:
            reasons.append("semantic_flatness_insufficient")
        if universe_flat < self._basis.required_consecutive_flat_rounds:
            reasons.append("search_universe_flatness_insufficient")
        if formulation_flat < self._basis.required_consecutive_flat_rounds:
            reasons.append("formulation_flatness_insufficient")
        if missing:
            reasons.append("independent_route_coverage_incomplete")
        if SearchRouteKind.PARENT_DISCIPLINE.value not in covered_set:
            reasons.append("parent_discipline_challenge_missing")
        if SearchRouteKind.LITERATURE_BRIDGE.value not in covered_set:
            reasons.append("literature_bridge_challenge_missing")
        if SearchRouteKind.ADVERSARIAL_OMISSION.value not in covered_set:
            reasons.append("omission_challenge_missing")

        return SaturationAssessment(
            status=SaturationStatus.BOUNDED_SATURATED if not reasons else SaturationStatus.OPEN,
            semantic_flat_rounds=semantic_flat,
            search_universe_flat_rounds=universe_flat,
            formulation_flat_rounds=formulation_flat,
            covered_route_kind_ids=covered,
            missing_route_kind_ids=missing,
            reasons=tuple(dict.fromkeys(reasons)),
        )
