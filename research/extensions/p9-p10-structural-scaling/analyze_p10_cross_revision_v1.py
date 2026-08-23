from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from fit_p10_native_state_v1 import (
    MATHLIB_COMMIT,
    LEAN_TOOLCHAIN,
    align_rows,
    build_markov,
    choose_c,
    fit_model,
    markov_result,
    merge_shards,
    model_nll,
    source_population,
    verify_receipt,
)

TARGET_COMMIT = "d77ef0741c6da1ff12df68fb4145ea0ae0850c54"
TARGET_TOOLCHAIN = "leanprover/lean4:v4.34.0-rc1"
TARGET_SCHEMA = "P10.CrossRevisionNativeTraceShard.v1"
BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 914039
SOURCE_PATHS = 457


def quantile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lo, hi = math.floor(position), math.ceil(position)
    if lo == hi:
        return ordered[lo]
    w = position - lo
    return ordered[lo] * (1 - w) + ordered[hi] * w


def target_merge(paths: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    source_paths = existing_paths = denominator = eligible = 0
    statuses: dict[str, int] = defaultdict(int)
    for path in paths:
        data = json.loads(Path(path).read_text())
        if data.get("schema") != TARGET_SCHEMA:
            raise SystemExit(f"bad target shard schema: {path}")
        if data.get("target_commit") != TARGET_COMMIT or data.get("target_toolchain") != TARGET_TOOLCHAIN:
            raise SystemExit("target revision/toolchain mismatch")
        identity = (int(data["shard_index"]), int(data["shard_count"]))
        if identity in seen:
            raise SystemExit(f"duplicate target shard {identity}")
        seen.add(identity)
        source_paths += int(data["source_manifest_paths_in_shard"])
        existing_paths += int(data["existing_target_paths"])
        denominator += int(data["target_transition_denominator"])
        eligible += int(data["eligible_target_transitions"])
        rows.extend(data["rows"])
        for file_row in data["files"]:
            statuses[str(file_row["status"])] += 1
    counts = {count for _, count in seen}
    if len(counts) != 1 or len(seen) != next(iter(counts)):
        raise SystemExit(f"incomplete target shards: {sorted(seen)}")
    if source_paths != SOURCE_PATHS:
        raise SystemExit(f"target path denominator mismatch: {source_paths}")
    if eligible != len(rows):
        raise SystemExit(f"target eligible count mismatch: {eligible} vs {len(rows)}")
    seen_receipts: set[str] = set()
    for row in rows:
        if row["mathlib_commit"] != TARGET_COMMIT or row["lean_toolchain"] != TARGET_TOOLCHAIN:
            raise SystemExit("target row identity mismatch")
        if not verify_receipt(row):
            raise SystemExit(f"target receipt invalid: {row['transition_id']}")
        receipt_key = f"{row['source_path']}|{row['transition_id']}"
        if receipt_key in seen_receipts:
            raise SystemExit(f"duplicate target receipt: {receipt_key}")
        seen_receipts.add(receipt_key)
    return rows, {
        "source_manifest_paths": source_paths,
        "existing_target_paths": existing_paths,
        "path_coverage": existing_paths / source_paths,
        "target_transition_denominator": denominator,
        "eligible_target_transitions": eligible,
        "native_coverage": eligible / denominator if denominator else 0.0,
        "file_status": dict(statuses),
    }


def accuracy(results: list[dict[str, Any]], rows: list[dict[str, Any]]) -> float:
    if not rows:
        raise ValueError("empty accuracy population")
    return sum(result["predicted_action"] == row["true_action"] for result, row in zip(results, rows)) / len(rows)


def block_bootstrap(module_effects: dict[str, list[float]]) -> list[float]:
    names = sorted(module_effects)
    rng = random.Random(BOOTSTRAP_SEED)
    samples: list[float] = []
    for _ in range(BOOTSTRAP_N):
        selected = [rng.choice(names) for _ in names]
        values: list[float] = []
        for name in selected:
            values.extend(module_effects[name])
        samples.append(sum(values) / len(values))
    return samples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-shards", nargs="+", required=True)
    parser.add_argument("--target-shards", nargs="+", required=True)
    parser.add_argument("--source-analysis", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source_population_rows = source_population()
    source_trace_rows, source_extraction = merge_shards(args.source_shards)
    source_rows = align_rows(source_trace_rows, source_population_rows)
    target_rows, target_extraction = target_merge(args.target_shards)
    source_analysis_wrapper = json.loads(Path(args.source_analysis).read_text())
    source_analysis = source_analysis_wrapper.get("native", source_analysis_wrapper)
    source_terminal = source_analysis.get("terminal")

    source_by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        source_by_module[row["top_module"]].append(row)
    source_population_by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_population_rows:
        source_population_by_module[row["top_module"]].append(row)
    target_by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in target_rows:
        target_by_module[row["top_module"]].append(row)

    modules = sorted(set(target_by_module) & set(source_by_module))
    source_results = {"B1": [], "B4": []}
    source_truth: list[dict[str, Any]] = []
    target_results = {"B1": [], "B4": []}
    target_truth: list[dict[str, Any]] = []
    target_effects: dict[str, list[float]] = defaultdict(list)
    fold_receipts: list[dict[str, Any]] = []

    for module in modules:
        source_train_eligible = [row for row in source_rows if row["top_module"] != module]
        source_test = source_by_module[module]
        target_test = target_by_module[module]
        source_train_all = [row for row in source_population_rows if row["top_module"] != module]
        next_by, global_next = build_markov(source_train_all)

        selected_c, nested_scores = choose_c(source_train_eligible, "B4")
        b4_model = fit_model(source_train_eligible, "B4", selected_c)
        _, source_b4 = model_nll(b4_model, source_test, "B4")
        _, target_b4 = model_nll(b4_model, target_test, "B4")
        source_b1 = [markov_result(next_by, global_next, row)[0] for row in source_test]
        target_b1 = [markov_result(next_by, global_next, row)[0] for row in target_test]

        source_results["B1"].extend(source_b1)
        source_results["B4"].extend(source_b4)
        source_truth.extend(source_test)
        target_results["B1"].extend(target_b1)
        target_results["B4"].extend(target_b4)
        target_truth.extend(target_test)
        for b1, b4, row in zip(target_b1, target_b4, target_test):
            target_effects[module].append(
                float(b4["predicted_action"] == row["true_action"])
                - float(b1["predicted_action"] == row["true_action"])
            )
        fold_receipts.append({
            "held_out_module": module,
            "source_train_eligible": len(source_train_eligible),
            "source_train_all_B1": len(source_train_all),
            "source_test": len(source_test),
            "target_test": len(target_test),
            "selected_C_B4": selected_c,
            "nested_source_log_loss": nested_scores,
            "target_refit": False,
        })

    if not target_truth or not source_truth:
        raise SystemExit("no matched source/target held-module evaluation rows")

    source_acc = {
        arm: accuracy(source_results[arm], source_truth)
        for arm in ("B1", "B4")
    }
    target_acc = {
        arm: accuracy(target_results[arm], target_truth)
        for arm in ("B1", "B4")
    }
    target_delta = target_acc["B4"] - target_acc["B1"]
    degradation = {
        arm: abs(target_acc[arm] - source_acc[arm])
        for arm in ("B1", "B4")
    }
    bootstrap = block_bootstrap(target_effects)
    interval = [quantile(bootstrap, 0.025), quantile(bootstrap, 0.975)]
    target_module_means = {
        module: sum(values) / len(values)
        for module, values in target_effects.items()
    }

    identity_green = (
        source_extraction["transition_denominator"] == 11_842
        and target_extraction["source_manifest_paths"] == 457
        and all(row["mathlib_commit"] == TARGET_COMMIT for row in target_rows)
        and all(row["lean_toolchain"] == TARGET_TOOLCHAIN for row in target_rows)
        and MATHLIB_COMMIT == "e72c1e277f31441626621f7d0c7207862fc25569"
        and LEAN_TOOLCHAIN == TARGET_TOOLCHAIN
    )
    checks = {
        "source_native_primary_supported": source_terminal == "P10_NATIVE_STATE_INCREMENTAL_VALUE_SUPPORTED",
        "target_path_coverage_ge_0_80": target_extraction["path_coverage"] >= 0.80,
        "target_native_coverage_ge_0_80": target_extraction["native_coverage"] >= 0.80,
        "target_B4_accuracy_gt_B1": target_acc["B4"] > target_acc["B1"],
        "B4_absolute_degradation_lt_B1": degradation["B4"] < degradation["B1"],
        "target_module_bootstrap_lower_gt_zero": interval[0] > 0,
        "identity_receipts_green": identity_green,
        "zero_target_refitting": all(not row["target_refit"] for row in fold_receipts),
    }
    terminal = (
        "STRUCTURAL_COORDINATES_CROSS_REVISION_ROBUSTNESS_SUPPORTED"
        if all(checks.values())
        else "STRUCTURAL_COORDINATES_CROSS_REVISION_GATE_NOT_MET"
    )
    output = {
        "schema": "P10.CrossRevisionStructuralTransferAnalysis.v1",
        "source_commit": MATHLIB_COMMIT,
        "target_commit": TARGET_COMMIT,
        "source_native_terminal": source_terminal,
        "source_extraction": source_extraction,
        "target_extraction": target_extraction,
        "matched_modules": modules,
        "source_accuracy": source_acc,
        "target_accuracy": target_acc,
        "target_B4_minus_B1": target_delta,
        "absolute_degradation": degradation,
        "target_module_effects": target_module_means,
        "target_bootstrap_95pct_interval": interval,
        "fold_receipts": fold_receipts,
        "checks": checks,
        "terminal": terminal,
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k != "fold_receipts"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
