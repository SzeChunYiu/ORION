"""Machine-readable serialization of the frozen Phase-3 protocol.

Mirrors :mod:`orion.self_orion.phase2_io`: the frozen protocol content (task
class, governance contract, baseline, metrics, statistics policy, escalation
conditions) is code-owned and is only ever *emitted*.  The loader accepts host
bindings only, so a JSON file cannot silently rewrite the task class or retune
the statistics after outcomes are visible.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orion.self_orion.phase3_preflight import (
    HOSTILE_ATTACK_IDS,
    PHASE3_PROTOCOL_ID,
    PHASE3_PROTOCOL_VERSION,
    UNBOUND_DIGEST,
    UNBOUND_IDENTITY,
    Phase3AuthorityBoundary,
    Phase3ProtocolFreeze,
)

PROTOCOL_SCHEMA = "Phase3ProtocolFreeze.v1"
BINDING_SCHEMA = "Phase3HostBinding.v1"

DEFAULT_BOUNDARY_ID = "phase3:authority-boundary:prefreeze-v1"


def _require_mapping(value: object, *, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be a JSON object")
    return value


def _require_text(value: object, *, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a JSON string")
    return value


def phase3_protocol_freeze_to_dict(freeze: Phase3ProtocolFreeze) -> dict[str, object]:
    """Serialize the whole frozen protocol, bindings included."""

    boundary = freeze.authority_boundary
    return {
        "schema": PROTOCOL_SCHEMA,
        "protocol_id": freeze.protocol_id,
        "protocol_version": freeze.protocol_version,
        "blocked_on_issue": 76,
        "grants_operating_authority": False,
        "sampling_epoch_id": freeze.sampling_epoch_id,
        "issue_pool_fingerprint": freeze.issue_pool_fingerprint,
        "task_class": {
            "rule_id": freeze.task_class.rule_id,
            "included_kinds": [item.value for item in freeze.task_class.included_kinds],
            "excluded_kinds": [item.value for item in freeze.task_class.excluded_kinds],
            "inclusion_rules": list(freeze.task_class.inclusion_rules),
            "exclusion_rules": list(freeze.task_class.exclusion_rules),
            "preserve_unresolved_tasks": freeze.task_class.preserve_unresolved_tasks,
            "preserve_failed_tasks": freeze.task_class.preserve_failed_tasks,
        },
        "governance": {
            "contract_id": freeze.governance.contract_id,
            "orion_owned": [item.value for item in freeze.governance.orion_owned],
            "worker_rights": [item.value for item in freeze.governance.worker_rights],
            "worker_forbidden": [item.value for item in freeze.governance.worker_forbidden],
            "valid_terminal_states": [
                item.value for item in freeze.governance.valid_terminal_states
            ],
            "isolated_content_addressed_candidate_state": (
                freeze.governance.isolated_content_addressed_candidate_state
            ),
            "acceptance_requires_replay": freeze.governance.acceptance_requires_replay,
            "acceptance_requires_independent_fresh_transfer": (
                freeze.governance.acceptance_requires_independent_fresh_transfer
            ),
            "acceptance_requires_protected_assurance": (
                freeze.governance.acceptance_requires_protected_assurance
            ),
            "rejected_variants_are_immutable_history": (
                freeze.governance.rejected_variants_are_immutable_history
            ),
        },
        "baseline": {
            "baseline_id": freeze.baseline.baseline_id,
            "description": freeze.baseline.description,
            "matched_dimensions": [item.value for item in freeze.baseline.matched_dimensions],
            "retry_budget_per_task": freeze.baseline.retry_budget_per_task,
            "host_intervention_budget_per_task": (
                freeze.baseline.host_intervention_budget_per_task
            ),
            "permitted_external_help": list(freeze.baseline.permitted_external_help),
            "prohibited_in_both_arms": list(freeze.baseline.prohibited_in_both_arms),
        },
        "metrics": [
            {
                "metric_id": metric.metric_id,
                "description": metric.description,
                "direction": metric.direction.value,
                "role": metric.role.value,
                "unit": metric.unit,
            }
            for metric in freeze.metrics
        ],
        "uncertainty_policy": {
            "policy_id": freeze.uncertainty.policy_id,
            "primary_efficacy_metric_id": freeze.uncertainty.primary_efficacy_metric_id,
            "primary_safety_metric_id": freeze.uncertainty.primary_safety_metric_id,
            "minimum_cycles": freeze.uncertainty.minimum_cycles,
            "comparison_unit": freeze.uncertainty.comparison_unit,
            "interval_method_proportions": freeze.uncertainty.interval_method_proportions,
            "interval_method_differences": freeze.uncertainty.interval_method_differences,
            "bootstrap_resamples": freeze.uncertainty.bootstrap_resamples,
            "alpha": freeze.uncertainty.alpha,
            "multiplicity_correction": freeze.uncertainty.multiplicity_correction,
            "minimum_effect_size_primary": freeze.uncertainty.minimum_effect_size_primary,
            "safety_non_inferiority_margin": freeze.uncertainty.safety_non_inferiority_margin,
            "interim_analysis_permitted": freeze.uncertainty.interim_analysis_permitted,
            "stopping_rule": freeze.uncertainty.stopping_rule,
        },
        "authority_boundary": {
            "boundary_id": boundary.boundary_id,
            "phase2_terminal_subject_revision_hash": (
                boundary.phase2_terminal_subject_revision_hash
            ),
            "phase2_evidence_receipt_hash": boundary.phase2_evidence_receipt_hash,
            "phase2_binding_complete": boundary.phase2_binding_complete,
            "external_promotion_authority_id": boundary.external_promotion_authority_id,
            "protected_custody_lineage_hash": boundary.protected_custody_lineage_hash,
            "escalation_conditions": [item.value for item in boundary.escalation_conditions],
            "escalation_conditions_frozen_before_outcome_access": (
                boundary.escalation_conditions_frozen_before_outcome_access
            ),
            "grants_self_merge": boundary.grants_self_merge,
            "grants_evaluator_mutation": boundary.grants_evaluator_mutation,
            "grants_holdout_access": boundary.grants_holdout_access,
            "grants_policy_mutation": boundary.grants_policy_mutation,
            "grants_phase_transition": boundary.grants_phase_transition,
        },
        "hostile_attack_ids": list(HOSTILE_ATTACK_IDS),
    }


def write_phase3_protocol_freeze(freeze: Phase3ProtocolFreeze, path: Path | str) -> None:
    Path(path).write_text(
        json.dumps(phase3_protocol_freeze_to_dict(freeze), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def phase3_host_binding_to_dict(freeze: Phase3ProtocolFreeze) -> dict[str, object]:
    """Serialize only the host-owned identities."""

    boundary = freeze.authority_boundary
    return {
        "schema": BINDING_SCHEMA,
        "protocol_id": freeze.protocol_id,
        "protocol_version": freeze.protocol_version,
        "boundary_id": boundary.boundary_id,
        "sampling_epoch_id": freeze.sampling_epoch_id,
        "issue_pool_fingerprint": freeze.issue_pool_fingerprint,
        "phase2_terminal_subject_revision_hash": boundary.phase2_terminal_subject_revision_hash,
        "phase2_evidence_receipt_hash": boundary.phase2_evidence_receipt_hash,
        "external_promotion_authority_id": boundary.external_promotion_authority_id,
        "protected_custody_lineage_hash": boundary.protected_custody_lineage_hash,
    }


def write_phase3_host_binding(freeze: Phase3ProtocolFreeze, path: Path | str) -> None:
    Path(path).write_text(
        json.dumps(phase3_host_binding_to_dict(freeze), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_phase3_host_binding(path: Path | str) -> Phase3ProtocolFreeze:
    """Load host bindings onto the code-owned frozen protocol.

    Task class, governance contract, baseline, metrics and statistics policy are
    never read from the file; only identities a host is entitled to bind are.
    """

    raw = _require_mapping(
        json.loads(Path(path).read_text(encoding="utf-8")), where="phase3 host binding"
    )
    if raw.get("schema") != BINDING_SCHEMA:
        raise ValueError(f"phase3 host binding schema must be {BINDING_SCHEMA}")
    # The schema name identifies the file format, not the protocol the bindings
    # belong to. A binding written against a future protocol revision must not
    # be silently applied to v1, so protocol identity is checked too.
    if raw.get("protocol_id", PHASE3_PROTOCOL_ID) != PHASE3_PROTOCOL_ID:
        raise ValueError(f"phase3 host binding protocol_id must be {PHASE3_PROTOCOL_ID}")
    if raw.get("protocol_version", PHASE3_PROTOCOL_VERSION) != PHASE3_PROTOCOL_VERSION:
        raise ValueError(
            f"phase3 host binding protocol_version must be {PHASE3_PROTOCOL_VERSION}"
        )

    boundary = Phase3AuthorityBoundary(
        boundary_id=_require_text(
            raw.get("boundary_id", DEFAULT_BOUNDARY_ID), field="boundary_id"
        ),
        phase2_terminal_subject_revision_hash=_require_text(
            raw.get("phase2_terminal_subject_revision_hash", UNBOUND_DIGEST),
            field="phase2_terminal_subject_revision_hash",
        ),
        phase2_evidence_receipt_hash=_require_text(
            raw.get("phase2_evidence_receipt_hash", UNBOUND_DIGEST),
            field="phase2_evidence_receipt_hash",
        ),
        external_promotion_authority_id=_require_text(
            raw.get("external_promotion_authority_id", UNBOUND_IDENTITY),
            field="external_promotion_authority_id",
        ),
        protected_custody_lineage_hash=_require_text(
            raw.get("protected_custody_lineage_hash", UNBOUND_DIGEST),
            field="protected_custody_lineage_hash",
        ),
    )
    return Phase3ProtocolFreeze(
        sampling_epoch_id=_require_text(
            raw.get("sampling_epoch_id", "phase3:epoch:unbound"), field="sampling_epoch_id"
        ),
        issue_pool_fingerprint=_require_text(
            raw.get("issue_pool_fingerprint", UNBOUND_DIGEST), field="issue_pool_fingerprint"
        ),
        authority_boundary=boundary,
    )


__all__ = [
    "BINDING_SCHEMA",
    "PROTOCOL_SCHEMA",
    "load_phase3_host_binding",
    "phase3_host_binding_to_dict",
    "phase3_protocol_freeze_to_dict",
    "write_phase3_host_binding",
    "write_phase3_protocol_freeze",
]
