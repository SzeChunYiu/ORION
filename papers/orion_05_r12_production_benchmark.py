#!/usr/bin/env python3
"""Prospectively frozen ORION-05 Round-2 production benchmark.

The module has two deliberately separate roles:

* a fresh child process executes one exact solver attempt; and
* an orchestrator retains every completed, timed-out, or failed attempt and
  applies the decision rule frozen in the R12 protocol.

Timing is evidence about the recorded machine only.  Exact costs and witnesses
remain the scientific correctness gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import signal
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "orion-05-tare-expressivity"
ROUND_DIR = PAPER / "rounds" / "r12-production-benchmark"
PROTOCOL_PATH = ROUND_DIR / "ORION05_R12_PRODUCTION_BENCHMARK_PROTOCOL.json"
SUBJECT_RECEIPT_PATH = (
    ROOT
    / "research"
    / "extensions"
    / "orion-q"
    / "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json"
)
Q_SOURCE = ROOT / "research" / "extensions" / "orion-q"
SPARSE_SOURCE = PAPER / "orion05_r11_sparse_direct_solver.py"
R11_VERIFIER_SOURCE = PAPER / "orion05_r11_sparse_equivalence_verify.py"
ALGORITHMS = ("support_two", "unrestricted_dp")
FULL = "FULL_SUBJECT"
METRICS = ("wall_ns", "cpu_ns", "peak_rss_kib", "verification_ns")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rss_to_kib(value: int, *, system: str | None = None) -> int:
    """Normalize getrusage's Darwin-byte/Linux-KiB platform difference."""
    return int(value // 1024) if (system or platform.system()) == "Darwin" else int(value)


def resolve_source_commit(root: Path = ROOT, environ: dict[str, str] | os._Environ[str] = os.environ) -> str:
    """Resolve a checkout commit or validate an exact archive-deployment binding."""
    bound = environ.get("ORION05_R12_SOURCE_COMMIT")
    if bound is not None:
        if len(bound) != 40 or any(char not in "0123456789abcdef" for char in bound):
            raise AssertionError("invalid ORION05_R12_SOURCE_COMMIT")
        source_file = root / "SOURCE_COMMIT.txt"
        if not source_file.is_file() or source_file.read_text().strip() != bound:
            raise AssertionError("archive source-commit binding mismatch")
        return bound
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def load_protocol(path: Path = PROTOCOL_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if value["status"] != "FROZEN_BEFORE_OUTCOME" or value["round"] != 2:
        raise AssertionError("R12 protocol is not the prospectively frozen Round-2 object")
    return value


def verify_source_bindings(protocol: dict[str, Any]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for name, binding in protocol["source_bindings"].items():
        path = ROOT / binding["path"]
        observed = {
            "path": binding["path"],
            "exists": path.is_file(),
            "bytes": path.stat().st_size if path.is_file() else None,
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        observed["matches"] = (
            observed["exists"]
            and observed["bytes"] == binding["bytes"]
            and observed["sha256"] == binding["sha256"]
        )
        rows[name] = observed
    return {"bindings": rows, "all_match": all(row["matches"] for row in rows.values())}


def perfect_matchings(indices: Sequence[int]) -> tuple[tuple[tuple[int, int], ...], ...]:
    ordered = tuple(sorted(int(index) for index in indices))
    if len(ordered) != 6 or len(set(ordered)) != 6:
        raise ValueError("six distinct indices are required")

    def rec(rest: tuple[int, ...]) -> tuple[tuple[tuple[int, int], ...], ...]:
        if not rest:
            return ((),)
        first = rest[0]
        out = []
        for offset in range(1, len(rest)):
            pair = (first, rest[offset])
            remaining = rest[1:offset] + rest[offset + 1 :]
            for tail in rec(remaining):
                out.append((pair,) + tail)
        return tuple(out)

    return tuple(sorted(set(tuple(sorted(row)) for row in rec(ordered))))


def _canonical_targets_from_witness(row: dict[str, Any]) -> list[tuple[int, tuple[int, int]]]:
    witness = row["witness"]
    matching = tuple(tuple(int(x) for x in pair) for pair in row["matching"])
    blocks = [tuple(tuple(int(x) for x in target) for target in witness["targets"][name]) for name in ("A", "B", "C")]
    if int(witness["relative_permutation_B"]):
        blocks[1] = tuple(reversed(blocks[1]))
    if int(witness["relative_permutation_C"]):
        blocks[2] = tuple(reversed(blocks[2]))
    return [(index, target) for pair, targets in zip(matching, blocks, strict=True) for index, target in zip(pair, targets, strict=True)]


def load_subject_panels(protocol: dict[str, Any]) -> dict[str, dict[str, Any]]:
    receipt = json.loads(SUBJECT_RECEIPT_PATH.read_text())
    panels: dict[str, dict[str, Any]] = {}
    selected = tuple(int(x) for x in protocol["panel"]["matching_indices"])
    for subject, frozen in protocol["subjects"].items():
        source = receipt["subjects"][subject]
        if source["source_blob_observed"] != frozen["source_blob"]:
            raise AssertionError({"subject_blob_mismatch": subject})
        rows = source["candidate_points"]
        expected_matchings = perfect_matchings(frozen["source_indices"])
        observed_matchings = tuple(
            tuple(tuple(int(x) for x in pair) for pair in row["matching"]) for row in rows
        )
        if observed_matchings != expected_matchings:
            raise AssertionError({"canonical_matching_order_mismatch": subject})
        target_by_index: dict[int, tuple[int, int]] = {}
        consistent = True
        for row in rows:
            for index, target in _canonical_targets_from_witness(row):
                prior = target_by_index.get(index)
                if prior is not None and prior != target:
                    consistent = False
                target_by_index[index] = target
        if set(target_by_index) != set(int(x) for x in frozen["source_indices"]):
            raise AssertionError({"subject_target_coverage_mismatch": subject})
        panels[subject] = {
            "n_qubits": int(frozen["n_qubits"]),
            "source_blob": frozen["source_blob"],
            "source_indices": tuple(int(x) for x in frozen["source_indices"]),
            "target_by_index": target_by_index,
            "matchings": expected_matchings,
            "selected_matching_indices": selected,
            "all_matching_target_maps_consistent": consistent,
        }
    return panels


def project_key(key: Sequence[int], n: int) -> tuple[int, int]:
    if n < 1:
        raise ValueError("projection size must be positive")
    mask = (1 << int(n)) - 1
    return int(key[0]) & mask, int(key[1]) & mask


def _attempt_id(spec: dict[str, Any]) -> str:
    projection = "full" if spec["projection"] == FULL else str(spec["projection"])
    return (
        f"{spec['subject']}-m{spec['matching_index']:02d}-q{projection}-"
        f"{spec['algorithm']}-r{spec['repeat']}"
    )


def attempt_schedule(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    """Initial schedule; completed support-two scale probes add two repeats later."""
    rows: list[dict[str, Any]] = []
    correctness = set(protocol["panel"]["correctness_panel"])
    repeats = int(protocol["panel"]["completed_cell_repeats"])
    for subject in sorted(protocol["subjects"]):
        for matching_index in protocol["panel"]["matching_indices"]:
            for projection in protocol["panel"]["projection_qubits"]:
                for algorithm in ALGORITHMS:
                    count = repeats if projection in correctness or algorithm == "unrestricted_dp" else 1
                    for repeat in range(count):
                        spec = {
                            "subject": subject,
                            "matching_index": int(matching_index),
                            "projection": projection,
                            "algorithm": algorithm,
                            "repeat": repeat,
                        }
                        spec["attempt_id"] = _attempt_id(spec)
                        rows.append(spec)
    return rows


def completed_scale_repeats(protocol: dict[str, Any], rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    repeats = int(protocol["panel"]["completed_cell_repeats"])
    scheduled = {row["attempt_id"] for row in rows}
    additions: list[dict[str, Any]] = []
    for row in rows:
        if (
            row.get("algorithm") != "support_two"
            or row.get("projection") not in protocol["panel"]["scale_panel"]
            or row.get("repeat") != 0
            or row.get("status") != "COMPLETED"
        ):
            continue
        for repeat in range(1, repeats):
            spec = {
                "subject": row["subject"],
                "matching_index": int(row["matching_index"]),
                "projection": row["projection"],
                "algorithm": "support_two",
                "repeat": repeat,
            }
            spec["attempt_id"] = _attempt_id(spec)
            if spec["attempt_id"] not in scheduled:
                additions.append(spec)
                scheduled.add(spec["attempt_id"])
    return additions


def _cell_key(row: dict[str, Any]) -> tuple[str, int, Any]:
    return row["subject"], int(row["matching_index"]), row["projection"]


def _algorithm_cell_rows(rows: Sequence[dict[str, Any]], algorithm: str) -> dict[tuple[str, int, Any], list[dict[str, Any]]]:
    grouped: dict[tuple[str, int, Any], list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("algorithm") == algorithm:
            grouped.setdefault(_cell_key(row), []).append(row)
    return grouped


def _completed(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("status") == "COMPLETED"]


def _metric_medians(rows: Sequence[dict[str, Any]]) -> dict[str, float | None]:
    completed = _completed(rows)
    return {
        metric: (float(statistics.median(int(row[metric]) for row in completed)) if completed else None)
        for metric in METRICS
    }


def adjudicate_rows(
    protocol: dict[str, Any],
    rows: Sequence[dict[str, Any]],
    *,
    source_bindings_ok: bool,
) -> dict[str, Any]:
    repeats = int(protocol["panel"]["completed_cell_repeats"])
    selected = [
        (subject, int(matching), projection)
        for subject in sorted(protocol["subjects"])
        for matching in protocol["panel"]["matching_indices"]
        for projection in protocol["panel"]["projection_qubits"]
    ]
    correctness_keys = {key for key in selected if key[2] in protocol["panel"]["correctness_panel"]}
    full_keys = {key for key in selected if key[2] == FULL}
    dp = _algorithm_cell_rows(rows, "unrestricted_dp")
    sparse = _algorithm_cell_rows(rows, "support_two")

    def complete_with_valid_witnesses(grouped, keys):
        return all(
            len(_completed(grouped.get(key, []))) >= repeats
            and all(row.get("witness_valid") is True for row in _completed(grouped.get(key, [])))
            for key in keys
        )

    correctness_complete = complete_with_valid_witnesses(dp, correctness_keys) and complete_with_valid_witnesses(sparse, correctness_keys)
    unrestricted_full_complete = complete_with_valid_witnesses(dp, full_keys)
    support_two_full_complete = complete_with_valid_witnesses(sparse, full_keys)

    cost_comparisons = []
    all_costs_equal = True
    for key in selected:
        left = _completed(dp.get(key, []))
        right = _completed(sparse.get(key, []))
        if not left or not right:
            continue
        left_costs = sorted(set(int(row["cost"]) for row in left))
        right_costs = sorted(set(int(row["cost"]) for row in right))
        equal = len(left_costs) == 1 and left_costs == right_costs
        cost_comparisons.append({"cell": list(key), "unrestricted_costs": left_costs, "support_two_costs": right_costs, "equal": equal})
        all_costs_equal = all_costs_equal and equal

    completed_rows = _completed(rows)
    all_completed_witnesses_valid = all(row.get("witness_valid") is True for row in completed_rows)
    hard_errors = [row for row in rows if row.get("status") not in ("COMPLETED", "TIMEOUT")]

    full_dp_rows = [row for row in rows if row.get("algorithm") == "unrestricted_dp" and row.get("projection") == FULL]
    full_sparse_rows = [row for row in rows if row.get("algorithm") == "support_two" and row.get("projection") == FULL]
    dp_medians = _metric_medians(full_dp_rows)
    sparse_medians = _metric_medians(full_sparse_rows)
    ratios: dict[str, float | None] = {}
    for metric in METRICS:
        left, right = dp_medians[metric], sparse_medians[metric]
        ratios[metric] = None if left in (None, 0) or right is None else float(right / left)

    improvement_metrics = [metric for metric in ("wall_ns", "cpu_ns", "peak_rss_kib") if ratios[metric] is not None and ratios[metric] <= 0.75]
    nonworse = all(ratios[metric] is not None and ratios[metric] <= 1.10 for metric in METRICS)
    positive = support_two_full_complete and bool(improvement_metrics) and nonworse

    preconditions = {
        "all_source_bindings_match": bool(source_bindings_ok),
        "correctness_panel_complete_with_valid_witnesses": correctness_complete,
        "unrestricted_referee_completes_full_subject_panel": unrestricted_full_complete,
        "all_shared_completed_costs_equal": all_costs_equal and bool(cost_comparisons),
        "all_completed_witnesses_valid": all_completed_witnesses_valid,
        "no_non_timeout_execution_errors": not hard_errors,
    }
    cannot_check = not all(preconditions.values())
    if cannot_check:
        terminal = protocol["decision_rule"]["terminals"]["cannot_check"]
    elif positive:
        terminal = protocol["decision_rule"]["terminals"]["positive"]
    else:
        terminal = protocol["decision_rule"]["terminals"]["null"]

    return {
        "schema": "ORION.ORION05.R12.ProductionBenchmarkResult.v1",
        "paper_id": "ORION-05",
        "round": 2,
        "terminal": terminal,
        "preconditions": preconditions,
        "decision": {
            "positive_rule_satisfied": positive,
            "improvement_metrics_at_least_25_percent": improvement_metrics,
            "all_resource_medians_no_more_than_10_percent_worse": nonworse,
        },
        "full_subject": {
            "unrestricted_complete": unrestricted_full_complete,
            "support_two_complete": support_two_full_complete,
            "unrestricted_timeouts": sum(row.get("status") == "TIMEOUT" for row in full_dp_rows),
            "support_two_timeouts": sum(row.get("status") == "TIMEOUT" for row in full_sparse_rows),
            "unrestricted_medians": dp_medians,
            "support_two_medians": sparse_medians,
            "support_two_over_unrestricted_ratios": ratios,
        },
        "cost_comparisons": cost_comparisons,
        "attempt_counts": {
            "total": len(rows),
            "completed": len(completed_rows),
            "timeouts": sum(row.get("status") == "TIMEOUT" for row in rows),
            "errors": len(hard_errors),
        },
        "rounds": {"consumed": 2, "maximum": 3, "science_status": "OPEN"},
        "authority": {
            "frozen_r6m_production_search_value": terminal == protocol["decision_rule"]["terminals"]["positive"],
            "generic_tare_complexity": False,
            "physical_or_fault_tolerant_resource_value": False,
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
            "submission_authorized": False,
        },
        "hard_errors": hard_errors,
    }


def _global_to_dense(key: Sequence[int], n: int, code_bits: dict[tuple[int, int], int]) -> tuple[int, ...]:
    return tuple(code_bits[((int(key[0]) >> q) & 1, (int(key[1]) >> q) & 1)] for q in range(n))


class SolverTimeout(Exception):
    pass


def _timeout_handler(_signum, _frame):
    raise SolverTimeout


def _load_solver_modules():
    sys.path.insert(0, str(PAPER))
    sys.path.insert(0, str(Q_SOURCE))
    import max_r6m_exact_three_tare2_shared_factor_dp as dp  # noqa: PLC0415
    import orion05_r11_sparse_direct_solver as sparse  # noqa: PLC0415
    import orion05_r11_sparse_equivalence_verify as verifier  # noqa: PLC0415

    return dp, sparse, verifier


def _cell_targets(protocol: dict[str, Any], subject: str, matching_index: int, projection: Any):
    panels = load_subject_panels(protocol)
    panel = panels[subject]
    n = panel["n_qubits"] if projection == FULL else int(projection)
    matching = panel["matchings"][matching_index]
    target_pairs = tuple(
        tuple(project_key(panel["target_by_index"][index], n) for index in pair) for pair in matching
    )
    return n, matching, target_pairs


def planned_states(algorithm: str, n: int) -> dict[str, int]:
    if algorithm == "support_two":
        pair_count = 54 * n**3 - 108 * n**2 + 60 * n
        return {
            "ordered_anticommuting_pairs": pair_count,
            "frame_pair_triples": pair_count**3,
            "orientation_checks_per_triple": 2,
            "relative_target_orders_per_feasible_triple": 4,
        }
    return {
        "outer_permutation_central_configurations": 32,
        "parity_states": 512,
        "local_letter_options": 4**7,
        "dp_transition_candidates_upper": 32 * n * 512 * 512,
    }


def run_child(spec: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    protocol = load_protocol()
    source = verify_source_bindings(protocol)
    n, matching, target_pairs_global = _cell_targets(
        protocol, spec["subject"], int(spec["matching_index"]), spec["projection"]
    )
    dp, sparse, verifier = _load_solver_modules()
    dense_pairs = tuple(
        tuple(_global_to_dense(target, n, dp.p10.h.BITS_CODE) for target in pair)
        for pair in target_pairs_global
    )
    row = dict(spec)
    row.update(
        {
            "n_qubits": n,
            "matching": [list(pair) for pair in matching],
            "planned_states": planned_states(spec["algorithm"], n),
            "source_bindings_ok": source["all_match"],
            "pid": os.getpid(),
            "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        }
    )
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler) if hasattr(signal, "SIGALRM") else None
    if hasattr(signal, "setitimer"):
        signal.setitimer(signal.ITIMER_REAL, timeout_seconds)
    started_wall = time.perf_counter_ns()
    started_cpu = time.process_time_ns()
    try:
        if spec["algorithm"] == "support_two":
            witness = sparse.solve_matching(dense_pairs)
            cost = int(witness.cost)
        elif spec["algorithm"] == "unrestricted_dp":
            terms = dp._synthetic_terms(target_pairs_global)
            witness = dp.exact_r6m_matching(terms, dp._SYNTHETIC_MATCHING, n, list(range(6)))
            cost = int(witness["C_R6M"])
        else:
            raise ValueError({"unknown_algorithm": spec["algorithm"]})
        row["wall_ns"] = time.perf_counter_ns() - started_wall
        row["cpu_ns"] = time.process_time_ns() - started_cpu
        if hasattr(signal, "setitimer"):
            signal.setitimer(signal.ITIMER_REAL, 0)
        verify_started = time.perf_counter_ns()
        if spec["algorithm"] == "support_two":
            witness_checks = sparse.verify_witness(dense_pairs, witness)
            phase_checks = sparse.build_phase_certificate(dense_pairs, witness)["checks"]
            witness_valid = all(witness_checks.values()) and all(phase_checks.values())
            serialized_witness = witness.as_dict()
        else:
            witness_checks = verifier.separately_check_production_witness(target_pairs_global, witness, n)
            witness_valid = all(witness_checks.values())
            serialized_witness = witness
        row.update(
            {
                "status": "COMPLETED",
                "cost": cost,
                "witness_valid": witness_valid,
                "witness_checks": witness_checks,
                "verification_ns": time.perf_counter_ns() - verify_started,
                "peak_rss_kib": rss_to_kib(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                "witness_sha256": hashlib.sha256(canonical_json(serialized_witness).encode()).hexdigest(),
            }
        )
    except SolverTimeout:
        row.update(
            {
                "status": "TIMEOUT",
                "cost": None,
                "witness_valid": None,
                "wall_ns": time.perf_counter_ns() - started_wall,
                "cpu_ns": time.process_time_ns() - started_cpu,
                "verification_ns": None,
                "peak_rss_kib": rss_to_kib(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                "timeout_seconds": timeout_seconds,
            }
        )
    finally:
        if hasattr(signal, "setitimer"):
            signal.setitimer(signal.ITIMER_REAL, 0)
        if old_handler is not None:
            signal.signal(signal.SIGALRM, old_handler)
    return row


def _run_subprocess(spec: dict[str, Any], python: str, timeout_seconds: int, core: int | None) -> dict[str, Any]:
    command = [
        python,
        str(Path(__file__).resolve()),
        "--child",
        "--subject",
        spec["subject"],
        "--matching-index",
        str(spec["matching_index"]),
        "--projection",
        str(spec["projection"]),
        "--algorithm",
        spec["algorithm"],
        "--repeat",
        str(spec["repeat"]),
        "--timeout-seconds",
        str(timeout_seconds),
    ]
    if core is not None:
        command = ["taskset", "-c", str(core), *command]
    env = os.environ.copy()
    env.update(
        {
            "PYTHONHASHSEED": "0",
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        }
    )

    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds + 30,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        row = dict(spec)
        row.update(
            {
                "status": "TIMEOUT",
                "cost": None,
                "witness_valid": None,
                "timeout_seconds": timeout_seconds,
                "hard_parent_timeout": True,
                "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
                "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
            }
        )
        return row
    if completed.returncode != 0:
        row = dict(spec)
        row.update(
            {
                "status": "ERROR",
                "returncode": completed.returncode,
                "stdout_tail": completed.stdout[-4000:],
                "stderr_tail": completed.stderr[-4000:],
            }
        )
        return row
    try:
        row = json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        row = dict(spec)
        row.update(
            {
                "status": "ERROR",
                "returncode": completed.returncode,
                "stdout_tail": completed.stdout[-4000:],
                "stderr_tail": completed.stderr[-4000:],
                "parse_failure": True,
            }
        )
    return row


def _run_specs(specs: Sequence[dict[str, Any]], python: str, timeout_seconds: int, workers: int) -> list[dict[str, Any]]:
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else []
    workers = max(1, min(workers, len(affinity) if affinity else workers))
    out: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _run_subprocess,
                spec,
                python,
                timeout_seconds,
                affinity[index % len(affinity)] if affinity else None,
            ): spec
            for index, spec in enumerate(specs)
        }
        for future in as_completed(futures):
            out.append(future.result())
    return out


def environment_receipt(python: str, workers: int) -> dict[str, Any]:
    numpy_version = subprocess.check_output([python, "-c", "import numpy; print(numpy.__version__)"], text=True).strip()
    commit = resolve_source_commit()
    return {
        "schema": "ORION.ORION05.R12.BenchmarkEnvironment.v1",
        "commit": commit,
        "python_executable": python,
        "python_version": subprocess.check_output([python, "-c", "import sys; print(sys.version)"], text=True).strip(),
        "numpy_version": numpy_version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "workers": workers,
        "slurm": {key: os.environ.get(key) for key in ("SLURM_JOB_ID", "SLURM_JOB_NODELIST", "SLURM_CPUS_PER_TASK", "SLURM_JOB_PARTITION")},
        "thread_limits": {key: "1" for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
    }


def run_benchmark(output_dir: Path, python: str, workers: int) -> dict[str, Any]:
    protocol = load_protocol()
    source = verify_source_bindings(protocol)
    panels = load_subject_panels(protocol)
    if not all(panel["all_matching_target_maps_consistent"] for panel in panels.values()):
        raise AssertionError("subject target reconstruction is inconsistent")
    timeout_seconds = int(protocol["panel"]["per_attempt_timeout_seconds"])
    initial = _run_specs(attempt_schedule(protocol), python, timeout_seconds, workers)
    additions = completed_scale_repeats(protocol, initial)
    rows = initial + _run_specs(additions, python, timeout_seconds, workers)
    rows.sort(key=lambda row: row["attempt_id"])
    output_dir.mkdir(parents=True, exist_ok=False)
    raw = output_dir / "RAW_ATTEMPTS.jsonl"
    raw.write_text("".join(canonical_json(row) + "\n" for row in rows))
    env = environment_receipt(python, workers)
    (output_dir / "BENCHMARK_ENVIRONMENT.json").write_text(json.dumps(env, indent=2, sort_keys=True) + "\n")
    result = adjudicate_rows(protocol, rows, source_bindings_ok=source["all_match"])
    result.update(
        {
            "protocol_sha256": sha256_file(PROTOCOL_PATH),
            "raw_attempts_sha256": sha256_file(raw),
            "environment_sha256": sha256_file(output_dir / "BENCHMARK_ENVIRONMENT.json"),
            "source_binding_audit": source,
            "subject_reconstruction": {
                name: {
                    "n_qubits": panel["n_qubits"],
                    "source_blob": panel["source_blob"],
                    "all_matching_target_maps_consistent": panel["all_matching_target_maps_consistent"],
                }
                for name, panel in panels.items()
            },
        }
    )
    (output_dir / "ORION05_R12_PRODUCTION_BENCHMARK_RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(result["terminal"])
    return result


def verify_result_bundle(
    output_dir: Path, *, require_current_source_bindings: bool = True
) -> dict[str, Any]:
    """Recompute a retained bundle without rerunning machine-specific timing."""
    protocol = load_protocol()
    raw_path = output_dir / "RAW_ATTEMPTS.jsonl"
    environment_path = output_dir / "BENCHMARK_ENVIRONMENT.json"
    result_path = output_dir / "ORION05_R12_PRODUCTION_BENCHMARK_RESULT.json"
    if not all(path.is_file() for path in (raw_path, environment_path, result_path)):
        raise AssertionError("R12 result bundle is incomplete")
    rows = [json.loads(line) for line in raw_path.read_text().splitlines() if line]
    ids = [row.get("attempt_id") for row in rows]
    if None in ids or len(ids) != len(set(ids)):
        raise AssertionError("R12 attempt IDs are missing or duplicated")

    initial_specs = attempt_schedule(protocol)
    initial_ids = {spec["attempt_id"] for spec in initial_specs}
    by_id = {row["attempt_id"]: row for row in rows}
    if not initial_ids.issubset(by_id):
        raise AssertionError({"missing_initial_attempts": sorted(initial_ids - set(by_id))})
    initial_rows = [by_id[spec["attempt_id"]] for spec in initial_specs]
    dynamic_ids = {spec["attempt_id"] for spec in completed_scale_repeats(protocol, initial_rows)}
    allowed = initial_ids | dynamic_ids
    if set(by_id) != allowed:
        raise AssertionError(
            {
                "unexpected_attempts": sorted(set(by_id) - allowed),
                "missing_dynamic_attempts": sorted(allowed - set(by_id)),
            }
        )

    bindings = verify_source_bindings(protocol)
    if require_current_source_bindings and not bindings["all_match"]:
        raise AssertionError(bindings)
    committed = json.loads(result_path.read_text())
    if committed.get("protocol_sha256") != sha256_file(PROTOCOL_PATH):
        raise AssertionError("R12 protocol digest mismatch")
    if committed.get("raw_attempts_sha256") != sha256_file(raw_path):
        raise AssertionError("R12 raw-attempt digest mismatch")
    if committed.get("environment_sha256") != sha256_file(environment_path):
        raise AssertionError("R12 environment digest mismatch")

    recomputed = adjudicate_rows(
        protocol,
        rows,
        source_bindings_ok=bindings["all_match"] if require_current_source_bindings else True,
    )
    core = (
        "schema",
        "paper_id",
        "round",
        "terminal",
        "preconditions",
        "decision",
        "full_subject",
        "cost_comparisons",
        "attempt_counts",
        "rounds",
        "authority",
        "hard_errors",
    )
    drift = {key: {"committed": committed.get(key), "recomputed": recomputed.get(key)} for key in core if committed.get(key) != recomputed.get(key)}
    if drift:
        raise AssertionError({"R12_adjudication_drift": drift})
    if committed["terminal"] not in set(protocol["decision_rule"]["terminals"].values()):
        raise AssertionError("R12 terminal is not predeclared")
    return committed


def parse_projection(value: str) -> int | str:
    return FULL if value == FULL else int(value)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--verify-bundle", type=Path)
    parser.add_argument("--subject", choices=("H4", "N2"))
    parser.add_argument("--matching-index", type=int)
    parser.add_argument("--projection")
    parser.add_argument("--algorithm", choices=ALGORITHMS)
    parser.add_argument("--repeat", type=int, default=0)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--workers", type=int, default=max(1, min(16, os.cpu_count() or 1)))
    args = parser.parse_args(argv)
    if args.child:
        required = (args.subject, args.matching_index, args.projection, args.algorithm)
        if any(value is None for value in required):
            parser.error("child mode requires subject, matching-index, projection and algorithm")
        spec = {
            "subject": args.subject,
            "matching_index": args.matching_index,
            "projection": parse_projection(args.projection),
            "algorithm": args.algorithm,
            "repeat": args.repeat,
        }
        spec["attempt_id"] = _attempt_id(spec)
        print(canonical_json(run_child(spec, args.timeout_seconds)))
        return 0
    if args.run:
        if args.output_dir is None:
            parser.error("run mode requires --output-dir")
        run_benchmark(args.output_dir, args.python, args.workers)
        return 0
    if args.verify_bundle is not None:
        result = verify_result_bundle(args.verify_bundle)
        print(result["terminal"])
        return 0
    parser.error("choose --child, --run or --verify-bundle")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
