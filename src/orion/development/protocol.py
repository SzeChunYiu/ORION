from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.engine.operators.saturate import SaturationAssessment


class DevelopmentImpact(str, Enum):
    LOW = "LOW"
    HIGH = "HIGH"


@dataclass(frozen=True)
class DevelopmentAtom:
    atom_id: str
    question: str
    dependency_atom_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.atom_id.strip() or not self.question.strip():
            raise ValueError("development atom identity and question are required")


@dataclass(frozen=True)
class BasisChallenge:
    """Explicit challenge to the knowledge/search basis before implementation."""

    challenge_id: str
    saturation_could_be_false_if: tuple[str, ...]
    potentially_missing_parent_domains: tuple[str, ...]
    prior_miss_hypotheses: tuple[str, ...]
    reopen_triggers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.challenge_id.strip():
            raise ValueError("challenge_id is required")
        if not self.saturation_could_be_false_if:
            raise ValueError("basis challenge must state how saturation could be false")
        if not self.prior_miss_hypotheses:
            raise ValueError("basis challenge must ask why relevant knowledge may have been missed")
        if not self.reopen_triggers:
            raise ValueError("basis challenge must define reopen triggers")


@dataclass(frozen=True)
class DevelopmentPacket:
    task_id: str
    impact: DevelopmentImpact
    atoms: tuple[DevelopmentAtom, ...]
    saturation: SaturationAssessment | None
    basis_challenge: BasisChallenge | None
    implementation_hypothesis: str
    low_impact_saturation_waiver_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.implementation_hypothesis.strip():
            raise ValueError("development task identity and implementation hypothesis are required")


def assert_ready_to_implement(packet: DevelopmentPacket) -> None:
    """Fail closed on high-impact coding before ORION-style knowledge work is complete."""

    if not packet.atoms:
        raise ValueError("development task must be atomized before implementation")
    if packet.impact is DevelopmentImpact.LOW:
        if not packet.low_impact_saturation_waiver_reason:
            raise ValueError("low-impact saturation waiver requires an explicit reason")
        return
    if packet.saturation is None or not packet.saturation.bounded_closed:
        raise ValueError("high-impact development requires bounded knowledge/formulation saturation")
    if packet.basis_challenge is None:
        raise ValueError("high-impact development requires an explicit saturation-basis challenge")
