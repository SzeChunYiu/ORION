"""Flagship paper falsification benchmarks.

These modules are evaluation surfaces, not scientific authority. A passing
known-world or hostile test may support an implementation claim but cannot by
itself establish external novelty or empirical superiority.
"""

from .authority_external import (
    FROZEN_AUTHORITY_BASELINE_IDS,
    AuthorityBenchmarkAssessment,
    AuthorityBenchmarkMetrics,
    AuthorityBenchmarkPanel,
    AuthorityBenchmarkStatus,
    AuthoritySystemObservation,
    assess_authority_benchmark,
)
from .external_evidence import (
    ExternalCriterion,
    ExternalEvidenceManifest,
    ExternalEvidenceRecord,
    ExternalEvidenceStatus,
    assess_external_flagship,
    assess_external_paper,
    empty_external_manifest,
)
from .flagship import (
    FlagshipEvidenceState,
    current_external_evidence_boundary,
    current_flagship_evidence_state,
    run_local_flagship_suite,
)
from .result import BenchmarkReport, BenchmarkStatus

__all__ = [
    "AuthorityBenchmarkAssessment",
    "AuthorityBenchmarkMetrics",
    "AuthorityBenchmarkPanel",
    "AuthorityBenchmarkStatus",
    "AuthoritySystemObservation",
    "BenchmarkReport",
    "BenchmarkStatus",
    "ExternalCriterion",
    "ExternalEvidenceManifest",
    "ExternalEvidenceRecord",
    "ExternalEvidenceStatus",
    "FROZEN_AUTHORITY_BASELINE_IDS",
    "FlagshipEvidenceState",
    "assess_authority_benchmark",
    "assess_external_flagship",
    "assess_external_paper",
    "current_external_evidence_boundary",
    "current_flagship_evidence_state",
    "empty_external_manifest",
    "run_local_flagship_suite",
]
