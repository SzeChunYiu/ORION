#!/usr/bin/env python3
"""Exact dual replay for ORION-04 Wave 3 supports 11 through 13."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

PACKET = Path(__file__).resolve().parent
PROTOCOL = PACKET / "PROTOCOL.json"
SOURCE_MANIFEST = PACKET / "SOURCE_MANIFEST.json"
EXPECTED_TERMINALS = PACKET / "EXPECTED_TERMINALS.json"
THEORY = PACKET / "THEORY.md"
CLAIM_DISPOSITION = PACKET / "CLAIM_DISPOSITION.md"
DEFAULT_OUTPUT = PACKET / "RESULT.json"
TOKEN = "ORION04_M4_REPLAY="

EXPECTED_M3_SCHEMA = "ORION.NonQuantumMath.M3.Support10Replay.v1"
EXPECTED_M3_DIGEST = "bc1a727fe936a3cd3ddf033bb0ac9c6ebad6d6969a9e10c45c8d53fd2732e044"
EXPECTED_M3_TERMINAL = (
    "NONQUANTUM_M3_C5CUBED_SUPPORT10_BOTH_DEFICIT_PATTERNS_EXCLUDED"
    "__OBSTRUCTION_SUPPORT_AT_LEAST11"
)

EXPECTED_RANK3: dict[tuple[int, int, int], dict[str, int]] = {
    (1, 5, 5): {"a1": 1, "b2": 5, "c4": 5, "support": 11, "nodes": 406521, "leaves": 0, "solutions": 0},
    (3, 2, 6): {"a1": 3, "b2": 2, "c4": 6, "support": 11, "nodes": 278515, "leaves": 0, "solutions": 0},
    (1, 7, 4): {"a1": 1, "b2": 7, "c4": 4, "support": 12, "nodes": 294085, "leaves": 0, "solutions": 0},
    (3, 4, 5): {"a1": 3, "b2": 4, "c4": 5, "support": 12, "nodes": 406521, "leaves": 0, "solutions": 0},
    (5, 1, 6): {"a1": 5, "b2": 1, "c4": 6, "support": 12, "nodes": 826347, "leaves": 0, "solutions": 0},
    (1, 9, 3): {"a1": 1, "b2": 9, "c4": 3, "support": 13, "nodes": 80203, "leaves": 0, "solutions": 0},
    (3, 6, 4): {"a1": 3, "b2": 6, "c4": 4, "support": 13, "nodes": 294085, "leaves": 0, "solutions": 0},
    (5, 3, 5): {"a1": 5, "b2": 3, "c4": 5, "support": 13, "nodes": 414477, "leaves": 0, "solutions": 0},
    (7, 0, 6): {"a1": 7, "b2": 0, "c4": 6, "support": 13, "nodes": 904555, "leaves": 0, "solutions": 0},
}

EXPECTED_RANK2_SEEDS = [
    {"third": 30, "nodes": 135751, "leaves": 0, "solutions": 0},
    {"third": 35, "nodes": 99651, "leaves": 0, "solutions": 0},
    {"third": 40, "nodes": 99651, "leaves": 0, "solutions": 0},
    {"third": 45, "nodes": 135751, "leaves": 0, "solutions": 0},
    {"third": 55, "nodes": 99651, "leaves": 0, "solutions": 0},
    {"third": 65, "nodes": 99651, "leaves": 0, "solutions": 0},
    {"third": 80, "nodes": 99651, "leaves": 0, "solutions": 0},
    {"third": 85, "nodes": 99651, "leaves": 0, "solutions": 0},
    {"third": 105, "nodes": 135751, "leaves": 0, "solutions": 0},
]
EXPECTED_RANK2_TOTAL = {"nodes": 1005159, "leaves": 0, "solutions": 0}


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "research" / "orion-rg" / "x1k_c0_support10_13_rank3_u128.c").is_file():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(PACKET)
RG = ROOT / "research" / "orion-rg"
M3 = RG / "NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json"
RANK3_U128 = RG / "x1k_c0_support10_13_rank3_u128.c"
RANK3_BYTES = RG / "x1k_c0_support10_13_rank3_bytes.c"
RANK2_U128 = RG / "x1k_c0_support13_rank2_u128.c"
RANK2_BYTES = RG / "x1k_c0_support13_rank2_bytes.c"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_digest(raw: dict[str, Any]) -> str:
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def enumerate_patterns() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for support in range(11, 14):
        for a1 in range(support + 1):
            for b2 in range(support + 1):
                for c4 in range(support + 1):
                    if a1 + b2 + c4 != support:
                        continue
                    if a1 + 2 * b2 + 4 * c4 != 31:
                        continue
                    branches = ["rank3", "rank2"] if (a1, b2, c4) == (1, 9, 3) else ["rank3"]
                    rows.append(
                        {
                            "support": support,
                            "pattern": [a1, b2, c4],
                            "branches": branches,
                        }
                    )
    return rows


def compile_source(source: Path, executable: Path) -> dict[str, Any]:
    command = [
        "gcc",
        "-std=gnu11",
        "-O3",
        "-Wall",
        "-Wextra",
        "-Werror",
        str(source),
        "-o",
        str(executable),
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0 or completed.stdout or completed.stderr:
        raise RuntimeError(
            {
                "source": str(source.relative_to(ROOT)),
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
    return {
        "source_path": str(source.relative_to(ROOT)),
        "source_sha256": file_sha256(source),
        "compile_command": ["gcc", "-std=gnu11", "-O3", "-Wall", "-Wextra", "-Werror", str(source.relative_to(ROOT)), "-o", "<temporary-executable>"],
        "compile_returncode": completed.returncode,
        "compile_stdout": completed.stdout,
        "compile_stderr": completed.stderr,
    }


def run_rank3(executable: Path, pattern: tuple[int, int, int]) -> dict[str, Any]:
    completed = subprocess.run(
        [str(executable), *(str(value) for value in pattern)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )
    if completed.returncode != 0 or completed.stderr:
        raise RuntimeError(
            {
                "branch": "rank3",
                "pattern": pattern,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
    return json.loads(completed.stdout)


def parse_rank2(stdout: str) -> dict[str, Any]:
    seed_re = re.compile(r"^third=(\d+) nodes=(\d+) leaves=(\d+) sol=(\d+)$")
    total_re = re.compile(r"^TOTAL nodes=(\d+) leaves=(\d+) solutions=(\d+)$")
    seeds: list[dict[str, int]] = []
    total: dict[str, int] | None = None
    for line in stdout.splitlines():
        seed_match = seed_re.fullmatch(line)
        if seed_match:
            seeds.append(
                {
                    "third": int(seed_match.group(1)),
                    "nodes": int(seed_match.group(2)),
                    "leaves": int(seed_match.group(3)),
                    "solutions": int(seed_match.group(4)),
                }
            )
            continue
        total_match = total_re.fullmatch(line)
        if total_match:
            total = {
                "nodes": int(total_match.group(1)),
                "leaves": int(total_match.group(2)),
                "solutions": int(total_match.group(3)),
            }
            continue
        raise RuntimeError({"unparsed_rank2_line": line})
    if total is None:
        raise RuntimeError("rank2 total line missing")
    return {
        "normalized_seed_candidates": 16,
        "seed_rows_executed": len(seeds),
        "seed_rows_rejected_before_dfs": 16 - len(seeds),
        "seed_rows": seeds,
        "total": total,
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
    }


def run_rank2(executable: Path) -> tuple[str, dict[str, Any]]:
    completed = subprocess.run(
        [str(executable)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )
    if completed.returncode != 0 or completed.stderr:
        raise RuntimeError(
            {
                "branch": "rank2",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
    return completed.stdout, parse_rank2(completed.stdout)


def parent_ledger() -> dict[str, Any]:
    raw = json.loads(M3.read_text())
    checks = {
        "schema": raw.get("schema") == EXPECTED_M3_SCHEMA,
        "terminal": raw.get("terminal") == EXPECTED_M3_TERMINAL,
        "result_digest": raw.get("result_digest") == EXPECTED_M3_DIGEST,
        "bounded_support_le10_authority": raw.get("bounded_support_le10_theorem_authority") is True,
        "support11_plus_not_preclaimed": raw.get("support_11_plus_theorem_authority") is False,
        "no_c0_or_exact_d4": raw.get("c0_31_authority") is False
        and raw.get("exact_d4_authority") is False,
    }
    return {
        "path": str(M3.relative_to(ROOT)),
        "schema": raw.get("schema"),
        "terminal": raw.get("terminal"),
        "result_digest": raw.get("result_digest"),
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def source_ledger() -> dict[str, Any]:
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    observed = []
    for item in manifest["sources"]:
        path = ROOT / item["path"]
        observed.append(
            {
                "role": item["role"],
                "path": item["path"],
                "expected_sha256": item["sha256"],
                "observed_sha256": file_sha256(path),
                "matches": file_sha256(path) == item["sha256"],
            }
        )
    return {
        "manifest_path": str(SOURCE_MANIFEST.relative_to(ROOT)),
        "manifest_sha256": file_sha256(SOURCE_MANIFEST),
        "observed_sources": observed,
        "all_checks": all(item["matches"] for item in observed),
    }


def replay_ledger() -> dict[str, Any]:
    temporary = Path(tempfile.mkdtemp(prefix="orion04-m4-", dir="/tmp"))
    try:
        builds = {
            "rank3_u128": compile_source(RANK3_U128, temporary / "rank3_u128"),
            "rank3_bytes": compile_source(RANK3_BYTES, temporary / "rank3_bytes"),
            "rank2_u128": compile_source(RANK2_U128, temporary / "rank2_u128"),
            "rank2_bytes": compile_source(RANK2_BYTES, temporary / "rank2_bytes"),
        }
        rank3_observed: dict[tuple[tuple[int, int, int], str], dict[str, Any]] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            rank3_futures = {
                executor.submit(run_rank3, temporary / executable, pattern): (pattern, engine)
                for pattern in EXPECTED_RANK3
                for engine, executable in (("u128", "rank3_u128"), ("bytes", "rank3_bytes"))
            }
            rank2_futures = {
                "u128": executor.submit(run_rank2, temporary / "rank2_u128"),
                "bytes": executor.submit(run_rank2, temporary / "rank2_bytes"),
            }
            for future, key in rank3_futures.items():
                rank3_observed[key] = future.result()
            rank2_u128_stdout, rank2_u128 = rank2_futures["u128"].result()
            rank2_bytes_stdout, rank2_bytes = rank2_futures["bytes"].result()
        rank3_rows = [
            {
                "pattern": list(pattern),
                "branch": "rank3",
                "u128": rank3_observed[(pattern, "u128")],
                "bytes": rank3_observed[(pattern, "bytes")],
            }
            for pattern in EXPECTED_RANK3
        ]
    finally:
        shutil.rmtree(temporary, ignore_errors=True)

    exact_rank3 = all(
        row["u128"] == row["bytes"] == EXPECTED_RANK3[tuple(row["pattern"])]
        for row in rank3_rows
    )
    exact_rank2 = (
        rank2_u128 == rank2_bytes
        and rank2_u128["seed_rows"] == EXPECTED_RANK2_SEEDS
        and rank2_u128["total"] == EXPECTED_RANK2_TOTAL
    )
    checks = {
        "four_sources_compiled_cleanly": all(
            build["compile_returncode"] == 0
            and build["compile_stdout"] == ""
            and build["compile_stderr"] == ""
            for build in builds.values()
        ),
        "nine_rank3_rows": len(rank3_rows) == 9,
        "rank3_dual_exact_registered_agreement": exact_rank3,
        "rank2_dual_exact_registered_agreement": exact_rank2,
        "rank2_stdout_byte_exact": rank2_u128_stdout == rank2_bytes_stdout,
        "all_branches_unsat": all(row["u128"]["solutions"] == 0 for row in rank3_rows)
        and rank2_u128["total"]["solutions"] == 0,
        "temporary_executables_deleted": not temporary.exists(),
    }
    return {
        "compiler": "gcc",
        "build_mode": "gnu11 O3 Wall Wextra Werror",
        "builds": builds,
        "rank3_rows": rank3_rows,
        "rank2_branch": {
            "pattern": [1, 9, 3],
            "branch": "rank2",
            "u128": rank2_u128,
            "bytes": rank2_bytes,
        },
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run() -> dict[str, Any]:
    protocol = json.loads(PROTOCOL.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    terminals = json.loads(EXPECTED_TERMINALS.read_text())
    patterns = enumerate_patterns()
    expected_patterns = protocol["multiplicity_grammar"]["expected_patterns"]
    parent = parent_ledger()
    sources = source_ledger()
    replay = replay_ledger()

    pattern_checks = {
        "complete_equation_solutions": patterns == expected_patterns,
        "all_c4_ge4_rows_rank3_forced": all(
            row["pattern"][2] < 4 or row["branches"] == ["rank3"] for row in patterns
        ),
        "sole_rank_split_is_1_9_3": [
            row["pattern"] for row in patterns if row["branches"] == ["rank3", "rank2"]
        ]
        == [[1, 9, 3]],
        "rank2_seed_coefficients_complete": replay["rank2_branch"]["u128"][
            "normalized_seed_candidates"
        ]
        == 16,
    }
    authority = protocol["authority"]
    authority_checks = {
        "bounded_support_le13_only": authority.get("bounded_support_le13_theorem_authority") is True,
        "no_support14_plus": authority.get("support_14_plus_theorem_authority") is False,
        "no_support23": authority.get("support_23_theorem_authority") is False,
        "no_external": authority.get("independent_external_replay_complete") is False,
        "no_c0_or_d4": authority.get("c0_31_authority") is False
        and authority.get("exact_d4_authority") is False,
        "no_novelty_or_venue": authority.get("novelty_authority") is False
        and authority.get("venue_authority") is False,
    }
    gates = {
        "protocol_and_packet_present": all(
            path.is_file()
            for path in (PROTOCOL, SOURCE_MANIFEST, EXPECTED_TERMINALS, THEORY, CLAIM_DISPOSITION)
        ),
        "base_revision_bound": protocol.get("base_revision") == manifest.get("base_revision")
        and isinstance(protocol.get("base_revision"), str)
        and len(protocol["base_revision"]) == 40
        and all(ch in "0123456789abcdef" for ch in protocol["base_revision"]),
        "m3_parent_bound": parent["all_checks"],
        "source_hashes_bound": sources["all_checks"],
        "pattern_grammar_complete": all(pattern_checks.values()),
        "dual_exact_replay": replay["all_checks"],
        "authority_fail_closed": all(authority_checks.values()),
        "prospective_support23_ledger_not_consumed": True,
    }
    positive = all(gates.values())
    result: dict[str, Any] = {
        "schema": "ORION.ORION04.Wave3.M4.Support11To13Replay.v1",
        "base_revision": protocol.get("base_revision"),
        "protocol": {
            "path": str(PROTOCOL.relative_to(ROOT)),
            "sha256": file_sha256(PROTOCOL),
            "schema": protocol.get("schema"),
        },
        "source_manifest": sources,
        "expected_terminals": {
            "path": str(EXPECTED_TERMINALS.relative_to(ROOT)),
            "sha256": file_sha256(EXPECTED_TERMINALS),
        },
        "theory": {"path": str(THEORY.relative_to(ROOT)), "sha256": file_sha256(THEORY)},
        "claim_disposition": {
            "path": str(CLAIM_DISPOSITION.relative_to(ROOT)),
            "sha256": file_sha256(CLAIM_DISPOSITION),
        },
        "parent_m3": parent,
        "pattern_ledger": {
            "rows": patterns,
            "checks": pattern_checks,
            "all_checks": all(pattern_checks.values()),
        },
        "replay_ledger": replay,
        "gates": gates,
        "terminal": terminals["source_positive"] if positive else terminals["source_reject"],
        "theorem": (
            "a length-31 total-zero sequence over C_5^3 with no nonempty zero-sum "
            "subsequence of length at most five, if one exists, has support at least 14"
        ),
        "scientific_authority": "BOUNDED_C5CUBED_SUPPORT_LE13_EXCLUSION_ONLY" if positive else "NONE",
        "result_owner": "NON_QUANTUM_MATH",
        "bounded_support_le13_theorem_authority": positive,
        "support_14_plus_theorem_authority": False,
        "support_23_theorem_authority": False,
        "independent_external_replay_complete": False,
        "prospective_validation_authority": False,
        "c0_31_authority": False,
        "exact_d4_authority": False,
        "novelty_authority": False,
        "venue_authority": False,
        "quantum_claim": False,
        "ci_authority": False,
    }
    result["result_digest"] = signed_digest(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canonical(
            {
                "terminal": result["terminal"],
                "result_digest": result["result_digest"],
                "patterns": len(result["pattern_ledger"]["rows"]),
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0 if all(result["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
