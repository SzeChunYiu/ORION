from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.residuals import Residual, ResidualKind, Responsibility


class CycleOperator(str, Enum):
    FRAME = "FRAME"
    SEARCH = "SEARCH"
    ABSORB = "ABSORB"
    RECONSTRUCT = "RECONSTRUCT"
    DETECT = "DETECT"
    DIAGNOSE = "DIAGNOSE"
    REFRAME = "REFRAME"
    REOPEN = "REOPEN"
    RECURSE = "RECURSE"
    SATURATE_BOUNDED = "SATURATE_BOUNDED"


_NON_AUTHORITY_OPERATORS = frozenset(
    {
        CycleOperator.FRAME,
        CycleOperator.SEARCH,
        CycleOperator.RECONSTRUCT,
        CycleOperator.DETECT,
        CycleOperator.DIAGNOSE,
        CycleOperator.REFRAME,
        CycleOperator.REOPEN,
        CycleOperator.RECURSE,
        CycleOperator.SATURATE_BOUNDED,
    }
)


@dataclass(frozen=True)
class Transition:
    operator: CycleOperator
    input_epoch: int
    output_epoch: int
    evidence_ids: tuple[str, ...] = ()
    residual_ids: tuple[str, ...] = ()
    authority_increase: bool = False
    scientific_authority_certificate_ids: tuple[str, ...] = ()
    changed_coordinates: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.output_epoch < self.input_epoch:
            raise ValueError("ORION transitions cannot move backward in epoch")
        if self.operator in _NON_AUTHORITY_OPERATORS and self.authority_increase:
            raise ValueError(f"{self.operator.value} cannot directly increase scientific authority")
        if self.authority_increase and not self.scientific_authority_certificate_ids:
            raise ValueError("authority increase requires certificate-producing evidence")


def revision_allowed(responsibilities: tuple[Responsibility, ...]) -> bool:
    """High-impact reframing is blocked while responsibility remains ambiguous."""

    return len(set(responsibilities)) == 1 and bool(responsibilities)


__all__ = [
    "CycleOperator",
    "Residual",
    "ResidualKind",
    "Responsibility",
    "Transition",
    "revision_allowed",
]
