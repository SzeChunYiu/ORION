from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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
    candidate_responsibilities: tuple[Responsibility, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()

    def metadata_dict(self) -> dict[str, str]:
        return dict(self.metadata)
