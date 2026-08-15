from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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


class ResidualKind(str, Enum):
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    CONTRADICTION = "CONTRADICTION"
    CONTEXT_GAP = "CONTEXT_GAP"
    REPRESENTATION_FAILURE = "REPRESENTATION_FAILURE"
    SEARCH_COVERAGE_FAILURE = "SEARCH_COVERAGE_FAILURE"
    DECOMPOSITION_FAILURE = "DECOMPOSITION_FAILURE"
    INTERFACE_FAILURE = "INTERFACE_FAILURE"
    MEASUREMENT_FAILURE = "MEASUREMENT_FAILURE"
    EVALUATOR_FAILURE = "EVALUATOR_FAILURE"
    METHOD_GAP = "METHOD_GAP"
    UNCLASSIFIED = "UNCLASSIFIED"


class Responsibility(str, Enum):
    QUESTION = "QUESTION"
    REPRESENTATION = "REPRESENTATION"
    SEARCH = "SEARCH"
    ROUTING = "ROUTING"
    DECOMPOSITION = "DECOMPOSITION"
    INTERFACE = "INTERFACE"
    MEASUREMENT = "MEASUREMENT"
    EVALUATOR = "EVALUATOR"
    METHOD = "METHOD"
    EVIDENCE = "EVIDENCE"
    EXECUTION = "EXECUTION"


@dataclass(frozen=True)
class Residual:
    residual_id: str
    kind: ResidualKind
    description: str
    material: bool = True


@dataclass(frozen=True)
class Transition:
    operator: CycleOperator
    input_epoch: int
    output_epoch: int
    evidence_ids: tuple[str, ...] = ()
    residual_ids: tuple[str, ...] = ()
    authority_increase: bool = False
    scientific_authority_certificate_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.output_epoch < self.input_epoch:
            raise ValueError("ORION transitions cannot move backward in epoch")
        if self.operator in {CycleOperator.SEARCH, CycleOperator.FRAME} and self.authority_increase:
            raise ValueError("FRAME/SEARCH cannot directly increase scientific authority")
        if self.authority_increase and not self.scientific_authority_certificate_ids:
            raise ValueError("authority increase requires certificate-producing evidence")


def revision_allowed(responsibilities: tuple[Responsibility, ...]) -> bool:
    """High-impact reframing is blocked while responsibility remains ambiguous."""

    return len(set(responsibilities)) == 1
