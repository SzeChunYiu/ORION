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
from .protocol import CapabilityRequest, CapabilityResult
from .recursive_runner import RecursiveRunLimits
from .recursive_budget_hardening import install_recursive_budget_hardening
from .recursive_cost_hardening import install_recursive_cost_hardening
from .recursive_experience_binding import (
    WorkspaceRecursiveLLMResearchReasoner,
    install_workspace_recursive_reasoner,
)
from .recursive_director_integration import install_research_director_integration
from .recursive_runner import run_problem_recursive
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
    "ContextCandidate",
    "ContextSelection",
    "ExecutionMode",
    "HostCapabilityFailed",
    "HostCapabilityRequired",
    "ProtectedReference",
    "RecursiveRunLimits",
    "ResearchWorkspace",
    "WorkspaceRecursiveLLMResearchReasoner",
    "atom_calculus_surface",
    "compile_workspace_development_fibre",
    "decide_campaign",
    "execution_coverage",
    "initialize_campaign",
    "install_governance_hardening",
    "install_recursive_budget_hardening",
    "install_recursive_cost_hardening",
    "install_research_director_integration",
    "install_workspace_recursive_reasoner",
    "mechanic_catalog",
    "mechanic_detail",
    "mechanics_coverage",
    "method_fibre_surface",
    "navigate_mechanics",
    "rank_workspace_development_fibres",
    "request_benchmark",
    "request_independent_review",
    "run_campaign",
    "run_campaign_cycle",
    "run_mechanic_receipts",
    "run_problem",
    "run_problem_recursive",
    "saturation_surface",
    "select_context",
    "validate_manifest",
]
