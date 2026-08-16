from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class TransferStatus(str, Enum):
    ADMISSIBLE = "ADMISSIBLE"
    BLOCKED_ASSUMPTION = "BLOCKED_ASSUMPTION"
    OBSTRUCTED = "OBSTRUCTED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ProblemSignature:
    """Surface-domain-independent description of a problem.

    The score derived from this object is only a retrieval heuristic. It never grants
    transfer authority; transfer authority is decided by explicit assumptions and
    falsifiers in :class:`AlgorithmCell`.
    """

    problem_id: str
    source_domain: str
    hidden_state: str
    observability: str
    actions: frozenset[str]
    ground_truth: str
    dependence: float
    authority_risk: float
    nonstationarity: float
    reversibility: float

    def __post_init__(self) -> None:
        for name in ("dependence", "authority_risk", "nonstationarity", "reversibility"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {value}")
        if not self.problem_id:
            raise ValueError("problem_id must be non-empty")
        if not self.source_domain:
            raise ValueError("source_domain must be non-empty")

    def structural_similarity(self, other: "ProblemSignature") -> float:
        categorical = (
            float(self.hidden_state == other.hidden_state)
            + float(self.observability == other.observability)
            + float(self.ground_truth == other.ground_truth)
        ) / 3.0
        union = self.actions | other.actions
        action_similarity = len(self.actions & other.actions) / len(union) if union else 1.0
        numeric = sum(
            1.0 - abs(a - b)
            for a, b in (
                (self.dependence, other.dependence),
                (self.authority_risk, other.authority_risk),
                (self.nonstationarity, other.nonstationarity),
                (self.reversibility, other.reversibility),
            )
        ) / 4.0
        return (categorical + action_similarity + numeric) / 3.0

    def far_domain_score(self, other: "ProblemSignature", domain_bonus: float = 0.15) -> float:
        """Rank a structurally similar but domain-distant candidate.

        This is deliberately not an admissibility score. A high value is only a reason
        to *inspect* a candidate mechanism.
        """

        if domain_bonus < 0:
            raise ValueError("domain_bonus must be non-negative")
        distance = 1.0 if self.source_domain != other.source_domain else 0.0
        return self.structural_similarity(other) + domain_bonus * distance


@dataclass(frozen=True)
class AlgorithmCell:
    cell_id: str
    source_signature: ProblemSignature
    mechanism: str
    assumptions: tuple[str, ...]
    invariants: tuple[str, ...]
    stopping_rule: str
    failure_modes: tuple[str, ...]
    falsifiers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.cell_id:
            raise ValueError("cell_id must be non-empty")
        if not self.mechanism:
            raise ValueError("mechanism must be non-empty")
        if not self.assumptions:
            raise ValueError("AlgorithmCell requires at least one explicit assumption")
        if not self.falsifiers:
            raise ValueError("AlgorithmCell requires at least one falsifier")


@dataclass(frozen=True)
class TransferAssessment:
    cell_id: str
    status: TransferStatus
    structural_score: float
    missing_assumptions: tuple[str, ...] = ()
    failed_assumptions: tuple[str, ...] = ()
    unknown_falsifiers: tuple[str, ...] = ()
    failed_falsifiers: tuple[str, ...] = ()

    @property
    def admissible(self) -> bool:
        return self.status is TransferStatus.ADMISSIBLE


def assess_transfer(
    target: ProblemSignature,
    cell: AlgorithmCell,
    assumption_truth: Mapping[str, bool | None],
    falsifier_results: Mapping[str, bool | None],
) -> TransferAssessment:
    """Fail-closed transfer assessment.

    ``True`` for a falsifier means the candidate *passed* the falsification check.
    Unknown prerequisites/falsifiers produce ``CANNOT_CHECK``. A high structural score
    can never override a missing, false, or failed transfer condition.
    """

    score = target.far_domain_score(cell.source_signature)
    failed_assumptions = tuple(a for a in cell.assumptions if assumption_truth.get(a) is False)
    if failed_assumptions:
        return TransferAssessment(
            cell_id=cell.cell_id,
            status=TransferStatus.BLOCKED_ASSUMPTION,
            structural_score=score,
            failed_assumptions=failed_assumptions,
        )

    missing_assumptions = tuple(a for a in cell.assumptions if assumption_truth.get(a) is None)
    if missing_assumptions:
        return TransferAssessment(
            cell_id=cell.cell_id,
            status=TransferStatus.CANNOT_CHECK,
            structural_score=score,
            missing_assumptions=missing_assumptions,
        )

    failed_falsifiers = tuple(f for f in cell.falsifiers if falsifier_results.get(f) is False)
    if failed_falsifiers:
        return TransferAssessment(
            cell_id=cell.cell_id,
            status=TransferStatus.OBSTRUCTED,
            structural_score=score,
            failed_falsifiers=failed_falsifiers,
        )

    unknown_falsifiers = tuple(f for f in cell.falsifiers if falsifier_results.get(f) is None)
    if unknown_falsifiers:
        return TransferAssessment(
            cell_id=cell.cell_id,
            status=TransferStatus.CANNOT_CHECK,
            structural_score=score,
            unknown_falsifiers=unknown_falsifiers,
        )

    return TransferAssessment(
        cell_id=cell.cell_id,
        status=TransferStatus.ADMISSIBLE,
        structural_score=score,
    )
