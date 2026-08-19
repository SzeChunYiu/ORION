"""Proposal-side discovery objects for ORION's recursive Jump studies.

These records support bounded research protocols; they do not grant scientific,
novelty, or adoption authority.
"""

from .concept_candidate import ConceptCandidate, build_concept_candidate
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
from .thought_experiment import (
    ExecutionMode,
    ProspectiveDiscriminationReport,
    ProspectiveDiscriminationStatus,
    ThoughtExperiment,
    assess_prospective_discrimination,
    build_thought_experiment,
)

__all__ = [name for name in globals() if not name.startswith("_")]
