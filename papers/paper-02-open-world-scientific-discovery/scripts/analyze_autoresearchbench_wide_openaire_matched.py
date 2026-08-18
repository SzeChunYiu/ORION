#!/usr/bin/env python3
"""Apply the prospectively frozen P2 Wide matched-campaign analysis.

The pinned upstream evaluator remains the authority for official Wide aggregate
metrics.  This script adds the predeclared distinct-question paired inference and
validity/terminal rule; it never rescans gold or rewrites candidate outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

SYSTEM_IDS = (
    "wide_dual_backend_balanced",
    "wide_dual_backend_governed",
    "wide_dual_backend_direct_first",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: row is not an object")
            rows.append(value)
    return rows


def pass0_by_question_last_write(evaluation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Mirror the frozen distinct-question inferential unit with last-write rows."""

    mapping: dict[str, dict[str, Any]] = {}
    records = evaluation.get("per_record_results")
    if not isinstance(records, list):
        raise ValueError("official evaluator output missing per_record_results")
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("official evaluator record is not an object")
        question = str(record.get("question") or "").strip()
        if not question:
            continue
        passes = record.get("pass_results")
        if not isinstance(passes, list):
            raise ValueError("official evaluator record missing pass_results")
        pass0 = next((item for item in passes if isinstance(item, dict) and int(item.get("pass_id", 0)) == 0), None)
        if pass0 is None:
            raise ValueError("official evaluator record has no pass 0")
        mapping[question] = pass0
    return mapping


def percentile(sorted_values: list[float], probability: float) -> float:
    """Linear-interpolated percentile over already-sorted finite values."""

    if not sorted_values:
        raise ValueError("cannot take percentile of empty sample")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability out of range")
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def paired_bootstrap(differences: list[float], *, resamples: int, seed: int) -> dict[str, Any]:
    if not differences:
        raise ValueError("paired bootstrap requires at least one difference")
    rng = random.Random(seed)
    n = len(differences)
    boot: list[float] = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(n):
            total += differences[rng.randrange(n)]
        boot.append(total / n)
    boot.sort()
    wins = sum(value > 1e-12 for value in differences)
    losses = sum(value < -1e-12 for value in differences)
    ties = n - wins - losses
    return {
        "n": n,
        "mean": sum(differences) / n,
        "median": statistics.median(differences),
        "ci95_low": percentile(boot, 0.025),
        "ci95_high": percentile(boot, 0.975),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "bootstrap_resamples": resamples,
        "bootstrap_seed": seed,
        "percentile_method": "linear_interpolation",
    }


def candidate_contract(path: Path, *, cap: int) -> dict[str, Any]:
    rows = load_jsonl(path)
    max_count = 0
    hidden_input_fields: list[str] = []
    malformed_candidates = 0
    for index, row in enumerate(rows):
        input_data = row.get("input_data")
        if not isinstance(input_data, dict) or set(input_data) != {"question"}:
            hidden_input_fields.append(f"row:{index}:input_keys={sorted(input_data) if isinstance(input_data, dict) else 'non_object'}")
        inference = row.get("inference_results")
        if not isinstance(inference, list) or len(inference) != 1 or not isinstance(inference[0], dict):
            raise ValueError(f"candidate row {index} does not carry exactly one inference result")
        candidates = inference[0].get("final_candidates")
        if not isinstance(candidates, list):
            raise ValueError(f"candidate row {index} final_candidates is not a list")
        max_count = max(max_count, len(candidates))
        for item in candidates:
            if not isinstance(item, dict) or set(item) != {"arxiv_id"}:
                malformed_candidates += 1
    return {
        "rows": len(rows),
        "max_candidate_count": max_count,
        "hidden_input_fields": hidden_input_fields,
        "malformed_candidates": malformed_candidates,
        "cap_respected": max_count <= cap,
        "sha256": sha256_file(path),
    }


def analyze(
    *,
    freeze_path: Path,
    manifest_path: Path,
    baseline_eval_path: Path,
    orion_eval_path: Path,
    diagnostic_eval_path: Path,
    baseline_candidate_path: Path,
    orion_candidate_path: Path,
    diagnostic_candidate_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    freeze = load_json(freeze_path)
    if freeze.get("schema_version") != "orion.p2.wide-openaire-matched-freeze.v1":
        raise ValueError("unexpected matched Wide freeze schema")
    manifest = load_json(manifest_path)
    if manifest.get("schema_version") != "orion.p2.wide-openaire-shared-capture.v1":
        raise ValueError("unexpected shared acquisition manifest schema")

    evaluations = {
        "wide_dual_backend_balanced": load_json(baseline_eval_path),
        "wide_dual_backend_governed": load_json(orion_eval_path),
        "wide_dual_backend_direct_first": load_json(diagnostic_eval_path),
    }
    candidates = {
        "wide_dual_backend_balanced": (baseline_candidate_path, candidate_contract(baseline_candidate_path, cap=int(freeze["acquisition"]["max_candidates_per_system"]))),
        "wide_dual_backend_governed": (orion_candidate_path, candidate_contract(orion_candidate_path, cap=int(freeze["acquisition"]["max_candidates_per_system"]))),
        "wide_dual_backend_direct_first": (diagnostic_candidate_path, candidate_contract(diagnostic_candidate_path, cap=int(freeze["acquisition"]["max_candidates_per_system"]))),
    }

    # Recheck immutable candidate hashes before deriving any terminal.
    hash_matches: dict[str, bool] = {}
    for system_id, (_, contract) in candidates.items():
        expected = str(manifest["candidate_hashes"][system_id])
        hash_matches[system_id] = contract["sha256"] == expected

    unit_maps = {system_id: pass0_by_question_last_write(value) for system_id, value in evaluations.items()}
    question_sets = {system_id: set(value) for system_id, value in unit_maps.items()}
    baseline_questions = question_sets["wide_dual_backend_balanced"]
    if any(value != baseline_questions for value in question_sets.values()):
        raise ValueError("official evaluator question sets differ across matched systems")
    expected_n = int(freeze["benchmark"]["expected_distinct_nonempty_question_units"])
    if len(baseline_questions) != expected_n:
        raise ValueError(f"expected {expected_n} distinct official question units, got {len(baseline_questions)}")

    ordered_questions = sorted(baseline_questions)
    differences = [
        float(unit_maps["wide_dual_backend_governed"][question]["iou"])
        - float(unit_maps["wide_dual_backend_balanced"][question]["iou"])
        for question in ordered_questions
    ]
    paired_cfg = freeze["evaluation"]["paired_inference"]
    paired = paired_bootstrap(
        differences,
        resamples=int(paired_cfg["bootstrap_resamples"]),
        seed=int(paired_cfg["seed"]),
    )

    official: dict[str, dict[str, Any]] = {}
    for system_id, evaluation in evaluations.items():
        aggregate = evaluation.get("aggregate_stats")
        if not isinstance(aggregate, dict):
            raise ValueError(f"official evaluator missing aggregate_stats for {system_id}")
        official[system_id] = aggregate

    baseline = official["wide_dual_backend_balanced"]
    orion = official["wide_dual_backend_governed"]
    diagnostic = official["wide_dual_backend_direct_first"]
    delta_iou = float(orion["avg_iou"]) - float(baseline["avg_iou"])
    delta_recall = float(orion["avg_recall"]) - float(baseline["avg_recall"])
    delta_precision = float(orion["avg_precision"]) - float(baseline["avg_precision"])

    cap = int(freeze["acquisition"]["max_candidates_per_system"])
    candidate_valid = all(
        contract["cap_respected"]
        and not contract["hidden_input_fields"]
        and contract["malformed_candidates"] == 0
        and contract["rows"] == int(freeze["benchmark"]["released_wide_rows"])
        for _, contract in candidates.values()
    )
    transport_ok = float(manifest["logical_provider_ok_fraction"]) >= float(
        freeze["validity"]["minimum_logical_provider_ok_fraction"]
    )
    validity = {
        "logical_provider_ok_fraction": float(manifest["logical_provider_ok_fraction"]),
        "logical_provider_ok": transport_ok,
        "candidate_contracts": {system_id: contract for system_id, (_, contract) in candidates.items()},
        "candidate_hash_matches_frozen_capture": hash_matches,
        "candidate_contracts_valid": candidate_valid,
        "same_acquisition_capture_for_all_systems": bool(manifest.get("same_acquisition_capture_for_all_systems")),
        "same_candidate_cap": all(contract["max_candidate_count"] <= cap for _, contract in candidates.values()),
        "raw_regex_arxiv_identity_extraction": bool(manifest.get("raw_regex_arxiv_identity_extraction")),
        "logical_request_count_exact": int(manifest["logical_provider_calls_planned"]) == int(manifest["logical_provider_calls_recorded"]),
        "freeze_hash_matches_capture": str(manifest.get("freeze_sha256")) == sha256_file(freeze_path),
        "all_candidate_hashes_match": all(hash_matches.values()),
    }
    all_valid = (
        validity["logical_provider_ok"]
        and validity["candidate_contracts_valid"]
        and validity["same_acquisition_capture_for_all_systems"]
        and validity["same_candidate_cap"]
        and not validity["raw_regex_arxiv_identity_extraction"]
        and validity["logical_request_count_exact"]
        and validity["freeze_hash_matches_capture"]
        and validity["all_candidate_hashes_match"]
    )

    rule = freeze["terminal_rule"]["supported"]
    scientific_rule = {
        "official_avg_iou_delta": delta_iou,
        "required_official_avg_iou_delta": float(rule["official_avg_iou_delta_orion_minus_baseline_at_least"]),
        "paired_iou_ci95_low": float(paired["ci95_low"]),
        "required_paired_iou_ci95_low_strictly_greater_than": float(rule["paired_iou_ci95_low_strictly_greater_than"]),
        "official_avg_recall_delta": delta_recall,
        "required_official_avg_recall_delta": float(rule["official_avg_recall_orion_minus_baseline_at_least"]),
    }
    scientific_supported = (
        delta_iou >= scientific_rule["required_official_avg_iou_delta"]
        and float(paired["ci95_low"]) > scientific_rule["required_paired_iou_ci95_low_strictly_greater_than"]
        and delta_recall >= scientific_rule["required_official_avg_recall_delta"]
    )
    terminals = freeze["terminal_rule"]
    if not all_valid:
        terminal = terminals["invalid_or_transport_terminal"]
    elif scientific_supported:
        terminal = terminals["positive_terminal"]
    else:
        terminal = terminals["negative_valid_terminal"]

    result = {
        "schema_version": "orion.p2.wide-openaire-matched-result.v1",
        "paper_id": "P2",
        "authority": "PINNED_OFFICIAL_WIDE_PLUS_PROSPECTIVE_PAIRED_ANALYSIS",
        "terminal": terminal,
        "claim_boundary": freeze["claim_boundary"],
        "freeze_sha256": sha256_file(freeze_path),
        "capture_manifest_sha256": sha256_file(manifest_path),
        "official": {
            "wide_dual_backend_balanced": baseline,
            "wide_dual_backend_governed": orion,
            "wide_dual_backend_direct_first": diagnostic,
            "orion_minus_primary_baseline": {
                "avg_iou": round(delta_iou, 12),
                "avg_recall": round(delta_recall, 12),
                "avg_precision": round(delta_precision, 12),
            },
        },
        "paired_distinct_question_iou": paired,
        "validity": validity,
        "all_validity_conditions": all_valid,
        "scientific_rule": scientific_rule,
        "scientific_supported": scientific_supported,
        "candidate_sha256": {system_id: contract["sha256"] for system_id, (_, contract) in candidates.items()},
        "evaluator_output_sha256": {
            "wide_dual_backend_balanced": sha256_file(baseline_eval_path),
            "wide_dual_backend_governed": sha256_file(orion_eval_path),
            "wide_dual_backend_direct_first": sha256_file(diagnostic_eval_path),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("P2_WIDE_OPENAIRE_MATCHED=" + json.dumps(result, sort_keys=True), flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--baseline-eval", required=True, type=Path)
    parser.add_argument("--orion-eval", required=True, type=Path)
    parser.add_argument("--diagnostic-eval", required=True, type=Path)
    parser.add_argument("--baseline-candidate", required=True, type=Path)
    parser.add_argument("--orion-candidate", required=True, type=Path)
    parser.add_argument("--diagnostic-candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    analyze(
        freeze_path=args.freeze,
        manifest_path=args.manifest,
        baseline_eval_path=args.baseline_eval,
        orion_eval_path=args.orion_eval,
        diagnostic_eval_path=args.diagnostic_eval,
        baseline_candidate_path=args.baseline_candidate,
        orion_candidate_path=args.orion_candidate,
        diagnostic_candidate_path=args.diagnostic_candidate,
        output_path=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
