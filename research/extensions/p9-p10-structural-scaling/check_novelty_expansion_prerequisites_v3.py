from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "NOVELTY_EXPANSION_PREREQUISITES_V3.json"


def exists(relative: str) -> bool:
    return (ROOT / relative).is_file()


def main() -> None:
    statuses = {
        "A_relational_complexity_frontier": {
            "status": "IMPLEMENTED_READY_TO_EXECUTE",
            "required": [
                "research/extensions/p9-p10-structural-scaling/NOVELTY_EXPANSION_PROTOCOL_V3.md",
                "research/extensions/p9-p10-structural-scaling/run_relational_complexity_frontier_v1.py",
            ],
        },
        "B_invertible_obfuscation_ladder": {
            "status": "IMPLEMENTED_READY_TO_EXECUTE",
            "required": [
                "research/extensions/p9-p10-structural-scaling/NOVELTY_EXPANSION_PROTOCOL_V3.md",
                "research/extensions/p9-p10-structural-scaling/INVERTIBLE_OBFUSCATION_THEOREM_V1.md",
                "research/extensions/p9-p10-structural-scaling/run_invertible_obfuscation_ladder_v1.py",
            ],
        },
        "C_semantic_orbit_llm": {
            "status": "CANNOT_CHECK_LLM_RUNTIME",
            "required": [
                "research/extensions/p9-p10-structural-scaling/P9_LLM_STRUCTURE_SCALING_PROTOCOL_V1.md",
            ],
            "missing_external": ["frozen multi-size open-weight inference runtime/checkpoints"],
        },
        "D_adaptive_compute_llm": {
            "status": "CANNOT_CHECK_MULTI_BUDGET_MODEL_RUNTIME",
            "required": [
                "research/extensions/p9-p10-structural-scaling/P9_LLM_STRUCTURE_SCALING_PROTOCOL_V1.md",
                "research/extensions/p9-p10-structural-scaling/NOVELTY_EXPANSION_PROTOCOL_V3.md",
            ],
            "missing_external": ["same-model reproducible multi-budget inference runtime"],
        },
        "E_p10_action_abstraction": {
            "status": "CANNOT_CHECK_NATIVE_RAW_TRACE_CORPUS",
            "required": [
                "research/extensions/p9-p10-structural-scaling/P10_NATIVE_STATE_INCREMENTAL_VALUE_PROTOCOL_V1.md",
                "research/extensions/p9-p10-structural-scaling/P10_INVARIANT_STATE_AND_SEARCH_PROTOCOL_V1.md",
            ],
            "missing_external": ["native/raw per-transition tactic trace corpus", "faithful macro-tactic comparator runtime"],
        },
        "F_same_information_lean_feedback": {
            "status": "CANNOT_CHECK_LEAN_REPAIR_RUNTIME",
            "required": [
                "research/extensions/p9-p10-structural-scaling/NOVELTY_EXPANSION_PROTOCOL_V3.md",
            ],
            "missing_external": ["exact Lean repair runner capable of raw and typed diagnostic re-rendering"],
        },
        "G_p10_cross_revision": {
            "status": "CANNOT_CHECK_SECOND_FROZEN_MATHLIB_REVISION",
            "required": [
                "research/extensions/p9-p10-structural-scaling/P10_NATIVE_STATE_INCREMENTAL_VALUE_PROTOCOL_V1.md",
            ],
            "missing_external": ["prospectively selected later Mathlib revision and native transition receipts"],
        },
        "H_cross_domain_meta": {
            "status": "BLOCKED_PENDING_SECOND_DOMAIN_SAME_INFORMATION_RESULT",
            "required": [
                "research/extensions/p9-p10-structural-scaling/NOVELTY_EXPANSION_PROTOCOL_V3.md",
            ],
            "missing_external": ["positive formal-domain same-information structural result"],
        },
    }

    for lane in statuses.values():
        missing_repo = [path for path in lane.get("required", []) if not exists(path)]
        lane["missing_repo"] = missing_repo
        if missing_repo and not lane["status"].startswith("CANNOT_CHECK"):
            lane["status"] = "INVALID_MISSING_REPOSITORY_PREREQUISITE"

    result = {
        "schema": "P9P10.NoveltyExpansionPrerequisites.v3",
        "lanes": statuses,
        "policy": "CANNOT_CHECK and BLOCKED states are not positive evidence and may not be promoted.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
