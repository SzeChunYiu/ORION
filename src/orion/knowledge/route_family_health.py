"""Longitudinal route-family health diagnostics reconstructed from RAKL.

Provenance: SzeChunYiu/RAKL@70f5f7c4a6771ffd1158765b42ac9f8aee8a270f
``src/rakl/route_family_health.py`` and its frozen tests.

This is search-control telemetry only.  It cannot emit a scientific truth
verdict, recommend abandonment, or grant scientific authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Protocol, Tuple


class RouteHealthState(str, Enum):
    PROGRESSIVE_SIGNAL = "PROGRESSIVE_SIGNAL"
    LOCALLY_PROGRESSIVE_ROOT_STALLED = "LOCALLY_PROGRESSIVE_ROOT_STALLED"
    STAGNANT_SIGNAL = "STAGNANT_SIGNAL"
    PATCH_ACCUMULATION_SIGNAL = "PATCH_ACCUMULATION_SIGNAL"
    RESTRUCTURING_SIGNAL = "RESTRUCTURING_SIGNAL"
    EXTERNALLY_BLOCKED = "EXTERNALLY_BLOCKED"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    CANNOT_CHECK = "CANNOT_CHECK"


class RouteHealthFailureMode(str, Enum):
    FAILURE_COUNT_AS_DEGENERATION = "FAILURE_COUNT_AS_DEGENERATION"
    LOCAL_PROGRESS_AS_ROOT_PROGRESS = "LOCAL_PROGRESS_AS_ROOT_PROGRESS"
    COMPLEXITY_AS_BADNESS = "COMPLEXITY_AS_BADNESS"
    PREMATURE_PROGRAMME_ABANDONMENT = "PREMATURE_PROGRAMME_ABANDONMENT"
    SUCCESS_HINDSIGHT_LEAK = "SUCCESS_HINDSIGHT_LEAK"
    RETROSPECTIVE_PREDICTION_REWRITE = "RETROSPECTIVE_PREDICTION_REWRITE"
    ROUTE_FAMILY_MISCLUSTERING = "ROUTE_FAMILY_MISCLUSTERING"
    EXTERNAL_BLOCKER_MISCLASSIFICATION = "EXTERNAL_BLOCKER_MISCLASSIFICATION"
    PHILOSOPHICAL_LABEL_AUTHORITY_LEAK = "PHILOSOPHICAL_LABEL_AUTHORITY_LEAK"
    SHORT_HORIZON_BIAS = "SHORT_HORIZON_BIAS"


class RootPreservationStatus(str, Enum):
    PRESERVATION_INTERFACE_ESTABLISHED = "PRESERVATION_INTERFACE_ESTABLISHED"
    PRESERVATION_INTERFACE_ABSENT = "PRESERVATION_INTERFACE_ABSENT"
    PRESERVATION_INTERFACE_REFUTED = "PRESERVATION_INTERFACE_REFUTED"
    CANNOT_CHECK = "CANNOT_CHECK"


class RootCoordinatePreservationInterface(Protocol):
    def preservation_status(self, *, surrogate_id: str, root_goal_id: str, scope: str) -> RootPreservationStatus: ...


class ProgressKind(str, Enum):
    ROOT_PROGRESS = "ROOT_PROGRESS"
    LOCAL_PROGRESS = "LOCAL_PROGRESS"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class SurrogateImprovement:
    improvement_id: str
    surrogate_id: str
    root_goal_id: str
    scope: str

    def __post_init__(self) -> None:
        if not self.improvement_id or not self.surrogate_id or not self.scope:
            raise ValueError("surrogate improvements require id, surrogate and scope")


@dataclass(frozen=True)
class ProgressClassification:
    improvement_id: str
    kind: ProgressKind
    preservation_status: RootPreservationStatus
    reasons: Tuple[str, ...]


def classify_surrogate_improvement(
    improvement: SurrogateImprovement,
    interface: Optional[RootCoordinatePreservationInterface],
) -> ProgressClassification:
    if interface is None:
        return ProgressClassification(
            improvement.improvement_id,
            ProgressKind.LOCAL_PROGRESS,
            RootPreservationStatus.PRESERVATION_INTERFACE_ABSENT,
            ("no_root_coordinate_preservation_interface_supplied", "surrogate_improvement_classified_as_local_progress"),
        )
    status = interface.preservation_status(
        surrogate_id=improvement.surrogate_id,
        root_goal_id=improvement.root_goal_id,
        scope=improvement.scope,
    )
    if status is RootPreservationStatus.PRESERVATION_INTERFACE_ESTABLISHED:
        return ProgressClassification(improvement.improvement_id, ProgressKind.ROOT_PROGRESS, status, ("surrogate_to_root_preservation_established_for_scope",))
    if status is RootPreservationStatus.CANNOT_CHECK:
        return ProgressClassification(improvement.improvement_id, ProgressKind.CANNOT_CHECK, status, ("preservation_status_unresolved",))
    return ProgressClassification(improvement.improvement_id, ProgressKind.LOCAL_PROGRESS, status, (f"preservation_status:{status.value}", "surrogate_improvement_is_not_root_progress"))


class ContinuityCoordinate(str, Enum):
    CORE_REPRESENTATION_OR_MECHANISM = "CORE_REPRESENTATION_OR_MECHANISM"
    ROOT_BRIDGE_HYPOTHESIS = "ROOT_BRIDGE_HYPOTHESIS"
    MECHANISM_FAMILY = "MECHANISM_FAMILY"
    SURROGATE_ROOT_COORDINATE_RELATION = "SURROGATE_ROOT_COORDINATE_RELATION"
    OPERATOR_MOTIF = "OPERATOR_MOTIF"
    FAILURE_INTERFACE = "FAILURE_INTERFACE"
    BACKWARD_OBLIGATION_LANDMARK = "BACKWARD_OBLIGATION_LANDMARK"
    ROOT_GOAL_ID = "ROOT_GOAL_ID"


class ContinuityVerdict(str, Enum):
    SAME_ROUTE_FAMILY = "SAME_ROUTE_FAMILY"
    DIFFERENT_ROUTE_FAMILY = "DIFFERENT_ROUTE_FAMILY"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class RouteEpisodeDescriptor:
    episode_id: str
    root_goal_id: str
    core_representation_or_mechanism: str = ""
    root_bridge_hypothesis: str = ""
    mechanism_family: str = ""
    surrogate_root_coordinate_relation: str = ""
    operator_motif: str = ""
    failure_interface: str = ""
    backward_obligation_landmark: str = ""

    def coordinate(self, coordinate: ContinuityCoordinate) -> str:
        return {
            ContinuityCoordinate.CORE_REPRESENTATION_OR_MECHANISM: self.core_representation_or_mechanism,
            ContinuityCoordinate.ROOT_BRIDGE_HYPOTHESIS: self.root_bridge_hypothesis,
            ContinuityCoordinate.MECHANISM_FAMILY: self.mechanism_family,
            ContinuityCoordinate.SURROGATE_ROOT_COORDINATE_RELATION: self.surrogate_root_coordinate_relation,
            ContinuityCoordinate.OPERATOR_MOTIF: self.operator_motif,
            ContinuityCoordinate.FAILURE_INTERFACE: self.failure_interface,
            ContinuityCoordinate.BACKWARD_OBLIGATION_LANDMARK: self.backward_obligation_landmark,
            ContinuityCoordinate.ROOT_GOAL_ID: self.root_goal_id,
        }[coordinate]


@dataclass(frozen=True)
class ContinuityPolicy:
    policy_id: str
    required_coordinates: Tuple[ContinuityCoordinate, ...]

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("continuity policies require a policy_id")
        if not self.required_coordinates:
            raise ValueError("a continuity policy must require at least one coordinate")
        if len(set(self.required_coordinates)) != len(self.required_coordinates):
            raise ValueError("required coordinates must be unique")
        if set(self.required_coordinates) == {ContinuityCoordinate.ROOT_GOAL_ID}:
            raise ValueError("root_goal_id alone is never route-family continuity")


DEFAULT_CONTINUITY_POLICY = ContinuityPolicy(
    "default_core_and_root_bridge",
    (ContinuityCoordinate.CORE_REPRESENTATION_OR_MECHANISM, ContinuityCoordinate.ROOT_BRIDGE_HYPOTHESIS),
)


@dataclass(frozen=True)
class ContinuityReport:
    verdict: ContinuityVerdict
    policy_id: str
    matched: Tuple[ContinuityCoordinate, ...]
    mismatched: Tuple[ContinuityCoordinate, ...]
    unknown: Tuple[ContinuityCoordinate, ...]
    reasons: Tuple[str, ...]


def same_route_family(left: RouteEpisodeDescriptor, right: RouteEpisodeDescriptor, policy: ContinuityPolicy = DEFAULT_CONTINUITY_POLICY) -> ContinuityReport:
    matched: list[ContinuityCoordinate] = []
    mismatched: list[ContinuityCoordinate] = []
    unknown: list[ContinuityCoordinate] = []
    for coordinate in policy.required_coordinates:
        left_value, right_value = left.coordinate(coordinate), right.coordinate(coordinate)
        if not left_value or not right_value:
            unknown.append(coordinate)
        elif left_value == right_value:
            matched.append(coordinate)
        else:
            mismatched.append(coordinate)
    if unknown:
        return ContinuityReport(ContinuityVerdict.CANNOT_CHECK, policy.policy_id, tuple(matched), tuple(mismatched), tuple(unknown), ("required_continuity_coordinate_unknown_on_one_or_both_episodes",))
    if mismatched:
        return ContinuityReport(ContinuityVerdict.DIFFERENT_ROUTE_FAMILY, policy.policy_id, tuple(matched), tuple(mismatched), (), ("required_continuity_coordinates_differ",))
    return ContinuityReport(ContinuityVerdict.SAME_ROUTE_FAMILY, policy.policy_id, tuple(matched), (), (), ("all_required_continuity_coordinates_agree",))


class ChronologyKind(str, Enum):
    PROSPECTIVE_DISCRIMINATOR = "PROSPECTIVE_DISCRIMINATOR"
    POSTHOC_REPAIR = "POSTHOC_REPAIR"


@dataclass(frozen=True)
class ChronologyRecord:
    record_id: str
    episode_id: str
    kind: ChronologyKind
    declared_before_outcome: Optional[bool]
    survived: Optional[bool] = None


@dataclass(frozen=True)
class ChronologyTally:
    prospective_successes: int
    prospective_attempts: int
    posthoc_repairs: int
    rewritten_predictions: Tuple[str, ...]
    unknown_chronology: Tuple[str, ...]


def tally_chronology(records: Iterable[ChronologyRecord]) -> ChronologyTally:
    successes = attempts = repairs = 0
    rewritten: list[str] = []
    unknown: list[str] = []
    for record in records:
        if record.declared_before_outcome is None:
            unknown.append(record.record_id)
        elif record.kind is ChronologyKind.POSTHOC_REPAIR:
            repairs += 1
        elif record.declared_before_outcome is False:
            rewritten.append(record.record_id)
        else:
            attempts += 1
            if record.survived is True:
                successes += 1
    return ChronologyTally(successes, attempts, repairs, tuple(rewritten), tuple(unknown))


class CoordinateDirection(str, Enum):
    HIGHER_IS_MOVEMENT = "HIGHER_IS_MOVEMENT"
    LOWER_IS_MOVEMENT = "LOWER_IS_MOVEMENT"
    CONTEXT_ONLY = "CONTEXT_ONLY"


COORDINATE_DIRECTIONS: dict[str, CoordinateDirection] = {
    "root_critical_obligations_closed": CoordinateDirection.HIGHER_IS_MOVEMENT,
    "new_root_reachable_states": CoordinateDirection.HIGHER_IS_MOVEMENT,
    "residual_contraction": CoordinateDirection.HIGHER_IS_MOVEMENT,
    "prospective_prediction_success": CoordinateDirection.HIGHER_IS_MOVEMENT,
    "discriminating_falsifier_yield": CoordinateDirection.HIGHER_IS_MOVEMENT,
    "representation_gain": CoordinateDirection.HIGHER_IS_MOVEMENT,
    "retrieval_gain": CoordinateDirection.HIGHER_IS_MOVEMENT,
    "new_verified_local_results": CoordinateDirection.HIGHER_IS_MOVEMENT,
    "auxiliary_complexity_growth": CoordinateDirection.CONTEXT_ONLY,
    "repeated_failure_redundancy": CoordinateDirection.CONTEXT_ONLY,
    "root_bridge_stability": CoordinateDirection.LOWER_IS_MOVEMENT,
    "verification_debt_growth": CoordinateDirection.CONTEXT_ONLY,
    "cost_per_epistemic_gain": CoordinateDirection.CONTEXT_ONLY,
    "exploration_diversity": CoordinateDirection.CONTEXT_ONLY,
    "external_blocker_fraction": CoordinateDirection.CONTEXT_ONLY,
}
COORDINATE_NAMES = tuple(COORDINATE_DIRECTIONS)
DEFAULT_NON_COMPENSATORY = (
    "root_critical_obligations_closed",
    "new_root_reachable_states",
    "root_bridge_stability",
)


@dataclass(frozen=True)
class ProgrammeHealthVector:
    coordinates: Tuple[Tuple[str, float], ...]
    non_compensatory_coordinates: Tuple[str, ...]
    window_episode_ids: Tuple[str, ...]

    def __post_init__(self) -> None:
        names = [name for name, _ in self.coordinates]
        if len(names) != len(set(names)):
            raise ValueError("health-vector coordinate names must be unique")
        if set(names) != set(COORDINATE_NAMES):
            raise ValueError("health vector must contain exactly the registered coordinates")
        if not self.non_compensatory_coordinates:
            raise ValueError("declare at least one non-compensatory coordinate")
        for name in self.non_compensatory_coordinates:
            if name not in COORDINATE_DIRECTIONS:
                raise ValueError(f"unknown non-compensatory coordinate:{name}")
            if COORDINATE_DIRECTIONS[name] is CoordinateDirection.CONTEXT_ONLY:
                raise ValueError("context-only coordinates cannot be non-compensatory")

    def __iter__(self):
        raise TypeError("ProgrammeHealthVector is deliberately non-aggregable")

    def __float__(self) -> float:
        raise TypeError("ProgrammeHealthVector has no scalar value")

    def value(self, name: str) -> float:
        for key, value in self.coordinates:
            if key == name:
                return value
        raise KeyError(name)

    def shows_movement(self, name: str) -> bool:
        direction = COORDINATE_DIRECTIONS[name]
        value = self.value(name)
        if direction is CoordinateDirection.HIGHER_IS_MOVEMENT:
            return value > 0
        if direction is CoordinateDirection.LOWER_IS_MOVEMENT:
            return value < 1.0
        raise ValueError(f"context-only coordinate has no movement predicate:{name}")


@dataclass(frozen=True)
class RouteFamilyLineage:
    lineage_id: str
    root_goal_id: str
    route_family_id: str
    core_representation_or_mechanism: str
    root_bridge_hypothesis: str
    founding_episode_id: str
    episode_ids_in_chronology: Tuple[str, ...]
    continuity_policy_id: str


@dataclass(frozen=True)
class RouteWindowObservation:
    lineage_id: str
    window_episode_ids: Tuple[str, ...]
    root_obligations_verified_closed: int
    root_reachable_states_from_verified_root_work: int
    residual_contraction: float
    discriminating_falsifiers_yielded: int
    representation_gain: float
    retrieval_gain: float
    verified_local_results: int
    auxiliary_assumptions_added_after_failure: int
    exception_classes_added: int
    route_specific_repair_lemmas: int
    interfaces_opened: int
    interfaces_closed: int
    repeated_failure_redundancy: float
    root_bridge_stability: float
    verification_debt_growth: float
    cost_per_epistemic_gain: float
    exploration_diversity: float
    actions_blocked_externally: int
    actions_attempted: int
    named_external_blockers: Tuple[str, ...]
    search_space_eliminated: float
    stable_obstruction_identified: bool
    forced_productive_representation_reset: bool
    representation_reset_declared: bool
    chronology_records: Tuple[ChronologyRecord, ...] = ()
    surrogate_improvements: Tuple[SurrogateImprovement, ...] = ()


@dataclass(frozen=True)
class RouteFamilyHealthReport:
    lineage_id: str
    state: RouteHealthState
    vector: ProgrammeHealthVector | None
    stalled_non_compensatory_coordinates: Tuple[str, ...]
    reasons: Tuple[str, ...]
    chronology: ChronologyTally | None

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def grants_abandonment_authority(self) -> bool:
        return False

    @property
    def recommends_abandonment(self) -> bool:
        return False

    @property
    def is_truth_verdict(self) -> bool:
        return False


def _vector(observation: RouteWindowObservation, root_interface: RootCoordinatePreservationInterface | None, non_compensatory: Tuple[str, ...]) -> ProgrammeHealthVector:
    root_from_surrogates = 0
    local_from_surrogates = 0
    unresolved_surrogates = 0
    for improvement in observation.surrogate_improvements:
        classification = classify_surrogate_improvement(improvement, root_interface)
        if classification.kind is ProgressKind.ROOT_PROGRESS:
            root_from_surrogates += 1
        elif classification.kind is ProgressKind.LOCAL_PROGRESS:
            local_from_surrogates += 1
        else:
            unresolved_surrogates += 1
    chronology = tally_chronology(observation.chronology_records)
    prospective_success = (
        chronology.prospective_successes / chronology.prospective_attempts
        if chronology.prospective_attempts else 0.0
    )
    coordinates = (
        ("root_critical_obligations_closed", float(observation.root_obligations_verified_closed)),
        ("new_root_reachable_states", float(observation.root_reachable_states_from_verified_root_work + root_from_surrogates)),
        ("residual_contraction", observation.residual_contraction),
        ("prospective_prediction_success", prospective_success),
        ("discriminating_falsifier_yield", float(observation.discriminating_falsifiers_yielded)),
        ("representation_gain", observation.representation_gain),
        ("retrieval_gain", observation.retrieval_gain),
        ("new_verified_local_results", float(observation.verified_local_results + local_from_surrogates)),
        ("auxiliary_complexity_growth", float(observation.auxiliary_assumptions_added_after_failure + observation.exception_classes_added + observation.route_specific_repair_lemmas)),
        ("repeated_failure_redundancy", observation.repeated_failure_redundancy),
        ("root_bridge_stability", observation.root_bridge_stability),
        ("verification_debt_growth", observation.verification_debt_growth),
        ("cost_per_epistemic_gain", observation.cost_per_epistemic_gain),
        ("exploration_diversity", observation.exploration_diversity),
        ("external_blocker_fraction", observation.actions_blocked_externally / observation.actions_attempted if observation.actions_attempted else 0.0),
    )
    if unresolved_surrogates:
        # The unresolved count is deliberately not hidden in another coordinate;
        # the caller receives CANNOT_CHECK before classifying the vector.
        raise RuntimeError("surrogate_root_preservation_unresolved")
    return ProgrammeHealthVector(coordinates, non_compensatory, observation.window_episode_ids)


def assess_route_family_health(
    lineage: RouteFamilyLineage,
    observation: RouteWindowObservation,
    *,
    non_compensatory_coordinates: Tuple[str, ...] = DEFAULT_NON_COMPENSATORY,
    root_preservation_interface: RootCoordinatePreservationInterface | None = None,
    minimum_history: int = 4,
) -> RouteFamilyHealthReport:
    if lineage.lineage_id != observation.lineage_id:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.CANNOT_CHECK, None, (), ("lineage_identity_mismatch",), None)
    if len(observation.window_episode_ids) < minimum_history:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.INSUFFICIENT_HISTORY, None, (), ("window_too_short_for_longitudinal_health",), tally_chronology(observation.chronology_records))
    if observation.representation_reset_declared:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.RESTRUCTURING_SIGNAL, None, (), ("representation_reset_starts_new_lineage_comparison",), tally_chronology(observation.chronology_records))
    try:
        vector = _vector(observation, root_preservation_interface, non_compensatory_coordinates)
    except RuntimeError:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.CANNOT_CHECK, None, (), ("surrogate_root_preservation_unresolved",), tally_chronology(observation.chronology_records))
    chronology = tally_chronology(observation.chronology_records)
    if chronology.unknown_chronology:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.CANNOT_CHECK, vector, (), ("prediction_chronology_unknown",), chronology)
    if observation.actions_blocked_externally > 0 and observation.named_external_blockers:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.EXTERNALLY_BLOCKED, vector, (), ("named_external_blocker_preempts_stagnation",), chronology)

    stalled = tuple(name for name in non_compensatory_coordinates if not vector.shows_movement(name))
    local_information = any((
        vector.value("new_verified_local_results") > 0,
        observation.search_space_eliminated > 0,
        observation.stable_obstruction_identified,
        observation.forced_productive_representation_reset,
        observation.discriminating_falsifiers_yielded > 0,
        observation.representation_gain > 0,
        observation.retrieval_gain > 0,
        observation.residual_contraction > 0,
    ))
    patch_growth = (
        observation.auxiliary_assumptions_added_after_failure
        + observation.exception_classes_added
        + max(0, observation.interfaces_opened - observation.interfaces_closed)
        + observation.route_specific_repair_lemmas
    )
    prospective_success = chronology.prospective_successes > 0

    if not stalled:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.PROGRESSIVE_SIGNAL, vector, (), ("all_non_compensatory_root_coordinates_moved",), chronology)
    if local_information:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.LOCALLY_PROGRESSIVE_ROOT_STALLED, vector, stalled, ("local_epistemic_gain_without_complete_root_movement",), chronology)
    if patch_growth > 0 and chronology.posthoc_repairs > 0 and not prospective_success:
        return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.PATCH_ACCUMULATION_SIGNAL, vector, stalled, ("posthoc_repair_complexity_without_prospective_success",), chronology)
    return RouteFamilyHealthReport(lineage.lineage_id, RouteHealthState.STAGNANT_SIGNAL, vector, stalled, ("no_root_or_local_epistemic_movement_in_window",), chronology)


__all__ = [
    "COORDINATE_DIRECTIONS", "DEFAULT_CONTINUITY_POLICY", "DEFAULT_NON_COMPENSATORY",
    "ChronologyKind", "ChronologyRecord", "ChronologyTally", "ContinuityCoordinate",
    "ContinuityPolicy", "ContinuityReport", "ContinuityVerdict", "CoordinateDirection",
    "ProgrammeHealthVector", "ProgressClassification", "ProgressKind",
    "RootCoordinatePreservationInterface", "RootPreservationStatus",
    "RouteEpisodeDescriptor", "RouteFamilyHealthReport", "RouteFamilyLineage",
    "RouteHealthFailureMode", "RouteHealthState", "RouteWindowObservation",
    "SurrogateImprovement", "assess_route_family_health", "classify_surrogate_improvement",
    "same_route_family", "tally_chronology",
]
