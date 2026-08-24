"""Execution/science separation and protected recursive adoption."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Mapping, Sequence

from .model import ExecutionIntegrity, Terminal
from .sufficiency import FiniteInterface, minimal_collision


@dataclass(frozen=True)
class ExecutionScienceCase:
    case_id: str
    integrity: ExecutionIntegrity
    scientific_terminal: Terminal


def integrity_interface(cases: Sequence[ExecutionScienceCase]) -> FiniteInterface:
    return FiniteInterface(
        name="execution-integrity-only",
        observations={case.case_id: case.integrity for case in cases},
    )


def integrity_does_not_identify_science(cases: Sequence[ExecutionScienceCase]) -> bool:
    states = tuple(case.case_id for case in cases)
    target = {case.case_id: case.scientific_terminal for case in cases}
    return minimal_collision(states, integrity_interface(cases), target) is not None


@dataclass(frozen=True)
class AdoptionWorld:
    world_id: str
    candidate_visible_record: Hashable
    protected_record: Hashable
    safe_to_adopt: bool


def candidate_only_adoption_is_identifying(worlds: Sequence[AdoptionWorld]) -> bool:
    seen: dict[Hashable, bool] = {}
    for world in worlds:
        previous = seen.setdefault(world.candidate_visible_record, world.safe_to_adopt)
        if previous != world.safe_to_adopt:
            return False
    return True


def protected_adoption_is_identifying(worlds: Sequence[AdoptionWorld]) -> bool:
    seen: dict[tuple[Hashable, Hashable], bool] = {}
    for world in worlds:
        key = (world.candidate_visible_record, world.protected_record)
        previous = seen.setdefault(key, world.safe_to_adopt)
        if previous != world.safe_to_adopt:
            return False
    return True


@dataclass(frozen=True)
class AdvanceCase:
    case_id: str
    reachable: bool
    admissible: bool

    @property
    def scientific_advance(self) -> bool:
        return self.reachable and self.admissible


def coupled_advance_separations(cases: Sequence[AdvanceCase]) -> bool:
    has_reachable_not_admissible = any(case.reachable and not case.admissible for case in cases)
    has_admissible_not_reachable = any(case.admissible and not case.reachable for case in cases)
    has_advance = any(case.scientific_advance for case in cases)
    has_neither = any(not case.reachable and not case.admissible for case in cases)
    return all(
        (
            has_reachable_not_admissible,
            has_admissible_not_reachable,
            has_advance,
            has_neither,
        )
    )


@dataclass(frozen=True)
class EvolutionCertificate:
    issue_identity: str
    diagnosis_and_discriminator: str
    candidate_intervention: str
    isolation_record: str
    replay_record: str
    fresh_transfer_record: str
    protected_assurance_record: str
    negative_history_update: str
    external_adoption_record: str

    @property
    def valid(self) -> bool:
        return all(
            bool(value.strip())
            for value in (
                self.issue_identity,
                self.diagnosis_and_discriminator,
                self.candidate_intervention,
                self.isolation_record,
                self.replay_record,
                self.fresh_transfer_record,
                self.protected_assurance_record,
                self.negative_history_update,
                self.external_adoption_record,
            )
        )


def black_box_synthesis_verification_gap(candidate_count: int) -> tuple[int, int]:
    """Exact deterministic worst-case for a unique marked black-box candidate.

    Every deterministic search order has a final candidate.  An adversary marks
    that candidate, forcing ``candidate_count`` oracle queries.  A supplied
    candidate certificate is checked with one oracle query.
    """

    if candidate_count <= 0:
        raise ValueError("candidate_count must be positive")
    return candidate_count, 1
