#!/usr/bin/env python3
"""Fail-closed schema adapter for the frozen FiberGuard R15 executor.

R15's first execution loaded the bound ASP-POTASSCO ARFF and stopped before any
aggregate result because the file did not expose an attribute literally named
``runtime``.  This adapter changes no scientific object.  It accepts exactly
one performance column after excluding the four ASlib identity/status fields,
records that column by scenario, and delegates every split, policy, objective
and gate to the prospectively frozen R15 implementation.
"""
from __future__ import annotations

import argparse
import collections
from pathlib import Path
from typing import Any

import fiberguard_multidomain_r15 as frozen

OBSERVED_PERFORMANCE_COLUMNS: dict[str, str] = {}


def load_algorithm_runs_with_timeout(
    path: Path,
    cutoff: float,
    read_arff,
    median,
    most_common_status,
):
    """Read one ASlib run table with an explicit unique measure-column gate."""
    attrs, rows = read_arff(path)
    identity = {"instance_id", "repetition", "algorithm", "runstatus"}
    missing = sorted(identity - set(attrs))
    if missing:
        raise ValueError(f"{path}: missing ASlib identity/status attributes {missing}")
    performance_columns = [name for name in attrs if name not in identity]
    if len(performance_columns) != 1:
        raise ValueError(
            f"{path}: expected exactly one performance column after {sorted(identity)}; "
            f"observed {performance_columns} in schema {attrs}"
        )
    performance = performance_columns[0]
    OBSERVED_PERFORMANCE_COLUMNS[path.parent.name] = performance
    index = {name: attrs.index(name) for name in (*sorted(identity), performance)}

    grouped: dict[tuple[str, str], list[tuple[float, str]]] = collections.defaultdict(list)
    algorithms: set[str] = set()
    for row in rows:
        instance = row[index["instance_id"]]
        algorithm = row[index["algorithm"]]
        grouped[(instance, algorithm)].append(
            (float(row[index[performance]]), row[index["runstatus"]])
        )
        algorithms.add(algorithm)

    names = sorted(algorithms)
    runtimes: dict[str, dict[str, float]] = collections.defaultdict(dict)
    timeout: dict[str, dict[str, bool]] = collections.defaultdict(dict)
    status_counts: collections.Counter[str] = collections.Counter()
    for (instance, algorithm), values in grouped.items():
        status = most_common_status(status for _, status in values)
        runtime = median([value for value, _ in values])
        status_counts[status] += 1
        timeout[instance][algorithm] = status != "ok"
        runtimes[instance][algorithm] = runtime if status == "ok" else 10.0 * cutoff

    incomplete = [
        instance for instance, row in runtimes.items() if set(row) != set(names)
    ]
    if incomplete:
        raise ValueError(f"incomplete algorithm matrix for {len(incomplete)} instances")
    return dict(runtimes), dict(timeout), names, dict(sorted(status_counts.items()))


def run(root: Path) -> dict[str, Any]:
    OBSERVED_PERFORMANCE_COLUMNS.clear()
    frozen.load_algorithm_runs_with_timeout = load_algorithm_runs_with_timeout
    result = frozen.run(root)
    expected = set(frozen.REGISTRY)
    if set(OBSERVED_PERFORMANCE_COLUMNS) != expected:
        raise AssertionError(
            "performance-column audit did not cover the full frozen registry: "
            f"{sorted(OBSERVED_PERFORMANCE_COLUMNS)} != {sorted(expected)}"
        )
    result["source_schema_adapter"] = {
        "first_failed_run_id": 33015635958,
        "first_failed_job_id": 98333009427,
        "first_failure_terminal": "PRE_AGGREGATE_SCHEMA_INCOMPATIBILITY",
        "scientific_protocol_changed": False,
        "scenario_registry_changed": False,
        "splits_changed": False,
        "arms_changed": False,
        "objectives_or_gates_changed": False,
        "observed_performance_columns": dict(sorted(OBSERVED_PERFORMANCE_COLUMNS.items())),
        "acceptance_rule": "exactly one non-identity/non-runstatus ARFF attribute",
    }
    result["controls"]["schema_adapter_covers_all_registered_scenarios"] = True
    result["controls"]["schema_adapter_preserves_frozen_scientific_contract"] = True
    return result


def self_test() -> dict[str, bool]:
    def fake_read_arff(_path: Path):
        return (
            ["instance_id", "repetition", "algorithm", "time", "runstatus"],
            [
                ["i1", "1", "a", "2.0", "ok"],
                ["i1", "2", "a", "4.0", "ok"],
                ["i1", "1", "b", "1.0", "timeout"],
            ],
        )

    runtimes, timeout, names, status = load_algorithm_runs_with_timeout(
        Path("Synthetic/time.arff"),
        10.0,
        fake_read_arff,
        lambda values: sum(values) / len(values),
        lambda values: collections.Counter(values).most_common(1)[0][0],
    )
    assert names == ["a", "b"]
    assert runtimes == {"i1": {"a": 3.0, "b": 100.0}}
    assert timeout == {"i1": {"a": False, "b": True}}
    assert status == {"ok": 1, "timeout": 1}

    def ambiguous_read_arff(_path: Path):
        return (
            ["instance_id", "repetition", "algorithm", "runtime", "memory", "runstatus"],
            [],
        )

    rejected = False
    try:
        load_algorithm_runs_with_timeout(
            Path("Synthetic/ambiguous.arff"),
            10.0,
            ambiguous_read_arff,
            min,
            min,
        )
    except ValueError:
        rejected = True
    assert rejected
    inherited = frozen.self_test()
    return {
        **inherited,
        "single_measure_alias": True,
        "ambiguous_measure_rejected": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aslib-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(frozen.canonical_json(self_test()))
        return 0
    if args.aslib_root is None or args.output is None:
        parser.error("--aslib-root and --output are required")
    result = run(args.aslib_root)
    payload = frozen.canonical_json(result) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    print(
        frozen.TERMINAL,
        f"scientific_terminal={result['scientific_terminal']}",
        f"scenario_passes={result['portfolio']['scenario_pass_count']}/{result['portfolio']['scenario_count']}",
        f"sha256={frozen.sha256_bytes(payload.encode())}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
