from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from orion.core.solution import SolutionStatus

from .live_trial import ResearchTrialKind, ShadowLiveTrialReport


LIVE_TRIAL_REPORT_SCHEMA = "ShadowLiveTrialReport.v1"


def _document_hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _evidence_artifact_hash_from_raw(raw: dict[str, object]) -> str:
    """Reproduce ``ShadowLiveTrialReport.evidence_artifact_hash`` from JSON detail.

    This deliberately ignores summary-only/resource fields exactly as the live
    report's evidence hash does. A replay audit therefore cannot accept a
    stored evidence hash after the raw search/answer-use/mechanic trace changed,
    even if a caller recomputes the outer document hash.
    """

    comparisons = raw.get("comparisons")
    if not isinstance(comparisons, list):
        raise ValueError("live trial comparisons must be an array")

    canonical_comparisons: list[dict[str, object]] = []
    for comparison in comparisons:
        if not isinstance(comparison, dict):
            raise ValueError("live trial comparison must be a JSON object")
        search_observations = comparison.get("search_observations")
        mechanic_trace = comparison.get("mechanic_trace")
        if not isinstance(search_observations, list):
            raise ValueError("live trial comparison search_observations must be an array")
        if not isinstance(mechanic_trace, list):
            raise ValueError("live trial comparison mechanic_trace must be an array")

        canonical_search: list[dict[str, object]] = []
        for observation in search_observations:
            if not isinstance(observation, dict):
                raise ValueError("live trial search observation must be a JSON object")
            items = observation.get("items")
            if not isinstance(items, list):
                raise ValueError("live trial search observation items must be an array")
            canonical_items: list[dict[str, object]] = []
            for retrieved in items:
                if not isinstance(retrieved, dict):
                    raise ValueError("live trial retrieved item must be a JSON object")
                domain_ids = retrieved.get("domain_ids")
                if not isinstance(domain_ids, list):
                    raise ValueError("live trial retrieved domain_ids must be an array")
                canonical_items.append(
                    {
                        "item_id": retrieved["item_id"],
                        "content": retrieved["content"],
                        "source_uri": retrieved["source_uri"],
                        "domain_ids": list(domain_ids),
                    }
                )
            canonical_search.append(
                {
                    "query_id": observation["query_id"],
                    "query_text": observation["query_text"],
                    "route_id": observation["route_id"],
                    "route_kind": observation["route_kind"],
                    "domain_hint": observation.get("domain_hint"),
                    "limit": observation["limit"],
                    "items": canonical_items,
                }
            )

        canonical_trace: list[dict[str, object]] = []
        for event in mechanic_trace:
            if not isinstance(event, dict):
                raise ValueError("live trial mechanic trace event must be a JSON object")
            canonical_trace.append(
                {
                    "operator": event["operator"],
                    "summary": event["summary"],
                    "receipt_id": event["receipt_id"],
                    "mechanic_id": event["mechanic_id"],
                    "status": event["status"],
                    "action_ids": list(event["action_ids"]),
                    "evidence_ids": list(event["evidence_ids"]),
                    "residual_ids": list(event["residual_ids"]),
                    "failure_signature": list(event["failure_signature"]),
                    "handoff_values": [list(value) for value in event["handoff_values"]],
                    "provenance_ids": list(event["provenance_ids"]),
                }
            )

        canonical_comparisons.append(
            {
                "task_id": comparison["task_id"],
                "kind": comparison["kind"],
                "orion_status": comparison["orion_status"],
                "solution_evidence_ids": list(comparison["solution_evidence_ids"]),
                "absorbed_evidence_ids": list(comparison["absorbed_evidence_ids"]),
                "retrieved_but_unused_ids": list(comparison["retrieved_but_unused_ids"]),
                "retrieved_but_unabsorbed_ids": list(
                    comparison["retrieved_but_unabsorbed_ids"]
                ),
                "search_observations": canonical_search,
                "mechanic_trace": canonical_trace,
            }
        )

    payload = {
        "packet_id": raw["packet_id"],
        "packet_fingerprint": raw["packet_fingerprint"],
        "comparisons": canonical_comparisons,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def shadow_live_trial_report_to_dict(
    report: ShadowLiveTrialReport,
) -> dict[str, object]:
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
    payload = shadow_live_trial_report_to_dict(report)
    payload["document_hash"] = _document_hash(payload)
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


@dataclass(frozen=True)
class LoadedShadowLiveTrialReport:
    packet_id: str
    packet_fingerprint: str
    evidence_artifact_hash: str
    raw_search_trace_retained: bool
    all_resource_matched: bool
    all_failures_recordable: bool
    wide_task_count: int
    deep_task_count: int
    grants_self_promotion: bool
    comparison_statuses: tuple[SolutionStatus, ...]
    document_hash: str


def load_shadow_live_trial_report(path: Path | str) -> LoadedShadowLiveTrialReport:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != LIVE_TRIAL_REPORT_SCHEMA:
        raise ValueError(f"live trial report schema must be {LIVE_TRIAL_REPORT_SCHEMA}")
    recorded_hash = raw.pop("document_hash", None)
    if not isinstance(recorded_hash, str) or recorded_hash != _document_hash(raw):
        raise ValueError("live trial report document hash mismatch")
    for name in (
        "raw_search_trace_retained",
        "all_resource_matched",
        "all_failures_recordable",
        "grants_self_promotion",
    ):
        if type(raw.get(name)) is not bool:
            raise ValueError(f"live trial report {name} must be boolean")
    if raw["grants_self_promotion"]:
        raise ValueError("live trial report cannot grant self-promotion")
    comparisons = raw.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        raise ValueError("live trial report comparisons must be a non-empty array")

    statuses: list[SolutionStatus] = []
    kinds: list[ResearchTrialKind] = []
    derived_resource_matched = True
    derived_failures_recordable = True
    derived_raw_trace = True
    for item in comparisons:
        if not isinstance(item, dict):
            raise ValueError("live trial comparison must be a JSON object")
        status = SolutionStatus(item["orion_status"])
        kind = ResearchTrialKind(item["kind"])
        statuses.append(status)
        kinds.append(kind)
        if type(item.get("resource_matched")) is not bool:
            raise ValueError("live trial comparison resource_matched must be boolean")
        derived_resource_matched = derived_resource_matched and item["resource_matched"]
        root_episode_id = item.get("root_episode_id")
        derived_failures_recordable = derived_failures_recordable and (
            status is SolutionStatus.SOLVED_VERIFIED
            or isinstance(root_episode_id, str)
            and bool(root_episode_id.strip())
        )
        search_observations = item.get("search_observations")
        if not isinstance(search_observations, list):
            raise ValueError("live trial comparison search_observations must be an array")
        derived_raw_trace = derived_raw_trace and bool(search_observations)

    derived_wide = sum(kind is ResearchTrialKind.WIDE_LITERATURE for kind in kinds)
    derived_deep = sum(kind is ResearchTrialKind.DEEP_TARGET for kind in kinds)
    if raw["raw_search_trace_retained"] != derived_raw_trace:
        raise ValueError("live trial raw-search summary contradicts task records")
    if raw["all_resource_matched"] != derived_resource_matched:
        raise ValueError("live trial resource summary contradicts task records")
    if raw["all_failures_recordable"] != derived_failures_recordable:
        raise ValueError("live trial failure-history summary contradicts task records")
    if int(raw["wide_task_count"]) != derived_wide:
        raise ValueError("live trial wide-task count contradicts task records")
    if int(raw["deep_task_count"]) != derived_deep:
        raise ValueError("live trial deep-task count contradicts task records")

    derived_evidence_hash = _evidence_artifact_hash_from_raw(raw)
    recorded_evidence_hash = raw.get("evidence_artifact_hash")
    if (
        not isinstance(recorded_evidence_hash, str)
        or recorded_evidence_hash != derived_evidence_hash
    ):
        raise ValueError("live trial evidence artifact hash mismatch")

    return LoadedShadowLiveTrialReport(
        packet_id=raw["packet_id"],
        packet_fingerprint=raw["packet_fingerprint"],
        evidence_artifact_hash=derived_evidence_hash,
        raw_search_trace_retained=derived_raw_trace,
        all_resource_matched=derived_resource_matched,
        all_failures_recordable=derived_failures_recordable,
        wide_task_count=derived_wide,
        deep_task_count=derived_deep,
        grants_self_promotion=False,
        comparison_statuses=tuple(statuses),
        document_hash=recorded_hash,
    )


__all__ = [
    "LIVE_TRIAL_REPORT_SCHEMA",
    "LoadedShadowLiveTrialReport",
    "load_shadow_live_trial_report",
    "shadow_live_trial_report_to_dict",
    "write_shadow_live_trial_report",
]
