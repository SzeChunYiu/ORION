from __future__ import annotations

import json
from pathlib import Path

from .live_trial import ShadowLiveTrialReport


LIVE_TRIAL_REPORT_SCHEMA = "ShadowLiveTrialReport.v1"


def shadow_live_trial_report_to_dict(
    report: ShadowLiveTrialReport,
) -> dict[str, object]:
    """Canonical host-facing serialization of the complete Shadow trial report."""

    return {
        "schema": LIVE_TRIAL_REPORT_SCHEMA,
        "packet_id": report.packet_id,
        "packet_fingerprint": report.packet_fingerprint,
        "evidence_artifact_hash": report.evidence_artifact_hash,
        "raw_search_trace_retained": report.raw_search_trace_retained,
        "all_resource_matched": report.all_resource_matched,
        "all_failures_recordable": report.all_failures_recordable,
        "wide_task_count": report.wide_task_count,
        "deep_task_count": report.deep_task_count,
        "grants_self_promotion": report.grants_self_promotion,
        "boundary": report.boundary,
        "comparisons": [
            {
                "task_id": comparison.task_id,
                "kind": comparison.kind.value,
                "orion_status": comparison.orion_status.value,
                "orion_evidence_count": comparison.orion_evidence_count,
                "orion_residual_count": comparison.orion_residual_count,
                "orion_resource_units": comparison.orion_resource_units,
                "baseline_solved": comparison.baseline_solved,
                "baseline_evidence_count": comparison.baseline_evidence_count,
                "baseline_residual_count": comparison.baseline_residual_count,
                "baseline_resource_units": comparison.baseline_resource_units,
                "resource_matched": comparison.resource_matched,
                "required_evidence_recovered": comparison.required_evidence_recovered,
                "root_episode_id": comparison.root_episode_id,
                "mechanic_episode_ids": list(comparison.mechanic_episode_ids),
                "solution_evidence_ids": list(comparison.solution_evidence_ids),
                "absorbed_evidence_ids": list(comparison.absorbed_evidence_ids),
                "retrieved_but_unused_ids": list(comparison.retrieved_but_unused_ids),
                "retrieved_but_unabsorbed_ids": list(
                    comparison.retrieved_but_unabsorbed_ids
                ),
                "search_observations": [
                    {
                        "query_id": observation.query_id,
                        "query_text": observation.query_text,
                        "route_id": observation.route_id,
                        "route_kind": observation.route_kind,
                        "domain_hint": observation.domain_hint,
                        "limit": observation.limit,
                        "items": [
                            {
                                "item_id": item.item_id,
                                "content": item.content,
                                "source_uri": item.source_uri,
                                "domain_ids": list(item.domain_ids),
                            }
                            for item in observation.items
                        ],
                    }
                    for observation in comparison.search_observations
                ],
                "mechanic_trace": [
                    {
                        "operator": event.operator,
                        "summary": event.summary,
                        "receipt_id": event.receipt_id,
                        "mechanic_id": event.mechanic_id,
                        "status": event.status,
                        "action_ids": list(event.action_ids),
                        "evidence_ids": list(event.evidence_ids),
                        "residual_ids": list(event.residual_ids),
                        "failure_signature": list(event.failure_signature),
                        "handoff_values": [list(value) for value in event.handoff_values],
                        "provenance_ids": list(event.provenance_ids),
                    }
                    for event in comparison.mechanic_trace
                ],
            }
            for comparison in report.comparisons
        ],
    }


def write_shadow_live_trial_report(
    report: ShadowLiveTrialReport, path: Path | str
) -> None:
    """Persist the raw host trial artifact without reducing it to summary counts."""

    Path(path).write_text(
        json.dumps(shadow_live_trial_report_to_dict(report), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


__all__ = [
    "LIVE_TRIAL_REPORT_SCHEMA",
    "shadow_live_trial_report_to_dict",
    "write_shadow_live_trial_report",
]
