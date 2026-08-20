"""Local host-tool bridge for canonical ORION research runs."""

from .broker import (
    BrokerLLMProvider,
    BrokerRetrievalProvider,
    BrokerVerificationProvider,
    CapabilityBroker,
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from .protocol import CapabilityRequest, CapabilityResult
from .runner import run_problem
from .workspace import ResearchWorkspace

__all__ = [
    "BrokerLLMProvider",
    "BrokerRetrievalProvider",
    "BrokerVerificationProvider",
    "CapabilityBroker",
    "CapabilityRequest",
    "CapabilityResult",
    "HostCapabilityFailed",
    "HostCapabilityRequired",
    "ResearchWorkspace",
    "run_problem",
]
