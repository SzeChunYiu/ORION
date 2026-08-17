#!/usr/bin/env python3
"""Bind exact P1 mutation-necessity arm/evaluator identity after world freeze.

Runs no candidate arm and accesses no task-level outcome beyond identity/count
checks already recorded in WORLD_FREEZE.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from freeze_mutation_necessity_worlds import ROOT, load_effective_protocol  # noqa: E402
from orion.study.p1_causal.necessity_policies_v3 import (  # noqa: E402
    ABLATION_ARMS,
    RUNNABLE_ARMS,
)

DEFAULT_PROTOCOL = (
    ROOT
    / "research"
    / "revival"
    / "p1"
    / "protocol"
    / "P1.epistemic-mutation-necessity.v2.2.3.json"
)
EXECUTION_SOURCE_PATHS = (
    "research/revival/p1/run_mutation_necessity_campaign.py",
    "src/orion/study/p1_causal/absorbed_mechanics.py",
    "src/orion/study/p1_causal/necessity_engine.py",
    "src/orion/study/p1_causal/necessity_policies.py",
    "src/orion/study/p1_causal/necessity_policies_v3.py",
    "src/orion/study/p1_causal/necessity_scoring.py",
    "src/orion/study/p1_causal/necessity_statistics.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_execution(protocol_path: Path, world_dir: Path, out: Path) -> dict:
    protocol, identity = load_effective_protocol(protocol_path)
    world_path = world_dir / "WORLD_FREEZE.json"
    world = json.loads(world_path.read_text())
    public = world_dir / "WORLD_PUBLIC.jsonl"
    protected = world_dir / "PROTECTED_RESPONSE_MATRIX.jsonl"

    if world.get("arms_executed") is not False or world.get("outcome_accessed") is not False:
        raise ValueError("world freeze records outcome access")
    if world.get("protocol_chain", {}).get("chain_sha256") != identity["chain_sha256"]:
        raise ValueError("world/protocol chain mismatch")
    if _sha(public) != world.get("public_sha256"):
        raise ValueError("public world drift")
    if _sha(protected) != world.get("protected_response_matrix_sha256"):
        raise ValueError("protected response-matrix drift")
    if int(world.get("n", -1)) != int(protocol["fresh_world_plan"]["total_n"]):
        raise ValueError("world count drift")

    runnable_ids = tuple(item.__name__ for item in RUNNABLE_ARMS)
    ablation_ids = tuple(item.__name__ for item in ABLATION_ARMS)
    frozen_runnable = tuple(
        item["id"]
        for item in protocol["matched_arms"]
        if item["id"] != "oracle_minimal_valid_ceiling"
    )
    if runnable_ids != frozen_runnable:
        raise ValueError(f"runnable arm registry drift:{runnable_ids}!={frozen_runnable}")
    if set(ablation_ids) != set(protocol["direct_ablations"]):
        raise ValueError("ablation registry drift")

    h1_parents = tuple(protocol["primary_hypotheses"][0]["comparators"])
    if not h1_parents or any(parent not in runnable_ids for parent in h1_parents):
        raise ValueError("frozen H1 parent missing from runnable registry")

    binding = {
        "schema_version": "P1.epistemic-mutation-necessity-execution-freeze.v1",
        "protocol_id": protocol["protocol_id"],
        "protocol_version": protocol["protocol_version"],
        "protocol_chain_sha256": identity["chain_sha256"],
        "world_freeze_sha256": _sha(world_path),
        "public_sha256": world["public_sha256"],
        "protected_response_matrix_sha256": world["protected_response_matrix_sha256"],
        "n": world["n"],
        "hidden_shift_n": world["hidden_shift_n"],
        "negative_control_n": world["negative_control_n"],
        "intervention_budget_units": float(protocol["intervention_budget"]["units_per_task"]),
        "runnable_arms": list(runnable_ids),
        "ablation_arms": list(ablation_ids),
        "h1_parents": list(h1_parents),
        "control_parent": protocol["primary_hypotheses"][1]["comparators"][0],
        "statistics": protocol["statistics"],
        "support_rule": protocol["support_rule"],
        "source_sha256": {path: _sha(ROOT / path) for path in EXECUTION_SOURCE_PATHS},
        "arms_executed": False,
        "outcome_accessed": False,
        "claim_boundary": "EXECUTION_IDENTITY_ONLY__NO_ARM_OUTPUT__NO_SCIENTIFIC_RESULT",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n")
    return binding


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--world-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = freeze_execution(args.protocol, args.world_dir, args.out)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
