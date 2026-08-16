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


@dataclass(frozen=True)
class ReopenFloor:
    """The reopen F1 a policy reaches with no diagnosis at all.

    Survivor closures are isolated while reopened chains run several long, so
    "reopen the largest closure component" scores well without reading the
    prompt, naming a responsibility, or doing anything the hypothesis is about.
    A reopen result at or below this number is graph shape, not
    dependency-directed reasoning.

    It is computed from the suite rather than quoted, so it moves when the
    cases move. A floor pasted in as a literal would silently go stale on the
    next re-freeze, which is exactly when it matters most.
    """

    expected_f1: float
    policy: str
    n_cases: int


def _f1(predicted: frozenset[str], required: frozenset[str]) -> float:
    if not predicted and not required:
        return 1.0
    true_positives = len(predicted & required)
    if not true_positives:
        return 0.0
    return 2 * true_positives / (
        2 * true_positives + len(predicted - required) + len(required - predicted)
    )


def blind_largest_component_floor(
    components_by_case: Mapping[str, Sequence[Sequence[str]]],
    required_by_case: Mapping[str, Sequence[str]],
) -> ReopenFloor:
    """Expected reopen F1 of picking the largest closure component, ties broken
    at random.

    Ties are averaged rather than resolved, because a policy that guesses cannot
    claim the best tied option — averaging is what "no diagnosis" actually
    scores.
    """

    scores: list[float] = []
    for case_id, components in components_by_case.items():
        required = frozenset(required_by_case.get(case_id, ()))
        if not components:
            continue
        largest = max(len(item) for item in components)
        tied = [frozenset(item) for item in components if len(item) == largest]
        scores.append(sum(_f1(item, required) for item in tied) / len(tied))
    expected = sum(scores) / len(scores) if scores else 0.0
    return ReopenFloor(
        expected_f1=expected,
        policy="largest_closure_component_random_tiebreak",
        n_cases=len(scores),
    )


@dataclass(frozen=True)
class SeparabilityReport:
    """Whether the label is recoverable from surface features taken together.

    Every leak check in this study so far has been univariate: one surface at a
    time, against a shuffle null. A cue that separates families only through the
    *interaction* of two surfaces — neither one carrying the signal alone —
    passes every such check. This closes that gap by classifying in the joint
    space.

    The prompt-length leak that survived two audits is the cautionary case: it
    was invisible to a best-single-threshold detector because the ordering was
    non-monotonic. An interaction leak is the same failure one dimension up.
    """

    accuracy: float
    majority_baseline: float
    p_value: float
    n_cases: int

    @property
    def leaks(self) -> bool:
        return self.p_value < 0.05 and self.accuracy > self.majority_baseline


def _loo_nearest_neighbour_accuracy(points: Sequence[Sequence[float]], labels: Sequence[str]) -> float:
    total = len(points)
    if total < 2:
        return 0.0
    dimensions = len(points[0])
    correct = 0
    for index in range(total):
        best: float | None = None
        nearest = 0
        for other in range(total):
            if other == index:
                continue
            distance = sum(
                (points[index][axis] - points[other][axis]) ** 2 for axis in range(dimensions)
            )
            if best is None or distance < best:
                best, nearest = distance, other
        if labels[nearest] == labels[index]:
            correct += 1
    return correct / total


def assess_joint_surface_separability(
    features_by_case: Mapping[str, Sequence[float]],
    labels_by_case: Mapping[str, str],
    *,
    resamples: int = 400,
    seed: int = 20260816,
) -> SeparabilityReport:
    """Can a nearest-neighbour rule recover the family from surfaces jointly?

    Features are z-scored so no surface dominates the metric by its units, and
    the null is a label shuffle over the same points, so the comparison holds
    the geometry fixed and varies only the labelling.
    """

    import random
    import statistics

    case_ids = sorted(features_by_case)
    if len(case_ids) < 2:
        return SeparabilityReport(0.0, 0.0, 1.0, len(case_ids))
    raw = [list(map(float, features_by_case[case_id])) for case_id in case_ids]
    labels = [labels_by_case[case_id] for case_id in case_ids]
    columns = list(zip(*raw))
    means = [statistics.mean(column) for column in columns]
    deviations = [statistics.pstdev(column) or 1.0 for column in columns]
    points = [
        [(value - means[axis]) / deviations[axis] for axis, value in enumerate(row)] for row in raw
    ]

    observed = _loo_nearest_neighbour_accuracy(points, labels)
    baseline = max(labels.count(item) for item in set(labels)) / len(labels)
    rng = random.Random(seed)
    hits = 0
    for _ in range(resamples):
        shuffled = labels[:]
        rng.shuffle(shuffled)
        if _loo_nearest_neighbour_accuracy(points, shuffled) >= observed:
            hits += 1
    return SeparabilityReport(
        accuracy=observed,
        majority_baseline=baseline,
        p_value=(hits + 1) / (resamples + 1),
        n_cases=len(case_ids),
    )


__all__ = [
    "ArmReport",
    "ArmVerdict",
    "ReopenFloor",
    "SeparabilityReport",
    "assess_joint_surface_separability",
    "assess_arm_discrimination",
    "assess_pair_discrimination",
    "blind_largest_component_floor",
]
