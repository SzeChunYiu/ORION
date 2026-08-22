#!/usr/bin/env python3
"""Check P6–P8 formal-to-runtime schema anchors against live ORION.

Run from repository root with:

    PYTHONPATH=src python papers/candidates/checkers/check_orion_schema_embedding_v1.py

This is a *schema correspondence* check. It does not prove exact P1–P5 decision
embedding or novelty. A failure means ORION_EXECUTABLE_EMBEDDING_V1.md plus its
V4 covariance erratum are stale and candidate formal mappings must reopen.
"""

from __future__ import annotations

from dataclasses import fields

from orion import registry
from orion.core.research_resolution import (
    ResearchNegativeResult,
    ResearchOutcomeKind,
    ResearchResolutionObligation,
    ResolutionAction,
)
from orion.mechanics.actions import ActionClass, MechanicAction, candidate_action_plan
from orion.mechanics.audit import MechanicAuditVerdict, audit_recursive
from orion.mechanics.dependencies import DependencyKind, DependencyRequirement
from orion.mechanics.invariants import InvariantKind, default_invariant_plan
from orion.mechanics.model import MechanicCell, MechanicDimension, MetricDirection


def field_names(cls: type) -> frozenset[str]:
    return frozenset(item.name for item in fields(cls))


def require_fields(cls: type, expected: set[str]) -> None:
    actual = field_names(cls)
    missing = expected - actual
    assert not missing, f"{cls.__name__} missing mapped fields: {sorted(missing)}"


def check_registry() -> None:
    assert registry.FRAMEWORK_VERSION == "0.3.10-shadow", (
        "framework version changed; refresh ORION_EXECUTABLE_EMBEDDING_V1.md and its covariance erratum"
    )
    assert registry.PAPER_SYNC_EPOCH == "2026-08-22-paper-framework-harness-covariance-v4"
    assert registry.CORE_STATE_COORDINATES == ("K", "W", "M")
    required_ops = {
        "FRAME.v1",
        "SEARCH.v1",
        "ABSORB.v1",
        "RECONSTRUCT.v1",
        "DETECT.v1",
        "DIAGNOSE.v1",
        "REFRAME.v1",
        "REOPEN.v1",
        "SATURATE_BOUNDED.v3",
    }
    assert required_ops <= set(registry.CORE_OPERATOR_IDS)
    required_substrate = {
        "MechanicCell.v1",
        "MechanicReceipt.v1",
        "TaskEpisode.v1",
        "MechanicTraceReceipt.v2",
        "MechanicGuard.v1",
        "AnswerRecord.v1",
        "ResearchResolutionObligation.v1",
        "ResearchNegativeResult.v1",
        "ScientificMeaningProjection.v1",
        "IgnoranceProjection.v1",
        "SelfOrionReadinessGate.v2",
        "DevelopmentIssue.v1",
        "EvolutionArchive.v1",
    }
    assert required_substrate <= set(registry.MECHANICS_SUBSTRATE_IDS)


def check_outcome_lifecycle() -> None:
    require_fields(
        ResearchResolutionObligation,
        {
            "obligation_id",
            "subject_id",
            "unresolved_class",
            "reason_codes",
            "required_object_ids",
            "next_actions",
            "attempt_ids",
            "blocker_ids",
            "bounded_stop_condition",
            "state",
            "outcome_kind",
            "grants_scientific_authority",
            "grants_novelty_authority",
            "grants_promotion_authority",
            "grants_global_task_stop_authority",
        },
    )
    require_fields(
        ResearchNegativeResult,
        {
            "result_id",
            "subject_id",
            "negative_kind",
            "evidence_ids",
            "reason_codes",
            "dispositions",
            "outcome_kind",
            "grants_scientific_authority",
            "grants_novelty_authority",
            "grants_promotion_authority",
            "grants_global_task_stop_authority",
        },
    )
    assert {item.value for item in ResearchOutcomeKind} == {
        "POSITIVE",
        "NEGATIVE",
        "UNRESOLVED",
    }
    assert ResolutionAction.TASK_STOP.value == "TASK_STOP"


def check_mechanic_cell() -> None:
    require_fields(
        MechanicCell,
        {
            "mechanic_id",
            "purpose",
            "scope",
            "input_ids",
            "output_ids",
            "handoff_fields",
            "state_ids",
            "observable_ids",
            "action_ids",
            "transition_semantics",
            "mathematical_semantics",
            "invariant_ids",
            "constraint_ids",
            "objective_ids",
            "metrics",
            "optimization_rules",
            "uncertainty_semantics",
            "resource_coordinates",
            "failure_signatures",
            "falsifiers",
            "diagnosis_rules",
            "storage_contracts",
            "provenance_contracts",
            "verification_contracts",
            "authority_boundaries",
            "engineering_contracts",
            "dependency_ids",
            "external_dependency_contract_ids",
            "child_mechanic_ids",
            "reopen_triggers",
            "search_coverage_obligations",
            "parent_domain_hypotheses",
            "saturation_criteria",
            "empirical_open_coordinates",
            "provisional_dimensions",
            "waivers",
        },
    )
    required_dimensions = {
        "STATE",
        "OBSERVABILITY",
        "ACTIONS",
        "TRANSITION_MODEL",
        "INVARIANTS",
        "FAILURE",
        "PROVENANCE",
        "VERIFICATION",
        "AUTHORITY_SECURITY",
        "DEPENDENCIES",
        "REOPEN",
        "SEARCH_COVERAGE",
        "SATURATION",
    }
    assert required_dimensions <= {item.value for item in MechanicDimension}
    assert MetricDirection.NON_COMPENSATORY_GATE.value == "NON_COMPENSATORY_GATE"


def check_actions() -> None:
    require_fields(
        MechanicAction,
        {
            "action_id",
            "mechanic_id",
            "action_class",
            "description",
            "preconditions",
            "authority_effect",
            "side_effect_semantics",
            "failure_semantics",
        },
    )
    assert {
        "INSPECT",
        "INFORMATION_ACQUISITION",
        "TRANSFORM",
        "CONTROL",
        "VERIFY",
        "EXTERNAL_EFFECT",
        "FAIL_CLOSED",
    } <= {item.value for item in ActionClass}

    search = MechanicCell("SEARCH.v1", "search", "fixture")
    search_actions = candidate_action_plan(search)
    stop_actions = [item for item in search_actions if item.action_id.endswith(":stop-route")]
    assert len(stop_actions) == 1
    assert "without implying task saturation" in stop_actions[0].description
    assert all("No action directly mints scientific authority" in item.authority_effect for item in search_actions)

    reopen = MechanicCell("REOPEN.v1", "reopen", "fixture")
    reopen_suffixes = {item.action_id.rsplit(":", 1)[-1] for item in candidate_action_plan(reopen)}
    assert {"compute-dependent-set", "stale-closure", "reopen-fibres"} <= reopen_suffixes


def check_dependencies() -> None:
    require_fields(
        DependencyRequirement,
        {
            "dependency_id",
            "mechanic_id",
            "kind",
            "required",
            "identity_binding",
            "precondition",
            "failure_propagation",
            "fallback_semantics",
            "integrity_provenance_requirement",
        },
    )
    assert {
        "MECHANIC",
        "PROVIDER",
        "EVALUATOR",
        "DATA",
        "TOOL",
        "SCHEMA",
        "EVIDENCE",
        "RESOURCE",
        "EXTERNAL_SYSTEM",
    } <= {item.value for item in DependencyKind}


def check_invariants() -> None:
    required_kinds = {
        "AUTHORITY",
        "RELATION",
        "HISTORY",
        "EVIDENCE",
        "SATURATION",
        "REOPEN",
        "EVALUATOR",
        "UNCERTAINTY",
        "EXECUTION",
        "ROOT_PROGRESS",
        "RESOURCE",
        "FAILURE_LEARNING",
    }
    assert required_kinds <= {item.value for item in InvariantKind}

    cell = MechanicCell("fixture.v1", "fixture", "embedding-check")
    plan = default_invariant_plan(cell)
    by_suffix = {item.invariant_id.rsplit(":", 1)[-1]: item for item in plan.invariants}
    required_suffixes = {
        "generation-non-authority",
        "typed-non-escalation",
        "negative-history-monotone",
        "missing-evidence-honesty",
        "lineage-independence",
        "residual-reopening",
        "evaluator-separation",
        "bounded-closure-honesty",
        "state-transition-only",
        "root-progress-transport",
        "resource-is-not-closure",
        "failure-no-self-promotion",
    }
    assert required_suffixes <= set(by_suffix)
    assert "CANNOT_CHECK" in by_suffix["missing-evidence-honesty"].statement
    assert "minimal affected fibre" in by_suffix["residual-reopening"].violation_semantics
    assert "never bounded closure" in by_suffix["resource-is-not-closure"].statement


def check_recursive_audit() -> None:
    a = MechanicCell(
        "A.v1",
        "A",
        "fixture",
        child_mechanic_ids=("B.v1",),
    )
    b = MechanicCell(
        "B.v1",
        "B",
        "fixture",
        dependency_ids=("A.v1",),
    )
    report = audit_recursive({"A.v1": a, "B.v1": b}, "A.v1")
    assert report.mixed_cycle_paths
    assert not report.bounded_ready
    assert {item.value for item in MechanicAuditVerdict} >= {
        "READY_FOR_BENCHMARK",
        "OPEN",
        "CANNOT_CHECK",
    }


def main() -> int:
    check_registry()
    check_outcome_lifecycle()
    check_mechanic_cell()
    check_actions()
    check_dependencies()
    check_invariants()
    check_recursive_audit()
    print("ORION P6-P8 schema embedding V1 + V4 covariance: PASS")
    print(f"  framework: {registry.FRAMEWORK_VERSION}")
    print(f"  paper sync epoch: {registry.PAPER_SYNC_EPOCH}")
    print("  core K/W/M + operator/substrate anchors: confirmed")
    print("  unresolved/negative outcome lifecycle anchors: confirmed")
    print("  MechanicCell formal-field anchors: confirmed")
    print("  action/effect/authority boundary anchors: confirmed")
    print("  dependency/provenance anchors: confirmed")
    print("  invariant/non-compensation/reopen/CANNOT_CHECK anchors: confirmed")
    print("  recursive mixed-cycle audit surface: confirmed")
    print("  exact P1-P5 decision embedding: NOT CHECKED BY THIS SCRIPT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
