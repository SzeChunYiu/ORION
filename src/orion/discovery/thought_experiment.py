"""Proposal-side thought experiments for the ORION Jump research programme.

A thought experiment is represented as a registered discrimination proposal.  It
may relax selected assumptions, hold others fixed, and record expected outcomes
under competing hypotheses.  Prospective discrimination is computed only from
those registered predictions; it is not evidence that the predictions are true.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


def _canonical_expected_outcomes(
    values: Mapping[str, Sequence[str]],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    rows: list[tuple[str, tuple[str, ...]]] = []
    for raw_hypothesis, raw_outcomes in values.items():
        hypothesis = str(raw_hypothesis)
        outcomes = _sorted_unique(raw_outcomes)
        if not hypothesis or not outcomes:
            raise ValueError("each thought-experiment hypothesis needs expected outcomes")
        rows.append((hypothesis, outcomes))
    rows.sort(key=lambda row: row[0])
    if len(rows) < 2:
        raise ValueError("thought experiment requires at least two competing hypotheses")
    return tuple(rows)


class ExecutionMode(str, Enum):
    SIMULATED = "SIMULATED"
    PHYSICAL = "PHYSICAL"
    FORMAL = "FORMAL"


class ProspectiveDiscriminationStatus(str, Enum):
    NONE = "NONE"
    PARTIAL = "PARTIAL"
    FULL = "FULL"


@dataclass(frozen=True)
class ThoughtExperiment:
    experiment_id: str
    tension_digest: str
    operation_kind: str
    relaxed_assumptions: tuple[str, ...]
    held_fixed_assumptions: tuple[str, ...]
    hypothetical_setup_id: str
    expected_outcomes: tuple[tuple[str, tuple[str, ...]], ...]
    execution_mode: ExecutionMode
    cost: float
    safety_constraints: tuple[str, ...]
    digest: str

    @property
    def grants_theory_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ThoughtExperiment.v1",
            "experiment_id": self.experiment_id,
            "tension_digest": self.tension_digest,
            "operation_kind": self.operation_kind,
            "relaxed_assumptions": list(self.relaxed_assumptions),
            "held_fixed_assumptions": list(self.held_fixed_assumptions),
            "hypothetical_setup_id": self.hypothetical_setup_id,
            "expected_outcomes": [
                [hypothesis, list(outcomes)]
                for hypothesis, outcomes in self.expected_outcomes
            ],
            "execution_mode": self.execution_mode.value,
            "cost": self.cost,
            "safety_constraints": list(self.safety_constraints),
            "grants_theory_authority": False,
        }

    def verify(self) -> None:
        if not self.experiment_id or not self.tension_digest or not self.operation_kind:
            raise ValueError("thought experiment, tension, and operation identities are required")
        if not self.hypothetical_setup_id:
            raise ValueError("thought experiment requires a hypothetical setup identity")
        overlap = set(self.relaxed_assumptions) & set(self.held_fixed_assumptions)
        if overlap:
            raise ValueError(
                "thought experiment cannot relax assumptions that are also held fixed: "
                + ",".join(sorted(overlap))
            )
        if self.cost < 0:
            raise ValueError("thought experiment cost must be non-negative")
        if len(self.expected_outcomes) < 2:
            raise ValueError("thought experiment requires competing hypotheses")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("thought experiment digest mismatch")


def build_thought_experiment(
    *,
    experiment_id: str,
    tension_digest: str,
    operation_kind: str,
    hypothetical_setup_id: str,
    expected_outcomes: Mapping[str, Sequence[str]],
    execution_mode: ExecutionMode,
    cost: float,
    relaxed_assumptions: Sequence[str] = (),
    held_fixed_assumptions: Sequence[str] = (),
    safety_constraints: Sequence[str] = (),
) -> ThoughtExperiment:
    expected = _canonical_expected_outcomes(expected_outcomes)
    payload = {
        "version": "ThoughtExperiment.v1",
        "experiment_id": str(experiment_id),
        "tension_digest": str(tension_digest),
        "operation_kind": str(operation_kind),
        "relaxed_assumptions": list(_sorted_unique(relaxed_assumptions)),
        "held_fixed_assumptions": list(_sorted_unique(held_fixed_assumptions)),
        "hypothetical_setup_id": str(hypothetical_setup_id),
        "expected_outcomes": [
            [hypothesis, list(outcomes)] for hypothesis, outcomes in expected
        ],
        "execution_mode": ExecutionMode(execution_mode).value,
        "cost": float(cost),
        "safety_constraints": list(_sorted_unique(safety_constraints)),
        "grants_theory_authority": False,
    }
    experiment = ThoughtExperiment(
        experiment_id=payload["experiment_id"],
        tension_digest=payload["tension_digest"],
        operation_kind=payload["operation_kind"],
        relaxed_assumptions=tuple(payload["relaxed_assumptions"]),
        held_fixed_assumptions=tuple(payload["held_fixed_assumptions"]),
        hypothetical_setup_id=payload["hypothetical_setup_id"],
        expected_outcomes=expected,
        execution_mode=ExecutionMode(payload["execution_mode"]),
        cost=payload["cost"],
        safety_constraints=tuple(payload["safety_constraints"]),
        digest=content_digest(payload),
    )
    experiment.verify()
    return experiment


@dataclass(frozen=True)
class ProspectiveDiscriminationReport:
    experiment_digest: str
    status: ProspectiveDiscriminationStatus
    distinguishable_pairs: int
    total_pairs: int
    indistinguishable_hypothesis_pairs: tuple[tuple[str, str], ...]
    digest: str

    @property
    def grants_theory_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ProspectiveThoughtExperimentDiscrimination.v1",
            "experiment_digest": self.experiment_digest,
            "status": self.status.value,
            "distinguishable_pairs": self.distinguishable_pairs,
            "total_pairs": self.total_pairs,
            "indistinguishable_hypothesis_pairs": [
                list(pair) for pair in self.indistinguishable_hypothesis_pairs
            ],
            "grants_theory_authority": False,
        }

    def verify(self) -> None:
        if self.distinguishable_pairs < 0 or self.total_pairs <= 0:
            raise ValueError("invalid prospective discrimination counts")
        if self.distinguishable_pairs > self.total_pairs:
            raise ValueError("distinguishable pairs cannot exceed total pairs")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("prospective discrimination digest mismatch")


def assess_prospective_discrimination(
    experiment: ThoughtExperiment,
) -> ProspectiveDiscriminationReport:
    experiment.verify()
    predictions = {
        hypothesis: set(outcomes) for hypothesis, outcomes in experiment.expected_outcomes
    }
    pairs = list(combinations(sorted(predictions), 2))
    indistinguishable: list[tuple[str, str]] = []
    distinguishable = 0
    for left, right in pairs:
        if predictions[left].isdisjoint(predictions[right]):
            distinguishable += 1
        else:
            indistinguishable.append((left, right))
    total = len(pairs)
    if distinguishable == 0:
        status = ProspectiveDiscriminationStatus.NONE
    elif distinguishable == total:
        status = ProspectiveDiscriminationStatus.FULL
    else:
        status = ProspectiveDiscriminationStatus.PARTIAL

    payload = {
        "version": "ProspectiveThoughtExperimentDiscrimination.v1",
        "experiment_digest": experiment.digest,
        "status": status.value,
        "distinguishable_pairs": distinguishable,
        "total_pairs": total,
        "indistinguishable_hypothesis_pairs": [list(pair) for pair in indistinguishable],
        "grants_theory_authority": False,
    }
    report = ProspectiveDiscriminationReport(
        experiment_digest=experiment.digest,
        status=status,
        distinguishable_pairs=distinguishable,
        total_pairs=total,
        indistinguishable_hypothesis_pairs=tuple(indistinguishable),
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "ExecutionMode",
    "ProspectiveDiscriminationReport",
    "ProspectiveDiscriminationStatus",
    "ThoughtExperiment",
    "assess_prospective_discrimination",
    "build_thought_experiment",
]
