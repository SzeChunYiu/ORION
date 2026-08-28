#!/usr/bin/env python3
"""R13 parent-certificate-guided first-candidate ordering revival.

This is deliberately not a standalone acceleration: the unrestricted exact
parent is executed and fully charged before its certificate is projected into
the sparse support-two representation.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
from typing import Any, Sequence

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[1]
PROTOCOL_PATH = PAPER / "rounds/r13-parent-certificate-ordering/ORION05_R13_PROTOCOL.json"
FULL = "FULL_SUBJECT"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_modules(root: Path):
    r12 = _load_path("orion05_r12_for_r13", root / "papers/orion_05_r12_production_benchmark.py")
    dp, sparse, verifier = r12._load_solver_modules()
    return r12, dp, sparse, verifier


def _sparse_key(global_key: Sequence[int], n: int, r12, dp, sparse):
    dense = r12._global_to_dense(global_key, n, dp.p10.h.BITS_CODE)
    return sparse.dense_to_sparse(dense)


def evaluate_cell(root: Path, subject: str, matching_index: int, projection: int | str = FULL) -> dict[str, Any]:
    root = Path(root).resolve()
    r12, dp, sparse, verifier = _load_modules(root)
    protocol = r12.load_protocol(root / "papers/orion-05-tare-expressivity/rounds/r12-production-benchmark/ORION05_R12_PRODUCTION_BENCHMARK_PROTOCOL.json")
    n, matching, target_pairs_global = r12._cell_targets(protocol, subject, matching_index, projection)
    dense_pairs = tuple(
        tuple(r12._global_to_dense(target, n, dp.p10.h.BITS_CODE) for target in pair)
        for pair in target_pairs_global
    )
    terms = dp._synthetic_terms(target_pairs_global)

    parent_wall_start = time.perf_counter_ns()
    parent_cpu_start = time.process_time_ns()
    parent = dp.exact_r6m_matching(terms, dp._SYNTHETIC_MATCHING, n, list(range(6)))
    parent_cpu_ns = time.process_time_ns() - parent_cpu_start
    parent_wall_ns = time.perf_counter_ns() - parent_wall_start
    parent_checks = verifier.separately_check_production_witness(target_pairs_global, parent, n)

    projection_wall_start = time.perf_counter_ns()
    projection_cpu_start = time.process_time_ns()
    pairs = tuple(
        sparse.FramePair(
            _sparse_key(parent["R"][block][0], n, r12, dp, sparse),
            _sparse_key(parent["R"][block][1], n, r12, dp, sparse),
        )
        for block in ("A", "B", "C")
    )
    tag = _sparse_key(parent["S"], n, r12, dp, sparse)
    permutations = (int(parent["relative_permutation_B"]), int(parent["relative_permutation_C"]))
    prep = dict(sparse._ordered_variants(dense_pairs))[permutations]
    centrals = tuple(int(value) for value in parent["centrals"])
    orientation = tuple(int(value) for value in parent["common_labels"])
    frame_cost = sparse.frame_cost(pairs, centrals)
    tag_cost = 2 * len(tag)
    restore_cost = sparse.restore_cost_sparse(prep, pairs)
    projected = sparse.SparseWitness(
        frame_cost + tag_cost + restore_cost,
        pairs,
        tag,
        orientation,
        centrals,
        permutations,
        frame_cost,
        tag_cost,
        restore_cost,
    )
    sparse_checks = sparse.verify_witness(dense_pairs, projected)
    phase_checks = sparse.build_phase_certificate(dense_pairs, projected)["checks"]
    projection_cpu_ns = time.process_time_ns() - projection_cpu_start
    projection_wall_ns = time.perf_counter_ns() - projection_wall_start
    frame_supports = [[len(pair.r0), len(pair.r1)] for pair in pairs]
    projection_valid = (
        all(parent_checks.values())
        and int(parent["C_R6M"]) == projected.cost
        and all(sparse_checks.values())
        and all(phase_checks.values())
    )
    return {
        "subject": subject,
        "matching_index": int(matching_index),
        "matching": [list(pair) for pair in matching],
        "projection": projection,
        "n_qubits": n,
        "parent_algorithm": "unrestricted_dp",
        "parent_cost": int(parent["C_R6M"]),
        "projected_cost": int(projected.cost),
        "frame_supports": frame_supports,
        "maximum_frame_support": max(value for pair in frame_supports for value in pair),
        "tag_support": len(tag),
        "parent_witness_checks": parent_checks,
        "sparse_witness_checks": sparse_checks,
        "phase_checks": phase_checks,
        "projection_valid": projection_valid,
        "parent_cpu_ns": parent_cpu_ns,
        "parent_wall_ns": parent_wall_ns,
        "projection_verify_cpu_ns": projection_cpu_ns,
        "projection_verify_wall_ns": projection_wall_ns,
        "charged_total_cpu_ns": parent_cpu_ns + projection_cpu_ns,
        "charged_total_wall_ns": parent_wall_ns + projection_wall_ns,
        "peak_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "projected_witness_sha256": hashlib.sha256(canonical_json(projected.as_dict()).encode()).hexdigest(),
    }


def adjudicate(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    complete = len(rows) == 24
    valid = complete and all(
        row.get("projection_valid") is True
        and row.get("parent_cost") == row.get("projected_cost")
        and int(row.get("charged_total_wall_ns", 0)) >= int(row.get("parent_wall_ns", 0))
        for row in rows
    )
    hard_error = any(row.get("status") == "ERROR" for row in rows)
    if hard_error or not complete:
        outcome = "CANNOT_CHECK"
    elif valid:
        outcome = "IMPROVED"
    else:
        outcome = "RETAINED_NEGATIVE"
    ratios = [row["charged_total_wall_ns"] / row["parent_wall_ns"] for row in rows if row.get("parent_wall_ns")]
    return {
        "schema": "ORION.ORION05.R13.ParentCertificateOrderingResult.v1",
        "date": "2026-08-27",
        "terminal": "ORION05_R13_PARENT_CERTIFICATE_ORDERING_COMPLETION_ONLY__R12_PRODUCTION_NULL_RETAINED" if outcome == "IMPROVED" else f"ORION05_R13_{outcome}",
        "revival_outcome": outcome,
        "scientific_authority_delta": "NONE",
        "cell_count": len(rows),
        "all_projection_valid": valid,
        "hybrid_over_parent_wall_ratio_min": min(ratios) if ratios else None,
        "hybrid_over_parent_wall_ratio_max": max(ratios) if ratios else None,
        "r12_null_preserved": True,
        "mechanism_disposition": "R12 timeouts are attributable to exhaustive candidate ordering on this held-out panel; parent-certificate ordering completes but requires and charges the parent, so standalone production value remains false.",
        "authority": {
            "standalone_production_value": False,
            "generic_tare": False,
            "physical_or_fault_tolerant_value": False,
            "external_independence": False,
            "novelty": False,
            "journal_or_submission": False,
            "final_freeze": False,
        },
    }


def _run_child_subprocess(root: Path, subject: str, index: int, python: str) -> dict[str, Any]:
    command = [python, str(Path(__file__).resolve()), "--child", "--root", str(root), "--subject", subject, "--matching-index", str(index)]
    completed = subprocess.run(command, check=False, text=True, capture_output=True, timeout=300, env={**os.environ, "PYTHONHASHSEED": "0", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"})
    if completed.returncode != 0:
        return {"subject": subject, "matching_index": index, "status": "ERROR", "returncode": completed.returncode, "stderr": completed.stderr[-2000:]}
    return json.loads(completed.stdout)


def run_confirmatory(root: Path, output_dir: Path, python: str) -> dict[str, Any]:
    root = Path(root).resolve()
    protocol = json.loads(PROTOCOL_PATH.read_text())
    if protocol["status"] != "FROZEN_BEFORE_CONFIRMATORY_OUTCOME":
        raise AssertionError("protocol not frozen")
    if output_dir.exists():
        raise FileExistsError(output_dir)
    output_dir.mkdir(parents=True)
    rows = [
        _run_child_subprocess(root, subject, index, python)
        for subject in protocol["confirmatory_panel"]["subjects"]
        for index in protocol["confirmatory_panel"]["included_heldout_indices"]
    ]
    raw = "".join(canonical_json(row) + "\n" for row in rows)
    (output_dir / "RAW_ATTEMPTS.jsonl").write_text(raw)
    result = adjudicate(rows)
    result.update({
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "source_commit": os.environ.get("ORION05_R13_SOURCE_COMMIT"),
        "slurm": {key: os.environ.get(key) for key in ("SLURM_JOB_ID", "SLURM_JOB_NAME", "SLURM_JOB_PARTITION", "SLURM_CPUS_PER_TASK", "SLURM_MEM_PER_NODE", "SLURMD_NODENAME")},
        "raw_attempts_sha256": hashlib.sha256(raw.encode()).hexdigest(),
    })
    (output_dir / "ORION05_R13_RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    environment = {"schema": "ORION.ORION05.R13.Environment.v1", "python": sys.version, "platform": platform.platform(), "executable": sys.executable}
    (output_dir / "ENVIRONMENT.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--subject")
    parser.add_argument("--matching-index", type=int)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args(argv)
    if args.child:
        print(canonical_json(evaluate_cell(args.root, args.subject, args.matching_index)))
        return 0
    if args.run:
        if args.output_dir is None:
            parser.error("--output-dir required")
        result = run_confirmatory(args.root, args.output_dir, args.python)
        print("ORION05_R13_RESULT=" + canonical_json(result))
        return 0
    parser.error("choose --child or --run")


if __name__ == "__main__":
    raise SystemExit(main())
