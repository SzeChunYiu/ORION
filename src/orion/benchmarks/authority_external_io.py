from __future__ import annotations

import json
from pathlib import Path

from .authority_external import (
    FROZEN_AUTHORITY_BASELINE_IDS,
    AuthorityBenchmarkMetrics,
    AuthorityBenchmarkPanel,
    AuthoritySystemObservation,
)


AUTHORITY_BENCHMARK_PANEL_SCHEMA = "AuthorityBenchmarkPanel.v1"


def _metrics_to_dict(metrics: AuthorityBenchmarkMetrics) -> dict[str, object]:
    return {
        "claim_correct": metrics.claim_correct,
        "claim_total": metrics.claim_total,
        "source_attribution_correct": metrics.source_attribution_correct,
        "source_attribution_total": metrics.source_attribution_total,
        "support_contradiction_tp": metrics.support_contradiction_tp,
        "support_contradiction_fp": metrics.support_contradiction_fp,
        "support_contradiction_fn": metrics.support_contradiction_fn,
        "conflation_detected": metrics.conflation_detected,
        "conflation_total": metrics.conflation_total,
        "substitution_detected": metrics.substitution_detected,
        "substitution_total": metrics.substitution_total,
        "tamper_leakage_detected": metrics.tamper_leakage_detected,
        "tamper_leakage_total": metrics.tamper_leakage_total,
        "false_promotions": metrics.false_promotions,
        "promotion_opportunities": metrics.promotion_opportunities,
        "correct_cannot_check": metrics.correct_cannot_check,
        "cannot_check_opportunities": metrics.cannot_check_opportunities,
        "resource_units": metrics.resource_units,
        "latency_seconds": metrics.latency_seconds,
    }


def _observation_to_dict(observation: AuthoritySystemObservation) -> dict[str, object]:
    return {
        "system_id": observation.system_id,
        "metrics": _metrics_to_dict(observation.metrics),
        "evidence_artifact_id": observation.evidence_artifact_id,
        "evidence_artifact_hash": observation.evidence_artifact_hash,
        "subject_revision_hash": observation.subject_revision_hash,
        "evaluator_artifact_hash": observation.evaluator_artifact_hash,
        "evaluation_epoch_id": observation.evaluation_epoch_id,
        "split_id": observation.split_id,
        "producer_process_lineage_hash": observation.producer_process_lineage_hash,
        "verifier_process_lineage_hash": observation.verifier_process_lineage_hash,
        "evaluator_frozen_before_candidate": observation.evaluator_frozen_before_candidate,
        "fresh_split": observation.fresh_split,
    }


def authority_benchmark_panel_to_dict(panel: AuthorityBenchmarkPanel) -> dict[str, object]:
    return {
        "schema": AUTHORITY_BENCHMARK_PANEL_SCHEMA,
        "panel_id": panel.panel_id,
        "panel_artifact_hash": panel.artifact_hash,
        "subject_revision_hash": panel.subject_revision_hash,
        "evaluator_artifact_hash": panel.evaluator_artifact_hash,
        "evaluation_epoch_id": panel.evaluation_epoch_id,
        "resource_budget_units": panel.resource_budget_units,
        "frozen_baseline_ids": list(FROZEN_AUTHORITY_BASELINE_IDS),
        "orion": _observation_to_dict(panel.orion),
        "baselines": [_observation_to_dict(item) for item in panel.baselines],
    }


def write_authority_benchmark_panel(panel: AuthorityBenchmarkPanel, path: Path | str) -> None:
    Path(path).write_text(
        json.dumps(authority_benchmark_panel_to_dict(panel), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _metrics(raw: object) -> AuthorityBenchmarkMetrics:
    if not isinstance(raw, dict):
        raise ValueError("authority benchmark metrics must be a JSON object")
    return AuthorityBenchmarkMetrics(**raw)


def _observation(raw: object) -> AuthoritySystemObservation:
    if not isinstance(raw, dict):
        raise ValueError("authority benchmark observation must be a JSON object")
    return AuthoritySystemObservation(
        system_id=raw["system_id"],
        metrics=_metrics(raw["metrics"]),
        evidence_artifact_id=raw["evidence_artifact_id"],
        evidence_artifact_hash=raw["evidence_artifact_hash"],
        subject_revision_hash=raw["subject_revision_hash"],
        evaluator_artifact_hash=raw["evaluator_artifact_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        split_id=raw["split_id"],
        producer_process_lineage_hash=raw["producer_process_lineage_hash"],
        verifier_process_lineage_hash=raw["verifier_process_lineage_hash"],
        evaluator_frozen_before_candidate=raw["evaluator_frozen_before_candidate"],
        fresh_split=raw["fresh_split"],
    )


def load_authority_benchmark_panel(path: Path | str) -> AuthorityBenchmarkPanel:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != AUTHORITY_BENCHMARK_PANEL_SCHEMA:
        raise ValueError(f"authority benchmark schema must be {AUTHORITY_BENCHMARK_PANEL_SCHEMA}")
    if tuple(raw.get("frozen_baseline_ids", ())) != FROZEN_AUTHORITY_BASELINE_IDS:
        raise ValueError("authority benchmark frozen baseline identities changed")
    baselines = raw.get("baselines")
    if not isinstance(baselines, list):
        raise ValueError("authority benchmark baselines must be a JSON array")
    panel = AuthorityBenchmarkPanel(
        panel_id=raw["panel_id"],
        subject_revision_hash=raw["subject_revision_hash"],
        evaluator_artifact_hash=raw["evaluator_artifact_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        resource_budget_units=raw["resource_budget_units"],
        orion=_observation(raw["orion"]),
        baselines=tuple(_observation(item) for item in baselines),
    )
    if raw.get("panel_artifact_hash") != panel.artifact_hash:
        raise ValueError("authority benchmark panel artifact hash mismatch")
    return panel


__all__ = [
    "AUTHORITY_BENCHMARK_PANEL_SCHEMA",
    "authority_benchmark_panel_to_dict",
    "load_authority_benchmark_panel",
    "write_authority_benchmark_panel",
]
