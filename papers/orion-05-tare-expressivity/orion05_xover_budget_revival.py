#!/usr/bin/env python3
"""Execute the previously missing one-cell XOVER budget revival."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
from typing import Any, Sequence

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[1]
ARCHIVE = PAPER / "evidence/historical/pr-1498-q1-xover-v1/raw/research/extensions/orion-q"
SOURCE_RESULT = ARCHIVE / "Q1_XOVER_RESULTS_V1.json"
PROTOCOL = PAPER / "rounds/xover-budget-revival-v1/ORION05_XOVER_BUDGET_REVIVAL_PROTOCOL.json"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_q1(root: Path, timeout_seconds: int):
    current_modules = root / "research/extensions/orion-q"
    sys.path.insert(0, str(current_modules))
    os.environ["Q1XOVER_DXX_BUDGET_S"] = str(timeout_seconds)
    path = root / SOURCE_RESULT.relative_to(ROOT).parent / "q1_crossover_evaluation.py"
    spec = importlib.util.spec_from_file_location("orion05_q1_xover_archived", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_frozen_cell(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    source = json.loads((root / SOURCE_RESULT.relative_to(ROOT)).read_text())
    cells = source["panel"]["uniform"]
    cell = next(row for row in cells if int(row["n"]) == 6)
    instance = cell["instances"][0]
    return {"family": "uniform", "n": 6, "instance_index": 0, "targets": instance["targets"], "original_dxx": instance["dxx"], "parent_cost": instance["C_DP"]}


def adjudicate(dxx: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    if parent.get("status") != "COMPLETED" or parent.get("witness_valid") is not True:
        outcome = "CANNOT_CHECK"
    elif dxx.get("status") == "TIMEOUT":
        outcome = "RETAINED_NEGATIVE"
    elif dxx.get("status") == "EXACT" and dxx.get("witness_valid") is True and dxx.get("cost") == parent.get("cost"):
        outcome = "IMPROVED"
    else:
        outcome = "CANNOT_CHECK"
    return {
        "revival_outcome": outcome,
        "scientific_authority_delta": "NONE",
        "original_verdict_preserved": "RUN_INCOMPLETE",
        "authority": {"whole_panel_revival": False, "standalone_production_value": False, "generic_tare": False, "external_independence": False, "novelty": False, "journal_or_submission": False, "final_freeze": False},
    }


def execute(root: Path, timeout_seconds: int = 1800) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = Path(root).resolve()
    selection = select_frozen_cell(root)
    q1 = _load_q1(root, timeout_seconds)
    q1.extend_pair_guard()
    target_pairs = tuple((tuple(selection["targets"][2*i]), tuple(selection["targets"][2*i+1])) for i in range(3))
    terms = q1.r6m._synthetic_terms(target_pairs)
    parent_wall = time.perf_counter()
    parent = q1.r6m.exact_r6m_matching(terms, q1.MATCHING, 6, list(range(6)))
    parent_seconds = time.perf_counter() - parent_wall
    parent_row = {"status": "COMPLETED", "cost": int(parent["C_R6M"]), "witness_valid": all(parent["checks"].values()), "wall_seconds": parent_seconds}
    dxx = q1.run_dxx_bounded(target_pairs, 6, True)
    if dxx["status"] == "EXACT":
        witness = dxx.get("witness")
        dxx_row = {"status": "EXACT", "cost": int(dxx["C_Dxx"]), "witness_valid": bool(q1.r6p.verify_dxx_witness(target_pairs, 6, witness)), "wall_seconds": dxx.get("witness_seconds"), "witness_sha256": hashlib.sha256(canonical_json(witness).encode()).hexdigest()}
    else:
        dxx_row = {"status": dxx["status"], "cost": None, "witness_valid": None, "wall_seconds": dxx.get("witness_seconds"), "timeout_seconds": timeout_seconds, "error": dxx.get("error")}
    return selection, parent_row, dxx_row


def run(root: Path, output_dir: Path) -> dict[str, Any]:
    protocol = json.loads((root / PROTOCOL.relative_to(ROOT)).read_text())
    if protocol["status"] != "FROZEN_BEFORE_REVIVAL_OUTCOME":
        raise AssertionError("protocol not frozen")
    if output_dir.exists():
        raise FileExistsError(output_dir)
    output_dir.mkdir(parents=True)
    selection, parent, dxx = execute(root, int(protocol["lever"]["revival_timeout_seconds"]))
    result = adjudicate(dxx, parent)
    result.update({
        "schema": "ORION.ORION05.XoverBudgetRevivalResult.v1",
        "date": "2026-08-27",
        "terminal": f"ORION05_XOVER_BUDGET_REVIVAL_{result['revival_outcome']}",
        "mechanism_stage": "EXHAUSTIVE_SEARCH_COMPUTE_BUDGET",
        "selection": selection,
        "strongest_parent": parent,
        "legacy_direct_dxx_revival": dxx,
        "protocol_sha256": sha256_file(root / PROTOCOL.relative_to(ROOT)),
        "source_result_sha256": sha256_file(root / SOURCE_RESULT.relative_to(ROOT)),
        "source_commit": os.environ.get("ORION05_XOVER_REVIVAL_SOURCE_COMMIT"),
        "slurm": {key: os.environ.get(key) for key in ("SLURM_JOB_ID", "SLURM_JOB_NAME", "SLURM_JOB_PARTITION", "SLURM_CPUS_PER_TASK", "SLURM_MEM_PER_NODE", "SLURMD_NODENAME")},
        "peak_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "environment": {"python": sys.version, "platform": platform.platform()},
    })
    (output_dir / "ORION05_XOVER_BUDGET_REVIVAL_RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    if not args.run or args.output_dir is None:
        parser.error("--run --output-dir required")
    result = run(args.root.resolve(), args.output_dir)
    print("ORION05_XOVER_BUDGET_REVIVAL=" + canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
