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

# Responsibilities whose local repair is genuinely a formulation/search-space
# revision. METHOD/EVALUATOR changes are separately protected by Self-ORION;
# EVIDENCE and EXECUTION call for acquisition/retry/implementation repair rather
# than rewriting the research formulation.
_LOCAL_REFRAME_RESPONSIBILITIES = frozenset(
    {
        Responsibility.QUESTION,
        Responsibility.REPRESENTATION,
        Responsibility.SEARCH,
        Responsibility.ROUTING,
        Responsibility.DECOMPOSITION,
        Responsibility.INTERFACE,
        Responsibility.MEASUREMENT,
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
    """High-impact revision is blocked while responsibility remains ambiguous."""

    return len(set(responsibilities)) == 1 and bool(responsibilities)


def local_reframe_allowed(responsibility: Responsibility) -> bool:
    """Whether the diagnosed responsibility is licensed for local REFRAME.

    This is deliberately narrower than `revision_allowed`: a singular diagnosis
    can still point to an acquisition/execution problem whose correct next action
    is not a formulation rewrite.
    """

    return responsibility in _LOCAL_REFRAME_RESPONSIBILITIES


__all__ = [
    "CycleOperator",
    "Residual",
    "ResidualKind",
    "Responsibility",
    "Transition",
    "local_reframe_allowed",
    "revision_allowed",
]
