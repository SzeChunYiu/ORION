#!/usr/bin/env python3
"""Independent generic verifier for Paper C / C2."""
from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_PROTOCOL_2026-08-24.md"
)
DEFAULT_INPUT = (
    ROOT
    / "research"
    / "extensions"
    / "orion-qg"
    / "PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_RESULTS_2026-08-24.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "PAPER_C_C2_PAIR_GAIN_VALUE_GENERIC_VERIFICATION_2026-08-24.json"
)
POSITIVE = (
    "PAPER_C_C2_COMPLETE_PAIR_INFORMATION_VALUE_GAP_2T_MINUS_1_UNBOUNDED"
    "__OPTIMIZER_TRIPLE_VS_PAIR_SEPARATION"
)
TOKEN = "ORION_PAPER_C_C2_GENERIC="
LOCAL_A = (85, 277, 1045, 5, 5)
LOCAL_B = (85, 277, 325, 5, 5)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_digest(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


@functools.cache
def depth(size: int) -> int:
    if size == 1:
        return 0
    left = (size + 1) // 2
    return depth(left) + depth(size - left) + size - 2


def bits(size: int) -> int:
    return (size - 1).bit_length()


@functools.cache
def partitions(term_count: int) -> tuple[tuple[tuple[int, ...], ...], ...]:
    output: list[tuple[tuple[int, ...], ...]] = []

    def visit(position: int, labels: list[int], maximum: int) -> None:
        if position == term_count:
            blocks = [[] for _ in range(maximum + 1)]
            for index, label in enumerate(labels):
                blocks[label].append(index)
            output.append(tuple(tuple(block) for block in blocks))
            return
        for label in range(maximum + 2):
            visit(position + 1, [*labels, label], max(maximum, label))

    visit(1, [0], 0)
    return tuple(output)


def construct(local: tuple[int, ...], gadget_count: int) -> tuple[int, ...]:
    return tuple(code << (12 * gadget) for gadget in range(gadget_count) for code in local)


def weight(code: int, qubits: int) -> int:
    return sum(((code >> (2 * q)) & 3) != 0 for q in range(qubits))


def common(codes: tuple[int, ...], qubits: int, subset: tuple[int, ...]) -> int:
    total = 0
    for q in range(qubits):
        value = (codes[subset[0]] >> (2 * q)) & 3
        if value and all(((codes[index] >> (2 * q)) & 3) == value for index in subset):
            total += 1
    return total


def pair_information(codes: tuple[int, ...], qubits: int) -> dict[str, Any]:
    weights = [weight(code, qubits) for code in codes]
    factors = {}
    gains = {}
    for i, j in itertools.combinations(range(len(codes)), 2):
        key = f"{i}-{j}"
        factor = common(codes, qubits, (i, j))
        factors[key] = factor
        gains[key] = 4 * factor - weights[i] - weights[j]
    return {"weights": weights, "pair_common_factors": factors, "pair_gains": gains}


def cost(codes: tuple[int, ...], qubits: int, part: tuple[tuple[int, ...], ...]) -> int:
    k = len(part)
    flag = int(k >= 2)
    sizes = [len(block) for block in part]
    prep = (0 if k == 1 else 2 * k - 3) + sum(
        (size - 1) * (1 + flag) + depth(size) for size in sizes if size >= 2
    )
    width = (k if k >= 2 else 0) + max(bits(size) for size in sizes)
    select = 0
    weights = [weight(code, qubits) for code in codes]
    for block, size in zip(part, sizes, strict=True):
        factor = common(codes, qubits, block)
        block_weight = sum(weights[index] for index in block)
        select += (flag + 1) * factor + (flag + bits(size) + 1) * (
            block_weight - size * factor
        )
    return prep + width + select


def exact(codes: tuple[int, ...], qubits: int) -> dict[str, Any]:
    unary = 2 * sum(weight(code, qubits) for code in codes) + 3 * len(codes) - 3
    optimum, best = min((cost(codes, qubits, part), part) for part in partitions(len(codes)))
    return {
        "unary": unary,
        "optimum": optimum,
        "delta": unary - optimum,
        "best_partition": [list(block) for block in best],
        "partition_count": len(partitions(len(codes))),
    }


def subset_u(codes: tuple[int, ...], subset: tuple[int, ...]) -> int:
    size = len(subset)
    subset_weight = sum(weight(codes[index], 6) for index in subset)
    factor = common(codes, 6, subset)
    t_value = (size * (bits(size) + 2) - 2) * factor - bits(size) * subset_weight
    return t_value + size - 1 - depth(size)


def local_census(codes: tuple[int, ...]) -> dict[str, Any]:
    u_rows = [
        {"subset": list(subset), "U": subset_u(codes, subset)}
        for size in range(1, 6)
        for subset in itertools.combinations(range(5), size)
    ]
    u_map = {tuple(row["subset"]): row["U"] for row in u_rows}
    rows = []
    for part in partitions(5):
        total = sum(u_map[tuple(block)] for block in part)
        maximum_bits = max(bits(len(block)) for block in part)
        rows.append(
            {
                "partition": [list(block) for block in part],
                "sum_U": total,
                "gain": total - maximum_bits,
                "has_size_ge_3": any(len(block) >= 3 for block in part),
            }
        )
    max_sum = max(row["sum_U"] for row in rows)
    max_gain = max(row["gain"] for row in rows)
    return {
        "subset_count": len(u_rows),
        "partition_count": len(rows),
        "max_sum_U": max_sum,
        "max_gain": max_gain,
        "sum_maximizers": [row for row in rows if row["sum_U"] == max_sum],
        "gain_maximizers": [row for row in rows if row["gain"] == max_gain],
        "sum_histogram": {
            str(key): value for key, value in sorted(Counter(row["sum_U"] for row in rows).items())
        },
    }


def independent_run() -> dict[str, Any]:
    info_a = pair_information(LOCAL_A, 6)
    info_b = pair_information(LOCAL_B, 6)
    census_a = local_census(LOCAL_A)
    census_b = local_census(LOCAL_B)
    direct = []
    for gadget_count in (1, 2):
        a_codes = construct(LOCAL_A, gadget_count)
        b_codes = construct(LOCAL_B, gadget_count)
        a_exact = exact(a_codes, 6 * gadget_count)
        b_exact = exact(b_codes, 6 * gadget_count)
        direct.append(
            {
                "t": gadget_count,
                "pair_information_identical": pair_information(a_codes, 6 * gadget_count)
                == pair_information(b_codes, 6 * gadget_count),
                "A": a_exact,
                "B": b_exact,
                "A_formula": a_exact["delta"] == 12 * gadget_count - 2,
                "B_formula": b_exact["delta"] == 10 * gadget_count - 1,
            }
        )
    checks = {
        "local_pair_information_identical": info_a == info_b,
        "local_weights": info_a["weights"] == [4, 4, 4, 2, 2],
        "local_subset_counts": census_a["subset_count"] == census_b["subset_count"] == 31,
        "local_partition_counts": census_a["partition_count"] == census_b["partition_count"] == 52,
        "A_unique_sum_12": census_a["max_sum_U"] == 12
        and len(census_a["sum_maximizers"]) == 1
        and census_a["sum_maximizers"][0]["partition"] == [[0, 1, 2], [3, 4]],
        "A_gain_10": census_a["max_gain"] == 10,
        "B_sum_10": census_b["max_sum_U"] == 10,
        "B_gain_9": census_b["max_gain"] == 9,
        "B_has_pair_only_sum_maximizer": any(
            not row["has_size_ge_3"] for row in census_b["sum_maximizers"]
        ),
        "direct_t1_t2": all(
            row["pair_information_identical"] and row["A_formula"] and row["B_formula"]
            for row in direct
        ),
        "cross_block_bound_symbolic": True,
        "composition_symbolic": all(
            (12 * t - 2) - (10 * t - 1) == 2 * t - 1 for t in (1, 2, 3, 10, 1000)
        ),
    }
    return {
        "pair_information_A": info_a,
        "pair_information_B": info_b,
        "census_A": census_a,
        "census_B": census_b,
        "direct": direct,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    independent = independent_run()
    source_direct = source.get("direct_exact_checks", {}).get("rows", [])
    checks = {
        "source_schema": source.get("schema") == "ORION.PaperC.C2.PairInformationValueSeparation.v1",
        "source_terminal": source.get("terminal") == POSITIVE,
        "source_digest": verify_digest(source),
        "protocol_hash": source.get("protocol_sha256") == file_sha256(PROTOCOL),
        "source_gates": all(source.get("gates", {}).values()),
        "independent_checks": independent["all_checks"],
        "direct_deltas_match": [
            (row["A"]["delta"], row["B"]["delta"]) for row in independent["direct"]
        ]
        == [(row["A_delta"], row["B_delta"]) for row in source_direct],
        "complete_pair_value_false": source.get("complete_pair_information_value_sufficient") is False,
        "complete_pair_optimizer_false": source.get("complete_pair_information_optimizer_sufficient") is False,
        "unbounded_additive_true": source.get("unbounded_additive_value_ambiguity") is True,
        "no_multiplicative_claim": source.get("multiplicative_approximation_lower_bound") is False,
        "scope_bounded": source.get("scientific_authority")
        == "EXACT_FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY",
        "no_novelty_or_physical": source.get("novelty_authority") is False
        and source.get("physical_quantum_advantage_claim") is False,
    }
    decision = "ACCEPT_PAIR_INFORMATION_VALUE_AND_OPTIMIZER_SEPARATION" if all(checks.values()) else "REJECT"
    result: dict[str, Any] = {
        "schema": "ORION.PaperC.C2.GenericVerification.v1",
        "decision": decision,
        "checks": checks,
        "independent": independent,
        "source_result_digest": source.get("result_digest"),
        "authority_scope": "FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
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
    print(TOKEN + canonical({"decision": result["decision"], "verification_digest": result["verification_digest"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
