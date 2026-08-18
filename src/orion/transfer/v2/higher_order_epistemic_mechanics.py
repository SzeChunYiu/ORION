"""Bounded higher-order epistemic mechanics for the P6 successor programme.

This module intentionally does *not* freeze a universal taxonomy of scientific
revision.  It supplies the smaller formal substrate needed to test one claim:
candidate epistemic changes have typed footprints and obligations, and a system
must not silently promote a broader change when a strictly narrower admissible
(or still unresolved) alternative exists for the same declared claim.

The objects here are non-authorizing.  They do not grant scientific authority,
Self-ORION adoption, novelty, or paper readiness.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest


class ObligationState(str, Enum):
    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    UNRESOLVED = "UNRESOLVED"


class AssessmentStatus(str, Enum):
    ADMISSIBLE = "ADMISSIBLE"
    BLOCKED = "BLOCKED"
    UNRESOLVED = "UNRESOLVED"


class SelectionStatus(str, Enum):
    UNIQUE_MINIMUM = "UNIQUE_MINIMUM"
    MULTIPLE_MINIMA = "MULTIPLE_MINIMA"
    NO_ADMISSIBLE = "NO_ADMISSIBLE"
    UNRESOLVED = "UNRESOLVED"


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


@dataclass(frozen=True)
class HigherOrderEpistemicMechanic:
    """Claim-relative material transition contract.

    ``kind`` is descriptive only.  No behavior, authority, or ordering is
    inferred from it.  The formal comparison uses declared write footprints,
    preservation obligations, and required authority domains.
    """

    mechanic_id: str
    claim_id: str
    kind: str
    read_coordinates: tuple[str, ...]
    write_coordinates: tuple[str, ...]
    preconditions: tuple[str, ...]
    hard_requirements: tuple[str, ...]
    preservation_obligations: tuple[str, ...]
    required_authorities: tuple[str, ...]
    cost: float
    can_self_authorize: bool
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "HigherOrderEpistemicMechanic.v1",
            "mechanic_id": self.mechanic_id,
            "claim_id": self.claim_id,
            "kind": self.kind,
            "read_coordinates": list(self.read_coordinates),
            "write_coordinates": list(self.write_coordinates),
            "preconditions": list(self.preconditions),
            "hard_requirements": list(self.hard_requirements),
            "preservation_obligations": list(self.preservation_obligations),
            "required_authorities": list(self.required_authorities),
            "cost": self.cost,
            "can_self_authorize": self.can_self_authorize,
            "authority_scope": "NON_AUTHORIZING_FORMAL_CONTRACT_ONLY",
        }

    def verify(self) -> None:
        if not self.mechanic_id or not self.claim_id:
            raise ValueError("mechanic and claim identities are required")
        if self.cost < 0:
            raise ValueError("mechanic cost must be non-negative")
        if self.can_self_authorize:
            raise ValueError("higher-order mechanic cannot self-authorize")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("higher-order mechanic digest mismatch")


def build_mechanic(
    *,
    mechanic_id: str,
    claim_id: str,
    kind: str = "GENERIC",
    read_coordinates: Sequence[str] = (),
    write_coordinates: Sequence[str] = (),
    preconditions: Sequence[str] = (),
    hard_requirements: Sequence[str] = (),
    preservation_obligations: Sequence[str] = (),
    required_authorities: Sequence[str] = (),
    cost: float = 0.0,
) -> HigherOrderEpistemicMechanic:
    payload = {
        "version": "HigherOrderEpistemicMechanic.v1",
        "mechanic_id": str(mechanic_id),
        "claim_id": str(claim_id),
        "kind": str(kind),
        "read_coordinates": list(_sorted_unique(read_coordinates)),
        "write_coordinates": list(_sorted_unique(write_coordinates)),
        "preconditions": list(_sorted_unique(preconditions)),
        "hard_requirements": list(_sorted_unique(hard_requirements)),
        "preservation_obligations": list(
            _sorted_unique(preservation_obligations)
        ),
        "required_authorities": list(_sorted_unique(required_authorities)),
        "cost": float(cost),
        "can_self_authorize": False,
        "authority_scope": "NON_AUTHORIZING_FORMAL_CONTRACT_ONLY",
    }
    mechanic = HigherOrderEpistemicMechanic(
        mechanic_id=payload["mechanic_id"],
        claim_id=payload["claim_id"],
        kind=payload["kind"],
        read_coordinates=tuple(payload["read_coordinates"]),
        write_coordinates=tuple(payload["write_coordinates"]),
        preconditions=tuple(payload["preconditions"]),
        hard_requirements=tuple(payload["hard_requirements"]),
        preservation_obligations=tuple(payload["preservation_obligations"]),
        required_authorities=tuple(payload["required_authorities"]),
        cost=payload["cost"],
        can_self_authorize=False,
        digest=content_digest(payload),
    )
    mechanic.verify()
    return mechanic


@dataclass(frozen=True)
class MechanicAssessment:
    mechanic_digest: str
    status: AssessmentStatus
    reasons: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "HigherOrderMechanicAssessment.v1",
            "mechanic_digest": self.mechanic_digest,
            "status": self.status.value,
            "reasons": list(self.reasons),
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("mechanic assessment digest mismatch")


def assess_mechanic(
    mechanic: HigherOrderEpistemicMechanic,
    *,
    obligation_states: Mapping[str, ObligationState],
    granted_authorities: Sequence[str] = (),
    forbidden_writes: Sequence[str] = (),
) -> MechanicAssessment:
    """Fail-closed assessment of one proposed mechanic.

    Any known violated hard condition or forbidden material write blocks.  Missing
    or explicitly unresolved obligation evidence remains unresolved.  Authority
    is non-compensatory: its absence blocks regardless of cost or other evidence.
    """

    mechanic.verify()
    blocked: list[str] = []
    unresolved: list[str] = []

    required_obligations = _sorted_unique(
        (*mechanic.preconditions, *mechanic.hard_requirements)
    )
    for name in required_obligations:
        state = obligation_states.get(name)
        if state is None:
            unresolved.append(f"OBLIGATION_STATE_MISSING:{name}")
        elif state is ObligationState.VIOLATED:
            blocked.append(f"OBLIGATION_VIOLATED:{name}")
        elif state is ObligationState.UNRESOLVED:
            unresolved.append(f"OBLIGATION_UNRESOLVED:{name}")
        elif state is not ObligationState.SATISFIED:
            raise ValueError(f"invalid obligation state for {name!r}: {state!r}")

    granted = set(map(str, granted_authorities))
    for authority in mechanic.required_authorities:
        if authority not in granted:
            blocked.append(f"AUTHORITY_MISSING:{authority}")

    forbidden = set(map(str, forbidden_writes))
    for coordinate in sorted(set(mechanic.write_coordinates) & forbidden):
        blocked.append(f"FORBIDDEN_WRITE:{coordinate}")

    if blocked:
        status = AssessmentStatus.BLOCKED
        reasons = tuple(sorted(set(blocked + unresolved)))
    elif unresolved:
        status = AssessmentStatus.UNRESOLVED
        reasons = tuple(sorted(set(unresolved)))
    else:
        status = AssessmentStatus.ADMISSIBLE
        reasons = ()

    payload = {
        "version": "HigherOrderMechanicAssessment.v1",
        "mechanic_digest": mechanic.digest,
        "status": status.value,
        "reasons": list(reasons),
        "grants_scientific_authority": False,
    }
    receipt = MechanicAssessment(
        mechanic_digest=mechanic.digest,
        status=status,
        reasons=reasons,
        digest=content_digest(payload),
    )
    receipt.verify()
    return receipt


def less_or_equal_invasiveness(
    left: HigherOrderEpistemicMechanic,
    right: HigherOrderEpistemicMechanic,
) -> bool:
    """Necessary claim-relative preorder used by tranche 1.

    ``left <= right`` only when both address the same declared claim, left writes
    no additional material coordinates, preserves at least the obligations right
    preserves, and requires no additional authority domain.

    This is intentionally a bounded design relation, not a universal ordering of
    scientific revisions.  #463 may replace it with semantic witnesses.
    """

    left.verify()
    right.verify()
    if left.claim_id != right.claim_id:
        return False
    return (
        set(left.write_coordinates) <= set(right.write_coordinates)
        and set(left.preservation_obligations)
        >= set(right.preservation_obligations)
        and set(left.required_authorities) <= set(right.required_authorities)
    )


def strictly_less_invasive(
    left: HigherOrderEpistemicMechanic,
    right: HigherOrderEpistemicMechanic,
) -> bool:
    if not less_or_equal_invasiveness(left, right):
        return False
    return (
        set(left.write_coordinates) < set(right.write_coordinates)
        or set(left.preservation_obligations)
        > set(right.preservation_obligations)
        or set(left.required_authorities) < set(right.required_authorities)
    )


@dataclass(frozen=True)
class MinimalRevisionSelection:
    claim_id: str
    status: SelectionStatus
    selected_mechanic_digest: str | None
    minimal_mechanic_digests: tuple[str, ...]
    reasons: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "MinimalRevisionSelection.v1",
            "claim_id": self.claim_id,
            "status": self.status.value,
            "selected_mechanic_digest": self.selected_mechanic_digest,
            "minimal_mechanic_digests": list(self.minimal_mechanic_digests),
            "reasons": list(self.reasons),
            "grants_adoption_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("minimal revision selection digest mismatch")
        if self.status is not SelectionStatus.UNIQUE_MINIMUM:
            if self.selected_mechanic_digest is not None:
                raise ValueError("non-unique selection cannot select a mechanic")


def _selection_receipt(
    *,
    claim_id: str,
    status: SelectionStatus,
    selected: str | None,
    minima: Sequence[str],
    reasons: Sequence[str] = (),
) -> MinimalRevisionSelection:
    minimal = tuple(sorted(set(map(str, minima))))
    reason_tuple = tuple(sorted(set(map(str, reasons))))
    payload = {
        "version": "MinimalRevisionSelection.v1",
        "claim_id": claim_id,
        "status": status.value,
        "selected_mechanic_digest": selected,
        "minimal_mechanic_digests": list(minimal),
        "reasons": list(reason_tuple),
        "grants_adoption_authority": False,
    }
    receipt = MinimalRevisionSelection(
        claim_id=claim_id,
        status=status,
        selected_mechanic_digest=selected,
        minimal_mechanic_digests=minimal,
        reasons=reason_tuple,
        digest=content_digest(payload),
    )
    receipt.verify()
    return receipt


def select_minimal_admissible(
    mechanics: Sequence[HigherOrderEpistemicMechanic],
    assessments: Sequence[MechanicAssessment],
) -> MinimalRevisionSelection:
    """Return the minimal admissible revision set without arbitrary escalation."""

    if not mechanics:
        raise ValueError("at least one candidate mechanic is required")
    for mechanic in mechanics:
        mechanic.verify()

    claim_ids = {mechanic.claim_id for mechanic in mechanics}
    if len(claim_ids) != 1:
        raise ValueError("minimal selection is claim-relative")
    claim_id = next(iter(claim_ids))

    by_digest: dict[str, MechanicAssessment] = {}
    for assessment in assessments:
        assessment.verify()
        if assessment.mechanic_digest in by_digest:
            raise ValueError("duplicate mechanic assessment")
        by_digest[assessment.mechanic_digest] = assessment

    mechanic_digests = {mechanic.digest for mechanic in mechanics}
    if set(by_digest) != mechanic_digests:
        raise ValueError("assessment set must match candidate mechanic set exactly")

    admissible = [
        mechanic
        for mechanic in mechanics
        if by_digest[mechanic.digest].status is AssessmentStatus.ADMISSIBLE
    ]
    unresolved = [
        mechanic
        for mechanic in mechanics
        if by_digest[mechanic.digest].status is AssessmentStatus.UNRESOLVED
    ]

    if not admissible:
        if unresolved:
            return _selection_receipt(
                claim_id=claim_id,
                status=SelectionStatus.UNRESOLVED,
                selected=None,
                minima=(),
                reasons=("NO_ADMISSIBLE_WITH_UNRESOLVED_CANDIDATES",),
            )
        return _selection_receipt(
            claim_id=claim_id,
            status=SelectionStatus.NO_ADMISSIBLE,
            selected=None,
            minima=(),
            reasons=("ALL_CANDIDATES_BLOCKED",),
        )

    minima = []
    for candidate in admissible:
        if any(
            other.digest != candidate.digest
            and strictly_less_invasive(other, candidate)
            for other in admissible
        ):
            continue
        minima.append(candidate)

    if any(
        strictly_less_invasive(unresolved_candidate, minimum)
        for unresolved_candidate in unresolved
        for minimum in minima
    ):
        return _selection_receipt(
            claim_id=claim_id,
            status=SelectionStatus.UNRESOLVED,
            selected=None,
            minima=[mechanic.digest for mechanic in minima],
            reasons=("NARROWER_UNRESOLVED_CANDIDATE",),
        )

    minimal_digests = tuple(sorted(mechanic.digest for mechanic in minima))
    if len(minimal_digests) == 1:
        return _selection_receipt(
            claim_id=claim_id,
            status=SelectionStatus.UNIQUE_MINIMUM,
            selected=minimal_digests[0],
            minima=minimal_digests,
        )

    return _selection_receipt(
        claim_id=claim_id,
        status=SelectionStatus.MULTIPLE_MINIMA,
        selected=None,
        minima=minimal_digests,
        reasons=("INCOMPARABLE_MINIMAL_REVISIONS",),
    )
