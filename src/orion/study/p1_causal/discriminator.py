"""Active discriminator: cheapest allowed probe expected to separate the top pair.

A probe never grants authority. It only names which observation to buy next.
"""

from __future__ import annotations

from dataclasses import dataclass

from .belief import ALL_AUTHORITY_CLASSES, AuthorityClass, BeliefState


@dataclass(frozen=True)
class ProbeSpec:
    probe_id: str
    cost: int
    separates: tuple[AuthorityClass, ...]
    description: str = ""

    def __post_init__(self) -> None:
        if self.cost < 1:
            raise ValueError(f"{self.probe_id}: cost must be at least 1")
        if not self.probe_id.strip():
            raise ValueError("probe_id is required")

    @property
    def blind(self) -> bool:
        return len(self.separates) < 2

    def to_payload(self) -> dict:
        return {
            "probe_id": self.probe_id,
            "cost": self.cost,
            "separates": [item.value for item in self.separates],
            "blind": self.blind,
            "description": self.description,
        }


@dataclass(frozen=True)
class ProbeChoice:
    probe: ProbeSpec | None
    reason: str
    top_pair: tuple[AuthorityClass, AuthorityClass] | None

    def to_payload(self) -> dict:
        return {
            "probe_id": self.probe.probe_id if self.probe else "",
            "reason": self.reason,
            "top_pair": (
                [item.value for item in self.top_pair] if self.top_pair else []
            ),
        }


@dataclass(frozen=True)
class ProbeCatalog:
    probes: tuple[ProbeSpec, ...]

    def by_id(self, probe_id: str) -> ProbeSpec:
        for probe in self.probes:
            if probe.probe_id == probe_id:
                return probe
        raise KeyError(probe_id)


DEFAULT_PROBES: tuple[ProbeSpec, ...] = (
    ProbeSpec(
        probe_id="blind_control",
        cost=1,
        separates=(),
        description="reaches nothing; negative control",
    ),
    ProbeSpec(
        probe_id="omitted_source_retrieval",
        cost=1,
        separates=(AuthorityClass.EVIDENCE, AuthorityClass.SEARCH_UNIVERSE),
        description="is the missing source obtainable inside the current universe",
    ),
    ProbeSpec(
        probe_id="environment_sanity",
        cost=1,
        separates=(AuthorityClass.EXECUTION, AuthorityClass.FORMULATION),
        description="does the phenomenon survive a corrected environment",
    ),
    ProbeSpec(
        probe_id="representation_transform",
        cost=2,
        separates=(AuthorityClass.FORMULATION, AuthorityClass.SEARCH_UNIVERSE),
        description="does a coordinate change remove the residual",
    ),
    ProbeSpec(
        probe_id="measurement_definition_lookup",
        cost=1,
        separates=(AuthorityClass.EVIDENCE, AuthorityClass.FORMULATION),
        description="is the quantity defined as the question requires",
    ),
)


def top_competing_pair(
    state: BeliefState,
) -> tuple[AuthorityClass, AuthorityClass] | None:
    ranked = [
        item
        for item in state.ranked
        if item.class_id is not AuthorityClass.UNRESOLVED
    ]
    if len(ranked) < 2:
        return None
    return ranked[0].class_id, ranked[1].class_id


def select_discriminator(
    state: BeliefState,
    catalog: ProbeCatalog | None = None,
    *,
    used: frozenset[str] = frozenset(),
) -> ProbeChoice:
    """Pick the cheapest unused probe that separates the current top pair.

    If the state is already unique-argmax and intervention-backed, no probe is
    selected. A blind probe is never chosen except when the catalog contains
    nothing else (hostile control).
    """

    probes = (catalog or ProbeCatalog(DEFAULT_PROBES)).probes
    if state.diagnosable and state.intervention_backed:
        return ProbeChoice(None, "already_intervention_backed", None)
    pair = top_competing_pair(state)
    if pair is None:
        return ProbeChoice(None, "no_competing_pair", None)
    left, right = pair
    eligible = [
        probe
        for probe in probes
        if probe.probe_id not in used
        and not probe.blind
        and left in probe.separates
        and right in probe.separates
    ]
    if not eligible:
        eligible = [
            probe
            for probe in probes
            if probe.probe_id not in used
            and not probe.blind
            and (left in probe.separates or right in probe.separates)
        ]
    if not eligible:
        return ProbeChoice(None, "no_separating_probe", pair)
    best = sorted(eligible, key=lambda item: (item.cost, item.probe_id))[0]
    return ProbeChoice(best, "cheapest_separator_of_top_pair", pair)


# Silence unused import if a caller wants the full class list for totality tests.
_ = ALL_AUTHORITY_CLASSES
