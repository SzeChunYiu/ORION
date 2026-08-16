from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum


class ArmVerdict(str, Enum):
    """Whether an evaluation arm could tell the compared systems apart at all.

    This is the degeneracy question one level up from the panel probe. The panel
    probe asks whether a blind responder can beat the baseline — is the *suite*
    measuring anything. This asks whether any system differed from any other —
    did the *arm* measure anything. Both must pass before a comparison between
    systems carries meaning.
    """

    DISCRIMINATED = "DISCRIMINATED"
    DID_NOT_DISCRIMINATE = "DID_NOT_DISCRIMINATE"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ArmReport:
    verdict: ArmVerdict
    distinct_behaviour_groups: int
    systems_compared: int
    reasons: tuple[str, ...] = ()
    largest_group: tuple[str, ...] = ()

    @property
    def permits_system_comparison(self) -> bool:
        return self.verdict is ArmVerdict.DISCRIMINATED


def assess_arm_discrimination(
    outcomes_by_system: Mapping[str, Sequence[object]],
    *,
    minimum_systems: int = 2,
) -> ArmReport:
    """Did this arm distinguish the systems, or did they all behave identically?

    A comparison between systems that produced byte-identical outcome vectors
    reports a difference of exactly zero. Read as a rate difference that is a
    finding — "the subject is no better than the comparator". It is not. It is
    the signature of an instrument that could not read the cases, and the honest
    verdict is CANNOT_CHECK.

    The observed case: on the frozen P1 suite every mechanical system scored
    5/90, ORION reframed 0 times out of 90, and H1 came back NOT_SUPPORTED with
    an interval of exactly [0.0000, 0.0000]. Nothing in the statistics could
    distinguish that from a real null, because a paired bootstrap over identical
    vectors is identically zero by construction.
    """

    systems = sorted(outcomes_by_system)
    if len(systems) < minimum_systems:
        return ArmReport(
            ArmVerdict.CANNOT_CHECK,
            distinct_behaviour_groups=len(systems),
            systems_compared=len(systems),
            reasons=(f"fewer than {minimum_systems} systems to compare",),
        )

    groups: dict[tuple, list[str]] = {}
    for system in systems:
        key = tuple(str(item) for item in outcomes_by_system[system])
        groups.setdefault(key, []).append(system)

    if not any(groups):
        return ArmReport(
            ArmVerdict.CANNOT_CHECK,
            distinct_behaviour_groups=0,
            systems_compared=len(systems),
            reasons=("no outcomes recorded for any system",),
        )

    largest = max(groups.values(), key=len)
    if len(groups) < 2:
        return ArmReport(
            ArmVerdict.DID_NOT_DISCRIMINATE,
            distinct_behaviour_groups=1,
            systems_compared=len(systems),
            reasons=(
                "every system produced an identical outcome vector; any difference "
                "between them is zero by construction, not by measurement",
            ),
            largest_group=tuple(largest),
        )

    return ArmReport(
        ArmVerdict.DISCRIMINATED,
        distinct_behaviour_groups=len(groups),
        systems_compared=len(systems),
        largest_group=tuple(largest),
    )


def assess_pair_discrimination(
    subject_outcomes: Sequence[object],
    comparator_outcomes: Sequence[object],
    *,
    subject_id: str = "subject",
    comparator_id: str = "comparator",
) -> ArmReport:
    """The pairwise form: can this specific comparison say anything?

    A hypothesis verdict rests on one pair, so the pair is what must be checked.
    Two systems that never differ on any unit cannot support SUPPORTED or
    NOT_SUPPORTED — only CANNOT_CHECK.
    """

    if len(subject_outcomes) != len(comparator_outcomes):
        return ArmReport(
            ArmVerdict.CANNOT_CHECK,
            distinct_behaviour_groups=0,
            systems_compared=2,
            reasons=("the paired outcome vectors have different lengths",),
        )
    return assess_arm_discrimination(
        {subject_id: subject_outcomes, comparator_id: comparator_outcomes}
    )


__all__ = [
    "ArmReport",
    "ArmVerdict",
    "assess_arm_discrimination",
    "assess_pair_discrimination",
]
