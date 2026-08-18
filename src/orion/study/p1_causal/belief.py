"""Responsibility belief state with explicit UNRESOLVED.

A mutating authority class may not be constructed without naming the
intervention that licensed it. Probes never appear in ``intervention_ids``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.kernel.store import canonical_bytes


class AuthorityClass(str, Enum):
    EVIDENCE = "EVIDENCE"
    EXECUTION = "EXECUTION"
    FORMULATION = "FORMULATION"
    SEARCH_UNIVERSE = "SEARCH_UNIVERSE"
    UNRESOLVED = "UNRESOLVED"


MUTATION_BEARING: frozenset[AuthorityClass] = frozenset(
    {AuthorityClass.FORMULATION, AuthorityClass.SEARCH_UNIVERSE}
)

ALL_AUTHORITY_CLASSES: tuple[AuthorityClass, ...] = tuple(AuthorityClass)


class UnauthorizedBeliefMutation(RuntimeError):
    """Raised when a caller tries to mint authority without an intervention."""


@dataclass(frozen=True)
class SupportRecord:
    class_id: AuthorityClass
    mass: float
    support_ids: tuple[str, ...]
    defeater_ids: tuple[str, ...] = ()

    def to_payload(self) -> dict:
        return {
            "class_id": self.class_id.value,
            "mass": round(self.mass + 0.0, 6),
            "support_ids": list(self.support_ids),
            "defeater_ids": list(self.defeater_ids),
        }


@dataclass(frozen=True)
class BeliefState:
    """Competing responsibilities plus what, if anything, may be done next."""

    supports: tuple[SupportRecord, ...]
    evidence_ids: tuple[str, ...]
    probe_ids: tuple[str, ...] = ()
    intervention_ids: tuple[str, ...] = ()
    intervention_backed: bool = False
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        names = tuple(item.class_id for item in self.supports)
        if set(names) != set(ALL_AUTHORITY_CLASSES) or len(names) != len(
            ALL_AUTHORITY_CLASSES
        ):
            raise UnauthorizedBeliefMutation(
                "belief state must be total over EVIDENCE/EXECUTION/FORMULATION/"
                "SEARCH_UNIVERSE/UNRESOLVED"
            )
        if (
            self.authority_class is AuthorityClass.UNRESOLVED
            and self.intervention_backed
        ):
            raise UnauthorizedBeliefMutation(
                "UNRESOLVED cannot be intervention-backed"
            )
        # Identification (unique argmax) is not authority. Mutating licenses are
        # refused in licensing.request_action unless intervention_backed.

    @property
    def ranked(self) -> tuple[SupportRecord, ...]:
        return tuple(
            sorted(
                self.supports,
                key=lambda item: (-item.mass, item.class_id.value),
            )
        )

    @property
    def authority_class(self) -> AuthorityClass:
        ranked = self.ranked
        top = ranked[0]
        runner = ranked[1]
        if top.class_id is AuthorityClass.UNRESOLVED:
            return AuthorityClass.UNRESOLVED
        if top.mass <= 0.5 or top.mass <= runner.mass:
            return AuthorityClass.UNRESOLVED
        return top.class_id

    @property
    def diagnosable(self) -> bool:
        return self.authority_class is not AuthorityClass.UNRESOLVED

    def mass(self, class_id: AuthorityClass) -> float:
        for item in self.supports:
            if item.class_id is class_id:
                return item.mass
        return 0.0

    def to_payload(self) -> dict:
        return {
            "authority_class": self.authority_class.value,
            "diagnosable": self.diagnosable,
            "intervention_backed": self.intervention_backed,
            "evidence_ids": list(self.evidence_ids),
            "probe_ids": list(self.probe_ids),
            "intervention_ids": list(self.intervention_ids),
            "supports": [item.to_payload() for item in self.supports],
            "notes": list(self.notes),
            "payload_sha256": _payload_digest(
                [item.to_payload() for item in self.supports]
            ),
        }


def _payload_digest(payload: object) -> str:
    import hashlib

    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def uniform_unresolved(*, evidence_ids: tuple[str, ...] = ()) -> BeliefState:
    share = 1.0 / float(len(ALL_AUTHORITY_CLASSES))
    supports = tuple(
        SupportRecord(class_id=item, mass=share, support_ids=())
        for item in ALL_AUTHORITY_CLASSES
    )
    return BeliefState(supports=supports, evidence_ids=evidence_ids)


def replace_masses(
    state: BeliefState,
    masses: dict[AuthorityClass, float],
    *,
    evidence_ids: tuple[str, ...] | None = None,
    probe_ids: tuple[str, ...] | None = None,
    intervention_ids: tuple[str, ...] | None = None,
    intervention_backed: bool | None = None,
    notes: tuple[str, ...] | None = None,
    support_ids: dict[AuthorityClass, tuple[str, ...]] | None = None,
) -> BeliefState:
    """The only admitted transition constructor besides ``uniform_unresolved``."""

    total = sum(masses[item] for item in ALL_AUTHORITY_CLASSES)
    if total <= 0.0:
        raise UnauthorizedBeliefMutation("masses must be positive")
    records = []
    for item in ALL_AUTHORITY_CLASSES:
        extra = () if support_ids is None else support_ids.get(item, ())
        records.append(
            SupportRecord(
                class_id=item,
                mass=masses[item] / total,
                support_ids=extra,
            )
        )
    return BeliefState(
        supports=tuple(records),
        evidence_ids=state.evidence_ids if evidence_ids is None else evidence_ids,
        probe_ids=state.probe_ids if probe_ids is None else probe_ids,
        intervention_ids=(
            state.intervention_ids if intervention_ids is None else intervention_ids
        ),
        intervention_backed=(
            state.intervention_backed
            if intervention_backed is None
            else intervention_backed
        ),
        notes=state.notes if notes is None else notes,
    )
