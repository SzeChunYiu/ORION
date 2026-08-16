from __future__ import annotations

from dataclasses import dataclass

from orion.benchmarks.discovery import run_discovery_known_world
from orion.benchmarks.external_evidence import (
    ExternalEvidenceManifest,
    assess_external_flagship,
    empty_external_manifest,
)
from orion.benchmarks.global_portrait import run_global_portrait_known_world
from orion.benchmarks.reconstruction import frozen_reconstruction_suite, run_hidden_shift_case
from orion.benchmarks.result import BenchmarkReport, BenchmarkStatus
from orion.benchmarks.self_orion import run_self_orion_known_world
from orion.benchmarks.verified_discovery import run_authority_laundering_suite


@dataclass(frozen=True)
class FlagshipEvidenceState:
    """Current evidence boundary for the five flagship papers.

    Local reports are deterministic known-world/hostile falsifiers. External
    reports are derived only from content/lineage-bound external evidence
    records. A green local suite therefore never becomes a publication claim by
    aggregation or caller-supplied booleans.
    """

    local_reports: tuple[BenchmarkReport, ...]
    external_reports: tuple[BenchmarkReport, ...]

    @property
    def local_all_pass(self) -> bool:
        return bool(self.local_reports) and all(item.passed for item in self.local_reports)

    @property
    def external_all_pass(self) -> bool:
        return bool(self.external_reports) and all(item.passed for item in self.external_reports)

    @property
    def publication_ready(self) -> bool:
        return self.local_all_pass and self.external_all_pass

    @property
    def cannot_check_papers(self) -> tuple[str, ...]:
        return tuple(
            item.paper_id
            for item in self.external_reports
            if item.status is BenchmarkStatus.CANNOT_CHECK
        )


def run_local_flagship_suite() -> tuple[BenchmarkReport, ...]:
    p1 = tuple(run_hidden_shift_case(case) for case in frozen_reconstruction_suite())
    return (
        *p1,
        run_discovery_known_world(),
        run_global_portrait_known_world(),
        run_authority_laundering_suite(),
        run_self_orion_known_world(),
    )


def current_external_evidence_boundary(
    manifest: ExternalEvidenceManifest | None = None,
) -> tuple[BenchmarkReport, ...]:
    """Derive the external boundary from an independently supplied manifest.

    The repository-only default is an empty manifest, so all five paper gates
    return CANNOT_CHECK rather than accepting declarations that an evaluator,
    baseline, hidden split or external result exists.
    """

    return assess_external_flagship(manifest or empty_external_manifest())


def current_flagship_evidence_state(
    manifest: ExternalEvidenceManifest | None = None,
) -> FlagshipEvidenceState:
    return FlagshipEvidenceState(
        local_reports=run_local_flagship_suite(),
        external_reports=current_external_evidence_boundary(manifest),
    )


__all__ = [
    "FlagshipEvidenceState",
    "current_external_evidence_boundary",
    "current_flagship_evidence_state",
    "run_local_flagship_suite",
]
