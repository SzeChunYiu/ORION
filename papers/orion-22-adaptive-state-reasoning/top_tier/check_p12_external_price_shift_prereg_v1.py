#!/usr/bin/env python3
"""Fail-closed checker for A2's outcome-blind external price/shift preregistration."""
from __future__ import annotations

import itertools
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PREREG = HERE / "P12_EXTERNAL_PRICE_SHIFT_SUCCESSOR_PREREG_V1.json"


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path)], cwd=ROOT, text=True
    ).strip()


def main() -> int:
    p = json.loads(PREREG.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["schema"] = p.get("schema") == "ORION.A2.ExternalPriceShiftSuccessorPrereg.v1"
    checks["outcome_blind"] = (
        p.get("results_exist") is False
        and p.get("protected_outcomes_accessed") is False
        and p.get("scientific_authority_delta") == "NONE__PROTOCOL_ONLY"
    )

    levels = p["price_grid"]["levels"]
    grid = list(itertools.product(levels, repeat=3))
    checks["price_levels_exact"] = levels == [0.5, 1.0, 2.0]
    checks["price_grid_27"] = len(grid) == p["price_grid"]["regime_count"] == 27
    checks["flat_reference_present"] = tuple(p["price_grid"]["flat_reference"]) in grid
    checks["three_charge_loci"] = all(
        key in p["price_grid"]
        for key in ("materialization_locus", "retrieval_locus", "reasoning_tool_locus")
    )

    shifts = p["distribution_shift_axes"]
    checks["all_external_benchmarks_have_axes"] = set(shifts) == {
        "ScienceAgentBench", "LongMemEval", "LongMemEval-V2"
    } and all(v.get("axes") for v in shifts.values())
    checks["sab_four_disciplines"] = len(shifts["ScienceAgentBench"]["disciplines"]) == 4
    checks["sab_domain_shift_is_one_at_a_time"] = any(
        "double_weight_each_discipline_one_at_a_time" in a.get("regimes", [])
        and "leave_one_discipline_out_each_discipline_one_at_a_time" in a.get("regimes", [])
        for a in shifts["ScienceAgentBench"]["axes"]
    )
    checks["longmemeval_six_types_bound"] = len(
        p["source_bindings"]["LongMemEval"]["question_types"]
    ) == 6
    checks["longmemeval_type_shift_frozen"] = any(
        "double_weight_each_type_one_at_a_time" in a.get("regimes", [])
        and "leave_one_type_out_each_type_one_at_a_time" in a.get("regimes", [])
        for a in shifts["LongMemEval"]["axes"]
    )
    checks["longmemeval_v2_domains_and_abilities_bound"] = (
        p["source_bindings"]["LongMemEval-V2"]["domains"] == ["web", "enterprise"]
        and len(p["source_bindings"]["LongMemEval-V2"]["memory_abilities"]) == 5
    )
    checks["longmemeval_v2_shift_frozen"] = {
        a["axis"] for a in shifts["LongMemEval-V2"]["axes"]
    } >= {"domain_mix", "ability_mix", "haystack_scale"}

    for name in ("orion22_stopgo_menu", "orion21_external_requirements"):
        bound = p["source_bindings"][name]
        checks[f"source_blob_{name}"] = git_blob(ROOT / bound["path"]) == bound["git_blob_sha"]

    allocator = p["allocator_freeze"]
    checks["original_allocator_no_retune"] = "no threshold" in allocator["original_allocator"]
    checks["successor_separate_prereg"] = "separately versioned preregistration" in allocator["price_aware_successor"]
    checks["phase_diagram_required"] = "per-benchmark phase diagram" in p["reporting_contract"]["required"]

    good = all(checks.values())
    print(json.dumps({"decision": "GREEN" if good else "REJECT", "checks": checks},
                     indent=2, sort_keys=True))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
