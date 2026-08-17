"""Regenerate the GLM-5.2 hidden-cause attribution report from raw records.

The merged 21/24 result is an immutable diagnosis seed. This module does not
call a model, does not rewrite residual errors, and cannot promote a transfer
result.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from orion.study.p5.freeze import ROOT_CAUSES, sha256_json


RESULTS_RELPATH = "papers/paper-05-self-orion/evidence/glm-5.2-attribution/results.jsonl"
RECEIPT_RELPATH = "papers/paper-05-self-orion/evidence/glm-5.2-attribution/REPRODUCTION_RECEIPT.json"
TABLE_RELPATH = "papers/paper-05-self-orion/evidence/TABLE_P5_3_HIDDEN_CAUSE_ATTRIBUTION.json"
CAMPAIGN_ID = "p5-glm-5.2-attribution-v1"
MODEL = "glm-5.2"

IMMUTABLE_RESIDUAL_ERRORS: tuple[dict[str, str], ...] = (
    {
        "case_id": "P5-HC-002",
        "gold": "RETRIEVAL_MISS",
        "attributed": "REPRESENTATION_GAP",
    },
    {
        "case_id": "P5-HC-012",
        "gold": "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
        "attributed": "IMPLEMENTATION_BUG",
    },
    {
        "case_id": "P5-HC-018",
        "gold": "REPRESENTATION_GAP",
        "attributed": "METHOD_BASIS_GAP",
    },
)


def load_raw_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        record = json.loads(raw_line)
        if not isinstance(record, Mapping):
            raise ValueError(f"results.jsonl line {line_number} must be an object")
        records.append(dict(record))
    if len(records) != 24:
        raise ValueError(f"expected 24 raw attribution records, found {len(records)}")
    return records


def _family_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for family in sorted(ROOT_CAUSES):
        family_records = [record for record in records if record["gold_root_cause"] == family]
        if not family_records:
            continue
        correct = sum(1 for record in family_records if record["gold_root_cause"] == record["attributed_root_cause"])
        total = len(family_records)
        recall = correct / total
        metrics[family] = {
            "recall": recall,
            "f1": recall,
            "cases": [record["case_id"] for record in family_records],
            "correct": correct,
            "total": total,
        }
    return metrics


def compute_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    transport_errors = sum(1 for record in records if record.get("error") not in (None, ""))
    correct = sum(
        1
        for record in records
        if record.get("error") in (None, "")
        and record["gold_root_cause"] == record["attributed_root_cause"]
    )
    incorrect = total - correct - transport_errors
    family_metrics = _family_metrics(records)
    macro_f1 = sum(item["f1"] for item in family_metrics.values()) / len(family_metrics)
    false_method_changes = [
        record
        for record in records
        if record["gold_root_cause"] == record["attributed_root_cause"]
        and record.get("intervention_prediction") == "NO"
        and record.get("error") in (None, "")
    ]
    confidence: dict[str, int] = {}
    for record in records:
        label = str(record["confidence"])
        confidence[label] = confidence.get(label, 0) + 1
    return {
        "total_cases": total,
        "correct_attributions": correct,
        "incorrect_attributions": incorrect,
        "errors": transport_errors,
        "accuracy": correct / total,
        "macro_f1": macro_f1,
        "false_method_change_rate": len(false_method_changes) / correct if correct else 0.0,
        "per_family_metrics": family_metrics,
        "confidence_distribution": confidence,
    }


def residual_errors(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    errors = [
        {
            "case_id": record["case_id"],
            "gold": record["gold_root_cause"],
            "attributed": record["attributed_root_cause"],
        }
        for record in records
        if record.get("error") in (None, "")
        and record["gold_root_cause"] != record["attributed_root_cause"]
    ]
    if errors != [dict(item) for item in IMMUTABLE_RESIDUAL_ERRORS]:
        raise ValueError("raw records no longer preserve the three immutable residual errors")
    return errors


def confusion_matrix(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    matrix: dict[str, dict[str, int]] = {}
    for record in records:
        gold = record["gold_root_cause"]
        attributed = f"attributed_{record['attributed_root_cause']}"
        family = matrix.setdefault(gold, {})
        family[attributed] = family.get(attributed, 0) + 1
    return matrix


def intervention_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"YES": 0, "NO": 0, "CANNOT_DETERMINE": 0}
    for record in records:
        prediction = record.get("intervention_prediction", "CANNOT_DETERMINE")
        if prediction not in counts:
            raise ValueError(f"unknown intervention_prediction: {prediction}")
        counts[prediction] += 1
    return counts


def _unsigned_receipt(records: list[dict[str, Any]], records_sha256: str) -> dict[str, Any]:
    metrics = compute_metrics(records)
    errors = residual_errors(records)
    return {
        "schema_version": "orion.p5.glm-attribution-reproduction.v1",
        "campaign_id": CAMPAIGN_ID,
        "model": MODEL,
        "records_path": RESULTS_RELPATH,
        "records_sha256": records_sha256,
        "metrics": {
            "total_cases": metrics["total_cases"],
            "correct_attributions": metrics["correct_attributions"],
            "incorrect_attributions": metrics["incorrect_attributions"],
            "errors": metrics["errors"],
            "accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"],
            "false_method_change_rate": metrics["false_method_change_rate"],
            "confidence_distribution": metrics["confidence_distribution"],
        },
        "residual_errors": errors,
        "empirical_authority": "ATTRIBUTION_DIAGNOSIS_ONLY",
        "promotion_terminal": None,
        "self_merge_authority": False,
        "notes": "Replay of archived raw records only. Does not execute a live campaign or authorize host promotion.",
    }


def reproduce_attribution_from_records(results_path: Path) -> dict[str, Any]:
    records = load_raw_records(results_path)
    records_sha256 = hashlib.sha256(results_path.read_bytes()).hexdigest()
    unsigned = _unsigned_receipt(records, records_sha256)
    receipt = dict(unsigned)
    receipt["receipt_sha256"] = sha256_json(unsigned)
    return receipt


def build_table_p5_3(results_path: Path) -> dict[str, Any]:
    records = load_raw_records(results_path)
    metrics = compute_metrics(records)
    return {
        "schema_version": "orion.p5.hidden-cause-attribution.v1",
        "paper_id": "P5",
        "issue": 282,
        "model": MODEL,
        "campaign_id": CAMPAIGN_ID,
        "evidence_files": [RESULTS_RELPATH, RECEIPT_RELPATH],
        "summary_metrics": {
            "total_cases": metrics["total_cases"],
            "correct_attributions": metrics["correct_attributions"],
            "incorrect_attributions": metrics["incorrect_attributions"],
            "errors": metrics["errors"],
            "accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"],
            "false_method_change_rate": metrics["false_method_change_rate"],
        },
        "confidence_distribution": metrics["confidence_distribution"],
        "per_family_metrics": metrics["per_family_metrics"],
        "confusion_matrix": confusion_matrix(records),
        "incorrect_cases": [
            {
                "case_id": record["case_id"],
                "gold": record["gold_root_cause"],
                "attributed": record["attributed_root_cause"],
                "confidence": record["confidence"],
            }
            for record in records
            if record["gold_root_cause"] != record["attributed_root_cause"]
        ],
        "intervention_predictions": intervention_counts(records),
        "empirical_authority": "ATTRIBUTION_DIAGNOSIS_ONLY",
        "limitations": (
            "Archived single-model attribution replay. Tables P5-2 and P5-4..P5-7 require a "
            "protected fresh-transfer campaign and remain CANNOT_CHECK."
        ),
    }


def write_reproduction_artifacts(repo_root: Path) -> dict[str, Any]:
    results_path = repo_root / RESULTS_RELPATH
    receipt = reproduce_attribution_from_records(results_path)
    table = build_table_p5_3(results_path)
    receipt_path = repo_root / RECEIPT_RELPATH
    table_path = repo_root / TABLE_RELPATH
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    table_path.write_text(json.dumps(table, indent=2) + "\n", encoding="utf-8")
    return receipt
