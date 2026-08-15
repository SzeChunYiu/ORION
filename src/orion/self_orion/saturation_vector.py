from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DevelopmentSaturationAxis(str, Enum):
    KNOWLEDGE = "KNOWLEDGE"
    SEARCH_UNIVERSE = "SEARCH_UNIVERSE"
    FORMULATION = "FORMULATION"
    OPERATOR = "OPERATOR"
    EXPERIENCE_PATTERN = "EXPERIENCE_PATTERN"
    OBSTRUCTION = "OBSTRUCTION"
    RELATION = "RELATION"
    PATH = "PATH"
    META_METHOD = "META_METHOD"


@dataclass(frozen=True)
class DevelopmentNoveltyRound:
    round_id: str
    route_family: str
    independent_route: bool
    retained_novelty: tuple[tuple[DevelopmentSaturationAxis, int], ...]
    residual_axes: tuple[DevelopmentSaturationAxis, ...] = ()
    residual_signature: tuple[str, ...] = ()
    resource_bound: bool = False

    def __post_init__(self) -> None:
        if not self.round_id.strip() or not self.route_family.strip():
            raise ValueError("novelty round identity and route family are required")
        axes = [axis for axis, _ in self.retained_novelty]
        if len(set(axes)) != len(axes):
            raise ValueError("each novelty axis may occur once per round")
        if any(count < 0 for _, count in self.retained_novelty):
            raise ValueError("novelty counts cannot be negative")

    def novelty_for(self, axis: DevelopmentSaturationAxis) -> int:
        return dict(self.retained_novelty).get(axis, 0)


@dataclass(frozen=True)
class DevelopmentSaturationAxisReport:
    axis: DevelopmentSaturationAxis
    flat: bool
    independent_flat_route_families: tuple[str, ...]
    recent_retained_novelty: int
    reopen_residuals: tuple[str, ...]


@dataclass(frozen=True)
class DevelopmentSaturationReport:
    axis_reports: tuple[DevelopmentSaturationAxisReport, ...]
    required_axes: tuple[DevelopmentSaturationAxis, ...]
    bounded_saturated: bool
    cannot_check_resource_bound: bool
    reasons: tuple[str, ...]

    @property
    def grants_absolute_completeness(self) -> bool:
        return False

    @property
    def grants_self_promotion(self) -> bool:
        return False

    def flat(self, axis: DevelopmentSaturationAxis) -> bool:
        return next(item.flat for item in self.axis_reports if item.axis is axis)


def assess_development_saturation(
    rounds: tuple[DevelopmentNoveltyRound, ...],
    *,
    required_axes: tuple[DevelopmentSaturationAxis, ...] = tuple(DevelopmentSaturationAxis),
    min_independent_flat_routes: int = 2,
    window: int = 6,
) -> DevelopmentSaturationReport:
    """Bounded multi-axis flatness for Self-ORION research/development.

    Ported conceptually from RAKL saturation_vector. A flat answer on one axis cannot
    compensate for novelty/residuals on another, and resource exhaustion is never
    converted into closure.
    """

    if min_independent_flat_routes < 1 or window < 1:
        raise ValueError("saturation route/window parameters must be positive")
    recent = rounds[-window:]
    reports: list[DevelopmentSaturationAxisReport] = []
    for axis in DevelopmentSaturationAxis:
        flat_routes: list[str] = []
        novelty = 0
        residuals: list[str] = []
        for round_ in recent:
            value = round_.novelty_for(axis)
            novelty += value
            if round_.independent_route and value == 0 and round_.route_family not in flat_routes:
                flat_routes.append(round_.route_family)
            if axis in round_.residual_axes:
                residuals.extend(round_.residual_signature or (f"residual:{round_.round_id}",))
        reports.append(
            DevelopmentSaturationAxisReport(
                axis=axis,
                flat=novelty == 0 and len(flat_routes) >= min_independent_flat_routes and not residuals,
                independent_flat_route_families=tuple(flat_routes),
                recent_retained_novelty=novelty,
                reopen_residuals=tuple(dict.fromkeys(residuals)),
            )
        )
    by_axis = {item.axis: item for item in reports}
    resource_bound = any(item.resource_bound for item in recent)
    reasons: list[str] = []
    for axis in required_axes:
        report = by_axis[axis]
        if report.flat:
            continue
        if report.reopen_residuals:
            reasons.append(f"{axis.value}:reopened_by_native_residual")
        elif report.recent_retained_novelty:
            reasons.append(f"{axis.value}:recent_retained_novelty")
        else:
            reasons.append(f"{axis.value}:insufficient_independent_flat_routes")
    if resource_bound:
        reasons.append("resource_bound_does_not_establish_closure")
    return DevelopmentSaturationReport(
        axis_reports=tuple(reports),
        required_axes=required_axes,
        bounded_saturated=not reasons,
        cannot_check_resource_bound=resource_bound,
        reasons=tuple(reasons),
    )


__all__ = [
    "DevelopmentNoveltyRound",
    "DevelopmentSaturationAxis",
    "DevelopmentSaturationAxisReport",
    "DevelopmentSaturationReport",
    "assess_development_saturation",
]
