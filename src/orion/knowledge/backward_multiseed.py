"""Backward obligation expansion and structured multi-seed bridge search.

Reconstructed from RAKL issue #141 at
SzeChunYiu/RAKL@70f5f7c4a6771ffd1158765b42ac9f8aee8a270f.

The RAKL contract is preserved while the old problem-solving-algebra dependency
is replaced by a small ORION-local transition-evidence boundary.  Backward
obligations are sufficient candidates, never necessities; waypoint seeds are
search candidates, never evidence or progress; meet-in-the-middle glue requires
an entirely verified chain and still grants no solution authority.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from hashlib import sha256
from typing import Iterable, Optional, Tuple

from orion.knowledge.similarity import (
    DistinguishingProbeCertificate,
    SimilarityWitness,
    WitnessVerdict,
    validate_similarity_witness,
)


class BackwardSeedFailureMode(str, Enum):
    BACKWARD_SUFFICIENCY_AS_NECESSITY = "BACKWARD_SUFFICIENCY_AS_NECESSITY"
    GOLD_PATH_LEAK = "GOLD_PATH_LEAK"
    RANDOM_SEED_NOISE = "RANDOM_SEED_NOISE"
    WAYPOINT_INTERESTINGNESS_OVERREACH = "WAYPOINT_INTERESTINGNESS_OVERREACH"
    UNVERIFIED_CONNECTION_AS_ROAD = "UNVERIFIED_CONNECTION_AS_ROAD"
    LOCAL_WAYPOINT_AS_ROOT_PROGRESS = "LOCAL_WAYPOINT_AS_ROOT_PROGRESS"
    SEED_FAMILY_COLLAPSE = "SEED_FAMILY_COLLAPSE"
    FRONTIER_REPRESENTATION_MISMATCH = "FRONTIER_REPRESENTATION_MISMATCH"
    MEET_IN_MIDDLE_FALSE_GLUE = "MEET_IN_MIDDLE_FALSE_GLUE"
    CONNECTION_AUTHORITY_LEAK = "CONNECTION_AUTHORITY_LEAK"


class ImplicationStatus(str, Enum):
    CANDIDATE_UNVERIFIED = "CANDIDATE_UNVERIFIED"
    IMPLICATION_VERIFIED = "IMPLICATION_VERIFIED"
    IMPLICATION_REFUTED = "IMPLICATION_REFUTED"
    CANNOT_CHECK = "CANNOT_CHECK"


class AlternativePredecessorSearch(str, Enum):
    ALTERNATIVES_RECORDED = "ALTERNATIVES_RECORDED"
    ALTERNATIVES_NOT_SEARCHED = "ALTERNATIVES_NOT_SEARCHED"
    BOUNDED_SEARCH_NONE_FOUND = "BOUNDED_SEARCH_NONE_FOUND"


def _hash(*parts: str) -> str:
    return sha256("|".join(parts).encode()).hexdigest()


@dataclass(frozen=True)
class BackwardObligation:
    obligation_id: str
    root_goal_id: str
    statement: str
    structural_signature: Tuple[str, ...]
    sufficient_for: Tuple[str, ...]
    supporting_family: str
    supporting_theorem_ids: Tuple[str, ...]
    assumptions: Tuple[str, ...]
    representation: str
    scope: str
    source_evidence_ids: Tuple[str, ...]
    implication_status: ImplicationStatus
    alternative_search: AlternativePredecessorSearch
    implication_checker: str = ""
    known_alternative_predecessor_families: Tuple[str, ...] = ()
    alternative_search_boundary: Tuple[str, ...] = ()
    expansion_depth: int = 1

    def __post_init__(self) -> None:
        if not self.obligation_id or not self.root_goal_id or not self.statement:
            raise ValueError("obligations require id, root goal and statement")
        if not self.sufficient_for or not self.structural_signature:
            raise ValueError("obligations require a sufficient target and structural signature")
        if not self.supporting_family or not self.scope or not self.representation:
            raise ValueError("obligations require supporting family, scope and representation")
        if self.expansion_depth < 1:
            raise ValueError("expansion depth must be positive")
        if self.implication_status is ImplicationStatus.IMPLICATION_VERIFIED and not self.implication_checker:
            raise ValueError("a verified implication requires a checker identity")
        if self.alternative_search is AlternativePredecessorSearch.ALTERNATIVES_RECORDED and not self.known_alternative_predecessor_families:
            raise ValueError("ALTERNATIVES_RECORDED requires at least one recorded alternative family")
        if self.alternative_search is AlternativePredecessorSearch.BOUNDED_SEARCH_NONE_FOUND and not self.alternative_search_boundary:
            raise ValueError("bounded search finding none must record its search boundary")

    @property
    def candidate_only(self) -> bool:
        return True

    @property
    def establishes_necessity(self) -> bool:
        return False

    @property
    def grants_root_progress(self) -> bool:
        return False

    @property
    def artifact_hash(self) -> str:
        return _hash(
            self.obligation_id, self.root_goal_id, self.statement,
            ",".join(self.structural_signature), ",".join(self.sufficient_for),
            self.supporting_family, self.representation, self.scope,
            self.implication_status.value, self.alternative_search.value,
        )


@dataclass(frozen=True)
class BackwardObligationProposal:
    proposal_id: str
    statement: str
    structural_signature: Tuple[str, ...]
    supporting_family: str
    representation: str
    scope: str
    implication_status: ImplicationStatus
    alternative_search: AlternativePredecessorSearch
    supporting_theorem_ids: Tuple[str, ...] = ()
    assumptions: Tuple[str, ...] = ()
    source_evidence_ids: Tuple[str, ...] = ()
    implication_checker: str = ""
    known_alternative_predecessor_families: Tuple[str, ...] = ()
    alternative_search_boundary: Tuple[str, ...] = ()
    claims_necessity: bool = False


@dataclass(frozen=True)
class RejectedProposal:
    proposal_id: str
    reasons: Tuple[str, ...]
    failure_modes: Tuple[BackwardSeedFailureMode, ...] = ()


@dataclass(frozen=True)
class BackwardExpansion:
    target_id: str
    root_goal_id: str
    generator_id: str
    obligations: Tuple[BackwardObligation, ...]
    rejected: Tuple[RejectedProposal, ...]
    reasons: Tuple[str, ...]

    @property
    def grants_necessity_authority(self) -> bool:
        return False

    @property
    def sufficient_frontier_signature(self) -> Tuple[str, ...]:
        return tuple(sorted({coord for item in self.obligations for coord in item.structural_signature}))


def expand_backward(*, target_id: str, root_goal_id: str, proposals: Iterable[BackwardObligationProposal], generator_id: str, expansion_depth: int = 1) -> BackwardExpansion:
    if not target_id or not root_goal_id or not generator_id:
        raise ValueError("backward expansion requires target, root goal and generator ids")
    accepted: list[BackwardObligation] = []
    rejected: list[RejectedProposal] = []
    for proposal in proposals:
        reasons: list[str] = []
        modes: list[BackwardSeedFailureMode] = []
        if proposal.claims_necessity:
            reasons.append("proposal_asserts_predecessor_is_necessary")
            modes.append(BackwardSeedFailureMode.BACKWARD_SUFFICIENCY_AS_NECESSITY)
        if not proposal.statement or not proposal.structural_signature:
            reasons.append("proposal_missing_statement_or_structural_signature")
        if reasons:
            rejected.append(RejectedProposal(proposal.proposal_id, tuple(reasons), tuple(modes)))
            continue
        try:
            accepted.append(BackwardObligation(
                obligation_id=proposal.proposal_id,
                root_goal_id=root_goal_id,
                statement=proposal.statement,
                structural_signature=proposal.structural_signature,
                sufficient_for=(target_id,),
                supporting_family=proposal.supporting_family,
                supporting_theorem_ids=proposal.supporting_theorem_ids,
                assumptions=proposal.assumptions,
                representation=proposal.representation,
                scope=proposal.scope,
                source_evidence_ids=proposal.source_evidence_ids,
                implication_status=proposal.implication_status,
                alternative_search=proposal.alternative_search,
                implication_checker=proposal.implication_checker,
                known_alternative_predecessor_families=proposal.known_alternative_predecessor_families,
                alternative_search_boundary=proposal.alternative_search_boundary,
                expansion_depth=expansion_depth,
            ))
        except ValueError as error:
            rejected.append(RejectedProposal(proposal.proposal_id, (str(error),)))
    return BackwardExpansion(
        target_id, root_goal_id, generator_id, tuple(accepted), tuple(rejected),
        ("generated_predecessors_are_sufficient_candidates_only", "no_generated_predecessor_is_claimed_necessary", "rejected_proposals_retained_as_negative_history"),
    )


class SeedFamily(str, Enum):
    CANDIDATE_LEMMA = "CANDIDATE_LEMMA"
    CANDIDATE_INVARIANT = "CANDIDATE_INVARIANT"
    ALTERNATIVE_REPRESENTATION = "ALTERNATIVE_REPRESENTATION"
    AUXILIARY_OBJECT = "AUXILIARY_OBJECT"
    INTERMEDIATE_BOUND = "INTERMEDIATE_BOUND"
    EXTREME_OR_BOUNDARY_CASE = "EXTREME_OR_BOUNDARY_CASE"
    NORMAL_FORM = "NORMAL_FORM"
    REDUCTION_TARGET = "REDUCTION_TARGET"
    KNOWN_THEOREM_INTERFACE = "KNOWN_THEOREM_INTERFACE"
    ANALOGY_OR_JUMP_DERIVED = "ANALOGY_OR_JUMP_DERIVED"
    COUNTEREXAMPLE_BOUNDARY = "COUNTEREXAMPLE_BOUNDARY"
    SYMMETRY_OR_DUALITY_COORDINATE = "SYMMETRY_OR_DUALITY_COORDINATE"
    LOCAL_TO_GLOBAL_BRIDGE_CANDIDATE = "LOCAL_TO_GLOBAL_BRIDGE_CANDIDATE"


class SeedOrigin(str, Enum):
    OPERATOR_APPLICATION = "OPERATOR_APPLICATION"
    RETRIEVAL = "RETRIEVAL"
    JUMP = "JUMP"
    FIBRE_EXPANSION = "FIBRE_EXPANSION"
    FAILURE_HISTORY = "FAILURE_HISTORY"


@dataclass(frozen=True)
class WaypointSeed:
    seed_id: str
    root_goal_id: str
    atom_ids: Tuple[str, ...]
    family: SeedFamily
    statement_or_object: str
    representation: str
    structural_signature: Tuple[str, ...]
    origin: SeedOrigin
    origin_operator_id: str
    expected_useful_connection: str
    falsifier_or_cheapest_connection_test: str
    assumptions: Tuple[str, ...] = ()
    scope: str = ""

    def __post_init__(self) -> None:
        if not self.seed_id or not self.root_goal_id:
            raise ValueError("waypoint seeds require seed_id and root_goal_id")
        if not self.statement_or_object or not self.structural_signature:
            raise ValueError("waypoint seeds require a statement/object and structural signature")
        if not self.expected_useful_connection:
            raise ValueError("a seed must declare the connection it is expected to expose")
        if not self.falsifier_or_cheapest_connection_test:
            raise ValueError("a seed must carry its cheapest connection test")

    @property
    def candidate_only(self) -> bool:
        return True

    @property
    def is_evidence(self) -> bool:
        return False

    @property
    def grants_root_progress(self) -> bool:
        return False

    @property
    def artifact_hash(self) -> str:
        return _hash(self.seed_id, self.root_goal_id, self.family.value, self.statement_or_object, self.representation, ",".join(self.structural_signature), self.origin.value)


@dataclass(frozen=True)
class SeedDiversityReport:
    families_present: Tuple[SeedFamily, ...]
    seeds_per_family: Tuple[Tuple[SeedFamily, int], ...]
    distinct_family_count: int
    total_seeds: int
    collapsed: bool
    reasons: Tuple[str, ...]

    @property
    def grants_progress_credit(self) -> bool:
        return False


def assess_seed_diversity(seeds: Iterable[WaypointSeed], *, min_distinct_families: int = 3) -> SeedDiversityReport:
    if min_distinct_families < 1:
        raise ValueError("min_distinct_families must be positive")
    rows = tuple(seeds)
    counts: dict[SeedFamily, int] = {}
    for seed in rows:
        counts[seed.family] = counts.get(seed.family, 0) + 1
    present = tuple(sorted(counts, key=lambda family: family.value))
    collapsed = bool(rows) and len(present) < min_distinct_families
    reasons: list[str] = []
    if not rows:
        reasons.append("no_seeds_supplied")
    if collapsed:
        reasons.append(f"{BackwardSeedFailureMode.SEED_FAMILY_COLLAPSE.value}:distinct_families:{len(present)}:required:{min_distinct_families}")
    reasons.append("seed_count_is_not_a_success_metric")
    return SeedDiversityReport(present, tuple((family, counts[family]) for family in present), len(present), len(rows), collapsed, tuple(reasons))


class ConnectionVerdict(str, Enum):
    VERIFIED_TRANSITION = "VERIFIED_TRANSITION"
    CANDIDATE_BRIDGE = "CANDIDATE_BRIDGE"
    ANALOGY_ONLY = "ANALOGY_ONLY"
    REFUTED = "REFUTED"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


class ConnectionNodeKind(str, Enum):
    FORWARD_FRONTIER_STATE = "FORWARD_FRONTIER_STATE"
    BACKWARD_OBLIGATION = "BACKWARD_OBLIGATION"
    WAYPOINT_SEED = "WAYPOINT_SEED"
    ROOT_GOAL = "ROOT_GOAL"


@dataclass(frozen=True)
class ConnectionNode:
    node_id: str
    kind: ConnectionNodeKind
    representation: str
    structural_signature: Tuple[str, ...]
    required_facts: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("connection nodes require a node_id")


@dataclass(frozen=True)
class TransitionEvidence:
    """Typed ORION replacement for RAKL's old problem-solving-algebra adapter."""

    operator_id: str
    required_obstructions: frozenset[str]
    source_obstructions: frozenset[str]
    source_facts: frozenset[str]
    adds_facts: frozenset[str]
    checker_id: str = ""
    verification_artifact_id: str = ""

    @property
    def applicable(self) -> bool:
        return self.required_obstructions.issubset(self.source_obstructions)

    @property
    def reached_facts(self) -> frozenset[str]:
        return self.source_facts | self.adds_facts if self.applicable else self.source_facts


@dataclass(frozen=True)
class ConnectionTrial:
    trial_id: str
    source: ConnectionNode
    target: ConnectionNode
    declared_before_outcomes: Optional[bool]
    blocked_dependency: str = ""
    transition: Optional[TransitionEvidence] = None
    witness: Optional[SimilarityWitness] = None
    refutation: Optional[DistinguishingProbeCertificate] = None


@dataclass(frozen=True)
class ConnectionReport:
    verdict: ConnectionVerdict
    trial_id: str
    source_id: str
    target_id: str
    reasons: Tuple[str, ...]
    failure_modes: Tuple[BackwardSeedFailureMode, ...] = ()

    @property
    def grants_route_authority(self) -> bool:
        return False

    @property
    def is_road(self) -> bool:
        return self.verdict is ConnectionVerdict.VERIFIED_TRANSITION

    @property
    def is_negative_history(self) -> bool:
        return self.verdict in {ConnectionVerdict.REFUTED, ConnectionVerdict.BLOCKED}


def _report(verdict: ConnectionVerdict, trial: ConnectionTrial, reasons: Tuple[str, ...], modes: Tuple[BackwardSeedFailureMode, ...] = ()) -> ConnectionReport:
    return ConnectionReport(verdict, trial.trial_id, trial.source.node_id, trial.target.node_id, reasons, modes)


def evaluate_connection(trial: ConnectionTrial) -> ConnectionReport:
    if not trial.trial_id or not trial.source.node_id or not trial.target.node_id:
        return _report(ConnectionVerdict.CANNOT_CHECK, trial, ("trial_or_node_identity_missing",))
    if trial.blocked_dependency:
        return _report(ConnectionVerdict.BLOCKED, trial, (f"named_unavailable_dependency:{trial.blocked_dependency}",))
    if trial.declared_before_outcomes is None:
        return _report(ConnectionVerdict.CANNOT_CHECK, trial, ("connection_freeze_chronology_unknown",))
    if trial.declared_before_outcomes is False:
        return _report(ConnectionVerdict.CANNOT_CHECK, trial, ("posthoc_connection_selection_is_not_an_admissible_check",))
    if trial.refutation is not None:
        return _report(ConnectionVerdict.REFUTED, trial, (f"distinguishing_probe:{trial.refutation.probe_id}", f"discrepancy:{trial.refutation.discrepancy}", "refutation_retained_as_negative_history"))
    if trial.transition is not None:
        evidence = trial.transition
        if not evidence.applicable:
            return _report(ConnectionVerdict.REFUTED, trial, (f"operator_preconditions_unmet:{evidence.operator_id}", "source_state_cannot_reach_target_by_this_operator"))
        if not trial.target.required_facts.issubset(evidence.reached_facts):
            missing = tuple(sorted(trial.target.required_facts - evidence.reached_facts))
            return _report(ConnectionVerdict.REFUTED, trial, ("target_facts_not_reached:" + ",".join(missing),))
        if not evidence.checker_id or not evidence.verification_artifact_id:
            return _report(ConnectionVerdict.CANDIDATE_BRIDGE, trial, ("operator_transition_is_symbolically_applicable", "no_checker_identity_or_verification_artifact", "unverified_transition_is_not_a_road"), (BackwardSeedFailureMode.UNVERIFIED_CONNECTION_AS_ROAD,))
        return _report(ConnectionVerdict.VERIFIED_TRANSITION, trial, (f"operator:{evidence.operator_id}", f"checker:{evidence.checker_id}", f"verification_artifact:{evidence.verification_artifact_id}", "transition_verified_but_grants_no_theorem_authority"))
    if trial.witness is not None:
        witness_report = validate_similarity_witness(trial.witness)
        if witness_report.verdict is WitnessVerdict.REJECT:
            return _report(ConnectionVerdict.REFUTED, trial, ("similarity_witness_rejected",) + witness_report.reasons)
        if witness_report.verdict is WitnessVerdict.CANNOT_CHECK:
            return _report(ConnectionVerdict.CANNOT_CHECK, trial, ("similarity_witness_incomplete",) + witness_report.reasons)
        return _report(ConnectionVerdict.ANALOGY_ONLY, trial, (f"similarity_relation:{trial.witness.relation.value}", "structural_resemblance_is_not_a_transition"))
    return _report(ConnectionVerdict.CANNOT_CHECK, trial, ("no_operator_bridge_path_or_witness_supplied",))


@dataclass(frozen=True)
class ConnectionHistory:
    entries: Tuple[ConnectionReport, ...] = ()

    def record(self, report: ConnectionReport) -> "ConnectionHistory":
        return replace(self, entries=self.entries + (report,))

    def attempts_for(self, source_id: str, target_id: str) -> Tuple[ConnectionReport, ...]:
        return tuple(entry for entry in self.entries if entry.source_id == source_id and entry.target_id == target_id)

    def is_known_failure(self, source_id: str, target_id: str) -> bool:
        return any(entry.verdict is ConnectionVerdict.REFUTED for entry in self.attempts_for(source_id, target_id))

    def repeated_known_failure_count(self) -> int:
        refuted: set[Tuple[str, str]] = set()
        repeats = 0
        for entry in self.entries:
            pair = (entry.source_id, entry.target_id)
            if pair in refuted:
                repeats += 1
            if entry.verdict is ConnectionVerdict.REFUTED:
                refuted.add(pair)
        return repeats

    @property
    def failed_bridge_ids(self) -> Tuple[str, ...]:
        return tuple(entry.trial_id for entry in self.entries if entry.verdict is ConnectionVerdict.REFUTED)

    @property
    def verified_roads(self) -> Tuple[ConnectionReport, ...]:
        return tuple(entry for entry in self.entries if entry.is_road)


class MeetInMiddleVerdict(str, Enum):
    VERIFIED_GLUE = "VERIFIED_GLUE"
    CANDIDATE_GLUE_UNVERIFIED = "CANDIDATE_GLUE_UNVERIFIED"
    DISCONNECTED = "DISCONNECTED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class MeetInMiddleReport:
    verdict: MeetInMiddleVerdict
    chain_trial_ids: Tuple[str, ...]
    reasons: Tuple[str, ...]
    failure_modes: Tuple[BackwardSeedFailureMode, ...] = ()

    @property
    def grants_solution_authority(self) -> bool:
        return False


def assess_meet_in_middle(chain: Iterable[ConnectionReport], *, forward_frontier_ids: Tuple[str, ...], backward_obligation_ids: Tuple[str, ...]) -> MeetInMiddleReport:
    links = tuple(chain)
    trial_ids = tuple(link.trial_id for link in links)
    if not links:
        return MeetInMiddleReport(MeetInMiddleVerdict.DISCONNECTED, (), ("no_connection_reports_supplied",))
    if not forward_frontier_ids or not backward_obligation_ids:
        return MeetInMiddleReport(MeetInMiddleVerdict.CANNOT_CHECK, trial_ids, ("frontier_identities_missing",))
    for index in range(len(links) - 1):
        if links[index].target_id != links[index + 1].source_id:
            return MeetInMiddleReport(MeetInMiddleVerdict.DISCONNECTED, trial_ids, (f"chain_break_between_links:{index}:{index + 1}",))
    if links[0].source_id not in forward_frontier_ids or links[-1].target_id not in backward_obligation_ids:
        return MeetInMiddleReport(MeetInMiddleVerdict.DISCONNECTED, trial_ids, ("chain_does_not_join_declared_frontiers",))
    if any(link.verdict is ConnectionVerdict.REFUTED for link in links):
        return MeetInMiddleReport(MeetInMiddleVerdict.DISCONNECTED, trial_ids, ("chain_contains_a_refuted_link",))
    weak = tuple(f"{link.trial_id}:{link.verdict.value}" for link in links if not link.is_road)
    if weak:
        return MeetInMiddleReport(MeetInMiddleVerdict.CANDIDATE_GLUE_UNVERIFIED, trial_ids, ("unverified_links_present:" + ",".join(weak), "candidate_glue_is_not_a_join"), (BackwardSeedFailureMode.MEET_IN_MIDDLE_FALSE_GLUE,))
    return MeetInMiddleReport(MeetInMiddleVerdict.VERIFIED_GLUE, trial_ids, ("every_link_is_a_verified_transition_with_a_checker", "verified_glue_still_requires_separate_solution_promotion"))


@dataclass(frozen=True)
class BridgeResidual:
    residual_id: str
    root_goal_id: str
    forward_frontier_signature: Tuple[str, ...]
    backward_sufficient_frontier_signature: Tuple[str, ...]
    missing_coordinates: Tuple[str, ...]
    incompatible_coordinates: Tuple[str, ...]
    known_failed_bridge_ids: Tuple[str, ...]
    candidate_waypoint_seed_ids: Tuple[str, ...]
    cheapest_discriminating_action: str

    def __post_init__(self) -> None:
        if not self.residual_id or not self.root_goal_id:
            raise ValueError("bridge residuals require residual_id and root_goal_id")
        if not self.cheapest_discriminating_action:
            raise ValueError("a residual must name the cheapest discriminating next action")

    @property
    def opens_atom_only(self) -> bool:
        return True

    @property
    def grants_root_progress(self) -> bool:
        return False

    @property
    def frontier_overlap(self) -> float:
        forward, backward = set(self.forward_frontier_signature), set(self.backward_sufficient_frontier_signature)
        union = forward | backward
        return len(forward & backward) / len(union) if union else 0.0


def compute_bridge_residual(*, residual_id: str, root_goal_id: str, forward_frontier_signature: Tuple[str, ...], expansion: BackwardExpansion, history: ConnectionHistory, seeds: Iterable[WaypointSeed] = (), incompatible_coordinates: Tuple[str, ...] = (), cheapest_discriminating_action: str) -> BridgeResidual:
    backward_signature = expansion.sufficient_frontier_signature
    missing = tuple(sorted(set(backward_signature) - set(forward_frontier_signature)))
    return BridgeResidual(
        residual_id, root_goal_id, tuple(sorted(set(forward_frontier_signature))), backward_signature,
        missing, tuple(sorted(set(incompatible_coordinates))), history.failed_bridge_ids,
        tuple(seed.seed_id for seed in seeds), cheapest_discriminating_action,
    )


@dataclass(frozen=True)
class BackwardSeedAuditReport:
    triggered: Tuple[BackwardSeedFailureMode, ...]
    reasons: Tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not self.triggered

    @property
    def grants_scientific_authority(self) -> bool:
        return False


def audit_backward_seed_state(*, diversity: SeedDiversityReport, history: ConnectionHistory, residual: Optional[BridgeResidual] = None, meet_in_middle: Optional[MeetInMiddleReport] = None, necessity_claims: Tuple[str, ...] = (), connections_cited_as_roads: Tuple[str, ...] = (), root_progress_claimed_from_seed_ids: Tuple[str, ...] = (), root_obligations_verified_closed: int = 0, gold_path_exposed: Optional[bool] = None) -> BackwardSeedAuditReport:
    triggered: list[BackwardSeedFailureMode] = []
    reasons: list[str] = []
    if necessity_claims:
        triggered.append(BackwardSeedFailureMode.BACKWARD_SUFFICIENCY_AS_NECESSITY)
        reasons.append("necessity_claimed_for:" + ",".join(necessity_claims))
    if gold_path_exposed is True:
        triggered.append(BackwardSeedFailureMode.GOLD_PATH_LEAK)
        reasons.append("gold_path_exposed_to_solver")
    if gold_path_exposed is None:
        reasons.append("gold_path_exposure_unknown_cannot_check")
    if diversity.collapsed:
        triggered.append(BackwardSeedFailureMode.SEED_FAMILY_COLLAPSE)
    roads = {report.trial_id for report in history.verified_roads}
    leaked = tuple(sorted(set(connections_cited_as_roads) - roads))
    if leaked:
        triggered.append(BackwardSeedFailureMode.UNVERIFIED_CONNECTION_AS_ROAD)
    if root_progress_claimed_from_seed_ids and root_obligations_verified_closed <= 0:
        triggered.append(BackwardSeedFailureMode.LOCAL_WAYPOINT_AS_ROOT_PROGRESS)
    if meet_in_middle is not None and meet_in_middle.verdict is MeetInMiddleVerdict.CANDIDATE_GLUE_UNVERIFIED:
        triggered.append(BackwardSeedFailureMode.MEET_IN_MIDDLE_FALSE_GLUE)
    if residual is not None and residual.frontier_overlap == 0.0:
        triggered.append(BackwardSeedFailureMode.FRONTIER_REPRESENTATION_MISMATCH)
    if history.repeated_known_failure_count() > 0:
        reasons.append(f"repeated_known_failure_attempts:{history.repeated_known_failure_count()}")
    reasons.append("audit_is_search_control_diagnostic_only")
    return BackwardSeedAuditReport(tuple(dict.fromkeys(triggered)), tuple(reasons))


__all__ = [
    "AlternativePredecessorSearch", "BackwardExpansion", "BackwardObligation",
    "BackwardObligationProposal", "BackwardSeedAuditReport", "BackwardSeedFailureMode",
    "BridgeResidual", "ConnectionHistory", "ConnectionNode", "ConnectionNodeKind",
    "ConnectionReport", "ConnectionTrial", "ConnectionVerdict", "ImplicationStatus",
    "MeetInMiddleReport", "MeetInMiddleVerdict", "RejectedProposal", "SeedDiversityReport",
    "SeedFamily", "SeedOrigin", "TransitionEvidence", "WaypointSeed", "assess_meet_in_middle",
    "assess_seed_diversity", "audit_backward_seed_state", "compute_bridge_residual",
    "evaluate_connection", "expand_backward",
]
