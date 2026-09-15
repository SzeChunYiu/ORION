"""Replayable host-tool, canonical-mechanics and scientific-campaign bridge for ORION."""

from .broker import (
    BrokerLLMProvider,
    BrokerRetrievalProvider,
    BrokerVerificationProvider,
    CapabilityBroker,
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from .campaign_control import decide_campaign, validate_manifest
from .campaign_protocol import (
    CampaignDecision,
    CampaignState,
    CampaignTransition,
    ProtectedReference,
)
from .campaign_runner import initialize_campaign, run_campaign, run_campaign_cycle
from .donor_campaign import build_donor_campaign_manifest
from .execution_coverage import ExecutionMode, execution_coverage
from .governance_runtime import (
    ContextCandidate,
    ContextSelection,
    request_benchmark,
    request_independent_review,
    select_context,
)
from .governance_hardening import install_governance_hardening
from .mechanics_bridge import (
    atom_calculus_surface,
    compile_workspace_development_fibre,
    mechanic_catalog,
    mechanic_detail,
    mechanics_coverage,
    method_fibre_surface,
    navigate_mechanics,
    rank_workspace_development_fibres,
    run_mechanic_receipts,
    saturation_surface,
)
from .paper_refinement import (
    ConcernClass,
    ConcernClosure,
    PaperConcern,
    PaperRefinementState,
    PaperReviewReceipt,
    RefinementTerminal,
    RepairRoute,
    VenueReadinessProfile,
    assess_refinement_terminal,
    create_refinement_state,
)
from .ocme_programme_hardening import install_ocme_programme_hardening
from .paper_structure_consensus import run_paper_structure_consensus
from .protocol import CapabilityRequest, CapabilityResult
from .recursive_runner import RecursiveRunLimits
from .publication_contract import (
    Q3_HARNESS_PUBLICATION_CONTRACT_ID,
    Q3_HARNESS_REQUIRED_PROPERTIES,
    q3_publication_contract,
    validate_q3_publication_contract,
)
from .p15_q3_instrument import (
    P15_Q3_INSTRUMENT_SCHEMA,
    P15Q3InstrumentReceipt,
    receipt_from_mapping,
)
from .scientific_execution_integrity import ScientificDisposition, ScientificExecutionRecord
from .recursive_runner import RecursiveRunLimits, run_problem_recursive
from .recursive_budget_hardening import install_recursive_budget_hardening
from .recursive_cost_hardening import install_recursive_cost_hardening
from .recursive_experience_binding import (
    WorkspaceRecursiveLLMResearchReasoner,
    install_workspace_recursive_reasoner,
)
from .recursive_director_integration import install_research_director_integration
from .recursive_runner import run_problem_recursive
from .research_resolution import (
    assimilate_negative_result,
    build_resolution_obligation,
    resolution_plan_from_mapping,
)
from .research_v4_conformance import research_v4_conformance
from .runner import run_problem
from .workspace import ResearchWorkspace

__all__ = [
    "BrokerLLMProvider",
    "BrokerRetrievalProvider",
    "BrokerVerificationProvider",
    "CampaignDecision",
    "CampaignState",
    "CampaignTransition",
    "CapabilityBroker",
    "CapabilityRequest",
    "CapabilityResult",
    "ConcernClass",
    "ConcernClosure",
    "ContextCandidate",
    "ContextSelection",
    "ExecutionMode",
    "HostCapabilityFailed",
    "HostCapabilityRequired",
    "PaperConcern",
    "PaperRefinementState",
    "PaperReviewReceipt",
    "P15_Q3_INSTRUMENT_SCHEMA",
    "P15Q3InstrumentReceipt",
    "ProtectedReference",
    "Q3_HARNESS_PUBLICATION_CONTRACT_ID",
    "Q3_HARNESS_REQUIRED_PROPERTIES",
    "RecursiveRunLimits",
    "RefinementTerminal",
    "RepairRoute",
    "ResearchWorkspace",
    "ScientificDisposition",
    "ScientificExecutionRecord",
    "VenueReadinessProfile",
    "WorkspaceRecursiveLLMResearchReasoner",
    "assess_refinement_terminal",
    "assimilate_negative_result",
    "atom_calculus_surface",
    "build_resolution_obligation",
    "build_donor_campaign_manifest",
    "compile_workspace_development_fibre",
    "create_refinement_state",
    "decide_campaign",
    "execution_coverage",
    "initialize_campaign",
    "install_governance_hardening",
    "install_ocme_programme_hardening",
    "install_recursive_budget_hardening",
    "install_recursive_cost_hardening",
    "install_research_director_integration",
    "install_workspace_recursive_reasoner",
    "mechanic_catalog",
    "mechanic_detail",
    "mechanics_coverage",
    "method_fibre_surface",
    "navigate_mechanics",
    "q3_publication_contract",
    "receipt_from_mapping",
    "rank_workspace_development_fibres",
    "request_benchmark",
    "request_independent_review",
    "research_v4_conformance",
    "resolution_plan_from_mapping",
    "run_campaign",
    "run_campaign_cycle",
    "run_mechanic_receipts",
    "run_paper_structure_consensus",
    "run_problem",
    "run_problem_recursive",
    "saturation_surface",
    "select_context",
    "validate_manifest",
    "validate_q3_publication_contract",
]
