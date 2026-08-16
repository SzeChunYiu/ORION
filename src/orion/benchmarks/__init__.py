"""Flagship paper falsification benchmarks.

These modules are evaluation surfaces, not scientific authority. A passing
known-world or hostile test may support an implementation claim but cannot by
itself establish external novelty or empirical superiority.
"""

from .flagship import (
    FlagshipEvidenceState,
    current_external_evidence_boundary,
    current_flagship_evidence_state,
    run_local_flagship_suite,
)
from .result import BenchmarkReport, BenchmarkStatus

__all__ = [
    "BenchmarkReport",
    "BenchmarkStatus",
    "FlagshipEvidenceState",
    "current_external_evidence_boundary",
    "current_flagship_evidence_state",
    "run_local_flagship_suite",
]
