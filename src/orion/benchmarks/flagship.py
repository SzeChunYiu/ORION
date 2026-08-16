from __future__ import annotations

from dataclasses import dataclass

from orion.benchmarks.discovery import external_discovery_gate, run_discovery_known_world
from orion.benchmarks.external import external_portrait_gate, external_reconstruction_gate
from orion.benchmarks.global_portrait import run_global_portrait_known_world
from orion.benchmarks.reconstruction import frozen_reconstruction_suite, run_hidden_shift_case
from orion.benchmarks.result import BenchmarkReport, BenchmarkStatus
from orion.benchmarks.self_orion import external_self_orion_gate, run_self_orion_known_world
from orion.benchmarks.verified_discovery import (
    external_authority_gate,
    run_authority_laundering_suite,
)


@dataclass(frozen=True)
class FlagshipEvidenceState:
    """Current evidence boundary for the five flagship papers.

    Local reports are deterministic known-world/hostile falsifiers. External
    reports are the stronger publication gates. A green local suite therefore
    never becomes a publication claim by aggregation.
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


def current_external_evidence_boundary() -> tuple[BenchmarkReport, ...]:
    """What remains unearned in this repository-only environment."""

    return (
        external_reconstruction_gate(
            hidden_representation_or_domain=True,
            matched_static_workflow_baseline=False,
            matched_tree_search_baseline=False,
            resource_matched=False,
            responsibility_labels_hidden=False,
            fresh_cases=False,
            root_success_better_than_baselines=None,
            unnecessary_reframe_not_worse=None,
        ),
        external_discovery_gate(
            benchmark_name="ResearchArena/AutoResearchBench/MetaSyn-live",
            complete_gold=True,
            matched_baseline=False,
            frozen_provider_trace=False,
            system_beats_baseline=None,
        ),
        external_portrait_gate(
            at_least_three_domains=True,
            multiple_operationalizations=True,
            source_projection_gold=False,
            mapping_gold=False,
            long_context_baseline_run=False,
            rag_translation_baseline_run=False,
            flat_schema_baseline_run=False,
            nlp_ablation_run=False,
            false_integration_better_than_baselines=None,
            source_recoverability_not_worse=None,
        ),
        external_authority_gate(
            source_attribution_benchmark_run=False,
            search_time_contamination_audited=False,
            evaluator_locked=False,
            heldout_access_logged=False,
            matched_nearest_work_baseline_run=False,
            false_promotion_better_than_baseline=None,
        ),
        external_self_orion_gate(
            matched_self_edit_baseline_run=False,
            matched_agent_design_baseline_run=False,
            failure_causes_hidden_from_candidate=False,
            fresh_transfer_split=False,
            evaluator_frozen_before_candidate=False,
            negative_history_complete=False,
            protected_path_access_logged=False,
            root_improvement_over_baselines=None,
        ),
    )


def current_flagship_evidence_state() -> FlagshipEvidenceState:
    return FlagshipEvidenceState(
        local_reports=run_local_flagship_suite(),
        external_reports=current_external_evidence_boundary(),
    )


__all__ = [
    "FlagshipEvidenceState",
    "current_external_evidence_boundary",
    "current_flagship_evidence_state",
    "run_local_flagship_suite",
]
