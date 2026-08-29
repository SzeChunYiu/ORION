#!/usr/bin/env python3
"""Independent static checker for the ORION-04 M4 support-11-to-13 packet."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
PACKET = HERE.parent.parent
PROTOCOL = PACKET / "PROTOCOL.json"
SOURCE_MANIFEST = PACKET / "SOURCE_MANIFEST.json"
EXPECTED_TERMINALS = PACKET / "EXPECTED_TERMINALS.json"
THEORY = PACKET / "THEORY.md"
CLAIM_DISPOSITION = PACKET / "CLAIM_DISPOSITION.md"
DEFAULT_INPUT = PACKET / "RESULT.json"
DEFAULT_OUTPUT = PACKET / "GENERIC_RESULT.json"
TOKEN = "ORION04_M4_CHECKER="

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


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_valid(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def independent_patterns() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for support in (11, 12, 13):
        for c4 in range(14):
            for b2 in range(14):
                a1 = support - b2 - c4
                if a1 < 0:
                    continue
                if a1 + 2 * b2 + 4 * c4 != 31:
                    continue
                rows.append(
                    {
                        "support": support,
                        "pattern": [a1, b2, c4],
                        "branches": ["rank3", "rank2"] if [a1, b2, c4] == [1, 9, 3] else ["rank3"],
                    }
                )
    return sorted(rows, key=lambda row: (row["support"], row["pattern"]))


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    terminals = json.loads(EXPECTED_TERMINALS.read_text())

    rank3_rows = source.get("replay_ledger", {}).get("rank3_rows", [])
    rank3_by_pattern = {tuple(row.get("pattern", [])): row for row in rank3_rows}
    rank2 = source.get("replay_ledger", {}).get("rank2_branch", {})
    source_rows = source.get("pattern_ledger", {}).get("rows", [])
    patterns = independent_patterns()

    source_hash_checks = []
    expected_observed_sources = []
    for item in manifest.get("sources", []):
        actual = file_sha256(ROOT / item["path"])
        source_hash_checks.append(actual == item["sha256"])
        expected_observed_sources.append(
            {
                "role": item["role"],
                "path": item["path"],
                "expected_sha256": item["sha256"],
                "observed_sha256": actual,
                "matches": actual == item["sha256"],
            }
        )

    exact_rank3 = set(rank3_by_pattern) == set(EXPECTED_RANK3) and all(
        rank3_by_pattern[pattern].get("branch") == "rank3"
        and rank3_by_pattern[pattern].get("u128") == expected
        and rank3_by_pattern[pattern].get("bytes") == expected
        for pattern, expected in EXPECTED_RANK3.items()
    )
    rank2_u128 = rank2.get("u128", {})
    rank2_bytes = rank2.get("bytes", {})
    exact_rank2 = (
        rank2.get("pattern") == [1, 9, 3]
        and rank2.get("branch") == "rank2"
        and rank2_u128 == rank2_bytes
        and rank2_u128.get("normalized_seed_candidates") == 16
        and rank2_u128.get("seed_rows_executed") == 9
        and rank2_u128.get("seed_rows_rejected_before_dfs") == 7
        and rank2_u128.get("seed_rows") == EXPECTED_RANK2_SEEDS
        and rank2_u128.get("total") == EXPECTED_RANK2_TOTAL
    )
    checks = {
        "source_schema": source.get("schema") == "ORION.ORION04.Wave3.M4.Support11To13Replay.v1",
        "source_digest": digest_valid(source),
        "source_terminal": source.get("terminal") == terminals.get("source_positive"),
        "protocol_schema": protocol.get("schema") == "ORION.ORION04.Wave3.M4.Support11To13Protocol.v1",
        "packet_paths": source.get("protocol", {}).get("path") == str(PROTOCOL.relative_to(ROOT))
        and source.get("source_manifest", {}).get("manifest_path")
        == str(SOURCE_MANIFEST.relative_to(ROOT))
        and source.get("expected_terminals", {}).get("path")
        == str(EXPECTED_TERMINALS.relative_to(ROOT))
        and source.get("theory", {}).get("path") == str(THEORY.relative_to(ROOT))
        and source.get("claim_disposition", {}).get("path")
        == str(CLAIM_DISPOSITION.relative_to(ROOT)),
        "protocol_hash": source.get("protocol", {}).get("sha256") == file_sha256(PROTOCOL),
        "manifest_hash": source.get("source_manifest", {}).get("manifest_sha256")
        == file_sha256(SOURCE_MANIFEST),
        "terminal_hash": source.get("expected_terminals", {}).get("sha256")
        == file_sha256(EXPECTED_TERMINALS),
        "theory_hash": source.get("theory", {}).get("sha256") == file_sha256(THEORY),
        "claim_disposition_hash": source.get("claim_disposition", {}).get("sha256")
        == file_sha256(CLAIM_DISPOSITION),
        "base_revision_bound": source.get("base_revision") == protocol.get("base_revision")
        == manifest.get("base_revision")
        and isinstance(source.get("base_revision"), str)
        and len(source["base_revision"]) == 40
        and all(ch in "0123456789abcdef" for ch in source["base_revision"]),
        "parent_digest": source.get("parent_m3", {}).get("result_digest") == EXPECTED_M3_DIGEST,
        "parent_terminal": source.get("parent_m3", {}).get("terminal") == EXPECTED_M3_TERMINAL,
        "parent_checks": source.get("parent_m3", {}).get("all_checks") is True,
        "source_hashes": all(source_hash_checks)
        and source.get("source_manifest", {}).get("all_checks") is True
        and source.get("source_manifest", {}).get("observed_sources")
        == expected_observed_sources,
        "patterns_independent": source_rows == patterns
        and protocol.get("multiplicity_grammar", {}).get("expected_patterns") == patterns,
        "nine_rank3_rows": exact_rank3,
        "rank2_branch": exact_rank2,
        "all_replay_checks": source.get("replay_ledger", {}).get("all_checks") is True
        and all(source.get("replay_ledger", {}).get("checks", {}).values()),
        "all_gates": all(source.get("gates", {}).values()),
        "bounded_authority": source.get("bounded_support_le13_theorem_authority") is True
        and source.get("scientific_authority") == "BOUNDED_C5CUBED_SUPPORT_LE13_EXCLUSION_ONLY",
        "no_support14_or_23": source.get("support_14_plus_theorem_authority") is False
        and source.get("support_23_theorem_authority") is False,
        "no_external_or_prospective": source.get("independent_external_replay_complete") is False
        and source.get("prospective_validation_authority") is False,
        "no_c0_or_exact_d4": source.get("c0_31_authority") is False
        and source.get("exact_d4_authority") is False,
        "no_novelty_venue_quantum_ci": source.get("novelty_authority") is False
        and source.get("venue_authority") is False
        and source.get("quantum_claim") is False
        and source.get("ci_authority") is False,
    }
    positive = all(checks.values())
    result: dict[str, Any] = {
        "schema": "ORION.ORION04.Wave3.M4.GenericVerification.v1",
        "decision": terminals["checker_accept"] if positive else terminals["checker_reject"],
        "source_result_digest": source.get("result_digest"),
        "independent_patterns": patterns,
        "checks": checks,
        "authority_scope": "BOUNDED_C5CUBED_SUPPORT_LE13_EXCLUSION_ONLY" if positive else "NONE",
        "bounded_support_le13_theorem_authority": positive,
        "support_14_plus_theorem_authority": False,
        "support_23_theorem_authority": False,
        "independent_external_replay_complete": False,
        "prospective_validation_authority": False,
        "c0_31_authority": False,
        "exact_d4_authority": False,
        "novelty_authority": False,
        "venue_authority": False,
    }
    result["verification_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canonical(
            {
                "decision": result["decision"],
                "verification_digest": result["verification_digest"],
                "all_checks": all(result["checks"].values()),
            }
        )
    )
    return 0 if all(result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
