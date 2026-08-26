#!/usr/bin/env python3
"""Vendored scientific logic of PR #618 Qwen cross-size analyzer.

Source blob: 29fbbd6af9c35f405d6f0a0ab80ae9cfe9265639
Only input-path discovery is handled outside this file by the recovery workflow.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

PRIMARY_BUDGET = 32
BOOTSTRAP_SEED = 914031
BOOTSTRAP_DRAWS = 10000
TARGETS = (0.50, 0.70, 0.85)
SCALES = ("0.5B", "1.5B", "3B")
REPS = ("R1_SAME_INFO", "R2_TYPED_STATE")
BUDGETS = (8, 32, 96)


def quantile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lo, hi = math.floor(position), math.ceil(position)
    if lo == hi:
        return ordered[lo]
    weight = position - lo
    return ordered[lo] * (1 - weight) + ordered[hi] * weight


def accuracy(rows: list[dict[str, Any]]) -> float:
    if not rows:
        raise SystemExit("empty analysis cell")
    return sum(bool(row["correct"]) for row in rows) / len(rows)


def paired_arm_accuracy(rows: list[dict[str, Any]], representation: str) -> float:
    selected = [row for row in rows if row["representation"] == representation]
    return accuracy(selected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs=3, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    runs = [json.loads(Path(path).read_text()) for path in args.inputs]
    runs = sorted(runs, key=lambda value: int(value["model_parameter_count"]))
    if tuple(run["model_scale"] for run in runs) != SCALES:
        raise SystemExit("model family/scale mismatch")
    if any(run.get("schema") != "P9.LLMGGUFServerRuns.v1" for run in runs):
        raise SystemExit("unexpected run schema")
    if any(run.get("terminal") != "RUN_COMPLETE_PENDING_CROSS_SIZE_ANALYSIS" for run in runs):
        raise SystemExit("incomplete model run")

    manifests = {run["item_manifest_sha256"] for run in runs}
    prompts = {run["prompt_sha256"] for run in runs}
    if len(manifests) != 1 or len(prompts) != 1:
        raise SystemExit("cross-size manifest/prompt identity mismatch")
    if any(run.get("equivalence_failures") != 0 for run in runs):
        raise SystemExit("renderer equivalence failure")

    cells: list[dict[str, Any]] = []
    by_key: dict[tuple[str, str, int], dict[str, Any]] = {}
    effects: list[dict[str, Any]] = []
    hostile: dict[str, Any] = {}

    for run in runs:
        scale = run["model_scale"]
        grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
        for row in run["records"]:
            grouped[(row["representation"], int(row["budget"]))].append(row)
        for rep in REPS:
            for budget in BUDGETS:
                rows = grouped[(rep, budget)]
                if len(rows) != 192:
                    raise SystemExit(f"incomplete primary cell {scale}/{rep}/{budget}: {len(rows)}")
                cell = {
                    "model_scale": scale,
                    "params": run["model_parameter_count"],
                    "representation": rep,
                    "budget": budget,
                    "accuracy": accuracy(rows),
                    "mean_output_tokens": sum(int(row["output_tokens"]) for row in rows) / len(rows),
                    "mean_input_tokens": sum(int(row["input_tokens"]) for row in rows) / len(rows),
                }
                cells.append(cell)
                by_key[(scale, rep, budget)] = cell

        r1 = by_key[(scale, "R1_SAME_INFO", PRIMARY_BUDGET)]["accuracy"]
        r2 = by_key[(scale, "R2_TYPED_STATE", PRIMARY_BUDGET)]["accuracy"]
        effects.append({"model_scale": scale, "R1": r1, "R2": r2, "delta": r2 - r1})

        token_receipts = run["token_receipts"]
        token_nonshorter = (
            len(token_receipts) == 192
            and all(int(row["R2_input_tokens"]) >= int(row["R1_input_tokens"]) for row in token_receipts)
            and all(max(int(row["R1_input_tokens"]), int(row["R2_input_tokens"])) < 4096 for row in token_receipts)
        )
        leakage_green = not run.get("leakage_failures")
        output_accounting = all(isinstance(row.get("output_tokens"), int) for row in run["records"])

        control_summary: dict[str, Any] = {}
        for control in ("ORDER", "SYMBOL"):
            rows = [row for row in run["control_records"] if row["control"] == control]
            if len(rows) != 96:
                raise SystemExit(f"incomplete hostile control {scale}/{control}: {len(rows)}")
            r1_control = paired_arm_accuracy(rows, "R1_SAME_INFO")
            r2_control = paired_arm_accuracy(rows, "R2_TYPED_STATE")
            control_summary[control] = {
                "R1_accuracy": r1_control,
                "R2_accuracy": r2_control,
                "delta": r2_control - r1_control,
                "passes_nonnegative_delta": r2_control - r1_control >= 0,
            }

        hostile[scale] = {
            "token_nonshorter_and_context_green": token_nonshorter,
            "leakage_green": leakage_green,
            "output_token_accounting_green": output_accounting,
            "ORDER": control_summary["ORDER"],
            "SYMBOL": control_summary["SYMBOL"],
        }

    largest = runs[-1]
    per_domain: dict[str, float] = {}
    domains = sorted({row["domain"] for row in largest["records"]})
    for domain in domains:
        values: dict[str, float] = {}
        for rep in REPS:
            rows = [
                row for row in largest["records"]
                if row["domain"] == domain
                and row["representation"] == rep
                and int(row["budget"]) == PRIMARY_BUDGET
            ]
            values[rep] = accuracy(rows)
        per_domain[domain] = values["R2_TYPED_STATE"] - values["R1_SAME_INFO"]

    rng = random.Random(BOOTSTRAP_SEED)
    bootstrap: list[float] = []
    for _ in range(BOOTSTRAP_DRAWS):
        draw = [rng.choice(domains) for _ in domains]
        bootstrap.append(sum(per_domain[domain] for domain in draw) / len(draw))
    interval = [quantile(bootstrap, 0.025), quantile(bootstrap, 0.975)]

    substitutions: list[dict[str, Any]] = []
    for target in TARGETS:
        for budget in BUDGETS:
            for small_index, small in enumerate(runs[:-1]):
                for large in runs[small_index + 1:]:
                    structured = by_key[(small["model_scale"], "R2_TYPED_STATE", budget)]["accuracy"]
                    flat = by_key[(large["model_scale"], "R1_SAME_INFO", budget)]["accuracy"]
                    if structured >= target and flat >= target and structured >= flat:
                        substitutions.append(
                            {
                                "target": target,
                                "budget": budget,
                                "smaller_structured": small["model_scale"],
                                "smaller_structured_accuracy": structured,
                                "larger_same_info": large["model_scale"],
                                "larger_same_info_accuracy": flat,
                            }
                        )

    compute_substitutions: list[dict[str, Any]] = []
    for run in runs:
        scale = run["model_scale"]
        for target in TARGETS:
            r1_budget = next(
                (budget for budget in BUDGETS if by_key[(scale, "R1_SAME_INFO", budget)]["accuracy"] >= target),
                None,
            )
            r2_budget = next(
                (budget for budget in BUDGETS if by_key[(scale, "R2_TYPED_STATE", budget)]["accuracy"] >= target),
                None,
            )
            if r1_budget is not None and r2_budget is not None and r2_budget < r1_budget:
                compute_substitutions.append(
                    {
                        "model_scale": scale,
                        "target": target,
                        "R1_budget": r1_budget,
                        "R2_budget": r2_budget,
                    }
                )

    hostile_all_green = all(
        value["token_nonshorter_and_context_green"]
        and value["leakage_green"]
        and value["output_token_accounting_green"]
        and value["ORDER"]["passes_nonnegative_delta"]
        and value["SYMBOL"]["passes_nonnegative_delta"]
        for value in hostile.values()
    )
    checks = {
        "positive_delta_every_size": all(effect["delta"] > 0 for effect in effects),
        "largest_domain_bootstrap_lower_gt_zero": interval[0] > 0,
        "largest_nonnegative_domain_fraction_ge_0_60": (
            sum(delta >= 0 for delta in per_domain.values()) / len(per_domain) >= 0.60
        ),
        "observed_smaller_structured_substitution_exists": bool(substitutions),
        "all_hostile_controls_green": hostile_all_green,
    }
    terminal = (
        "LLM_STRUCTURE_SCALING_FRONTIER_SUPPORTED"
        if all(checks.values())
        else "LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED"
    )

    output = {
        "schema": "P9.LLMGGUFScalingAnalysis.v1.1",
        "primary_budget": PRIMARY_BUDGET,
        "effects": effects,
        "largest_model_domain_deltas": per_domain,
        "domain_block_bootstrap_95pct": interval,
        "substitutions": substitutions,
        "compute_substitutions": compute_substitutions,
        "hostile_controls": hostile,
        "cells": cells,
        "checks": checks,
        "terminal": terminal,
        "claim_boundary": (
            "Exact Qwen2.5 Q4_K_M 0.5B/1.5B/3B family only. Structured prompts were padded "
            "to remove any shorter-input advantage. No full-precision or cross-family generalization."
        ),
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
