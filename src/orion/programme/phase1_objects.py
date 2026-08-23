"""Minimal, fail-closed Phase 1 objects for the P9/P10 bridge.

These are transport records, not learned models or authority.  Each record keeps
its owning phase explicit so later consumers cannot silently re-own a contract.
The objects intentionally contain no empirical claim or equivalence rule.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class CheckStatus(StrEnum):
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class CandidateDisposition(StrEnum):
    PROPOSED = "PROPOSED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


def _required(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must be non-empty")


def _owner(value: str, expected: str) -> None:
    _required(value, "owner")
    if value != expected:
        raise ValueError(f"{expected} is the sole owner of this object")


@dataclass(frozen=True)
class MethodRealization:
    object_id: str
    method_id: str
    assumptions: tuple[str, ...]
    effects: tuple[str, ...]
    failures: tuple[str, ...]
    lineage: tuple[str, ...]
    owner: str = "P1"
    schema_version: str = "MethodRealization.v1"

    def __post_init__(self) -> None:
        _required(self.object_id, "object_id")
        _required(self.method_id, "method_id")
        _owner(self.owner, "P1")
        if not self.assumptions or not self.effects or not self.failures:
            raise ValueError("assumptions, effects, and failures are required")
        if not self.lineage:
            raise ValueError("lineage is required; provenance cannot be erased")


@dataclass(frozen=True)
class MethodStructureProjection:
    object_id: str
    realization_id: str
    source_id: str
    semantics: Mapping[str, str]
    owner: str = "P3"
    schema_version: str = "MethodStructureProjection.v1"

    def __post_init__(self) -> None:
        for value, name in ((self.object_id, "object_id"), (self.realization_id, "realization_id"), (self.source_id, "source_id")):
            _required(value, name)
        _owner(self.owner, "P3")
        if not self.semantics:
            raise ValueError("source-local semantics are required")


@dataclass(frozen=True)
class StructuralSignature:
    object_id: str
    reduction_id: str
    coordinates: Mapping[str, str]
    owner: str = "P6"
    schema_version: str = "StructuralSignature.v1"

    def __post_init__(self) -> None:
        _required(self.object_id, "object_id")
        _required(self.reduction_id, "reduction_id")
        _owner(self.owner, "P6")
        if not self.coordinates:
            raise ValueError("claim-relative coordinates are required")


@dataclass(frozen=True)
class MethodFibre:
    object_id: str
    signature_id: str
    realization_ids: tuple[str, ...]
    reduction_id: str
    owner: str = "P6"
    schema_version: str = "MethodFibre.v1"

    def __post_init__(self) -> None:
        for value, name in ((self.object_id, "object_id"), (self.signature_id, "signature_id"), (self.reduction_id, "reduction_id")):
            _required(value, name)
        _owner(self.owner, "P6")
        if not self.realization_ids:
            raise ValueError("a fibre requires at least one realization")


@dataclass(frozen=True)
class StructuralDiscoveryRoute:
    object_id: str
    source_structure_id: str
    route_steps: tuple[str, ...]
    owner: str = "P2"
    schema_version: str = "StructuralDiscoveryRoute.v1"

    def __post_init__(self) -> None:
        _required(self.object_id, "object_id")
        _required(self.source_structure_id, "source_structure_id")
        _owner(self.owner, "P2")
        if not self.route_steps:
            raise ValueError("route_steps are required")


@dataclass(frozen=True)
class MethodChart:
    object_id: str
    signature_ids: tuple[str, ...]
    mappings: Mapping[str, str]
    owner: str = "P7"
    schema_version: str = "MethodChart.v1"

    def __post_init__(self) -> None:
        _required(self.object_id, "object_id")
        _owner(self.owner, "P7")
        if not self.signature_ids or not self.mappings:
            raise ValueError("a chart requires signatures and mappings")


@dataclass(frozen=True)
class MethodTransferReceipt:
    object_id: str
    donor_id: str
    target_id: str
    adaptation: str
    verification: CheckStatus
    novelty: CheckStatus
    owner: str = "P4"
    schema_version: str = "MethodTransferReceipt.v1"

    def __post_init__(self) -> None:
        for value, name in ((self.object_id, "object_id"), (self.donor_id, "donor_id"), (self.target_id, "target_id"), (self.adaptation, "adaptation")):
            _required(value, name)
        _owner(self.owner, "P4")


@dataclass(frozen=True)
class MethodChallenger:
    object_id: str
    failure_id: str
    replay_id: str
    fresh_transfer_id: str
    disposition: CandidateDisposition
    owner: str = "P5"
    schema_version: str = "MethodChallenger.v1"

    def __post_init__(self) -> None:
        for value, name in ((self.object_id, "object_id"), (self.failure_id, "failure_id"), (self.replay_id, "replay_id"), (self.fresh_transfer_id, "fresh_transfer_id")):
            _required(value, name)
        _owner(self.owner, "P5")


@dataclass(frozen=True)
class MethodAuthorityRecord:
    object_id: str
    validity: CheckStatus
    applicability: CheckStatus
    transfer: CheckStatus
    novelty: CheckStatus
    utility: CheckStatus
    adoption: CheckStatus = CheckStatus.UNKNOWN
    owner: str = "P8"
    schema_version: str = "MethodAuthorityRecord.v1"

    def __post_init__(self) -> None:
        _required(self.object_id, "object_id")
        _owner(self.owner, "P8")
        if any(status is CheckStatus.UNKNOWN for status in (self.validity, self.applicability, self.transfer, self.novelty, self.utility, self.adoption)) and self.adoption is not CheckStatus.UNKNOWN:
            raise ValueError("UNKNOWN evidence cannot be laundered into adoption authority")


@dataclass(frozen=True)
class StructuralEpisode:
    object_id: str
    structure_ids: tuple[str, ...]
    split: str
    outcome: CheckStatus
    owner: str = "P9"
    schema_version: str = "StructuralEpisode.v1"

    def __post_init__(self) -> None:
        _required(self.object_id, "object_id")
        _required(self.split, "split")
        _owner(self.owner, "P9")
        if not self.structure_ids:
            raise ValueError("an episode requires structural inputs")

    @property
    def scoreable(self) -> bool:
        return self.outcome is not CheckStatus.UNKNOWN


@dataclass(frozen=True)
class BreakthroughEpisode:
    object_id: str
    pre_state_id: str
    method_space_edit: str
    post_state_id: str
    cutoff: str
    owner: str = "P10"
    schema_version: str = "BreakthroughEpisode.v1"

    def __post_init__(self) -> None:
        for value, name in ((self.object_id, "object_id"), (self.pre_state_id, "pre_state_id"), (self.method_space_edit, "method_space_edit"), (self.post_state_id, "post_state_id"), (self.cutoff, "cutoff")):
            _required(value, name)
        _owner(self.owner, "P10")


@dataclass(frozen=True)
class InventedMethodCandidate:
    object_id: str
    episode_id: str
    proposed_edit: str
    disposition: CandidateDisposition = CandidateDisposition.PROPOSED
    owner: str = "P10"
    schema_version: str = "InventedMethodCandidate.v1"
    authority_granted: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        for value, name in ((self.object_id, "object_id"), (self.episode_id, "episode_id"), (self.proposed_edit, "proposed_edit")):
            _required(value, name)
        _owner(self.owner, "P10")
        if self.authority_granted:
            raise ValueError("invented candidates are non-authoritative")


__all__ = [
    "BreakthroughEpisode", "CandidateDisposition", "CheckStatus", "InventedMethodCandidate",
    "MethodAuthorityRecord", "MethodChart", "MethodChallenger", "MethodFibre",
    "MethodRealization", "MethodStructureProjection", "MethodTransferReceipt",
    "StructuralDiscoveryRoute", "StructuralEpisode", "StructuralSignature",
]
