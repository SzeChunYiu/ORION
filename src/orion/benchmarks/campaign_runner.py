from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ablation_runner import (
    ABLATION_IDS,
    run_ablation,
    run_ablation_campaign,
    run_orion,
    run_orion_campaign,
)
from .authority_external import AuthorityBenchmarkMetrics
from .baseline_runner import (
    BASELINE_IDS,
    run_baseline,
    run_baseline_campaign,
    verdicts_to_metrics,
)


RESULT_RECORD_SCHEMA_VERSION = "orion.publication-result-record.v1"
RESULT_RECORD_SCHEMA = "RESULT_RECORD_SCHEMA_V1.json"

SYSTEM_CATEGORIES = ("baseline", "ablation", "orion")


def _sha256(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _manifest_hash(manifest_path: Path | str) -> str:
    """Content hash of a JSONL manifest (stable across formatting differences)."""
    raw_lines = [
        line.strip()
        for line in Path(manifest_path).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    return _sha256("\n".join(raw_lines))


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
        "false_negative_count": metrics.false_negative_count,
        "clean_positive_total": metrics.clean_positive_total,
        "resource_units": metrics.resource_units,
        "latency_seconds": metrics.latency_seconds,
    }


def _derive_verdict_fields(verdict: Any) -> dict[str, Any]:
    """Derive result-record satellite fields from a verdict object.

    `status`: PROMOTE -> PASS, BLOCK -> FAIL, CANNOT_CHECK -> CANNOT_CHECK.
    A campaign-level metrics object may be given instead of a verdict
    (the runner treats the whole campaign as one record), in which case
    the status is PASS when the metrics are complete and CANNOT_CHECK
    when incomplete.
    """
    if hasattr(verdict, "promoted"):
        if verdict.promoted:
            return {"status": "PASS", "authority_flags": {"promoted": True, "blocked": False, "cannot_check": False}}
        if verdict.blocked:
            return {"status": "FAIL", "authority_flags": {"promoted": False, "blocked": True, "cannot_check": False}}
        return {"status": "CANNOT_CHECK", "authority_flags": {"promoted": False, "blocked": False, "cannot_check": True}}
    if hasattr(verdict, "complete"):
        return {"status": "PASS" if verdict.complete else "CANNOT_CHECK", "authority_flags": {}}
    return {"status": "INVALID", "authority_flags": {}}


def make_result_record(
    *,
    paper_id: str,
    protocol_id: str,
    run_manifest_hash: str,
    system_id: str,
    task_id: str,
    task_family: str,
    seed: int,
    metrics: AuthorityBenchmarkMetrics | dict[str, object],
    cost: dict[str, float],
    status: str | None = None,
    failure_class: str | None = None,
    raw_artifact_hash: str | None = None,
    contamination: dict[str, Any] | None = None,
    authority_flags: dict[str, Any] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Build one result record conforming to RESULT_RECORD_SCHEMA_V1.json.

    `status` must be derived by the caller from the underlying verdict
    (PROMOTE -> PASS, BLOCK -> FAIL, CANNOT_CHECK -> CANNOT_CHECK). When
    omitted it falls back to the notionally-possible verbs above; passing it
    explicitly is required for per-verdict records so that FAIL/CANNOT_CHECK
    survive aggregation into metrics.

    The caller is responsible for the `raw_artifact_hash`; when omitted it is
    computed from the canonical JSON of the metrics+authority_flags payload
    (stable, deterministic).
    """
    if isinstance(metrics, AuthorityBenchmarkMetrics):
        metrics_dict = _metrics_to_dict(metrics)
    else:
        metrics_dict = {str(k): v for k, v in metrics.items() if isinstance(v, (int, float))}
    if status is None:
        status = _derive_verdict_fields(metrics)["status"]
    if authority_flags is None:
        authority_flags = _derive_verdict_fields(metrics)["authority_flags"]
    if raw_artifact_hash is None:
        payload = {"metrics": metrics_dict, "authority_flags": authority_flags or {}}
        raw_artifact_hash = _sha256(json.dumps(payload, sort_keys=True))
    return {
        "schema_version": RESULT_RECORD_SCHEMA_VERSION,
        "paper_id": paper_id,
        "protocol_id": protocol_id,
        "run_manifest_hash": run_manifest_hash,
        "result_id": _sha256(
            f"{paper_id}|{protocol_id}|{run_manifest_hash}|{system_id}|{task_id}|{seed}"
        ),
        "system_id": system_id,
        "task_id": task_id,
        "task_family": task_family,
        "seed": seed,
        "status": status,
        "metrics": metrics_dict,
        "cost": {
            "wallclock_seconds": float(cost.get("wallclock_seconds", 0.0)),
            "model_tokens": float(cost.get("model_tokens", 0.0)),
            "tool_calls": float(cost.get("tool_calls", 0.0)),
            "reported_currency_cost": float(cost.get("reported_currency_cost", 0.0)),
        },
        "failure_class": failure_class,
        "raw_artifact_hash": raw_artifact_hash,
        "contamination": contamination or {},
        "authority_flags": authority_flags or {},
        "notes": notes,
    }


def write_result_records(records: list[dict[str, Any]], path: Path | str) -> None:
    Path(path).write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
        encoding="utf-8",
    )


def load_result_records(path: Path | str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def _manifest_cases(manifest_path: Path | str) -> list[dict[str, Any]]:
    cases = []
    for line in Path(manifest_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cases.append(json.loads(line))
    return cases


def run_manifest_campaign(
    manifest_path: Path | str,
    *,
    paper_id: str,
    protocol_id: str,
    out_dir: Path | str | None = None,
    categories: tuple[str, ...] = SYSTEM_CATEGORIES,
    seed: int = 0,
) -> list[dict[str, Any]]:
    """Run a JSONL attack manifest through baselines, ablations, and ORION.

    Each manifest line is one attack case (ATTACK_CASE_SCHEMA_V1 shape).
    Returns one result record (RESULT_RECORD_SCHEMA_V1) per system per case.

    All systems share one `run_manifest_hash` derived from the manifest file
    content (so re-running over a mutated manifest changes every result_id).
    """
    if not set(categories).issubset(set(SYSTEM_CATEGORIES)):
        raise ValueError(f"unknown category in {categories!r}; expected {SYSTEM_CATEGORIES}")
    cases = _manifest_cases(manifest_path)
    if not cases:
        raise ValueError(f"manifest contains no attack cases: {manifest_path}")
    manifest_hash = _manifest_hash(manifest_path)
    out_dir = Path(out_dir) if out_dir else Path(manifest_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for system_id in BASELINE_IDS if "baseline" in categories else ():
        for case in cases:
            verdict = run_baseline(system_id, case)
            status = "PASS" if verdict.promoted else ("FAIL" if verdict.blocked else "CANNOT_CHECK")
            records.append(
                make_result_record(
                    paper_id=paper_id,
                    protocol_id=protocol_id,
                    run_manifest_hash=manifest_hash,
                    system_id=system_id,
                    task_id=case["case_id"],
                    task_family=verdict.task_family,
                    seed=seed,
                    metrics=verdicts_to_metrics((verdict,)),
                    cost={"wallclock_seconds": verdict.latency_seconds, "model_tokens": 0.0, "tool_calls": 0.0, "reported_currency_cost": 0.0},
                    status=status,
                    authority_flags={"promoted": verdict.promoted, "blocked": verdict.blocked, "cannot_check": verdict.cannot_check},
                    raw_artifact_hash=None,
                    notes="",
                )
            )

    for ablation_id in ABLATION_IDS if "ablation" in categories else ():
        for case in cases:
            verdict = run_ablation(ablation_id, case)
            status = "PASS" if verdict.promoted else ("FAIL" if verdict.blocked else "CANNOT_CHECK")
            records.append(
                make_result_record(
                    paper_id=paper_id,
                    protocol_id=protocol_id,
                    run_manifest_hash=manifest_hash,
                    system_id=f"orion+{ablation_id}",
                    task_id=case["case_id"],
                    task_family=verdict.task_family,
                    seed=seed,
                    metrics=verdicts_to_metrics((verdict,)),
                    cost={"wallclock_seconds": verdict.latency_seconds, "model_tokens": 0.0, "tool_calls": 0.0, "reported_currency_cost": 0.0},
                    status=status,
                    authority_flags={"promoted": verdict.promoted, "blocked": verdict.blocked, "cannot_check": verdict.cannot_check},
                    raw_artifact_hash=None,
                    notes="",
                )
            )

    if "orion" in categories:
        for case in cases:
            verdict = run_orion(case)
            status = "PASS" if verdict.promoted else ("FAIL" if verdict.blocked else "CANNOT_CHECK")
            records.append(
                make_result_record(
                    paper_id=paper_id,
                    protocol_id=protocol_id,
                    run_manifest_hash=manifest_hash,
                    system_id="orion",
                    task_id=case["case_id"],
                    task_family=verdict.task_family,
                    seed=seed,
                    metrics=verdicts_to_metrics((verdict,)),
                    cost={"wallclock_seconds": verdict.latency_seconds, "model_tokens": 0.0, "tool_calls": 0.0, "reported_currency_cost": 0.0},
                    status=status,
                    authority_flags={"promoted": verdict.promoted, "blocked": verdict.blocked, "cannot_check": verdict.cannot_check},
                    raw_artifact_hash=None,
                    notes="",
                )
            )

    records.sort(key=lambda r: (r["system_id"], r["task_id"]))
    write_result_records(records, out_dir / "result_records.jsonl")
    return records


__all__ = [
    "RESULT_RECORD_SCHEMA_VERSION",
    "RESULT_RECORD_SCHEMA",
    "SYSTEM_CATEGORIES",
    "load_result_records",
    "make_result_record",
    "run_manifest_campaign",
    "write_result_records",
]