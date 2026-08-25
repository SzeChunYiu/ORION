"""Proposal-side discovery objects for ORION's recursive Jump studies.

These records support bounded research protocols; they do not grant scientific,
novelty, or adoption authority.
"""

from .concept_candidate import ConceptCandidate, build_concept_candidate
from .decision_geometry import (
    BayesDecision,
    MinimaxDecision,
    TwoWorldHedgeReport,
    bayes_decision,
    common_optimal_actions,
    minimax_regret_decision,
    optimal_actions,
    partition_bayes_regret,
    refines,
    regret_table,
    two_world_hedge_report,
    validate_loss_table,
    zero_regret_supported,
)
from .epistemic_tension import (
    EpistemicTensionCandidate,
    EpistemicTensionReport,
    EvidencePresence,
    TensionStatus,
    assess_tensions,
    build_tension_candidate,
)
from .episodes import (
    AssertionConfidence,
    AssertionRole,
    DiscoveryEpisode,
    EpisodeAssertion,
    EpisodeSource,
    FailureEpisode,
    FailureStage,
    FailureVisibility,
    HistoricalUseMode,
    PreCutoffCandidatePacket,
    SourceKind,
    SourceTemporalRelation,
    build_discovery_episode,
    build_episode_assertion,
    build_episode_source,
    build_failure_episode,
    project_pre_cutoff_candidate_packet,
)
from .harness_identifiability import (
    ClaimVariant,
    HarnessIdentifiabilityReport,
    PreconditionReport,
    assess_identifiability,
    assess_precondition,
    clause_witness_map,
    constant_variant,
    distinguishing_cases,
    minimal_distinguishing_case_sets,
    unattained_clauses,
)
from .model_chronology import (
    HistoricalEligibilityEvidence,
    HistoricalEligibilityState,
    ModelChronologyContract,
    ModelChronologyState,
    TriangulationEvidence,
    TriangulationState,
    build_model_chronology_contract,
)
from .proposal_origin import (
    DiscoveryCreditEvidence,
    DiscoveryCreditState,
    EditKind,
    ProposalOriginRecord,
    ReducibilityState,
    TargetOracleAccess,
    build_proposal_origin,
    supplied_menu_is_outside_closure_candidate,
)
from .thought_experiment import (
    ExecutionMode,
    ProspectiveDiscriminationReport,
    ProspectiveDiscriminationStatus,
    ThoughtExperiment,
    assess_prospective_discrimination,
    build_thought_experiment,
)

__all__ = [name for name in globals() if not name.startswith("_")]
