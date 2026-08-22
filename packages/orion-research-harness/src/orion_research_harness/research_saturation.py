from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from orion.self_orion.saturation_vector import (
    DevelopmentNoveltyRound,
    DevelopmentSaturationAxis,
    DevelopmentSaturationReport,
    assess_development_saturation,
)

from .epistemic_navigation import RouteContract, structurally_independent


@dataclass(frozen=True)
class ResearchRoundEvidence:
    """Observed research movement from one executed route round.

    `axis_item_ids` carries identities actually observed on each development axis.
    Novelty is derived by set difference; callers never supply novelty counts.
    `observed_axes` is explicit so an uninstrumented axis cannot accidentally look flat.
    """

    round_id: str
    route_contracts: tuple[RouteContract, ...]
    observed_axes: tuple[DevelopmentSaturationAxis, ...]
    axis_item_ids: tuple[tuple[DevelopmentSaturationAxis, tuple[str, ...]], ...]
    residual_axes: tuple[DevelopmentSaturationAxis, ...] = ()
    residual_signature: tuple[str, ...] = ()
    resource_bound: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.round_id, str) or not self.round_id.strip():
            raise ValueError("round_id is required")
        route_ids = [item.route_id for item in self.route_contracts]
        if len(route_ids) != len(set(route_ids)):
            raise ValueError("route contracts must have unique identities per round")
        if len(self.observed_axes) != len(set(self.observed_axes)):
            raise ValueError("observed_axes must be unique")
        rows: list[tuple[DevelopmentSaturationAxis, tuple[str, ...]]] = []
        seen_axes: set[DevelopmentSaturationAxis] = set()
        for axis, raw_ids in self.axis_item_ids:
            if axis in seen_axes:
                raise ValueError("axis_item_ids may contain each axis once")
            seen_axes.add(axis)
            if isinstance(raw_ids, (str, bytes)):
                raise TypeError("axis item ids must be an array")
            ids = tuple(str(item) for item in raw_ids)
            if any(not item.strip() for item in ids):
                raise ValueError("axis item identities must be non-empty")
            if len(ids) != len(set(ids)):
                raise ValueError("axis item identities must be unique")
            rows.append((axis, ids))
        object.__setattr__(self, "axis_item_ids", tuple(rows))
        if len(self.residual_axes) != len(set(self.residual_axes)):
            raise ValueError("residual_axes must be unique")
        if any(not isinstance(item, str) or not item.strip() for item in self.residual_signature):
            raise ValueError("residual signatures must be non-empty strings")
        if not isinstance(self.resource_bound, bool):
            raise TypeError("resource_bound must be boolean")


def _route_family(round_: ResearchRoundEvidence) -> str:
    if not round_.route_contracts:
        return f"UNIDENTIFIED:{round_.round_id}"
    return "+".join(sorted({item.route_family for item in round_.route_contracts}))


def _round_independent(
    round_: ResearchRoundEvidence,
    prior_routes: Sequence[RouteContract],
) -> bool:
    """Derive, never accept, the independence bit consumed by canonical saturation."""

    if not round_.route_contracts:
        return False
    if any(not route.structurally_identified for route in round_.route_contracts):
        return False
    if not prior_routes:
        return True
    return any(
        all(structurally_independent(route, previous) for previous in prior_routes)
        for route in round_.route_contracts
    )


def derive_development_novelty_rounds(
    rounds: Sequence[ResearchRoundEvidence],
    *,
    required_axes: tuple[DevelopmentSaturationAxis, ...] = tuple(DevelopmentSaturationAxis),
) -> tuple[DevelopmentNoveltyRound, ...]:
    seen: dict[DevelopmentSaturationAxis, set[str]] = {
        axis: set() for axis in DevelopmentSaturationAxis
    }
    prior_routes: list[RouteContract] = []
    derived: list[DevelopmentNoveltyRound] = []
    required = set(required_axes)
    for round_ in rounds:
        by_axis = dict(round_.axis_item_ids)
        observed = set(round_.observed_axes)
        retained: list[tuple[DevelopmentSaturationAxis, int]] = []
        missing = required - observed
        residual_axes = list(round_.residual_axes)
        residual_signature = list(round_.residual_signature)
        for axis in DevelopmentSaturationAxis:
            values = set(by_axis.get(axis, ()))
            new = values - seen[axis]
            seen[axis].update(values)
            retained.append((axis, len(new)))
        for axis in sorted(missing, key=lambda item: item.value):
            if axis not in residual_axes:
                residual_axes.append(axis)
            residual_signature.append(f"unobserved-axis:{axis.value}")
        independent = _round_independent(round_, prior_routes)
        derived.append(
            DevelopmentNoveltyRound(
                round_id=round_.round_id,
                route_family=_route_family(round_),
                independent_route=independent,
                retained_novelty=tuple(retained),
                residual_axes=tuple(residual_axes),
                residual_signature=tuple(dict.fromkeys(residual_signature)),
                resource_bound=round_.resource_bound,
            )
        )
        for route in round_.route_contracts:
            if route.route_id not in {item.route_id for item in prior_routes}:
                prior_routes.append(route)
    return tuple(derived)


def assess_evidence_derived_saturation(
    rounds: Sequence[ResearchRoundEvidence],
    *,
    required_axes: tuple[DevelopmentSaturationAxis, ...] = tuple(DevelopmentSaturationAxis),
    min_independent_flat_routes: int = 2,
    window: int = 6,
) -> DevelopmentSaturationReport:
    derived = derive_development_novelty_rounds(rounds, required_axes=required_axes)
    return assess_development_saturation(
        derived,
        required_axes=required_axes,
        min_independent_flat_routes=min_independent_flat_routes,
        window=window,
    )


__all__ = [
    "ResearchRoundEvidence",
    "assess_evidence_derived_saturation",
    "derive_development_novelty_rounds",
]
