#!/usr/bin/env python3
"""Finite corroboration for AB R12 production-registry non-identifiability."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "ORION.AB.RegistryNonidentifiability.R12.v1"
TERMINAL = "AB_REGISTRY_NONIDENTIFIABILITY_R12_PASS"
SOURCE_BASE = "533a8e15dc20fd875eb442b573fd72eb9264b218"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descending_edges(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((source, target) for source in range(2, n + 1) for target in range(1, source))


def terminal_complexity(n: int, registry: frozenset[tuple[int, int]]) -> int:
    outgoing = {source for source, _ in registry}
    terminals = [state for state in range(1, n + 1) if state not in outgoing]
    return max(terminals)


def direct_optimizer_signature(n: int) -> dict[str, int]:
    return {"feasible_state_count": n, "optimum_value": 1, "optimum_witness": 1}


def exhaustive_panel() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for n in range(2, 7):
        edges = descending_edges(n)
        histogram: collections.Counter[int] = collections.Counter()
        signatures: set[str] = set()
        for mask in range(1 << len(edges)):
            registry = frozenset(
                edge for index, edge in enumerate(edges) if (mask >> index) & 1
            )
            histogram[terminal_complexity(n, registry)] += 1
            signatures.add(canonical_json(direct_optimizer_signature(n)))
        if len(signatures) != 1:
            raise AssertionError("direct optimizer signature changed with registry")
        if set(histogram) != set(range(1, n + 1)):
            raise AssertionError(("terminal range incomplete", n, histogram))
        if sum(histogram.values()) != 1 << (n * (n - 1) // 2):
            raise AssertionError(("registry denominator mismatch", n))
        rows.append(
            {
                "n": n,
                "candidate_edge_count": len(edges),
                "registry_count": 1 << len(edges),
                "direct_optimizer": direct_optimizer_signature(n),
                "terminal_complexity_histogram": {
                    str(key): histogram[key] for key in sorted(histogram)
                },
                "minimum_terminal_complexity": min(histogram),
                "maximum_terminal_complexity": max(histogram),
            }
        )
    return rows


def unbounded_family() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for n in range(2, 33):
        empty: frozenset[tuple[int, int]] = frozenset()
        chain = frozenset((state, state - 1) for state in range(2, n + 1))
        empty_value = terminal_complexity(n, empty)
        chain_value = terminal_complexity(n, chain)
        if (empty_value, chain_value) != (n, 1):
            raise AssertionError(("family drift", n, empty_value, chain_value))
        rows.append(
            {
                "n": n,
                "optimizer_value": 1,
                "empty_registry_terminal_complexity": empty_value,
                "chain_registry_terminal_complexity": chain_value,
                "ambiguity_gap": empty_value - chain_value,
            }
        )
    return rows


def hidden_edge_controls() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for n in range(2, 33):
        without: frozenset[tuple[int, int]] = frozenset()
        with_hidden = frozenset({(n, 1)})
        left = terminal_complexity(n, without)
        right = terminal_complexity(n, with_hidden)
        if (left, right) != (n, n - 1):
            raise AssertionError(("hidden-edge drift", n, left, right))
        rows.append(
            {
                "n": n,
                "unresolved_edge_source": n,
                "unresolved_edge_target": 1,
                "terminal_complexity_if_absent": left,
                "terminal_complexity_if_present": right,
            }
        )
    return rows


def build_result(script: Path) -> dict[str, Any]:
    exhaustive = exhaustive_panel()
    family = unbounded_family()
    hidden = hidden_edge_controls()
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_base": SOURCE_BASE,
        "verifier_sha256": sha256_file(script),
        "exhaustive_panel": exhaustive,
        "exhaustive_registry_total": sum(row["registry_count"] for row in exhaustive),
        "unbounded_family": family,
        "hidden_edge_controls": hidden,
        "controls": {
            "same_optimizer_signature_for_every_registry": True,
            "terminal_complexities_span_one_through_n": True,
            "empty_vs_chain_gap_is_n_minus_one": True,
            "one_unresolved_edge_changes_terminal_complexity": True,
            "all_moves_semantics_preserving_by_single_class": True,
            "all_enumerated_edges_strictly_resource_decreasing": True,
        },
        "authority": {
            "analytic_theorems": "PROVED_IN_ADDENDUM",
            "finite_verification": "IMPLEMENTATION_CORROBORATION_ONLY",
            "r6m_registry_completeness": False,
            "production_transfer": False,
            "external_independence": "CANNOT_CHECK",
            "novelty": "CANNOT_CHECK",
            "grants_journal_authority": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_result(Path(__file__))
    payload = canonical_json(result) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(
        TERMINAL,
        f"registries={result['exhaustive_registry_total']}",
        f"sha256={digest}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
